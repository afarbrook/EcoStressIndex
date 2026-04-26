ELASTICITY = 0.30  # absolute value; standard short-run US residential price elasticity
CO2_LBS_PER_KWH = 0.93  # US average grid emission factor


def run_simulation(neighborhood: str, esi_score: float, dynamic_price: float, base_rate: float = 0.12) -> dict:
    """
    Deterministic price-elasticity simulation.
    Higher ESI neighborhoods have higher baseline use.
    Reduction is proportional to price premium via standard elasticity.
    """
    baseline_kwh = round(750 + esi_score * 700, 1)

    price_increase_pct = ((dynamic_price - base_rate) / base_rate * 100) if base_rate > 0 else 0
    reduction_pct = round(min(40.0, max(0.0, ELASTICITY * price_increase_pct)), 1)
    projected_kwh = round(baseline_kwh * (1 - reduction_pct / 100), 1)
    co2_saved_lbs = round((baseline_kwh - projected_kwh) * CO2_LBS_PER_KWH, 1)

    # Confidence scales with how large the price signal is
    confidence = round(min(0.95, 0.65 + abs(price_increase_pct) * 0.008), 2)

    insight = (
        f"A {price_increase_pct:.0f}% price premium (${dynamic_price}/kWh) is projected to reduce "
        f"{neighborhood}'s average monthly consumption by {reduction_pct}%, "
        f"from {baseline_kwh:.0f} to {projected_kwh:.0f} kWh — "
        f"saving roughly {int(co2_saved_lbs)} lbs of CO₂ per household per month."
    )

    return {
        "neighborhood": neighborhood,
        "baseline_kwh": baseline_kwh,
        "projected_kwh": projected_kwh,
        "reduction_pct": reduction_pct,
        "price_applied": dynamic_price,
        "co2_saved_lbs": co2_saved_lbs,
        "confidence": confidence,
        "gemini_insight": insight,
    }
