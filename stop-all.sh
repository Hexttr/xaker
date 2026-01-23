#!/bin/bash
# Скрипт для остановки всех сервисов

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🛑 Останавливаю все процессы Node.js..."

# Останавливаем процессы по PID файлам, если они существуют
if [ -f "$SCRIPT_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$SCRIPT_DIR/backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend остановлен (PID: $BACKEND_PID)"
    fi
    rm -f "$SCRIPT_DIR/backend.pid"
fi

if [ -f "$SCRIPT_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend остановлен (PID: $FRONTEND_PID)"
    fi
    rm -f "$SCRIPT_DIR/frontend.pid"
fi

# Останавливаем все остальные процессы node (на всякий случай)
pkill -f "node.*server" 2>/dev/null
pkill -f "vite" 2>/dev/null

sleep 2
echo "✅ Все процессы остановлены"

