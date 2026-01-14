import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pentestApi, Pentest, CreatePentestRequest } from '../services/api';
import LogViewer from '../components/LogViewer';
import StatusBar from '../components/StatusBar';

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

  // Получаем текущий статус для отображения
  const { data: statusData } = useQuery({
    queryKey: ['pentest-status', pentest.id],
    queryFn: () => pentestApi.getStatus(pentest.id).then(res => res.data),
    enabled: pentest.status === 'running',
    refetchInterval: pentest.status === 'running' ? 2000 : false,
  });

  // Получаем найденные уязвимости
  const { data: vulnerabilities = [] } = useQuery({
    queryKey: ['pentest-vulnerabilities', pentest.id],
    queryFn: () => pentestApi.getVulnerabilities(pentest.id).then(res => res.data),
    enabled: pentest.status === 'running' || pentest.status === 'completed',
    refetchInterval: pentest.status === 'running' ? 3000 : false,
  });

  const currentStatus = statusData?.status || '⚙️ Выполнение пентеста...';

  return (
    <div className="p-4 md:p-6 hover:bg-gray-50 transition-colors duration-200">
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 md:gap-3 mb-2">
            <h3 className="text-lg md:text-xl font-semibold text-gray-900 break-words">
              {pentest.name}
            </h3>
            <span
              className={`px-2 md:px-3 py-1 rounded-full text-white text-xs md:text-sm font-medium whitespace-nowrap ${getStatusColor(pentest.status)}`}
            >
              {getStatusText(pentest.status)}
            </span>
          </div>
          <StatusBar status={currentStatus} isRunning={pentest.status === 'running'} />
          <p className="text-gray-600 mb-2 break-words">
            <span className="font-medium">Цель:</span> 
            <span className="ml-1 font-mono text-xs md:text-sm break-all">{pentest.targetUrl}</span>
          </p>
          <div className="flex flex-wrap gap-2 md:gap-3 text-xs md:text-sm text-gray-500">
            <span>
              📅 Создан: {new Date(pentest.createdAt).toLocaleString('ru-RU')}
            </span>
            {pentest.startedAt && (
              <span>
                🚀 Запущен: {new Date(pentest.startedAt).toLocaleString('ru-RU')}
              </span>
            )}
          </div>
        </div>
        <div className="flex flex-wrap gap-2 lg:ml-4 lg:flex-nowrap">
          {pentest.status === 'pending' && (
            <button
              onClick={onStart}
              disabled={startPending}
              className="bg-green-600 hover:bg-green-700 text-white px-3 md:px-4 py-2 rounded-lg text-xs md:text-sm font-medium disabled:opacity-50 transition-colors duration-200 flex items-center justify-center gap-2 flex-1 md:flex-initial"
            >
              ▶️ Запустить
            </button>
          )}
          {pentest.status === 'running' && (
            <button
              onClick={onStop}
              disabled={stopPending}
              className="bg-red-600 hover:bg-red-700 text-white px-3 md:px-4 py-2 rounded-lg text-xs md:text-sm font-medium disabled:opacity-50 transition-colors duration-200 flex items-center justify-center gap-2 animate-pulse flex-1 md:flex-initial"
            >
              ⏹️ Остановить
            </button>
          )}
          <button
            onClick={onToggleExpand}
            className="bg-gradient-to-r from-red-600 to-red-800 hover:from-red-700 hover:to-red-900 text-white px-3 md:px-4 py-2 rounded-lg text-xs md:text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 flex-1 md:flex-initial shadow-md hover:shadow-lg"
          >
            {expanded ? (
              <>📋 Скрыть логи</>
            ) : (
              <>📋 Показать логи</>
            )}
          </button>
          <button
            onClick={onDelete}
            disabled={deletePending}
            className="bg-gray-600 hover:bg-gray-700 text-white px-3 md:px-4 py-2 rounded-lg text-xs md:text-sm font-medium disabled:opacity-50 transition-colors duration-200 flex-1 md:flex-initial"
          >
            🗑️ Удалить
          </button>
        </div>
      </div>
      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <VulnerabilitiesList vulnerabilities={vulnerabilities} />
          <div className="mt-4">
            <LogViewer logs={logs} autoScroll={true} maxHeight="24rem" />
          </div>
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
    <div className="min-h-screen bg-gray-100 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6 md:mb-8">
          <div>
            <h1 className="text-2xl md:text-4xl font-bold text-gray-900">
              <span className="bg-gradient-to-r from-red-600 to-red-800 bg-clip-text text-transparent">
                Pentest.red
              </span>
            </h1>
            <p className="text-gray-500 text-sm mt-1 hidden md:block">
              AI пентестер
            </p>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-gradient-to-r from-red-600 to-red-800 hover:from-red-700 hover:to-red-900 text-white px-4 md:px-6 py-2 rounded-lg font-semibold transition-all duration-200 w-full md:w-auto shadow-md hover:shadow-lg"
          >
            {showCreateForm ? 'Отмена' : '+ Новый пентест'}
          </button>
        </div>

        {showCreateForm && (
          <div className="bg-white rounded-lg shadow-lg p-4 md:p-6 mb-6 border border-gray-200">
            <h2 className="text-xl md:text-2xl font-semibold mb-4 text-gray-900">
              Создать новый пентест
            </h2>
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
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold disabled:opacity-50 transition-colors duration-200 w-full md:w-auto"
              >
                {createMutation.isPending ? '⏳ Создание...' : '✅ Создать пентест'}
              </button>
            </form>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg border border-gray-200">
          <div className="p-4 md:p-6 border-b border-gray-200">
            <h2 className="text-xl md:text-2xl font-semibold text-gray-900">
              Список пентестов
            </h2>
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
