export default function PriceTag({ price }) {
  return (
    <span className="text-sm font-medium text-gray-700">
      ${price.toFixed(3)}<span className="text-xs text-gray-400">/kWh</span>
    </span>
  );
}
