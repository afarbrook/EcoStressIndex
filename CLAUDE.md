# EcoStress Index (ESI) — Hackathon Project

## Project Overview
A scalable web app that scores any city's neighborhoods on environmental burden using
real sensor/satellite data and AI-generated weights via Google Gemini. Designed as a
B2B tool for energy companies to implement dynamic pricing — greener neighborhoods pay
less, higher-impact areas pay more. Launches with Tucson, AZ but works for any city.

---

## Team Split

| Person A (Alex) — This file's focus | Person B — Simulation |
|---|---|
| Supabase auth + login page | Energy use simulation model |
| City search + Leaflet map | Predict post-pricing energy behavior |
| Neighborhood ESI scoring | Feed simulation results back to `/api/simulate` |
| Dynamic pricing display | Show before/after energy use projections |
| Gemini weight generation | Gemini-assisted simulation reasoning |

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| Database / Auth | Supabase (Postgres + Auth) |
| AI Weights | Google Gemini API (gemini-1.5-flash) |
| Frontend | HTML + Leaflet.js + Vanilla JS (no build step) |
| Neighborhood Boundaries | OpenStreetMap Nominatim + Overpass API (any city) |
| Map tiles | OpenStreetMap (free) |
| Data sources | PurpleAir, AirNow, NASA VIIRS, NASA Landsat/SEDAC |

---

## Project Structure

```
ecostress/
├── app.py                        # Flask app, all routes
├── esi.py                        # ESI scoring + pricing logic
├── gemini_weights.py             # Gemini — dynamic weight generation
├── gemini_explain.py             # Gemini — neighborhood natural language explanation
├── geo.py                        # City/neighborhood boundary fetching (Nominatim)
├── data_sources/
│   ├── air_quality.py            # PurpleAir + AirNow API calls
│   ├── light_pollution.py        # NASA VIIRS
│   ├── heat_island.py            # NASA Landsat thermal
│   └── energy_use.py             # EIA API
├── mock/
│   └── mock_data.py              # Realistic fallback data generator (city-aware)
├── templates/
│   ├── login.html                # Login / signup page
│   └── map.html                  # Main map page (post-auth)
├── static/
│   ├── map.js                    # Leaflet map logic
│   ├── search.js                 # City/address search
│   └── style.css
├── simulation/                   # Person B's module
│   ├── simulate.py               # Energy behavior simulation
│   └── README.md                 # Person B's docs
├── requirements.txt
└── .env                          # API keys — never commit
```

---

## Pages

### 1. Login Page (`/`) → `login.html`
- Email + password login via Supabase Auth
- Sign up option
- On success → redirect to `/map`
- Store Supabase session token in localStorage
- All `/api/*` routes require valid Supabase JWT

### 2. Map Page (`/map`) → `map.html`
- Protected route — redirect to `/` if not authenticated
- Search bar at top: accepts city name or address (e.g. "Tucson, AZ" or "4th Ave, Tucson")
- On search:
  - Geocode via Nominatim → get lat/lng + bounding box
  - Fetch neighborhood boundaries for that city via Overpass API
  - Load ESI scores for each neighborhood via `/api/city`
  - Render colored polygons on Leaflet map (green → red)
- Click neighborhood polygon:
  - Side panel opens showing:
    - Neighborhood name
    - ESI score + visual gauge
    - Component breakdown (AQ, LP, HI, EU) with weights
    - Recommended price per kWh
    - Gemini AI explanation (why this score)
    - Simulation panel (Person B's output — before/after pricing projection)

---

## Supabase Setup

### Tables

```sql
-- Users are handled by Supabase Auth automatically

-- Cache ESI scores so you don't re-fetch APIs on every request
CREATE TABLE esi_cache (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  city text NOT NULL,
  neighborhood text NOT NULL,
  esi_score float NOT NULL,
  component_scores jsonb NOT NULL,
  weights jsonb NOT NULL,
  dynamic_price float NOT NULL,
  computed_at timestamp DEFAULT now(),
  UNIQUE(city, neighborhood)
);

-- Log searches for analytics / demo purposes
CREATE TABLE search_log (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid REFERENCES auth.users,
  query text NOT NULL,
  city text,
  searched_at timestamp DEFAULT now()
);

-- Store simulation results (Person B writes to this)
CREATE TABLE simulations (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  city text NOT NULL,
  neighborhood text NOT NULL,
  baseline_kwh float,
  projected_kwh float,
  price_applied float,
  reduction_pct float,
  simulated_at timestamp DEFAULT now()
);
```

### Auth Flow (Frontend)
```javascript
// login.html
const { data, error } = await supabase.auth.signInWithPassword({
  email, password
});
if (data.session) window.location.href = "/map";

// map.html — protect route
const { data: { session } } = await supabase.auth.getSession();
if (!session) window.location.href = "/";

// Pass JWT to Flask API
const res = await fetch("/api/city", {
  headers: { "Authorization": `Bearer ${session.access_token}` }
});
```

### Auth Verification (Flask)
```python
from supabase import create_client
from functools import wraps
import os

supabase_client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            user = supabase_client.auth.get_user(token)
            request.user = user
        except:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
```

---

## Scalable City Fetching (`geo.py`)

This is what makes it work for ANY city — no hardcoded boundaries.

```python
import requests

def get_city_bbox(city_name: str) -> dict:
    """Get bounding box for any city via Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "EcoStressIndex/1.0"}
    res = requests.get(url, params=params, headers=headers).json()
    if not res:
        return None
    r = res[0]
    return {
        "lat": float(r["lat"]),
        "lon": float(r["lon"]),
        "bbox": r["boundingbox"]  # [south, north, west, east]
    }

def get_neighborhoods_geojson(city_name: str) -> dict:
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
    res = requests.post("https://overpass-api.de/api/interpreter", data=query)
    return res.json()
```

---

## Gemini Integration (`gemini_weights.py`)

Gemini generates weights based on city context — Tucson gets high heat island weight,
Seattle gets high AQ weight, Miami gets high energy weight. Fully adaptive.

```python
import google.generativeai as genai
import json, os

def get_weights(city_name: str) -> dict:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    You are an environmental data scientist building a city pollution scoring model.
    For the city of {city_name}, assign weights to each factor below for an
    Environmental Stress Index (ESI). Weights must sum to exactly 1.0.
    Consider the city's climate, geography, and known environmental challenges.
    Return ONLY valid JSON, no explanation outside the JSON.

    {{
        "air_quality": 0.00,
        "light_pollution": 0.00,
        "heat_island": 0.00,
        "energy_use": 0.00,
        "reasoning": "one sentence explaining why these weights fit this city"
    }}
    """

    response = model.generate_content(prompt)
    text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(text)

# Example outputs:
# Tucson:  heat_island=0.35, energy=0.25, AQ=0.28, LP=0.12
# Seattle: AQ=0.40, heat_island=0.15, energy=0.25, LP=0.20
# Phoenix: heat_island=0.40, energy=0.30, AQ=0.20, LP=0.10
```

---

## ESI Formula + Pricing (`esi.py`)

```python
def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0
    return max(0, min(1, (value - min_val) / (max_val - min_val)))

def compute_esi(components: dict, weights: dict) -> float:
    """
    ESI = w1(AQ) + w2(LP) + w3(HI) + w4(EU)
    All components normalized to [0, 1] — higher = worse
    """
    return (
        weights["air_quality"]     * components["air_quality_normalized"] +
        weights["light_pollution"] * components["light_pollution_normalized"] +
        weights["heat_island"]     * components["heat_island_normalized"] +
        weights["energy_use"]      * components["energy_use_normalized"]
    )

def compute_price(esi_score: float, base_rate: float = 0.12, alpha: float = 0.5) -> float:
    """
    Price = BaseRate x (1 + alpha x ESI)
    ESI of 0 -> base rate ($0.12/kWh)
    ESI of 1 -> base rate + 50% premium ($0.18/kWh)
    alpha is tunable by the energy company
    """
    return round(base_rate * (1 + alpha * esi_score), 4)
```

---

## Flask API Routes (`app.py`)

```
GET  /                              # Login page
GET  /map                           # Map page (auth required)

GET  /api/city?name=Tucson,AZ       # All neighborhoods + ESI scores for a city
GET  /api/weights?city=Tucson,AZ    # Gemini weights + reasoning for a city
GET  /api/neighborhood?city=X&n=Y   # Detail for one neighborhood
GET  /api/simulate?city=X&n=Y       # Person B's simulation results
POST /api/search-log                # Log search query to Supabase
```

### `/api/city` response shape
```json
{
  "city": "Tucson, AZ",
  "weights": { "heat_island": 0.35, "air_quality": 0.28, "light_pollution": 0.12, "energy_use": 0.25 },
  "gemini_reasoning": "Heat island weighted highest due to Tucson's extreme desert heat...",
  "neighborhoods": [
    {
      "id": "downtown-tucson",
      "name": "Downtown Tucson",
      "geojson": { "...": "..." },
      "esi_score": 0.74,
      "dynamic_price_per_kwh": 0.164,
      "components": {
        "air_quality": 0.68,
        "light_pollution": 0.80,
        "heat_island": 0.75,
        "energy_use": 0.71
      }
    }
  ]
}
```

---

## Frontend Map Logic (`map.js`)

```javascript
// Search handler
async function searchCity(query) {
  const res = await fetch(`/api/city?name=${encodeURIComponent(query)}`, {
    headers: { "Authorization": `Bearer ${getToken()}` }
  });
  const data = await res.json();
  renderNeighborhoods(data.neighborhoods);
  showWeightsPanel(data.weights, data.gemini_reasoning);
}

// Color scale: green (0) -> yellow (0.5) -> red (1)
function esiToColor(score) {
  const r = Math.round(255 * score);
  const g = Math.round(255 * (1 - score));
  return `rgb(${r}, ${g}, 0)`;
}

// Render GeoJSON polygons
function renderNeighborhoods(neighborhoods) {
  neighborhoods.forEach(n => {
    L.geoJSON(n.geojson, {
      style: { fillColor: esiToColor(n.esi_score), fillOpacity: 0.6, weight: 1 }
    })
    .bindPopup(`<b>${n.name}</b><br>ESI: ${n.esi_score.toFixed(2)}`)
    .on("click", () => openSidePanel(n))
    .addTo(map);
  });
}

// Side panel on neighborhood click
function openSidePanel(neighborhood) {
  document.getElementById("panel-name").textContent = neighborhood.name;
  document.getElementById("panel-esi").textContent = neighborhood.esi_score.toFixed(2);
  document.getElementById("panel-price").textContent =
    `$${neighborhood.dynamic_price_per_kwh}/kWh`;
  loadSimulation(neighborhood.id);
}
```

---

## Simulation Module (Person B)

Person B owns `simulation/simulate.py` and the `/api/simulate` route.

**What it does:**
Given a neighborhood's current ESI score and the new dynamic price, simulate how energy
consumption is expected to change. Feed results into the `simulations` Supabase table.

**API contract Alex's frontend expects:**
```json
GET /api/simulate?city=Tucson,AZ&neighborhood=Downtown%20Tucson

{
  "neighborhood": "Downtown Tucson",
  "baseline_kwh": 1250,
  "projected_kwh": 987,
  "reduction_pct": 21.0,
  "price_applied": 0.164,
  "confidence": 0.82,
  "gemini_insight": "A 37% price premium is projected to reduce consumption by..."
}
```

**Side panel HTML Alex renders:**
```html
<div id="simulation-panel">
  <h3>Projected Impact After Pricing</h3>
  <p>Current avg use: <span id="baseline">--</span> kWh/mo</p>
  <p>Projected after pricing: <span id="projected">--</span> kWh/mo</p>
  <p>Estimated reduction: <span id="reduction">--</span>%</p>
  <p class="ai-note" id="sim-insight"></p>
</div>
```

---

## Environment Variables (`.env`)

```
GEMINI_API_KEY=your_key_here
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=your_anon_key_here
PURPLEAIR_API_KEY=your_key_here
AIRNOW_API_KEY=your_key_here
EIA_API_KEY=your_key_here
```

---

## Build Order (Alex, ~10 hours)

| Time | Task |
|---|---|
| Hour 1 | Flask skeleton, .env, Supabase project setup, tables created |
| Hour 2 | Login page + Supabase auth working (login redirects to /map) |
| Hour 3 | Leaflet map rendering, city search bar, Nominatim geocoding |
| Hour 4 | Overpass neighborhood boundary fetching OR mock Tucson GeoJSON |
| Hour 5 | Gemini weights working, ESI + pricing formula in esi.py |
| Hour 6 | /api/city route returning scores, map polygons colored green-red |
| Hour 7 | Side panel — ESI breakdown + price on neighborhood click |
| Hour 8 | Connect simulation panel, Supabase search logging |
| Hour 9 | Polish UI, loading states, error handling, mobile layout |
| Hour 10 | Integration test with Person B, Devpost writeup, demo prep |

---

## Mock Data Fallback

Always have this ready. If any API call fails, fall back silently.

```python
MOCK_NEIGHBORHOODS = {
    "tucson": [
        {"name": "Downtown",        "esi": 0.74, "aq": 0.68, "lp": 0.80, "hi": 0.75, "eu": 0.71},
        {"name": "University Area", "esi": 0.61, "aq": 0.55, "lp": 0.72, "hi": 0.58, "eu": 0.60},
        {"name": "Foothills",       "esi": 0.31, "aq": 0.20, "lp": 0.25, "hi": 0.40, "eu": 0.35},
        {"name": "South Side",      "esi": 0.82, "aq": 0.85, "lp": 0.70, "hi": 0.88, "eu": 0.80},
        {"name": "Midtown",         "esi": 0.52, "aq": 0.50, "lp": 0.55, "hi": 0.50, "eu": 0.53},
        {"name": "Rincon Heights",  "esi": 0.44, "aq": 0.40, "lp": 0.38, "hi": 0.50, "eu": 0.45},
    ]
}

def get_mock_for_city(city_name: str) -> list:
    key = city_name.lower().split(",")[0].strip()
    return MOCK_NEIGHBORHOODS.get(key, MOCK_NEIGHBORHOODS["tucson"])
```

---

## Judging Talking Points

- **Scalable by design:** Works for any city in the world via Nominatim + Overpass.
  Not hardcoded to Tucson. Pitch as a national or global utility platform.
- **AI is load-bearing:** Gemini sets the model parameters based on regional climate
  context — Tucson != Seattle != Miami. That's adaptive AI, not a chatbot wrapper.
- **Real product feel:** Supabase login + user accounts makes this look like something
  a utility company would actually buy, not a hackathon script.
- **Feedback loop story:** Pricing changes behavior → behavior feeds back into next ESI
  score → creates a policy feedback loop. Compelling systems thinking.
- **Local relevance:** Tucson's dark sky ordinances make LP variation meaningful.
  Heat island is a documented public health crisis in the Sonoran Desert.
- **Real data where it counts:** PurpleAir has live Tucson sensors. Lead with that.
