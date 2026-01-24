#!/usr/bin/env python3
"""
Automatic deployment script
Deploys changes to server without manual intervention
"""

import sys
import subprocess
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def deploy_via_ssh():
    """Deploy using SSH subprocess"""
    config_path = Path(__file__).parent.parent / ".server-config.local"
    
    # Load config
    config = {}
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    host = config.get('SERVER_HOST', '5.129.235.52')
    user = config.get('SERVER_USER', 'root')
    password = config.get('SERVER_PASSWORD', 'cY7^kCCA_6uQ5S')
    port = int(config.get('SERVER_PORT', 22))
    
    ssh_cmd_base = ['ssh', '-p', str(port), '-o', 'StrictHostKeyChecking=no', 
                    '-o', 'UserKnownHostsFile=/dev/null', f"{user}@{host}"]
    
    commands = [
        "cd /root/xaker && git pull origin prod",
        "cd /root/xaker/backend && npm run build",
        "pm2 restart xaker-backend || (cd /root/xaker/backend && pm2 start npm --name xaker-backend -- run start)",
        "pm2 status xaker-backend"
    ]
    
    print("=" * 60)
    print("AUTOMATIC DEPLOYMENT")
    print("=" * 60)
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n[{i}/{len(commands)}] Executing: {cmd}")
        print("-" * 60)
        
        # Try with sshpass if available
        if password:
            try:
                result = subprocess.run(
                    ['sshpass', '-p', password] + ssh_cmd_base + [cmd],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                if result.returncode != 0:
                    print(f"[WARNING] Command returned exit code {result.returncode}")
            except FileNotFoundError:
                # Try with expect-like approach using plink
                print("sshpass not found, trying plink...")
                plink_path = r"C:\Program Files\PuTTY\plink.exe"
                if os.path.exists(plink_path):
                    result = subprocess.run(
                        [plink_path, '-ssh', '-P', str(port), '-pw', password, 
                         f"{user}@{host}", cmd],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        input='y\n'  # Accept host key
                    )
                    print(result.stdout)
                    if result.stderr:
                        print("STDERR:", result.stderr)
                else:
                    print("[ERROR] Neither sshpass nor plink found")
                    return False
        else:
            # Try without password (using SSH keys)
            result = subprocess.run(
                ssh_cmd_base + [cmd],
                capture_output=True,
                text=True,
                timeout=300
            )
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
    
    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE")
    print("=" * 60)
    return True

def deploy_via_paramiko():
    """Deploy using paramiko"""
    try:
        import paramiko
    except ImportError:
        print("paramiko not installed, trying subprocess method...")
        return deploy_via_ssh()
    
    config_path = Path(__file__).parent.parent / ".server-config.local"
    
    # Load config
    config = {}
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    host = config.get('SERVER_HOST', '5.129.235.52')
    user = config.get('SERVER_USER', 'root')
    password = config.get('SERVER_PASSWORD', 'cY7^kCCA_6uQ5S')
    port = int(config.get('SERVER_PORT', 22))
    
    print("=" * 60)
    print("AUTOMATIC DEPLOYMENT (via paramiko)")
    print("=" * 60)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"\nConnecting to {user}@{host}:{port}...")
        ssh.connect(
            hostname=host,
            port=port,
            username=user,
            password=password,
            timeout=30,
            banner_timeout=60,
            auth_timeout=30
        )
        print("[OK] Connected")
        
        commands = [
            ("cd /root/xaker && git pull origin prod", "Pull changes"),
            ("cd /root/xaker/backend && npm run build", "Build backend"),
            ("pm2 restart xaker-backend || (cd /root/xaker/backend && pm2 start npm --name xaker-backend -- run start)", "Restart backend"),
            ("pm2 status xaker-backend", "Check status")
        ]
        
        for i, (cmd, desc) in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] {desc}")
            print("-" * 60)
            print(f"Command: {cmd}")
            
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
            exit_code = stdout.channel.recv_exit_status()
            
            stdout_text = stdout.read().decode('utf-8')
            stderr_text = stderr.read().decode('utf-8')
            
            if stdout_text:
                print(stdout_text)
            if stderr_text:
                print("STDERR:", stderr_text)
            
            if exit_code != 0 and i < len(commands) - 1:  # Don't fail on last command (status check)
                print(f"[WARNING] Command returned exit code {exit_code}")
        
        ssh.close()
        print("\n" + "=" * 60)
        print("DEPLOYMENT COMPLETE")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("Falling back to subprocess method...")
        return deploy_via_ssh()

if __name__ == "__main__":
    # Try paramiko first, fallback to subprocess
    success = deploy_via_paramiko()
    sys.exit(0 if success else 1)

