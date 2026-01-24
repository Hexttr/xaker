#!/usr/bin/env python3
"""
Server Utilities Module
Provides functions for secure server access
Reads credentials from .server-config.local file

Requirements:
    pip install paramiko

Alternative (using subprocess with ssh/scp):
    No additional requirements if SSH keys are configured
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional, List

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False


def get_server_config() -> Dict[str, str]:
    """Read server configuration from .server-config.local file"""
    script_dir = Path(__file__).parent
    config_file = script_dir.parent / ".server-config.local"
    
    if not config_file.exists():
        print(f"Error: Configuration file not found: {config_file}")
        print("Please copy .server-config.local.example to .server-config.local and fill in your credentials")
        sys.exit(1)
    
    config = {}
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config


def invoke_server_command(command: str, config: Optional[Dict[str, str]] = None) -> tuple[int, str, str]:
    """
    Execute a command on the remote server via SSH
    
    Returns: (exit_code, stdout, stderr)
    """
    if config is None:
        config = get_server_config()
    
    host = config.get('SERVER_HOST')
    user = config.get('SERVER_USER')
    password = config.get('SERVER_PASSWORD')
    port = int(config.get('SERVER_PORT', 22))
    ssh_key_path = config.get('SSH_KEY_PATH')
    
    ssh_command = f"{user}@{host}"
    
    # Try SSH key first, then password
    if ssh_key_path and os.path.exists(os.path.expanduser(ssh_key_path)):
        # Use SSH key
        ssh_cmd = [
            'ssh',
            '-i', os.path.expanduser(ssh_key_path),
            '-p', str(port),
            '-o', 'StrictHostKeyChecking=no',
            ssh_command,
            command
        ]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True)
        return (result.returncode, result.stdout, result.stderr)
    
    elif HAS_PARAMIKO and password:
        # Use paramiko for password-based auth
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=port, username=user, password=password, timeout=10)
            
            stdin, stdout, stderr = ssh.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode('utf-8')
            stderr_text = stderr.read().decode('utf-8')
            
            ssh.close()
            return (exit_code, stdout_text, stderr_text)
        except Exception as e:
            return (1, "", str(e))
    else:
        # Fallback to subprocess ssh (requires SSH key or passwordless setup)
        if password:
            print("Warning: Password-based SSH requires paramiko. Install with: pip install paramiko")
            print("Or configure SSH_KEY_PATH in .server-config.local")
            return (1, "", "Password-based SSH not available without paramiko")
        
        ssh_cmd = ['ssh', '-p', str(port), '-o', 'StrictHostKeyChecking=no', ssh_command, command]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True)
        return (result.returncode, result.stdout, result.stderr)


def copy_to_server(local_path: str, remote_path: str, config: Optional[Dict[str, str]] = None) -> bool:
    """Copy files to the remote server via SCP"""
    if config is None:
        config = get_server_config()
    
    host = config.get('SERVER_HOST')
    user = config.get('SERVER_USER')
    password = config.get('SERVER_PASSWORD')
    port = int(config.get('SERVER_PORT', 22))
    ssh_key_path = config.get('SSH_KEY_PATH')
    
    ssh_command = f"{user}@{host}"
    
    if ssh_key_path and os.path.exists(os.path.expanduser(ssh_key_path)):
        scp_cmd = [
            'scp',
            '-i', os.path.expanduser(ssh_key_path),
            '-P', str(port),
            '-r',
            local_path,
            f"{ssh_command}:{remote_path}"
        ]
    elif HAS_PARAMIKO and password:
        # Use paramiko for password-based SCP
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=port, username=user, password=password, timeout=10)
            
            sftp = ssh.open_sftp()
            
            # Handle directory copying
            if os.path.isdir(local_path):
                # Create remote directory
                invoke_server_command(f"mkdir -p {remote_path}", config)
                
                # Copy files recursively
                for root, dirs, files in os.walk(local_path):
                    for file in files:
                        local_file = os.path.join(root, file)
                        rel_path = os.path.relpath(local_file, local_path)
                        remote_file = os.path.join(remote_path, rel_path).replace('\\', '/')
                        remote_dir = os.path.dirname(remote_file)
                        invoke_server_command(f"mkdir -p {remote_dir}", config)
                        sftp.put(local_file, remote_file)
            else:
                sftp.put(local_path, remote_path)
            
            sftp.close()
            ssh.close()
            return True
        except Exception as e:
            print(f"Error copying files: {e}")
            return False
    else:
        if password:
            print("Warning: Password-based SCP requires paramiko. Install with: pip install paramiko")
            return False
        
        scp_cmd = ['scp', '-P', str(port), '-r', local_path, f"{ssh_command}:{remote_path}"]
    
    result = subprocess.run(scp_cmd, capture_output=True, text=True)
    return result.returncode == 0


def copy_from_server(remote_path: str, local_path: str, config: Optional[Dict[str, str]] = None) -> bool:
    """Copy files from the remote server via SCP"""
    if config is None:
        config = get_server_config()
    
    host = config.get('SERVER_HOST')
    user = config.get('SERVER_USER')
    password = config.get('SERVER_PASSWORD')
    port = int(config.get('SERVER_PORT', 22))
    ssh_key_path = config.get('SSH_KEY_PATH')
    
    ssh_command = f"{user}@{host}"
    
    if ssh_key_path and os.path.exists(os.path.expanduser(ssh_key_path)):
        scp_cmd = [
            'scp',
            '-i', os.path.expanduser(ssh_key_path),
            '-P', str(port),
            '-r',
            f"{ssh_command}:{remote_path}",
            local_path
        ]
    elif HAS_PARAMIKO and password:
        # Use paramiko for password-based SCP
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=port, username=user, password=password, timeout=10)
            
            sftp = ssh.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            ssh.close()
            return True
        except Exception as e:
            print(f"Error copying files: {e}")
            return False
    else:
        if password:
            print("Warning: Password-based SCP requires paramiko. Install with: pip install paramiko")
            return False
        
        scp_cmd = ['scp', '-P', str(port), '-r', f"{ssh_command}:{remote_path}", local_path]
    
    result = subprocess.run(scp_cmd, capture_output=True, text=True)
    return result.returncode == 0


if __name__ == "__main__":
    # Test connection
    config = get_server_config()
    print(f"Testing connection to {config.get('SERVER_USER')}@{config.get('SERVER_HOST')}...")
    
    exit_code, stdout, stderr = invoke_server_command("echo 'Connection test successful'", config)
    
    if exit_code == 0:
        print("✅ Connection successful!")
        print(stdout)
    else:
        print("❌ Connection failed!")
        print(stderr)

