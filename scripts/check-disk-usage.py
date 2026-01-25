#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check disk usage on server"""

import paramiko
import sys

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
print("CHECKING DISK USAGE")
print("=" * 80)

print("\n1. Overall disk usage:")
stdin, stdout, stderr = ssh.exec_command('df -h')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n2. Top directories by size:")
stdin, stdout, stderr = ssh.exec_command('du -h --max-depth=1 / 2>/dev/null | sort -hr | head -20')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n3. Docker disk usage:")
stdin, stdout, stderr = ssh.exec_command('docker system df')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n4. Docker images:")
stdin, stdout, stderr = ssh.exec_command('docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | head -20')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n5. Docker containers:")
stdin, stdout, stderr = ssh.exec_command('docker ps -a --format "table {{.Names}}\t{{.Size}}"')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n6. Docker volumes:")
stdin, stdout, stderr = ssh.exec_command('docker volume ls -q | xargs -r docker volume inspect --format "{{.Name}}: {{.Mountpoint}}" 2>/dev/null | head -10')
volumes = stdout.read().decode('utf-8', errors='replace')
print(volumes)

if volumes.strip():
    print("\n7. Checking volume sizes:")
    for line in volumes.strip().split('\n'):
        if ':' in line:
            vol_name = line.split(':')[0]
            vol_path = line.split(':', 1)[1].strip()
            stdin, stdout, stderr = ssh.exec_command(f'du -sh {vol_path} 2>/dev/null')
            size = stdout.read().decode('utf-8', errors='replace').strip()
            if size:
                print(f"   {vol_name}: {size}")

print("\n8. Project directory size:")
stdin, stdout, stderr = ssh.exec_command('du -sh /opt/xaker /root/xaker /var/www 2>/dev/null')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n9. Large files (>100MB):")
stdin, stdout, stderr = ssh.exec_command('find / -type f -size +100M 2>/dev/null | head -20')
large_files = stdout.read().decode('utf-8', errors='replace')
if large_files.strip():
    print(large_files)
    print("\n   Getting sizes:")
    for file_path in large_files.strip().split('\n')[:10]:
        if file_path:
            stdin, stdout, stderr = ssh.exec_command(f'ls -lh "{file_path}" 2>/dev/null')
            size_info = stdout.read().decode('utf-8', errors='replace').strip()
            if size_info:
                print(f"   {size_info}")
else:
    print("   No large files found")

print("\n10. Docker build cache:")
stdin, stdout, stderr = ssh.exec_command('docker builder prune --dry-run --all 2>&1 | head -20')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nTo free up space, you can:")
print("1. docker system prune -a --volumes (removes unused images, containers, volumes)")
print("2. docker builder prune -a (removes build cache)")
print("3. Remove old Docker images: docker image prune -a")
print("4. Check /var/lib/docker for Docker data")

ssh.close()

