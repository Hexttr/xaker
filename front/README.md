# Frontend для Pentest.red

Этот каталог содержит фронтенд-приложение пентестера - веб-интерфейс для управления пентестами.

## Структура проекта

```
front/
├── src/
│   ├── components/     # React компоненты
│   ├── pages/          # Страницы приложения
│   ├── services/       # API сервисы
│   ├── contexts/        # React контексты (Auth)
│   ├── utils/           # Утилиты
│   ├── App.tsx          # Главный компонент
│   └── main.tsx         # Точка входа
├── public/              # Статические файлы
├── index.html           # HTML шаблон
├── package.json         # Зависимости
├── vite.config.ts       # Конфигурация Vite
└── tailwind.config.js   # Конфигурация Tailwind CSS
```

## Технологии

- **React 18** - UI библиотека
- **TypeScript** - Типизация
- **Vite** - Сборщик и dev-сервер
- **Tailwind CSS** - Стилизация
- **React Router** - Маршрутизация
- **Axios** - HTTP клиент
- **Socket.io Client** - WebSocket для логов в реальном времени
- **React Query** - Управление состоянием и кэшированием
- **Recharts** - Графики и аналитика

## Установка и запуск

### Требования

- Node.js 18+ 
- npm или yarn

### Установка зависимостей

```bash
cd front
npm install
```

### Разработка

```bash
npm run dev
```

Приложение будет доступно по адресу: `http://localhost:5173`

### Сборка для production

```bash
npm run build
```

Собранные файлы будут в папке `dist/`

### Предпросмотр production сборки

```bash
npm run preview
```

## Конфигурация

### API Endpoint

По умолчанию фронтенд подключается к API по адресу `/api` (относительный путь).

В режиме разработки (`npm run dev`) используется proxy в `vite.config.ts`:
- `/api` → `http://localhost:3000/api`
- `/socket.io` → `http://localhost:3000/socket.io`

### Базовый путь (base path)

В production используется базовый путь `/app/` (настраивается в `vite.config.ts`).

В development используется `/` (корень).

## Основные компоненты

### Pages (Страницы)

- **Home** (`/`) - Главная страница с дашбордом
- **Services** (`/services`) - Управление сервисами
- **Pentests** (`/pentests`) - Управление пентестами
- **Reports** (`/reports`) - Отчеты
- **Analytics** (`/analytics`) - Аналитика
- **About** (`/about`) - О приложении

### Components (Компоненты)

- **Layout** - Основной layout с сайдбаром
- **Sidebar** - Боковое меню навигации
- **LogViewer** - Просмотр логов пентеста в реальном времени
- **VulnerabilitiesList** - Список уязвимостей
- **StatusBar** - Статус бар с информацией о пентесте
- **LoginModal** - Модальное окно авторизации
- **ProtectedRoute** - Защищенный роут (требует авторизации)

### Services (API)

Все API вызовы находятся в `src/services/api.ts`:

- `pentestApi` - API для работы с пентестами
- `serviceApi` - API для работы с сервисами

## Аутентификация

Приложение использует JWT токены для аутентификации.

Токен хранится в `localStorage` под ключом `authToken`.

При отсутствии токена показывается модальное окно логина.

## WebSocket для логов

Приложение подключается к WebSocket серверу (`/socket.io`) для получения логов пентестов в реальном времени.

## Стилизация

Используется **Tailwind CSS** для стилизации.

Основные цвета и темы настраиваются в `tailwind.config.js` и `src/index.css`.

## Развертывание

### Production сборка

1. Соберите проект:
   ```bash
   npm run build
   ```

2. Скопируйте содержимое папки `dist/` на веб-сервер

3. Настройте веб-сервер (nginx/apache) для обслуживания статических файлов

4. Настройте проксирование API запросов на backend сервер

### Пример конфигурации Nginx

```nginx
server {
    listen 80;
    server_name pentest.red;

    # Frontend
    location /app {
        alias /var/www/pentest.red/app;
        try_files $uri $uri/ /app/index.html;
    }

    # API
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /socket.io {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Зависимости

Основные зависимости указаны в `package.json`:

- `react`, `react-dom` - React библиотека
- `react-router-dom` - Маршрутизация
- `axios` - HTTP клиент
- `socket.io-client` - WebSocket клиент
- `@tanstack/react-query` - Управление состоянием
- `recharts` - Графики
- `react-icons` - Иконки

## Примечания

- Приложение автоматически определяет окружение (development/production) по hostname
- В production используется базовый путь `/app/`
- Все API запросы автоматически добавляют JWT токен из localStorage
- При ошибке 401 токен удаляется и показывается модальное окно логина

