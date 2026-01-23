# Скрипт для автоматического исправления и деплоя
# Использование: .\fix-and-deploy.ps1

$ErrorActionPreference = "Stop"

Write-Host "🔧 Исправление и деплой..." -ForegroundColor Cyan

$plink = "C:\Program Files\PuTTY\plink.exe"
$pscp = "C:\Program Files\PuTTY\pscp.exe"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"

# 1. Обновляем код из Git
Write-Host "`n📥 1. Обновление кода на сервере..." -ForegroundColor Yellow
& $plink -ssh $server -pw $password -hostkey $hostkey "cd /opt/xaker && git pull origin prod"

# 2. Копируем критичные файлы напрямую (на случай если Git не синхронизирован)
Write-Host "`n📤 2. Копирование файлов..." -ForegroundColor Yellow

# Layout.tsx
& $pscp -pw $password -hostkey $hostkey "C:\Xakerprod\frontend\src\components\Layout.tsx" "$server`:/opt/xaker/frontend/src/components/Layout.tsx"

# Logo.tsx
& $pscp -pw $password -hostkey $hostkey "C:\Xakerprod\frontend\src\components\Logo.tsx" "$server`:/opt/xaker/frontend/src/components/Logo.tsx"

# Sidebar.tsx
& $pscp -pw $password -hostkey $hostkey "C:\Xakerprod\frontend\src\components\Sidebar.tsx" "$server`:/opt/xaker/frontend/src/components/Sidebar.tsx"

# index.css
& $pscp -pw $password -hostkey $hostkey "C:\Xakerprod\frontend\src\index.css" "$server`:/opt/xaker/frontend/src/index.css"

# tailwind.config.js
& $pscp -pw $password -hostkey $hostkey "C:\Xakerprod\frontend\tailwind.config.js" "$server`:/opt/xaker/frontend/tailwind.config.js"

# 3. Очистка кэша и пересборка
Write-Host "`n🔨 3. Очистка кэша и пересборка..." -ForegroundColor Yellow
& $plink -ssh $server -pw $password -hostkey $hostkey "cd /opt/xaker/frontend && rm -rf dist node_modules/.vite .vite && NODE_ENV=production npm run build 2>&1 | tail -5"

# 4. Проверка результата
Write-Host "`n✅ 4. Проверка результата..." -ForegroundColor Yellow
$jsFile = & $plink -ssh $server -pw $password -hostkey $hostkey "ls /opt/xaker/frontend/dist/assets/index-*.js | head -1"
$jsFile = $jsFile.Trim()

$hasGrid = & $plink -ssh $server -pw $password -hostkey $hostkey "grep -c 'absolute inset-0' $jsFile"
$hasSVG = & $plink -ssh $server -pw $password -hostkey $hostkey "grep -c 'viewBox.*32 32' $jsFile"
$hasLogoText = & $plink -ssh $server -pw $password -hostkey $hostkey "grep -c 'Pentest.*red' $jsFile"

Write-Host "  Grid (absolute inset-0): $hasGrid"
Write-Host "  Logo SVG (viewBox 32 32): $hasSVG"
Write-Host "  Logo текст (Pentest.red): $hasLogoText"

# 5. Перезагрузка Nginx
Write-Host "`n🔄 5. Перезагрузка Nginx..." -ForegroundColor Yellow
& $plink -ssh $server -pw $password -hostkey $hostkey "systemctl reload nginx"

Write-Host "`n✅ Готово! Проверьте https://pentest.red/app/" -ForegroundColor Green

