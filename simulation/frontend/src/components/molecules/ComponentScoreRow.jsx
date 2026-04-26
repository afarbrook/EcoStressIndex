import GaugeBar from '../atoms/GaugeBar';

export default function ComponentScoreRow({ label, value }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-500 w-24 shrink-0">{label}</span>
      <div className="flex-1">
        <GaugeBar value={value} />
      </div>
      <span className="text-xs text-gray-700 w-8 text-right">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}
