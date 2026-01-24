#!/usr/bin/env python3
"""
Universal Server Manager
Works with multiple connection methods:
1. Paramiko (SSH library)
2. Subprocess SSH (with sshpass for passwords)
3. PuTTY plink (Windows)
4. Direct SSH key authentication
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

# Try to import paramiko
try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False


class UniversalServerManager:
    """Universal server manager that tries multiple connection methods"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with config file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / ".server-config.local"
        
        self.config = self._load_config(config_path)
        self.connection_method = None
        self.ssh_client = None
        self.sftp_client = None
    
    def _load_config(self, config_path: Path) -> Dict[str, str]:
        """Load configuration from file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        config = {}
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        
        return config
    
    def _test_connection_method(self) -> str:
        """Test which connection method works"""
        host = self.config['SERVER_HOST']
        port = int(self.config.get('SERVER_PORT', 22))
        user = self.config['SERVER_USER']
        password = self.config.get('SERVER_PASSWORD')
        ssh_key_path = self.config.get('SSH_KEY_PATH')
        
        # Method 1: Try SSH key with subprocess (most reliable)
        if ssh_key_path and os.path.exists(os.path.expanduser(ssh_key_path)):
            key_path = os.path.expanduser(ssh_key_path)
            test_cmd = ['ssh', '-i', key_path, '-p', str(port), 
                       '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=5',
                       f"{user}@{host}", "echo test"]
            try:
                result = subprocess.run(test_cmd, capture_output=True, timeout=10)
                if result.returncode == 0:
                    return "ssh_key_subprocess"
            except:
                pass
        
        # Method 2: Try paramiko with password
        if HAS_PARAMIKO and password:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=host,
                    port=port,
                    username=user,
                    password=password,
                    timeout=10,
                    banner_timeout=10
                )
                ssh.close()
                return "paramiko_password"
            except:
                pass
        
        # Method 3: Try plink (PuTTY) on Windows
        if sys.platform == 'win32':
            plink_paths = ['plink.exe', 'C:\\Program Files\\PuTTY\\plink.exe']
            for plink in plink_paths:
                if os.path.exists(plink) or subprocess.run(['where', plink], capture_output=True).returncode == 0:
                    return "plink"
        
        # Method 4: Try sshpass (Linux/Mac)
        if subprocess.run(['which', 'sshpass'], capture_output=True).returncode == 0:
            return "sshpass"
        
        return "none"
    
    def connect(self) -> bool:
        """Connect to server using best available method"""
        method = self._test_connection_method()
        self.connection_method = method
        
        if method == "none":
            print("No working connection method found")
            print("Available methods:")
            print("  1. SSH key authentication (recommended)")
            print("  2. Paramiko with password (requires: pip install paramiko)")
            print("  3. PuTTY plink (Windows)")
            print("  4. sshpass (Linux/Mac)")
            return False
        
        print(f"Using connection method: {method}")
        return True
    
    def execute(self, command: str) -> Tuple[int, str, str]:
        """Execute command on server"""
        if not self.connection_method:
            if not self.connect():
                return (1, "", "Not connected")
        
        method = self.connection_method
        host = self.config['SERVER_HOST']
        port = int(self.config.get('SERVER_PORT', 22))
        user = self.config['SERVER_USER']
        password = self.config.get('SERVER_PASSWORD')
        ssh_key_path = self.config.get('SSH_KEY_PATH')
        
        # Method 1: SSH key with subprocess
        if method == "ssh_key_subprocess":
            key_path = os.path.expanduser(ssh_key_path)
            ssh_cmd = ['ssh', '-i', key_path, '-p', str(port),
                      '-o', 'StrictHostKeyChecking=no',
                      f"{user}@{host}", command]
            try:
                result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)
                return (result.returncode, result.stdout, result.stderr)
            except subprocess.TimeoutExpired:
                return (1, "", "Command timeout")
        
        # Method 2: Paramiko with password
        elif method == "paramiko_password":
            try:
                if not self.ssh_client:
                    self.ssh_client = paramiko.SSHClient()
                    self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    self.ssh_client.connect(
                        hostname=host,
                        port=port,
                        username=user,
                        password=password,
                        timeout=30,
                        banner_timeout=60
                    )
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
                exit_code = stdout.channel.recv_exit_status()
                return (exit_code, stdout.read().decode('utf-8'), stderr.read().decode('utf-8'))
            except Exception as e:
                return (1, "", str(e))
        
        # Method 3: PuTTY plink
        elif method == "plink":
            plink_paths = ['plink.exe', 'C:\\Program Files\\PuTTY\\plink.exe']
            plink = None
            for p in plink_paths:
                if os.path.exists(p):
                    plink = p
                    break
            if not plink:
                # Try to find in PATH
                result = subprocess.run(['where', 'plink.exe'], capture_output=True, text=True)
                if result.returncode == 0:
                    plink = result.stdout.strip().split('\n')[0]
            
            if plink:
                cmd = [plink, '-ssh', '-P', str(port), '-pw', password, f"{user}@{host}", command]
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    return (result.returncode, result.stdout, result.stderr)
                except Exception as e:
                    return (1, "", str(e))
        
        # Method 4: sshpass
        elif method == "sshpass":
            ssh_cmd = ['sshpass', '-p', password, 'ssh', '-p', str(port),
                      '-o', 'StrictHostKeyChecking=no',
                      f"{user}@{host}", command]
            try:
                result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)
                return (result.returncode, result.stdout, result.stderr)
            except Exception as e:
                return (1, "", str(e))
        
        return (1, "", "Unknown connection method")
    
    def read_file(self, remote_path: str) -> Optional[str]:
        """Read file from server"""
        exit_code, stdout, stderr = self.execute(f"cat {remote_path}")
        if exit_code == 0:
            return stdout
        return None
    
    def write_file(self, remote_path: str, content: str) -> bool:
        """Write file to server"""
        # Escape content for shell
        import shlex
        escaped_content = shlex.quote(content)
        command = f"mkdir -p $(dirname {shlex.quote(remote_path)}) && echo {escaped_content} > {shlex.quote(remote_path)}"
        exit_code, _, _ = self.execute(command)
        return exit_code == 0
    
    def disconnect(self):
        """Disconnect from server"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


if __name__ == "__main__":
    print("Testing universal server manager...")
    manager = UniversalServerManager()
    
    if manager.connect():
        print(f"Connected using method: {manager.connection_method}")
        exit_code, stdout, stderr = manager.execute("echo 'Test successful'")
        print(f"Command result: exit={exit_code}")
        print(f"Output: {stdout.strip()}")
        if stderr:
            print(f"Error: {stderr}")
    else:
        print("Failed to connect")
        print("\nTo fix:")
        print("1. Install paramiko: pip install paramiko")
        print("2. Or configure SSH_KEY_PATH in .server-config.local")
        print("3. Or install PuTTY (Windows) or sshpass (Linux/Mac)")

