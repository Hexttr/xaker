# Исправление порядка location блоков в Nginx
$plink = "C:\Program Files\PuTTY\plink.exe"
$hostkey = "ssh-ed25519 255 SHA256:DGP2HvATs7KUcY8Anq/F7Q7Kvyll3BWJSZqE2zdfj78"
$server = "root@5.129.235.52"
$password = "cY7^kCCA_6uQ5S"

Write-Host "`n🔧 Исправление порядка location блоков в Nginx...`n" -ForegroundColor Cyan

# Создаем правильную конфигурацию с location /api ПЕРВЫМ
$nginxConfig = @"
server {
    server_name pentest.red www.pentest.red;

    # Логи
    access_log /var/log/nginx/pentest.red.access.log;
    error_log /var/log/nginx/pentest.red.error.log;

    # Backend API - ДОЛЖЕН БЫТЬ ПЕРВЫМ!
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

    # WebSocket для Socket.IO
    location /socket.io {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade `$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }

    # Специальная обработка для index.html - НИКОГДА не кэшировать
    location = /app/index.html {
        alias /opt/xaker/frontend/dist/index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
        add_header Last-Modified "" always;
        add_header ETag "" always;
        expires -1;
        add_header X-Content-Type-Options "nosniff" always;
    }
    
    # React приложение (SPA) - все пути начинающиеся с /app
    location /app {
        alias /opt/xaker/frontend/dist;
        try_files `$uri `$uri/ /app/index.html;
        
        # Заголовки безопасности
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        
        # CORS заголовки для модулей
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
        
        # Отключаем кэширование для HTML
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
        
        # Правильный Content-Type для JavaScript модулей
        location ~* \.js$ {
            default_type "application/javascript; charset=utf-8";
            add_header Cache-Control "no-cache, no-store, must-revalidate" always;
            add_header Pragma "no-cache" always;
            add_header Expires "0" always;
            add_header X-Content-Type-Options "nosniff" always;
        }
        
        # Отключаем кэширование для CSS
        location ~* \.css$ {
            add_header Cache-Control "no-cache, no-store, must-revalidate" always;
            add_header Pragma "no-cache" always;
            add_header Expires "0" always;
        }
        
        # Кэширование остальных статических файлов
        location ~* \.(png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            add_header Cache-Control "no-cache, no-store, must-revalidate" always;
            add_header Pragma "no-cache" always;
            add_header Expires "0" always;
        }
    }

    # Landing page (главная страница)
    location = / {
        root /var/www/pentest.red/landing;
        try_files /index.html =404;
    }

    # Статические файлы landing page (assets, images, favicon, robots.txt)
    # Только если НЕ начинается с /app или /api
    location ~ ^/(assets|images|favicon\.ico|robots\.txt|.*\.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot))$ {
        root /var/www/pentest.red/landing;
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files `$uri =404;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/pentest.red/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/pentest.red/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if (`$host = pentest.red) {
        return 301 https://`$host`$request_uri;
    } # managed by Certbot

    if (`$host = www.pentest.red) {
        return 301 https://`$host`$request_uri;
    } # managed by Certbot

    listen 80;
    server_name pentest.red www.pentest.red;
    return 404; # managed by Certbot
}
"@

# Сохраняем конфигурацию во временный файл
$tempFile = [System.IO.Path]::GetTempFileName()
$nginxConfig | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "1. Копируем конфигурацию на сервер..." -ForegroundColor Yellow
$pscp = "C:\Program Files\PuTTY\pscp.exe"
& $pscp -pw $password -hostkey $hostkey $tempFile "$server`:/tmp/nginx-pentest-fixed.conf"

Write-Host "2. Проверяем синтаксис..." -ForegroundColor Yellow
$cmd1 = "sudo cp /tmp/nginx-pentest-fixed.conf /etc/nginx/sites-available/pentest.red && sudo nginx -t"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd1

Write-Host "3. Перезагружаем Nginx..." -ForegroundColor Yellow
$cmd2 = "sudo systemctl reload nginx"
& $plink -ssh $server -pw $password -hostkey $hostkey -batch $cmd2

Remove-Item $tempFile -Force

Write-Host "`n✅ Конфигурация Nginx обновлена!`n" -ForegroundColor Green
Write-Host "Теперь /api должен работать для landing page!`n" -ForegroundColor Cyan

