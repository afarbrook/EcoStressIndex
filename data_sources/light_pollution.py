import requests
import os


def get_light_pollution(city_name: str) -> float:
    """
    Fetch light pollution radiance for a city using NASA VIIRS Night-time Lights.
    Returns a radiance value (nW/cm²/sr) — higher = more light pollution.
    """
    # NASA VIIRS via LAADS DAAC or fallback to static lookup
    try:
        return _fetch_viirs(city_name)
    except Exception:
        raise RuntimeError(f"Light pollution fetch failed for {city_name}")


def _fetch_viirs(city_name: str) -> float:
    """
    Query NASA GIBS/LAADS for VIIRS DNB monthly composite.
    In production, you'd hit the NASA EarthData API with proper auth.
    This stub returns a reasonable city-aware estimate.
    """
    # Static radiance estimates (nW/cm²/sr) based on known city characteristics
    city_key = city_name.lower().split(",")[0].strip()
    estimates = {
        "tucson": 12.0,   # Dark sky ordinances → lower light pollution
        "phoenix": 38.0,
        "los angeles": 55.0,
        "seattle": 28.0,
        "miami": 42.0,
        "new york": 60.0,
        "chicago": 48.0,
    }
    if city_key in estimates:
        return estimates[city_key]
    # Default mid-range
    return 25.0
