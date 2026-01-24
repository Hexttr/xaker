# Server Utilities Module
# Provides functions for secure server access
# Reads credentials from .server-config.local file

function Get-ServerConfig {
    <#
    .SYNOPSIS
    Reads server configuration from .server-config.local file
    #>
    $configFile = Join-Path $PSScriptRoot ".." ".server-config.local"
    
    if (-not (Test-Path $configFile)) {
        Write-Error "Configuration file not found: $configFile"
        Write-Host "Please copy .server-config.local.example to .server-config.local and fill in your credentials"
        exit 1
    }
    
    $config = @{}
    Get-Content $configFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $config[$key] = $value
        }
    }
    
    return $config
}

function Invoke-ServerCommand {
    <#
    .SYNOPSIS
    Executes a command on the remote server via SSH
    .PARAMETER Command
    The command to execute
    .PARAMETER Config
    Server configuration (optional, will be loaded if not provided)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Command,
        [hashtable]$Config = $null
    )
    
    if ($null -eq $Config) {
        $Config = Get-ServerConfig
    }
    
    $host = $Config.SERVER_HOST
    $user = $Config.SERVER_USER
    $password = $Config.SERVER_PASSWORD
    $port = if ($Config.SERVER_PORT) { $Config.SERVER_PORT } else { 22 }
    
    # Use plink (PuTTY) for password-based SSH on Windows
    # Alternative: use sshpass or SSH key-based auth
    $plinkPath = "plink.exe"
    
    if (-not (Get-Command $plinkPath -ErrorAction SilentlyContinue)) {
        # Try using native SSH if available (Windows 10+)
        if (Get-Command ssh -ErrorAction SilentlyContinue) {
            # Use SSH with password via expect-like approach or key
            if ($Config.SSH_KEY_PATH) {
                $sshKey = $Config.SSH_KEY_PATH
                $result = & ssh -i $sshKey -p $port -o StrictHostKeyChecking=no "$user@$host" $Command 2>&1
            } else {
                Write-Warning "SSH key not configured. Install plink.exe or configure SSH_KEY_PATH"
                Write-Warning "For now, you can manually SSH: ssh $user@$host"
                return $null
            }
        } else {
            Write-Error "Neither plink.exe nor ssh found. Please install PuTTY or use OpenSSH"
            return $null
        }
    } else {
        # Use plink with password
        $result = echo y | & $plinkPath -ssh -P $port -pw $password "$user@$host" $Command 2>&1
    }
    
    return $result
}

function Copy-ToServer {
    <#
    .SYNOPSIS
    Copies files to the remote server via SCP
    .PARAMETER LocalPath
    Local file or directory path
    .PARAMETER RemotePath
    Remote destination path
    .PARAMETER Config
    Server configuration (optional)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$LocalPath,
        [Parameter(Mandatory=$true)]
        [string]$RemotePath,
        [hashtable]$Config = $null
    )
    
    if ($null -eq $Config) {
        $Config = Get-ServerConfig
    }
    
    $host = $Config.SERVER_HOST
    $user = $Config.SERVER_USER
    $password = $Config.SERVER_PASSWORD
    $port = if ($Config.SERVER_PORT) { $Config.SERVER_PORT } else { 22 }
    
    # Use pscp (PuTTY) for password-based SCP on Windows
    $pscpPath = "pscp.exe"
    
    if (-not (Get-Command $pscpPath -ErrorAction SilentlyContinue)) {
        # Try using native SCP if available
        if (Get-Command scp -ErrorAction SilentlyContinue) {
            if ($Config.SSH_KEY_PATH) {
                $sshKey = $Config.SSH_KEY_PATH
                & scp -i $sshKey -P $port -r "$LocalPath" "$user@$host`:$RemotePath" 2>&1
            } else {
                Write-Warning "SSH key not configured. Install pscp.exe or configure SSH_KEY_PATH"
                return $false
            }
        } else {
            Write-Error "Neither pscp.exe nor scp found. Please install PuTTY or use OpenSSH"
            return $false
        }
    } else {
        # Use pscp with password
        & $pscpPath -P $port -pw $password -r "$LocalPath" "$user@$host`:$RemotePath" 2>&1
    }
    
    return $true
}

function Copy-FromServer {
    <#
    .SYNOPSIS
    Copies files from the remote server via SCP
    .PARAMETER RemotePath
    Remote file or directory path
    .PARAMETER LocalPath
    Local destination path
    .PARAMETER Config
    Server configuration (optional)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$RemotePath,
        [Parameter(Mandatory=$true)]
        [string]$LocalPath,
        [hashtable]$Config = $null
    )
    
    if ($null -eq $Config) {
        $Config = Get-ServerConfig
    }
    
    $host = $Config.SERVER_HOST
    $user = $Config.SERVER_USER
    $password = $Config.SERVER_PASSWORD
    $port = if ($Config.SERVER_PORT) { $Config.SERVER_PORT } else { 22 }
    
    $pscpPath = "pscp.exe"
    
    if (-not (Get-Command $pscpPath -ErrorAction SilentlyContinue)) {
        if (Get-Command scp -ErrorAction SilentlyContinue) {
            if ($Config.SSH_KEY_PATH) {
                $sshKey = $Config.SSH_KEY_PATH
                & scp -i $sshKey -P $port -r "$user@$host`:$RemotePath" "$LocalPath" 2>&1
            } else {
                Write-Warning "SSH key not configured. Install pscp.exe or configure SSH_KEY_PATH"
                return $false
            }
        } else {
            Write-Error "Neither pscp.exe nor scp found. Please install PuTTY or use OpenSSH"
            return $false
        }
    } else {
        & $pscpPath -P $port -pw $password -r "$user@$host`:$RemotePath" "$LocalPath" 2>&1
    }
    
    return $true
}

# Export functions
Export-ModuleMember -Function Get-ServerConfig, Invoke-ServerCommand, Copy-ToServer, Copy-FromServer

