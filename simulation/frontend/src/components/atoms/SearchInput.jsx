export default function SearchInput({ onSearch, isLoading }) {
  function handleKeyDown(e) {
    if (e.key === 'Enter') onSearch(e.target.value);
  }

  return (
    <div className="relative w-full">
      <input
        type="text"
        placeholder="Search a city..."
        disabled={isLoading}
        onKeyDown={handleKeyDown}
        className="w-full px-3 py-2 text-sm border border-gray-200 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-brand-mid disabled:opacity-50"
      />
      {isLoading && (
        <span className="absolute right-3 top-2.5 text-xs text-gray-400">...</span>
      )}
    </div>
  );
}
