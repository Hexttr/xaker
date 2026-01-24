# 🔐 Руководство по работе с сервером

## Быстрый старт

1. **Создайте конфигурационный файл:**
   ```bash
   cp .server-config.local.example .server-config.local
   ```

2. **Отредактируйте `.server-config.local`** и заполните ваши SSH данные:
   ```bash
   SERVER_HOST=5.129.235.52
   SERVER_USER=root
   SERVER_PASSWORD=your_password_here
   ```

3. **Используйте скрипты для работы с сервером:**
   ```powershell
   # Подключиться к серверу
   .\scripts\connect-server.ps1
   
   # Проверить статус
   .\scripts\server-status.ps1
   
   # Задеплоить backend
   .\scripts\deploy-backend.ps1
   
   # Задеплоить frontend
   .\scripts\deploy-frontend.ps1
   ```

## Безопасность

### ✅ Рекомендуется: SSH ключи

1. **Сгенерируйте SSH ключ** (если еще нет):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **Скопируйте публичный ключ на сервер:**
   ```bash
   ssh-copy-id -p 22 root@5.129.235.52
   ```

3. **Укажите путь к ключу в `.server-config.local`:**
   ```bash
   SSH_KEY_PATH=~/.ssh/id_ed25519
   ```

### ⚠️ Альтернатива: Пароли

Если используете пароли, установите `paramiko` для Python:
```bash
pip install paramiko
```

Или используйте PuTTY на Windows:
- Скачайте PuTTY: https://www.putty.org/
- Добавьте `plink.exe` и `pscp.exe` в PATH

## Доступные скрипты

### PowerShell (Windows)

- `scripts/connect-server.ps1` - Подключение к серверу по SSH
- `scripts/server-status.ps1` - Проверка статуса сервера
- `scripts/deploy-backend.ps1` - Деплой backend
- `scripts/deploy-frontend.ps1` - Деплой frontend
- `scripts/server-utils.ps1` - Утилиты для работы с сервером

### Python (кроссплатформенный)

- `scripts/server-utils.py` - Модуль утилит для работы с сервером

Использование в Python:
```python
from scripts.server_utils import get_server_config, invoke_server_command

config = get_server_config()
exit_code, stdout, stderr = invoke_server_command("ls -la", config)
print(stdout)
```

## Структура конфигурации

Файл `.server-config.local` содержит:

```bash
# Сервер
SERVER_HOST=5.129.235.52
SERVER_USER=root
SERVER_PASSWORD=your_password
SERVER_PORT=22

# SSH ключ (опционально, приоритет над паролем)
SSH_KEY_PATH=~/.ssh/id_ed25519

# Директории на сервере
SERVER_PROJECT_DIR=/root/xaker
SERVER_BACKEND_DIR=/root/xaker/backend
SERVER_FRONTEND_DIR=/root/xaker/frontend
SERVER_LANDING_DIR=/var/www/pentest.red/landing

# Локальные директории
LOCAL_BACKEND_DIR=backend
LOCAL_FRONTEND_DIR=frontend
LOCAL_LANDING_DIR=landing
```

## Примеры использования

### Выполнить команду на сервере

**PowerShell:**
```powershell
. .\scripts\server-utils.ps1
$config = Get-ServerConfig
Invoke-ServerCommand -Command "pm2 list" -Config $config
```

**Python:**
```python
from scripts.server_utils import get_server_config, invoke_server_command

config = get_server_config()
exit_code, stdout, stderr = invoke_server_command("pm2 list", config)
print(stdout)
```

### Скопировать файлы на сервер

**PowerShell:**
```powershell
. .\scripts\server-utils.ps1
$config = Get-ServerConfig
Copy-ToServer -LocalPath "backend\dist" -RemotePath "/root/xaker/backend/dist" -Config $config
```

**Python:**
```python
from scripts.server_utils import get_server_config, copy_to_server

config = get_server_config()
copy_to_server("backend/dist", "/root/xaker/backend/dist", config)
```

## Устранение проблем

### Ошибка: "Configuration file not found"
- Убедитесь, что файл `.server-config.local` существует
- Скопируйте из `.server-config.local.example`

### Ошибка: "SSH not found"
- Windows: Установите OpenSSH или PuTTY
- Linux/Mac: Обычно OpenSSH уже установлен

### Ошибка: "Permission denied"
- Проверьте правильность пароля/ключа
- Убедитесь, что пользователь имеет доступ к серверу

### Ошибка: "paramiko not found" (при использовании паролей)
```bash
pip install paramiko
```

## Важные замечания

1. **Файл `.server-config.local` НЕ коммитится в git** (в .gitignore)
2. **Каждый разработчик создает свой `.server-config.local`** локально
3. **SSH ключи безопаснее паролей** - используйте их когда возможно
4. **Не делитесь `.server-config.local`** с другими людьми

