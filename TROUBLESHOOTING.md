# Решение проблем

## Проблема: "выполнение сценариев отключено в этой системе"

### Решение 1: Изменить политику выполнения (рекомендуется)

Выполните в PowerShell от имени администратора:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Или для текущей сессии:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### Решение 2: Использовать cmd вместо PowerShell

Откройте обычную командную строку (cmd) и выполните:
```cmd
npm run dev
```

### Решение 3: Запустить напрямую через cmd

```cmd
cd backend
npm run dev
```

В другом окне:
```cmd
cd frontend
npm run dev
```

## Проверка работы серверов

### Backend
Откройте в браузере: http://localhost:3000/api/health

Должен вернуть:
```json
{"status":"ok","timestamp":"..."}
```

### Frontend
Откройте в браузере: http://localhost:5173

Должна открыться страница с заголовком "Xaker - AI Penetration Tester"

## Если серверы не запускаются

1. Проверьте, что порты свободны:
```powershell
netstat -ano | findstr ':3000 :5173'
```

2. Убейте процессы, занимающие порты:
```powershell
# Найти PID процесса на порту 3000
netstat -ano | findstr ':3000'
# Убить процесс (замените PID на реальный)
taskkill /PID <PID> /F
```

3. Проверьте логи в консоли, где запущен `npm run dev`

4. Убедитесь, что файл `backend/.env` существует








