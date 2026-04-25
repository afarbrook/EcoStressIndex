from flask import Flask, render_template, request, jsonify, redirect
from functools import wraps
from supabase import create_client
from dotenv import load_dotenv
import os

from esi import compute_esi, compute_price, normalize
from gemini_weights import get_weights
from gemini_explain import get_explanation
from geo import get_neighborhoods_geojson, get_city_bbox
from mock.mock_data import get_mock_for_city
from data_sources.air_quality import get_air_quality
from data_sources.light_pollution import get_light_pollution
from data_sources.heat_island import get_heat_island
from data_sources.energy_use import get_energy_use

load_dotenv()

app = Flask(__name__)

supabase_client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


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
    return render_template("login.html")


@app.route("/map")
def map_page():
    return render_template("map.html")


@app.route("/api/city")
@require_auth
def api_city():
    city = request.args.get("name", "Tucson, AZ")

    # Try to get Gemini weights; fall back to defaults
    try:
        weights_data = get_weights(city)
        weights = {k: v for k, v in weights_data.items() if k != "reasoning"}
        gemini_reasoning = weights_data.get("reasoning", "")
    except Exception:
        weights = {"air_quality": 0.25, "light_pollution": 0.25, "heat_island": 0.25, "energy_use": 0.25}
        gemini_reasoning = "Default equal weights applied (Gemini unavailable)."

    # Try Supabase cache first
    try:
        cached = supabase_client.table("esi_cache").select("*").eq("city", city).execute()
        if cached.data:
            neighborhoods = []
            for row in cached.data:
                neighborhoods.append({
                    "id": row["neighborhood"].lower().replace(" ", "-"),
                    "name": row["neighborhood"],
                    "geojson": None,
                    "esi_score": row["esi_score"],
                    "dynamic_price_per_kwh": row["dynamic_price"],
                    "components": row["component_scores"],
                })
            return jsonify({"city": city, "weights": weights, "gemini_reasoning": gemini_reasoning, "neighborhoods": neighborhoods})
    except Exception:
        pass

    # Fetch real data / fall back to mock
    neighborhoods = _build_neighborhoods(city, weights)

    # Cache to Supabase
    try:
        for n in neighborhoods:
            supabase_client.table("esi_cache").upsert({
                "city": city,
                "neighborhood": n["name"],
                "esi_score": n["esi_score"],
                "component_scores": n["components"],
                "weights": weights,
                "dynamic_price": n["dynamic_price_per_kwh"],
            }).execute()
    except Exception:
        pass

    return jsonify({"city": city, "weights": weights, "gemini_reasoning": gemini_reasoning, "neighborhoods": neighborhoods})


@app.route("/api/weights")
@require_auth
def api_weights():
    city = request.args.get("city", "Tucson, AZ")
    try:
        data = get_weights(city)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/neighborhood")
@require_auth
def api_neighborhood():
    city = request.args.get("city", "Tucson, AZ")
    neighborhood = request.args.get("n", "")
    try:
        weights_data = get_weights(city)
        weights = {k: v for k, v in weights_data.items() if k != "reasoning"}
    except Exception:
        weights = {"air_quality": 0.25, "light_pollution": 0.25, "heat_island": 0.25, "energy_use": 0.25}

    neighborhoods = _build_neighborhoods(city, weights)
    match = next((n for n in neighborhoods if n["name"].lower() == neighborhood.lower()), None)
    if not match:
        return jsonify({"error": "Neighborhood not found"}), 404

    try:
        match["gemini_explanation"] = get_explanation(city, match["name"], match["esi_score"], match["components"])
    except Exception:
        match["gemini_explanation"] = ""

    return jsonify(match)


@app.route("/api/simulate")
@require_auth
def api_simulate():
    city = request.args.get("city", "Tucson, AZ")
    neighborhood = request.args.get("neighborhood", "")

    try:
        from simulation.simulate import run_simulation
        result = run_simulation(city, neighborhood)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

def _build_neighborhoods(city: str, weights: dict) -> list:
    """Build neighborhood list from real APIs with mock fallback."""
    mock_list = get_mock_for_city(city)

    try:
        geo_data = get_neighborhoods_geojson(city)
    except Exception:
        geo_data = None

    results = []
    for item in mock_list:
        name = item["name"]

        # Try real data sources, fall back to mock values
        try:
            aq_raw = get_air_quality(city)
        except Exception:
            aq_raw = item["aq"] * 100  # denormalize mock

        try:
            lp_raw = get_light_pollution(city)
        except Exception:
            lp_raw = item["lp"] * 50

        try:
            hi_raw = get_heat_island(city)
        except Exception:
            hi_raw = item["hi"] * 5

        try:
            eu_raw = get_energy_use(city)
        except Exception:
            eu_raw = item["eu"] * 2000

        components = {
            "air_quality_normalized": normalize(aq_raw, 0, 200),
            "light_pollution_normalized": normalize(lp_raw, 0, 100),
            "heat_island_normalized": normalize(hi_raw, 0, 10),
            "energy_use_normalized": normalize(eu_raw, 0, 4000),
        }

        esi = compute_esi(components, weights)
        price = compute_price(esi)

        # Extract display-friendly component scores
        display_components = {
            "air_quality": round(components["air_quality_normalized"], 2),
            "light_pollution": round(components["light_pollution_normalized"], 2),
            "heat_island": round(components["heat_island_normalized"], 2),
            "energy_use": round(components["energy_use_normalized"], 2),
        }

        results.append({
            "id": name.lower().replace(" ", "-"),
            "name": name,
            "geojson": None,
            "esi_score": round(esi, 2),
            "dynamic_price_per_kwh": price,
            "components": display_components,
        })

    return results


if __name__ == "__main__":
    app.run(debug=True)
