# Full automatic deployment script
# Uses PuTTY plink with proper output handling

$ErrorActionPreference = "Continue"
$plink = "C:\Program Files\PuTTY\plink.exe"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$port = 22

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AUTOMATIC DEPLOYMENT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Server: $server" -ForegroundColor Yellow
Write-Host ""

# Function to execute command
function Execute-Command {
    param($Command, $Description)
    
    Write-Host "[$Description]" -ForegroundColor Yellow
    Write-Host ("-" * 60) -ForegroundColor Gray
    Write-Host "Command: $Command" -ForegroundColor Gray
    Write-Host ""
    
    $process = Start-Process -FilePath $plink -ArgumentList @(
        "-ssh",
        "-P", $port,
        "-pw", $password,
        $server,
        $Command
    ) -NoNewWindow -Wait -PassThru -RedirectStandardOutput "deploy_output.txt" -RedirectStandardError "deploy_error.txt"
    
    if (Test-Path "deploy_output.txt") {
        $output = Get-Content "deploy_output.txt" -Raw
        if ($output) {
            Write-Host $output
        }
        Remove-Item "deploy_output.txt" -ErrorAction SilentlyContinue
    }
    
    if (Test-Path "deploy_error.txt") {
        $error = Get-Content "deploy_error.txt" -Raw
        if ($error -and $error -notmatch "The server's host key") {
            Write-Host "STDERR: $error" -ForegroundColor Red
        }
        Remove-Item "deploy_error.txt" -ErrorAction SilentlyContinue
    }
    
    Write-Host ""
    return $process.ExitCode
}

# Accept host key first (silent)
Write-Host "[0/4] Accepting host key..." -ForegroundColor Gray
echo y | & $plink -ssh -P $port -pw $password $server "echo 'Connected'" | Out-Null

# Step 1: Pull changes
$exit1 = Execute-Command "cd /root/xaker && git pull origin prod" "1/4 Pulling changes from git"
if ($exit1 -ne 0) {
    Write-Host "[WARNING] Git pull returned exit code $exit1" -ForegroundColor Yellow
}

# Step 2: Build backend
$exit2 = Execute-Command "cd /root/xaker/backend && npm run build" "2/4 Building backend"
if ($exit2 -ne 0) {
    Write-Host "[ERROR] Build failed with exit code $exit2" -ForegroundColor Red
    exit 1
}

# Step 3: Restart backend
$exit3 = Execute-Command "pm2 restart xaker-backend || (cd /root/xaker/backend && pm2 start npm --name xaker-backend -- run start)" "3/4 Restarting backend"
if ($exit3 -ne 0) {
    Write-Host "[WARNING] PM2 restart returned exit code $exit3" -ForegroundColor Yellow
}

# Step 4: Check status
$exit4 = Execute-Command "pm2 status xaker-backend" "4/4 Checking status"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

