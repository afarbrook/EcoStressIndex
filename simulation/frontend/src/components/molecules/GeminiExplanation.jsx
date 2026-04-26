export default function GeminiExplanation({ text, isLoading }) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-2 animate-pulse">
        <div className="h-3 bg-gray-100 rounded w-full" />
        <div className="h-3 bg-gray-100 rounded w-5/6" />
        <div className="h-3 bg-gray-100 rounded w-4/6" />
      </div>
    );
  }

  return (
    <p className="text-xs text-gray-600 leading-relaxed">{text}</p>
  );
}
