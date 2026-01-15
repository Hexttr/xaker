// Компонент для отображения текущего статуса пентеста
interface StatusBarProps {
  status: string;
  isRunning?: boolean;
}

export default function StatusBar({ status, isRunning = false }: StatusBarProps) {
  if (!isRunning) {
    return null;
  }

  return (
    <div className="mt-2 mb-3 px-3 py-2 bg-gray-800/50 border-l-4 border-green-500 rounded-r-lg">
      <div className="flex items-center gap-2">
        <div className="flex-shrink-0">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
        </div>
        <span className="text-sm md:text-base text-gray-300 font-medium">
          {status}
        </span>
      </div>
    </div>
  );
}


