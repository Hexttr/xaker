# Скрипт для проверки и сборки Shannon
$ErrorActionPreference = "Stop"

Write-Host "🔍 Проверяю сборку Shannon..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$shannonPath = "/opt/xaker/shannon"

Write-Host "`n📁 Проверяю структуру..." -ForegroundColor Yellow
$checkCommand = "cd $shannonPath && echo '=== Структура ===' && ls -la | head -20 && echo '=== dist ===' && ls -la dist 2>/dev/null || echo 'dist не существует' && echo '=== src ===' && ls -la src | head -10"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $checkCommand
Write-Host $result

Write-Host "`n🔨 Собираю TypeScript..." -ForegroundColor Yellow
$buildCommand = "cd $shannonPath && npm run build"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $buildCommand
Write-Host $result

Write-Host "`n✅ Проверяю результат..." -ForegroundColor Yellow
$verifyCommand = "cd $shannonPath && if [ -d dist ]; then echo '✅ dist существует'; ls -la dist | head -10; if [ -f dist/shannon.js ]; then echo '✅ shannon.js найден!'; else echo '❌ shannon.js не найден'; find dist -name '*.js' | head -5; fi; else echo '❌ dist не существует'; fi"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $verifyCommand
Write-Host $result

