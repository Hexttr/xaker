#!/bin/bash
# Скрипт для запуска frontend

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/frontend"

echo "🚀 Запускаю frontend..."
echo ""

npm run dev



