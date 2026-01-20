import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { serviceApi, Service, CreateServiceRequest, UpdateServiceRequest } from '../services/api';
import { FiPlus, FiEdit2, FiTrash2, FiServer, FiGlobe } from 'react-icons/fi';

export default function Services() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingService, setEditingService] = useState<Service | null>(null);
  const [formData, setFormData] = useState({ name: '', url: '' });
  const queryClient = useQueryClient();

  const { data: services = [], isLoading } = useQuery({
    queryKey: ['services'],
    queryFn: () => serviceApi.getAll().then(res => res.data),
  });

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

  return (
    <div className="min-h-screen bg-black">
      <div className="p-6 md:p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Сервисы</h1>
              <p className="text-gray-400">Управление целевыми сервисами для пентестинга</p>
            </div>
            <button
              onClick={() => {
                setEditingService(null);
                setFormData({ name: '', url: '' });
                setShowCreateForm(true);
              }}
              className="bg-gradient-to-r from-red-600 to-red-800 hover:from-red-700 hover:to-red-900 text-white px-6 py-2 rounded-lg font-semibold transition-all duration-200 flex items-center gap-2 shadow-md hover:shadow-lg"
            >
              <FiPlus className="w-5 h-5" />
              Добавить сервис
            </button>
          </div>

          {/* Create/Edit Form */}
          {showCreateForm && (
            <div className="bg-gray-900 rounded-lg shadow-lg p-6 mb-6 border border-gray-700 border-l-4 border-l-green-500">
              <h2 className="text-xl font-semibold mb-4 text-white">
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
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
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
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 font-mono"
                    placeholder="https://example.com"
                    required
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={createMutation.isPending || updateMutation.isPending}
                    className="bg-gradient-to-r from-red-600 to-red-800 hover:from-red-700 hover:to-red-900 text-white px-6 py-2 rounded-lg font-semibold disabled:opacity-50 transition-colors duration-200"
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
                    className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-2 rounded-lg font-semibold transition-colors duration-200"
                  >
                    Отмена
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Services List */}
          <div className="bg-gray-900 rounded-lg shadow-lg border border-gray-700">
            <div className="p-6 border-b border-gray-700">
              <h2 className="text-2xl font-bold text-white">Список сервисов</h2>
            </div>

            {isLoading ? (
              <div className="p-6 text-center text-gray-400">Загрузка...</div>
            ) : services.length === 0 ? (
              <div className="p-6 text-center text-gray-400">
                Сервисы еще не добавлены. Создайте новый сервис для начала.
              </div>
            ) : (
              <div className="divide-y divide-gray-700">
                {services.map((service) => (
                  <div
                    key={service.id}
                    className="p-6 hover:bg-gray-800 transition-colors duration-200"
                  >
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <FiServer className="w-5 h-5 text-red-600" />
                          <h3 className="text-xl font-semibold text-white">{service.name}</h3>
                        </div>
                        <div className="flex items-center gap-2 text-gray-400 mb-3">
                          <FiGlobe className="w-4 h-4" />
                          <span className="font-mono text-sm break-all">{service.url}</span>
                        </div>
                        <div className="text-xs text-gray-500">
                          Создан: {new Date(service.createdAt).toLocaleString('ru-RU')}
                          {service.updatedAt !== service.createdAt && (
                            <span className="ml-4">
                              Обновлен: {new Date(service.updatedAt).toLocaleString('ru-RU')}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEdit(service)}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2"
                        >
                          <FiEdit2 className="w-4 h-4" />
                          Редактировать
                        </button>
                        <button
                          onClick={() => {
                            if (confirm('Удалить этот сервис?')) {
                              deleteMutation.mutate(service.id);
                            }
                          }}
                          disabled={deleteMutation.isPending}
                          className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 transition-colors duration-200 flex items-center gap-2"
                        >
                          <FiTrash2 className="w-4 h-4" />
                          Удалить
                        </button>
                      </div>
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

