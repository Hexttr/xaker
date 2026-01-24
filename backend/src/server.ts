import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:5173",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3000;

// Middleware
console.log('🔧 Настройка middleware...');
app.use(cors());
app.use(express.json());

// Логирование всех запросов
app.use((req, res, next) => {
  console.log(`📥 ${req.method} ${req.path} - ${new Date().toISOString()}`);
  next();
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API Routes
console.log('📦 Загрузка routes...');
import authRoutes from './routes/auth.routes';
import pentestRoutes from './routes/pentest.routes';
import serviceRoutes from './routes/service.routes';
import demoRequestsRoutes from './routes/demo-requests.routes';

// Публичные роуты (не требуют аутентификации)
app.use('/api/auth', authRoutes);
app.use('/api/demo-requests', demoRequestsRoutes);

// Защищенные роуты (требуют аутентификации)
import { authMiddleware } from './middleware/auth.middleware';
app.use('/api/pentests', authMiddleware, pentestRoutes);
app.use('/api/services', authMiddleware, serviceRoutes);

console.log('✅ Routes загружены успешно');

// WebSocket connection
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Start server
console.log('🚀 Запуск сервера...');
httpServer.listen(Number(PORT), '0.0.0.0', () => {
  console.log(`✅ Backend server running on http://localhost:${PORT}`);
  console.log(`📡 WebSocket server ready`);
  console.log(`🌐 Accessible on: http://localhost:${PORT} and http://127.0.0.1:${PORT}`);
  console.log(`📋 Endpoints:`);
  console.log(`   - GET  /api/health`);
  console.log(`   - POST /api/auth/login`);
  console.log(`   - GET  /api/auth/verify`);
  console.log(`   - GET  /api/pentests (protected)`);
  console.log(`   - POST /api/pentests (protected)`);
  console.log(`   - POST /api/demo-requests`);
});

// Error handling
httpServer.on('error', (error: NodeJS.ErrnoException) => {
  if (error.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} is already in use`);
  } else {
    console.error('❌ Server error:', error);
  }
  process.exit(1);
});

