# Скрипт для остановки всех сервисов
Write-Host "🛑 Останавливаю все процессы Node.js..." -ForegroundColor Cyan
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Write-Host "✅ Все процессы остановлены" -ForegroundColor Green








