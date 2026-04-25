MOCK_NEIGHBORHOODS = {
    "tucson": [
        {"name": "Downtown",        "esi": 0.74, "aq": 0.68, "lp": 0.80, "hi": 0.75, "eu": 0.71},
        {"name": "University Area", "esi": 0.61, "aq": 0.55, "lp": 0.72, "hi": 0.58, "eu": 0.60},
        {"name": "Foothills",       "esi": 0.31, "aq": 0.20, "lp": 0.25, "hi": 0.40, "eu": 0.35},
        {"name": "South Side",      "esi": 0.82, "aq": 0.85, "lp": 0.70, "hi": 0.88, "eu": 0.80},
        {"name": "Midtown",         "esi": 0.52, "aq": 0.50, "lp": 0.55, "hi": 0.50, "eu": 0.53},
        {"name": "Rincon Heights",  "esi": 0.44, "aq": 0.40, "lp": 0.38, "hi": 0.50, "eu": 0.45},
    ],
    "phoenix": [
        {"name": "Downtown Phoenix",   "esi": 0.81, "aq": 0.78, "lp": 0.85, "hi": 0.90, "eu": 0.75},
        {"name": "Scottsdale",         "esi": 0.55, "aq": 0.45, "lp": 0.60, "hi": 0.65, "eu": 0.50},
        {"name": "Tempe",              "esi": 0.67, "aq": 0.62, "lp": 0.70, "hi": 0.72, "eu": 0.63},
        {"name": "Mesa",               "esi": 0.60, "aq": 0.55, "lp": 0.62, "hi": 0.68, "eu": 0.57},
        {"name": "Gilbert",            "esi": 0.42, "aq": 0.35, "lp": 0.40, "hi": 0.50, "eu": 0.40},
    ],
    "seattle": [
        {"name": "Capitol Hill",   "esi": 0.48, "aq": 0.55, "lp": 0.60, "hi": 0.25, "eu": 0.45},
        {"name": "Ballard",        "esi": 0.40, "aq": 0.42, "lp": 0.52, "hi": 0.20, "eu": 0.40},
        {"name": "SoDo",           "esi": 0.65, "aq": 0.75, "lp": 0.70, "hi": 0.40, "eu": 0.60},
        {"name": "Fremont",        "esi": 0.35, "aq": 0.38, "lp": 0.45, "hi": 0.18, "eu": 0.35},
        {"name": "Rainier Valley", "esi": 0.58, "aq": 0.62, "lp": 0.60, "hi": 0.35, "eu": 0.55},
    ],
}


def get_mock_for_city(city_name: str) -> list:
    """Return mock neighborhood data for a city. Falls back to Tucson."""
    key = city_name.lower().split(",")[0].strip()
    return MOCK_NEIGHBORHOODS.get(key, MOCK_NEIGHBORHOODS["tucson"])
