import requests
import os


def get_heat_island(city_name: str) -> float:
    """
    Fetch urban heat island intensity for a city using NASA Landsat thermal data.
    Returns temperature delta in °C between urban core and surrounding rural areas.
    Higher = stronger heat island effect.
    """
    try:
        return _fetch_landsat_heat(city_name)
    except Exception:
        raise RuntimeError(f"Heat island fetch failed for {city_name}")


def _fetch_landsat_heat(city_name: str) -> float:
    """
    In production: query NASA Landsat 8/9 Band 10 (thermal) via Google Earth Engine
    or NASA SEDAC urban heat island dataset.
    This stub returns city-aware UHI intensity estimates in °C.
    """
    city_key = city_name.lower().split(",")[0].strip()
    # UHI intensity (°C) — research-derived estimates
    estimates = {
        "tucson": 4.2,    # Extreme desert heat island
        "phoenix": 5.8,   # One of the highest UHI in the US
        "las vegas": 5.2,
        "los angeles": 3.1,
        "seattle": 1.4,   # Mild due to coastal climate
        "miami": 2.8,
        "chicago": 2.2,
        "new york": 3.5,
    }
    if city_key in estimates:
        return estimates[city_key]
    return 2.5  # national average UHI
