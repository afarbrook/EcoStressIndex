import EsiScoreCard from '../molecules/EsiScoreCard';
import ComponentScoreRow from '../molecules/ComponentScoreRow';
import GeminiExplanation from '../molecules/GeminiExplanation';
import SimulationCard from '../molecules/SimulationCard';
import PriceTag from '../atoms/PriceTag';

const COMPONENT_LABELS = {
  heat_island: 'Heat island',
  air_quality: 'Air quality',
  energy_use: 'Energy use',
  light_pollution: 'Light pollution',
};

export default function NeighborhoodPanel({ neighborhood, simulation, isLoading }) {
  if (!neighborhood) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <p className="text-xs text-gray-400 text-center">Click a neighborhood to explore</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto flex flex-col gap-4 p-4">
      <h2 className="text-base font-medium text-gray-800">{neighborhood.name}</h2>

      <EsiScoreCard score={neighborhood.esi_score} />

      <PriceTag price={neighborhood.dynamic_price_per_kwh} />

      <div className="flex flex-col gap-2">
        <span className="text-xs text-gray-400 uppercase tracking-wide">Components</span>
        {Object.entries(COMPONENT_LABELS).map(([key, label]) => (
          <ComponentScoreRow key={key} label={label} value={neighborhood.components[key] ?? 0} />
        ))}
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-xs text-gray-400 uppercase tracking-wide">AI Insight</span>
        <GeminiExplanation text={neighborhood.gemini_explanation} isLoading={isLoading} />
      </div>

      {simulation && (
        <SimulationCard
          baselineKwh={simulation.baseline_kwh}
          projectedKwh={simulation.projected_kwh}
          reductionPct={simulation.reduction_pct}
          priceApplied={simulation.price_applied}
        />
      )}
    </div>
  );
}
