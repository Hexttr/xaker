#!/bin/bash
# Fix duplicate and rebuild

cd /opt/xaker/shannon

# Fix duplicate NODE
sed -i '/NODE=\/usr\/bin\/node/,${ /NODE=\/usr\/bin\/node/!b; :a; N; /NODE=\/usr\/bin\/node/{ s/.*//; ba; }; }' docker-compose.yml

# Validate
docker-compose config > /dev/null 2>&1 && echo "✅ docker-compose.yml valid" || echo "⚠️ Validation failed"

# Rebuild
echo "Rebuilding worker image..."
docker-compose build --no-cache worker 2>&1 | tail -20

# Restart
docker-compose up -d worker

# Verify
sleep 5
docker ps | grep shannon | grep worker && echo "✅ Worker running" || echo "⚠️ Worker not running"

# Check node
CONTAINER=$(docker ps | grep shannon | grep worker | awk '{print $1}')
if [ -n "$CONTAINER" ]; then
    docker exec $CONTAINER sh -c "su pentest -c 'which node && node --version'" && echo "✅ Node accessible"
fi

# Restart backend
pm2 restart xaker-backend && echo "✅ Backend restarted"

echo "✅ Done!"

