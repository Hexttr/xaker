# Исправление проблемы с Frontend

## Проблема
Frontend не открывается, показывается страница ошибки Яндекса (yastatic.net).

## Решение

### 1. Проверьте окно PowerShell
Откройте окно PowerShell, где запущен `npm run dev`. Там должны быть видны:
- Логи запуска Vite
- Ошибки компиляции (если есть)
- URL сервера (обычно http://localhost:5173)

### 2. Перезапустите серверы

**Вариант 1: Через одно окно**
```powershell
cd C:\Xaker
npm run dev
```

**Вариант 2: Отдельно**
```powershell
# Окно 1 - Backend
cd C:\Xaker\backend
node dist/server.js

# Окно 2 - Frontend  
cd C:\Xaker\frontend
npm run dev
```

### 3. Проверьте порты

```powershell
netstat -ano | findstr ':3000 :5173'
```

Должны быть видны:
- Порт 3000 (backend)
- Порт 5173 (frontend)

### 4. Откройте в браузере

Попробуйте оба варианта:
- http://localhost:5173
- http://127.0.0.1:5173

### 5. Если не работает

1. **Проверьте ошибки в консоли браузера (F12)**
   - Могут быть ошибки JavaScript
   - Могут быть проблемы с импортами

2. **Проверьте ошибки компиляции:**
   ```powershell
   cd C:\Xaker\frontend
   npm run type-check
   ```

3. **Переустановите зависимости:**
   ```powershell
   cd C:\Xaker\frontend
   rm -rf node_modules
   npm install
   ```

## Типичные проблемы

### Ошибка: "Cannot find module"
- Переустановите зависимости: `npm install`

### Ошибка: "Port 5173 is already in use"
- Убейте процесс: `Get-Process node | Stop-Process -Force`
- Или измените порт в `vite.config.ts`

### Страница не загружается
- Убедитесь, что Vite запущен
- Проверьте, что нет ошибок компиляции
- Попробуйте очистить кэш браузера (Ctrl+Shift+Delete)



