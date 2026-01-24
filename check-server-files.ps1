# Проверка файлов на сервере
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔍 Проверка файлов на сервере...`n" -ForegroundColor Cyan

# Проверяем последний коммит на сервере
Write-Host "📋 Последний коммит на сервере:" -ForegroundColor Yellow
$cmd1 = "cd /opt/xaker/frontend && git log --oneline -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

# Проверяем файлы в dist/assets
Write-Host "`n📦 Файлы в dist/assets:" -ForegroundColor Yellow
$cmd2 = "cd /opt/xaker/frontend/dist/assets && ls -lt index-*.js | head -1"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

# Проверяем содержимое index.html
Write-Host "`n📄 index.html ссылается на:" -ForegroundColor Yellow
$cmd3 = "cd /opt/xaker/frontend/dist && grep 'index-.*\.js' index.html"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd3

# Проверяем наличие __DEBUG__ в JS файле
Write-Host "`n🔍 Проверка наличия __DEBUG__ в JS:" -ForegroundColor Yellow
$cmd4 = "cd /opt/xaker/frontend/dist/assets && grep -l '__DEBUG__' index-*.js 2>/dev/null | head -1"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd4
if ($result) {
    Write-Host "✅ Найден файл с __DEBUG__: $result" -ForegroundColor Green
} else {
    Write-Host "❌ Файлы с __DEBUG__ не найдены!" -ForegroundColor Red
}

Write-Host ""

