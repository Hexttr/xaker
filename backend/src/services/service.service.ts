import { Service, CreateServiceRequest, UpdateServiceRequest } from '../types/service';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

/**
 * Сервис для управления сервисами (целевыми приложениями для пентестинга)
 */
class ServiceService {
  private services: Map<string, Service> = new Map();
  private readonly DATA_DIR = join(process.cwd(), 'data');
  private readonly SERVICES_FILE = join(this.DATA_DIR, 'services.json');

  constructor() {
    this.loadServices();
  }

  /**
   * Загрузить сервисы из файла
   */
  private loadServices(): void {
    try {
      if (!existsSync(this.DATA_DIR)) {
        mkdirSync(this.DATA_DIR, { recursive: true });
      }

      if (existsSync(this.SERVICES_FILE)) {
        const data = readFileSync(this.SERVICES_FILE, 'utf-8');
        const services = JSON.parse(data) as Service[];
        this.services = new Map(services.map(s => [s.id, s]));
      }
    } catch (error) {
      console.error('Ошибка при загрузке сервисов:', error);
      this.services = new Map();
    }
  }

  /**
   * Сохранить сервисы в файл
   */
  private saveServices(): void {
    try {
      if (!existsSync(this.DATA_DIR)) {
        mkdirSync(this.DATA_DIR, { recursive: true });
      }
      const services = Array.from(this.services.values());
      writeFileSync(this.SERVICES_FILE, JSON.stringify(services, null, 2), 'utf-8');
    } catch (error) {
      console.error('Ошибка при сохранении сервисов:', error);
    }
  }

  /**
   * Получить все сервисы
   */
  getAllServices(): Service[] {
    return Array.from(this.services.values()).sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  /**
   * Получить сервис по ID
   */
  getService(id: string): Service | undefined {
    return this.services.get(id);
  }

  /**
   * Создать новый сервис
   */
  createService(data: CreateServiceRequest): Service {
    const id = crypto.randomUUID();
    const now = new Date().toISOString();
    
    const service: Service = {
      id,
      name: data.name,
      url: data.url,
      createdAt: now,
      updatedAt: now,
    };

    this.services.set(id, service);
    this.saveServices();
    return service;
  }

  /**
   * Обновить сервис
   */
  updateService(id: string, data: UpdateServiceRequest): Service | null {
    const service = this.services.get(id);
    if (!service) {
      return null;
    }

    const updated: Service = {
      ...service,
      ...data,
      updatedAt: new Date().toISOString(),
    };

    this.services.set(id, updated);
    this.saveServices();
    return updated;
  }

  /**
   * Удалить сервис
   */
  deleteService(id: string): boolean {
    if (!this.services.has(id)) {
      return false;
    }
    this.services.delete(id);
    this.saveServices();
    return true;
  }
}

export const serviceService = new ServiceService();

