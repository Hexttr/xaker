# Установка MiroMind через Python и HuggingFace

Write-Host "🧠 Установка MiroMind локально..." -ForegroundColor Cyan

# Проверка Python
$pythonVersion = python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python не найден. Установите Python 3.10+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python найден: $pythonVersion" -ForegroundColor Green

# Создание виртуального окружения
Write-Host "📦 Создание виртуального окружения..." -ForegroundColor Cyan
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка создания виртуального окружения" -ForegroundColor Red
    exit 1
}

# Активация виртуального окружения
Write-Host "🔧 Активация виртуального окружения..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# Установка базовых зависимостей
Write-Host "📥 Установка зависимостей..." -ForegroundColor Cyan
pip install --upgrade pip
pip install transformers torch accelerate

# Создание requirements.txt
@"
transformers>=4.35.0
torch>=2.0.0
accelerate>=0.24.0
"@ | Out-File -FilePath requirements.txt -Encoding UTF8

Write-Host "✅ Установка завершена!" -ForegroundColor Green
Write-Host "📝 Следующий шаг: запустите start-server.ps1" -ForegroundColor Yellow

