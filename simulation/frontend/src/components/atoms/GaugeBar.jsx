import { esiToColor } from '../../utils/esiColor';

export default function GaugeBar({ value, color }) {
  const fillColor = color ?? esiToColor(value);
  const pct = Math.round(value * 100);

  return (
    <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{ width: `${pct}%`, backgroundColor: fillColor }}
      />
    </div>
  );
}
