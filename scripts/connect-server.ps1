# Connect to server via SSH
# Usage: .\scripts\connect-server.ps1

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Import server utilities
. "$scriptPath\server-utils.ps1"

$config = Get-ServerConfig

$host = $config.SERVER_HOST
$user = $config.SERVER_USER
$port = if ($config.SERVER_PORT) { $config.SERVER_PORT } else { 22 }

Write-Host "🔌 Connecting to $user@$host`:$port..." -ForegroundColor Cyan

# Try SSH key first
if ($config.SSH_KEY_PATH -and (Test-Path $config.SSH_KEY_PATH)) {
    ssh -i $config.SSH_KEY_PATH -p $port "$user@$host"
} elseif (Get-Command ssh -ErrorAction SilentlyContinue) {
    ssh -p $port "$user@$host"
} else {
    Write-Host "SSH not found. Please install OpenSSH or configure SSH_KEY_PATH" -ForegroundColor Red
    Write-Host "Or use PuTTY/plink.exe" -ForegroundColor Yellow
}

