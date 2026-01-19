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
    
    // Проверяем доступность при инициализации
    this.checkAvailability();
  }

  /**
   * Проверить доступность MiroMind сервера
   */
  private async checkAvailability(): Promise<void> {
    try {
      // Простая проверка через fetch
      const response = await fetch(`${this.baseURL.replace('/v1', '')}/v1/models`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        this.isAvailable = true;
        console.log(`✅ MiroMind сервер доступен: ${this.baseURL}`);
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
   */
  async generateText(prompt: string, maxTokens: number = 8192): Promise<string> {
    if (!this.isAvailable) {
      await this.checkAvailability();
      if (!this.isAvailable) {
        throw new Error('MiroMind сервер недоступен. Убедитесь, что сервер запущен на ' + this.baseURL);
      }
    }

    try {
      const message = await this.client.messages.create({
        model: this.model,
        max_tokens: maxTokens,
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
    } catch (error: any) {
      const errorMessage = error?.message || String(error);
      throw new Error(`MiroMind API error: ${errorMessage}`);
    }
  }

  /**
   * Проверить, доступен ли MiroMind
   */
  isServiceAvailable(): boolean {
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

