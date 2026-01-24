import { Request, Response, NextFunction } from 'express';
import { verifyToken, JWTPayload } from '../utils/jwt.util';

// Расширяем Request для добавления userId
declare global {
  namespace Express {
    interface Request {
      userId?: string;
      username?: string;
    }
  }
}

/**
 * Middleware для проверки JWT токена
 */
export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  // Получаем токен из заголовка Authorization
  const authHeader = req.headers.authorization;
  
  console.log(`[authMiddleware] ${req.method} ${req.path} - Authorization header:`, authHeader ? 'present' : 'missing');
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    console.log(`[authMiddleware] 401 - Токен не предоставлен для ${req.path}`);
    return res.status(401).json({
      error: 'Токен не предоставлен',
      message: 'Необходима аутентификация',
    });
  }

  const token = authHeader.substring(7); // Убираем "Bearer "

  // Проверяем токен
  const decoded = verifyToken(token);
  
  if (!decoded) {
    console.log(`[authMiddleware] 401 - Невалидный токен для ${req.path}`);
    return res.status(401).json({
      error: 'Невалидный или истекший токен',
      message: 'Требуется повторная аутентификация',
    });
  }

  // Добавляем userId и username в request
  req.userId = decoded.userId;
  req.username = decoded.username;
  console.log(`[authMiddleware] ✅ Токен валиден для пользователя: ${decoded.username}`);

  next();
};

