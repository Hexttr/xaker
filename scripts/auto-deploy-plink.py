#!/usr/bin/env python3
"""
Automatic deployment using PuTTY plink
Works reliably on Windows
"""

import subprocess
import sys
import os
from pathlib import Path

def load_config():
    """Load server configuration"""
    config_path = Path(__file__).parent.parent / ".server-config.local"
    config = {}
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config

def run_command(plink_path, host, user, password, port, command, description):
    """Run command via plink"""
    print(f"\n[{description}]")
    print("-" * 60)
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(
            [plink_path, '-ssh', '-P', str(port), '-pw', password, f"{user}@{host}", command],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes timeout
            input='y\n'  # Accept host key
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.stderr.strip() and "The server's host key is not cached" not in result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("[ERROR] Command timed out")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    config = load_config()
    
    plink_path = r"C:\Program Files\PuTTY\plink.exe"
    if not os.path.exists(plink_path):
        print(f"[ERROR] PuTTY plink not found at {plink_path}")
        return False
    
    host = config.get('SERVER_HOST', '5.129.235.52')
    user = config.get('SERVER_USER', 'root')
    password = config.get('SERVER_PASSWORD', 'cY7^kCCA_6uQ5S')
    port = int(config.get('SERVER_PORT', 22))
    
    print("=" * 60)
    print("AUTOMATIC DEPLOYMENT")
    print("=" * 60)
    print(f"Server: {user}@{host}:{port}")
    print(f"Using: {plink_path}")
    
    commands = [
        ("cd /root/xaker && git pull origin prod", "1/4 Pulling changes from git"),
        ("cd /root/xaker/backend && npm run build", "2/4 Building backend"),
        ("pm2 restart xaker-backend || (cd /root/xaker/backend && pm2 start npm --name xaker-backend -- run start)", "3/4 Restarting backend"),
        ("pm2 status xaker-backend && pm2 logs xaker-backend --lines 10 --nostream", "4/4 Checking status and logs")
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(plink_path, host, user, password, port, cmd, desc):
            if "status" not in desc.lower():  # Don't fail on status check
                print(f"[WARNING] Command failed, but continuing...")
                success = False
    
    print("\n" + "=" * 60)
    if success:
        print("DEPLOYMENT COMPLETE")
    else:
        print("DEPLOYMENT COMPLETED WITH WARNINGS")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

