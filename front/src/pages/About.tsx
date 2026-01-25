import {
  FiInfo,
  FiShield,
  FiServer,
  FiActivity,
  FiFileText,
  FiEye,
  FiBarChart2,
  FiTrendingUp,
} from 'react-icons/fi';

export default function About() {
  const features = [
    {
      icon: FiServer,
      title: 'Управление целевыми сервисами',
      description: 'Добавляйте и управляйте списком сервисов для тестирования',
      color: 'blue',
    },
    {
      icon: FiActivity,
      title: 'Автоматизированное проведение пентестов',
      description: 'Запускайте пентесты с помощью ИИ и отслеживайте прогресс в реальном времени',
      color: 'green',
    },
    {
      icon: FiFileText,
      title: 'Генерация детальных отчетов',
      description: 'Получайте подробные PDF-отчеты с результатами тестирования',
      color: 'purple',
    },
    {
      icon: FiEye,
      title: 'Мониторинг уязвимостей в реальном времени',
      description: 'Отслеживайте обнаруженные уязвимости по мере выполнения пентеста',
      color: 'red',
    },
    {
      icon: FiBarChart2,
      title: 'Бизнес-анализ рисков',
      description: 'Анализируйте риски безопасности и получайте рекомендации',
      color: 'yellow',
    },
    {
      icon: FiTrendingUp,
      title: 'Просмотр динамики',
      description: 'Отслеживайте изменения безопасности во времени и сравнивайте результаты пентестов',
      color: 'cyan',
    },
  ];

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'blue':
        return {
          bg: 'bg-blue-500/10',
          icon: 'text-blue-400',
          border: 'border-blue-500/20',
        };
      case 'green':
        return {
          bg: 'bg-green-500/10',
          icon: 'text-green-400',
          border: 'border-green-500/20',
        };
      case 'purple':
        return {
          bg: 'bg-purple-500/10',
          icon: 'text-purple-400',
          border: 'border-purple-500/20',
        };
      case 'red':
        return {
          bg: 'bg-red-500/10',
          icon: 'text-red-400',
          border: 'border-red-500/20',
        };
      case 'yellow':
        return {
          bg: 'bg-yellow-500/10',
          icon: 'text-yellow-400',
          border: 'border-yellow-500/20',
        };
      case 'cyan':
        return {
          bg: 'bg-cyan-500/10',
          icon: 'text-cyan-400',
          border: 'border-cyan-500/20',
        };
      default:
        return {
          bg: 'bg-gray-500/10',
          icon: 'text-gray-400',
          border: 'border-gray-500/20',
        };
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <div className="p-4 md:p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white mb-1">О сервисе</h1>
              <p className="text-sm text-gray-400">Информация о платформе Pentest.red ENTERPRISE</p>
            </div>
          </div>

          {/* Main Info Card */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-8 border border-gray-700 shadow-lg">
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-gradient-to-br from-red-600 to-red-800 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                <FiShield className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">
                Pentest<span className="text-red-600">.red</span> ENTERPRISE
              </h2>
              <p className="text-base text-gray-400">AI Penetration Testing Platform</p>
            </div>

            <div className="mb-8">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <FiInfo className="w-5 h-5 text-blue-400" />
                О платформе
              </h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Pentest.red ENTERPRISE - это платформа для автоматизированного пентестинга веб-приложений
                с использованием искусственного интеллекта. Платформа позволяет проводить комплексные
                проверки безопасности и генерировать детальные отчеты. Используя передовые технологии
                машинного обучения, система автоматически обнаруживает уязвимости и предоставляет
                подробную аналитику для принятия обоснованных решений по безопасности.
              </p>
            </div>
          </div>

          {/* Features Section */}
          <div>
            <h2 className="text-xl md:text-2xl font-bold text-white mb-6">Возможности</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map((feature, index) => {
                const colors = getColorClasses(feature.color);
                const IconComponent = feature.icon;
                return (
                  <div
                    key={index}
                    className={`bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg hover:shadow-xl transition-all duration-200 hover:border-gray-600 ${colors.border}`}
                  >
                    <div className={`p-3 ${colors.bg} rounded-lg w-fit mb-4`}>
                      <IconComponent className={`w-6 h-6 ${colors.icon}`} />
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                    <p className="text-sm text-gray-400 leading-relaxed">{feature.description}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Footer */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
            <p className="text-xs text-gray-500 text-center">
              © 2026 Pentest.red ENTERPRISE. Все права защищены.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
