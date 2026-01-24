# Скрипт для установки правильного API ключа из master
$ErrorActionPreference = "Stop"

Write-Host "🔑 Устанавливаю правильный API ключ из master..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$serverBackendDir = "/opt/xaker/backend"

# Получаем ключ из master на сервере
Write-Host "`n📥 Получаю ключ из master на сервере..." -ForegroundColor Yellow
$getKeyCommand = "cd /opt/xaker && git stash && git checkout master 2>&1 && cd backend && cat .env | grep '^ANTHROPIC_API_KEY=' | head -1 | cut -d'=' -f2"
$apiKey = & $plink -ssh $server -pw $password -hostkey $hostkey $getKeyCommand

if ($apiKey -match "sk-ant") {
    Write-Host "✅ Ключ получен: $($apiKey.Substring(0, 20))..." -ForegroundColor Green
    
    # Возвращаемся на prod
    Write-Host "`n🔄 Возвращаюсь на prod..." -ForegroundColor Yellow
    & $plink -ssh $server -pw $password -hostkey $hostkey "cd /opt/xaker && git checkout prod 2>&1"
    
    # Устанавливаем ключ в prod
    Write-Host "`n📝 Устанавливаю ключ в prod..." -ForegroundColor Yellow
    $setKeyCommand = "cd $serverBackendDir && if [ -f .env ]; then sed -i '/^ANTHROPIC_API_KEY=/d' .env; echo 'ANTHROPIC_API_KEY=$apiKey' >> .env; echo '✅ Ключ установлен'; else echo 'ANTHROPIC_API_KEY=$apiKey' > .env; echo '✅ .env создан'; fi && cat .env | grep '^ANTHROPIC_API_KEY=' | head -1"
    $result = & $plink -ssh $server -pw $password -hostkey $hostkey $setKeyCommand
    Write-Host $result -ForegroundColor Green
    
    Write-Host "`n🔄 Перезапускаю backend..." -ForegroundColor Yellow
    & $plink -ssh $server -pw $password -hostkey $hostkey "cd $serverBackendDir && pm2 restart backend --update-env"
    Write-Host "✅ Backend перезапущен!`n" -ForegroundColor Green
} else {
    Write-Host "❌ Не удалось получить ключ из master" -ForegroundColor Red
    Write-Host "Попробуйте установить ключ вручную" -ForegroundColor Yellow
}

