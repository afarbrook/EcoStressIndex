import GaugeBar from '../atoms/GaugeBar';
import EsiBadge from '../atoms/EsiBadge';

export default function EsiScoreCard({ score }) {
  return (
    <div className="flex flex-col items-center gap-3 p-4 bg-white rounded-xl border border-gray-100">
      <span className="text-xs text-gray-400 uppercase tracking-wide">ESI Score</span>
      <span className="text-5xl font-medium text-gray-800">{score.toFixed(2)}</span>
      <EsiBadge score={score} />
      <div className="w-full mt-1">
        <GaugeBar value={score} />
      </div>
    </div>
  );
}
