# Simulation Module — Person B

This module owns the `/api/simulate` endpoint logic.

## What it does

Given a neighborhood's current ESI score and the new dynamic price applied by the
ESI pricing engine, simulate how residential energy consumption is expected to change.

## Files

- `simulate.py` — main entry point, `run_simulation(city, neighborhood)` function
- This README

## API contract

Alex's frontend calls:
```
GET /api/simulate?city=Tucson,AZ&neighborhood=Downtown%20Tucson
```

Expected JSON response:
```json
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

## Supabase table

Write results to `simulations` table:
```sql
INSERT INTO simulations (city, neighborhood, baseline_kwh, projected_kwh, price_applied, reduction_pct)
VALUES (...);
```

## Implementation notes

- Use price elasticity of demand for residential electricity (~-0.2 to -0.4)
- Optionally call Gemini to generate the `gemini_insight` field
- The `confidence` field should reflect model uncertainty (0-1)
