import express from 'express';

const app = express();
const PORT = 3000;

// Простой health check без middleware
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Корневой маршрут
app.get('/', (req, res) => {
  res.json({ message: 'Backend is running', port: PORT });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Test server running on http://0.0.0.0:${PORT}`);
  console.log(`✅ Server is listening on port ${PORT}`);
  console.log(`🌐 Try: http://localhost:${PORT}/api/health`);
});



