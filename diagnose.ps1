# Скрипт диагностики для проверки состояния приложения на сервере
# Использование: .\diagnose.ps1

$ErrorActionPreference = "Stop"

Write-Host "🔍 Начинаем диагностику..." -ForegroundColor Cyan

$plink = "C:\Program Files\PuTTY\plink.exe"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"

function Run-ServerCommand {
    param([string]$Command)
    $output = & $plink -ssh $server -pw $password -hostkey $hostkey $Command 2>&1
    return $output
}

Write-Host "`n📁 1. Проверка файлов на сервере..." -ForegroundColor Yellow
$serverFiles = Run-ServerCommand "cd /opt/xaker/frontend && find src/components -name '*.tsx' -o -name '*.ts' | sort"
Write-Host $serverFiles

Write-Host "`n📦 2. Проверка собранных файлов..." -ForegroundColor Yellow
$distFiles = Run-ServerCommand "ls -lh /opt/xaker/frontend/dist/assets/*.{js,css} 2>/dev/null | tail -5"
Write-Host $distFiles

Write-Host "`n🔍 3. Проверка Layout.tsx на сервере..." -ForegroundColor Yellow
$layoutServer = Run-ServerCommand "cat /opt/xaker/frontend/src/components/Layout.tsx | grep -A 3 'Grid Background'"
Write-Host $layoutServer

Write-Host "`n🔍 4. Проверка Logo.tsx на сервере..." -ForegroundColor Yellow
$logoServer = Run-ServerCommand "test -f /opt/xaker/frontend/src/components/Logo.tsx && head -20 /opt/xaker/frontend/src/components/Logo.tsx || echo 'Logo.tsx НЕ НАЙДЕН'"
Write-Host $logoServer

Write-Host "`n🔍 5. Проверка Sidebar.tsx на сервере..." -ForegroundColor Yellow
$sidebarServer = Run-ServerCommand "cat /opt/xaker/frontend/src/components/Sidebar.tsx | grep -A 2 'import Logo'"
Write-Host $sidebarServer

Write-Host "`n📄 6. Проверка index.html на сервере..." -ForegroundColor Yellow
$indexHtml = Run-ServerCommand "cat /opt/xaker/frontend/dist/index.html | grep -E '(index-|favicon)'"
Write-Host $indexHtml

Write-Host "`n🔍 7. Проверка наличия компонентов в собранном JS..." -ForegroundColor Yellow
$jsFile = Run-ServerCommand "ls /opt/xaker/frontend/dist/assets/index-*.js | head -1"
$jsFile = $jsFile.Trim()
Write-Host "Проверяем файл: $jsFile"

$hasLayout = Run-ServerCommand "grep -c 'min-h-screen bg-black' $jsFile"
$hasGrid = Run-ServerCommand "grep -c 'absolute inset-0' $jsFile"
$hasLogo = Run-ServerCommand "grep -c 'Pentest.*red' $jsFile"
$hasSVG = Run-ServerCommand "grep -c 'viewBox.*32 32' $jsFile"

Write-Host "  Layout (min-h-screen bg-black): $hasLayout"
Write-Host "  Grid (absolute inset-0): $hasGrid"
Write-Host "  Logo текст (Pentest.red): $hasLogo"
Write-Host "  Logo SVG (viewBox 32 32): $hasSVG"

Write-Host "`n🔍 8. Проверка CSS..." -ForegroundColor Yellow
$cssFile = Run-ServerCommand "ls /opt/xaker/frontend/dist/assets/index-*.css | head -1"
$cssFile = $cssFile.Trim()
$hasFonts = Run-ServerCommand "grep -c 'Inter.*JetBrains' $cssFile"
$hasGridCSS = Run-ServerCommand "grep -c 'bg-grid-dark' $cssFile"
Write-Host "  Шрифты (Inter, JetBrains): $hasFonts"
Write-Host "  Grid CSS (bg-grid-dark): $hasGridCSS"

Write-Host "`n🔍 9. Проверка локальных файлов..." -ForegroundColor Yellow
$localLayout = Get-Content "C:\Xakerprod\frontend\src\components\Layout.tsx" -Raw
$localLogo = Test-Path "C:\Xakerprod\frontend\src\components\Logo.tsx"
Write-Host "  Layout.tsx локально: $($localLayout.Length) байт"
Write-Host "  Logo.tsx локально: $localLogo"

Write-Host "`n🔍 10. Сравнение Layout.tsx..." -ForegroundColor Yellow
$serverLayout = Run-ServerCommand "cat /opt/xaker/frontend/src/components/Layout.tsx"
$localLayoutContent = Get-Content "C:\Xakerprod\frontend\src\components\Layout.tsx" -Raw
if ($serverLayout -eq $localLayoutContent) {
    Write-Host "  ✅ Layout.tsx совпадает" -ForegroundColor Green
} else {
    Write-Host "  ❌ Layout.tsx РАЗЛИЧАЕТСЯ!" -ForegroundColor Red
    Write-Host "  Нужно обновить на сервере"
}

Write-Host "`n✅ Диагностика завершена!" -ForegroundColor Green

