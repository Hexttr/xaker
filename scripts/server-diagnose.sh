#!/bin/bash
# Server-side diagnostics script
# Run this on the server to diagnose pentest issues

echo "============================================================"
echo "PENTEST DIAGNOSTICS ON SERVER"
echo "============================================================"

# 1. Current directory
echo ""
echo "1. Current directory:"
pwd

# 2. Project structure
echo ""
echo "2. Project structure:"
ls -la /root/xaker/ 2>/dev/null | head -10

# 3. Shannon check
echo ""
echo "3. Shannon installation:"
if [ -d "/root/shannon" ]; then
    echo "   [OK] /root/shannon exists"
    ls -la /root/shannon/dist/temporal/client.js 2>/dev/null && echo "   [OK] Shannon built" || echo "   [ERROR] Shannon not built"
else
    echo "   [ERROR] /root/shannon not found"
fi

# 4. Backend .env
echo ""
echo "4. Backend configuration:"
if [ -f "/root/xaker/backend/.env" ]; then
    echo "   [OK] .env exists"
    if grep -q "ANTHROPIC_API_KEY=" /root/xaker/backend/.env; then
        API_KEY_PREVIEW=$(grep "ANTHROPIC_API_KEY=" /root/xaker/backend/.env | head -c 40)
        echo "   [OK] API key found: ${API_KEY_PREVIEW}..."
    else
        echo "   [ERROR] API key NOT FOUND in .env"
    fi
else
    echo "   [ERROR] .env not found"
fi

# 5. PM2 status
echo ""
echo "5. PM2 processes:"
pm2 list 2>/dev/null || echo "   [ERROR] PM2 not running"

# 6. Backend logs
echo ""
echo "6. Backend logs (last 30 lines):"
pm2 logs xaker-backend --lines 30 --nostream 2>/dev/null | tail -30 || echo "   [ERROR] Cannot get logs"

# 7. Node version
echo ""
echo "7. Node.js version:"
node --version
npm --version

# 8. Check if Shannon path is correct
echo ""
echo "8. Shannon path check:"
cd /root/xaker/backend
NODE_PROCESS_CWD=$(node -e "console.log(process.cwd())")
echo "   Node process.cwd(): $NODE_PROCESS_CWD"
SHANNON_EXPECTED=$(node -e "const path = require('path'); console.log(path.resolve(process.cwd(), '../shannon'))")
echo "   Expected Shannon path: $SHANNON_EXPECTED"
if [ -d "$SHANNON_EXPECTED" ]; then
    echo "   [OK] Shannon found at expected path"
else
    echo "   [ERROR] Shannon NOT found at expected path"
fi

echo ""
echo "============================================================"
echo "DIAGNOSTICS COMPLETE"
echo "============================================================"

