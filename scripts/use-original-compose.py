#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Use original docker-compose.yml from Shannon repo"""

import paramiko
import sys
import time

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)

print("=" * 80)
print("USING ORIGINAL DOCKER-COMPOSE.YML FROM SHANNON REPO")
print("=" * 80)
print("\nBased on original Shannon repository structure")
print("Using simple entrypoint with proper PATH setup")

# Original docker-compose.yml from Shannon repo
original_compose = """services:
  temporal:
    image: temporalio/temporal:latest
    command: ["server", "start-dev", "--db-filename", "/home/temporal/temporal.db", "--ip", "0.0.0.0"]
    ports:
      - "7233:7233"   # gRPC
      - "8233:8233"   # Web UI (built-in)
    volumes:
      - temporal-data:/home/temporal
    healthcheck:
      test: ["CMD", "temporal", "operator", "cluster", "health", "--address", "localhost:7233"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

  worker:
    build: .
    entrypoint: ["node", "dist/temporal/worker.js"]
    environment:
      - TEMPORAL_ADDRESS=temporal:7233
      - PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
      - ANTHROPIC_BASE_URL=${ANTHROPIC_BASE_URL:-}
      - ANTHROPIC_AUTH_TOKEN=${ANTHROPIC_AUTH_TOKEN:-}
      - ROUTER_DEFAULT=${ROUTER_DEFAULT:-}
      - CLAUDE_CODE_OAUTH_TOKEN=${CLAUDE_CODE_OAUTH_TOKEN:-}
      - CLAUDE_CODE_MAX_OUTPUT_TOKENS=${CLAUDE_CODE_MAX_OUTPUT_TOKENS:-64000}
    depends_on:
      temporal:
        condition: service_healthy
    volumes:
      - ./prompts:/app/prompts
      - ./audit-logs:/app/audit-logs
      - ${OUTPUT_DIR:-./audit-logs}:/app/output
      - ${TARGET_REPO:-.}:/target-repo
      - ${BENCHMARKS_BASE:-.}:/benchmarks
    shm_size: 2gb
    ipc: host
    security_opt:
      - seccomp:unconfined

volumes:
  temporal-data:
"""

print("\n1. Writing original docker-compose.yml...")
sftp = ssh.open_sftp()
with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
    f.write(original_compose.encode('utf-8'))
sftp.close()
print("   ✅ docker-compose.yml restored to original")

print("\n2. Stopping and removing old worker...")
stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n3. Starting worker with original config...")
stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
output = stdout.read().decode('utf-8', errors='replace')
error = stderr.read().decode('utf-8', errors='replace')
print(output)
if error:
    print(f"Errors: {error}")

time.sleep(5)

print("\n4. Verifying worker...")
stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
worker = stdout.read().decode('utf-8', errors='replace')
if worker:
    print("   ✅ Worker is running!")
    
    print("\n5. Checking PATH and node...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "echo PATH=$PATH && which node && node --version"')
    env_check = stdout.read().decode('utf-8', errors='replace')
    print(env_check)
    
    if '/usr/bin/node' in env_check or 'node' in env_check.lower():
        print("\n   ✅ Node is accessible!")
        
        # Restart backend
        print("\n6. Restarting backend...")
        stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS!")
        print("=" * 80)
        print("\nUsing original docker-compose.yml from Shannon repo")
        print("PATH is set correctly: /usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin")
        print("\n⚠️  Try a new pentest now!")
        print("If spawn node ENOENT still occurs, the issue is in the library")
        print("and we'll need to patch it or use a different approach")
    else:
        print("\n   ⚠️ Node not found in PATH")
else:
    print("\n   ⚠️ Worker not running")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose logs worker --tail=20')
    print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()

