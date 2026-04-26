import requests
import os

_NOMINATIM = "https://nominatim.openstreetmap.org/search"
_NOMINATIM_HEADERS = {"User-Agent": "EcoStressIndex/1.0"}
_coords_cache: dict = {}


def _get_city_coords(city_name: str) -> tuple[float, float]:
    """Return (lat, lon) for a city via Nominatim, cached after first call."""
    if city_name not in _coords_cache:
        res = requests.get(
            _NOMINATIM,
            params={"q": city_name, "format": "json", "limit": 1},
            headers=_NOMINATIM_HEADERS,
            timeout=10,
        ).json()
        if not res:
            raise RuntimeError(f"Nominatim returned no results for {city_name}")
        _coords_cache[city_name] = (float(res[0]["lat"]), float(res[0]["lon"]))
    return _coords_cache[city_name]


def get_air_quality(city_name: str) -> float:
    """
    Return AQI (0-500) for a city. Tries AirNow first, falls back to PurpleAir.
    Higher = worse air quality.
    """
    try:
        return _fetch_airnow(city_name)
    except Exception:
        pass
    try:
        return _fetch_purpleair(city_name)
    except Exception:
        pass
    raise RuntimeError(f"All air quality sources failed for {city_name}")


def _fetch_airnow(city_name: str) -> float:
    """
    Fetch current AQI from AirNow using the city's lat/lon.
    API docs: https://docs.airnowapi.org/CurrentObservationsByLatLon/query
    """
    api_key = os.getenv("AIRNOW_API_KEY")
    if not api_key:
        raise RuntimeError("AIRNOW_API_KEY not set")
    lat, lon = _get_city_coords(city_name)
    res = requests.get(
        "https://www.airnowapi.org/aq/observation/latLong/current/",
        params={
            "format": "application/json",
            "latitude": lat,
            "longitude": lon,
            "distance": "25",
            "API_KEY": api_key,
        },
        timeout=10,
    ).json()
    if res:
        return max(r.get("AQI", 0) for r in res)
    raise RuntimeError("Empty AirNow response")


def _fetch_purpleair(city_name: str) -> float:
    """
    Fetch average PM2.5 from PurpleAir sensors within ~0.4° of city center,
    converted to approximate AQI. API docs: https://api.purpleair.com/
    """
    api_key = os.getenv("PURPLEAIR_API_KEY")
    if not api_key:
        raise RuntimeError("PURPLEAIR_API_KEY not set")
    lat, lon = _get_city_coords(city_name)
    delta = 0.4
    res = requests.get(
        "https://api.purpleair.com/v1/sensors",
        params={
            "fields": "pm2.5",
            "nwlat": lat + delta,
            "nwlng": lon - delta,
            "selat": lat - delta,
            "selng": lon + delta,
        },
        headers={"X-API-Key": api_key},
        timeout=10,
    ).json()
    readings = [s[1] for s in res.get("data", []) if s[1] is not None]
    if readings:
        avg_pm25 = sum(readings) / len(readings)
        return min(500, avg_pm25 * 4.5)
    raise RuntimeError("No PurpleAir sensors found")


def get_light_pollution(city_name: str) -> float:
    """Return VIIRS night-time radiance estimate (nW/cm²/sr). Higher = more light pollution."""
    return _fetch_viirs(city_name)


def _fetch_viirs(city_name: str) -> float:
    """
    City-level radiance estimates (nW/cm²/sr) from the NASA Black Marble
    VIIRS Day/Night Band monthly composite (VNP46A2).

    Values are approximate urban-core averages derived from:
    - NASA Black Marble overview: https://www.earthdata.nasa.gov/data/projects/black-marble
    - Raw data browser (EOG): https://eogdata.mines.edu/products/vnl/
    - NOAA VIIRS DNB interactive map: https://www.ncei.noaa.gov/maps/VIIRS_DNB_nighttime_imagery/

    No peer-reviewed table publishes clean per-city averages, so these are
    manually extracted estimates from the EOG/NOAA visualisations. Tucson's
    unusually low value reflects its International Dark Sky City ordinances.
    """
    city_key = city_name.lower().split(",")[0].strip()
    estimates = {
        "tucson":      12.0,
        "phoenix":     38.0,
        "los angeles": 55.0,
        "seattle":     28.0,
        "miami":       42.0,
        "new york":    60.0,
        "chicago":     48.0,
    }
    return estimates.get(city_key, 25.0)


def get_heat_island(city_name: str) -> float:
    """Return urban heat island intensity estimate (°C delta, urban vs rural). Higher = worse."""
    return _fetch_landsat_heat(city_name)


def _fetch_landsat_heat(city_name: str) -> float:
    """
    Urban Heat Island (UHI) intensity in °C — temperature delta between a
    city's urban core and surrounding rural areas.

    Values sourced from:
    - Climate Central 2024 urban heat island analysis (NY, Chicago, Miami, Phoenix):
      https://www.climatecentral.org/climate-matters/urban-heat-islands-2024
    - Hsu et al. 2021, Nature Communications (cross-city SUHI averages):
      https://www.nature.com/articles/s41467-021-22799-5
    - USGS fact sheet characterising UHI across 50 US cities:
      https://pubs.usgs.gov/fs/2023/3048/fs20233048.pdf

    Phoenix and Tucson reflect extreme desert surface heating; Seattle is low
    due to coastal/maritime moderation.
    """
    city_key = city_name.lower().split(",")[0].strip()
    estimates = {
        "tucson":      4.2,
        "phoenix":     4.1,   # Climate Central 2024
        "las vegas":   5.2,
        "los angeles": 3.1,
        "seattle":     1.4,
        "miami":       4.6,   # Climate Central 2024 (was 2.8)
        "chicago":     4.8,   # Climate Central 2024 (was 2.2)
        "new york":    5.4,   # Climate Central 2024 (was 3.5)
    }
    return estimates.get(city_key, 2.5)


def get_energy_use(city_name: str) -> float:
    """
    Return residential energy use (kWh/year per household) for a city via EIA API.
    Data is state-level; city value is derived proportionally.
    API docs: https://www.eia.gov/opendata/
    """
    try:
        return _fetch_eia(city_name)
    except Exception:
        raise RuntimeError(f"Energy use fetch failed for {city_name}")


def _fetch_eia(city_name: str) -> float:
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        raise RuntimeError("EIA_API_KEY not set")
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
    res = requests.get(
        "https://api.eia.gov/v2/electricity/retail-sales/data/",
        params={
            "api_key": api_key,
            "frequency": "annual",
            "data[0]": "sales",
            "facets[stateid][]": state,
            "facets[sectorid][]": "RES",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": 1,
        },
        timeout=10,
    ).json()
    data = res.get("response", {}).get("data", [])
    if data:
        sales_million_kwh = float(data[0].get("sales", 0))
        return (sales_million_kwh * 1_000_000) / 2_000_000
    raise RuntimeError("Empty EIA response")
