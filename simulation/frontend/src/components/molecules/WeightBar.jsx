export default function WeightBar({ label, weight }) {
  const pct = Math.round(weight * 100);
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-500 w-16 shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className="h-full bg-brand-mid rounded-full" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-700 w-8 text-right">{pct}%</span>
    </div>
  );
}
