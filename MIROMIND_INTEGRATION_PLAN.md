# 🧠 План интеграции MiroMind с пентестером Xaker

## 📋 Анализ текущей ситуации

### Текущая архитектура
- **Используется:** `@anthropic-ai/claude-agent-sdk` с функцией `query()`
- **API Endpoint:** `api.anthropic.com` (по умолчанию)
- **Аутентификация:** `ANTHROPIC_API_KEY` из переменных окружения
- **Места использования:**
  - `backend/src/services/pdfReport.service.ts` - генерация PDF отчетов
  - `backend/src/services/shannon.service.ts` - интеграция с Shannon
  - `backend/generate-pdf.js` - скрипт генерации отчетов

### Проблема
- Требуется баланс на счету Anthropic
- Нужен VPN для доступа из РФ
- Ограничения по запросам и стоимости

---

## 🔍 Совместимость MiroMind

### Что такое MiroMind/MiroThinker
- **MiroThinker** - open-source агентная модель (8B, 14B, 32B параметров)
- **MiroFlow** - фреймворк с поддержкой инструментов (tools)
- Можно развернуть локально через SGLang, vLLM или Docker
- API совместим с OpenAI/Anthropic форматом через HTTP endpoint

### API Совместимость
✅ **Хорошая новость:** MiroMind может работать через HTTP API с форматом, совместимым с Anthropic API

**Формат запроса:**
```json
POST http://localhost:8000/v1/messages
{
  "model": "mirothinker-8b",
  "messages": [{"role": "user", "content": "..."}],
  "max_tokens": 4096
}
```

**Отличие от Claude Agent SDK:**
- Claude Agent SDK использует `query({ prompt, options })` - это обертка над дочерним процессом
- MiroMind работает через прямой HTTP API (как `@anthropic-ai/sdk`)

---

## 📊 План интеграции

### Этап 1: Подготовка инфраструктуры (1-2 часа)

#### 1.1 Оценка ресурсов
- **Минимум:** 8GB RAM, CPU (без GPU)
- **Рекомендуется:** 16GB+ RAM, GPU (RTX 3060+ или эквивалент)
- **Для 8B модели:** ~8GB RAM
- **Для 14B модели:** ~14GB RAM
- **Для 32B модели:** ~32GB RAM + GPU обязательно

#### 1.2 Установка MiroMind
```bash
# Вариант 1: Через Docker (рекомендуется)
docker pull miromind/mirothinker:latest

# Вариант 2: Через Python + SGLang
pip install sglang[all]
# Загрузить модель MiroThinker-8B

# Вариант 3: Через Ollama (если поддерживается)
ollama pull mirothinker-8b
```

#### 1.3 Запуск MiroMind сервера
```bash
# Пример для SGLang
python -m sglang.launch_server \
  --model-path ./mirothinker-8b \
  --port 8000 \
  --host 0.0.0.0
```

**Проверка:**
```bash
curl http://localhost:8000/v1/models
```

---

### Этап 2: Создание адаптера API (2-3 часа)

#### 2.1 Создать новый сервис `miromind.service.ts`
```typescript
// backend/src/services/miromind.service.ts
import Anthropic from '@anthropic-ai/sdk';

class MiroMindService {
  private client: Anthropic;
  private baseURL: string;
  
  constructor() {
    this.baseURL = process.env.MIROMIND_API_URL || 'http://localhost:8000/v1';
    this.client = new Anthropic({
      apiKey: process.env.MIROMIND_API_KEY || 'not-needed', // MiroMind может не требовать ключ
      baseURL: this.baseURL, // Переопределяем endpoint
    });
  }
  
  async generateReport(prompt: string, options: any): Promise<string> {
    // Используем прямой API вызов вместо query()
    const message = await this.client.messages.create({
      model: process.env.MIROMIND_MODEL || 'mirothinker-8b',
      max_tokens: options.max_tokens || 8192,
      messages: [{ role: 'user', content: prompt }]
    });
    
    // Извлекаем текст
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
}
```

#### 2.2 Обновить `pdfReport.service.ts`
```typescript
// Добавить проверку: использовать MiroMind или Claude
const useMiroMind = process.env.USE_MIROMIND === 'true';
const miromindService = useMiroMind ? new MiroMindService() : null;

// В функции generateAttackChainWithAI:
if (useMiroMind && miromindService) {
  // Используем MiroMind
  fullResponse = await miromindService.generateReport(prompt, options);
} else {
  // Используем Claude Agent SDK (текущий код)
  for await (const message of query({ prompt, options })) {
    // ... существующий код
  }
}
```

---

### Этап 3: Настройка переменных окружения (30 минут)

#### 3.1 Обновить `backend/.env`
```env
# Выбор провайдера AI
USE_MIROMIND=true  # или false для Claude

# MiroMind настройки
MIROMIND_API_URL=http://localhost:8000/v1
MIROMIND_MODEL=mirothinker-8b
MIROMIND_API_KEY=not-needed  # Опционально, если требуется

# Claude (fallback)
ANTHROPIC_API_KEY=sk-ant-api03-...  # Оставить для fallback
```

#### 3.2 Обновить `backend/env.example`
```env
# AI Provider Selection
USE_MIROMIND=false  # true для MiroMind, false для Claude

# MiroMind Configuration
MIROMIND_API_URL=http://localhost:8000/v1
MIROMIND_MODEL=mirothinker-8b
MIROMIND_API_KEY=not-needed

# Claude Configuration (fallback)
ANTHROPIC_API_KEY=your_api_key_here
```

---

### Этап 4: Обновление зависимостей (15 минут)

#### 4.1 Установить дополнительные пакеты (если нужны)
```bash
cd backend
npm install --save axios  # Если нужен прямой HTTP клиент
```

**Примечание:** `@anthropic-ai/sdk` уже поддерживает кастомный `baseURL`, так что дополнительные пакеты могут не понадобиться.

---

### Этап 5: Тестирование (1-2 часа)

#### 5.1 Базовый тест подключения
```typescript
// Тест в отдельном файле или через API endpoint
async function testMiroMind() {
  const service = new MiroMindService();
  const response = await service.generateReport(
    "Привет! Это тест MiroMind.",
    { max_tokens: 100 }
  );
  console.log('MiroMind ответ:', response);
}
```

#### 5.2 Тест генерации отчета
- Запустить генерацию отчета для теста #5
- Сравнить результаты с Claude
- Проверить качество анализа

#### 5.3 Нагрузочное тестирование
- Проверить, сколько параллельных запросов выдерживает
- Измерить latency
- Проверить стабильность

---

### Этап 6: Интеграция с Shannon (опционально, 2-3 часа)

#### 6.1 Обновить `shannon.service.ts`
```typescript
// Добавить поддержку MiroMind для Shannon
if (process.env.USE_MIROMIND === 'true') {
  // Использовать MiroMind endpoint для Shannon
  env.MIROMIND_API_URL = process.env.MIROMIND_API_URL;
}
```

**Примечание:** Shannon может требовать изменений в своем коде, если он жестко привязан к Anthropic API.

---

## 🔧 Детальный план изменений в коде

### Файл 1: `backend/src/services/miromind.service.ts` (новый)
```typescript
import Anthropic from '@anthropic-ai/sdk';

export class MiroMindService {
  private client: Anthropic;
  private baseURL: string;
  private model: string;
  
  constructor() {
    this.baseURL = process.env.MIROMIND_API_URL || 'http://localhost:8000/v1';
    this.model = process.env.MIROMIND_MODEL || 'mirothinker-8b';
    
    this.client = new Anthropic({
      apiKey: process.env.MIROMIND_API_KEY || 'not-needed',
      baseURL: this.baseURL,
    });
  }
  
  async generateText(prompt: string, maxTokens: number = 8192): Promise<string> {
    try {
      const message = await this.client.messages.create({
        model: this.model,
        max_tokens: maxTokens,
        messages: [{ role: 'user', content: prompt }]
      });
      
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
      throw new Error(`MiroMind API error: ${error.message}`);
    }
  }
  
  isAvailable(): boolean {
    // Можно добавить проверку доступности endpoint
    return true;
  }
}
```

### Файл 2: `backend/src/services/pdfReport.service.ts` (изменения)

**Добавить импорт:**
```typescript
import { MiroMindService } from './miromind.service';
```

**Добавить проверку в начале класса:**
```typescript
private miromindService: MiroMindService | null = null;
private useMiroMind: boolean = false;

constructor() {
  // ... существующий код
  this.useMiroMind = process.env.USE_MIROMIND === 'true';
  if (this.useMiroMind) {
    this.miromindService = new MiroMindService();
    this.log('✅ MiroMind активирован');
  }
}
```

**Изменить `generateAttackChainWithAI`:**
```typescript
// В начале функции, после получения apiKey
if (this.useMiroMind && this.miromindService) {
  this.log('🧠 Использую MiroMind для генерации отчета...');
  try {
    fullResponse = await this.miromindService.generateText(
      prompt,
      8192
    );
    result = fullResponse;
    // Продолжить обработку как обычно
  } catch (error: any) {
    this.logError(`Ошибка MiroMind: ${error.message}`);
    // Fallback на Claude или простую генерацию
    throw error;
  }
} else {
  // Существующий код с query()
  for await (const message of query({ prompt, options })) {
    // ...
  }
}
```

**Аналогично изменить:**
- `generateAttackChainSection`
- `generateDetailedAnalysis`

---

## 📝 Конфигурация

### Минимальная конфигурация для тестирования
```env
USE_MIROMIND=true
MIROMIND_API_URL=http://localhost:8000/v1
MIROMIND_MODEL=mirothinker-8b
```

### Рекомендуемая конфигурация
```env
USE_MIROMIND=true
MIROMIND_API_URL=http://localhost:8000/v1
MIROMIND_MODEL=mirothinker-14b  # Если есть ресурсы
MIROMIND_API_KEY=not-needed

# Fallback на Claude (если MiroMind недоступен)
ANTHROPIC_API_KEY=sk-ant-api03-...
```

---

## ⚠️ Важные замечания

### 1. Производительность
- **MiroThinker-8B** на CPU: ~1-5 сек на запрос (зависит от промпта)
- **MiroThinker-8B** на GPU: ~0.5-2 сек на запрос
- **MiroThinker-14B/32B** требует GPU для приемлемой скорости

### 2. Качество ответов
- MiroThinker может быть менее точным, чем Claude для сложных задач
- Рекомендуется тестирование на реальных данных
- Возможно, потребуется fine-tuning на ваших данных

### 3. Совместимость с Claude Agent SDK
- `query()` из Claude Agent SDK - это обертка над дочерним процессом
- MiroMind работает через HTTP API
- **Нужен адаптер** для полной совместимости

### 4. Безопасность
- MiroMind работает локально - данные не уходят в облако ✅
- Но нужно обеспечить изоляцию для пентестинга
- Рекомендуется использовать sandbox для выполнения кода

---

## 🚀 Порядок выполнения

1. **Установить MiroMind** (30-60 мин)
2. **Создать `miromind.service.ts`** (30 мин)
3. **Обновить `pdfReport.service.ts`** (1 час)
4. **Настроить `.env`** (15 мин)
5. **Протестировать** (1-2 часа)
6. **Оптимизировать** (по необходимости)

**Общее время:** ~4-6 часов для базовой интеграции

---

## 📚 Полезные ссылки

- **MiroThinker GitHub:** https://github.com/MiroMindAI/MiroThinker
- **MiroFlow GitHub:** https://github.com/MiroMindAI/MiroFlow
- **SGLang (для запуска):** https://github.com/sgl-project/sglang
- **Документация:** https://miromindai.github.io/

---

## ✅ Чеклист готовности

- [ ] MiroMind установлен и запущен
- [ ] Endpoint доступен на `http://localhost:8000/v1`
- [ ] Создан `miromind.service.ts`
- [ ] Обновлен `pdfReport.service.ts`
- [ ] Настроен `.env`
- [ ] Протестирована генерация отчетов
- [ ] Проверена производительность
- [ ] Документация обновлена

---

**Готов начать интеграцию?** 🚀

