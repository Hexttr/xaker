import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { pentestApi, PentestComparison } from '../services/api';
import { serviceApi } from '../services/api';
import { FiBarChart2, FiServer, FiLoader, FiTrendingUp, FiCheckCircle, FiAlertTriangle, FiTrendingDown } from 'react-icons/fi';

export default function Analytics() {
  const [selectedServiceId, setSelectedServiceId] = useState<string>('');
  const [expandedFixed, setExpandedFixed] = useState<boolean>(false);
  const [expandedNew, setExpandedNew] = useState<boolean>(false);

  // Загружаем список сервисов
  const { data: services = [], isLoading: servicesLoading } = useQuery({
    queryKey: ['services'],
    queryFn: () => serviceApi.getAll().then(res => res.data),
    staleTime: 5 * 60 * 1000, // Кэш 5 минут
  });

  // Загружаем все пентесты (только при выборе сервиса)
  const { data: allPentests = [], isLoading: pentestsLoading } = useQuery({
    queryKey: ['pentests'],
    queryFn: () => pentestApi.getAll().then(res => res.data),
    enabled: !!selectedServiceId, // Загружаем только при выборе сервиса
    staleTime: 2 * 60 * 1000, // Кэш 2 минуты
  });

  // Фильтруем пентесты по выбранному сервису
  const selectedService = services.find(s => s.id === selectedServiceId);
  const servicePentests = useMemo(() => {
    if (!selectedService || !allPentests.length) return [];
    return allPentests
      .filter(p => p.targetUrl === selectedService.url)
      .filter(p => p.status === 'completed') // Только завершенные
      .sort((a, b) => {
        const dateA = a.completedAt ? new Date(a.completedAt).getTime() : 0;
        const dateB = b.completedAt ? new Date(b.completedAt).getTime() : 0;
        return dateB - dateA; // Сначала новые
      });
  }, [selectedService, allPentests]);

  // Загружаем сравнение для последнего пентеста
  const latestPentest = servicePentests[0];
  const { data: comparison, isLoading: comparisonLoading } = useQuery({
    queryKey: ['pentest-comparison', latestPentest?.id],
    queryFn: () => pentestApi.compareWithPrevious(latestPentest!.id).then(res => res.data),
    enabled: !!latestPentest && latestPentest.status === 'completed',
    staleTime: 5 * 60 * 1000, // Кэш 5 минут
    placeholderData: (previousData) => previousData ?? undefined,
  });

  // Подготовка данных для графика
  const chartData = useMemo(() => {
    if (!servicePentests.length) return [];
    
    // Группируем по датам
    const groupedByDate: { [key: string]: number } = {};
    servicePentests.forEach(pentest => {
      if (pentest.completedAt) {
        const date = new Date(pentest.completedAt).toLocaleDateString('ru-RU', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
        groupedByDate[date] = (groupedByDate[date] || 0) + 1;
      }
    });

    return Object.entries(groupedByDate)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [servicePentests]);

  // Максимальное значение для масштабирования графика
  const maxCount = useMemo(() => {
    return Math.max(...chartData.map(d => d.count), 1);
  }, [chartData]);

  return (
    <div className="min-h-screen bg-black">
      <div className="p-4 md:p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white mb-1">Аналитика</h1>
              <p className="text-sm text-gray-400">Анализ пентестов по сервисам</p>
            </div>
            <div className="flex gap-2">
              <select
                value={selectedServiceId}
                onChange={(e) => setSelectedServiceId(e.target.value)}
                className="px-4 py-2 bg-gray-900 border border-gray-700 text-white rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
                disabled={servicesLoading}
              >
                <option value="">Выберите сервис</option>
                {services.map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {selectedServiceId && (
            <>
              {/* График по датам */}
              {pentestsLoading ? (
                <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-8 border border-gray-700 shadow-lg text-center">
                  <FiLoader className="w-8 h-8 text-gray-600 mx-auto mb-3 animate-spin" />
                  <p className="text-sm text-gray-500">Загрузка данных...</p>
                </div>
              ) : chartData.length > 0 ? (
                <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                  <h2 className="text-lg font-semibold text-white mb-4">График проведения пентестов</h2>
                  <div className="space-y-3">
                    {chartData.map((item, index) => (
                      <div key={index} className="flex items-center gap-3">
                        <div className="text-xs text-gray-400 w-32 flex-shrink-0">
                          {item.date}
                        </div>
                        <div className="flex-1 bg-gray-800 rounded-full h-6 relative overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-red-600 to-red-800 h-full rounded-full flex items-center justify-end pr-2 transition-all duration-500"
                            style={{ width: `${(item.count / maxCount) * 100}%` }}
                          >
                            <span className="text-xs text-white font-medium">{item.count}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 text-xs text-gray-500">
                    Всего завершенных пентестов: <span className="text-white font-medium">{servicePentests.length}</span>
                  </div>
                </div>
              ) : (
                <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-8 border border-gray-700 shadow-lg text-center">
                  <p className="text-sm text-gray-500">Нет завершенных пентестов для выбранного сервиса</p>
                </div>
              )}

              {/* Сравнение с предыдущим пентестом */}
              {comparisonLoading ? (
                <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-4 border border-gray-700 shadow-lg">
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <FiLoader className="w-4 h-4 animate-spin" />
                    Загрузка сравнения с предыдущим пентестом...
                  </div>
                </div>
              ) : comparison && comparison.comparison ? (
                <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <FiTrendingUp className="w-5 h-5 text-green-400" />
                    Сравнение с предыдущим пентестом
                  </h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                      <div className="text-xs text-gray-400 mb-1">Исправлено</div>
                      <div className="text-2xl font-bold text-green-400">{comparison.comparison.metrics.totalFixed}</div>
                    </div>
                    <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4">
                      <div className="text-xs text-gray-400 mb-1">Осталось</div>
                      <div className="text-2xl font-bold text-yellow-400">{comparison.comparison.metrics.totalRemaining}</div>
                    </div>
                    <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
                      <div className="text-xs text-gray-400 mb-1">Новых</div>
                      <div className="text-2xl font-bold text-red-400">{comparison.comparison.metrics.totalNew}</div>
                    </div>
                    <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
                      <div className="text-xs text-gray-400 mb-1">Улучшение</div>
                      <div className="text-2xl font-bold text-blue-400">
                        {comparison.comparison.metrics.improvementRate.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  
                  {comparison.comparison.fixed.length > 0 && (
                    <div className="mb-4">
                      <div className="text-sm text-green-400 font-semibold mb-2 flex items-center gap-2">
                        <FiCheckCircle className="w-4 h-4" />
                        Исправленные уязвимости ({comparison.comparison.fixed.length})
                      </div>
                      <div className="text-sm text-gray-400 space-y-1 bg-gray-800/50 rounded p-2 overflow-visible">
                        <div className={`space-y-1 transition-all duration-300 ease-in-out ${expandedFixed ? 'max-h-none' : 'max-h-32 overflow-hidden'}`}>
                          {(expandedFixed ? comparison.comparison.fixed : comparison.comparison.fixed.slice(0, 5)).map((v: any, idx: number) => (
                            <div key={idx} className="flex items-start gap-2 break-words">
                              <span className="text-green-400 flex-shrink-0">✓</span>
                              <span className="break-words whitespace-normal">{v.fingerprint?.id || v.id}: {v.fingerprint?.title || v.title}</span>
                            </div>
                          ))}
                        </div>
                        {comparison.comparison.fixed.length > 5 && (
                          <button
                            onClick={() => setExpandedFixed(!expandedFixed)}
                            className="text-blue-400 hover:text-blue-300 text-xs mt-2 cursor-pointer transition-colors duration-200"
                          >
                            {expandedFixed ? 'Скрыть' : `... и еще ${comparison.comparison.fixed.length - 5}`}
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {comparison.comparison.new.length > 0 && (
                    <div>
                      <div className="text-sm text-red-400 font-semibold mb-2 flex items-center gap-2">
                        <FiAlertTriangle className="w-4 h-4" />
                        Новые уязвимости ({comparison.comparison.new.length})
                      </div>
                      <div className="text-sm text-gray-400 space-y-1 bg-gray-800/50 rounded p-2 overflow-visible">
                        <div className={`space-y-1 transition-all duration-300 ease-in-out ${expandedNew ? 'max-h-none' : 'max-h-32 overflow-hidden'}`}>
                          {(expandedNew ? comparison.comparison.new : comparison.comparison.new.slice(0, 5)).map((v: any, idx: number) => (
                            <div key={idx} className="flex items-start gap-2 break-words">
                              <span className="text-red-400 flex-shrink-0">+</span>
                              <span className="break-words whitespace-normal">{v.fingerprint?.id || v.id}: {v.fingerprint?.title || v.title}</span>
                            </div>
                          ))}
                        </div>
                        {comparison.comparison.new.length > 5 && (
                          <button
                            onClick={() => setExpandedNew(!expandedNew)}
                            className="text-blue-400 hover:text-blue-300 text-xs mt-2 cursor-pointer transition-colors duration-200"
                          >
                            {expandedNew ? 'Скрыть' : `... и еще ${comparison.comparison.new.length - 5}`}
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : comparison && comparison.message ? (
                <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-4 border border-gray-700 shadow-lg">
                  <p className="text-sm text-gray-400">{comparison.message}</p>
                </div>
              ) : null}
            </>
          )}

          {!selectedServiceId && (
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-8 border border-gray-700 shadow-lg text-center">
              <FiBarChart2 className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-sm text-gray-500">
                Выберите сервис для просмотра аналитики
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
