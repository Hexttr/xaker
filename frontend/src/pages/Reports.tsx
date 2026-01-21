import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { serviceApi, Service } from '../services/api';
import { pentestApi, Pentest } from '../services/api';
import { FiServer, FiFileText, FiDownload, FiCalendar, FiLoader, FiRefreshCw } from 'react-icons/fi';

export default function Reports() {
  const [selectedServiceId, setSelectedServiceId] = useState<string>('');
  const [generatingReportId, setGeneratingReportId] = useState<string | null>(null);

  const { data: services = [] } = useQuery({
    queryKey: ['services'],
    queryFn: () => serviceApi.getAll().then(res => res.data),
  });

  const { data: pentests = [] } = useQuery({
    queryKey: ['pentests'],
    queryFn: () => pentestApi.getAll().then(res => res.data),
  });

  // Фильтруем завершенные пентесты по выбранному сервису
  const selectedService = services.find(s => s.id === selectedServiceId);
  const completedPentests = useMemo(() => {
    return selectedServiceId
      ? pentests.filter(
          p => p.status === 'completed' && p.targetUrl === selectedService?.url
        )
      : pentests.filter(p => p.status === 'completed');
  }, [pentests, selectedServiceId, selectedService]);

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
    staleTime: 30 * 1000, // Кэш 30 секунд
  });

  const handleDownloadReport = async (pentestId: string) => {
    setGeneratingReportId(pentestId);
    try {
      // Всегда вызываем generatePdfReport - он вернет существующий или сгенерирует новый
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
      console.error('Ошибка при загрузке отчета:', error);
      alert('Ошибка при загрузке отчета');
    } finally {
      setGeneratingReportId(null);
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <div className="p-4 md:p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-4">
            <h1 className="text-xl font-semibold text-white mb-1">Отчеты</h1>
            <p className="text-sm text-gray-500">Просмотр и загрузка отчетов по пентестам</p>
          </div>

          {/* Service Selection */}
          <div className="bg-gray-900 rounded p-4 mb-4 border border-gray-700">
            <label className="block text-xs font-normal text-gray-400 mb-1.5">
              <FiServer className="inline w-3 h-3 mr-1.5" />
              Выберите сервис
            </label>
            <select
              value={selectedServiceId}
              onChange={(e) => setSelectedServiceId(e.target.value)}
              className="w-full md:w-auto px-3 py-1.5 text-sm bg-gray-800 border border-gray-700 text-white rounded focus:ring-1 focus:ring-red-500 focus:border-red-500"
            >
              <option value="">Все сервисы</option>
              {services.map((service) => (
                <option key={service.id} value={service.id}>
                  {service.name} ({service.url})
                </option>
              ))}
            </select>
          </div>

          {/* Reports List */}
          <div className="bg-gray-900 rounded border border-gray-700">
            <div className="p-4 border-b border-gray-700">
              <h2 className="text-base font-medium text-white">
                Отчеты {selectedService && `- ${selectedService.name}`}
              </h2>
            </div>

            {completedPentests.length === 0 ? (
              <div className="p-4 text-center text-sm text-gray-500">
                {selectedServiceId
                  ? 'Отчеты для выбранного сервиса не найдены.'
                  : 'Завершенные пентесты не найдены. Отчеты появятся после завершения пентестов.'}
              </div>
            ) : (
              <div className="divide-y divide-gray-700">
                {completedPentests.map((pentest) => (
                  <div
                    key={pentest.id}
                    className="p-4 hover:bg-gray-800 transition-colors duration-200"
                  >
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1.5">
                          <FiFileText className="w-4 h-4 text-blue-600" />
                          <h3 className="text-sm font-medium text-white">{pentest.name}</h3>
                        </div>
                        <p className="text-gray-500 mb-2 font-mono text-xs">{pentest.targetUrl}</p>
                        <div className="flex items-center gap-3 text-xs text-gray-600">
                          <span className="flex items-center gap-1">
                            <FiCalendar className="w-3 h-3" />
                            {pentest.completedAt
                              ? new Date(pentest.completedAt).toLocaleString('ru-RU', {
                                  dateStyle: 'short',
                                  timeStyle: 'short',
                                })
                              : new Date(pentest.createdAt).toLocaleString('ru-RU', {
                                  dateStyle: 'short',
                                  timeStyle: 'short',
                                })}
                          </span>
                        </div>
                      </div>
                      {(() => {
                        const reportExists = reportChecks.data?.[pentest.id] ?? false;
                        const isGenerating = generatingReportId === pentest.id;
                        
                        return (
                          <button
                            onClick={() => handleDownloadReport(pentest.id)}
                            disabled={isGenerating}
                            className={`bg-gradient-to-r ${
                              reportExists 
                                ? 'from-green-600 to-green-800 hover:from-green-700 hover:to-green-900' 
                                : 'from-blue-600 to-blue-800 hover:from-blue-700 hover:to-blue-900'
                            } disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-1.5 rounded text-sm font-medium transition-all duration-200 flex items-center gap-1.5`}
                          >
                            {isGenerating ? (
                              <>
                                <FiLoader className="w-4 h-4 animate-spin" />
                                {reportExists ? 'Обновляю отчет...' : 'Генерирую отчет...'}
                              </>
                            ) : reportExists ? (
                              <>
                                <FiDownload className="w-4 h-4" />
                                Скачать отчет
                              </>
                            ) : (
                              <>
                                <FiRefreshCw className="w-4 h-4" />
                                Сгенерировать отчет
                              </>
                            )}
                          </button>
                        );
                      })()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

