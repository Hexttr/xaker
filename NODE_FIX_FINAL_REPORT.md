# Финальный отчет по исправлению ошибки spawn node ENOENT

## Проблема
Пентест падает с ошибкой: `Failed to spawn Claude Code process: spawn node ENOENT`

## Причина
Библиотека `@anthropic-ai/claude-agent-sdk` запускает процесс `node` через `spawn('node', ...)`, но не находит его в PATH внутри Docker контейнера worker.

## Примененные исправления

### 1. ✅ Создан симлинк `/usr/local/bin/node -> /usr/bin/node`
- Создается автоматически через entrypoint в docker-compose.yml
- PATH включает `/usr/local/bin`

### 2. ✅ Создан wrapper script `/usr/local/bin/node`
- Скрипт выполняет `exec /usr/bin/node "$@"`
- Доступен в PATH

### 3. ✅ Обновлен entrypoint в docker-compose.yml
- Entrypoint создает симлинк при каждом запуске контейнера
- Команда: `mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js`

### 4. ⚠️ Попытка патча библиотеки
- Файл минифицирован, паттерны не найдены
- Прямой патч не удался

## Текущий статус

- ✅ Симлинк создается автоматически
- ✅ Wrapper script создан
- ✅ PATH настроен правильно
- ⚠️ Ошибка все еще возникает

## Возможные причины сохранения ошибки

1. **Библиотека не использует PATH** - может использовать жестко закодированный путь или другой механизм поиска
2. **Контекст выполнения** - activity в Temporal может иметь другой PATH
3. **Права доступа** - пользователь `pentest` может не иметь доступа к `/usr/local/bin/node`

## Рекомендации

### Вариант 1: Пересобрать Docker образ
Пересобрать образ с правильным Dockerfile, где симлинк создается до `USER pentest`:

```dockerfile
RUN mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node
ENV PATH="/usr/local/bin:$PATH"
USER pentest
```

### Вариант 2: Использовать переменную окружения NODE
Если библиотека поддерживает переменную `NODE`, установить её в docker-compose.yml:

```yaml
environment:
  - NODE=/usr/bin/node
```

### Вариант 3: Патч библиотеки через postinstall
Создать postinstall скрипт в package.json Shannon, который будет патчить библиотеку после установки:

```json
{
  "scripts": {
    "postinstall": "node scripts/patch-claude-library.js"
  }
}
```

### Вариант 4: Использовать volume mount
Создать node wrapper на хосте и смонтировать его в контейнер:

```yaml
volumes:
  - /usr/local/bin/node:/usr/local/bin/node:ro
```

## Следующие шаги

1. Проверить логи worker для понимания контекста выполнения
2. Попробовать установить переменную `NODE=/usr/bin/node`
3. Если не поможет - пересобрать образ с правильным Dockerfile
4. В крайнем случае - патчить библиотеку через postinstall скрипт

## Файлы и скрипты

Все скрипты для исправления находятся в `scripts/`:
- `create-symlink-final.py` - создание симлинка
- `create-node-wrapper-script.py` - создание wrapper script
- `fix-entrypoint-permanent.py` - обновление entrypoint
- `patch-library-force.py` - попытка патча библиотеки
- И другие вспомогательные скрипты

