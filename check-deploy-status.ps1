# Проверка статуса деплоя
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔍 Проверка статуса деплоя...`n" -ForegroundColor Cyan

# 1. Проверяем коммит
Write-Host "1. Коммит на сервере:" -ForegroundColor Yellow
$cmd1 = "cd /opt/xaker/frontend && git log --oneline -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

# 2. Проверяем собранный файл
Write-Host "`n2. Собранный файл в dist:" -ForegroundColor Yellow
$cmd2 = "cd /opt/xaker/frontend/dist/assets && ls -lt index-*.js | head -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

# 3. Проверяем index.html
Write-Host "`n3. index.html ссылается на:" -ForegroundColor Yellow
$cmd3 = "cd /opt/xaker/frontend/dist && grep 'index-.*\.js' index.html"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd3

# 4. Проверяем, скопирован ли файл в /opt/xaker/frontend/dist
Write-Host "`n4. Файлы в /opt/xaker/frontend/dist/assets:" -ForegroundColor Yellow
$cmd4 = "cd /opt/xaker/frontend/dist/assets && ls -lt index-*.js | head -3"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd4

# 5. Проверяем наличие __DEBUG__ в файле
Write-Host "`n5. Проверка наличия __DEBUG__:" -ForegroundColor Yellow
$cmd5 = "cd /opt/xaker/frontend/dist/assets && grep -l '__DEBUG__' index-*.js 2>/dev/null | head -1"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd5
if ($result) {
    Write-Host "✅ Найден: $result" -ForegroundColor Green
} else {
    Write-Host "❌ Не найден!" -ForegroundColor Red
}

# 6. Проверяем, что файлы скопированы в правильное место для Nginx
Write-Host "`n6. Проверка файлов для Nginx:" -ForegroundColor Yellow
$cmd6 = "ls -lt /opt/xaker/frontend/dist/assets/index-*.js 2>/dev/null | head -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd6

Write-Host ""

