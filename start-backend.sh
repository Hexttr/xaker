#!/bin/bash
# Скрипт для запуска backend

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/backend"

echo "🚀 Запускаю backend..."
echo ""

npm run dev



