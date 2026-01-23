# Финальное исправление - проверка и пересборка
$plink = "C:\Program Files\PuTTY\plink.exe"
$pscp = "C:\Program Files\PuTTY\pscp.exe"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"

Write-Host "🔧 Финальное исправление..." -ForegroundColor Cyan

# 1. Убеждаемся, что все файлы на месте
Write-Host "`n1. Проверка файлов..." -ForegroundColor Yellow
$files = @(
    "C:\Xakerprod\frontend\src\components\Layout.tsx",
    "C:\Xakerprod\frontend\src\components\Logo.tsx",
    "C:\Xakerprod\frontend\src\components\Sidebar.tsx",
    "C:\Xakerprod\frontend\src\index.css"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✅ $(Split-Path $file -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $(Split-Path $file -Leaf) НЕ НАЙДЕН!" -ForegroundColor Red
        exit 1
    }
}

# 2. Копируем файлы на сервер
Write-Host "`n2. Копирование файлов на сервер..." -ForegroundColor Yellow
& $pscp -pw $password -hostkey $hostkey "C:\Xakerprod\frontend\src\components\Layout.tsx" "$server`:/opt/xaker/frontend/src/components/Layout.tsx"
& $pscp -pw $password -hostkey $hostkey "C:\Xakerprod\frontend\src\components\Logo.tsx" "$server`:/opt/xaker/frontend/src/components/Logo.tsx"
& $pscp -pw $password -hostkey $hostkey "C:\Xakerprod\frontend\src\components\Sidebar.tsx" "$server`:/opt/xaker/frontend/src/components/Sidebar.tsx"
& $pscp -pw $password -hostkey $hostkey "C:\Xakerprod\frontend\src\index.css" "$server`:/opt/xaker/frontend/src/index.css"

# 3. Полная очистка и пересборка
Write-Host "`n3. Полная очистка и пересборка..." -ForegroundColor Yellow
$buildOutput = & $plink -ssh $server -pw $password -hostkey $hostkey @"
cd /opt/xaker/frontend
rm -rf dist node_modules/.vite .vite
NODE_ENV=production npm run build 2>&1 | tail -10
"@
Write-Host $buildOutput

# 4. Проверка результата
Write-Host "`n4. Проверка результата..." -ForegroundColor Yellow
$jsFile = & $plink -ssh $server -pw $password -hostkey $hostkey "ls /opt/xaker/frontend/dist/assets/index-*.js | head -1"
$jsFile = $jsFile.Trim()

$checks = @{
    "Layout (min-h-screen)" = "min-h-screen bg-black"
    "Grid div (absolute)" = "absolute inset-0"
    "Grid class (bg-grid-dark)" = "bg-grid-dark"
    "Logo text" = "Pentest.*red"
    "SVG viewBox" = "viewBox.*32 32"
}

foreach ($check in $checks.GetEnumerator()) {
    $result = & $plink -ssh $server -pw $password -hostkey $hostkey "grep -c '$($check.Value)' $jsFile 2>/dev/null || echo '0'"
    $result = $result.Trim()
    if ([int]$result -gt 0) {
        Write-Host "  ✅ $($check.Key): $result" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($check.Key): НЕ НАЙДЕН" -ForegroundColor Red
    }
}

# 5. Проверка CSS
Write-Host "`n5. Проверка CSS..." -ForegroundColor Yellow
$cssFile = & $plink -ssh $server -pw $password -hostkey $hostkey "ls /opt/xaker/frontend/dist/assets/index-*.css | head -1"
$cssFile = $cssFile.Trim()

$cssChecks = @{
    "bg-grid-dark" = "bg-grid-dark"
    "Inter font" = "Inter"
    "JetBrains font" = "JetBrains"
}

foreach ($check in $cssChecks.GetEnumerator()) {
    $result = & $plink -ssh $server -pw $password -hostkey $hostkey "grep -c '$($check.Value)' $cssFile 2>/dev/null || echo '0'"
    $result = $result.Trim()
    if ([int]$result -gt 0) {
        Write-Host "  ✅ $($check.Key): $result" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($check.Key): НЕ НАЙДЕН" -ForegroundColor Red
    }
}

# 6. Перезагрузка Nginx
Write-Host "`n6. Перезагрузка Nginx..." -ForegroundColor Yellow
& $plink -ssh $server -pw $password -hostkey $hostkey "systemctl reload nginx"

Write-Host "`n✅ Готово! Откройте https://pentest.red/app/ и проверьте:" -ForegroundColor Green
Write-Host "  - Логотип должен быть виден" -ForegroundColor Cyan
Write-Host "  - Сетчатый фон должен быть виден" -ForegroundColor Cyan
Write-Host "  - В консоли: document.querySelector('[data-testid=\"grid-background\"]')" -ForegroundColor Cyan

