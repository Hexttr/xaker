import rateLimit from 'express-rate-limit';

/**
 * Rate limiting для логина (защита от брутфорса)
 * 5 попыток в минуту
 */
export const loginRateLimit = rateLimit({
  windowMs: 60 * 1000, // 1 минута
  max: 5, // максимум 5 запросов
  message: {
    error: 'Слишком много попыток входа',
    message: 'Пожалуйста, попробуйте снова через минуту',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

