# Setup server configuration
# Usage: .\scripts\setup-server-config.ps1

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
$configFile = Join-Path $projectRoot ".server-config.local"
$exampleFile = Join-Path $projectRoot ".server-config.local.example"

if (Test-Path $configFile) {
    Write-Host "⚠️  Configuration file already exists: $configFile" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host "📝 Setting up server configuration..." -ForegroundColor Cyan

# Copy example file
Copy-Item $exampleFile $configFile

Write-Host "✅ Configuration file created: $configFile" -ForegroundColor Green
Write-Host ""
Write-Host "Please edit the file and fill in your server credentials:" -ForegroundColor Yellow
Write-Host "  notepad $configFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or use your favorite editor to edit:" -ForegroundColor Yellow
Write-Host "  $configFile" -ForegroundColor Cyan

