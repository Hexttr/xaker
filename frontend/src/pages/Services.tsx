import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { serviceApi, Service, CreateServiceRequest, UpdateServiceRequest } from '../services/api';
import { pentestApi } from '../services/api';
import { FiPlus, FiEdit2, FiTrash2, FiServer, FiGlobe, FiShield, FiActivity, FiAlertCircle, FiCalendar, FiCheckCircle } from 'react-icons/fi';

export default function Services() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingService, setEditingService] = useState<Service | null>(null);
  const [formData, setFormData] = useState({ name: '', url: '' });
  const queryClient = useQueryClient();

  const { data: services = [], isLoading } = useQuery({
    queryKey: ['services'],
    queryFn: () => serviceApi.getAll().then(res => res.data),
  });

  // Загружаем пентесты для статистики
  const { data: pentests = [] } = useQuery({
    queryKey: ['pentests'],
    queryFn: () => pentestApi.getAll().then(res => res.data),
  });

  // Получаем ID последних завершенных пентестов для каждого сервиса
  const lastPentestIds = useMemo(() => {
    const ids: string[] = [];
    services.forEach(service => {
      const servicePentests = pentests.filter(p => p.targetUrl === service.url);
      const lastCompleted = [...servicePentests]
        .filter(p => p.status === 'completed')
        .sort((a, b) => {
          const dateA = a.completedAt ? new Date(a.completedAt).getTime() : 0;
          const dateB = b.completedAt ? new Date(b.completedAt).getTime() : 0;
          return dateB - dateA;
        })[0];
      if (lastCompleted?.id) {
        ids.push(lastCompleted.id);
      }
    });
    return ids;
  }, [services, pentests]);

  // Загружаем уязвимости для последних завершенных пентестов (максимум 10)
  const pentestIdsToLoad = lastPentestIds.slice(0, 10);
  const vulnerabilitiesData1 = useQuery({
    queryKey: ['vulnerabilities', pentestIdsToLoad[0]],
    queryFn: () => pentestApi.getVulnerabilities(pentestIdsToLoad[0]!).then(res => res.data),
    enabled: !!pentestIdsToLoad[0],
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData2 = useQuery({
    queryKey: ['vulnerabilities', pentestIdsToLoad[1]],
    queryFn: () => pentestApi.getVulnerabilities(pentestIdsToLoad[1]!).then(res => res.data),
    enabled: !!pentestIdsToLoad[1],
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData3 = useQuery({
    queryKey: ['vulnerabilities', pentestIdsToLoad[2]],
    queryFn: () => pentestApi.getVulnerabilities(pentestIdsToLoad[2]!).then(res => res.data),
    enabled: !!pentestIdsToLoad[2],
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData4 = useQuery({
    queryKey: ['vulnerabilities', pentestIdsToLoad[3]],
    queryFn: () => pentestApi.getVulnerabilities(pentestIdsToLoad[3]!).then(res => res.data),
    enabled: !!pentestIdsToLoad[3],
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData5 = useQuery({
    queryKey: ['vulnerabilities', pentestIdsToLoad[4]],
    queryFn: () => pentestApi.getVulnerabilities(pentestIdsToLoad[4]!).then(res => res.data),
    enabled: !!pentestIdsToLoad[4],
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData6 = useQuery({
    queryKey: ['vulnerabilities', pentestIdsToLoad[5]],
    queryFn: () => pentestApi.getVulnerabilities(pentestIdsToLoad[5]!).then(res => res.data),
    enabled: !!pentestIdsToLoad[5],
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData7 = useQuery({
    queryKey: ['vulnerabilities', pentestIdsToLoad[6]],
    queryFn: () => pentestApi.getVulnerabilities(pentestIdsToLoad[6]!).then(res => res.data),
    enabled: !!pentestIdsToLoad[6],
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData8 = useQuery({
    queryKey: ['vulnerabilities', pentestIdsToLoad[7]],
    queryFn: () => pentestApi.getVulnerabilities(pentestIdsToLoad[7]!).then(res => res.data),
    enabled: !!pentestIdsToLoad[7],
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData9 = useQuery({
    queryKey: ['vulnerabilities', pentestIdsToLoad[8]],
    queryFn: () => pentestApi.getVulnerabilities(pentestIdsToLoad[8]!).then(res => res.data),
    enabled: !!pentestIdsToLoad[8],
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData10 = useQuery({
    queryKey: ['vulnerabilities', pentestIdsToLoad[9]],
    queryFn: () => pentestApi.getVulnerabilities(pentestIdsToLoad[9]!).then(res => res.data),
    enabled: !!pentestIdsToLoad[9],
    staleTime: 5 * 60 * 1000,
  });

  // Создаем мапу: pentestId -> количество уязвимостей
  const vulnerabilitiesMap = useMemo(() => {
    const map: Record<string, number> = {};
    const queries = [
      vulnerabilitiesData1,
      vulnerabilitiesData2,
      vulnerabilitiesData3,
      vulnerabilitiesData4,
      vulnerabilitiesData5,
      vulnerabilitiesData6,
      vulnerabilitiesData7,
      vulnerabilitiesData8,
      vulnerabilitiesData9,
      vulnerabilitiesData10,
    ];
    
    pentestIdsToLoad.forEach((pentestId, index) => {
      const query = queries[index];
      if (query?.data) {
        map[pentestId] = query.data.length;
      } else {
        map[pentestId] = 0;
      }
    });
    return map;
  }, [pentestIdsToLoad, vulnerabilitiesData1, vulnerabilitiesData2, vulnerabilitiesData3, vulnerabilitiesData4, vulnerabilitiesData5, vulnerabilitiesData6, vulnerabilitiesData7, vulnerabilitiesData8, vulnerabilitiesData9, vulnerabilitiesData10]);

  const createMutation = useMutation({
    mutationFn: (data: CreateServiceRequest) => serviceApi.create(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] });
      setShowCreateForm(false);
      setFormData({ name: '', url: '' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateServiceRequest }) =>
      serviceApi.update(id, data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] });
      setEditingService(null);
      setFormData({ name: '', url: '' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => serviceApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingService) {
      updateMutation.mutate({ id: editingService.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (service: Service) => {
    setEditingService(service);
    setFormData({ name: service.name, url: service.url });
    setShowCreateForm(true);
  };

  const handleCancel = () => {
    setShowCreateForm(false);
    setEditingService(null);
    setFormData({ name: '', url: '' });
  };

  // Вычисляем статистику для каждого сервиса
  const getServiceStats = (serviceUrl: string) => {
    const servicePentests = pentests.filter(p => p.targetUrl === serviceUrl);
    const completed = servicePentests.filter(p => p.status === 'completed').length;
    const running = servicePentests.filter(p => p.status === 'running').length;
    const failed = servicePentests.filter(p => p.status === 'failed').length;
    
    // Находим последний завершенный пентест
    const lastCompletedPentest = [...servicePentests]
      .filter(p => p.status === 'completed')
      .sort((a, b) => {
        const dateA = a.completedAt ? new Date(a.completedAt).getTime() : 0;
        const dateB = b.completedAt ? new Date(b.completedAt).getTime() : 0;
        return dateB - dateA;
      })[0];
    
    // Получаем количество уязвимостей из последнего пентеста
    const vulnerabilitiesCount = lastCompletedPentest?.id 
      ? (vulnerabilitiesMap[lastCompletedPentest.id] || 0)
      : 0;
    
    return {
      total: servicePentests.length,
      completed,
      running,
      failed,
      vulnerabilities: vulnerabilitiesCount,
    };
  };

  return (
    <div className="min-h-screen bg-black">
      <div className="p-4 md:p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-4">
            <div>
              <h1 className="text-xl font-semibold text-white mb-1">Сервисы</h1>
              <p className="text-sm text-gray-500">Управление целевыми сервисами для пентестинга</p>
            </div>
            <button
              onClick={() => {
                setEditingService(null);
                setFormData({ name: '', url: '' });
                setShowCreateForm(true);
              }}
              className="bg-gradient-to-r from-red-600 to-red-800 hover:from-red-700 hover:to-red-900 text-white px-4 py-1.5 rounded text-sm font-medium transition-all duration-200 flex items-center gap-2"
            >
              <FiPlus className="w-4 h-4" />
              Добавить сервис
            </button>
          </div>

          {/* Create/Edit Form */}
          {showCreateForm && (
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg border-l-4 border-l-green-500 mb-6">
              <h2 className="text-lg font-semibold mb-4 text-white">
                {editingService ? 'Редактировать сервис' : 'Создать новый сервис'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Название сервиса
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2.5 text-sm bg-gray-800 border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                    placeholder="Например: Мой веб-сайт"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    URL сервиса
                  </label>
                  <input
                    type="url"
                    value={formData.url}
                    onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                    className="w-full px-4 py-2.5 text-sm bg-gray-800 border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 font-mono transition-all"
                    placeholder="https://example.com"
                    required
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <button
                    type="submit"
                    disabled={createMutation.isPending || updateMutation.isPending}
                    className="bg-gradient-to-r from-red-600 to-red-800 hover:from-red-700 hover:to-red-900 text-white px-6 py-2.5 rounded-lg text-sm font-semibold disabled:opacity-50 transition-all duration-200 shadow-md hover:shadow-lg"
                  >
                    {createMutation.isPending || updateMutation.isPending
                      ? 'Сохранение...'
                      : editingService
                      ? 'Сохранить изменения'
                      : 'Создать сервис'}
                  </button>
                  <button
                    type="button"
                    onClick={handleCancel}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium transition-colors duration-200"
                  >
                    Отмена
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Services Grid */}
          {isLoading ? (
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-8 border border-gray-700 shadow-lg text-center">
              <p className="text-gray-400">Загрузка...</p>
            </div>
          ) : services.length === 0 ? (
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-8 border border-gray-700 shadow-lg text-center">
              <FiServer className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400 mb-2">Сервисы еще не добавлены</p>
              <p className="text-sm text-gray-500">Создайте новый сервис для начала</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {services.map((service) => {
                const stats = getServiceStats(service.url);
                return (
                  <div
                    key={service.id}
                    className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-4 sm:p-6 border border-gray-700 shadow-lg hover:shadow-xl transition-all duration-200 hover:border-gray-600 min-w-0"
                  >
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4 min-w-0">
                      <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
                        <div className="p-2 sm:p-3 bg-red-500/10 rounded-lg flex-shrink-0">
                          <FiServer className="w-5 h-5 sm:w-6 sm:h-6 text-red-400" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <h3 className="text-base sm:text-lg font-semibold text-white mb-1 truncate">{service.name}</h3>
                          <div className="flex items-center gap-1.5 text-gray-400 min-w-0">
                            <FiGlobe className="w-3 h-3 flex-shrink-0" />
                            <span className="font-mono text-xs break-all">{service.url}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-2 gap-2 sm:gap-3 mb-4">
                      <div className="bg-gray-800/50 rounded-lg p-2 sm:p-3 border border-gray-700 min-w-0">
                        <div className="flex items-center gap-1.5 sm:gap-2 mb-1">
                          <FiShield className="w-3 h-3 sm:w-4 sm:h-4 text-blue-400 flex-shrink-0" />
                          <span className="text-xs text-gray-400 truncate">Пентестов</span>
                        </div>
                        <p className="text-lg sm:text-xl font-bold text-white">{stats.total}</p>
                      </div>
                      <div className="bg-gray-800/50 rounded-lg p-2 sm:p-3 border border-gray-700 min-w-0">
                        <div className="flex items-center gap-1.5 sm:gap-2 mb-1">
                          <FiCheckCircle className="w-3 h-3 sm:w-4 sm:h-4 text-green-400 flex-shrink-0" />
                          <span className="text-xs text-gray-400 truncate">Завершено</span>
                        </div>
                        <p className="text-lg sm:text-xl font-bold text-white">{stats.completed}</p>
                      </div>
                      <div className="bg-gray-800/50 rounded-lg p-2 sm:p-3 border border-gray-700 min-w-0">
                        <div className="flex items-center gap-1.5 sm:gap-2 mb-1">
                          <FiActivity className="w-3 h-3 sm:w-4 sm:h-4 text-blue-400 flex-shrink-0" />
                          <span className="text-xs text-gray-400 truncate">В процессе</span>
                        </div>
                        <p className="text-lg sm:text-xl font-bold text-white">{stats.running}</p>
                      </div>
                      <div className="bg-gray-800/50 rounded-lg p-2 sm:p-3 border border-gray-700 min-w-0">
                        <div className="flex items-center gap-1.5 sm:gap-2 mb-1">
                          <FiAlertCircle className="w-3 h-3 sm:w-4 sm:h-4 text-red-400 flex-shrink-0" />
                          <span className="text-xs text-gray-400 truncate">Ошибок</span>
                        </div>
                        <p className="text-lg sm:text-xl font-bold text-white">{stats.failed}</p>
                      </div>
                      <div className="bg-gray-800/50 rounded-lg p-2 sm:p-3 border border-gray-700 min-w-0 col-span-2">
                        <div className="flex items-center gap-1.5 sm:gap-2 mb-1">
                          <FiAlertCircle className="w-3 h-3 sm:w-4 sm:h-4 text-orange-400 flex-shrink-0" />
                          <span className="text-xs text-gray-400 truncate">Уязвимости</span>
                        </div>
                        <p className="text-lg sm:text-xl font-bold text-white">{stats.vulnerabilities}</p>
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="pt-4 border-t border-gray-700">
                      <div className="flex items-center justify-between mb-3">
                        <div className="text-xs text-gray-500 min-w-0 flex-1">
                          <div className="flex items-center gap-1 mb-1">
                            <FiCalendar className="w-3 h-3 flex-shrink-0" />
                            <span className="truncate">Создан: {new Date(service.createdAt).toLocaleDateString('ru-RU')}</span>
                          </div>
                          {service.updatedAt !== service.createdAt && (
                            <div className="text-xs text-gray-600 truncate">
                              Обновлен: {new Date(service.updatedAt).toLocaleDateString('ru-RU')}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex flex-col sm:flex-row gap-2">
                        <button
                          onClick={() => handleEdit(service)}
                          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors duration-200 flex items-center justify-center gap-1.5 sm:gap-2 min-w-0"
                        >
                          <FiEdit2 className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
                          <span className="truncate">Редактировать</span>
                        </button>
                        <button
                          onClick={() => {
                            if (confirm('Удалить этот сервис?')) {
                              deleteMutation.mutate(service.id);
                            }
                          }}
                          disabled={deleteMutation.isPending}
                          className="flex-1 bg-red-600 hover:bg-red-700 text-white px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium disabled:opacity-50 transition-colors duration-200 flex items-center justify-center gap-1.5 sm:gap-2 min-w-0"
                        >
                          <FiTrash2 className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
                          <span className="truncate">Удалить</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

