import { FiInfo, FiShield } from 'react-icons/fi';

export default function About() {
  return (
    <div className="min-h-screen bg-black">
      <div className="p-6 md:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gray-900 rounded-lg shadow-lg p-12 border border-gray-700">
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-gradient-to-br from-red-600 to-red-800 rounded-lg flex items-center justify-center mx-auto mb-4">
                <FiShield className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Pentest<span className="text-red-600">.red</span> ENTERPRISE
              </h1>
              <p className="text-gray-400">AI Penetration Testing Platform</p>
            </div>

            <div className="space-y-6 text-gray-300">
              <div>
                <h2 className="text-xl font-semibold text-white mb-2 flex items-center gap-2">
                  <FiInfo className="w-5 h-5" />
                  О платформе
                </h2>
                <p className="text-gray-400">
                  Pentest.red ENTERPRISE - это платформа для автоматизированного пентестинга веб-приложений
                  с использованием искусственного интеллекта. Платформа позволяет проводить комплексные
                  проверки безопасности и генерировать детальные отчеты.
                </p>
              </div>

              <div>
                <h2 className="text-xl font-semibold text-white mb-2">Возможности</h2>
                <ul className="list-disc list-inside space-y-2 text-gray-400 ml-4">
                  <li>Управление целевыми сервисами</li>
                  <li>Автоматизированное проведение пентестов</li>
                  <li>Генерация детальных отчетов</li>
                  <li>Мониторинг уязвимостей в реальном времени</li>
                  <li>Бизнес-анализ рисков</li>
                </ul>
              </div>

              <div className="pt-6 border-t border-gray-700">
                <p className="text-sm text-gray-500 text-center">
                  © 2026 Pentest.red ENTERPRISE. Все права защищены.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

