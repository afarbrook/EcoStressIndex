import requests
import hashlib
import math

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
CENSUS_GEOCODER = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
TIGER_URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/0/query"
HEADERS = {"User-Agent": "EcoStressIndex/1.0"}

_tiger_cache: dict = {}


def get_city_bbox(city_name: str) -> dict | None:
    params = {"q": city_name, "format": "json", "limit": 1}
    res = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10).json()
    if not res:
        return None
    r = res[0]
    return {
        "lat": float(r["lat"]),
        "lon": float(r["lon"]),
        "bbox": r["boundingbox"],  # [south, north, west, east]
    }


def _get_county_fips(lat: float, lon: float) -> tuple[str, str] | None:
    try:
        res = requests.get(CENSUS_GEOCODER, params={
            "x": lon, "y": lat,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current",
            "layers": "Census Tracts",
            "format": "json",
        }, timeout=10).json()
        tracts = res["result"]["geographies"]["Census Tracts"]
        if tracts:
            return tracts[0]["STATE"], tracts[0]["COUNTY"]
    except Exception:
        pass
    return None


def _polygon_centroid(coordinates: list) -> tuple[float, float]:
    ring = coordinates[0]
    lats = [p[1] for p in ring]
    lons = [p[0] for p in ring]
    return sum(lats) / len(lats), sum(lons) / len(lons)


def get_city_tracts(city_name: str) -> tuple[list, dict | None]:
    """
    Fetch census tract boundaries for a city via Census TIGER API.
    Returns (features, city_center).
    Each feature: {name, geojson, lat, lon}
    Results are cached in-process after first fetch.
    """
    if city_name in _tiger_cache:
        return _tiger_cache[city_name]

    city_info = get_city_bbox(city_name)
    if not city_info:
        _tiger_cache[city_name] = ([], None)
        return [], None

    city_center = {"lat": city_info["lat"], "lon": city_info["lon"]}
    s, n, w, e = [float(x) for x in city_info["bbox"]]

    fips = _get_county_fips(city_info["lat"], city_info["lon"])
    if not fips:
        _tiger_cache[city_name] = ([], city_center)
        return [], city_center

    state_fips, county_fips = fips

    try:
        res = requests.get(TIGER_URL, params={
            "where": f"STATE='{state_fips}' AND COUNTY='{county_fips}'",
            "outFields": "GEOID,BASENAME",
            "returnGeometry": True,
            "outSR": 4326,
            "f": "geojson",
        }, timeout=30).json()

        features = []
        for feat in res.get("features", []):
            geo = feat.get("geometry")
            props = feat.get("properties", {})
            if not geo:
                continue

            # Compute centroid
            coords = geo.get("coordinates", [])
            if geo["type"] == "Polygon" and coords:
                clat, clon = _polygon_centroid(coords)
            elif geo["type"] == "MultiPolygon" and coords:
                clat, clon = _polygon_centroid(coords[0])
            else:
                continue

            # Filter to city bounding box
            if not (s <= clat <= n and w <= clon <= e):
                continue

            tract_id = props.get("BASENAME", "")
            features.append({
                "name": f"Tract {tract_id}",
                "geojson": geo,
                "lat": clat,
                "lon": clon,
            })

        _tiger_cache[city_name] = (features, city_center)
        return features, city_center

    except Exception:
        _tiger_cache[city_name] = ([], city_center)
        return [], city_center


def tract_components(tract_lat: float, tract_lon: float,
                     city_lat: float, city_lon: float) -> dict:
    """
    Assign ESI component values for a census tract based on geographic position.
    Deterministic: same coordinates always produce the same scores.
    Model: higher stress near downtown and south of center, lower toward suburbs.
    """
    dlat = city_lat - tract_lat   # positive = south of center → higher stress
    distance = math.sqrt(dlat**2 + (tract_lon - city_lon)**2)

    base = max(0.25, 0.70 - distance * 2.8)
    south_gradient = max(-0.12, min(0.18, dlat * 0.9))

    seed = f"{tract_lat:.4f},{tract_lon:.4f}"

    def _noise(tag: str, spread: float = 0.22) -> float:
        h = int(hashlib.md5((seed + tag).encode()).hexdigest()[:6], 16) / 0xFFFFFF
        return (h - 0.5) * spread

    esi_base = max(0.15, min(0.90, base + south_gradient + _noise("esi")))

    return {
        "air_quality":     round(max(0.1, min(0.95, esi_base + _noise("aq", 0.18))), 2),
        "light_pollution": round(max(0.1, min(0.95, esi_base * 0.85 + _noise("lp", 0.14))), 2),
        "heat_island":     round(max(0.1, min(0.95, esi_base + _noise("hi", 0.14))), 2),
        "energy_use":      round(max(0.1, min(0.95, esi_base + _noise("eu", 0.14))), 2),
    }
