# Диагностика проблем с логином и /app
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔍 Диагностика проблем...`n" -ForegroundColor Cyan

# 1. Проверяем backend
Write-Host "1. Проверка backend:" -ForegroundColor Yellow
$cmd1 = "pm2 list | grep xaker"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

# 2. Проверяем API напрямую
Write-Host "`n2. Проверка API напрямую (localhost:3000):" -ForegroundColor Yellow
$cmd2 = "curl -s http://localhost:3000/api/health"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

# 3. Проверяем API через Nginx
Write-Host "`n3. Проверка API через Nginx (https://pentest.red/api/health):" -ForegroundColor Yellow
$cmd3 = "curl -s https://pentest.red/api/health"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd3

# 4. Проверяем коммит на сервере
Write-Host "`n4. Последний коммит на сервере (frontend):" -ForegroundColor Yellow
$cmd4 = "cd /opt/xaker/frontend && git log --oneline -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd4

# 5. Проверяем последний собранный файл
Write-Host "`n5. Последний собранный файл:" -ForegroundColor Yellow
$cmd5 = "cd /opt/xaker/frontend/dist/assets && ls -lt index-*.js | head -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd5

# 6. Проверяем логи Nginx
Write-Host "`n6. Последние ошибки Nginx:" -ForegroundColor Yellow
$cmd6 = "tail -10 /var/log/nginx/pentest.red.error.log 2>/dev/null || echo 'Нет ошибок'"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd6

# 7. Проверяем, что /api проксируется правильно
Write-Host "`n7. Тест проксирования /api:" -ForegroundColor Yellow
$cmd7 = "curl -s -I https://pentest.red/api/health | head -5"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd7

Write-Host ""

