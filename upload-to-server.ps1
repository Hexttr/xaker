# Скрипт для загрузки файлов на сервер
$plink = "C:\Program Files\PuTTY\plink.exe"
$pscp = "C:\Program Files\PuTTY\pscp.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"
$remotePath = "/opt/xaker"

Write-Host "Загрузка файлов на сервер..." -ForegroundColor Cyan

# Создаем список файлов для загрузки (исключая node_modules, .git и т.д.)
$filesToUpload = @(
    "backend",
    "frontend", 
    "docs",
    "*.sh",
    "*.md",
    "package.json",
    "package-lock.json"
)

# Загружаем основные файлы
foreach ($item in $filesToUpload) {
    $localPath = Join-Path $PSScriptRoot $item
    if (Test-Path $localPath) {
        Write-Host "Загрузка: $item" -ForegroundColor Yellow
        & $pscp -pw $password -hostkey $hostkey -r $localPath "${server}:${remotePath}/"
    }
}

Write-Host "Загрузка завершена!" -ForegroundColor Green

