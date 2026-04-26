# EcoStress Index (ESI)

A web app that scores city neighborhoods on environmental burden using real sensor and satellite data, with AI-generated weights via Google Gemini. Built as a B2B tool for energy companies to implement dynamic pricing — greener neighborhoods pay less, higher-impact areas pay more.

---

## How It Works

### The ESI Score
Every neighborhood gets an Environmental Stress Index (ESI) score between 0 and 1 (higher = worse). It's a weighted sum of four components:

```
ESI = w1(Air Quality) + w2(Light Pollution) + w3(Heat Island) + w4(Energy Use)
```

What makes it adaptive: **Gemini generates the weights per city**. Tucson gets a high heat island weight because of the Sonoran Desert. Seattle gets a high air quality weight because of wildfire smoke. The model isn't hardcoded — it reasons about each city's climate and geography.

### Dynamic Pricing
Once a neighborhood has an ESI score, its electricity price is:

```
Price = BaseRate × (1 + alpha × ESI)
```

- ESI of 0 → base rate (e.g. $0.12/kWh)
- ESI of 1 → base rate + 50% premium (e.g. $0.18/kWh)
- `alpha` (0.5 by default) and `BaseRate` are configurable — intended to be set by the utility company

### Data Sources

| Component | Source | Notes |
|---|---|---|
| Air Quality | **AirNow API** (primary) | Live AQI via lat/lon — requires `AIRNOW_API_KEY` |
| Air Quality | **PurpleAir API** (fallback) | PM2.5 from local sensors — requires `PURPLEAIR_API_KEY` |
| Light Pollution | NASA VIIRS estimates | City-level radiance (nW/cm²/sr) from Black Marble composites. Real VIIRS data lives at [eogdata.mines.edu](https://eogdata.mines.edu/products/vnl/) — currently city-level estimates |
| Heat Island | NASA Landsat / Climate Central estimates | UHI intensity in °C. Values sourced from [Climate Central 2024](https://www.climatecentral.org/climate-matters/urban-heat-islands-2024) and [Hsu et al. 2021](https://www.nature.com/articles/s41467-021-22799-5) |
| Energy Use | **EIA API** | State-level residential kWh/household — requires `EIA_API_KEY` |
| Neighborhood Boundaries | **Census TIGER API** | Real tract polygons for any US city, no API key needed |
| Geocoding | **Nominatim (OpenStreetMap)** | City bounding boxes and lat/lon — no API key needed |
| AI Weights | **Google Gemini** (`gemini-4-31b-it`) | Generates component weights + reasoning per city — requires `GEMINI_API_KEY` |
| AI Explanation | **Google Gemini** (`gemini-4-31b-it`) | Natural language explanation per neighborhood on click |
| Auth + DB | **Supabase** | Email/password auth, ESI score caching, search logging |

---

## Project Structure

```
EcoStressIndex/
├── app.py                  # Flask app — all routes and request handling
├── esi.py                  # ESI formula and dynamic pricing calculation
├── geo.py                  # City bounding boxes (Nominatim) + Census TIGER tract fetching
├── gemini_weights.py       # Gemini — generates per-city ESI weights
├── gemini_explain.py       # Gemini — neighborhood natural language explanation
├── data_sources.py         # AirNow, PurpleAir, VIIRS, Landsat, EIA API calls
├── mock_data.py            # Realistic fallback data for known cities
├── simulation/
│   └── simulate.py         # Energy behavior simulation (stub — see Person B)
├── templates/
│   ├── login.html          # Auth page
│   └── map.html            # Main map page
├── static/
│   ├── map.js              # Leaflet map, neighborhood rendering, side panel
│   ├── search.js           # City search handler
│   └── style.css
├── requirements.txt
├── Procfile                # For Railway / Heroku deployment
└── .env                    # API keys — never commit this
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- A Supabase project (free tier is fine)
- API keys (see Environment Variables below)

### 1. Clone and install

```bash
git clone https://github.com/afarbrook/EcoStressIndex.git
cd EcoStressIndex
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Then fill in your keys (see Environment Variables section below).

### 3. Set up Supabase

In your Supabase project, open the SQL editor and run:

```sql
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

CREATE TABLE search_log (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid REFERENCES auth.users,
  query text NOT NULL,
  city text,
  searched_at timestamp DEFAULT now()
);

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

Enable **Email auth** under Authentication → Providers in your Supabase dashboard.

### 4. Run

```bash
flask run
```

Open [http://localhost:5000](http://localhost:5000), create an account, and search any US city.

---

## Environment Variables

Create a `.env` file in the project root with the following:

```env
# Google Gemini — weights generation and neighborhood explanations
# Get yours at: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_key_here

# Supabase — auth and database
# Found in: Supabase dashboard → Project Settings → API
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=your_anon_key_here

# AirNow — live air quality data (primary AQ source)
# Register at: https://docs.airnowapi.org/
AIRNOW_API_KEY=your_key_here

# PurpleAir — fallback AQ from local sensors
# Register at: https://develop.purpleair.com/
PURPLEAIR_API_KEY=your_key_here

# EIA — residential energy use by state
# Register at: https://www.eia.gov/opendata/register.php
EIA_API_KEY=your_key_here
```

The app degrades gracefully — if an API key is missing or a call fails, it falls back to research-based estimates silently. The only hard requirement for a working demo is `GEMINI_API_KEY` and Supabase.

---

## Deploying to Railway (with a custom domain)

1. Push your repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select this repo — Railway auto-detects Flask via the `Procfile`
4. Go to **Variables** and add all your `.env` keys
5. Once deployed, go to **Settings → Custom Domain** and enter your domain
6. In your domain registrar, add a CNAME record:
   ```
   Type:  CNAME
   Name:  @ (or www)
   Value: your-app.up.railway.app
   ```
7. DNS propagation takes a few minutes to an hour

---

## API Reference

All `/api/*` routes require a valid Supabase JWT in the `Authorization: Bearer <token>` header.

| Method | Endpoint | Params | Description |
|---|---|---|---|
| `GET` | `/api/city` | `name`, `base_rate` | All neighborhoods + ESI scores for a city |
| `GET` | `/api/weights` | `city` | Gemini weights and reasoning for a city |
| `GET` | `/api/neighborhood` | `city`, `n`, `base_rate` | Detail + Gemini explanation for one neighborhood |
| `GET` | `/api/simulate` | `city`, `neighborhood` | Energy simulation results (Person B) |
| `POST` | `/api/search-log` | `{ query, city }` | Log a search to Supabase |

### `/api/city` response shape

```json
{
  "city": "Tucson, AZ",
  "city_center": { "lat": 32.22, "lon": -110.97 },
  "weights": {
    "air_quality": 0.28,
    "light_pollution": 0.12,
    "heat_island": 0.35,
    "energy_use": 0.25
  },
  "gemini_reasoning": "Heat island weighted highest due to Tucson's extreme desert heat...",
  "neighborhoods": [
    {
      "id": "downtown-tucson",
      "name": "Downtown Tucson",
      "geojson": { "type": "Polygon", "coordinates": [[...]] },
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

## Fallback Behavior

No API key? No problem for a demo. The app fails silently and falls back at every layer:

- **Census TIGER fails** → uses mock neighborhood data for Tucson, Boston, Phoenix, Seattle
- **AirNow fails** → tries PurpleAir → falls back to geographic estimate
- **Gemini fails** → uses equal weights (0.25 each), no explanation text
- **EIA fails** → uses geographic estimate based on city position

---

```
