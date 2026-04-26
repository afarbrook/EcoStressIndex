import { esiBgClass } from '../../utils/esiColor';

export default function EsiBadge({ score }) {
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${esiBgClass(score)}`}>
      {score.toFixed(2)}
    </span>
  );
}
