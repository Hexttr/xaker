# Скрипт для добавления пользователя
param(
    [Parameter(Mandatory=$true)]
    [string]$Username,
    [Parameter(Mandatory=$true)]
    [string]$Password
)

Write-Host "🔐 Добавление пользователя..." -ForegroundColor Cyan
Write-Host "Username: $Username" -ForegroundColor Yellow

# Переходим в директорию backend
$backendDir = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path $backendDir)) {
    Write-Host "❌ Директория backend не найдена!" -ForegroundColor Red
    exit 1
}

Set-Location $backendDir

# Проверяем наличие Node.js
$nodeVersion = node --version 2>$null
if (-not $nodeVersion) {
    Write-Host "❌ Node.js не найден!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Node.js найден: $nodeVersion" -ForegroundColor Green

# Создаем временный скрипт для добавления пользователя
$scriptContent = @"
const bcrypt = require('bcrypt');
const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const USERS_FILE = path.join(process.cwd(), 'users.json');
const SALT_ROUNDS = 10;

async function addUser() {
  try {
    const username = '$Username';
    const password = '$Password';

    // Загружаем существующих пользователей
    let users = [];
    try {
      const data = await fs.readFile(USERS_FILE, 'utf-8');
      users = JSON.parse(data);
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      // Файл не существует, создадим новый
    }

    // Проверяем, не существует ли уже такой username
    const existing = users.find(u => u.username.toLowerCase() === username.toLowerCase());
    if (existing) {
      console.error('❌ Пользователь с таким username уже существует');
      process.exit(1);
    }

    // Хешируем пароль
    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);

    // Создаем пользователя
    const user = {
      id: uuidv4(),
      username: username,
      passwordHash: passwordHash,
      createdAt: new Date().toISOString(),
    };

    users.push(user);

    // Сохраняем
    await fs.writeFile(USERS_FILE, JSON.stringify(users, null, 2), 'utf-8');

    console.log('✅ Пользователь успешно добавлен!');
    console.log('   ID:', user.id);
    console.log('   Username:', user.username);
    console.log('   Created:', user.createdAt);
  } catch (error) {
    console.error('❌ Ошибка:', error.message);
    process.exit(1);
  }
}

addUser();
"@

$tempScript = [System.IO.Path]::GetTempFileName() + ".js"
$scriptContent | Out-File -FilePath $tempScript -Encoding UTF8

try {
    Write-Host "`n🔄 Хеширование пароля и создание пользователя..." -ForegroundColor Yellow
    node $tempScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Пользователь добавлен успешно!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Ошибка при добавлении пользователя" -ForegroundColor Red
        exit 1
    }
} finally {
    Remove-Item $tempScript -ErrorAction SilentlyContinue
}

