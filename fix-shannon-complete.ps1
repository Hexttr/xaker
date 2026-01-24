# Полная проверка и сборка Shannon на сервере
$ErrorActionPreference = "Stop"

Write-Host "🔧 Полная проверка и сборка Shannon..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$shannonPath = "/opt/xaker/shannon"

Write-Host "`n📥 Обновляю репозиторий Shannon..." -ForegroundColor Yellow
$updateCommand = "cd $shannonPath && git fetch origin && git pull origin main 2>&1 || git pull origin master 2>&1 || git pull 2>&1"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $updateCommand
Write-Host $result

Write-Host "`n🔍 Проверяю структуру..." -ForegroundColor Yellow
$checkCommand = "cd $shannonPath && echo '=== package.json ===' && cat package.json | grep -A 3 'main\|bin' && echo '=== src структура ===' && ls -la src/ | head -15 && echo '=== Ищу shannon.ts ===' && find . -name 'shannon.ts' -o -name 'index.ts' | grep -v node_modules | head -5"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $checkCommand
Write-Host $result

Write-Host "`n🔨 Собираю проект..." -ForegroundColor Yellow
$buildCommand = "cd $shannonPath && npm run build 2>&1"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $buildCommand
Write-Host $result

Write-Host "`n✅ Проверяю результат..." -ForegroundColor Yellow
$verifyCommand = "cd $shannonPath && if [ -f dist/shannon.js ]; then echo '✅✅✅ shannon.js СОЗДАН!'; ls -lh dist/shannon.js; else echo '❌ shannon.js не найден'; echo 'Содержимое dist:'; ls -la dist/ | head -15; fi"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $verifyCommand
Write-Host $result -ForegroundColor $(if ($result -match "СОЗДАН") { "Green" } else { "Red" })

Write-Host "`n✅ Проверка завершена!`n" -ForegroundColor Green

