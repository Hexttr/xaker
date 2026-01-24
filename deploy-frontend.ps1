# Автоматизированный скрипт для деплоя frontend
# Использование: .\deploy-frontend.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Начинаем деплой frontend..." -ForegroundColor Cyan

# Переменные
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$serverDir = "/opt/xaker"
$frontendDir = "frontend"

# Проверяем, что мы в правильной директории
if (-not (Test-Path $frontendDir)) {
    Write-Host "❌ Ошибка: директория $frontendDir не найдена" -ForegroundColor Red
    exit 1
}

# 1. Коммитим и пушим изменения в Git
Write-Host "📝 Коммитим изменения в Git..." -ForegroundColor Yellow
try {
    git add -A
    $hasChanges = git diff --cached --quiet
    if (-not $hasChanges) {
        git commit -m "Deploy: Frontend updates $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git push origin prod
        Write-Host "✅ Изменения запушены в Git" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Нет изменений для коммита" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Ошибка при работе с Git: $_" -ForegroundColor Yellow
}

# 2. Обновляем код на сервере
Write-Host "📥 Обновляем код на сервере..." -ForegroundColor Yellow
$updateCommand = "cd $serverDir && git stash && git pull origin prod"
& $plink -ssh $server -pw $password -hostkey $hostkey $updateCommand

# 3. Собираем frontend на сервере
Write-Host "🔨 Собираем frontend на сервере..." -ForegroundColor Yellow
$buildCommand = "cd $serverDir/$frontendDir && rm -rf node_modules/.vite dist && npm run build"
& $plink -ssh $server -pw $password -hostkey $hostkey $buildCommand

# 4. Копируем public файлы в dist
Write-Host "📦 Копируем public файлы..." -ForegroundColor Yellow
$copyCommand = "cd $serverDir/$frontendDir && cp -r public/* dist/ 2>/dev/null || true"
& $plink -ssh $server -pw $password -hostkey $hostkey $copyCommand

# 5. Перезагружаем Nginx
Write-Host "🔄 Перезагружаем Nginx..." -ForegroundColor Yellow
& $plink -ssh $server -pw $password -hostkey $hostkey "systemctl reload nginx"

# 6. Проверяем результат
Write-Host "✅ Проверяем результат..." -ForegroundColor Yellow
$checkCommand = "cd $serverDir/$frontendDir/dist && ls -lh assets/index-*.js | tail -1 && cat index.html | grep 'index-.*\.js'"
& $plink -ssh $server -pw $password -hostkey $hostkey $checkCommand

Write-Host "✅ Frontend успешно задеплоен!" -ForegroundColor Green
Write-Host "🌐 Проверьте: https://pentest.red/app/" -ForegroundColor Cyan

