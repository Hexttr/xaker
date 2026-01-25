# Финальное исправление ошибки spawn node ENOENT

## Проблема
Пентест падает с ошибкой: `Failed to spawn Claude Code process: spawn node ENOENT`

## Решение применено

1. ✅ Создан wrapper `/app/bin/node` в running контейнере
2. ✅ Создан симлинк `/usr/local/bin/node -> /usr/bin/node` через docker exec -u root
3. ✅ PATH включает `/usr/local/bin` (уже был в docker-compose.yml)

## Текущий статус

- Wrapper создан: `/app/bin/node` ✅
- Симлинк создан: `/usr/local/bin/node -> /usr/bin/node` ✅  
- PATH включает `/usr/local/bin` ✅
- Worker перезапущен ✅

## Проверка

Выполните на сервере:
```bash
docker exec shannon_worker_1 ls -la /usr/local/bin/node
docker exec shannon_worker_1 which node
docker exec shannon_worker_1 /usr/local/bin/node --version
```

Если все команды работают - запустите новый пентест.

## Важно

Это временное исправление в running контейнере. При пересборке образа изменения потеряются.

Для постоянного исправления нужно:
1. Пересобрать образ с правильным Dockerfile (wrapper создается перед USER pentest)
2. Или использовать volume mount для /usr/local/bin

## Следующие шаги

1. Запустить новый пентест
2. Если работает - пересобрать образ для постоянного исправления
3. Если не работает - проверить логи worker и библиотеки

