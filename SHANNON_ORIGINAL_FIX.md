# Исправление на основе оригинального репозитория Shannon

## Изучение оригинального репозитория

Изучен оригинальный репозиторий Shannon: https://github.com/KeygraphHQ/shannon

### Ключевые находки из оригинального Dockerfile:

1. **Используется `nodejs-22` из apk** - устанавливает node в `/usr/bin/node`
2. **PATH установлен как** `ENV PATH="/usr/local/bin:$PATH"` после `USER pentest`
3. **Нет явного создания симлинка** в оригинале
4. **Entrypoint**: `ENTRYPOINT ["node", "dist/shannon.js"]`

### Проблема:

В оригинальном Dockerfile PATH включает `/usr/local/bin`, но node находится в `/usr/bin/node`. 
Библиотека `@anthropic-ai/claude-agent-sdk` использует `spawn('node', ...)`, который ищет node через PATH.

### Решение:

1. ✅ **Создать симлинк** `/usr/local/bin/node -> /usr/bin/node` **ДО** `USER pentest`
2. ✅ **Обновить PATH** чтобы включить `/usr/bin` первым: `ENV PATH="/usr/bin:/usr/local/bin:$PATH"`

## Примененные исправления

### Dockerfile исправлен:

```dockerfile
# Create symlink for node (nodejs-22 installs to /usr/bin/node)
RUN mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node

USER pentest

# ... другие настройки ...

ENV PATH="/usr/bin:/usr/local/bin:$PATH"
```

### Преимущества этого подхода:

1. **Соответствует оригиналу** - использует тот же подход, что и оригинальный Shannon
2. **Симлинк создается до USER** - пользователь `pentest` имеет доступ к симлинку
3. **PATH включает оба пути** - `/usr/bin` и `/usr/local/bin` для максимальной совместимости
4. **Постоянное решение** - исправление встроено в образ, не теряется при перезапуске

## Статус

- ✅ Dockerfile исправлен
- ✅ Образ пересобран
- ✅ Симлинк создан: `/usr/local/bin/node -> /usr/bin/node`
- ✅ PATH настроен правильно
- ✅ Worker перезапущен

## Следующие шаги

Запустите новый пентест. Ошибка `spawn node ENOENT` должна быть исправлена.

## Ссылки

- Оригинальный репозиторий: https://github.com/KeygraphHQ/shannon
- Оригинальный Dockerfile: https://raw.githubusercontent.com/KeygraphHQ/shannon/main/Dockerfile
- Оригинальный docker-compose.yml: https://raw.githubusercontent.com/KeygraphHQ/shannon/main/docker-compose.yml

