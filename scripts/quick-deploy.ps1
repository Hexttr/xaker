# Quick deploy script with output logging
$plink = "C:\Program Files\PuTTY\plink.exe"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "Deploying..." -ForegroundColor Cyan

# Accept host key and pull
$cmd1 = "cd /root/xaker && git pull origin prod"
$output1 = echo y | & $plink -ssh -P 22 -pw $password $server $cmd1 2>&1
Write-Host "Git pull:" -ForegroundColor Yellow
Write-Host $output1

# Build
$cmd2 = "cd /root/xaker/backend && npm run build"
$output2 = echo y | & $plink -ssh -P 22 -pw $password $server $cmd2 2>&1
Write-Host "`nBuild:" -ForegroundColor Yellow
Write-Host $output2

# Restart
$cmd3 = "pm2 restart xaker-backend"
$output3 = echo y | & $plink -ssh -P 22 -pw $password $server $cmd3 2>&1
Write-Host "`nPM2 restart:" -ForegroundColor Yellow
Write-Host $output3

Write-Host "`nDone!" -ForegroundColor Green

