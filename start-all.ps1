# Скрипт для запуска всех сервисов
Write-Host "🚀 Запускаю все сервисы..." -ForegroundColor Cyan
Write-Host ""

# Запускаем backend
Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start-backend.ps1"
Start-Sleep -Seconds 3

# Запускаем frontend
Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start-frontend.ps1"
Start-Sleep -Seconds 3

Write-Host "✅ Backend и Frontend запущены" -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:3000" -ForegroundColor White
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")




