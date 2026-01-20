import Anthropic from '@anthropic-ai/sdk';

/**
 * Сервис для работы с локальным MiroMind API
 * Заменяет Claude API для генерации отчетов
 */
export class MiroMindService {
  private client: Anthropic;
  private baseURL: string;
  private model: string;
  private isAvailable: boolean = false;

  constructor() {
    this.baseURL = process.env.MIROMIND_API_URL || 'http://localhost:11434/v1';
    this.model = process.env.MIROMIND_MODEL || 'llama3.1:8b';
    
    // Создаем клиент Anthropic SDK с кастомным baseURL
    // MiroMind API совместим с Anthropic форматом
    this.client = new Anthropic({
      apiKey: process.env.MIROMIND_API_KEY || 'not-needed', // MiroMind может не требовать ключ
      baseURL: this.baseURL, // Переопределяем endpoint на локальный
    });
    
    // Проверяем доступность при инициализации (асинхронно, не блокируем)
    // Реальная проверка будет выполнена при первом использовании
    this.checkAvailability().catch(err => {
      console.warn('⚠️  Предварительная проверка MiroMind не удалась:', err);
    });
  }

  /**
   * Проверить доступность MiroMind сервера
   */
  private async checkAvailability(): Promise<void> {
    try {
      // Для Ollama используем /api/tags вместо /v1/models
      const checkUrl = this.baseURL.includes('11434') 
        ? 'http://localhost:11434/api/tags'
        : `${this.baseURL.replace('/v1', '')}/v1/models`;
      
      const response = await fetch(checkUrl, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json() as any;
        // Проверяем, есть ли нужная модель
        const models = data.models || data.data || [];
        const modelName = this.model.split(':')[0];
        const hasModel = models.some((m: any) => 
          m.name?.includes(modelName) || 
          m.id?.includes(modelName) ||
          m.name === this.model ||
          m.id === this.model
        );
        
        if (hasModel || models.length > 0) {
          this.isAvailable = true;
          console.log(`✅ MiroMind сервер доступен: ${this.baseURL}`);
          const modelList = models.map((m: any) => m.name || m.id).join(', ');
          console.log(`   Доступные модели: ${modelList}`);
        } else {
          this.isAvailable = false;
          console.warn(`⚠️  Модель ${this.model} не найдена на сервере`);
        }
      } else {
        this.isAvailable = false;
        console.warn(`⚠️  MiroMind сервер недоступен: ${response.status}`);
      }
    } catch (error) {
      this.isAvailable = false;
      console.warn(`⚠️  MiroMind сервер недоступен: ${error}`);
    }
  }

  /**
   * Генерировать текст через MiroMind
   * Без ограничений по токенам - модель сама определит оптимальный размер ответа
   */
  async generateText(prompt: string): Promise<string> {
    if (!this.isAvailable) {
      await this.checkAvailability();
      if (!this.isAvailable) {
        throw new Error('MiroMind сервер недоступен. Убедитесь, что сервер запущен на ' + this.baseURL);
      }
    }

    try {
      // Для Ollama используем прямой API вызов, так как формат может отличаться
      if (this.baseURL.includes('11434')) {
        // Ollama API формат - без ограничений по токенам
        const response = await fetch('http://localhost:11434/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: this.model,
            prompt: prompt,
            stream: false
            // Не указываем num_predict - модель сама определит размер ответа
          })
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Ollama API error: ${response.status} - ${errorText}`);
        }
        
        const data = await response.json() as any;
        return data.response || '';
      } else {
        // Стандартный Anthropic API формат - используем максимальное значение
        const message = await this.client.messages.create({
          model: this.model,
          max_tokens: 8192, // Максимальное значение для большинства моделей
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ]
        });
        
        // Извлекаем текст из ответа
        let response = '';
        if (message.content && Array.isArray(message.content)) {
          for (const block of message.content) {
            if (block.type === 'text') {
              response += block.text;
            }
          }
        }
        
        return response;
      }
    } catch (error: any) {
      const errorMessage = error?.message || String(error);
      throw new Error(`MiroMind API error: ${errorMessage}`);
    }
  }

  /**
   * Проверить, доступен ли MiroMind
   * Если проверка еще не выполнена, выполняет её синхронно
   */
  async isServiceAvailable(): Promise<boolean> {
    if (!this.isAvailable) {
      await this.checkAvailability();
    }
    return this.isAvailable;
  }

  /**
   * Получить информацию о модели
   */
  getModelInfo(): { baseURL: string; model: string; available: boolean } {
    return {
      baseURL: this.baseURL,
      model: this.model,
      available: this.isAvailable
    };
  }
}

