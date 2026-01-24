# Исправление конфликта и обновление кода на сервере
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔧 Исправление конфликта на сервере...`n" -ForegroundColor Cyan

# Удаляем конфликтующие файлы
Write-Host "1. Удаляем конфликтующие файлы..." -ForegroundColor Yellow
$cmd1 = "cd /opt/xaker && rm -f backend/src/routes/demo-requests.routes.ts frontend/public/favicon.svg"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

# Обновляем код
Write-Host "2. Обновляем код из Git..." -ForegroundColor Yellow
$cmd2 = "cd /opt/xaker && git pull origin prod"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

# Проверяем коммит
Write-Host "3. Проверяем коммит..." -ForegroundColor Yellow
$cmd3 = "cd /opt/xaker && git log --oneline -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd3

# Пересобираем frontend
Write-Host "4. Пересобираем frontend..." -ForegroundColor Yellow
$cmd4 = "cd /opt/xaker/frontend && rm -rf node_modules/.vite dist && npm run build"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd4

# Проверяем наличие __DEBUG__
Write-Host "5. Проверяем наличие __DEBUG__..." -ForegroundColor Yellow
$cmd5 = "cd /opt/xaker/frontend/dist/assets && grep -l '__DEBUG__' index-*.js 2>/dev/null | head -1"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd5
if ($result) {
    Write-Host "✅ Найден файл с __DEBUG__: $result" -ForegroundColor Green
} else {
    Write-Host "❌ Файлы с __DEBUG__ не найдены!" -ForegroundColor Red
}

# Перезагружаем Nginx
Write-Host "6. Перезагружаем Nginx..." -ForegroundColor Yellow
$cmd6 = "systemctl reload nginx"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd6

Write-Host "`n✅ Готово!`n" -ForegroundColor Green

