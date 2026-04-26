from flask import Flask, render_template, request, jsonify
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from supabase import create_client
from dotenv import load_dotenv
import threading
import os

from esi import compute_esi, compute_price, normalize
from gemini_weights import get_weights
from gemini_explain import get_explanation
from geo import get_city_tracts, get_city_bbox, tract_components
from mock_data import get_mock_for_city
from data_sources import get_air_quality, get_light_pollution, get_heat_island, get_energy_use
from simulation.simulate import run_simulation

load_dotenv()

app = Flask(__name__)

supabase_client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

# In-process caches — persist for server lifetime, reset on restart.
# All bounded by the number of distinct cities users actually search.
_weights_cache: dict = {}
_neighborhoods_cache: dict = {}   # keyed by city only — no base_rate
_explanation_cache: dict = {}

# Per-key locks prevent duplicate work when two requests race on the same cold key,
# without blocking requests for different keys (cities/neighborhoods).
_key_locks: dict[str, threading.Lock] = {}
_key_locks_meta = threading.Lock()  # protects the _key_locks dict itself


def _get_lock(key: str) -> threading.Lock:
    with _key_locks_meta:
        if key not in _key_locks:
            _key_locks[key] = threading.Lock()
        return _key_locks[key]

_CACHE_MAX = 50  # evict oldest city if cache grows beyond this


def require_auth(f):
    """Flask decorator that validates a Supabase JWT from the Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            user = supabase_client.auth.get_user(token)
            request.user = user
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def login():
    return render_template(
        "login.html",
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_ANON_KEY", ""),
    )


@app.route("/map")
def map_page():
    return render_template("map.html")


@app.route("/api/city")
@require_auth
def api_city():
    """Return all neighborhoods with ESI scores, prices, and Gemini weights for a city."""
    city = request.args.get("name", "Tucson, AZ")
    try:
        base_rate = max(0.01, min(5.0, float(request.args.get("base_rate", 0.12))))
    except ValueError:
        base_rate = 0.12

    # Gemini weights and Census TIGER tracts are independent — fetch in parallel
    with ThreadPoolExecutor(max_workers=2) as ex:
        weights_f = ex.submit(_get_weights, city)
        ex.submit(get_city_tracts, city)   # warms _tiger_cache for _get_neighborhoods
    weights, gemini_reasoning = weights_f.result()

    neighborhoods, city_center = _get_neighborhoods(city, weights, base_rate)

    return jsonify({
        "city": city,
        "city_center": city_center,
        "weights": weights,
        "gemini_reasoning": gemini_reasoning,
        "neighborhoods": neighborhoods,
    })


@app.route("/api/weights")
@require_auth
def api_weights():
    """Return Gemini-generated ESI weights and reasoning for a city."""
    city = request.args.get("city", "Tucson, AZ")
    try:
        return jsonify(get_weights(city))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/neighborhood")
@require_auth
def api_neighborhood():
    """Return ESI detail and Gemini explanation for a single neighborhood."""
    city = request.args.get("city", "Tucson, AZ")
    neighborhood = request.args.get("n", "")
    try:
        base_rate = max(0.01, min(5.0, float(request.args.get("base_rate", 0.12))))
    except ValueError:
        base_rate = 0.12
    weights, _ = _get_weights(city)

    neighborhoods, _ = _get_neighborhoods(city, weights, base_rate)
    match = next((n for n in neighborhoods if n["name"].lower() == neighborhood.lower()), None)
    if not match:
        return jsonify({"error": "Neighborhood not found"}), 404

    cache_key = f"{city}|{neighborhood.lower()}"
    if cache_key not in _explanation_cache:
        with _get_lock(f"explain:{cache_key}"):
            if cache_key not in _explanation_cache:
                try:
                    _explanation_cache[cache_key] = get_explanation(
                        city, match["name"], match["esi_score"], match["components"]
                    )
                except Exception:
                    _explanation_cache[cache_key] = ""

    result = dict(match)
    result["gemini_explanation"] = _explanation_cache[cache_key]
    return jsonify(result)


@app.route("/api/simulate")
@require_auth
def api_simulate():
    """Return simulation results for a single neighborhood."""
    city = request.args.get("city", "Tucson, AZ")
    neighborhood = request.args.get("neighborhood", "")
    try:
        base_rate = max(0.01, min(5.0, float(request.args.get("base_rate", 0.12))))
    except ValueError:
        base_rate = 0.12

    weights, _ = _get_weights(city)
    neighborhoods, _ = _get_neighborhoods(city, weights, base_rate)
    match = next((n for n in neighborhoods if n["name"].lower() == neighborhood.lower()), None)
    if not match:
        return jsonify({"error": "Neighborhood not found"}), 404

    return jsonify(run_simulation(match["name"], match["esi_score"], match["dynamic_price_per_kwh"], base_rate))


@app.route("/api/simulate-city")
@require_auth
def api_simulate_city():
    """Return simulation results for all neighborhoods in a city (used by map impact layer)."""
    city = request.args.get("name", "Tucson, AZ")
    try:
        base_rate = max(0.01, min(5.0, float(request.args.get("base_rate", 0.12))))
    except ValueError:
        base_rate = 0.12

    weights, _ = _get_weights(city)
    neighborhoods, _ = _get_neighborhoods(city, weights, base_rate)

    simulations = [
        run_simulation(n["name"], n["esi_score"], n["dynamic_price_per_kwh"], base_rate)
        for n in neighborhoods
    ]
    return jsonify({"city": city, "simulations": simulations})


@app.route("/api/search-log", methods=["POST"])
@require_auth
def api_search_log():
    """Log a city search query to Supabase for analytics."""
    body = request.get_json(silent=True) or {}
    try:
        supabase_client.table("search_log").insert({
            "user_id": request.user.user.id,
            "query": body.get("query", ""),
            "city": body.get("city", ""),
        }).execute()
    except Exception:
        pass
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _evict_if_full(cache: dict) -> None:
    """Drop the oldest entry when the cache hits its size cap."""
    if len(cache) >= _CACHE_MAX:
        cache.pop(next(iter(cache)))


def _get_weights(city: str) -> tuple[dict, str]:
    """Return (weights_dict, reasoning) for a city, cached in-process after first call."""
    if city in _weights_cache:
        return _weights_cache[city]
    with _get_lock(f"weights:{city}"):
        if city not in _weights_cache:  # re-check after acquiring lock
            try:
                data = get_weights(city)
                weights = {k: v for k, v in data.items() if k != "reasoning"}
                reasoning = data.get("reasoning", "")
            except Exception:
                weights = {"air_quality": 0.25, "light_pollution": 0.25,
                           "heat_island": 0.25, "energy_use": 0.25}
                reasoning = "Default equal weights applied (Gemini unavailable)."
            _evict_if_full(_weights_cache)
            _weights_cache[city] = (weights, reasoning)
    return _weights_cache[city]


def _get_neighborhoods(city: str, weights: dict, base_rate: float = 0.12) -> tuple[list, dict | None]:
    """Return (neighborhoods, city_center) with prices applied for base_rate.

    Neighborhood ESI data is cached by city only. Prices (which depend on
    base_rate) are computed on the fly so slider changes don't create new
    cache entries and leak memory.
    """
    if city not in _neighborhoods_cache:
        with _get_lock(f"neighborhoods:{city}"):
            if city not in _neighborhoods_cache:
                _evict_if_full(_neighborhoods_cache)
                _neighborhoods_cache[city] = _build_neighborhoods(city, weights)

    neighborhoods, city_center = _neighborhoods_cache[city]
    priced = [
        {**n, "dynamic_price_per_kwh": compute_price(n["esi_score"], base_rate)}
        for n in neighborhoods
    ]
    return priced, city_center


def _build_neighborhoods(city: str, weights: dict) -> tuple[list, dict | None]:
    """Build scored neighborhood list from Census tracts, blending real API data where available. Falls back to mock data if TIGER is unavailable."""
    features, city_center = get_city_tracts(city)

    # Fallback: mock neighborhood names with no polygons
    if len(features) < 3:
        mock_list = get_mock_for_city(city)
        features = [{"name": m["name"], "geojson": None,
                     "lat": city_center["lat"] if city_center else 0,
                     "lon": city_center["lon"] if city_center else 0}
                    for m in mock_list] if city_center else []

    if not city_center:
        try:
            info = get_city_bbox(city)
            city_center = {"lat": info["lat"], "lon": info["lon"]} if info else None
        except Exception:
            city_center = None

    city_lat = city_center["lat"] if city_center else 0
    city_lon = city_center["lon"] if city_center else 0

    # Only air_quality and energy_use make real network calls — fetch those in parallel.
    # light_pollution and heat_island are local dict lookups and don't need threads.
    with ThreadPoolExecutor(max_workers=2) as ex:
        aq_f = ex.submit(get_air_quality, city)
        eu_f = ex.submit(get_energy_use, city)

    city_aq = city_lp = city_hi = city_eu = None
    try: city_aq = normalize(aq_f.result(), 0, 200)
    except Exception: pass
    try: city_lp = normalize(get_light_pollution(city), 0, 100)
    except Exception: pass
    try: city_hi = normalize(get_heat_island(city), 0, 10)
    except Exception: pass
    try: city_eu = normalize(eu_f.result(), 0, 4000)
    except Exception: pass

    def blend(geo_val: float, real_val, weight: float = 0.35) -> float:
        if real_val is None:
            return geo_val
        return round(geo_val * (1 - weight) + real_val * weight, 3)

    results = []
    for feat in features:
        geo = tract_components(feat["lat"], feat["lon"], city_lat, city_lon)

        components = {
            "air_quality_normalized":     blend(geo["air_quality"], city_aq),
            "light_pollution_normalized": blend(geo["light_pollution"], city_lp),
            "heat_island_normalized":     blend(geo["heat_island"], city_hi),
            "energy_use_normalized":      blend(geo["energy_use"], city_eu),
        }

        esi = compute_esi(components, weights)

        results.append({
            "id": feat["name"].lower().replace(" ", "-"),
            "name": feat["name"],
            "geojson": feat["geojson"],
            "esi_score": round(esi, 2),
            "components": {
                "air_quality":     round(components["air_quality_normalized"], 2),
                "light_pollution": round(components["light_pollution_normalized"], 2),
                "heat_island":     round(components["heat_island_normalized"], 2),
                "energy_use":      round(components["energy_use_normalized"], 2),
            },
        })

    return results, city_center


if __name__ == "__main__":
    app.run(debug=True)
