# Скрипт для деплоя landing page на сервер
# Использование: .\deploy-landing.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Начинаем деплой landing page..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$serverLandingDir = "/var/www/pentest.red/landing"
$localLandingDir = "landing"

# Проверяем, что мы в правильной директории
if (-not (Test-Path $localLandingDir)) {
    Write-Host "❌ Ошибка: директория $localLandingDir не найдена" -ForegroundColor Red
    exit 1
}

# Собираем landing page
Write-Host "📦 Собираем landing page..." -ForegroundColor Yellow
Push-Location $localLandingDir
try {
    npm install --silent
    npm run build
    
    if (-not (Test-Path "dist")) {
        Write-Host "❌ Ошибка: сборка не создала директорию dist" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Сборка завершена" -ForegroundColor Green
} finally {
    Pop-Location
}

# Создаем временный архив
Write-Host "📦 Создаем архив..." -ForegroundColor Yellow
$tempArchive = [System.IO.Path]::GetTempFileName() + ".tar.gz"
$distPath = Join-Path $localLandingDir "dist"

# Используем tar для создания архива (Windows 10+)
$tarCommand = "tar -czf `"$tempArchive`" -C `"$distPath`" ."
Invoke-Expression $tarCommand

if (-not (Test-Path $tempArchive)) {
    Write-Host "❌ Ошибка: не удалось создать архив" -ForegroundColor Red
    exit 1
}

# Копируем на сервер
Write-Host "📤 Копируем на сервер..." -ForegroundColor Yellow
$pscp = "C:\Program Files\PuTTY\pscp.exe"
$archiveName = Split-Path $tempArchive -Leaf

# Создаем директорию на сервере
& $plink -ssh $server -pw $password -hostkey $hostkey "mkdir -p $serverLandingDir"

# Копируем архив
& $pscp -pw $password -hostkey $hostkey $tempArchive "$server`:/tmp/$archiveName"

# Распаковываем на сервере
Write-Host "📥 Распаковываем на сервере..." -ForegroundColor Yellow
$unpackCommand = "cd $serverLandingDir && rm -rf * && tar -xzf /tmp/$archiveName && rm /tmp/$archiveName && chown -R www-data:www-data $serverLandingDir && chmod -R 755 $serverLandingDir"

& $plink -ssh $server -pw $password -hostkey $hostkey $unpackCommand

# Удаляем локальный архив
Remove-Item $tempArchive -Force

Write-Host "✅ Landing page успешно задеплоен!" -ForegroundColor Green
Write-Host "🌐 Проверьте: https://pentest.red/" -ForegroundColor Cyan

