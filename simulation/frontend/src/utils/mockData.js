export const mockNeighborhood = {
  id: 'tract-001',
  name: 'Barrio Hollywood',
  esi_score: 0.74,
  dynamic_price_per_kwh: 0.1644,
  components: {
    air_quality: 0.68,
    light_pollution: 0.45,
    heat_island: 0.80,
    energy_use: 0.72,
  },
  gemini_explanation:
    "This area's elevated ESI score is driven primarily by its proximity to industrial activity along the I-10 corridor, raising both air quality stress and heat island intensity.",
  geojson: null,
};

export const mockWeights = {
  air_quality: 0.28,
  light_pollution: 0.12,
  heat_island: 0.35,
  energy_use: 0.25,
};

export const mockSimulation = {
  baseline_kwh: 1150,
  projected_kwh: 920,
  reduction_pct: 20.0,
  price_applied: 0.164,
};
