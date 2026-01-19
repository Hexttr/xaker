# Запуск MiroMind сервера

Write-Host "🚀 Запуск MiroMind сервера..." -ForegroundColor Cyan

# Активация виртуального окружения
if (-not (Test-Path "venv")) {
    Write-Host "❌ Виртуальное окружение не найдено. Запустите install.ps1" -ForegroundColor Red
    exit 1
}

.\venv\Scripts\Activate.ps1

# Проверка доступности модели
Write-Host "📥 Проверка модели MiroThinker..." -ForegroundColor Cyan

# Запуск простого HTTP сервера для тестирования
# В реальности здесь будет запуск через SGLang или vLLM
Write-Host "⚠️  Для полной установки требуется:" -ForegroundColor Yellow
Write-Host "   1. Установить SGLang или vLLM" -ForegroundColor Yellow
Write-Host "   2. Загрузить модель MiroThinker с HuggingFace" -ForegroundColor Yellow
Write-Host "   3. Запустить inference сервер" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 Документация: https://github.com/MiroMindAI/MiroThinker" -ForegroundColor Cyan

# Временный заглушка для тестирования API
Write-Host "🔧 Запуск тестового сервера на порту 8000..." -ForegroundColor Cyan
Write-Host "   (Это временная заглушка для тестирования интеграции)" -ForegroundColor Yellow

# Можно использовать простой HTTP сервер для тестирования
python -m http.server 8000 --directory . 2>&1 | Out-Null

