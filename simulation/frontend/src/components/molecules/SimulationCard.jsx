export default function SimulationCard({ baselineKwh, projectedKwh, reductionPct, priceApplied }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 flex flex-col gap-4">
      <span className="text-xs text-gray-400 uppercase tracking-wide">Energy Simulation</span>
      <div className="flex gap-3">
        <div className="flex-1 bg-gray-50 rounded-lg p-3 flex flex-col gap-1">
          <span className="text-xs text-gray-400">Baseline</span>
          <span className="text-xl font-medium text-gray-700">{baselineKwh.toLocaleString()}</span>
          <span className="text-xs text-gray-400">kWh/mo</span>
        </div>
        <div className="flex-1 bg-esi-green-light rounded-lg p-3 flex flex-col gap-1">
          <span className="text-xs text-esi-green-dark">Projected</span>
          <span className="text-xl font-medium text-esi-green-dark">{projectedKwh.toLocaleString()}</span>
          <span className="text-xs text-esi-green-dark">kWh/mo</span>
        </div>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">Reduction</span>
        <span className="text-sm font-medium text-esi-green-dark">↓ {reductionPct}%</span>
      </div>
      <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-esi-green-mid rounded-full"
          style={{ width: `${reductionPct}%` }}
        />
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">Price applied</span>
        <span className="text-xs font-medium text-gray-700">${priceApplied.toFixed(3)}/kWh</span>
      </div>
    </div>
  );
}
