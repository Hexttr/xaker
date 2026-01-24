import { Router, Request, Response } from 'express';
import { userService } from '../services/user.service';
import { generateToken } from '../utils/jwt.util';
import { loginRateLimit } from '../middleware/rateLimit.middleware';
import { LoginRequest, LoginResponse } from '../types/user';

const router = Router();

/**
 * POST /api/auth/login
 * Аутентификация пользователя
 */
router.post('/login', loginRateLimit, async (req: Request, res: Response) => {
  try {
    const { username, password }: LoginRequest = req.body;

    // Валидация
    if (!username || !password) {
      return res.status(400).json({
        success: false,
        error: 'Необходимо указать username и password',
      } as LoginResponse);
    }

    // Находим пользователя
    const user = await userService.findByUsername(username);
    if (!user) {
      return res.status(401).json({
        success: false,
        error: 'Неверный username или password',
      } as LoginResponse);
    }

    // Проверяем пароль
    const isValidPassword = await userService.verifyPassword(user, password);
    if (!isValidPassword) {
      return res.status(401).json({
        success: false,
        error: 'Неверный username или password',
      } as LoginResponse);
    }

    // Генерируем JWT токен
    const token = generateToken(user.id, user.username);

    console.log(`✅ Успешный вход: ${username}`);

    res.json({
      success: true,
      token,
      user: {
        id: user.id,
        username: user.username,
      },
    } as LoginResponse);
  } catch (error: any) {
    console.error('❌ Ошибка при входе:', error);
    res.status(500).json({
      success: false,
      error: 'Ошибка при входе',
      details: error?.message || String(error),
    } as LoginResponse);
  }
});

/**
 * GET /api/auth/verify
 * Проверка валидности токена
 */
router.get('/verify', async (req: Request, res: Response) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        valid: false,
        error: 'Токен не предоставлен',
      });
    }

    const token = authHeader.substring(7);
    const { verifyToken } = require('../utils/jwt.util');
    const decoded = verifyToken(token);

    if (!decoded) {
      return res.status(401).json({
        valid: false,
        error: 'Невалидный или истекший токен',
      });
    }

    // Проверяем, существует ли пользователь
    const user = await userService.findById(decoded.userId);
    if (!user) {
      return res.status(401).json({
        valid: false,
        error: 'Пользователь не найден',
      });
    }

    res.json({
      valid: true,
      user: {
        id: user.id,
        username: user.username,
      },
    });
  } catch (error: any) {
    console.error('❌ Ошибка при проверке токена:', error);
    res.status(500).json({
      valid: false,
      error: 'Ошибка при проверке токена',
    });
  }
});

export default router;

