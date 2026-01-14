export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Xaker - AI Penetration Tester
        </h1>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Добро пожаловать!</h2>
          <p className="text-gray-600">
            Веб-интерфейс для управления AI пентестером на основе Shannon.
          </p>
          <p className="text-gray-600 mt-2">
            Backend API: <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">http://localhost:3000</span>
          </p>
        </div>
      </div>
    </div>
  );
}

