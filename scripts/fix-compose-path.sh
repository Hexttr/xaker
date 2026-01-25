#!/bin/bash
# Fix PATH in docker-compose.yml

cd /opt/xaker/shannon

# Add PATH after environment: line in worker section
sed -i '/worker:/,/^  [^ ]/ {
  /environment:/a\
      - PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin
}' docker-compose.yml

echo "PATH added to docker-compose.yml"
grep -A 12 "worker:" docker-compose.yml | head -15

