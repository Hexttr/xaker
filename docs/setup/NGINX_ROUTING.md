# Настройка Nginx для разделения Landing Page и приложения

## Обзор

После настройки приложение будет доступно по адресу `https://pentest.red/app/`, а главная страница (`/`) будет отдавать статический landing page.

## Структура роутинга

- `/` → Статический landing page (HTML/CSS/JS)
- `/app/*` → React приложение (SPA)
- `/api/*` → Backend API (проксирование на Node.js)
- `/socket.io/*` → WebSocket соединения (проксирование на Node.js)

## Настройка Nginx

### 1. Создайте директорию для landing page

```bash
sudo mkdir -p /var/www/pentest.red/landing
sudo chown -R $USER:$USER /var/www/pentest.red/landing
```

### 2. Обновите конфигурацию Nginx

Отредактируйте файл `/etc/nginx/sites-available/pentest.red`:

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

    # SSL сертификаты (Certbot)
    ssl_certificate /etc/letsencrypt/live/pentest.red/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pentest.red/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Корневая директория для landing page
    root /var/www/pentest.red/landing;
    index index.html;

    # Логи
    access_log /var/log/nginx/pentest.red.access.log;
    error_log /var/log/nginx/pentest.red.error.log;

    # Landing page (главная страница)
    location = / {
        try_files /index.html =404;
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

    # Статические файлы для landing page
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Проверьте конфигурацию и перезагрузите Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Создание Landing Page

### Минимальный пример `index.html`

Создайте файл `/var/www/pentest.red/landing/index.html`:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pentest.Red - Платформа для пентестинга</title>
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .container {
            max-width: 800px;
            text-align: center;
        }
        
        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        p {
            font-size: 1.25rem;
            margin-bottom: 2rem;
            color: #a0a0a0;
        }
        
        .btn {
            display: inline-block;
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: #fff;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Pentest.Red</h1>
        <p>Профессиональная платформа для автоматизированного пентестинга</p>
        <a href="/app" class="btn">Перейти в приложение</a>
    </div>
</body>
</html>
```

## Проверка работы

1. **Landing page**: Откройте `https://pentest.red/` - должна открыться главная страница
2. **Приложение**: Откройте `https://pentest.red/app/` - должно открыться React приложение
3. **API**: Проверьте `https://pentest.red/api/pentests` - должен вернуть JSON

## Важные замечания

1. **Пути в React приложении**: Все внутренние ссылки в React приложении будут работать автоматически благодаря `basename="/app"` в Router
2. **API запросы**: Axios и другие HTTP клиенты должны использовать абсолютные пути `/api/...` (они будут работать корректно)
3. **Socket.IO**: WebSocket соединения также будут работать через `/socket.io`
4. **Пересборка**: После изменений в React приложении нужно пересобрать:
   ```bash
   cd /opt/xaker/frontend
   npm run build
   sudo systemctl reload nginx
   ```

## Альтернатива: Поддомен

Если предпочтете использовать поддомен (например, `app.pentest.red`):

1. Добавьте A-запись в DNS: `app.pentest.red` → IP сервера
2. Создайте отдельный server block в Nginx для `app.pentest.red`
3. Уберите `base: '/app/'` из `vite.config.ts` и `basename` из `App.tsx`
4. Настройте Certbot для нового поддомена: `sudo certbot --nginx -d app.pentest.red`


