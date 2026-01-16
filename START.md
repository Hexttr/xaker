# Инструкция по запуску

## Быстрый запуск

### Вариант 1: Через PowerShell (рекомендуется)

1. **Убедитесь, что политика выполнения разрешена:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. **Проверьте наличие .env файла:**
```powershell
Test-Path backend\.env
```
Если `False`, создайте файл:
```powershell
Copy-Item backend\env.example backend\.env
```

3. **Запустите проект:**
```powershell
npm run dev
```

### Вариант 2: Через CMD (если PowerShell не работает)

Откройте две командные строки (cmd):

**Окно 1 - Backend:**
```cmd
cd backend
npm run dev
```

**Окно 2 - Frontend:**
```cmd
cd frontend
npm run dev
```

## Проверка работы

После запуска откройте в браузере:

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:3000/api/health

Backend должен вернуть:
```json
{"status":"ok","timestamp":"..."}
```

## Если что-то не работает

1. **Проверьте логи в консоли** - там будут видны ошибки
2. **Проверьте порты:**
```powershell
netstat -ano | findstr ':3000 :5173'
```
3. **Убейте процессы на портах:**
```powershell
# Найти PID
netstat -ano | findstr ':3000'
# Убить (замените PID)
taskkill /PID <PID> /F
```

## Структура .env файла

Файл `backend/.env` должен содержать:
```
PORT=3000
FRONTEND_URL=http://localhost:5173
NODE_ENV=development
```

Если порт 3000 занят, измените на другой:
```
PORT=3001
```

И обновите `frontend/vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:3001',  // Изменить здесь
    changeOrigin: true,
  },
}
```



