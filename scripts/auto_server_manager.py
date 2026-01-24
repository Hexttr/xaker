#!/usr/bin/env python3
"""
Automated Server Manager
Provides direct file management capabilities on Ubuntu server
No manual intervention required - AI can use this directly
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    print("Installing paramiko...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko", "--quiet"])
    import paramiko
    HAS_PARAMIKO = True


class ServerManager:
    """Automated server manager with full file access"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with config file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / ".server-config.local"
        
        self.config = self._load_config(config_path)
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.sftp_client: Optional[paramiko.SFTPClient] = None
    
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
    
    def connect(self) -> bool:
        """Connect to server"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            host = self.config['SERVER_HOST']
            port = int(self.config.get('SERVER_PORT', 22))
            user = self.config['SERVER_USER']
            password = self.config.get('SERVER_PASSWORD')
            ssh_key_path = self.config.get('SSH_KEY_PATH')
            
            # Connection parameters with increased timeout
            connect_params = {
                'hostname': host,
                'port': port,
                'username': user,
                'timeout': 30,  # Increased timeout
                'banner_timeout': 60,  # Increased banner timeout
                'auth_timeout': 30,  # Auth timeout
                'look_for_keys': False,  # Don't look for keys automatically
                'allow_agent': False,  # Don't use SSH agent
            }
            
            # Try SSH key first
            if ssh_key_path and os.path.exists(os.path.expanduser(ssh_key_path)):
                key_path = os.path.expanduser(ssh_key_path)
                connect_params['key_filename'] = key_path
                connect_params['look_for_keys'] = True
                self.ssh_client.connect(**connect_params)
            elif password:
                connect_params['password'] = password
                # Try connecting with password
                try:
                    self.ssh_client.connect(**connect_params)
                except paramiko.ssh_exception.SSHException as e:
                    # If banner error, try with subprocess fallback
                    if "banner" in str(e).lower():
                        print(f"Paramiko banner error, trying subprocess fallback...")
                        # Will use subprocess fallback in execute method
                        raise ConnectionError("Banner error, will use subprocess")
                    raise
            else:
                raise ValueError("No SSH key or password provided")
            
            self.sftp_client = self.ssh_client.open_sftp()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            print(f"Host: {host}, Port: {port}, User: {user}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
    
    def execute(self, command: str, use_subprocess: bool = False) -> tuple[int, str, str]:
        """Execute command on server"""
        # Try subprocess fallback if paramiko fails
        if use_subprocess or not self.ssh_client:
            return self._execute_subprocess(command)
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode('utf-8')
            stderr_text = stderr.read().decode('utf-8')
            return (exit_code, stdout_text, stderr_text)
        except Exception as e:
            print(f"Paramiko execution failed: {e}, trying subprocess...")
            return self._execute_subprocess(command)
    
    def _execute_subprocess(self, command: str) -> tuple[int, str, str]:
        """Execute command using subprocess (fallback)"""
        import subprocess
        
        host = self.config['SERVER_HOST']
        port = int(self.config.get('SERVER_PORT', 22))
        user = self.config['SERVER_USER']
        password = self.config.get('SERVER_PASSWORD')
        ssh_key_path = self.config.get('SSH_KEY_PATH')
        
        ssh_cmd = ['ssh', '-p', str(port), '-o', 'StrictHostKeyChecking=no']
        
        if ssh_key_path and os.path.exists(os.path.expanduser(ssh_key_path)):
            ssh_cmd.extend(['-i', os.path.expanduser(ssh_key_path)])
        
        ssh_cmd.append(f"{user}@{host}")
        ssh_cmd.append(command)
        
        try:
            # For password auth, we'd need sshpass, but let's try without first
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                input=password if password and not ssh_key_path else None
            )
            return (result.returncode, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return (1, "", "Command timeout")
        except FileNotFoundError:
            return (1, "", "SSH command not found. Install OpenSSH or configure SSH_KEY_PATH")
        except Exception as e:
            return (1, "", str(e))
    
    def read_file(self, remote_path: str) -> Optional[str]:
        """Read file from server"""
        if not self.sftp_client:
            if not self.connect():
                return None
        
        try:
            with self.sftp_client.open(remote_path, 'r') as f:
                return f.read().decode('utf-8')
        except Exception as e:
            print(f"Error reading file {remote_path}: {e}")
            return None
    
    def write_file(self, remote_path: str, content: str) -> bool:
        """Write file to server"""
        if not self.sftp_client:
            if not self.connect():
                return False
        
        try:
            # Create directory if needed
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                self.execute(f"mkdir -p {remote_dir}")
            
            with self.sftp_client.open(remote_path, 'w') as f:
                f.write(content.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error writing file {remote_path}: {e}")
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """Delete file from server"""
        if not self.sftp_client:
            if not self.connect():
                return False
        
        try:
            self.sftp_client.remove(remote_path)
            return True
        except Exception as e:
            print(f"Error deleting file {remote_path}: {e}")
            return False
    
    def list_directory(self, remote_path: str) -> List[Dict[str, Any]]:
        """List directory contents"""
        if not self.sftp_client:
            if not self.connect():
                return []
        
        try:
            items = []
            for item in self.sftp_client.listdir_attr(remote_path):
                items.append({
                    'name': item.filename,
                    'size': item.st_size,
                    'mode': oct(item.st_mode),
                    'is_dir': item.st_mode & 0o040000 != 0
                })
            return items
        except Exception as e:
            print(f"Error listing directory {remote_path}: {e}")
            return []
    
    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists on server"""
        if not self.sftp_client:
            if not self.connect():
                return False
        
        try:
            self.sftp_client.stat(remote_path)
            return True
        except:
            return False
    
    def create_directory(self, remote_path: str) -> bool:
        """Create directory on server"""
        exit_code, _, _ = self.execute(f"mkdir -p {remote_path}")
        return exit_code == 0
    
    def copy_file(self, local_path: str, remote_path: str) -> bool:
        """Copy file from local to server"""
        if not self.sftp_client:
            if not self.connect():
                return False
        
        try:
            # Create directory if needed
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                self.create_directory(remote_dir)
            
            self.sftp_client.put(local_path, remote_path)
            return True
        except Exception as e:
            print(f"Error copying file {local_path} to {remote_path}: {e}")
            return False
    
    def copy_from_server(self, remote_path: str, local_path: str) -> bool:
        """Copy file from server to local"""
        if not self.sftp_client:
            if not self.connect():
                return False
        
        try:
            # Create local directory if needed
            local_dir = os.path.dirname(local_path)
            if local_dir:
                os.makedirs(local_dir, exist_ok=True)
            
            self.sftp_client.get(remote_path, local_path)
            return True
        except Exception as e:
            print(f"Error copying file {remote_path} to {local_path}: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Convenience functions for direct use
def get_server_manager() -> ServerManager:
    """Get configured server manager instance"""
    return ServerManager()


if __name__ == "__main__":
    # Test connection
    print("Testing server connection...")
    with ServerManager() as server:
        exit_code, stdout, stderr = server.execute("echo 'Connection test successful'")
        if exit_code == 0:
            print("✅ Connection successful!")
            print(stdout)
        else:
            print("❌ Connection failed!")
            print(stderr)

