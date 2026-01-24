# Полное исправление всех проблем
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔧 Полное исправление проблем...`n" -ForegroundColor Cyan

# 1. Проверяем и исправляем Nginx конфигурацию для /api
Write-Host "1. Проверка Nginx конфигурации для /api..." -ForegroundColor Yellow
$cmd1 = "grep -A 5 'location /api' /etc/nginx/sites-available/pentest.red | head -6"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

# 2. Убеждаемся, что proxy_pass использует 127.0.0.1
Write-Host "`n2. Исправление proxy_pass на 127.0.0.1..." -ForegroundColor Yellow
$cmd2 = "sudo sed -i 's|proxy_pass http://localhost:3000|proxy_pass http://127.0.0.1:3000|g' /etc/nginx/sites-available/pentest.red && sudo sed -i 's|proxy_pass http://\[::1\]:3000|proxy_pass http://127.0.0.1:3000|g' /etc/nginx/sites-available/pentest.red"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

# 3. Пересобираем frontend с новым timestamp
Write-Host "`n3. Пересборка frontend..." -ForegroundColor Yellow
$cmd3 = "cd /opt/xaker/frontend && rm -rf node_modules/.vite dist && npm run build"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd3

# 4. Проверяем новый файл
Write-Host "`n4. Проверка нового файла..." -ForegroundColor Yellow
$cmd4 = "cd /opt/xaker/frontend/dist/assets && ls -lt index-*.js | head -1 && grep '__DEBUG__' index-*.js 2>/dev/null | head -1 | cut -d: -f1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd4

# 5. Перезагружаем Nginx
Write-Host "`n5. Перезагрузка Nginx..." -ForegroundColor Yellow
$cmd5 = "sudo nginx -t && sudo systemctl reload nginx"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd5

# 6. Проверяем API
Write-Host "`n6. Тест API..." -ForegroundColor Yellow
$cmd6 = "curl -s https://pentest.red/api/health"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd6

Write-Host "`n✅ Готово!`n" -ForegroundColor Green

