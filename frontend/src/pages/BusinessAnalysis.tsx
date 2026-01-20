import { FiBarChart2 } from 'react-icons/fi';

export default function BusinessAnalysis() {
  return (
    <div className="min-h-screen bg-black">
      <div className="p-4 md:p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gray-900 rounded p-8 border border-gray-700 text-center">
            <FiBarChart2 className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <h1 className="text-xl font-semibold text-white mb-3">Бизнес анализ</h1>
            <p className="text-sm text-gray-500">
              Раздел находится в разработке
            </p>
            <p className="text-xs text-gray-600 mt-2">
              Здесь будет отображаться анализ потенциальных потерь из-за уязвимостей
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

