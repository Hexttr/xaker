import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { serviceApi, Service } from '../services/api';
import { pentestApi, Pentest } from '../services/api';
import { FiServer, FiFileText, FiDownload, FiCalendar } from 'react-icons/fi';

export default function Reports() {
  const [selectedServiceId, setSelectedServiceId] = useState<string>('');

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
  const completedPentests = selectedServiceId
    ? pentests.filter(
        p => p.status === 'completed' && p.targetUrl === selectedService?.url
      )
    : pentests.filter(p => p.status === 'completed');

  const handleDownloadReport = async (pentestId: string) => {
    try {
      const blob = await pentestApi.generatePdfReport(pentestId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `pentest-report-${pentestId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Ошибка при загрузке отчета:', error);
      alert('Ошибка при загрузке отчета');
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <div className="p-6 md:p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-white mb-2">Отчеты</h1>
            <p className="text-gray-400">Просмотр и загрузка отчетов по пентестам</p>
          </div>

          {/* Service Selection */}
          <div className="bg-gray-900 rounded-lg shadow-lg p-6 mb-6 border border-gray-700">
            <label className="block text-sm font-medium text-gray-300 mb-3">
              <FiServer className="inline w-4 h-4 mr-2" />
              Выберите сервис
            </label>
            <select
              value={selectedServiceId}
              onChange={(e) => setSelectedServiceId(e.target.value)}
              className="w-full md:w-auto px-4 py-2 bg-gray-800 border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
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
          <div className="bg-gray-900 rounded-lg shadow-lg border border-gray-700">
            <div className="p-6 border-b border-gray-700">
              <h2 className="text-2xl font-bold text-white">
                Отчеты {selectedService && `- ${selectedService.name}`}
              </h2>
            </div>

            {completedPentests.length === 0 ? (
              <div className="p-6 text-center text-gray-400">
                {selectedServiceId
                  ? 'Отчеты для выбранного сервиса не найдены.'
                  : 'Завершенные пентесты не найдены. Отчеты появятся после завершения пентестов.'}
              </div>
            ) : (
              <div className="divide-y divide-gray-700">
                {completedPentests.map((pentest) => (
                  <div
                    key={pentest.id}
                    className="p-6 hover:bg-gray-800 transition-colors duration-200"
                  >
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <FiFileText className="w-5 h-5 text-blue-600" />
                          <h3 className="text-xl font-semibold text-white">{pentest.name}</h3>
                        </div>
                        <p className="text-gray-300 mb-2 font-mono text-sm">{pentest.targetUrl}</p>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span className="flex items-center gap-1">
                            <FiCalendar className="w-4 h-4" />
                            {pentest.completedAt
                              ? new Date(pentest.completedAt).toLocaleString('ru-RU', {
                                  dateStyle: 'long',
                                  timeStyle: 'short',
                                })
                              : new Date(pentest.createdAt).toLocaleString('ru-RU', {
                                  dateStyle: 'long',
                                  timeStyle: 'short',
                                })}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDownloadReport(pentest.id)}
                        className="bg-gradient-to-r from-blue-600 to-blue-800 hover:from-blue-700 hover:to-blue-900 text-white px-6 py-2 rounded-lg font-semibold transition-all duration-200 flex items-center gap-2 shadow-md hover:shadow-lg"
                      >
                        <FiDownload className="w-5 h-5" />
                        Скачать отчет
                      </button>
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

