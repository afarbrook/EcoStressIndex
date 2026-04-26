# Real OSM neighborhood names — Nominatim polygon lookups verified for each.
# Tucson LP scores are low by design: city has strict dark sky ordinances.
MOCK_NEIGHBORHOODS = {
    "tucson": [
        # High stress — industrial/south corridor near I-10 and rail
        {"name": "Menlo Park",        "esi": 0.82, "aq": 0.85, "lp": 0.55, "hi": 0.90, "eu": 0.82},
        {"name": "Barrio Hollywood",  "esi": 0.74, "aq": 0.68, "lp": 0.45, "hi": 0.80, "eu": 0.72},
        {"name": "Barrio Viejo",      "esi": 0.72, "aq": 0.70, "lp": 0.60, "hi": 0.78, "eu": 0.72},
        {"name": "Barrio Anita",      "esi": 0.70, "aq": 0.72, "lp": 0.48, "hi": 0.75, "eu": 0.68},
        # Medium-high — downtown core, dense pavement, commercial lighting
        {"name": "Iron Horse",        "esi": 0.67, "aq": 0.65, "lp": 0.58, "hi": 0.72, "eu": 0.68},
        {"name": "El Presidio",       "esi": 0.68, "aq": 0.65, "lp": 0.65, "hi": 0.72, "eu": 0.68},
        {"name": "Armory Park",       "esi": 0.65, "aq": 0.60, "lp": 0.55, "hi": 0.70, "eu": 0.65},
        {"name": "Pie Allen",         "esi": 0.63, "aq": 0.62, "lp": 0.52, "hi": 0.68, "eu": 0.62},
        # Medium — established residential, mix of housing age
        {"name": "West University",   "esi": 0.60, "aq": 0.55, "lp": 0.60, "hi": 0.65, "eu": 0.62},
        {"name": "Samos",             "esi": 0.58, "aq": 0.55, "lp": 0.45, "hi": 0.62, "eu": 0.58},
        {"name": "Dunbar Spring",     "esi": 0.55, "aq": 0.50, "lp": 0.38, "hi": 0.60, "eu": 0.55},
        {"name": "Glenn",             "esi": 0.52, "aq": 0.50, "lp": 0.42, "hi": 0.58, "eu": 0.55},
        # Lower stress — suburban residential, proximity to mountains/open space
        {"name": "Jefferson Park",    "esi": 0.50, "aq": 0.48, "lp": 0.40, "hi": 0.55, "eu": 0.52},
        {"name": "Miramonte",         "esi": 0.48, "aq": 0.45, "lp": 0.32, "hi": 0.52, "eu": 0.50},
        {"name": "Rincon Heights",    "esi": 0.44, "aq": 0.40, "lp": 0.30, "hi": 0.48, "eu": 0.50},
        {"name": "Sam Hughes",        "esi": 0.42, "aq": 0.35, "lp": 0.28, "hi": 0.45, "eu": 0.55},
    ],
    "boston": [
        {"name": "East Boston",       "esi": 0.80, "aq": 0.85, "lp": 0.72, "hi": 0.78, "eu": 0.78},
        {"name": "Roxbury",           "esi": 0.78, "aq": 0.80, "lp": 0.70, "hi": 0.75, "eu": 0.75},
        {"name": "Dorchester",        "esi": 0.72, "aq": 0.70, "lp": 0.68, "hi": 0.72, "eu": 0.70},
        {"name": "South End",         "esi": 0.62, "aq": 0.60, "lp": 0.72, "hi": 0.55, "eu": 0.60},
        {"name": "Jamaica Plain",     "esi": 0.45, "aq": 0.40, "lp": 0.50, "hi": 0.38, "eu": 0.48},
        {"name": "Back Bay",          "esi": 0.48, "aq": 0.50, "lp": 0.60, "hi": 0.40, "eu": 0.45},
    ],
    "phoenix": [
        {"name": "Maryvale",          "esi": 0.81, "aq": 0.78, "lp": 0.85, "hi": 0.90, "eu": 0.75},
        {"name": "South Mountain",    "esi": 0.67, "aq": 0.62, "lp": 0.65, "hi": 0.78, "eu": 0.62},
        {"name": "Arcadia",           "esi": 0.52, "aq": 0.48, "lp": 0.55, "hi": 0.58, "eu": 0.50},
        {"name": "Ahwatukee",         "esi": 0.45, "aq": 0.40, "lp": 0.45, "hi": 0.55, "eu": 0.42},
        {"name": "Desert View",       "esi": 0.38, "aq": 0.32, "lp": 0.35, "hi": 0.45, "eu": 0.38},
    ],
    "seattle": [
        {"name": "SoDo",              "esi": 0.65, "aq": 0.75, "lp": 0.70, "hi": 0.40, "eu": 0.60},
        {"name": "Capitol Hill",      "esi": 0.48, "aq": 0.55, "lp": 0.60, "hi": 0.25, "eu": 0.45},
        {"name": "Ballard",           "esi": 0.40, "aq": 0.42, "lp": 0.52, "hi": 0.20, "eu": 0.40},
        {"name": "Rainier Valley",    "esi": 0.58, "aq": 0.62, "lp": 0.60, "hi": 0.35, "eu": 0.55},
        {"name": "Fremont",           "esi": 0.35, "aq": 0.38, "lp": 0.45, "hi": 0.18, "eu": 0.35},
    ],
}


def get_mock_for_city(city_name: str) -> list:
    """Return mock neighborhood data for a city, falling back to Tucson if unknown."""
    key = city_name.lower().split(",")[0].strip()
    return MOCK_NEIGHBORHOODS.get(key, MOCK_NEIGHBORHOODS["tucson"])
