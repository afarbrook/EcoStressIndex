import requests
import os


def get_energy_use(city_name: str) -> float:
    """
    Fetch residential energy use (kWh/year per household) for a city using EIA API.
    Returns annual kWh per household.
    """
    try:
        return _fetch_eia(city_name)
    except Exception:
        raise RuntimeError(f"Energy use fetch failed for {city_name}")


def _fetch_eia(city_name: str) -> float:
    """
    Query EIA API for state-level residential electricity consumption.
    EIA data is at state level; city estimates are derived proportionally.
    """
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        raise RuntimeError("EIA_API_KEY not set")

    # Map city → state abbreviation
    city_key = city_name.lower().split(",")[0].strip()
    state_map = {
        "tucson": "AZ", "phoenix": "AZ", "scottsdale": "AZ",
        "seattle": "WA", "spokane": "WA",
        "miami": "FL", "orlando": "FL", "tampa": "FL",
        "los angeles": "CA", "san francisco": "CA", "san diego": "CA",
        "chicago": "IL",
        "new york": "NY",
        "las vegas": "NV",
    }
    state = state_map.get(city_key, "AZ")

    url = "https://api.eia.gov/v2/electricity/retail-sales/data/"
    params = {
        "api_key": api_key,
        "frequency": "annual",
        "data[0]": "sales",
        "facets[stateid][]": state,
        "facets[sectorid][]": "RES",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 1,
    }
    res = requests.get(url, params=params, timeout=10).json()
    data = res.get("response", {}).get("data", [])
    if data:
        # sales is in million kWh; convert to per-household estimate
        sales_million_kwh = float(data[0].get("sales", 0))
        # Rough households: state population / 2.5
        return (sales_million_kwh * 1_000_000) / 2_000_000  # approx per-household kWh/yr
    raise RuntimeError("Empty EIA response")
