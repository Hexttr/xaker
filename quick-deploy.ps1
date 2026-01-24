# Быстрый деплой через Git (рекомендуемый способ)
# Использование: .\quick-deploy.ps1 -Type "landing" или "backend"

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("landing", "backend", "all")]
    [string]$Type
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Быстрый деплой ($Type)..." -ForegroundColor Cyan

# Переходим в рабочую директорию
cd C:\Xaker

# Коммитим все изменения
Write-Host "📦 Коммит изменений..." -ForegroundColor Yellow
git add -A
$commitMessage = "Update: $Type changes - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git commit -m $commitMessage 2>&1 | Out-Null
git push origin prod

if ($Type -eq "landing" -or $Type -eq "all") {
    Write-Host "🔄 Деплой лендинга..." -ForegroundColor Yellow
    ssh root@pentest.red "cd /opt/xaker/landing && git pull origin prod && npm run build && cp -r dist/* /var/www/pentest.red/landing/ && echo '✅ Лендинг обновлен'"
}

if ($Type -eq "backend" -or $Type -eq "all") {
    Write-Host "🔄 Деплой бэкенда..." -ForegroundColor Yellow
    ssh root@pentest.red "cd /opt/xaker/backend && git pull origin prod && npm run build && pm2 restart xaker-backend && sleep 2 && echo '✅ Бэкенд обновлен'"
}

Write-Host "✅ Деплой завершен!" -ForegroundColor Green

