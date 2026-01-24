# Проверка конфигурации Nginx
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔍 Проверка конфигурации Nginx...`n" -ForegroundColor Cyan

# Проверяем конфигурацию
Write-Host "1. Конфигурация Nginx:" -ForegroundColor Yellow
$cmd1 = "cat /etc/nginx/sites-available/pentest.red 2>/dev/null || cat /etc/nginx/conf.d/pentest.red.conf 2>/dev/null || echo 'Файл не найден'"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

Write-Host "`n2. Проверка синтаксиса Nginx:" -ForegroundColor Yellow
$cmd2 = "nginx -t"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

Write-Host "`n3. Проверка работы backend:" -ForegroundColor Yellow
$cmd3 = "curl -s http://localhost:3000/api/health || echo 'Backend не отвечает'"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd3

Write-Host ""

