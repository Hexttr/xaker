#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check and use existing image"""

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

def use_existing():
    """Use existing image"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("USING EXISTING IMAGE AND ENSURING NODE")
    print("=" * 80)
    
    # Check for existing images
    print("\n1. Checking for existing images...")
    stdin, stdout, stderr = ssh.exec_command('docker images --format "{{.Repository}}:{{.Tag}}" | grep shannon')
    images = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
    images = [img for img in images if img]
    
    if images:
        print(f"   Found {len(images)} images: {images}")
        image_name = images[0]
        print(f"   Using: {image_name}")
    else:
        print("   ⚠️  No existing images found")
        ssh.close()
        return
    
    # Update docker-compose.yml to use image instead of build
    print("\n2. Updating docker-compose.yml to use existing image...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose_content = f.read().decode('utf-8')
    
    # Replace build: . with image: shannon_worker:latest
    if 'build: .' in compose_content:
        compose_content = compose_content.replace('build: .', f'image: {image_name}')
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
            f.write(compose_content.encode('utf-8'))
        print("   ✅ Updated docker-compose.yml to use existing image")
    else:
        print("   Already using image")
    
    sftp.close()
    
    # Start services
    print("\n3. Starting services...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose down && docker-compose up -d')
    start_output = stdout.read().decode('utf-8', errors='replace')
    print(start_output)
    
    time.sleep(5)
    
    # Get worker container
    print("\n4. Finding worker container...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker | head -1')
    worker = stdout.read().decode('utf-8', errors='replace')
    
    if worker:
        container_id = worker.split()[0]
        print(f"   Container: {container_id}")
        
        # Create symlink
        print("\n5. Creating symlink...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec -u root {container_id} sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node && ls -la /usr/local/bin/node"')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        # Verify
        print("\n6. Verifying...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "which node && /usr/local/bin/node --version && printenv NODE && printenv PATH"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        # Restart backend
        print("\n7. Restarting backend...")
        stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        print("\n✅ SUCCESS! Using existing image with node symlink")
        print("Try a new pentest now")
    else:
        print("   ⚠️  Worker container not found")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    use_existing()

