# Скрипт для отключения режима симуляции на сервере
# Использование: .\disable-simulation.ps1

$ErrorActionPreference = "Stop"

Write-Host "🔧 Отключаю режим симуляции на сервере..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$serverBackendDir = "/opt/xaker/backend"

# Команда для установки USE_SIMULATION=false
$command = "cd $serverBackendDir && if [ -f .env ]; then sed -i '/^USE_SIMULATION=/d' .env; echo 'USE_SIMULATION=false' >> .env; echo 'USE_SIMULATION=false установлен'; else echo 'USE_SIMULATION=false' > .env; echo '.env файл создан'; fi && cat .env | grep USE_SIMULATION"

Write-Host "`n📝 Устанавливаю USE_SIMULATION=false..." -ForegroundColor Yellow
& $plink -ssh $server -pw $password -hostkey $hostkey $command

Write-Host "`n✅ Режим симуляции отключен!" -ForegroundColor Green
Write-Host "⚠️  Убедитесь, что ANTHROPIC_API_KEY установлен и валиден" -ForegroundColor Yellow
Write-Host "🔄 Перезапустите backend: pm2 restart backend`n" -ForegroundColor Cyan

