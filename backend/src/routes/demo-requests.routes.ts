import { Router, Request, Response } from 'express';
import { promises as fs } from 'fs';
import path from 'path';
import fetch from 'node-fetch';

const router = Router();

// Путь к файлу для хранения заявок
const DEMO_REQUESTS_FILE = path.join(process.cwd(), 'demo-requests.json');

// Убедимся, что файл существует
async function ensureFileExists() {
  try {
    await fs.access(DEMO_REQUESTS_FILE);
  } catch {
    // Файл не существует, создаем его с пустым массивом
    await fs.writeFile(DEMO_REQUESTS_FILE, JSON.stringify([], null, 2), 'utf-8');
  }
}

// Отправить уведомление в Telegram
async function sendTelegramNotification(name: string, phone: string) {
  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  if (!botToken || !chatId) {
    console.log('⚠️ Telegram не настроен: TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не установлены');
    return;
  }

  try {
    const message = `🆕 *New Demo Request*\n\n` +
      `👤 *Name:* ${name}\n` +
      `📞 *Phone:* ${phone}\n` +
      `🕐 *Time:* ${new Date().toLocaleString('en-US', { timeZone: 'UTC' })} UTC`;

    const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: 'Markdown',
      }),
    });

    if (response.ok) {
      console.log('✅ Уведомление отправлено в Telegram');
    } else {
      const error = await response.text();
      console.error('❌ Ошибка отправки в Telegram:', error);
    }
  } catch (error: any) {
    console.error('❌ Ошибка при отправке в Telegram:', error?.message || error);
  }
}

// Сохранить заявку на демо
router.post('/', async (req: Request, res: Response) => {
  try {
    const { name, phone } = req.body;

    // Валидация
    if (!name || !phone) {
      return res.status(400).json({
        error: 'Name and phone are required',
      });
    }

    // Убедимся, что файл существует
    await ensureFileExists();

    // Читаем существующие заявки
    const fileContent = await fs.readFile(DEMO_REQUESTS_FILE, 'utf-8');
    const requests = JSON.parse(fileContent);

    // Добавляем новую заявку
    const newRequest = {
      id: Date.now().toString(),
      name: name.trim(),
      phone: phone.trim(),
      timestamp: new Date().toISOString(),
      status: 'new',
    };

    requests.push(newRequest);

    // Сохраняем обратно в файл
    await fs.writeFile(DEMO_REQUESTS_FILE, JSON.stringify(requests, null, 2), 'utf-8'));

    console.log(`✅ Новая заявка на демо: ${name} - ${phone}`);

    // Отправляем уведомление в Telegram (не блокируем ответ)
    sendTelegramNotification(name, phone).catch(err => {
      console.error('Ошибка отправки Telegram (не критично):', err);
    });

    res.status(201).json({
      success: true,
      message: 'Request submitted successfully',
      id: newRequest.id,
    });
  } catch (error: any) {
    console.error('❌ Ошибка при сохранении заявки:', error);
    res.status(500).json({
      error: 'Error saving request',
      details: error?.message || String(error),
    });
  }
});

// Получить все заявки (для админки, опционально)
router.get('/', async (req: Request, res: Response) => {
  try {
    await ensureFileExists();
    const fileContent = await fs.readFile(DEMO_REQUESTS_FILE, 'utf-8');
    const requests = JSON.parse(fileContent);
    res.json(requests);
  } catch (error: any) {
    console.error('❌ Ошибка при чтении заявок:', error);
    res.status(500).json({
      error: 'Error reading requests',
      details: error?.message || String(error),
    });
  }
});

export default router;

