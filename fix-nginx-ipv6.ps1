# Исправление Nginx - использование IPv4 вместо IPv6
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔧 Исправление Nginx (IPv4 вместо IPv6)...`n" -ForegroundColor Cyan

# Исправляем proxy_pass на 127.0.0.1
Write-Host "1. Исправляем proxy_pass на 127.0.0.1..." -ForegroundColor Yellow
$cmd1 = "sudo sed -i 's|proxy_pass http://localhost:3000|proxy_pass http://127.0.0.1:3000|g' /etc/nginx/sites-available/pentest.red"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

Write-Host "2. Проверяем синтаксис..." -ForegroundColor Yellow
$cmd2 = "sudo nginx -t"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

Write-Host "3. Перезагружаем Nginx..." -ForegroundColor Yellow
$cmd3 = "sudo systemctl reload nginx"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd3

Write-Host "`n✅ Nginx исправлен!`n" -ForegroundColor Green

