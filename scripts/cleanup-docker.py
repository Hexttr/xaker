#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cleanup Docker to free up space"""

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
print("CLEANING UP DOCKER TO FREE UP SPACE")
print("=" * 80)

print("\nCurrent disk usage:")
stdin, stdout, stderr = ssh.exec_command('df -h /')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n1. Stopping unused containers...")
stdin, stdout, stderr = ssh.exec_command('docker ps -a --filter "status=exited" --format "{{.ID}}" | xargs -r docker rm')
removed = stdout.read().decode('utf-8', errors='replace')
if removed:
    print(f"   Removed containers: {removed.strip()}")
else:
    print("   No stopped containers to remove")

print("\n2. Removing unused images (dangling)...")
stdin, stdout, stderr = ssh.exec_command('docker image prune -f')
prune_output = stdout.read().decode('utf-8', errors='replace')
print(prune_output)

print("\n3. Removing unused images (all unused)...")
print("   ⚠️  This will remove all images not used by running containers")
stdin, stdout, stderr = ssh.exec_command('docker image prune -a -f')
prune_all_output = stdout.read().decode('utf-8', errors='replace')
print(prune_all_output)

print("\n4. Removing unused volumes...")
stdin, stdout, stderr = ssh.exec_command('docker volume prune -f')
volume_output = stdout.read().decode('utf-8', errors='replace')
print(volume_output)

print("\n5. Cleaning build cache...")
stdin, stdout, stderr = ssh.exec_command('docker builder prune -af')
builder_output = stdout.read().decode('utf-8', errors='replace')
print(builder_output)

print("\n6. Full system prune (removes everything unused)...")
stdin, stdout, stderr = ssh.exec_command('docker system prune -af --volumes')
system_output = stdout.read().decode('utf-8', errors='replace')
print(system_output[-1000:])  # Last 1000 chars

print("\n7. Checking disk usage after cleanup:")
stdin, stdout, stderr = ssh.exec_command('df -h /')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n8. Docker disk usage after cleanup:")
stdin, stdout, stderr = ssh.exec_command('docker system df')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n9. Remaining images:")
stdin, stdout, stderr = ssh.exec_command('docker images')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n10. Remaining containers:")
stdin, stdout, stderr = ssh.exec_command('docker ps -a')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)
print("\nIf space is still low, you may need to:")
print("1. Remove specific large images manually")
print("2. Check /var/lib/docker/overlay2 for large directories")
print("3. Restart Docker service if needed")

ssh.close()

