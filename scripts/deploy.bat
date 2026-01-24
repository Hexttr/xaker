@echo off
setlocal enabledelayedexpansion

set PLINK="C:\Program Files\PuTTY\plink.exe"
set SERVER=root@5.129.235.52
set PASSWORD=cY7^kCCA_6uQ5S
set PORT=22

echo ============================================================
echo AUTOMATIC DEPLOYMENT
echo ============================================================
echo.

echo [1/4] Pulling changes from git...
echo y | %PLINK% -ssh -P %PORT% -pw %PASSWORD% %SERVER% "cd /root/xaker && git pull origin prod" > deploy_step1.txt 2>&1
type deploy_step1.txt
echo.

echo [2/4] Building backend...
echo y | %PLINK% -ssh -P %PORT% -pw %PASSWORD% %SERVER% "cd /root/xaker/backend && npm run build" > deploy_step2.txt 2>&1
type deploy_step2.txt
echo.

echo [3/4] Restarting backend...
echo y | %PLINK% -ssh -P %PORT% -pw %PASSWORD% %SERVER% "pm2 restart xaker-backend" > deploy_step3.txt 2>&1
type deploy_step3.txt
echo.

echo [4/4] Checking status...
echo y | %PLINK% -ssh -P %PORT% -pw %PASSWORD% %SERVER% "pm2 status xaker-backend" > deploy_step4.txt 2>&1
type deploy_step4.txt
echo.

echo ============================================================
echo DEPLOYMENT COMPLETE
echo ============================================================

del deploy_step*.txt 2>nul

