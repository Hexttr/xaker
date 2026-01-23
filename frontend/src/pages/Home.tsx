import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { serviceApi, Service } from '../services/api';
import { pentestApi, Pentest, Vulnerability } from '../services/api';
import {
  FiServer,
  FiShield,
  FiAlertCircle,
  FiCheckCircle,
  FiTrendingUp,
  FiTrendingDown,
  FiActivity,
  FiClock,
  FiArrowRight,
  FiBarChart2,
  FiTarget,
} from 'react-icons/fi';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function Home() {
  const [selectedServiceId, setSelectedServiceId] = useState<string>('');

  // Загружаем сервисы
  const { data: services = [] } = useQuery({
    queryKey: ['services'],
    queryFn: () => serviceApi.getAll().then(res => res.data),
  });

  // Загружаем пентесты
  const { data: pentests = [] } = useQuery({
    queryKey: ['pentests'],
    queryFn: () => pentestApi.getAll().then(res => res.data),
  });

  // Фильтруем пентесты по выбранному сервису
  const selectedService = services.find(s => s.id === selectedServiceId);
  const filteredPentests = useMemo(() => {
    if (!selectedServiceId) return pentests;
    return pentests.filter(p => p.targetUrl === selectedService?.url);
  }, [pentests, selectedServiceId, selectedService]);

  // Загружаем уязвимости для последних 5 завершенных пентестов
  const completedPentests = filteredPentests.filter(p => p.status === 'completed');
  const pentestsToLoad = completedPentests.slice(0, 5);
  
  // Загружаем уязвимости для каждого пентеста отдельно
  const vulnerabilitiesData1 = useQuery({
    queryKey: ['vulnerabilities', pentestsToLoad[0]?.id],
    queryFn: () => pentestApi.getVulnerabilities(pentestsToLoad[0]!.id).then(res => res.data),
    enabled: !!pentestsToLoad[0]?.id,
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData2 = useQuery({
    queryKey: ['vulnerabilities', pentestsToLoad[1]?.id],
    queryFn: () => pentestApi.getVulnerabilities(pentestsToLoad[1]!.id).then(res => res.data),
    enabled: !!pentestsToLoad[1]?.id,
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData3 = useQuery({
    queryKey: ['vulnerabilities', pentestsToLoad[2]?.id],
    queryFn: () => pentestApi.getVulnerabilities(pentestsToLoad[2]!.id).then(res => res.data),
    enabled: !!pentestsToLoad[2]?.id,
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData4 = useQuery({
    queryKey: ['vulnerabilities', pentestsToLoad[3]?.id],
    queryFn: () => pentestApi.getVulnerabilities(pentestsToLoad[3]!.id).then(res => res.data),
    enabled: !!pentestsToLoad[3]?.id,
    staleTime: 5 * 60 * 1000,
  });
  const vulnerabilitiesData5 = useQuery({
    queryKey: ['vulnerabilities', pentestsToLoad[4]?.id],
    queryFn: () => pentestApi.getVulnerabilities(pentestsToLoad[4]!.id).then(res => res.data),
    enabled: !!pentestsToLoad[4]?.id,
    staleTime: 5 * 60 * 1000,
  });
  
  const allVulnerabilitiesQueries = [
    vulnerabilitiesData1,
    vulnerabilitiesData2,
    vulnerabilitiesData3,
    vulnerabilitiesData4,
    vulnerabilitiesData5,
  ];

  // Вычисляем метрики
  const metrics = useMemo(() => {
    const totalServices = services.length;
    const totalPentests = filteredPentests.length;
    const completedCount = filteredPentests.filter(p => p.status === 'completed').length;
    const runningCount = filteredPentests.filter(p => p.status === 'running').length;
    const failedCount = filteredPentests.filter(p => p.status === 'failed').length;

    // Собираем все уязвимости из загруженных запросов
    let allVulnerabilities: Vulnerability[] = [];
    allVulnerabilitiesQueries.forEach((query) => {
      if (query.data) {
        allVulnerabilities = [...allVulnerabilities, ...query.data];
      }
    });

    const critical = allVulnerabilities.filter(v => v.severity === 'critical').length;
    const high = allVulnerabilities.filter(v => v.severity === 'high').length;
    const medium = allVulnerabilities.filter(v => v.severity === 'medium').length;
    const low = allVulnerabilities.filter(v => v.severity === 'low').length;
    const totalVulnerabilities = allVulnerabilities.length;

    // Последний пентест
    const lastPentest = [...filteredPentests].sort((a, b) => {
      const dateA = new Date(a.createdAt).getTime();
      const dateB = new Date(b.createdAt).getTime();
      return dateB - dateA;
    })[0];

    return {
      totalServices,
      totalPentests,
      completedPentests: completedCount,
      runningPentests: runningCount,
      failedPentests: failedCount,
      critical,
      high,
      medium,
      low,
      totalVulnerabilities,
      lastPentest,
    };
  }, [services, filteredPentests, allVulnerabilitiesQueries]);

  // Security Score (0-100)
  const securityScore = useMemo(() => {
    if (metrics.totalVulnerabilities === 0) return 100;
    const criticalWeight = metrics.critical * 10;
    const highWeight = metrics.high * 5;
    const mediumWeight = metrics.medium * 2;
    const lowWeight = metrics.low * 1;
    const totalWeight = criticalWeight + highWeight + mediumWeight + lowWeight;
    const score = Math.max(0, 100 - Math.min(100, totalWeight / (metrics.totalPentests || 1)));
    return Math.round(score);
  }, [metrics]);

  // Данные для графика пентестов по датам
  const pentestsChartData = useMemo(() => {
    const last30Days = Array.from({ length: 30 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (29 - i));
      return {
        date: date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' }),
        completed: 0,
        failed: 0,
        running: 0,
      };
    });

    filteredPentests.forEach(pentest => {
      const pentestDate = new Date(pentest.createdAt);
      const daysAgo = Math.floor((Date.now() - pentestDate.getTime()) / (1000 * 60 * 60 * 24));
      if (daysAgo >= 0 && daysAgo < 30) {
        const index = 29 - daysAgo;
        if (pentest.status === 'completed') last30Days[index].completed++;
        else if (pentest.status === 'failed') last30Days[index].failed++;
        else if (pentest.status === 'running') last30Days[index].running++;
      }
    });

    return last30Days;
  }, [filteredPentests]);

  // Данные для круговой диаграммы уязвимостей
  const vulnerabilitiesPieData = [
    { name: 'Критичные', value: metrics.critical, color: '#dc2626' },
    { name: 'Высокие', value: metrics.high, color: '#ea580c' },
    { name: 'Средние', value: metrics.medium, color: '#f59e0b' },
    { name: 'Низкие', value: metrics.low, color: '#eab308' },
  ];

  // Последние пентесты (топ 5)
  const recentPentests = useMemo(() => {
    return [...filteredPentests]
      .sort((a, b) => {
        const dateA = new Date(a.createdAt).getTime();
        const dateB = new Date(b.createdAt).getTime();
        return dateB - dateA;
      })
      .slice(0, 5);
  }, [filteredPentests]);

  // Критические уязвимости (топ 10)
  const criticalVulnerabilities = useMemo(() => {
    // Здесь нужно собрать все уязвимости из завершенных пентестов
    // Пока возвращаем пустой массив, так как нужна более сложная логика
    return [];
  }, []);

  const getStatusColor = (status: Pentest['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'running':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'failed':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'stopped':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  const getStatusText = (status: Pentest['status']) => {
    switch (status) {
      case 'completed':
        return 'Завершен';
      case 'running':
        return 'Выполняется';
      case 'failed':
        return 'Ошибка';
      case 'stopped':
        return 'Остановлен';
      default:
        return 'Ожидание';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-black">
      <div className="p-4 md:p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white mb-1">Дэшборд</h1>
              <p className="text-sm text-gray-400">
                {selectedService
                  ? `Статистика по сервису: ${selectedService.name}`
                  : 'Общая статистика по всем сервисам'}
              </p>
            </div>
            <div className="flex gap-2">
              <select
                value={selectedServiceId}
                onChange={(e) => setSelectedServiceId(e.target.value)}
                className="px-4 py-2 bg-gray-900 border border-gray-700 text-white rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Security Score */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-500/10 rounded-lg">
                  <FiShield className="w-6 h-6 text-blue-400" />
                </div>
                <span className={`text-3xl font-bold ${getScoreColor(securityScore)}`}>
                  {securityScore}
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Security Score</h3>
              <p className="text-xs text-gray-500">Общий уровень безопасности</p>
            </div>

            {/* Total Services */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-purple-500/10 rounded-lg">
                  <FiServer className="w-6 h-6 text-purple-400" />
                </div>
                <span className="text-3xl font-bold text-white">{metrics.totalServices}</span>
              </div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Сервисов</h3>
              <p className="text-xs text-gray-500">Всего отслеживается</p>
            </div>

            {/* Total Pentests */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-500/10 rounded-lg">
                  <FiActivity className="w-6 h-6 text-green-400" />
                </div>
                <div className="text-right">
                  <span className="text-3xl font-bold text-white block">{metrics.totalPentests}</span>
                  <div className="text-xs text-gray-500 mt-1">
                    <span className="text-green-400">{metrics.completedPentests}</span> /{' '}
                    <span className="text-blue-400">{metrics.runningPentests}</span> /{' '}
                    <span className="text-red-400">{metrics.failedPentests}</span>
                  </div>
                </div>
              </div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Пентестов</h3>
              <p className="text-xs text-gray-500">Завершено / В процессе / Ошибок</p>
            </div>

            {/* Total Vulnerabilities */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-red-500/10 rounded-lg">
                  <FiAlertCircle className="w-6 h-6 text-red-400" />
                </div>
                <div className="text-right">
                  <span className="text-3xl font-bold text-white block">{metrics.totalVulnerabilities}</span>
                  <div className="text-xs text-gray-500 mt-1">
                    <span className="text-red-400">{metrics.critical}</span> /{' '}
                    <span className="text-orange-400">{metrics.high}</span> /{' '}
                    <span className="text-yellow-400">{metrics.medium}</span> /{' '}
                    <span className="text-yellow-300">{metrics.low}</span>
                  </div>
                </div>
              </div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">Уязвимостей</h3>
              <p className="text-xs text-gray-500">Критич. / Высок. / Сред. / Низк.</p>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Pentests Chart */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <h2 className="text-lg font-semibold text-white mb-4">Пентесты за 30 дней</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={pentestsChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
                  <YAxis stroke="#9ca3af" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '8px',
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="completed"
                    stroke="#10b981"
                    strokeWidth={2}
                    name="Завершено"
                  />
                  <Line
                    type="monotone"
                    dataKey="running"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    name="В процессе"
                  />
                  <Line
                    type="monotone"
                    dataKey="failed"
                    stroke="#ef4444"
                    strokeWidth={2}
                    name="Ошибки"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Vulnerabilities Pie Chart */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <h2 className="text-lg font-semibold text-white mb-4">Распределение уязвимостей</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={vulnerabilitiesPieData.filter(item => item.value > 0)}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ cx, cy, midAngle, innerRadius, outerRadius, name, percent }) => {
                      if (!midAngle || percent === undefined) return null;
                      const RADIAN = Math.PI / 180;
                      const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
                      const x = cx + radius * Math.cos(-midAngle * RADIAN);
                      const y = cy + radius * Math.sin(-midAngle * RADIAN);

                      return (
                        <text
                          x={x}
                          y={y}
                          fill="#ffffff"
                          textAnchor={x > cx ? 'start' : 'end'}
                          dominantBaseline="central"
                          fontSize={13}
                          fontWeight="700"
                          style={{
                            filter: 'drop-shadow(0 0 4px rgba(0,0,0,0.9))',
                            textShadow: '2px 2px 4px rgba(0,0,0,0.9), 0 0 8px rgba(0,0,0,0.5)',
                          }}
                        >
                          {`${name}: ${(percent * 100).toFixed(0)}%`}
                        </text>
                      );
                    }}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {vulnerabilitiesPieData
                      .filter(item => item.value > 0)
                      .map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#111827',
                      border: '2px solid #4b5563',
                      borderRadius: '8px',
                      color: '#ffffff',
                      fontSize: '13px',
                      fontWeight: '600',
                      padding: '10px 14px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
                    }}
                    itemStyle={{
                      color: '#ffffff',
                      fontSize: '13px',
                      fontWeight: '600',
                    }}
                    labelStyle={{
                      color: '#e5e7eb',
                      fontSize: '14px',
                      fontWeight: '700',
                      marginBottom: '4px',
                    }}
                    formatter={(value: number | undefined, name: string) => [`${value ?? 0}`, name]}
                  />
                  <Legend
                    wrapperStyle={{ color: '#e5e7eb', fontSize: '13px', fontWeight: '500' }}
                    iconType="circle"
                    formatter={(value: string, entry: any) => {
                      const total = vulnerabilitiesPieData.reduce((sum, item) => sum + item.value, 0);
                      const percent = total > 0 ? ((entry.payload.value / total) * 100).toFixed(0) : '0';
                      return `${value}: ${percent}%`;
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              {/* Дополнительная информация под графиком */}
              {vulnerabilitiesPieData.some(item => item.value === 0) && (
                <div className="mt-4 pt-4 border-t border-gray-700">
                  <div className="flex flex-wrap gap-4 text-xs text-gray-400">
                    {vulnerabilitiesPieData
                      .filter(item => item.value === 0)
                      .map((item, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: item.color }}
                          />
                          <span>{item.name}: 0</span>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Recent Pentests and Critical Vulnerabilities */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Pentests */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">Последние пентесты</h2>
                <Link
                  to="/pentests"
                  className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
                >
                  Все пентесты <FiArrowRight className="w-4 h-4" />
                </Link>
              </div>
              <div className="space-y-3">
                {recentPentests.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-8">Нет пентестов</p>
                ) : (
                  recentPentests.map((pentest) => (
                    <Link
                      key={pentest.id}
                      to="/pentests"
                      className="block p-4 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-sm font-medium text-white mb-1">{pentest.name}</h3>
                          <p className="text-xs text-gray-400 font-mono mb-2">{pentest.targetUrl}</p>
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <FiClock className="w-3 h-3" />
                            {new Date(pentest.createdAt).toLocaleString('ru-RU')}
                          </div>
                        </div>
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(
                            pentest.status
                          )}`}
                        >
                          {getStatusText(pentest.status)}
                        </span>
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </div>

            {/* Critical Vulnerabilities */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">Критические уязвимости</h2>
                <Link
                  to="/analytics"
                  className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
                >
                  Аналитика <FiArrowRight className="w-4 h-4" />
                </Link>
              </div>
              <div className="space-y-3">
                {metrics.critical === 0 && metrics.high === 0 ? (
                  <div className="text-center py-8">
                    <FiCheckCircle className="w-12 h-12 text-green-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">Нет критических уязвимостей</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {metrics.critical > 0 && (
                      <div className="p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <FiAlertCircle className="w-4 h-4 text-red-400" />
                              <span className="text-sm font-medium text-red-400">Критичные</span>
                            </div>
                            <p className="text-xs text-gray-400">
                              {metrics.critical} критических уязвимостей требуют немедленного внимания
                            </p>
                          </div>
                          <span className="text-2xl font-bold text-red-400">{metrics.critical}</span>
                        </div>
                      </div>
                    )}
                    {metrics.high > 0 && (
                      <div className="p-4 bg-orange-500/10 rounded-lg border border-orange-500/20">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <FiAlertCircle className="w-4 h-4 text-orange-400" />
                              <span className="text-sm font-medium text-orange-400">Высокие</span>
                            </div>
                            <p className="text-xs text-gray-400">
                              {metrics.high} высоких уязвимостей требуют внимания
                            </p>
                          </div>
                          <span className="text-2xl font-bold text-orange-400">{metrics.high}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

