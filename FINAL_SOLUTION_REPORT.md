# Финальный отчет и решение проблемы spawn node ENOENT

## Текущая ситуация

Ошибка `spawn node ENOENT` все еще возникает, несмотря на все исправления:
- ✅ Симлинк создан в Dockerfile
- ✅ PATH обновлен
- ✅ Entrypoint создает симлинк при запуске
- ✅ Переменная NODE добавлена в docker-compose.yml
- ⚠️ TypeScript ошибки в Shannon мешают пересборке образа

## Проблема

Библиотека `@anthropic-ai/claude-agent-sdk` использует `spawn('node', ...)` и не может найти node, даже когда:
- Симлинк `/usr/local/bin/node -> /usr/bin/node` создан
- PATH включает `/usr/local/bin` и `/usr/bin`
- Переменная `NODE=/usr/bin/node` установлена

## Возможные причины

1. **Библиотека не использует PATH** - может использовать жестко закодированный путь
2. **Контекст выполнения** - activity в Temporal может иметь другой PATH или окружение
3. **Библиотека использует другой механизм** - может искать node через `which` или другой способ

## Рекомендуемое решение

### Вариант 1: Использовать существующий образ и создать симлинк в running контейнере

Если есть уже собранный образ (даже со старым кодом), можно использовать его и создать симлинк при каждом запуске:

```bash
# На сервере
cd /opt/xaker/shannon
docker-compose down
docker-compose up -d worker

# Создать симлинк в running контейнере
docker exec -u root shannon_worker_1 sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node"

# Проверить
docker exec shannon_worker_1 which node
docker exec shannon_worker_1 /usr/local/bin/node --version
```

### Вариант 2: Исправить TypeScript ошибки и пересобрать

1. Исправить импорт Duration в workflows.ts
2. Исправить использование Duration в retry policies
3. Пересобрать образ

### Вариант 3: Патч библиотеки через postinstall

Создать postinstall скрипт в package.json Shannon, который будет патчить библиотеку после установки:

```json
{
  "scripts": {
    "postinstall": "node scripts/patch-claude-library.js"
  }
}
```

Скрипт будет заменять `'node'` на `'/usr/bin/node'` в библиотеке.

## Текущий статус

- ✅ Dockerfile исправлен (симлинк создается до USER pentest)
- ✅ docker-compose.yml исправлен (entrypoint создает симлинк, добавлена переменная NODE)
- ✅ PATH настроен правильно
- ⚠️ TypeScript ошибки мешают пересборке образа
- ⚠️ Worker не запускается из-за ошибок сборки

## Следующие шаги

1. **Исправить TypeScript ошибки** в workflows.ts (добавить правильный импорт Duration)
2. **Пересобрать образ** после исправления ошибок
3. **Проверить worker** - убедиться, что симлинк создается и node доступен
4. **Запустить новый пентест** и проверить, что ошибка исправлена

## Альтернативное решение

Если пересборка образа проблематична, можно:
1. Использовать существующий образ
2. Создать симлинк в running контейнере через entrypoint (уже сделано)
3. Убедиться, что переменная NODE установлена (уже сделано)
4. Перезапустить backend для применения изменений (уже сделано)

## Проверка

После всех исправлений проверьте:

```bash
# На сервере
docker exec shannon_worker_1 ls -la /usr/local/bin/node
docker exec shannon_worker_1 which node
docker exec shannon_worker_1 printenv NODE
docker exec shannon_worker_1 printenv PATH
```

Если все команды работают, но ошибка все еще возникает, возможно, библиотека использует другой механизм поиска node, и нужно патчить её напрямую.

