import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pentestApi, Pentest, CreatePentestRequest } from '../services/api';

// Компонент для отображения отдельного пентеста
function PentestItem({
  pentest,
  expanded,
  onToggleExpand,
  onStart,
  onStop,
  onDelete,
  startPending,
  stopPending,
  deletePending,
  getStatusColor,
  getStatusText,
}: {
  pentest: Pentest;
  expanded: boolean;
  onToggleExpand: () => void;
  onStart: () => void;
  onStop: () => void;
  onDelete: () => void;
  startPending: boolean;
  stopPending: boolean;
  deletePending: boolean;
  getStatusColor: (status: Pentest['status']) => string;
  getStatusText: (status: Pentest['status']) => string;
}) {
  const { data: logs = [] } = useQuery({
    queryKey: ['pentest-logs', pentest.id],
    queryFn: () => pentestApi.getLogs(pentest.id).then(res => res.data),
    enabled: expanded,
    refetchInterval: expanded ? 1000 : false,
  });

  const getLogColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-600';
      case 'warn': return 'text-yellow-600';
      case 'success': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="p-6 hover:bg-gray-50">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-xl font-semibold text-gray-900">
              {pentest.name}
            </h3>
            <span
              className={`px-3 py-1 rounded-full text-white text-sm font-medium ${getStatusColor(pentest.status)}`}
            >
              {getStatusText(pentest.status)}
            </span>
          </div>
          <p className="text-gray-600 mb-2">
            <span className="font-medium">Цель:</span> {pentest.targetUrl}
          </p>
          <p className="text-sm text-gray-500">
            Создан: {new Date(pentest.createdAt).toLocaleString('ru-RU')}
            {pentest.startedAt && (
              <> • Запущен: {new Date(pentest.startedAt).toLocaleString('ru-RU')}</>
            )}
          </p>
        </div>
        <div className="flex gap-2 ml-4">
          {pentest.status === 'pending' && (
            <button
              onClick={onStart}
              disabled={startPending}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
            >
              Запустить
            </button>
          )}
          {pentest.status === 'running' && (
            <button
              onClick={onStop}
              disabled={stopPending}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
            >
              Остановить
            </button>
          )}
          <button
            onClick={onToggleExpand}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            {expanded ? 'Скрыть логи' : 'Показать логи'}
          </button>
          <button
            onClick={onDelete}
            disabled={deletePending}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
          >
            Удалить
          </button>
        </div>
      </div>
      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h4 className="text-lg font-semibold mb-3">Логи пентеста:</h4>
          {logs.length === 0 ? (
            <p className="text-gray-500 text-sm">Логи отсутствуют</p>
          ) : (
            <div className="bg-gray-900 text-gray-100 p-4 rounded-lg max-h-96 overflow-y-auto font-mono text-sm">
              {logs.map((log: any) => (
                <div key={log.id} className={`mb-1 ${getLogColor(log.level)}`}>
                  <span className="text-gray-400 text-xs mr-2">
                    {new Date(log.timestamp).toLocaleTimeString('ru-RU')}
                  </span>
                  <span className={`font-medium ${getLogColor(log.level)}`}>
                    [{log.level.toUpperCase()}]
                  </span>
                  <span className="ml-2">{log.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function Dashboard() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', targetUrl: '' });
  const [expandedPentestId, setExpandedPentestId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: pentests = [], isLoading } = useQuery({
    queryKey: ['pentests'],
    queryFn: () => pentestApi.getAll().then(res => res.data),
    refetchInterval: 2000, // Обновление каждые 2 секунды
  });

  const createMutation = useMutation({
    mutationFn: (data: CreatePentestRequest) => pentestApi.create(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pentests'] });
      setShowCreateForm(false);
      setFormData({ name: '', targetUrl: '' });
    },
  });

  const startMutation = useMutation({
    mutationFn: (id: string) => pentestApi.start(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pentests'] });
    },
  });

  const stopMutation = useMutation({
    mutationFn: (id: string) => pentestApi.stop(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pentests'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => pentestApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pentests'] });
    },
  });

  const getStatusColor = (status: Pentest['status']) => {
    switch (status) {
      case 'running': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      case 'stopped': return 'bg-gray-500';
      default: return 'bg-yellow-500';
    }
  };

  const getStatusText = (status: Pentest['status']) => {
    switch (status) {
      case 'running': return 'Запущен';
      case 'completed': return 'Завершен';
      case 'failed': return 'Ошибка';
      case 'stopped': return 'Остановлен';
      default: return 'Ожидание';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      name: formData.name,
      config: {
        targetUrl: formData.targetUrl,
      },
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900">
            Pentest.red
            <span className="text-2xl text-gray-600 font-normal ml-3">
              AI Penetration Tester
            </span>
          </h1>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold"
          >
            {showCreateForm ? 'Отмена' : '+ Новый пентест'}
          </button>
        </div>

        {showCreateForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-semibold mb-4">Создать новый пентест</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Название пентеста
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Например: Тест веб-приложения"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL цели
                </label>
                <input
                  type="url"
                  value={formData.targetUrl}
                  onChange={(e) => setFormData({ ...formData, targetUrl: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="https://example.com"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold disabled:opacity-50"
              >
                {createMutation.isPending ? 'Создание...' : 'Создать пентест'}
              </button>
            </form>
          </div>
        )}

        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-2xl font-semibold">Список пентестов</h2>
          </div>

          {isLoading ? (
            <div className="p-6 text-center text-gray-500">Загрузка...</div>
          ) : pentests.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              Нет созданных пентестов. Создайте новый пентест для начала.
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {pentests.map((pentest) => (
                <PentestItem
                  key={pentest.id}
                  pentest={pentest}
                  expanded={expandedPentestId === pentest.id}
                  onToggleExpand={() => setExpandedPentestId(expandedPentestId === pentest.id ? null : pentest.id)}
                  onStart={() => startMutation.mutate(pentest.id)}
                  onStop={() => stopMutation.mutate(pentest.id)}
                  onDelete={() => {
                    if (confirm('Удалить этот пентест?')) {
                      deleteMutation.mutate(pentest.id);
                    }
                  }}
                  startPending={startMutation.isPending}
                  stopPending={stopMutation.isPending}
                  deletePending={deleteMutation.isPending}
                  getStatusColor={getStatusColor}
                  getStatusText={getStatusText}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
