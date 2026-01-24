# Скрипт для исправления пути к Shannon
$ErrorActionPreference = "Stop"

Write-Host "🔧 Исправляю путь к Shannon..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$shannonPath = "/opt/xaker/shannon"

Write-Host "`n🔍 Проверяю наличие shannon.js..." -ForegroundColor Yellow
$checkCommand = "cd $shannonPath && if [ -f dist/shannon.js ]; then echo '✅ shannon.js существует'; ls -lh dist/shannon.js; else echo '❌ shannon.js не найден'; echo 'Проверяю исходный файл...'; if [ -f src/shannon.ts ]; then echo '✅ src/shannon.ts существует'; echo 'Пересобираю...'; npm run build 2>&1; if [ -f dist/shannon.js ]; then echo '✅ shannon.js создан!'; else echo '❌ Ошибка сборки'; fi; else echo '❌ src/shannon.ts не найден'; fi; fi"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $checkCommand
Write-Host $result

Write-Host "`n✅ Проверка завершена!`n" -ForegroundColor Green

