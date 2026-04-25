import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "EcoStressIndex/1.0"}


def get_city_bbox(city_name: str) -> dict | None:
    """Get bounding box for any city via Nominatim."""
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


def get_neighborhoods_geojson(city_name: str) -> dict | None:
    """Fetch neighborhood polygons for any city via Overpass API."""
    bbox = get_city_bbox(city_name)
    if not bbox:
        return None
    s, n, w, e = bbox["bbox"]
    query = f"""
    [out:json][timeout:25];
    (
      relation["boundary"="administrative"]["admin_level"="10"]({s},{w},{n},{e});
      relation["place"="neighbourhood"]({s},{w},{n},{e});
    );
    out body; >; out skel qt;
    """
    res = requests.post(OVERPASS_URL, data=query, timeout=30)
    return res.json()
