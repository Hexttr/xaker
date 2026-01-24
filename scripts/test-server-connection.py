#!/usr/bin/env python3
"""Quick test of server connectivity"""

import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import sys
sys.path.insert(0, str(Path(__file__).parent))
from auto_server_manager import ServerManager

def test_port(host, port, timeout=5):
    """Test if port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Port test error: {e}")
        return False

def main():
    # Load config
    config_path = Path(__file__).parent.parent / ".server-config.local"
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        return
    
    config = {}
    with open(config_path, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    host = config.get('SERVER_HOST', '5.129.235.52')
    port = int(config.get('SERVER_PORT', 22))
    
    print(f"Testing connection to {host}:{port}...")
    
    # Test port
    print("1. Testing port connectivity...")
    if test_port(host, port):
        print("   ✅ Port is open")
    else:
        print("   ❌ Port is closed or filtered")
        print("   This might be a firewall issue or server is down")
        return
    
    # Test SSH connection
    print("2. Testing SSH connection...")
    try:
        manager = ServerManager()
        if manager.connect():
            print("   ✅ SSH connection successful!")
            
            # Test command execution
            exit_code, stdout, stderr = manager.execute("echo 'Test command'")
            if exit_code == 0:
                print(f"   ✅ Command execution works: {stdout.strip()}")
            else:
                print(f"   ⚠️  Command execution failed: {stderr}")
            
            manager.disconnect()
        else:
            print("   ❌ SSH connection failed")
    except Exception as e:
        print(f"   ❌ SSH connection error: {e}")

if __name__ == "__main__":
    main()

