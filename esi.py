def normalize(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to [0, 1]. Higher = worse."""
    if max_val == min_val:
        return 0
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def compute_esi(components: dict, weights: dict) -> float:
    """
    ESI = w1(AQ) + w2(LP) + w3(HI) + w4(EU)
    All components normalized to [0, 1] — higher = worse environmental stress.
    """
    return (
        weights["air_quality"]     * components["air_quality_normalized"] +
        weights["light_pollution"] * components["light_pollution_normalized"] +
        weights["heat_island"]     * components["heat_island_normalized"] +
        weights["energy_use"]      * components["energy_use_normalized"]
    )


def compute_price(esi_score: float, base_rate: float = 0.12, alpha: float = 0.5) -> float:
    """
    Price = BaseRate × (1 + alpha × ESI)
    ESI 0 → $0.12/kWh (base)
    ESI 1 → $0.18/kWh (+50% premium)
    alpha is tunable by the energy company.
    """
    return round(base_rate * (1 + alpha * esi_score), 4)
