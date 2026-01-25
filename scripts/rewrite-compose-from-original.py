#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rewrite docker-compose.yml from original with our fixes"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def rewrite_compose():
    """Rewrite docker-compose.yml"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("REWRITING DOCKER-COMPOSE.YML FROM ORIGINAL")
    print("=" * 80)
    
    # Create new docker-compose.yml based on original but with our entrypoint fix
    new_compose = """services:
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
    entrypoint: ["/bin/sh", "-c"]
    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"
    environment:
      - TEMPORAL_ADDRESS=temporal:7233
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
      - ANTHROPIC_BASE_URL=${ANTHROPIC_BASE_URL:-}  # Optional: route through claude-code-router
      - ANTHROPIC_AUTH_TOKEN=${ANTHROPIC_AUTH_TOKEN:-}  # Auth token for router
      - ROUTER_DEFAULT=${ROUTER_DEFAULT:-}  # Model name when using router (e.g., "gemini,gemini-2.5-pro")
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
    
    print("\n1. Writing new docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(new_compose.encode('utf-8'))
    sftp.close()
    
    # Verify
    print("\n2. Verifying docker-compose.yml...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose config 2>&1')
    verify = stdout.read().decode('utf-8', errors='replace')
    if 'error' in verify.lower() or 'Error' in verify:
        print(f"   ⚠️  Errors: {verify[-500:]}")
    else:
        print("   ✅ docker-compose.yml is valid")
    
    # Start services
    print("\n3. Starting services...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose down && docker-compose up -d')
    start_output = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    print(start_output)
    if errors:
        print(f"Errors: {errors}")
    
    import time
    time.sleep(5)
    
    # Check status
    print("\n4. Checking status...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps')
    status = stdout.read().decode('utf-8', errors='replace')
    print(status)
    
    # Verify worker
    print("\n5. Verifying worker...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker | head -1')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   Worker container: {container_id}")
        
        time.sleep(3)
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version"')
        verify_worker = stdout.read().decode('utf-8', errors='replace')
        print(verify_worker)
    else:
        print("   Worker container not found")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("REWRITE COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    rewrite_compose()

