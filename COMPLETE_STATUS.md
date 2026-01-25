# Полный статус исправления ошибки spawn node ENOENT

## Текущая ситуация

Ошибка `spawn node ENOENT` все еще возникает при запуске пентеста.

## Что было сделано

### ✅ Исправления в Dockerfile
1. Создан симлинк `/usr/local/bin/node -> /usr/bin/node` **ДО** `USER pentest`
2. Обновлен PATH: `ENV PATH="/usr/bin:/usr/local/bin:$PATH"`

### ✅ Исправления в docker-compose.yml
1. Entrypoint создает симлинк при каждом запуске: `mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node`
2. Добавлена переменная окружения: `NODE=/usr/bin/node`

### ✅ Backend перезапущен
- PM2 процесс `xaker-backend` перезапущен

### ⚠️ Проблемы
1. TypeScript ошибки в Shannon мешают пересборке образа
2. Worker не запускается из-за ошибок сборки
3. Нет существующих образов для использования

## Рекомендации

### Вариант 1: Исправить TypeScript ошибки (рекомендуется)

Нужно исправить импорты Duration в:
- `/opt/xaker/shannon/src/temporal/client.ts` - добавить `Duration` в импорт из `@temporalio/client`
- `/opt/xaker/shannon/src/temporal/workflows.ts` - добавить `import { Duration } from '@temporalio/common';`

После исправления:
```bash
cd /opt/xaker/shannon
npm run build
docker-compose build worker
docker-compose up -d worker
```

### Вариант 2: Использовать старую версию Shannon

Если есть старая рабочая версия Shannon, можно использовать её:
```bash
cd /opt/xaker/shannon
git checkout <старый-коммит-где-работало>
docker-compose build worker
docker-compose up -d worker
```

### Вариант 3: Патч библиотеки через postinstall

Создать скрипт, который будет патчить библиотеку после установки npm пакетов.

## Текущий статус

- ✅ Dockerfile исправлен
- ✅ docker-compose.yml исправлен  
- ✅ Backend перезапущен
- ⚠️ Worker не запускается (TypeScript ошибки)
- ⚠️ Образ не пересобран

## Следующие шаги

1. Исправить TypeScript ошибки в Shannon
2. Пересобрать образ
3. Запустить worker
4. Проверить, что симлинк создается
5. Запустить новый пентест

## Альтернатива

Если исправление TypeScript проблематично, можно:
1. Использовать старую версию Shannon из git
2. Или патчить библиотеку `@anthropic-ai/claude-agent-sdk` напрямую после установки

