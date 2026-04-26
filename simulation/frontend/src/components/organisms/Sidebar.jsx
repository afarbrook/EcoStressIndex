import SearchInput from '../atoms/SearchInput';
import WeightBar from '../molecules/WeightBar';

const WEIGHT_LABELS = {
  heat_island: 'Heat',
  air_quality: 'Air',
  energy_use: 'Energy',
  light_pollution: 'Light',
};

export default function Sidebar({ weights, onSearch, isLoading, user, onLogout }) {
  return (
    <div className="h-full flex flex-col p-4 gap-6">
      <div>
        <span className="text-xs font-medium text-brand-dark uppercase tracking-wide">EcoStress</span>
      </div>

      <SearchInput onSearch={onSearch} isLoading={isLoading} />

      {weights && (
        <div className="flex flex-col gap-3">
          <span className="text-xs text-gray-400 uppercase tracking-wide">Gemini Weights</span>
          {Object.entries(WEIGHT_LABELS).map(([key, label]) => (
            <WeightBar key={key} label={label} weight={weights[key] ?? 0} />
          ))}
        </div>
      )}

      <div className="mt-auto">
        <button onClick={onLogout} className="text-xs text-gray-400 hover:text-brand-mid">
          Logout
        </button>
      </div>
    </div>
  );
}
