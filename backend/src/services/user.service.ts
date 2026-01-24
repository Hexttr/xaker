import { promises as fs } from 'fs';
import { join } from 'path';
import { v4 as uuidv4 } from 'uuid';
import { User } from '../types/user';
import { hashPassword, comparePassword } from '../utils/password.util';

const USERS_FILE = join(process.cwd(), 'users.json');

class UserService {
  private users: Map<string, User> = new Map();

  constructor() {
    this.loadUsers();
  }

  /**
   * Загрузить пользователей из файла
   */
  private async loadUsers(): Promise<void> {
    try {
      const data = await fs.readFile(USERS_FILE, 'utf-8');
      const users: User[] = JSON.parse(data);
      users.forEach(user => this.users.set(user.id, user));
      console.log(`✅ Загружено ${users.length} пользователей`);
    } catch (error: any) {
      if (error.code === 'ENOENT') {
        // Файл не существует, создадим при первом добавлении пользователя
        console.log('ℹ️ Файл users.json не найден, будет создан при добавлении пользователя');
      } else {
        console.error('❌ Ошибка при загрузке пользователей:', error);
      }
    }
  }

  /**
   * Сохранить пользователей в файл
   */
  private async saveUsers(): Promise<void> {
    try {
      const users = Array.from(this.users.values());
      await fs.writeFile(USERS_FILE, JSON.stringify(users, null, 2), 'utf-8');
    } catch (error) {
      console.error('❌ Ошибка при сохранении пользователей:', error);
      throw error;
    }
  }

  /**
   * Найти пользователя по username
   */
  async findByUsername(username: string): Promise<User | null> {
    const user = Array.from(this.users.values()).find(
      u => u.username.toLowerCase() === username.toLowerCase()
    );
    return user || null;
  }

  /**
   * Найти пользователя по ID
   */
  async findById(id: string): Promise<User | null> {
    return this.users.get(id) || null;
  }

  /**
   * Проверить пароль
   */
  async verifyPassword(user: User, password: string): Promise<boolean> {
    return comparePassword(password, user.passwordHash);
  }

  /**
   * Создать нового пользователя
   */
  async createUser(username: string, password: string): Promise<User> {
    // Проверяем, не существует ли уже такой username
    const existing = await this.findByUsername(username);
    if (existing) {
      throw new Error('Пользователь с таким username уже существует');
    }

    const passwordHash = await hashPassword(password);
    const user: User = {
      id: uuidv4(),
      username,
      passwordHash,
      createdAt: new Date().toISOString(),
    };

    this.users.set(user.id, user);
    await this.saveUsers();

    console.log(`✅ Пользователь создан: ${username}`);
    return user;
  }

  /**
   * Получить всех пользователей (для админки, опционально)
   */
  getAllUsers(): User[] {
    return Array.from(this.users.values());
  }
}

export const userService = new UserService();

