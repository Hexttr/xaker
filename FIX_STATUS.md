# Статус исправления

## Текущая ситуация

✅ **docker-compose.yml** - валиден  
✅ **Worker контейнер** - запущен  
⚠️ **Node доступность** - НЕ доступен для пользователя pentest  
⚠️ **Backend** - не запущен  

## Проблема

Ошибка `spawn node ENOENT` возникает потому, что:
- PATH пустой для пользователя `pentest` в Docker контейнере
- Библиотека `@anthropic-ai/claude-agent-sdk` вызывает `spawn('node')`, но не может найти node

## Что уже исправлено

1. ✅ Dockerfile обновлен - PATH установлен перед `USER pentest`
2. ✅ Startup скрипт обновлен - PATH экспортируется явно
3. ✅ docker-compose.yml обновлен - добавлены NODE и PATH env vars
4. ✅ Симлинки созданы - `/usr/local/bin/node` и `/bin/node`

## Что нужно сделать

**Пересобрать Docker образ** с исправленным Dockerfile. Это займет 2-3 минуты.

## Команда для выполнения

```bash
cd /opt/xaker/shannon
docker-compose build --no-cache worker
docker-compose up -d worker
pm2 restart xaker-backend
```

Или запустить скрипт:
```bash
python scripts/final-complete-rebuild.py
```

## После пересборки

После успешной пересборки:
1. Worker будет иметь правильный PATH
2. Node будет доступен для пользователя pentest
3. Ошибка `spawn node ENOENT` должна исчезнуть
4. Пентесты смогут выполняться успешно

