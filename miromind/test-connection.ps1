# Тест подключения к MiroMind API

Write-Host "🧪 Тестирование подключения к MiroMind..." -ForegroundColor Cyan

$apiUrl = "http://localhost:8000/v1/models"

try {
    $response = Invoke-WebRequest -Uri $apiUrl -Method GET -TimeoutSec 5
    Write-Host "✅ MiroMind сервер доступен!" -ForegroundColor Green
    Write-Host "📊 Ответ сервера:" -ForegroundColor Cyan
    Write-Host $response.Content
} catch {
    Write-Host "❌ MiroMind сервер недоступен" -ForegroundColor Red
    Write-Host "   Убедитесь, что сервер запущен на порту 8000" -ForegroundColor Yellow
    Write-Host "   Ошибка: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

