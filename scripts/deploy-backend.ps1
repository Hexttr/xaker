# Deploy backend to server
# Usage: .\scripts\deploy-backend.ps1

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Import server utilities
. "$scriptPath\server-utils.ps1"

$config = Get-ServerConfig

Write-Host "🚀 Deploying backend to server..." -ForegroundColor Cyan

# Build backend
Write-Host "📦 Building backend..." -ForegroundColor Yellow
Push-Location "$projectRoot\backend"
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Copy files to server
$localBackend = "$projectRoot\backend"
$remoteBackend = $config.SERVER_BACKEND_DIR

Write-Host "📤 Copying files to server..." -ForegroundColor Yellow
Copy-ToServer -LocalPath "$localBackend\dist" -RemotePath "$remoteBackend\dist" -Config $config
Copy-ToServer -LocalPath "$localBackend\package.json" -RemotePath "$remoteBackend\package.json" -Config $config
Copy-ToServer -LocalPath "$localBackend\package-lock.json" -RemotePath "$remoteBackend\package-lock.json" -Config $config

# Copy .env if exists (optional)
if (Test-Path "$localBackend\.env") {
    Write-Host "📤 Copying .env file..." -ForegroundColor Yellow
    Copy-ToServer -LocalPath "$localBackend\.env" -RemotePath "$remoteBackend\.env" -Config $config
}

# Install dependencies and restart on server
Write-Host "🔄 Installing dependencies and restarting on server..." -ForegroundColor Yellow
$command = @"
cd $remoteBackend
npm install --production
pm2 restart xaker-backend || pm2 start npm --name xaker-backend -- run start
"@

$result = Invoke-ServerCommand -Command $command -Config $config
Write-Host $result

Write-Host "✅ Backend deployed successfully!" -ForegroundColor Green

