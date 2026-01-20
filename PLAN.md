# План разработки Xaker

## Анализ исходного проекта Shannon

### Архитектура Shannon
Shannon использует:
- **Язык**: TypeScript (82.2%), JavaScript (15.8%)
- **Ядро**: Anthropic Claude Agent SDK
- **Архитектура**: Многоагентная система с 4 фазами:
  1. **Reconnaissance** - разведка и картографирование
  2. **Vulnerability Analysis** - анализ уязвимостей
  3. **Exploitation** - эксплуатация (proof-by-exploitation)
  4. **Reporting** - генерация отчетов

### Ключевые компоненты Shannon
- `src/` - основной код
- `configs/` - конфигурации
- `prompts/` - промпты для AI
- `mcp-server/` - MCP сервер
- `scripts/` - вспомогательные скрипты
- `sessions/` - сессии пентестов
- `deliverables/` - отчеты

## План разработки веб-интерфейса

### Этап 1: Подготовка и анализ (Текущий)
**Цель**: Подготовить окружение и понять структуру Shannon

**Задачи**:
1. ✅ Создать структуру проекта
2. ⏳ Изучить исходный код Shannon
3. ⏳ Определить точки интеграции
4. ⏳ Настроить окружение разработки

**Результат**: Готовая структура проекта и понимание архитектуры

---

### Этап 2: Backend API
**Цель**: Создать REST API для управления пентестами

**Технологии**:
- Node.js + TypeScript
- Express или Fastify
- WebSocket (Socket.io) для real-time
- SQLite/PostgreSQL для хранения результатов

**API Endpoints**:
```
POST   /api/pentest/start       - Запуск пентеста
GET    /api/pentest/:id         - Статус пентеста
POST   /api/pentest/:id/stop    - Остановка пентеста
GET    /api/pentest/:id/logs    - Логи в реальном времени (WebSocket)
GET    /api/pentest/:id/report  - Получить отчет
GET    /api/pentests            - Список всех пентестов
POST   /api/config              - Сохранить конфигурацию
GET    /api/config              - Получить конфигурацию
```

**Структура**:
```
backend/
├── src/
│   ├── server.ts          # Главный сервер
│   ├── routes/            # API маршруты
│   ├── services/          # Бизнес-логика
│   │   ├── pentest.service.ts
│   │   └── shannon.service.ts
│   ├── models/            # Модели данных
│   ├── websocket/         # WebSocket обработчики
│   └── config/            # Конфигурация
├── package.json
└── tsconfig.json
```

---

### Этап 3: Frontend
**Цель**: Создать современный веб-интерфейс

**Технологии**:
- React + TypeScript
- Vite для сборки
- Tailwind CSS для стилей
- React Query для управления состоянием
- Socket.io-client для real-time

**Компоненты**:
```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard/     # Главная панель
│   │   ├── PentestList/   # Список пентестов
│   │   ├── PentestDetail/ # Детали пентеста
│   │   ├── Config/        # Настройки
│   │   └── Reports/       # Просмотр отчетов
│   ├── pages/
│   ├── hooks/             # Custom hooks
│   ├── services/          # API клиент
│   ├── types/             # TypeScript типы
│   └── App.tsx
├── package.json
└── vite.config.ts
```

**Основные экраны**:
1. **Dashboard** - обзор активных пентестов
2. **New Pentest** - форма запуска нового пентеста
3. **Pentest Detail** - детали, логи, прогресс
4. **Reports** - просмотр отчетов
5. **Settings** - настройки конфигурации

---

### Этап 4: Интеграция с Shannon
**Цель**: Интегрировать ядро Shannon с веб-интерфейсом

**Подход**:
1. Изучить как Shannon запускается и управляется
2. Создать обертку (wrapper) для вызова Shannon
3. Перехватывать логи и события
4. Сохранять результаты в БД
5. Генерировать отчеты для веб-интерфейса

**Интеграция**:
```
core/
├── shannon/
│   ├── runner.ts          # Запуск Shannon
│   ├── logger.ts          # Перехват логов
│   ├── parser.ts          # Парсинг результатов
│   └── adapter.ts         # Адаптер для веб-интерфейса
└── types.ts
```

---

### Этап 5: База данных
**Цель**: Хранить историю пентестов и результаты

**Схема БД**:
```sql
pentests:
  - id (UUID)
  - name
  - target_url
  - status (pending/running/completed/failed)
  - config (JSON)
  - started_at
  - completed_at
  - created_at

pentest_logs:
  - id
  - pentest_id
  - level (info/warn/error)
  - message
  - timestamp

pentest_results:
  - id
  - pentest_id
  - phase (recon/vuln/exploit/report)
  - data (JSON)
  - timestamp

reports:
  - id
  - pentest_id
  - content (JSON/HTML)
  - created_at
```

---

### Этап 6: Docker и развертывание
**Цель**: Упростить развертывание на Windows

**Docker Compose**:
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
  
  db:
    image: postgres:15
    volumes:
      - db_data:/var/lib/postgresql/data
```

**Windows-специфичные настройки**:
- PowerShell скрипты для запуска
- WSL2 поддержка (опционально)
- Настройка для работы с Windows Defender

---

## Порядок реализации

### Неделя 1: Основа
1. Настройка проекта и окружения
2. Изучение Shannon
3. Создание базового Backend API
4. Создание базового Frontend

### Неделя 2: Интеграция
1. Интеграция с Shannon
2. WebSocket для real-time
3. База данных
4. Базовый UI

### Неделя 3: Полировка
1. Улучшение UI/UX
2. Обработка ошибок
3. Тестирование
4. Документация

---

## Технические решения

### Почему Node.js/TypeScript?
- Shannon уже на TypeScript
- Единый стек технологий
- Легкая интеграция

### Почему React?
- Популярный и зрелый
- Большое сообщество
- Хорошая экосистема

### Почему SQLite для начала?
- Простота настройки
- Не требует отдельного сервера
- Легко мигрировать на PostgreSQL позже

---

## Риски и митигация

1. **Сложность интеграции с Shannon**
   - Митигация: Детальное изучение кода, создание адаптеров

2. **Производительность real-time обновлений**
   - Митигация: Оптимизация WebSocket, батчинг обновлений

3. **Безопасность веб-интерфейса**
   - Митигация: Аутентификация, валидация входных данных

---

## Следующие шаги

1. ✅ Создать структуру проекта
2. ⏳ Настроить package.json и зависимости
3. ⏳ Изучить исходный код Shannon
4. ⏳ Создать базовый Backend сервер
5. ⏳ Создать базовый Frontend








