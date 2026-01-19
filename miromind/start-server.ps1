# Запуск MiroMind сервера

Write-Host "🚀 Запуск MiroMind сервера..." -ForegroundColor Cyan

# Активация виртуального окружения
if (-not (Test-Path "venv")) {
    Write-Host "❌ Виртуальное окружение не найдено. Запустите install.ps1" -ForegroundColor Red
    exit 1
}

.\venv\Scripts\Activate.ps1

# Запуск тестового сервера
Write-Host "🔧 Запуск тестового сервера на порту 8000..." -ForegroundColor Cyan
Write-Host "   (Это тестовый сервер для проверки интеграции)" -ForegroundColor Yellow
Write-Host "   Для реальной работы нужна установка SGLang/vLLM и модель MiroThinker" -ForegroundColor Yellow
Write-Host ""

python simple-server.py 8000

