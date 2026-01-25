#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check and start Temporal if needed"""

import paramiko
import sys
import os

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_temporal():
    """Check Temporal status"""
    print("=" * 80)
    print("CHECKING TEMPORAL STATUS")
    print("=" * 80)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
        
        # Check if Temporal is running
        print("\n1. Checking Temporal processes...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'temporal|tctl' | grep -v grep")
        temporal_processes = stdout.read().decode('utf-8', errors='replace')
        if temporal_processes.strip():
            print(temporal_processes)
        else:
            print("   ⚠️  No Temporal processes found")
        
        # Check if port 7233 is listening
        print("\n2. Checking Temporal port 7233...")
        stdin, stdout, stderr = ssh.exec_command("netstat -tuln | grep 7233 || ss -tuln | grep 7233 || echo 'Port 7233 not listening'")
        port_info = stdout.read().decode('utf-8', errors='replace')
        print(port_info)
        
        # Check if Temporal is installed
        print("\n3. Checking Temporal installation...")
        stdin, stdout, stderr = ssh.exec_command("which temporal || find /opt /usr/local -name temporal -type f 2>/dev/null | head -5")
        temporal_path = stdout.read().decode('utf-8', errors='replace')
        if temporal_path.strip():
            print(f"   Found: {temporal_path.strip()}")
        else:
            print("   ⚠️  Temporal not found in PATH")
        
        # Check Shannon directory for Temporal config
        print("\n4. Checking Shannon directory for Temporal config...")
        stdin, stdout, stderr = ssh.exec_command("ls -la /opt/xaker/shannon/ 2>&1 | head -20")
        shannon_dir = stdout.read().decode('utf-8', errors='replace')
        print(shannon_dir)
        
        # Check docker containers (Temporal might be in Docker)
        print("\n5. Checking Docker containers...")
        stdin, stdout, stderr = ssh.exec_command("docker ps -a 2>&1 | grep -i temporal || echo 'No Temporal containers'")
        docker_info = stdout.read().decode('utf-8', errors='replace')
        print(docker_info)
        
        # Check systemd services
        print("\n6. Checking systemd services...")
        stdin, stdout, stderr = ssh.exec_command("systemctl list-units --type=service | grep -i temporal || echo 'No Temporal services'")
        systemd_info = stdout.read().decode('utf-8', errors='replace')
        print(systemd_info)
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("RECOMMENDATION:")
        print("=" * 80)
        if "7233" not in port_info:
            print("❌ Temporal is NOT running!")
            print("   Shannon needs Temporal to work.")
            print("   Options:")
            print("   1. Start Temporal server")
            print("   2. Check if Temporal should be running in Docker")
            print("   3. Check Shannon documentation for Temporal setup")
        else:
            print("✅ Temporal appears to be running")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_temporal()

