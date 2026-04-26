export default function MapLegend() {
  return (
    <div className="bg-white rounded-lg shadow px-3 py-2 flex flex-col gap-1">
      <span className="text-xs text-gray-400 uppercase tracking-wide">ESI Score</span>
      <div className="w-40 h-2 rounded-full" style={{
        background: 'linear-gradient(to right, #3b6d11, #ef9f27, #e24b4a)'
      }} />
      <div className="flex justify-between">
        <span className="text-xs text-gray-500">0.0</span>
        <span className="text-xs text-gray-500">1.0</span>
      </div>
    </div>
  );
}
