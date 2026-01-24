@echo off
setlocal

set WINSCP="C:\Users\User\AppData\Local\Programs\WinSCP\WinSCP.com"
set SERVER=5.129.235.52
set USER=root
set PASSWORD=cY7^kCCA_6uQ5S

echo ============================================================
echo AUTOMATIC DEPLOYMENT via WinSCP
echo ============================================================
echo.

(
echo option batch abort
echo option confirm off
echo open sftp://%USER%:%PASSWORD%@%SERVER%/
echo cd /root/xaker
echo call git pull origin prod
echo cd backend
echo call npm run build
echo call pm2 restart xaker-backend
echo call pm2 status xaker-backend
echo exit
) | %WINSCP% /script=-

echo.
echo ============================================================
echo DEPLOYMENT COMPLETE
echo ============================================================

