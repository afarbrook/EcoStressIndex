export function esiToColor(score) {
  if (score < 0.5) {
    const t = score / 0.5;
    const r = Math.round(59 + t * (239 - 59));
    const g = Math.round(109 + t * (159 - 109));
    const b = Math.round(17 + t * (39 - 17));
    return `rgb(${r},${g},${b})`;
  } else {
    const t = (score - 0.5) / 0.5;
    const r = Math.round(239 + t * (226 - 239));
    const g = Math.round(159 + t * (75 - 159));
    const b = Math.round(39 + t * (74 - 39));
    return `rgb(${r},${g},${b})`;
  }
}

export function esiBgClass(score) {
  if (score < 0.4) return 'bg-esi-green-light text-esi-green-dark';
  if (score < 0.7) return 'bg-esi-amber-light text-esi-amber-dark';
  return 'bg-esi-red-light text-esi-red-dark';
}
