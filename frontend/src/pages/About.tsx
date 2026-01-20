import { FiInfo, FiShield } from 'react-icons/fi';

export default function About() {
  return (
    <div className="min-h-screen bg-black">
      <div className="p-4 md:p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gray-900 rounded p-8 border border-gray-700">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-red-600 to-red-800 rounded flex items-center justify-center mx-auto mb-3">
                <FiShield className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-xl font-semibold text-white mb-1.5">
                Pentest<span className="text-red-600">.red</span> ENTERPRISE
              </h1>
              <p className="text-sm text-gray-500">AI Penetration Testing Platform</p>
            </div>

            <div className="space-y-4 text-gray-400">
              <div>
                <h2 className="text-base font-medium text-white mb-1.5 flex items-center gap-1.5">
                  <FiInfo className="w-4 h-4" />
                  О платформе
                </h2>
                <p className="text-sm text-gray-500">
                  Pentest.red ENTERPRISE - это платформа для автоматизированного пентестинга веб-приложений
                  с использованием искусственного интеллекта. Платформа позволяет проводить комплексные
                  проверки безопасности и генерировать детальные отчеты.
                </p>
              </div>

              <div>
                <h2 className="text-base font-medium text-white mb-1.5">Возможности</h2>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-500 ml-3">
                  <li>Управление целевыми сервисами</li>
                  <li>Автоматизированное проведение пентестов</li>
                  <li>Генерация детальных отчетов</li>
                  <li>Мониторинг уязвимостей в реальном времени</li>
                  <li>Бизнес-анализ рисков</li>
                </ul>
              </div>

              <div className="pt-4 border-t border-gray-700">
                <p className="text-xs text-gray-600 text-center">
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

