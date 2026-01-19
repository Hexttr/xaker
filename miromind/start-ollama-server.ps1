# Запуск MiroThinker через Ollama

Write-Host "🧠 Запуск MiroThinker через Ollama..." -ForegroundColor Cyan

# Проверка наличия Ollama
$ollamaExists = Get-Command ollama -ErrorAction SilentlyContinue

if (-not $ollamaExists) {
    Write-Host "❌ Ollama не найден!" -ForegroundColor Red
    Write-Host "📥 Скачайте и установите Ollama:" -ForegroundColor Yellow
    Write-Host "   https://ollama.com/download" -ForegroundColor Cyan
    Write-Host "`nПосле установки:" -ForegroundColor Yellow
    Write-Host "   1. Запустите: ollama pull mirothinker-8b" -ForegroundColor White
    Write-Host "   2. Запустите: ollama serve" -ForegroundColor White
    Write-Host "   3. Ollama будет доступен на http://localhost:11434" -ForegroundColor White
    exit 1
}

# Проверка наличия модели
Write-Host "🔍 Проверка наличия модели mirothinker-8b..." -ForegroundColor Cyan
$models = ollama list 2>&1

if ($models -notmatch "mirothinker") {
    Write-Host "📥 Модель не найдена. Загружаю mirothinker-8b..." -ForegroundColor Yellow
    Write-Host "   Это может занять 10-30 минут (модель ~16GB)..." -ForegroundColor Yellow
    ollama pull mirothinker-8b
}

# Запуск сервера Ollama
Write-Host "🚀 Запуск Ollama сервера..." -ForegroundColor Cyan
Write-Host "   Endpoint: http://localhost:11434" -ForegroundColor Green
Write-Host "   Модель: mirothinker-8b" -ForegroundColor Green
Write-Host "`n⚠️  Для работы с Xaker нужно настроить:" -ForegroundColor Yellow
Write-Host "   MIROMIND_API_URL=http://localhost:11434/v1" -ForegroundColor White
Write-Host "   MIROMIND_MODEL=mirothinker-8b" -ForegroundColor White

ollama serve

