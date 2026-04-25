# simulation/simulate.py
# Owned by Person B
# Stub implementation — Person B replaces this with the real model.

import random


def run_simulation(city: str, neighborhood: str) -> dict:
    """
    Given a city and neighborhood, return projected energy consumption change
    after dynamic pricing is applied.

    Person B: replace the stub logic below with your real elasticity model + Gemini insight.
    Write results to the `simulations` Supabase table.

    Returns the JSON shape that Alex's frontend expects:
    {
        "neighborhood": str,
        "baseline_kwh": float,
        "projected_kwh": float,
        "reduction_pct": float,
        "price_applied": float,
        "confidence": float,
        "gemini_insight": str,
    }
    """
    # --- STUB: replace with real model ---
    baseline = round(random.uniform(900, 1400), 1)
    reduction = round(random.uniform(10, 30), 1)
    projected = round(baseline * (1 - reduction / 100), 1)
    price = round(random.uniform(0.12, 0.18), 4)
    confidence = round(random.uniform(0.70, 0.92), 2)

    return {
        "neighborhood": neighborhood,
        "baseline_kwh": baseline,
        "projected_kwh": projected,
        "reduction_pct": reduction,
        "price_applied": price,
        "confidence": confidence,
        "gemini_insight": (
            f"A dynamic pricing premium of ${price}/kWh is projected to reduce "
            f"{neighborhood}'s average monthly consumption by {reduction}%, "
            f"from {baseline} kWh to {projected} kWh."
        ),
    }
