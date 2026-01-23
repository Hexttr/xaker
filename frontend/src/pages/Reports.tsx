import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { serviceApi, Service } from '../services/api';
import { pentestApi, Pentest } from '../services/api';
import {
  FiServer,
  FiFileText,
  FiDownload,
  FiCalendar,
  FiLoader,
  FiRefreshCw,
  FiCheckCircle,
  FiSearch,
  FiGlobe,
} from 'react-icons/fi';

export default function Reports() {
  const [selectedServiceId, setSelectedServiceId] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [generatingReportId, setGeneratingReportId] = useState<string | null>(null);

  const { data: services = [] } = useQuery({
    queryKey: ['services'],
    queryFn: () => serviceApi.getAll().then(res => res.data),
  });

  const { data: pentests = [] } = useQuery({
    queryKey: ['pentests'],
    queryFn: () => pentestApi.getAll().then(res => res.data),
  });

  // Фильтруем завершенные пентесты
  const completedPentests = useMemo(() => {
    return pentests.filter(p => p.status === 'completed');
  }, [pentests]);

  // Фильтруем по выбранному сервису для метрик
  const filteredPentestsForMetrics = useMemo(() => {
    if (!selectedServiceId) return completedPentests;
    const selectedService = services.find(s => s.id === selectedServiceId);
    if (!selectedService) return completedPentests;
    return completedPentests.filter(p => p.targetUrl === selectedService.url);
  }, [completedPentests, services, selectedServiceId]);

  // Проверяем наличие отчетов для каждого пентеста
  const reportChecks = useQuery({
    queryKey: ['report-exists', completedPentests.map(p => p.id)],
    queryFn: async () => {
      const checks = await Promise.all(
        completedPentests.map(async (pentest) => {
          try {
            const response = await pentestApi.checkReportExists(pentest.id);
            return { pentestId: pentest.id, exists: response.data.exists };
          } catch {
            return { pentestId: pentest.id, exists: false };
          }
        })
      );
      return checks.reduce((acc, check) => {
        acc[check.pentestId] = check.exists;
        return acc;
      }, {} as Record<string, boolean>);
    },
    enabled: completedPentests.length > 0,
    staleTime: 30 * 1000,
    refetchInterval: 30000, // Обновляем каждые 30 секунд
  });

  // Вычисляем метрики
  const metrics = useMemo(() => {
    const total = filteredPentestsForMetrics.length;
    const withReports = filteredPentestsForMetrics.filter(
      p => reportChecks.data?.[p.id] === true
    ).length;
    const withoutReports = total - withReports;

    return {
      total,
      withReports,
      withoutReports,
    };
  }, [filteredPentestsForMetrics, reportChecks.data]);

  // Фильтруем и группируем пентесты
  const { filteredAndGroupedPentests, groupedByService } = useMemo(() => {
    let filtered = completedPentests;

    // Фильтр по сервису
    if (selectedServiceId) {
      const selectedService = services.find(s => s.id === selectedServiceId);
      if (selectedService) {
        filtered = filtered.filter(p => p.targetUrl === selectedService.url);
      }
    }

    // Поиск
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        p =>
          p.name.toLowerCase().includes(query) ||
          p.targetUrl.toLowerCase().includes(query) ||
          p.id.toLowerCase().includes(query)
      );
    }

    // Группировка по сервисам
    const grouped: Record<string, { service: Service; pentests: Pentest[] }> = {};
    filtered.forEach(pentest => {
      const service = services.find(s => s.url === pentest.targetUrl);
      if (service) {
        if (!grouped[service.id]) {
          grouped[service.id] = { service, pentests: [] };
        }
        grouped[service.id].pentests.push(pentest);
      } else {
        if (!grouped['unknown']) {
          grouped['unknown'] = {
            service: { id: 'unknown', name: 'Неизвестный сервис', url: pentest.targetUrl, createdAt: '', updatedAt: '' },
            pentests: [],
          };
        }
        grouped['unknown'].pentests.push(pentest);
      }
    });

    return {
      filteredAndGroupedPentests: grouped,
      groupedByService: Object.keys(grouped).length > 1,
    };
  }, [completedPentests, services, selectedServiceId, searchQuery]);

  const handleDownloadReport = async (pentestId: string, _forceGenerate: boolean = false) => {
    setGeneratingReportId(pentestId);
    try {
      // Всегда вызываем generatePdfReport - он вернет существующий или сгенерирует новый
      // forceGenerate можно использовать для принудительной перегенерации
      const blob = await pentestApi.generatePdfReport(pentestId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `pentest-report-${pentestId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      // Обновляем кэш проверки отчетов
      reportChecks.refetch();
    } catch (error) {
      console.error('Ошибка при загрузке/генерации отчета:', error);
      alert('Ошибка при загрузке/генерации отчета');
    } finally {
      setGeneratingReportId(null);
    }
  };

  // Извлекаем название сервиса из имени пентеста
  const getPentestServiceName = (pentestName: string): string => {
    const match = pentestName.match(/Пентест\s+(.+?)\s*-/);
    return match ? match[1] : pentestName;
  };

  return (
    <div className="min-h-screen bg-black">
      <div className="p-4 md:p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white mb-1">Отчеты</h1>
              <p className="text-sm text-gray-400">Просмотр и загрузка отчетов по пентестам</p>
            </div>
            <div className="flex gap-2">
              <select
                value={selectedServiceId}
                onChange={(e) => setSelectedServiceId(e.target.value)}
                className="px-4 py-2 bg-gray-900 border border-gray-700 text-white rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
              >
                <option value="">Все сервисы</option>
                {services.map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-500/10 rounded-lg">
                  <FiFileText className="w-6 h-6 text-blue-400" />
                </div>
                <span className="text-3xl font-bold text-white">{metrics.total}</span>
              </div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Всего отчетов</h3>
              <p className="text-xs text-gray-500">Завершенные пентесты</p>
            </div>

            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-500/10 rounded-lg">
                  <FiCheckCircle className="w-6 h-6 text-green-400" />
                </div>
                <span className="text-3xl font-bold text-white">{metrics.withReports}</span>
              </div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Сгенерировано</h3>
              <p className="text-xs text-gray-500">Отчеты готовы к скачиванию</p>
            </div>

            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-yellow-500/10 rounded-lg">
                  <FiRefreshCw className="w-6 h-6 text-yellow-400" />
                </div>
                <span className="text-3xl font-bold text-white">{metrics.withoutReports}</span>
              </div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Требуют генерации</h3>
              <p className="text-xs text-gray-500">Отчеты не созданы</p>
            </div>
          </div>

          {/* Filters and Search */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <FiSearch className="inline w-4 h-4 mr-2" />
                  Поиск
                </label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Поиск по названию, URL или ID..."
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 text-white rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
                />
              </div>

              {/* Service Selection */}
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <FiServer className="inline w-4 h-4 mr-2" />
                  Сервис
                </label>
                <select
                  value={selectedServiceId}
                  onChange={(e) => setSelectedServiceId(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 text-white rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
                >
                  <option value="">Все сервисы</option>
                  {services.map((service) => (
                    <option key={service.id} value={service.id}>
                      {service.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Reports Grid */}
          {Object.keys(filteredAndGroupedPentests).length === 0 ? (
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-8 border border-gray-700 shadow-lg text-center">
              <FiFileText className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400 mb-2">Отчеты не найдены</p>
              <p className="text-sm text-gray-500">
                {selectedServiceId || searchQuery.trim()
                  ? 'Измените фильтры для поиска отчетов'
                  : 'Завершенные пентесты не найдены. Отчеты появятся после завершения пентестов.'}
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(filteredAndGroupedPentests).map(([serviceId, { service, pentests: servicePentests }]) => (
                <div key={serviceId}>
                  {groupedByService && (
                    <div className="mb-4">
                      <h2 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                        <FiServer className="w-5 h-5 text-blue-400" />
                        {service.name}
                        <span className="text-sm text-gray-400 font-normal">
                          ({servicePentests.length} {servicePentests.length === 1 ? 'отчет' : 'отчетов'})
                        </span>
                      </h2>
                      <p className="text-sm text-gray-500 font-mono mb-4">{service.url}</p>
                    </div>
                  )}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {servicePentests.map((pentest) => {
                      const reportExists = reportChecks.data?.[pentest.id] ?? false;
                      const isGenerating = generatingReportId === pentest.id;

                      return (
                        <div
                          key={pentest.id}
                          className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-4 sm:p-6 border border-gray-700 shadow-lg hover:shadow-xl transition-all duration-200 hover:border-gray-600"
                        >
                          {/* Header */}
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-2">
                                <div className="p-2 bg-blue-500/10 rounded-lg flex-shrink-0">
                                  <FiFileText className="w-5 h-5 text-blue-400" />
                                </div>
                                <div className="flex-1 min-w-0">
                                  <h3 className="text-base sm:text-lg font-semibold text-white mb-1 truncate">
                                    {getPentestServiceName(pentest.name)}
                                  </h3>
                                  <div className="flex items-center gap-1.5 text-gray-400 mb-2 text-sm">
                                    <FiGlobe className="w-4 h-4 flex-shrink-0" />
                                    <span className="font-mono text-xs break-all">{pentest.targetUrl}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Status Badge */}
                          <div className="mb-4">
                            <div className="flex items-center gap-2">
                              {reportExists ? (
                                <span className="px-2 py-1 rounded text-xs font-medium text-white bg-green-500 flex items-center gap-1">
                                  <FiCheckCircle className="w-3 h-3" />
                                  Отчет готов
                                </span>
                              ) : (
                                <span className="px-2 py-1 rounded text-xs font-medium text-white bg-yellow-500 flex items-center gap-1">
                                  <FiRefreshCw className="w-3 h-3" />
                                  Требует генерации
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Date */}
                          <div className="mb-4">
                            <div className="flex items-center gap-1 text-xs text-gray-500">
                              <FiCalendar className="w-3 h-3" />
                              <span>
                                {pentest.completedAt
                                  ? `Завершен: ${new Date(pentest.completedAt).toLocaleString('ru-RU', {
                                      dateStyle: 'short',
                                      timeStyle: 'short',
                                    })}`
                                  : `Создан: ${new Date(pentest.createdAt).toLocaleString('ru-RU', {
                                      dateStyle: 'short',
                                      timeStyle: 'short',
                                    })}`}
                              </span>
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="pt-4 border-t border-gray-700">
                            <div className="flex flex-col gap-2">
                              <button
                                onClick={() => handleDownloadReport(pentest.id, false)}
                                disabled={isGenerating}
                                className={`w-full px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                                  reportExists
                                    ? 'bg-gradient-to-r from-green-600 to-green-800 hover:from-green-700 hover:to-green-900 text-white'
                                    : 'bg-gradient-to-r from-blue-600 to-blue-800 hover:from-blue-700 hover:to-blue-900 text-white'
                                }`}
                              >
                                {isGenerating ? (
                                  <>
                                    <FiLoader className="w-4 h-4 animate-spin" />
                                    {reportExists ? 'Обновляю...' : 'Генерирую...'}
                                  </>
                                ) : reportExists ? (
                                  <>
                                    <FiDownload className="w-4 h-4" />
                                    Скачать отчет
                                  </>
                                ) : (
                                  <>
                                    <FiFileText className="w-4 h-4" />
                                    Сгенерировать отчет
                                  </>
                                )}
                              </button>
                              {reportExists && (
                                <button
                                  onClick={() => handleDownloadReport(pentest.id, true)}
                                  disabled={isGenerating}
                                  className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-xs font-medium transition-colors duration-200 flex items-center justify-center gap-2 disabled:opacity-50"
                                  title="Перегенерировать отчет"
                                >
                                  <FiRefreshCw className="w-3 h-3" />
                                  Перегенерировать
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
