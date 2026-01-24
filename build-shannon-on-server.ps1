# Скрипт для сборки Shannon на сервере
$ErrorActionPreference = "Stop"

Write-Host "🔨 Собираю Shannon на сервере..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$shannonPath = "/opt/xaker/shannon"

Write-Host "`n📁 Проверяю наличие src/shannon.ts..." -ForegroundColor Yellow
$checkCommand = "cd $shannonPath && if [ -f src/shannon.ts ]; then echo '✅ shannon.ts найден'; else echo '❌ shannon.ts не найден'; find src -name '*.ts' | head -5; fi"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $checkCommand
Write-Host $result

Write-Host "`n🔨 Собираю TypeScript..." -ForegroundColor Yellow
$buildCommand = "cd $shannonPath && npm run build 2>&1"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $buildCommand
Write-Host $result

Write-Host "`n✅ Проверяю результат..." -ForegroundColor Yellow
$verifyCommand = "cd $shannonPath && if [ -f dist/shannon.js ]; then echo '✅ shannon.js создан!'; ls -lh dist/shannon.js; else echo '❌ shannon.js не найден после сборки'; ls -la dist/ | head -10; fi"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $verifyCommand
Write-Host $result -ForegroundColor $(if ($result -match "создан") { "Green" } else { "Red" })

Write-Host "`n✅ Сборка завершена!`n" -ForegroundColor Green

