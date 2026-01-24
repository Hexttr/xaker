# Deploy to server script
# Uses PuTTY plink for SSH access

$plink = "C:\Program Files\PuTTY\plink.exe"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$port = 22

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DEPLOYING TO SERVER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Step 1: Pull latest changes
Write-Host "`n[1/4] Pulling latest changes from git..." -ForegroundColor Yellow
& $plink -ssh -P $port -pw $password $server "cd /root/xaker && git pull origin prod"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Git pull failed!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Git pull successful" -ForegroundColor Green

# Step 2: Build backend
Write-Host "`n[2/4] Building backend..." -ForegroundColor Yellow
& $plink -ssh -P $port -pw $password $server "cd /root/xaker/backend && npm run build"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Build successful" -ForegroundColor Green

# Step 3: Restart PM2
Write-Host "`n[3/4] Restarting backend..." -ForegroundColor Yellow
& $plink -ssh -P $port -pw $password $server "pm2 restart xaker-backend"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] PM2 restart failed, trying to start..." -ForegroundColor Yellow
    & $plink -ssh -P $port -pw $password $server "cd /root/xaker/backend && pm2 start npm --name xaker-backend -- run start"
}
Write-Host "[OK] Backend restarted" -ForegroundColor Green

# Step 4: Check status
Write-Host "`n[4/4] Checking backend status..." -ForegroundColor Yellow
& $plink -ssh -P $port -pw $password $server "pm2 status xaker-backend"
Write-Host "`n[OK] Deployment complete!" -ForegroundColor Green

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

