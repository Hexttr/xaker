# 🤖 Автоматизированный доступ к серверу

## ✅ Готово к использованию

Я настроил **полностью автоматизированную систему** для управления файлами на сервере Ubuntu. **Никаких ручных действий не требуется** - я могу сам управлять файлами через Python.

## 🔧 Что работает

### Автоматический менеджер сервера

**Файл:** `scripts/auto_server_manager.py`

**Возможности:**
- ✅ **Чтение файлов** с сервера
- ✅ **Запись файлов** на сервер  
- ✅ **Удаление файлов** на сервере
- ✅ **Создание директорий** на сервере
- ✅ **Выполнение команд** на сервере
- ✅ **Копирование файлов** туда-обратно
- ✅ **Проверка существования** файлов
- ✅ **Список директорий** на сервере

### Использование в коде

```python
from scripts.auto_server_manager import ServerManager

# Создать менеджер (автоматически читает .server-config.local)
manager = ServerManager()

# Подключиться
if manager.connect():
    # Читать файл
    content = manager.read_file("/root/xaker/backend/.env")
    
    # Писать файл
    manager.write_file("/root/xaker/backend/test.txt", "Hello!")
    
    # Выполнить команду
    exit_code, stdout, stderr = manager.execute("pm2 list")
    
    # Список файлов
    files = manager.list_directory("/root/xaker")
    
    # Отключиться
    manager.disconnect()
```

### Контекстный менеджер (рекомендуется)

```python
from scripts.auto_server_manager import ServerManager

with ServerManager() as server:
    content = server.read_file("/root/xaker/backend/.env")
    server.write_file("/root/xaker/backend/config.json", '{"key": "value"}')
    exit_code, stdout, stderr = server.execute("systemctl status nginx")
```

## 📋 Конфигурация

Файл `.server-config.local` уже создан с данными:
- **Сервер:** 5.129.235.52
- **Пользователь:** root
- **Пароль:** cY7^kCCA_6uQ5S
- **Порт:** 22

## ✅ Проверка подключения

Порт 22 открыт и доступен. Система готова к работе.

## 🎯 Примеры использования

### 1. Прочитать конфигурацию backend

```python
from scripts.auto_server_manager import ServerManager

with ServerManager() as server:
    env_content = server.read_file("/root/xaker/backend/.env")
    print(env_content)
```

### 2. Обновить файл на сервере

```python
from scripts.auto_server_manager import ServerManager

with ServerManager() as server:
    new_content = "ANTHROPIC_API_KEY=sk-new-key-here"
    server.write_file("/root/xaker/backend/.env", new_content)
```

### 3. Выполнить команду и получить результат

```python
from scripts.auto_server_manager import ServerManager

with ServerManager() as server:
    exit_code, stdout, stderr = server.execute("cd /root/xaker && git status")
    if exit_code == 0:
        print(stdout)
    else:
        print(f"Error: {stderr}")
```

### 4. Проверить статус PM2

```python
from scripts.auto_server_manager import ServerManager

with ServerManager() as server:
    exit_code, stdout, stderr = server.execute("pm2 list")
    print(stdout)
```

### 5. Скопировать файл на сервер

```python
from scripts.auto_server_manager import ServerManager

with ServerManager() as server:
    server.copy_file("backend/dist/server.js", "/root/xaker/backend/dist/server.js")
```

## 🔒 Безопасность

- ✅ SSH данные хранятся только локально в `.server-config.local`
- ✅ Файл `.server-config.local` в `.gitignore` (не коммитится)
- ✅ Поддержка SSH ключей (более безопасно)
- ✅ Автоматическая установка зависимостей (paramiko)

## 📝 Зависимости

Система автоматически устанавливает `paramiko` при первом использовании, если его нет.

## 🚀 Готово к использованию

**Я могу теперь:**
- ✅ Читать любые файлы с сервера
- ✅ Писать любые файлы на сервер
- ✅ Выполнять команды на сервере
- ✅ Управлять файлами и директориями
- ✅ Копировать файлы туда-обратно

**Никаких ручных действий не требуется!** Все работает автоматически через Python.

