# Деплой Landing Page на Production

## Структура

- **Landing page**: `https://pentest.red/` → статический сайт из `landing/dist/`
- **Приложение**: `https://pentest.red/app/` → React приложение из `frontend/dist/`

## Локальная подготовка

1. Убедитесь, что файлы landing page находятся в папке `landing/`
2. Установите зависимости:
   ```bash
   cd landing
   npm install
   ```

3. Соберите проект:
   ```bash
   npm run build
   ```

## Деплой на сервер

### Вариант 1: PowerShell скрипт (Windows)

```powershell
.\deploy-landing.ps1
```

### Вариант 2: Ручной деплой

1. Соберите landing page:
   ```bash
   cd landing
   npm run build
   ```

2. Создайте архив:
   ```bash
   cd dist
   tar -czf ../../landing-dist.tar.gz .
   ```

3. Скопируйте на сервер:
   ```bash
   scp landing-dist.tar.gz root@5.129.235.52:/tmp/
   ```

4. Распакуйте на сервере:
   ```bash
   ssh root@5.129.235.52
   cd /var/www/pentest.red/landing
   rm -rf *
   tar -xzf /tmp/landing-dist.tar.gz
   chown -R www-data:www-data /var/www/pentest.red/landing
   chmod -R 755 /var/www/pentest.red/landing
   ```

## Настройка Nginx

Обновите конфигурацию `/etc/nginx/sites-available/pentest.red`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name pentest.red www.pentest.red;
    
    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name pentest.red www.pentest.red;

    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/pentest.red/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pentest.red/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Логи
    access_log /var/log/nginx/pentest.red.access.log;
    error_log /var/log/nginx/pentest.red.error.log;

    # Landing page (главная страница)
    location = / {
        root /var/www/pentest.red/landing;
        try_files /index.html =404;
    }

    # Статические файлы landing page
    location ~ ^/(assets|images|favicon\.ico|robots\.txt) {
        root /var/www/pentest.red/landing;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # React приложение (SPA) - все пути начинающиеся с /app
    location /app {
        alias /opt/xaker/frontend/dist;
        try_files $uri $uri/ /app/index.html;
        
        # Кэширование статических файлов
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket для Socket.IO
    location /socket.io {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

После обновления конфигурации:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Проверка

1. **Landing page**: Откройте `https://pentest.red/` - должна открыться главная страница
2. **Приложение**: Откройте `https://pentest.red/app/` - должно открыться React приложение
3. **API**: Проверьте `https://pentest.red/api/pentests` - должен вернуть JSON

## Обновление landing page

После изменений в коде:

1. Пересоберите:
   ```bash
   cd landing
   npm run build
   ```

2. Задеплойте:
   ```powershell
   .\deploy-landing.ps1
   ```

Или вручную скопируйте содержимое `landing/dist/` в `/var/www/pentest.red/landing/` на сервере.

