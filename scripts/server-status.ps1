# Check server status
# Usage: .\scripts\server-status.ps1

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Import server utilities
. "$scriptPath\server-utils.ps1"

$config = Get-ServerConfig

Write-Host "📊 Checking server status..." -ForegroundColor Cyan

# Check PM2 processes
Write-Host "`n🔄 PM2 Processes:" -ForegroundColor Yellow
$pm2Status = Invoke-ServerCommand -Command "pm2 list" -Config $config
Write-Host $pm2Status

# Check disk space
Write-Host "`n💾 Disk Space:" -ForegroundColor Yellow
$diskSpace = Invoke-ServerCommand -Command "df -h" -Config $config
Write-Host $diskSpace

# Check backend service
Write-Host "`n🌐 Backend Health:" -ForegroundColor Yellow
$healthCheck = Invoke-ServerCommand -Command "curl -s http://localhost:3000/api/health || echo 'Backend not responding'" -Config $config
Write-Host $healthCheck

# Check Nginx
Write-Host "`n🔧 Nginx Status:" -ForegroundColor Yellow
$nginxStatus = Invoke-ServerCommand -Command "systemctl status nginx --no-pager | head -10" -Config $config
Write-Host $nginxStatus

Write-Host "`n✅ Status check complete!" -ForegroundColor Green

