# Скрипт для проверки режима симуляции на сервере
# Использование: .\check-simulation-mode.ps1

$ErrorActionPreference = "Stop"

Write-Host "🔍 Проверяю режим симуляции на сервере..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$serverBackendDir = "/opt/xaker/backend"

# Проверяем .env на сервере
Write-Host "`n📋 Проверяю .env файл на сервере..." -ForegroundColor Yellow
$envCheck = & $plink -ssh $server -pw $password -hostkey $hostkey "cd $serverBackendDir && cat .env 2>/dev/null | grep -E 'USE_SIMULATION|ANTHROPIC_API_KEY' || echo 'Файл не найден или переменные отсутствуют'"

Write-Host $envCheck

# Проверяем USE_SIMULATION
if ($envCheck -match "USE_SIMULATION=true") {
    Write-Host "`n⚠️  USE_SIMULATION=true - режим симуляции ВКЛЮЧЕН!" -ForegroundColor Red
    Write-Host "   Нужно установить USE_SIMULATION=false" -ForegroundColor Yellow
} elseif ($envCheck -match "USE_SIMULATION=false") {
    Write-Host "`n✅ USE_SIMULATION=false - режим симуляции ОТКЛЮЧЕН" -ForegroundColor Green
} else {
    Write-Host "`nℹ️  USE_SIMULATION не установлен (по умолчанию false)" -ForegroundColor Cyan
}

# Проверяем ANTHROPIC_API_KEY
if ($envCheck -match "ANTHROPIC_API_KEY=your_api_key_here" -or $envCheck -notmatch "ANTHROPIC_API_KEY=") {
    Write-Host "`n⚠️  ANTHROPIC_API_KEY не установлен или равен 'your_api_key_here'" -ForegroundColor Red
    Write-Host "   Будет использоваться режим симуляции" -ForegroundColor Yellow
} elseif ($envCheck -match "ANTHROPIC_API_KEY=") {
    Write-Host "`n✅ ANTHROPIC_API_KEY установлен" -ForegroundColor Green
}

Write-Host "`n💡 Для отключения симуляции:" -ForegroundColor Cyan
Write-Host "   1. Установите USE_SIMULATION=false в .env на сервере" -ForegroundColor White
Write-Host "   2. Установите валидный ANTHROPIC_API_KEY" -ForegroundColor White
Write-Host "   3. Перезапустите backend (pm2 restart backend)`n" -ForegroundColor White

