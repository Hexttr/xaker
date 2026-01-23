# Хелпер для выполнения команд на сервере
param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

& $plink -ssh $server -pw $password -hostkey $hostkey $Command

