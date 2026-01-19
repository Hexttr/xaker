# Установка реальной модели MiroThinker через Ollama или прямую загрузку

Write-Host "🧠 Установка реальной модели MiroThinker..." -ForegroundColor Cyan

# Вариант 1: Через Ollama (рекомендуется для Windows)
Write-Host "`n📦 Вариант 1: Установка через Ollama" -ForegroundColor Yellow
Write-Host "   1. Скачайте Ollama с https://ollama.com/download" -ForegroundColor White
Write-Host "   2. Установите Ollama" -ForegroundColor White
Write-Host "   3. Запустите: ollama pull mirothinker-8b" -ForegroundColor White
Write-Host "   4. Запустите: ollama serve" -ForegroundColor White

# Вариант 2: Прямая установка через transformers
Write-Host "`n📦 Вариант 2: Прямая установка через HuggingFace" -ForegroundColor Yellow

if (-not (Test-Path "venv")) {
    Write-Host "❌ Виртуальное окружение не найдено. Запустите install.ps1" -ForegroundColor Red
    exit 1
}

.\venv\Scripts\Activate.ps1

Write-Host "📥 Загрузка модели MiroThinker-8B с HuggingFace..." -ForegroundColor Cyan
Write-Host "   Это может занять время (модель ~16GB)..." -ForegroundColor Yellow

# Установка дополнительных зависимостей для работы с моделями
pip install huggingface-hub --quiet

# Создание скрипта для загрузки модели
@"
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
import os

model_name = "MiroMindAI/MiroThinker-v1.0-8B"
cache_dir = "./models"

print(f"📥 Загрузка модели {model_name}...")
print("   Это может занять 10-30 минут в зависимости от скорости интернета...")

try:
    # Загружаем модель
    snapshot_download(
        repo_id=model_name,
        cache_dir=cache_dir,
        local_files_only=False
    )
    print(f"✅ Модель загружена в {cache_dir}")
except Exception as e:
    print(f"❌ Ошибка загрузки: {e}")
    print("💡 Попробуйте использовать Ollama (проще для Windows)")
"@ | Out-File -FilePath download-model.py -Encoding UTF8

Write-Host "✅ Скрипт загрузки создан: download-model.py" -ForegroundColor Green
Write-Host "   Запустите: python download-model.py" -ForegroundColor Yellow

