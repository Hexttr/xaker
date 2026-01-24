# Исправление конфигурации Nginx для проксирования API
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔧 Исправление конфигурации Nginx...`n" -ForegroundColor Cyan

# Создаем правильную конфигурацию
$nginxConfig = @"
server {
    listen 80;
    server_name pentest.red www.pentest.red;
    return 301 https://`$host`$request_uri;
}

server {
    listen 443 ssl http2;
    server_name pentest.red www.pentest.red;

    ssl_certificate /etc/letsencrypt/live/pentest.red/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pentest.red/privkey.pem;

    access_log /var/log/nginx/pentest.red.access.log;
    error_log /var/log/nginx/pentest.red.error.log;

    # API проксирование - ДОЛЖНО БЫТЬ ПЕРВЫМ!
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade `$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
        proxy_cache_bypass `$http_upgrade;
    }

    # Frontend приложение
    location /app {
        alias /var/www/pentest.red/app;
        try_files `$uri `$uri/ /app/index.html;
        index index.html;
    }

    # Landing page
    location / {
        root /var/www/pentest.red/landing;
        try_files `$uri `$uri/ /index.html;
        index index.html;
    }
}
"@

# Сохраняем конфигурацию во временный файл
$tempFile = [System.IO.Path]::GetTempFileName()
$nginxConfig | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "1. Копируем конфигурацию на сервер..." -ForegroundColor Yellow
$pscp = "C:\Program Files\PuTTY\pscp.exe"
& $pscp -pw $password -hostkey $hostkey $tempFile "$server`:/tmp/nginx-pentest.conf"

Write-Host "2. Проверяем синтаксис..." -ForegroundColor Yellow
$cmd1 = "sudo cp /tmp/nginx-pentest.conf /etc/nginx/sites-available/pentest.red && sudo nginx -t"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

Write-Host "3. Перезагружаем Nginx..." -ForegroundColor Yellow
$cmd2 = "sudo systemctl reload nginx"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

Remove-Item $tempFile -Force

Write-Host "`n✅ Конфигурация Nginx обновлена!`n" -ForegroundColor Green

