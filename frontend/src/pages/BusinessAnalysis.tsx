import { FiBarChart2 } from 'react-icons/fi';

export default function BusinessAnalysis() {
  return (
    <div className="min-h-screen bg-black">
      <div className="p-6 md:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gray-900 rounded-lg shadow-lg p-12 border border-gray-700 text-center">
            <FiBarChart2 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h1 className="text-3xl font-bold text-white mb-4">Бизнес анализ</h1>
            <p className="text-gray-400 text-lg">
              Раздел находится в разработке
            </p>
            <p className="text-gray-500 text-sm mt-2">
              Здесь будет отображаться анализ потенциальных потерь из-за уязвимостей
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

