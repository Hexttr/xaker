# Скрипт для быстрого переключения между моделями Claude
# Использование: .\switch-claude-model.ps1 [haiku|sonnet|sonnet45]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("haiku", "sonnet", "sonnet45")]
    [string]$Model = "sonnet45"
)

$envFile = Join-Path $PSScriptRoot ".env"
$envExampleFile = Join-Path $PSScriptRoot "env.example"

# Определяем модель по параметру
$modelMap = @{
    "haiku" = "claude-3-haiku-20240307"
    "sonnet" = "claude-3-5-sonnet-20241022"
    "sonnet45" = "claude-sonnet-4-5-20250929"
}

$selectedModel = $modelMap[$Model]

Write-Host "`n🔄 Переключение модели Claude..." -ForegroundColor Cyan
Write-Host "   Выбранная модель: $selectedModel" -ForegroundColor Yellow

if (-not (Test-Path $envFile)) {
    Write-Host "`n⚠️  Файл .env не найден, создаю из env.example..." -ForegroundColor Yellow
    if (Test-Path $envExampleFile) {
        Copy-Item $envExampleFile $envFile
    } else {
        Write-Host "❌ Файл env.example также не найден!" -ForegroundColor Red
        exit 1
    }
}

# Читаем содержимое .env
$content = Get-Content $envFile -Raw

# Обновляем или добавляем CLAUDE_MODEL
if ($content -match "CLAUDE_MODEL=") {
    $content = $content -replace "CLAUDE_MODEL=.*", "CLAUDE_MODEL=$selectedModel"
    Write-Host "   ✅ Обновлена существующая переменная CLAUDE_MODEL" -ForegroundColor Green
} else {
    $content += "`n# Claude Model Selection`nCLAUDE_MODEL=$selectedModel`n"
    Write-Host "   ✅ Добавлена новая переменная CLAUDE_MODEL" -ForegroundColor Green
}

# Сохраняем изменения
Set-Content -Path $envFile -Value $content -NoNewline

Write-Host "`n✅ Модель успешно переключена на: $selectedModel" -ForegroundColor Green
Write-Host "`n📋 Информация о моделях:" -ForegroundColor Cyan
Write-Host "   haiku    - Claude 3 Haiku (legacy) - ~`$0.80/`$4 за млн токенов" -ForegroundColor White
Write-Host "   sonnet   - Claude 3.5 Sonnet - ~`$3/`$15 за млн токенов" -ForegroundColor White
Write-Host "   sonnet45 - Claude 4.5 Sonnet - ~`$3/`$15 за млн токенов (самая умная)" -ForegroundColor White
Write-Host "`n⚠️  ВАЖНО: Перезапустите backend для применения изменений!" -ForegroundColor Yellow
Write-Host "   Команда: cd backend && npm run dev`n" -ForegroundColor White

