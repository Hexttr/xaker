#!/bin/bash

# Скрипт для деплоя landing page на сервер
# Использование: ./deploy-landing.sh

set -e

echo "🚀 Начинаем деплой landing page..."

# Переменные
SERVER_USER="root"
SERVER_HOST="5.129.235.52"
SERVER_LANDING_DIR="/var/www/pentest.red/landing"
LOCAL_LANDING_DIR="landing"

# Проверяем, что мы в правильной директории
if [ ! -d "$LOCAL_LANDING_DIR" ]; then
    echo "❌ Ошибка: директория $LOCAL_LANDING_DIR не найдена"
    exit 1
fi

# Собираем landing page
echo "📦 Собираем landing page..."
cd "$LOCAL_LANDING_DIR"
npm install --silent
npm run build

if [ ! -d "dist" ]; then
    echo "❌ Ошибка: сборка не создала директорию dist"
    exit 1
fi

echo "✅ Сборка завершена"

# Создаем временный архив
echo "📦 Создаем архив..."
cd ..
TEMP_ARCHIVE=$(mktemp -u landing-XXXXXX.tar.gz)
tar -czf "$TEMP_ARCHIVE" -C "$LOCAL_LANDING_DIR/dist" .

# Копируем на сервер
echo "📤 Копируем на сервер..."
ssh "$SERVER_USER@$SERVER_HOST" "mkdir -p $SERVER_LANDING_DIR"
scp "$TEMP_ARCHIVE" "$SERVER_USER@$SERVER_HOST:/tmp/"

# Распаковываем на сервере
echo "📥 Распаковываем на сервере..."
ssh "$SERVER_USER@$SERVER_HOST" << EOF
    cd $SERVER_LANDING_DIR
    rm -rf *
    tar -xzf /tmp/$TEMP_ARCHIVE
    rm /tmp/$TEMP_ARCHIVE
    chown -R www-data:www-data $SERVER_LANDING_DIR
    chmod -R 755 $SERVER_LANDING_DIR
EOF

# Удаляем локальный архив
rm "$TEMP_ARCHIVE"

echo "✅ Landing page успешно задеплоен!"
echo "🌐 Проверьте: https://pentest.red/"

