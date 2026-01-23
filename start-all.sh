#!/bin/bash
# Скрипт для запуска всех сервисов

echo "🚀 Запускаю все сервисы..."
echo ""

# Получаем директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Запускаем backend в фоне
cd "$SCRIPT_DIR/backend"
echo "🚀 Запускаю backend..."
npm run dev > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

# Ждем немного
sleep 3

# Запускаем frontend в фоне
cd "$SCRIPT_DIR/frontend"
echo "🚀 Запускаю frontend..."
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid

sleep 3

echo "✅ Backend и Frontend запущены"
echo ""
echo "Backend: http://localhost:3000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:5173 (PID: $FRONTEND_PID)"
echo ""
echo "Логи:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "Для остановки выполните: ./stop-all.sh"
echo ""



