import { Router, Request, Response } from 'express';
import { serviceService } from '../services/service.service';
import { CreateServiceRequest, UpdateServiceRequest } from '../types/service';

const router = Router();

// Получить все сервисы
router.get('/', (req: Request, res: Response) => {
  try {
    const services = serviceService.getAllServices();
    res.json(services);
  } catch (error: any) {
    console.error('Ошибка при получении сервисов:', error);
    res.status(500).json({ 
      error: 'Ошибка при получении сервисов',
      details: error?.message || String(error)
    });
  }
});

// Получить сервис по ID
router.get('/:id', (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const service = serviceService.getService(id);
    if (!service) {
      return res.status(404).json({ error: 'Сервис не найден' });
    }
    res.json(service);
  } catch (error: any) {
    console.error('Ошибка при получении сервиса:', error);
    res.status(500).json({ 
      error: 'Ошибка при получении сервиса',
      details: error?.message || String(error)
    });
  }
});

// Создать новый сервис
router.post('/', (req: Request, res: Response) => {
  try {
    const { name, url } = req.body;

    if (!name || !url) {
      return res.status(400).json({ 
        error: 'Необходимо указать name и url' 
      });
    }

    // Валидация URL
    try {
      new URL(url);
    } catch {
      return res.status(400).json({ 
        error: 'Некорректный URL' 
      });
    }

    const service = serviceService.createService({ name, url });
    res.status(201).json(service);
  } catch (error: any) {
    console.error('Ошибка при создании сервиса:', error);
    res.status(500).json({ 
      error: 'Ошибка при создании сервиса',
      details: error?.message || String(error)
    });
  }
});

// Обновить сервис
router.put('/:id', (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { name, url } = req.body;

    const updateData: UpdateServiceRequest = {};
    if (name !== undefined) updateData.name = name;
    if (url !== undefined) {
      // Валидация URL
      try {
        new URL(url);
        updateData.url = url;
      } catch {
        return res.status(400).json({ 
          error: 'Некорректный URL' 
        });
      }
    }

    const service = serviceService.updateService(id, updateData);
    if (!service) {
      return res.status(404).json({ error: 'Сервис не найден' });
    }
    res.json(service);
  } catch (error: any) {
    console.error('Ошибка при обновлении сервиса:', error);
    res.status(500).json({ 
      error: 'Ошибка при обновлении сервиса',
      details: error?.message || String(error)
    });
  }
});

// Удалить сервис
router.delete('/:id', (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const deleted = serviceService.deleteService(id);
    if (!deleted) {
      return res.status(404).json({ error: 'Сервис не найден' });
    }
    res.json({ message: 'Сервис удален' });
  } catch (error: any) {
    console.error('Ошибка при удалении сервиса:', error);
    res.status(500).json({ 
      error: 'Ошибка при удалении сервиса',
      details: error?.message || String(error)
    });
  }
});

export default router;

