# Скрипт для перезапуска backend на сервере
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "🔄 Перезапускаю backend..." -ForegroundColor Yellow
& $plink -ssh $server -pw $password -hostkey $hostkey "cd /opt/xaker/backend && pm2 restart backend"
Write-Host "✅ Backend перезапущен!" -ForegroundColor Green

