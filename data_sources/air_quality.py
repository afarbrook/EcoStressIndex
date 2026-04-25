import requests
import os


def get_air_quality(city_name: str) -> float:
    """
    Fetch AQI for a city using AirNow API.
    Returns AQI value (0-500 scale; 0=clean, 500=hazardous).
    Falls back to PurpleAir if AirNow fails.
    """
    # Try AirNow first
    try:
        return _fetch_airnow(city_name)
    except Exception:
        pass

    # Try PurpleAir
    try:
        return _fetch_purpleair(city_name)
    except Exception:
        pass

    raise RuntimeError(f"All air quality sources failed for {city_name}")


def _fetch_airnow(city_name: str) -> float:
    api_key = os.getenv("AIRNOW_API_KEY")
    if not api_key:
        raise RuntimeError("AIRNOW_API_KEY not set")

    # AirNow uses zip codes; use a simple city→zip mapping or Nominatim
    url = "https://www.airnowapi.org/aq/observation/zipCode/current/"
    # For demo, use Tucson zip
    params = {
        "format": "application/json",
        "zipCode": "85701",
        "distance": "25",
        "API_KEY": api_key,
    }
    res = requests.get(url, params=params, timeout=10).json()
    if res:
        # Return the PM2.5 or Ozone AQI (whichever is higher)
        return max(r.get("AQI", 0) for r in res)
    raise RuntimeError("Empty AirNow response")


def _fetch_purpleair(city_name: str) -> float:
    api_key = os.getenv("PURPLEAIR_API_KEY")
    if not api_key:
        raise RuntimeError("PURPLEAIR_API_KEY not set")

    # Tucson bounding box as default
    url = "https://api.purpleair.com/v1/sensors"
    params = {
        "fields": "pm2.5",
        "nwlng": -111.1,
        "nwlat": 32.35,
        "selng": -110.7,
        "selat": 32.15,
    }
    headers = {"X-API-Key": api_key}
    res = requests.get(url, params=params, headers=headers, timeout=10).json()
    readings = [s[1] for s in res.get("data", []) if s[1] is not None]
    if readings:
        avg_pm25 = sum(readings) / len(readings)
        # Convert PM2.5 µg/m³ to approximate AQI
        return min(500, avg_pm25 * 4.5)
    raise RuntimeError("No PurpleAir sensors found")
