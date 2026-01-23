# Глубокая диагностика сборки
$plink = "C:\Program Files\PuTTY\plink.exe"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"

Write-Host "🔍 Глубокая диагностика..." -ForegroundColor Cyan

# Проверяем, что Layout рендерится
Write-Host "`n1. Проверка Layout в JS..." -ForegroundColor Yellow
$jsFile = & $plink -ssh $server -pw $password -hostkey $hostkey "ls /opt/xaker/frontend/dist/assets/index-*.js | head -1"
$jsFile = $jsFile.Trim()

$layoutCheck = & $plink -ssh $server -pw $password -hostkey $hostkey "grep -o 'Layout.*rendering' $jsFile | head -1"
Write-Host "  Layout логи: $layoutCheck"

# Проверяем inline стили
Write-Host "`n2. Проверка inline стилей..." -ForegroundColor Yellow
$styleCheck = & $plink -ssh $server -pw $password -hostkey $hostkey "grep -o 'backgroundImage.*linear-gradient' $jsFile | head -1"
Write-Host "  backgroundImage: $($styleCheck.Substring(0, [Math]::Min(80, $styleCheck.Length)))..."

# Проверяем SVG path
Write-Host "`n3. Проверка SVG path..." -ForegroundColor Yellow
$svgPath = & $plink -ssh $server -pw $password -hostkey $hostkey "grep -o 'M16 2L4 7V15' $jsFile | head -1"
Write-Host "  SVG path: $svgPath"

# Проверяем CSS классы
Write-Host "`n4. Проверка CSS классов..." -ForegroundColor Yellow
$cssFile = & $plink -ssh $server -pw $password -hostkey $hostkey "ls /opt/xaker/frontend/dist/assets/index-*.css | head -1"
$cssFile = $cssFile.Trim()

$bgGridCheck = & $plink -ssh $server -pw $password -hostkey $hostkey "grep -c 'bg-grid-dark' $cssFile"
Write-Host "  bg-grid-dark в CSS: $bgGridCheck"

# Проверяем исходники
Write-Host "`n5. Проверка исходников..." -ForegroundColor Yellow
$layoutSource = & $plink -ssh $server -pw $password -hostkey $hostkey "cat /opt/xaker/frontend/src/components/Layout.tsx | grep -A 5 'Grid Background'"
Write-Host $layoutSource

Write-Host "`n✅ Диагностика завершена" -ForegroundColor Green

