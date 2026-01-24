# Быстрое редактирование файлов на сервере
# Использование: .\edit-server-file.ps1 -Path "/opt/xaker/landing/src/components/Header.tsx" -LocalFile "Header.tsx"

param(
    [Parameter(Mandatory=$true)]
    [string]$Path,
    
    [Parameter(Mandatory=$true)]
    [string]$LocalFile,
    
    [string]$Server = "root@pentest.red"
)

Write-Host "📝 Редактирование файла на сервере..." -ForegroundColor Cyan
Write-Host "   Локальный файл: $LocalFile" -ForegroundColor Yellow
Write-Host "   Серверный путь: $Path" -ForegroundColor Yellow

# Проверяем существование локального файла
if (-not (Test-Path $LocalFile)) {
    Write-Host "❌ Локальный файл не найден: $LocalFile" -ForegroundColor Red
    exit 1
}

# Копируем файл на сервер
Write-Host "📤 Копирование файла на сервер..." -ForegroundColor Yellow
scp $LocalFile "${Server}:${Path}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Файл успешно обновлен на сервере!" -ForegroundColor Green
} else {
    Write-Host "❌ Ошибка при копировании файла" -ForegroundColor Red
    exit 1
}

