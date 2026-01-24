# Скрипт для быстрого деплоя бэкенда
# Использование: .\deploy-backend.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Деплой бэкенда..." -ForegroundColor Cyan

# 1. Коммитим изменения в Git
Write-Host "📦 Коммит изменений в Git..." -ForegroundColor Yellow
cd C:\Xaker
git add .
git commit -m "Update: Backend changes" 2>&1 | Out-Null
git push origin prod

# 2. На сервере: pull, build, restart
Write-Host "🔄 Обновление на сервере..." -ForegroundColor Yellow
ssh root@pentest.red "cd /opt/xaker/backend && git pull origin prod && npm run build && pm2 restart xaker-backend && sleep 2 && pm2 logs xaker-backend --lines 5 --nostream"

Write-Host "✅ Деплой завершен!" -ForegroundColor Green

