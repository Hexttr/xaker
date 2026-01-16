import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pentestApi, Pentest, CreatePentestRequest } from '../services/api';
import LogViewer from '../components/LogViewer';
import StatusBar from '../components/StatusBar';
import VulnerabilitiesList from '../components/VulnerabilitiesList';
import { FiPlus, FiPlay, FiSquare, FiTrash2, FiChevronDown, FiChevronUp, FiClock, FiTarget, FiAlertCircle, FiShield, FiFileText } from 'react-icons/fi';

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

  const handleGenerateReport = async () => {
    try {
      const blob = await pentestApi.generatePdfReport(pentest.id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `pentest-report-${pentest.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Ошибка при генерации PDF:', error);
      alert('Ошибка при генерации PDF отчета');
    }
  };

  return (
    <div className="p-4 md:p-6 hover:bg-gray-800 transition-colors duration-200 border-l-4 border-l-transparent hover:border-l-green-500">
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 md:gap-3 mb-3">
            <h3 className="text-lg md:text-xl font-semibold text-white break-words">
              {pentest.name}
            </h3>
            <span
              className={`px-2 md:px-3 py-1 rounded-full text-white text-xs md:text-sm font-medium whitespace-nowrap flex items-center gap-1.5 ${getStatusColor(pentest.status)}`}
            >
              {pentest.status === 'failed' && <FiAlertCircle className="w-3 h-3" />}
              {getStatusText(pentest.status)}
            </span>
          </div>
          <StatusBar status={currentStatus} isRunning={pentest.status === 'running'} />
          <p className="text-gray-300 mb-3 break-words flex items-center gap-2">
            <FiTarget className="w-4 h-4 text-gray-400 flex-shrink-0" />
            <span className="font-medium text-gray-400">Цель:</span> 
            <span className="ml-2 text-sm break-all text-cyan-400 font-mono">{pentest.targetUrl}</span>
          </p>
          <div className="flex flex-wrap gap-3 md:gap-4 text-xs md:text-sm text-gray-400">
            <span className="flex items-center gap-1">
              <FiClock className="w-3 h-3" />
              Создан: {new Date(pentest.createdAt).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })}
            </span>
            {pentest.startedAt && (
              <span className="flex items-center gap-1">
                <FiClock className="w-3 h-3" />
                Запущен: {new Date(pentest.startedAt).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })}
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
              <FiPlay className="w-4 h-4" />
              Запустить
            </button>
          )}
          {pentest.status === 'running' && (
            <button
              onClick={onStop}
              disabled={stopPending}
              className="bg-red-600 hover:bg-red-700 text-white px-3 md:px-4 py-2 rounded-lg text-xs md:text-sm font-medium disabled:opacity-50 transition-colors duration-200 flex items-center justify-center gap-2 animate-pulse flex-1 md:flex-initial"
            >
              <FiSquare className="w-4 h-4" />
              Остановить
            </button>
          )}
          <button
            onClick={onToggleExpand}
            className="bg-gradient-to-r from-red-600 to-red-800 hover:from-red-700 hover:to-red-900 text-white px-3 md:px-4 py-2 rounded-lg text-xs md:text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 flex-1 md:flex-initial shadow-md hover:shadow-lg"
          >
            {expanded ? (
              <>
                <FiChevronUp className="w-4 h-4" />
                Скрыть логи
              </>
            ) : (
              <>
                <FiChevronDown className="w-4 h-4" />
                Показать логи
              </>
            )}
          </button>
          {pentest.status === 'completed' && (
            <button
              onClick={handleGenerateReport}
              className="bg-gradient-to-r from-blue-600 to-blue-800 hover:from-blue-700 hover:to-blue-900 text-white px-3 md:px-4 py-2 rounded-lg text-xs md:text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 flex-1 md:flex-initial shadow-md hover:shadow-lg"
            >
              <FiFileText className="w-4 h-4" />
              Отчет
            </button>
          )}
          <button
            onClick={onDelete}
            disabled={deletePending}
            className="bg-gray-700 hover:bg-gray-600 text-white px-3 md:px-4 py-2 rounded-lg text-xs md:text-sm font-medium disabled:opacity-50 transition-colors duration-200 flex items-center justify-center gap-2 flex-1 md:flex-initial border border-gray-600"
          >
            <FiTrash2 className="w-4 h-4" />
            Удалить
          </button>
        </div>
      </div>
      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-700">
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
    <div className="min-h-screen bg-black flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold flex items-start gap-3">
                <FiShield className="w-10 h-10 md:w-12 md:h-12 text-red-600 flex-shrink-0" style={{ transform: 'translate(4px, 8px)' }} />
                <div>
                  <div className="flex items-center gap-0">
                    <span className="text-white">Pentest</span>
                    <span className="bg-gradient-to-r from-red-600 to-red-800 bg-clip-text text-transparent">.red</span>
                  </div>
                  <p className="text-gray-400 text-xs md:text-sm mt-1">
                    AI Penetration Testing Platform
                  </p>
                </div>
              </h1>
            </div>
            <button
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="bg-gradient-to-r from-red-600 to-red-800 hover:from-red-700 hover:to-red-900 text-white px-4 md:px-6 py-2 rounded-lg font-semibold transition-all duration-200 w-full md:w-auto shadow-md hover:shadow-lg flex items-center gap-2"
            >
              <FiPlus className="w-4 h-4" />
              {showCreateForm ? 'Отмена' : 'Новый пентест'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-4 md:p-8">
        <div className="max-w-7xl mx-auto">

        {showCreateForm && (
          <div className="bg-gray-900 rounded-lg shadow-lg p-4 md:p-6 mb-6 border border-gray-700 border-l-4 border-l-green-500">
            <h2 className="text-xl md:text-2xl font-semibold mb-4 text-white">
              Создать новый пентест
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Название пентеста
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="Например: Тест веб-приложения"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  URL цели
                </label>
                <input
                  type="url"
                  value={formData.targetUrl}
                  onChange={(e) => setFormData({ ...formData, targetUrl: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 font-mono"
                  placeholder="https://example.com"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="bg-gradient-to-r from-red-600 to-red-800 hover:from-red-700 hover:to-red-900 text-white px-6 py-2 rounded-lg font-semibold disabled:opacity-50 transition-colors duration-200 w-full md:w-auto shadow-md hover:shadow-lg"
              >
                {createMutation.isPending ? 'Создание...' : 'Создать пентест'}
              </button>
            </form>
          </div>
        )}

        <div className="bg-gray-900 rounded-lg shadow-lg border border-gray-700">
          <div className="p-4 md:p-6 border-b border-gray-700">
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">
              Активные пентесты
            </h2>
            <p className="text-gray-400 text-sm md:text-base">
              Мониторинг и управление проверками безопасности.
            </p>
          </div>

          {isLoading ? (
            <div className="p-6 text-center text-gray-400">Загрузка...</div>
          ) : pentests.length === 0 ? (
            <div className="p-6 text-center text-gray-400">
              Пентесты еще не созданы. Создайте новый пентест для начала.
            </div>
          ) : (
            <div className="divide-y divide-gray-700">
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
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-gray-900/50 backdrop-blur-sm mt-auto">
        <div className="max-w-7xl mx-auto px-4 md:px-8 py-4">
          <p className="text-center text-gray-400 text-sm font-mono">
            Enterprise Security Platform • Real-time Threat Detection
          </p>
        </div>
      </footer>
    </div>
  );
}
