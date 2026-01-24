import { Router, Request, Response } from 'express';
import { promises as fs } from 'fs';
import path from 'path';

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

// Сохранить заявку на демо
router.post('/', async (req: Request, res: Response) => {
  try {
    const { name, phone } = req.body;

    // Валидация
    if (!name || !phone) {
      return res.status(400).json({
        error: 'Необходимо указать имя и телефон',
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

    res.status(201).json({
      success: true,
      message: 'Заявка успешно отправлена',
      id: newRequest.id,
    });
  } catch (error: any) {
    console.error('❌ Ошибка при сохранении заявки:', error);
    res.status(500).json({
      error: 'Ошибка при сохранении заявки',
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
      error: 'Ошибка при чтении заявок',
      details: error?.message || String(error),
    });
  }
});

export default router;

