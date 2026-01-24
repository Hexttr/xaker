# Deployment script with proper host key handling
$plink = "C:\Program Files\PuTTY\plink.exe"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "Starting deployment..." -ForegroundColor Cyan

# Accept host key first
Write-Host "Accepting host key..." -ForegroundColor Gray
$null = echo y | & $plink -ssh -P 22 -pw $password $server "exit" 2>&1

# Deploy commands
$commands = @(
    "cd /root/xaker && git pull origin prod",
    "cd /root/xaker/backend && npm run build", 
    "pm2 restart xaker-backend",
    "pm2 status xaker-backend"
)

foreach ($cmd in $commands) {
    Write-Host "`nExecuting: $cmd" -ForegroundColor Yellow
    $output = echo y | & $plink -ssh -P 22 -pw $password $server $cmd 2>&1
    Write-Host $output
}

Write-Host "`nDeployment complete!" -ForegroundColor Green

