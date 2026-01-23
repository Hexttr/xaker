# Скрипт для подключения к серверу
$server = "5.129.235.52"
$user = "root"
$password = "cY7^kCCA_6uQ5S"
$puttyPath = "C:\Program Files\PuTTY\plink.exe"

Write-Host "Подключение к серверу $server..." -ForegroundColor Cyan

# Принимаем host key автоматически при первом подключении
& $puttyPath -ssh "$user@$server" -pw $password -batch "echo 'Connected successfully'"

