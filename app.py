from flask import Flask, render_template, request, jsonify
from functools import wraps
from supabase import create_client
from dotenv import load_dotenv
import os

from esi import compute_esi, compute_price, normalize
from gemini_weights import get_weights
from gemini_explain import get_explanation
from geo import get_city_tracts, get_city_bbox, tract_components
from mock.mock_data import get_mock_for_city
from data_sources.air_quality import get_air_quality
from data_sources.light_pollution import get_light_pollution
from data_sources.heat_island import get_heat_island
from data_sources.energy_use import get_energy_use

load_dotenv()

app = Flask(__name__)

supabase_client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# In-process caches — persist for server lifetime, reset on restart
_weights_cache: dict = {}


def require_auth(f):
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
    city = request.args.get("name", "Tucson, AZ")
    weights, gemini_reasoning = _get_weights(city)
    neighborhoods, city_center = _build_neighborhoods(city, weights)

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
    city = request.args.get("city", "Tucson, AZ")
    try:
        return jsonify(get_weights(city))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/neighborhood")
@require_auth
def api_neighborhood():
    city = request.args.get("city", "Tucson, AZ")
    neighborhood = request.args.get("n", "")
    weights, _ = _get_weights(city)

    neighborhoods, _ = _build_neighborhoods(city, weights)
    match = next((n for n in neighborhoods if n["name"].lower() == neighborhood.lower()), None)
    if not match:
        return jsonify({"error": "Neighborhood not found"}), 404

    try:
        match["gemini_explanation"] = get_explanation(
            city, match["name"], match["esi_score"], match["components"]
        )
    except Exception:
        match["gemini_explanation"] = ""

    return jsonify(match)


@app.route("/api/search-log", methods=["POST"])
@require_auth
def api_search_log():
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


def _build_neighborhoods(city: str, weights: dict) -> tuple[list, dict | None]:
    """
    Build neighborhood list from Census tract boundaries.
    Falls back to mock + city center if TIGER is unavailable.
    """
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

    # City-level real data to calibrate absolute scale
    city_aq = city_lp = city_hi = city_eu = None
    try: city_aq = normalize(get_air_quality(city), 0, 200)
    except Exception: pass
    try: city_lp = normalize(get_light_pollution(city), 0, 100)
    except Exception: pass
    try: city_hi = normalize(get_heat_island(city), 0, 10)
    except Exception: pass
    try: city_eu = normalize(get_energy_use(city), 0, 4000)
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
        price = compute_price(esi)

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
