# Скрипт для установки Shannon на сервере
$ErrorActionPreference = "Stop"

Write-Host "📦 Устанавливаю Shannon на сервере..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$shannonRepo = "https://github.com/KeygraphHQ/shannon.git"
$shannonPath = "/opt/xaker/shannon"

Write-Host "`n📥 Клонирую Shannon репозиторий..." -ForegroundColor Yellow
$cloneCommand = "cd /opt/xaker && if [ -d shannon ]; then echo 'Shannon уже существует, обновляю...'; cd shannon && git pull; else git clone $shannonRepo shannon; fi"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $cloneCommand
Write-Host $result -ForegroundColor Green

Write-Host "`n📦 Устанавливаю зависимости Shannon..." -ForegroundColor Yellow
$installCommand = "cd $shannonPath && npm install"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $installCommand
Write-Host "Зависимости установлены" -ForegroundColor Green

Write-Host "`n🔨 Собираю Shannon..." -ForegroundColor Yellow
$buildCommand = "cd $shannonPath && npm run build"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $buildCommand
Write-Host "Shannon собран" -ForegroundColor Green

Write-Host "`n🔨 Собираю mcp-server..." -ForegroundColor Yellow
$mcpBuildCommand = "cd $shannonPath/mcp-server && npm install && npm run build"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $mcpBuildCommand
Write-Host "mcp-server собран" -ForegroundColor Green

Write-Host "`n✅ Проверяю установку..." -ForegroundColor Yellow
$checkCommand = "if [ -f $shannonPath/dist/shannon.js ]; then echo '✅ Shannon установлен успешно!'; ls -lh $shannonPath/dist/shannon.js; else echo '❌ Ошибка: shannon.js не найден'; fi"
$result = & $plink -ssh $server -pw $password -hostkey $hostkey $checkCommand
Write-Host $result -ForegroundColor $(if ($result -match "успешно") { "Green" } else { "Red" })

Write-Host "`n✅ Shannon установлен!`n" -ForegroundColor Green

