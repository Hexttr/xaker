# Скрипт для установки API ключа на сервере
# Использование: .\set-api-key.ps1 -ApiKey "sk-ant-api03-..."

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiKey
)

$ErrorActionPreference = "Stop"

Write-Host "🔑 Устанавливаю API ключ на сервере..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$serverBackendDir = "/opt/xaker/backend"

# Команда для установки API ключа
$command = "cd $serverBackendDir && if [ -f .env ]; then sed -i '/^ANTHROPIC_API_KEY=/d' .env; echo 'ANTHROPIC_API_KEY=$ApiKey' >> .env; echo 'API ключ установлен'; else echo 'ANTHROPIC_API_KEY=$ApiKey' > .env; echo '.env файл создан'; fi && cat .env | grep ANTHROPIC_API_KEY | head -1"

Write-Host "`n📝 Устанавливаю ANTHROPIC_API_KEY..." -ForegroundColor Yellow
& $plink -ssh $server -pw $password -hostkey $hostkey $command

Write-Host "`n✅ API ключ установлен!" -ForegroundColor Green
Write-Host "🔄 Перезапускаю backend..." -ForegroundColor Yellow
& $plink -ssh $server -pw $password -hostkey $hostkey "cd $serverBackendDir && pm2 restart backend"
Write-Host "✅ Backend перезапущен!`n" -ForegroundColor Green

