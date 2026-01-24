#!/bin/bash
# Server-side deployment script
# Run this on the server: bash scripts/server-deploy.sh

set -e

echo "============================================================"
echo "SERVER-SIDE DEPLOYMENT"
echo "============================================================"

cd /root/xaker

echo ""
echo "[1/4] Pulling latest changes..."
git pull origin prod

echo ""
echo "[2/4] Building backend..."
cd backend
npm run build

echo ""
echo "[3/4] Restarting backend..."
pm2 restart xaker-backend || (pm2 start npm --name xaker-backend -- run start)

echo ""
echo "[4/4] Checking status..."
pm2 status xaker-backend
pm2 logs xaker-backend --lines 20 --nostream

echo ""
echo "============================================================"
echo "DEPLOYMENT COMPLETE"
echo "============================================================"

