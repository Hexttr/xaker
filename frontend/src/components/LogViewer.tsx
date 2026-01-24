// Компонент для отображения логов с цветовым кодированием
import { useState, useEffect, useRef, useMemo, useCallback } from 'react';

interface Log {
  id: string;
  level: 'info' | 'warn' | 'error' | 'success';
  message: string;
  timestamp: string;
}

interface LogViewerProps {
  logs: Log[];
  autoScroll?: boolean;
  maxHeight?: string;
  isLoading?: boolean;
}

export default function LogViewer({ 
  logs, 
  autoScroll = true,
  maxHeight = '24rem',
  isLoading = false
}: LogViewerProps) {
  const [isPaused, setIsPaused] = useState(false);
  const [filter, setFilter] = useState<string>('');
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Оптимизация: используем requestAnimationFrame для плавного скролла
  useEffect(() => {
    if (autoScroll && !isPaused && logContainerRef.current) {
      // Используем requestAnimationFrame для неблокирующего скролла
      requestAnimationFrame(() => {
        if (logContainerRef.current) {
          logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
      });
    }
  }, [logs.length, autoScroll, isPaused]); // Зависим от длины, а не от всего массива

  const getLogColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-red-400';
      case 'warn':
        return 'text-yellow-400';
      case 'success':
        return 'text-green-400';
      default:
        return 'text-blue-400';
    }
  };

  const getLogBg = (level: string) => {
    switch (level) {
      case 'error':
        return 'bg-red-900/20';
      case 'warn':
        return 'bg-yellow-900/20';
      case 'success':
        return 'bg-green-900/20';
      default:
        return '';
    }
  };

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'error':
        return '🔴';
      case 'warn':
        return '🟡';
      case 'success':
        return '✅';
      default:
        return '🟢';
    }
  };

  // Мемоизируем highlightKeywords - не пересоздавать функцию при каждом рендере
  const highlightKeywords = useCallback((text: string) => {
    // Упрощаем - убираем подсветку для производительности, если текст слишком длинный
    if (text.length > 500) {
      return text; // Не подсвечиваем длинные сообщения
    }
    const keywords = ['vulnerability', 'critical', 'error', 'CVSS', 'exploited', 'уязвимость', 'критическая', 'ошибка', 'эксплуатирована'];
    let highlighted = text;
    keywords.forEach(keyword => {
      const regex = new RegExp(`(${keyword})`, 'gi');
      highlighted = highlighted.replace(regex, '<span class="font-bold text-white">$1</span>');
    });
    return highlighted;
  }, []);

  // Мемоизируем фильтрацию и ограничиваем количество логов для производительности
  const filteredLogs = useMemo(() => {
    let result = logs.filter(log => 
      filter === '' || 
      log.message.toLowerCase().includes(filter.toLowerCase()) ||
      log.level.toLowerCase().includes(filter.toLowerCase())
    );
    
    // Ограничиваем количество отображаемых логов (показываем только последние 500)
    // Это критично для производительности при большом количестве логов
    if (result.length > 500) {
      result = result.slice(-500);
    }
    
    return result;
  }, [logs, filter]);

  // Мемоизируем форматирование даты
  const formatTime = useCallback((timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  }, []);

  return (
    <div className="border border-gray-700 rounded overflow-hidden bg-gray-900">
      <div className="bg-gray-800 px-3 py-1.5 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-2 flex-1">
          <h4 className="text-white text-xs font-medium">Live Logs</h4>
          <span className="text-gray-500 text-xs">
            {filteredLogs.length} сообщений
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <input
            id="log-filter"
            name="log-filter"
            type="text"
            placeholder="Поиск в логах..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-gray-700 text-white px-2 py-0.5 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          {autoScroll && (
            <button
              onClick={() => setIsPaused(!isPaused)}
              className={`px-2 py-0.5 rounded text-xs font-normal ${
                isPaused 
                  ? 'bg-yellow-600 hover:bg-yellow-700 text-white' 
                  : 'bg-gray-700 hover:bg-gray-600 text-white'
              }`}
            >
              {isPaused ? '▶️' : '⏸️'}
            </button>
          )}
        </div>
      </div>
      <div
        ref={logContainerRef}
        className="p-3 font-mono text-xs overflow-y-auto"
        style={{ maxHeight, minHeight: '200px' }}
      >
        {isLoading && logs.length === 0 ? (
          <div className="text-gray-400 text-center py-8 flex flex-col items-center gap-2">
            <div className="w-6 h-6 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-xs">Загружаю логи...</span>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="text-gray-600 text-center py-6 text-xs">
            {filter ? 'Нет логов, соответствующих фильтру' : 'Логи отсутствуют'}
          </div>
        ) : (
          <>
            {isLoading && logs.length > 0 && (
              <div className="text-gray-500 text-center py-2 text-xs flex items-center justify-center gap-2 mb-2 border-b border-gray-700">
                <div className="w-3 h-3 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
                <span>Обновление логов...</span>
              </div>
            )}
            {filteredLogs.length >= 500 && logs.length > filteredLogs.length && (
              <div className="text-yellow-500 text-center py-2 text-xs mb-2 border-b border-gray-700">
                Показаны последние 500 из {logs.length} логов
              </div>
            )}
            {filteredLogs.map((log) => (
              <div
                key={log.id}
                className={`mb-0.5 px-1.5 py-0.5 rounded ${getLogBg(log.level)}`}
              >
                <span className="text-gray-600 text-xs mr-1.5">
                  {formatTime(log.timestamp)}
                </span>
                <span className="mr-1.5 text-xs">{getLogIcon(log.level)}</span>
                <span className={`font-normal text-xs ${getLogColor(log.level)}`}>
                  [{log.level.toUpperCase()}]
                </span>
                <span 
                  className="ml-1.5 text-gray-400 text-xs"
                  dangerouslySetInnerHTML={{ 
                    __html: highlightKeywords(log.message)
                  }}
                />
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}








