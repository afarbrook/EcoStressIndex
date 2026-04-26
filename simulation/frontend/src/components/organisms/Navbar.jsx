export default function Navbar({ city, user, onLogout }) {
  return (
    <div className="h-12 px-4 bg-white border-b border-gray-200 flex items-center justify-between shrink-0">
      <span className="text-base font-medium text-brand-dark">EcoStress Index</span>
      <span className="text-sm text-gray-500">{city || '—'}</span>
      <div className="flex items-center gap-3">
        <span className="text-xs text-gray-400">{user?.email}</span>
        <button onClick={onLogout} className="text-xs text-brand-mid hover:text-brand-dark">
          Logout
        </button>
      </div>
    </div>
  );
}
