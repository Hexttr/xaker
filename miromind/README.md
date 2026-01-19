# MiroMind локальная установка

Этот каталог содержит конфигурацию для локального развертывания MiroMind.

## Установка через Docker (рекомендуется)

```bash
# Запуск MiroThinker через Docker
docker run -d \
  --name mirothinker \
  -p 8000:8000 \
  --gpus all \
  miromind/mirothinker:latest
```

## Установка через Python (альтернатива)

```bash
# Установка зависимостей
pip install transformers torch accelerate

# Загрузка модели
python -m transformers.download --model MiroMindAI/MiroThinker-v1.0-8B
```

## Проверка доступности

```bash
curl http://localhost:8000/v1/models
```

## Конфигурация

Endpoint по умолчанию: `http://localhost:8000/v1`
Модель по умолчанию: `mirothinker-8b`

