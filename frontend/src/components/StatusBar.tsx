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
    <div className="mt-1.5 mb-2 px-2.5 py-1.5 bg-gray-800/50 border-l-2 border-green-500 rounded-r">
      <div className="flex items-center gap-1.5">
        <div className="flex-shrink-0">
          <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse shadow shadow-green-500/50"></div>
        </div>
        <span className="text-xs text-gray-400 font-normal">
          {status}
        </span>
      </div>
    </div>
  );
}


