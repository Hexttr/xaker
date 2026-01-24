# Deploy frontend to server
# Usage: .\scripts\deploy-frontend.ps1

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Import server utilities
. "$scriptPath\server-utils.ps1"

$config = Get-ServerConfig

Write-Host "🚀 Deploying frontend to server..." -ForegroundColor Cyan

# Build frontend
Write-Host "📦 Building frontend..." -ForegroundColor Yellow
Push-Location "$projectRoot\frontend"
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Copy dist to server
$localDist = "$projectRoot\frontend\dist"
$remoteFrontend = $config.SERVER_FRONTEND_DIR

Write-Host "📤 Copying dist to server..." -ForegroundColor Yellow
Copy-ToServer -LocalPath $localDist -RemotePath "$remoteFrontend\dist" -Config $config

Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
Write-Host "🌐 Frontend should be accessible via Nginx" -ForegroundColor Cyan

