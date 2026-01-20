# Ответы на вопросы по архитектуре

## 1. Для Shannon может использоваться исключительно Claude?

### Текущая ситуация:
**Да, Shannon использует исключительно Claude API** по следующим причинам:

1. **Shannon использует Anthropic SDK** (`@anthropic-ai/claude-agent-sdk`)
   - SDK требует формат Anthropic API
   - Ollama API не полностью совместим с Anthropic API форматом
   - Это вызывает ошибки "Connection error"

2. **Shannon - это готовый инструмент** от Anthropic
   - Он разработан специально для работы с Claude
   - Использует специфичные функции Claude Agent SDK
   - Требует определенный формат запросов/ответов

### Возможные альтернативы:

#### Вариант A: Использовать Ollama с Anthropic API совместимостью
- Ollama v0.14.0+ поддерживает Anthropic API совместимый интерфейс
- Можно настроить `ANTHROPIC_API_BASE_URL` на Ollama endpoint
- **НО**: Не все функции Claude Agent SDK могут работать корректно

#### Вариант B: Оставить Shannon с Claude API
- **Рекомендуется**: Shannon использует Claude API для выполнения пентеста
- MiroMind используется только для генерации отчетов (экономия)
- Это разделение функций оптимально

### Вывод:
**Shannon должен использовать Claude API** для выполнения пентеста, так как:
- Shannon - это специализированный инструмент от Anthropic
- Он требует специфичный формат Anthropic API
- Попытки использовать Ollama приводят к ошибкам совместимости

---

## 2. Почему в отчете для формирования цепочки взлома мы обращаемся к Claude?

### Текущая проблема:
Функция `generateAttackChainSection()` **не проверяет `USE_MIROMIND`** и всегда использует Claude API:

```typescript
private async generateAttackChainSection(...) {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    
    if (!apiKey || apiKey === 'your_api_key_here') {
        return this.generateAttackChainSimple(...); // Fallback
    }
    
    // ВСЕГДА использует Claude API, даже если USE_MIROMIND=true
    // ...
}
```

### Почему так сделано:
1. **Исторические причины**: Функция была написана до интеграции MiroMind
2. **Неполная миграция**: При добавлении MiroMind забыли обновить эту функцию
3. **Разные функции**: `generateAttackChain()` использует MiroMind, а `generateAttackChainSection()` - нет

### Решение:
**Нужно добавить проверку MiroMind** в `generateAttackChainSection()`, аналогично `generateDetailedAnalysis()`:

```typescript
private async generateAttackChainSection(...) {
    // Проверяем MiroMind ПЕРВЫМ
    const miromindAvailable = this.useMiroMind && this.miromindService 
        ? await this.miromindService.isServiceAvailable() 
        : false;
    
    if (miromindAvailable) {
        return this.generateAttackChainSectionWithMiroMind(...);
    }
    
    // Fallback на Claude API
    // ...
}
```

### Вывод:
**Это можно и нужно исправить!** Цепочка взлома должна использовать MiroMind, если он доступен, для единообразия и экономии.

---

## 3. Существуют надстройки для MiroMind чтобы ее модели имели доступ к поиску в интернете?

### Да, существуют!

### Вариант A: Ollama Web Search API (официальный)

Ollama поддерживает **web_search** и **web_fetch** инструменты:

```javascript
// Пример использования
const response = await fetch('http://localhost:11434/api/generate', {
    method: 'POST',
    body: JSON.stringify({
        model: 'llama3.1:8b',
        prompt: 'Найди информацию о CVE-2024-1234',
        tools: [
            {
                type: 'web_search',
                web_search: {}
            }
        ]
    })
});
```

**Требования:**
- Ollama v0.11+ (лучше v0.14+)
- API ключ для web search (если используется облачный сервис)
- Настройка инструментов в запросах

### Вариант B: Внешние плагины

1. **ollama-web-search** - использует SearxNG для поиска
2. **Open-WebUI** - имеет встроенную поддержку web search
3. **Custom wrapper** - можно создать свой агент, который:
   - Получает запрос от модели
   - Выполняет поиск через внешний API (Google, Bing, SearxNG)
   - Возвращает результаты модели

### Вариант C: Интеграция через MiroMind Service

Можно расширить `MiroMindService` для поддержки web search:

```typescript
class MiroMindService {
    async generateTextWithWebSearch(prompt: string, maxTokens: number) {
        // 1. Отправляем запрос с инструментом web_search
        // 2. Модель решает, нужен ли поиск
        // 3. Если да - выполняем поиск
        // 4. Возвращаем результаты модели
    }
}
```

### Ограничения:

1. **Локальные модели не имеют доступа к интернету по умолчанию**
   - Нужно явно включать инструменты поиска
   - Требуется настройка API ключей для поисковых сервисов

2. **Качество поиска зависит от провайдера**
   - Google Search API (платный)
   - Bing Search API (платный)
   - SearxNG (бесплатный, но требует настройки)

3. **Производительность**
   - Поиск добавляет задержку
   - Увеличивает стоимость (если используется платный API)

### Рекомендации:

**Для пентестинга доступ к интернету НЕ критичен**, потому что:
- Shannon сам делает HTTP запросы к анализируемому сайту
- Модель анализирует данные, которые Shannon собрал
- Модель не нужна для поиска в интернете - она работает с локальными данными

**Но если нужен доступ к интернету:**
1. Использовать Ollama web_search инструменты
2. Настроить SearxNG или другой поисковый сервис
3. Расширить MiroMindService для поддержки web search

---

## Итоговые рекомендации:

1. **Shannon → Claude API** (оставить как есть)
   - Shannon требует Anthropic API формат
   - Это специализированный инструмент от Anthropic

2. **Отчеты → MiroMind** (исправить цепочку взлома)
   - Добавить поддержку MiroMind в `generateAttackChainSection()`
   - Для единообразия и экономии

3. **Доступ к интернету → Опционально**
   - Не критично для пентестинга
   - Можно добавить через Ollama web_search, если понадобится


