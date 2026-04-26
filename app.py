from flask import Flask, render_template, request, jsonify
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from supabase import create_client
from dotenv import load_dotenv
import os

from esi import compute_esi, compute_price, normalize
from gemini_weights import get_weights
from gemini_explain import get_explanation
from geo import get_city_tracts, get_city_bbox, tract_components
from mock_data import get_mock_for_city
from data_sources import get_air_quality, get_light_pollution, get_heat_island, get_energy_use

load_dotenv()

app = Flask(__name__)

supabase_client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# In-process caches — persist for server lifetime, reset on restart
_weights_cache: dict = {}
_neighborhoods_cache: dict = {}
_explanation_cache: dict = {}


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
        try:
            _explanation_cache[cache_key] = get_explanation(
                city, match["name"], match["esi_score"], match["components"]
            )
        except Exception:
            _explanation_cache[cache_key] = ""

    result = dict(match)
    result["gemini_explanation"] = _explanation_cache[cache_key]
    return jsonify(result)


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

def _get_weights(city: str) -> tuple[dict, str]:
    """Return (weights_dict, reasoning) for a city, cached in-process after first call."""
    if city not in _weights_cache:
        try:
            data = get_weights(city)
            weights = {k: v for k, v in data.items() if k != "reasoning"}
            reasoning = data.get("reasoning", "")
        except Exception:
            weights = {"air_quality": 0.25, "light_pollution": 0.25,
                       "heat_island": 0.25, "energy_use": 0.25}
            reasoning = "Default equal weights applied (Gemini unavailable)."
        _weights_cache[city] = (weights, reasoning)
    return _weights_cache[city]


def _get_neighborhoods(city: str, weights: dict, base_rate: float = 0.12) -> tuple[list, dict | None]:
    """Return (neighborhoods, city_center), cached per city+rate combination."""
    cache_key = f"{city}|{base_rate}"
    if cache_key not in _neighborhoods_cache:
        _neighborhoods_cache[cache_key] = _build_neighborhoods(city, weights, base_rate)
    return _neighborhoods_cache[cache_key]


def _build_neighborhoods(city: str, weights: dict, base_rate: float = 0.12) -> tuple[list, dict | None]:
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

    # Fetch all 4 data sources in parallel — wait for the slowest, not the sum
    with ThreadPoolExecutor(max_workers=4) as ex:
        aq_f = ex.submit(get_air_quality, city)
        lp_f = ex.submit(get_light_pollution, city)
        hi_f = ex.submit(get_heat_island, city)
        eu_f = ex.submit(get_energy_use, city)

    city_aq = city_lp = city_hi = city_eu = None
    try: city_aq = normalize(aq_f.result(), 0, 200)
    except Exception: pass
    try: city_lp = normalize(lp_f.result(), 0, 100)
    except Exception: pass
    try: city_hi = normalize(hi_f.result(), 0, 10)
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
        price = compute_price(esi, base_rate=base_rate)

        results.append({
            "id": feat["name"].lower().replace(" ", "-"),
            "name": feat["name"],
            "geojson": feat["geojson"],
            "esi_score": round(esi, 2),
            "dynamic_price_per_kwh": price,
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
