# Скрипт для запуска backend
Set-Location $PSScriptRoot\backend
Write-Host "🚀 Запускаю backend..." -ForegroundColor Cyan
Write-Host ""
npx tsx src/server.ts


