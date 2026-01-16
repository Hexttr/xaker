# Инструкция по установке и запуску

## Требования

- **Node.js** 18+ ([скачать](https://nodejs.org/))
- **npm** или **yarn**
- **Git** для клонирования репозитория
- **Windows 10/11**

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/Hexttr/xaker.git
cd xaker
```

### 2. Установка зависимостей

```bash
# Установить зависимости для всех проектов
npm run install:all

# Или вручную:
npm install
cd backend && npm install
cd ../frontend && npm install
```

### 3. Настройка окружения

Создайте файл `.env` в папке `backend`:

```bash
cd backend
copy .env.example .env
```

Отредактируйте `.env` и укажите необходимые параметры:
- `PORT` - порт для backend (по умолчанию 3000)
- `FRONTEND_URL` - URL frontend (по умолчанию http://localhost:5173)
- `ANTHROPIC_API_KEY` - API ключ для Claude (если используете Shannon)

### 4. Запуск в режиме разработки

Из корневой папки проекта:

```bash
npm run dev
```

Это запустит:
- Backend на `http://localhost:3000`
- Frontend на `http://localhost:5173`

### 5. Открыть в браузере

Откройте [http://localhost:5173](http://localhost:5173)

## Структура проекта

```
xaker/
├── backend/          # Backend API сервер
│   ├── src/
│   │   └── server.ts
│   ├── package.json
│   └── tsconfig.json
├── frontend/         # React веб-интерфейс
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── package.json      # Root package.json для монорепо
├── README.md
└── PLAN.md
```

## Возможные проблемы

### Порт уже занят

Если порт 3000 или 5173 занят, измените их в:
- Backend: `backend/.env` → `PORT=3001`
- Frontend: `frontend/vite.config.ts` → `port: 5174`

### Ошибки при установке зависимостей

Попробуйте:
```bash
# Очистить кэш npm
npm cache clean --force

# Удалить node_modules и переустановить
rm -rf node_modules backend/node_modules frontend/node_modules
npm run install:all
```

### Windows Defender блокирует файлы

Добавьте папку проекта в исключения Windows Defender:
1. Откройте "Защита от вирусов и угроз"
2. Управление настройками → Исключения
3. Добавьте папку проекта

## Следующие шаги

После успешного запуска:
1. Изучите код в `backend/src/server.ts`
2. Изучите компоненты в `frontend/src/`
3. Начните разработку согласно `PLAN.md`



