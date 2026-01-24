# Исправление конфликта и обновление frontend
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔧 Исправление конфликта и обновление...`n" -ForegroundColor Cyan

# Удаляем конфликтующий файл
Write-Host "1. Удаляем конфликтующий файл..." -ForegroundColor Yellow
$cmd1 = "cd /opt/xaker && rm -f landing/src/components/RequestDemoModal.tsx && git pull origin prod"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

# Пересобираем frontend
Write-Host "2. Пересобираем frontend..." -ForegroundColor Yellow
$cmd2 = "cd /opt/xaker/frontend && rm -rf node_modules/.vite dist && npm run build"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

# Проверяем результат
Write-Host "3. Проверяем результат..." -ForegroundColor Yellow
$cmd3 = "cd /opt/xaker/frontend && git log --oneline -1 && ls -lt dist/assets/index-*.js | head -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd3

Write-Host "`n✅ Готово!`n" -ForegroundColor Green

