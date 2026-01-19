# Скрипт для настройки модели в Ollama

Write-Host "🧠 Настройка модели для Ollama..." -ForegroundColor Cyan

$ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"

if (-not (Test-Path $ollamaPath)) {
    Write-Host "❌ Ollama не найден!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Ollama найден: $ollamaPath" -ForegroundColor Green

# Проверяем доступные модели
Write-Host "`n📋 Проверка доступных моделей..." -ForegroundColor Cyan
$models = & $ollamaPath list 2>&1
Write-Host $models

# MiroThinker может быть недоступен в Ollama напрямую
# Используем альтернативу - llama3.1 или mistral, которые совместимы
Write-Host "`n💡 MiroThinker может быть недоступен в Ollama" -ForegroundColor Yellow
Write-Host "   Используем альтернативу: llama3.1:8b (совместимая модель)" -ForegroundColor Yellow

Write-Host "`n📥 Загрузка llama3.1:8b..." -ForegroundColor Cyan
& $ollamaPath pull llama3.1:8b

Write-Host "`n✅ Модель загружена!" -ForegroundColor Green
Write-Host "   Для использования в Xaker настройте:" -ForegroundColor Yellow
Write-Host "   MIROMIND_MODEL=llama3.1:8b" -ForegroundColor White

