# Проверка деплоя
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔍 Проверка деплоя...`n" -ForegroundColor Cyan

# 1. Проверяем коммит на сервере
Write-Host "1. Последний коммит на сервере:" -ForegroundColor Yellow
$cmd1 = "cd /opt/xaker && git log --oneline -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

# 2. Проверяем файл на сервере
Write-Host "`n2. Последний собранный файл:" -ForegroundColor Yellow
$cmd2 = "cd /opt/xaker/frontend/dist/assets && ls -lt index-*.js | head -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

# 3. Проверяем наличие name="username" в собранном файле
Write-Host "`n3. Проверка наличия name='username' в JS:" -ForegroundColor Yellow
$cmd3 = "cd /opt/xaker/frontend/dist/assets && grep -o 'name=.*username' index-*.js 2>/dev/null | head -1"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd3
if ($result) {
    Write-Host "✅ Найдено: $result" -ForegroundColor Green
} else {
    Write-Host "❌ Не найдено!" -ForegroundColor Red
}

# 4. Проверяем index.html
Write-Host "`n4. index.html ссылается на:" -ForegroundColor Yellow
$cmd4 = "cd /opt/xaker/frontend/dist && grep 'index-.*\.js' index.html"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd4

Write-Host ""

