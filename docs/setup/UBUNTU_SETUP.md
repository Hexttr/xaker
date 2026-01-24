# 📦 Инструкция по установке Xaker на Ubuntu 24.02

## 📋 Требования

### Системные требования:
- **ОС:** Ubuntu 24.02 LTS
- **Node.js:** v18.0.0 или выше
- **npm:** v9.0.0 или выше
- **Git:** для клонирования репозитория
- **8GB+ RAM** (рекомендуется)
- **5GB+ свободного места** на диске

### Дополнительно:
- **Anthropic API ключ** (для реальных пентестов)
- **VPN** (если находитесь в РФ, для доступа к Anthropic API)

---

## 🚀 Быстрая установка

### Шаг 1: Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
```

### Шаг 2: Установка Node.js

```bash
# Установка Node.js через NodeSource (рекомендуется)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Проверка установки
node --version  # Должно быть: v18.0.0 или выше
npm --version   # Должно быть: v9.0.0 или выше
```

**Альтернативный способ (через snap):**
```bash
sudo snap install node --classic
```

### Шаг 3: Установка системных зависимостей для Puppeteer

Puppeteer требует Chromium и системные библиотеки для генерации PDF:

```bash
# Установка зависимостей для Puppeteer
sudo apt install -y \
  ca-certificates \
  fonts-liberation \
  libappindicator3-1 \
  libasound2 \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libc6 \
  libcairo2 \
  libcups2 \
  libdbus-1-3 \
  libexpat1 \
  libfontconfig1 \
  libgbm1 \
  libgcc1 \
  libglib2.0-0 \
  libgtk-3-0 \
  libnspr4 \
  libnss3 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libstdc++6 \
  libx11-6 \
  libx11-xcb1 \
  libxcb1 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxi6 \
  libxrandr2 \
  libxrender1 \
  libxss1 \
  libxtst6 \
  lsb-release \
  wget \
  xdg-utils

# Установка Chromium (опционально, Puppeteer может использовать встроенный)
sudo apt install -y chromium-browser
```

### Шаг 4: Установка Git (если не установлен)

```bash
sudo apt install -y git
git --version
```

### Шаг 5: Клонирование репозитория

```bash
# Перейдите в нужную директорию
cd /opt  # или /home/username/projects

# Клонируйте репозиторий (замените на ваш URL)
git clone <URL_РЕПОЗИТОРИЯ> xaker
cd xaker

# Переключитесь на ветку prod
git checkout prod
```

### Шаг 6: Установка зависимостей проекта

```bash
# Установка всех зависимостей (корневой проект, backend, frontend)
npm run install:all
```

Это займет несколько минут. Если возникнут ошибки с правами доступа:

```bash
# Исправление прав (если нужно)
sudo chown -R $USER:$USER ~/.npm
```

### Шаг 7: Настройка backend

Создайте файл `.env` на основе примера для продакшена:

```bash
cd backend
cp env.production.example .env
```

Откройте файл `.env` в редакторе:

```bash
# Через nano (встроенный редактор)
nano .env

# Или через vim
vim .env

# Или через VS Code (если установлен)
code .env
```

Обязательно настройте:

```env
# Укажите ваш домен или IP
FRONTEND_URL=http://your-domain.com

# Добавьте ваш Anthropic API ключ
ANTHROPIC_API_KEY=your_api_key_here

# Выберите модель (для экономии используйте haiku)
CLAUDE_MODEL=claude-3-haiku-20240307
```

Сохраните файл:
- В nano: `Ctrl + O` (сохранить), `Enter`, `Ctrl + X` (выйти)
- В vim: `Esc`, `:wq`, `Enter`
- В VS Code: `Ctrl + S`

### Шаг 8: Сборка проекта

```bash
# Вернитесь в корневую директорию
cd ..

# Соберите проект
npm run build
```

### Шаг 9: Настройка прав на скрипты

```bash
# Сделайте скрипты исполняемыми
chmod +x start-all.sh
chmod +x start-backend.sh
chmod +x start-frontend.sh
chmod +x stop-all.sh
chmod +x backend/switch-claude-model.sh
```

---

## 🚀 Запуск приложения

### Вариант 1: Запуск через скрипты (для разработки)

```bash
# Запуск всех сервисов
./start-all.sh

# Или запуск отдельно
./start-backend.sh   # В первом терминале
./start-frontend.sh  # Во втором терминале
```

### Вариант 2: Запуск через PM2 (рекомендуется для продакшена)

Установка PM2:

```bash
sudo npm install -g pm2
```

Запуск через PM2:

```bash
# Запуск backend
cd backend
pm2 start npm --name "xaker-backend" -- run start

# Запуск frontend (если нужен dev режим)
cd ../frontend
pm2 start npm --name "xaker-frontend" -- run dev

# Или для продакшена используйте nginx для раздачи статики
```

Настройка автозапуска PM2:

```bash
pm2 startup
pm2 save
```

### Вариант 3: Запуск через systemd (альтернатива PM2)

Создайте файл `/etc/systemd/system/xaker-backend.service`:

```ini
[Unit]
Description=Xaker Backend Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/xaker/backend
Environment=NODE_ENV=production
ExecStart=/usr/bin/node dist/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация сервиса:

```bash
sudo systemctl daemon-reload
sudo systemctl enable xaker-backend
sudo systemctl start xaker-backend
sudo systemctl status xaker-backend
```

---

## 🌐 Настройка Nginx (для продакшена)

Установка Nginx:

```bash
sudo apt install -y nginx
```

Создайте конфигурацию `/etc/nginx/sites-available/xaker`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend (статичные файлы)
    location / {
        root /opt/xaker/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket для Socket.IO
    location /socket.io {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Активация конфигурации:

```bash
sudo ln -s /etc/nginx/sites-available/xaker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo certbot renew --dry-run
```

---

## 🛠️ Решение проблем

### Проблема: "Command not found: node"

**Решение:**
```bash
# Проверьте установку Node.js
which node
node --version

# Если не установлен, установите через NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### Проблема: "EACCES: permission denied"

**Решение:**
```bash
# Исправление прав на npm директорию
sudo chown -R $USER:$USER ~/.npm
```

### Проблема: Puppeteer не может запустить Chromium

**Решение:**
```bash
# Установите все зависимости для Puppeteer (см. Шаг 3)
sudo apt install -y libgbm1 libnss3 libatk-bridge2.0-0

# Или установите Chromium
sudo apt install -y chromium-browser

# В коде можно указать путь к Chromium:
# PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
```

### Проблема: "Port 3000 already in use" или "Port 5173 already in use"

**Решение:**
```bash
# Найти процесс, использующий порт
sudo lsof -i :3000  # для backend
sudo lsof -i :5173  # для frontend

# Остановить процесс
sudo kill -9 $(sudo lsof -t -i:3000)
sudo kill -9 $(sudo lsof -t -i:5173)
```

### Проблема: "Cannot find module" после установки

**Решение:**
```bash
# Удалите node_modules и установите заново
rm -rf node_modules backend/node_modules frontend/node_modules
npm run install:all
```

---

## 📝 Полезные команды

### Остановка приложения

```bash
# Через скрипт
./stop-all.sh

# Через PM2
pm2 stop all
pm2 delete all

# Через systemd
sudo systemctl stop xaker-backend
```

### Просмотр логов

```bash
# PM2 логи
pm2 logs xaker-backend
pm2 logs xaker-frontend

# systemd логи
sudo journalctl -u xaker-backend -f

# Nginx логи
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Обновление приложения

```bash
# Перейти в директорию проекта
cd /opt/xaker

# Получить последние изменения
git pull origin prod

# Переустановить зависимости (если нужно)
npm run install:all

# Пересобрать проект
npm run build

# Перезапустить сервисы
pm2 restart all
# или
sudo systemctl restart xaker-backend
sudo systemctl reload nginx
```

---

## ✅ Проверка установки

После установки проверьте:

1. ✅ Node.js установлен: `node --version`
2. ✅ npm установлен: `npm --version`
3. ✅ Зависимости установлены: `ls node_modules` (должна быть папка)
4. ✅ Backend .env настроен: `cat backend/.env` (должен содержать ANTHROPIC_API_KEY)
5. ✅ Проект собран: `ls backend/dist` (должны быть скомпилированные файлы)
6. ✅ Backend отвечает: `curl http://localhost:3000/api/services`
7. ✅ Frontend доступен: откройте в браузере ваш домен

---

## 🎯 Следующие шаги

1. Настройте домен и DNS записи
2. Настройте SSL сертификат
3. Настройте бэкапы для данных пентестов
4. Настройте мониторинг (опционально)
5. Изучите [Руководство по тестированию](../guides/REAL_TEST_GUIDE.md)

---

## 💡 Советы

- Используйте **PM2** для управления процессами в продакшене
- Настройте **автоматические бэкапы** для папки `backend/pentests`
- Используйте **fail2ban** для защиты от брутфорса
- Настройте **firewall** (ufw) для ограничения доступа
- Используйте **logrotate** для управления логами

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте раздел "Решение проблем" выше
2. Изучите логи приложения
3. Проверьте статус сервисов: `pm2 status` или `sudo systemctl status xaker-backend`

---

**Готово!** Теперь вы можете использовать Xaker на Ubuntu 24.02. 🎉



