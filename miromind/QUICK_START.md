# ⚡ Быстрый старт MiroMind для Xaker

## Для вашей конфигурации (32GB RAM, RTX 5060 8GB)

### 1. Установить Ollama (5 минут)

1. Скачайте: https://ollama.com/download/windows
2. Установите
3. Проверьте: `ollama --version`

### 2. Загрузить модель (10-30 минут)

```powershell
ollama pull mirothinker-8b
```

### 3. Запустить сервер

```powershell
ollama serve
```

Оставьте это окно открытым!

### 4. Настроить Xaker

В `backend/.env` добавьте:
```env
USE_MIROMIND=true
MIROMIND_API_URL=http://localhost:11434/v1
MIROMIND_MODEL=mirothinker-8b
```

### 5. Перезапустить backend

```powershell
cd backend
npm run dev
```

### 6. Готово! ✅

Теперь:
- **Генерация отчетов** → использует MiroMind
- **Shannon** → использует MiroMind (если поддерживается)

## Проверка

```powershell
curl http://localhost:11434/v1/models
```

Должен вернуть список с `mirothinker-8b`

## Преимущества

✅ Не нужен баланс Anthropic  
✅ Не нужен VPN  
✅ Все работает локально  
✅ Нет лимитов запросов  

