import { join } from 'path';
import { existsSync, readFileSync, readdirSync, statSync } from 'fs';
import { marked } from 'marked';
import puppeteer from 'puppeteer';
import { pentestService } from './pentest.service';
import { query } from '@anthropic-ai/claude-agent-sdk';

/**
 * Сервис для генерации PDF отчетов
 */
class PdfReportService {
  private readonly REPORTS_DIR = join(process.cwd(), 'reports');

  constructor() {
    // Создаем директорию для отчетов, если её нет
    if (!existsSync(this.REPORTS_DIR)) {
      const fs = require('fs');
      fs.mkdirSync(this.REPORTS_DIR, { recursive: true });
    }
  }

  /**
   * Сгенерировать PDF отчет для пентеста
   */
  async generatePdfReport(pentestId: string): Promise<string> {
    const pentest = pentestService.getPentest(pentestId);
    if (!pentest) {
      throw new Error('Пентест не найден');
    }

    // Путь к папке с результатами пентеста
    const pentestDir = join(process.cwd(), 'pentests', pentestId);
    const deliverablesDir = join(pentestDir, 'deliverables');

    if (!existsSync(deliverablesDir)) {
      throw new Error('Папка с результатами пентеста не найдена');
    }

    // Генерируем Markdown отчет с промптом
    const markdownReport = await this.generateMarkdownReport(pentestId, pentest, deliverablesDir);

    // Конвертируем Markdown в HTML
    const htmlReport = await this.markdownToHtml(markdownReport, pentest);

    // Конвертируем HTML в PDF
    const pdfPath = await this.htmlToPdf(htmlReport, pentestId);

    return pdfPath;
  }

  /**
   * Сгенерировать Markdown отчет с анализом всех файлов
   */
  private async generateMarkdownReport(
    pentestId: string,
    pentest: any,
    deliverablesDir: string
  ): Promise<string> {
    // Читаем все файлы из deliverables
    const files = this.getAllReportFiles(deliverablesDir);

    // Читаем содержимое всех отчетов
    let allContent = '';
    for (const file of files) {
      try {
        const content = readFileSync(file.path, 'utf-8');
        allContent += `\n\n## ${file.name}\n\n${content}\n\n`;
      } catch (error) {
        console.error(`Ошибка чтения файла ${file.path}:`, error);
      }
    }

    // Генерируем отчет с новым промптом
    let aiReport = await this.generateAttackChain(allContent, pentest.targetUrl, deliverablesDir);
    
    // Применяем очистку к результату независимо от источника (AI или fallback)
    aiReport = this.cleanReportFromEnglishSections(aiReport);
    
    const report = `# 🛡️ Отчет о пентесте: ${pentest.targetUrl}

**AI Penetration Testing Platform | Pentest.red**

---

## 📋 Общая информация

| Параметр | Значение |
|----------|----------|
| **Цель тестирования** | ${pentest.targetUrl} |
| **Название пентеста** | ${pentest.name} |
| **Статус** | ${pentest.status === 'completed' ? '✅ Завершен' : pentest.status} |
| **Дата создания** | ${new Date(pentest.createdAt).toLocaleString('ru-RU')} |
| **Дата начала** | ${pentest.startedAt ? new Date(pentest.startedAt).toLocaleString('ru-RU') : 'Не начат'} |
| **Дата завершения** | ${pentest.completedAt ? new Date(pentest.completedAt).toLocaleString('ru-RU') : 'Не завершен'} |
| **ID пентеста** | \`${pentestId}\` |

---

${aiReport}

---

## ⚖️ Правовая информация

Данный отчет создан в рамках авторизованного тестирования на проникновение. Все найденные уязвимости должны быть использованы исключительно для улучшения безопасности системы.

---

**© 2026 Pentest.red | Enterprise Security Platform**

*Дата создания отчета: ${new Date().toLocaleString('ru-RU')}*

*Отчет сгенерирован автоматически AI Penetration Testing Platform*
`;

    // ВАЖНО: Применяем очистку ко всему финальному отчету для удаления английских разделов
    return this.cleanFinalReport(report);
  }

  /**
   * Генерировать детальную цепочку взлома из содержимого отчетов
   * Использует AI (Claude) для создания максимально подробной цепочки взлома
   */
  private async generateAttackChain(content: string, targetUrl: string, deliverablesDir: string): Promise<string> {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    
    // Если есть API ключ, используем AI для генерации детальной цепочки
    if (apiKey && apiKey !== 'your_api_key_here') {
      try {
        return await this.generateAttackChainWithAI(content, targetUrl, deliverablesDir, apiKey);
      } catch (error) {
        console.error('Ошибка при генерации цепочки взлома через AI:', error);
        // Fallback на простой парсинг
      }
    }
    
    // Fallback: простой парсинг без AI
    return this.generateAttackChainSimple(content, targetUrl);
  }

  /**
   * Генерировать детальную цепочку взлома с использованием Claude AI
   */
  private async generateAttackChainWithAI(
    content: string,
    targetUrl: string,
    deliverablesDir: string,
    apiKey: string
  ): Promise<string> {
    // Читаем все файлы для контекста
    const files = this.getAllReportFiles(deliverablesDir);
    let allFilesContent = '';
    for (const file of files) {
      try {
        const fileContent = readFileSync(file.path, 'utf-8');
        allFilesContent += `\n\n=== ${file.name} ===\n\n${fileContent}\n\n`;
      } catch (error) {
        // Игнорируем ошибки чтения
      }
    }

    const prompt = `Ты эксперт по кибербезопасности и пентестингу. Проанализируй все предоставленные файлы с результатами пентеста и создай ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА для сервиса ${targetUrl}.

КРИТИЧЕСКИ ВАЖНЫЕ ТРЕБОВАНИЯ:
1. ВСЕ РАЗДЕЛЫ ОТЧЕТА ДОЛЖНЫ БЫТЬ НАПИСАНЫ НА РУССКОМ ЯЗЫКЕ
2. НЕ создавай разделы на английском языке - ВСЕ разделы должны быть на русском
3. НЕ копируй английские разделы из исходных файлов - переведи их на русский
4. НЕ ДУБЛИРУЙ разделы - каждый раздел должен быть представлен ТОЛЬКО ОДИН РАЗ
5. НЕ создавай дополнительные разделы вне указанной структуры
6. НЕ добавляй английские заголовки разделов типа "Summary of Findings", "Technical Details", "Authentication Analysis Report" и т.д.
7. НЕ повторяй информацию из одного раздела в другом
8. Разрешены ТОЛЬКО английские названия уязвимостей (XSS, SQL Injection) и технические термины в коде/командах

СТРУКТУРА ОТЧЕТА (создай ТОЛЬКО эти 6 разделов, БЕЗ ПОВТОРОВ):

## ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА

### 1. Executive Summary (Краткое резюме)
   - Краткое описание проведенного пентеста
   - Общая оценка уровня безопасности сервиса
   - Ключевые выводы и рекомендации
   - Критичность найденных уязвимостей (общая статистика)

### 2. Методология тестирования
   - Описание использованной методологии
   - Объем и глубина тестирования
   - Инструменты и технологии
   - Временные рамки проведения пентеста

### 3. Детальный анализ найденных уязвимостей
   Для КАЖДОЙ найденной уязвимости предоставь (ВСЕ НА РУССКОМ ЯЗЫКЕ):
   - **Название уязвимости** (четкое и понятное на русском, можно указать английское название в скобках, например: "Обход CAPTCHA (Cloudflare Turnstile Bypass)")
   - **Критичность** (КРИТИЧЕСКАЯ/ВЫСОКАЯ/СРЕДНЯЯ/НИЗКАЯ или CRITICAL/HIGH/MEDIUM/LOW)
   - **Расположение** (URL, эндпоинт, компонент) - описание на русском
   - **Детальное описание** (что именно не так, почему это проблема) - ТОЛЬКО НА РУССКОМ
   - **Техническое описание** (как воспроизвести, proof-of-concept) - описание на русском, команды/код могут быть на английском
   - **Бизнес-влияние** (какой ущерб может быть нанесен) - ТОЛЬКО НА РУССКОМ
   - **Рекомендации по исправлению** (конкретные шаги для устранения) - ТОЛЬКО НА РУССКОМ
   - **Оценка сложности исправления** (простая/средняя/сложная)

### 4. Оценка рисков
   - Общая оценка рисков для бизнеса - НА РУССКОМ
   - Приоритизация уязвимостей по бизнес-критичности - НА РУССКОМ
   - Потенциальный ущерб от эксплуатации уязвимостей - НА РУССКОМ
   - Временные рамки для исправления критических уязвимостей - НА РУССКОМ

### 5. Рекомендации и план действий
   - Общие рекомендации по улучшению безопасности - НА РУССКОМ
   - План действий по устранению уязвимостей (приоритизированный) - НА РУССКОМ
   - Рекомендации по долгосрочному улучшению безопасности - НА РУССКОМ
   - Best practices для предотвращения подобных уязвимостей - НА РУССКОМ

### 6. Заключение
   - Общие выводы по результатам пентеста - НА РУССКОМ
   - Оценка текущего состояния безопасности - НА РУССКОМ
   - Рекомендации по дальнейшему мониторингу - НА РУССКОМ

ФОРМАТИРОВАНИЕ:
- Используй заголовки ## для "ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА"
- Используй заголовки ### для разделов 1-6
- Используй таблицы для сравнения и статистики
- Используй списки для рекомендаций
- Все примеры кода и команды оформляй в блоки кода
- Будь максимально подробным и конкретным

ЗАПРЕЩЕНО:
- Дублировать разделы 1-6
- Создавать дополнительные разделы вне указанной структуры
- Использовать английские заголовки разделов (кроме "Executive Summary" в разделе 1)
- Добавлять разделы типа "Authentication Analysis Report", "Security Assessment Report", "Summary of Findings", "Technical Details"
- Создавать разделы на английском языке
- Копировать английские разделы из исходных файлов без перевода
- Повторять одну и ту же информацию в разных разделах
- Использовать английский язык для описаний, выводов и рекомендаций

ФАЙЛЫ С РЕЗУЛЬТАТАМИ ПЕНТЕСТА:
${allFilesContent.substring(0, 200000)}

Создай ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА. Отчет должен:
- Быть на русском языке (английские названия и технические детали разрешены)
- Содержать ТОЛЬКО 6 указанных разделов
- НЕ содержать повторов разделов
- НЕ содержать английских заголовков разделов (кроме "Executive Summary" в разделе 1)
- НЕ содержать дополнительных разделов`;

    try {
      // Настраиваем прокси для VPN (как в Shannon)
      const proxyUrl = process.env.HTTP_PROXY || process.env.HTTPS_PROXY || process.env.http_proxy || process.env.https_proxy || 'http://127.0.0.1:12334';
      
      // Опции для query (как в Shannon)
      const options: any = {
        apiKey: apiKey,
        model: 'claude-sonnet-4-5-20250929', // Используем ту же модель, что и Shannon
        maxTurns: 50, // Ограничиваем количество поворотов для генерации отчета
        cwd: deliverablesDir, // Рабочая директория
        permissionMode: 'bypassPermissions' as const, // Обходим проверки разрешений
      };

      // Устанавливаем прокси для VPN (как в Shannon)
      const originalHttpProxy = process.env.HTTP_PROXY;
      const originalHttpsProxy = process.env.HTTPS_PROXY;
      
      if (proxyUrl) {
        process.env.HTTP_PROXY = proxyUrl;
        process.env.HTTPS_PROXY = proxyUrl;
      }
      
      try {
        // Используем query из Claude Agent SDK (как в Shannon)
        let fullResponse = '';
        let result: string | null = null;
        let messageCount = 0;
        
        console.log('Отправляю запрос к Claude AI для генерации отчета...');
        for await (const message of query({ prompt, options })) {
          messageCount++;
          
          // Обрабатываем сообщение типа 'result' - это финальный результат (как в Shannon)
          if (message.type === 'result') {
            const resultMessage = message as any;
            // В Shannon результат берется из resultMessage.result
            if (resultMessage.result && typeof resultMessage.result === 'string') {
              // Добавляем к накопленному ответу, а не заменяем
              if (fullResponse && !fullResponse.includes(resultMessage.result)) {
                fullResponse += '\n\n' + resultMessage.result;
              } else if (!fullResponse) {
                fullResponse = resultMessage.result;
              }
              result = fullResponse;
              console.log(`✅ Получен финальный результат из result.result (${resultMessage.result.length} символов, всего: ${fullResponse.length})`);
            } else if (resultMessage.content) {
              if (typeof resultMessage.content === 'string') {
                if (fullResponse && !fullResponse.includes(resultMessage.content)) {
                  fullResponse += '\n\n' + resultMessage.content;
                } else if (!fullResponse) {
                  fullResponse = resultMessage.content;
                }
                result = fullResponse;
                console.log(`✅ Получен результат из result.content (${resultMessage.content.length} символов, всего: ${fullResponse.length})`);
              }
            } else if (resultMessage.text) {
              if (fullResponse && !fullResponse.includes(resultMessage.text)) {
                fullResponse += '\n\n' + resultMessage.text;
              } else if (!fullResponse) {
                fullResponse = resultMessage.text;
              }
              result = fullResponse;
              console.log(`✅ Получен результат из result.text (${resultMessage.text.length} символов, всего: ${fullResponse.length})`);
            }
          } else if (message.type === 'assistant') {
            // В Shannon также собираем из assistant сообщений - ВАЖНО: собираем ВСЕ сообщения
            const assistantMsg = message as any;
            if (assistantMsg.message && assistantMsg.message.content) {
              const content = Array.isArray(assistantMsg.message.content)
                ? assistantMsg.message.content.map((c: any) => c.text || JSON.stringify(c)).join('\n')
                : String(assistantMsg.message.content);
              if (content && typeof content === 'string' && content.trim().length > 0) {
                // Добавляем к накопленному ответу
                fullResponse += content + '\n\n';
                console.log(`✅ Получен текст из assistant.message.content (${content.length} символов, всего: ${fullResponse.length})`);
              }
            } else if (assistantMsg.content && Array.isArray(assistantMsg.content)) {
              for (const content of assistantMsg.content) {
                if (content.type === 'text' && content.text && content.text.trim().length > 0) {
                  fullResponse += content.text + '\n\n';
                  console.log(`✅ Получен текст из assistant.content[] (${content.text.length} символов, всего: ${fullResponse.length})`);
                }
              }
            }
          }
        }
        
        console.log(`Всего сообщений: ${messageCount}, Длина ответа: ${fullResponse.length}`);

        // Восстанавливаем оригинальные значения прокси
        if (originalHttpProxy) process.env.HTTP_PROXY = originalHttpProxy;
        else delete process.env.HTTP_PROXY;
        if (originalHttpsProxy) process.env.HTTPS_PROXY = originalHttpsProxy;
        else delete process.env.HTTPS_PROXY;

        const finalResponse = result || fullResponse;

        // Очищаем ответ от лишних разделов - оставляем ТОЛЬКО "ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА"
        return this.cleanReportFromEnglishSections(finalResponse);
      } catch (queryError: any) {
        // Восстанавливаем оригинальные значения прокси при ошибке
        if (originalHttpProxy) process.env.HTTP_PROXY = originalHttpProxy;
        else delete process.env.HTTP_PROXY;
        if (originalHttpsProxy) process.env.HTTPS_PROXY = originalHttpsProxy;
        else delete process.env.HTTPS_PROXY;
        
        throw queryError;
      }
    } catch (error: any) {
      console.error('Ошибка при вызове Claude API:', error);
      throw error;
    }
  }

  /**
   * Очистить отчет от английских разделов и повторов
   */
  private cleanReportFromEnglishSections(response: string): string {
    let cleanedResponse = response;
        
        // Находим начало "ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА"
        const fullReportPattern = /##\s*ПОЛНЫЙ\s+ОТЧЕТ\s+ПО\s+РЕЗУЛЬТАТАМ\s+ПЕНТЕСТА/i;
        const fullReportMatch = cleanedResponse.match(fullReportPattern);
        
        if (fullReportMatch && fullReportMatch.index !== undefined) {
          // Удаляем все что до начала отчета
          cleanedResponse = cleanedResponse.substring(fullReportMatch.index);
        } else {
          // Если не нашли точный заголовок, ищем альтернативные варианты
          const altPatterns = [
            /##\s*ПОЛНЫЙ\s+ОТЧЕТ/i,
            /##\s*ОТЧЕТ\s+ПО\s+РЕЗУЛЬТАТАМ/i,
            /###\s*1[\.\)]?\s*Executive\s+Summary/i
          ];
          
          for (const pattern of altPatterns) {
            const match = cleanedResponse.match(pattern);
            if (match && match.index !== undefined) {
              // Ищем начало отчета (может быть немного выше)
              const startIndex = Math.max(0, match.index - 200);
              cleanedResponse = cleanedResponse.substring(startIndex);
              break;
            }
          }
        }
        
        // Удаляем все английские разделы в начале (до "ПОЛНЫЙ ОТЧЕТ")
        const englishSections = [
          /^[^#]*##\s*[A-Z][a-z]+.*?(?=##\s*ПОЛНЫЙ\s+ОТЧЕТ|###\s*1[\.\)]?\s*Executive)/is,
          /^[^#]*##\s*Executive\s+Summary.*?(?=##\s*ПОЛНЫЙ\s+ОТЧЕТ|###\s*1[\.\)]?\s*Executive)/is,
          /^[^#]*##\s*[A-Z][a-z\s]+Report.*?(?=##\s*ПОЛНЫЙ\s+ОТЧЕТ|###\s*1[\.\)]?\s*Executive)/is
        ];
        
        for (const pattern of englishSections) {
          cleanedResponse = cleanedResponse.replace(pattern, '');
        }
        
        // Находим конец отчета - ищем раздел "Заключение" (раздел 6)
        const conclusionPattern = /###\s*6[\.\)]?\s*Заключение/i;
        const conclusionMatch = cleanedResponse.match(conclusionPattern);
        
        if (conclusionMatch && conclusionMatch.index !== undefined) {
          // Находим конец раздела "Заключение" - до следующего ## или до конца
          const afterConclusion = cleanedResponse.substring(conclusionMatch.index);
          const endMatch = afterConclusion.match(/###\s*6[\.\)]?\s*Заключение[\s\S]*?(?=\n##\s+[^#]|\n---|$)/i);
          
          if (endMatch) {
            const endIndex = conclusionMatch.index + endMatch[0].length;
            cleanedResponse = cleanedResponse.substring(0, endIndex);
          } else {
            // Если не нашли конец, берем до следующего ## или до конца
            const nextSectionMatch = afterConclusion.match(/###\s*6[\.\)]?\s*Заключение[\s\S]*?(?=\n##|$)/i);
            if (nextSectionMatch) {
              const endIndex = conclusionMatch.index + nextSectionMatch[0].length;
              cleanedResponse = cleanedResponse.substring(0, endIndex);
            }
          }
        }
        
        // Удаляем все английские разделы после заключения - более агрессивная очистка
        // ВАЖНО: Добавляем конкретные заголовки из исходных файлов
        const englishPatterns = [
          /##\s*[A-Z][a-z\s]+Report/gi,
          /##\s*Authentication\s+Analysis/gi,
          /##\s*Security\s+Assessment/gi,
          /##\s*Detailed\s+Analysis/gi,
          /##\s*[A-Z][a-z\s]+Dashboard/gi,
          /##\s*Executive\s+Summary/gi,
          /##\s*[A-Z][a-z\s]+Analysis/gi,
          /##\s*[A-Z][a-z\s]+Report/gi,
          /##\s*Summary\s+of\s+Findings/gi,
          /##\s*Technical\s+Details/gi,
          /##\s*[A-Z][a-z\s]+Vulnerability/gi,
          /##\s*[A-Z][a-z\s]+Bypass/gi,
          /##\s*[A-Z][a-z\s]+Access/gi,
          /##\s*[A-Z][a-z\s]+Endpoint/gi,
          // Конкретные заголовки из исходных файлов deliverables
          /##\s*Security\s+Assessment\s+Report/gi,
          /##\s*Authentication\s+Exploitation\s+Evidence/gi,
          /##\s*Authentication\s+Analysis\s+Report/gi,
          /##\s*Authorization\s+Analysis\s+Report/gi,
          /##\s*Penetration\s+Test\s+Scope\s+&\s+Boundaries/gi,
          /##\s*Injection\s+Analysis\s+Report/gi,
          /##\s*Pre-Reconnaissance\s+Report/gi,
          /##\s*Reconnaissance\s+Deliverable/gi,
          /##\s*SSRF\s+Analysis\s+Report/gi,
          /##\s*Cross-Site\s+Scripting\s+\(XSS\)\s+Analysis\s+Report/gi,
          /##\s*XSS\s+Analysis\s+Report/gi
        ];
        
        // Удаляем все что после заключения, если там английские разделы
        if (conclusionMatch && conclusionMatch.index !== undefined) {
          const afterConclusion = cleanedResponse.substring(conclusionMatch.index + conclusionMatch[0].length);
          // Проверяем, есть ли английские разделы после заключения
          let hasEnglishAfter = false;
          for (const pattern of englishPatterns) {
            if (pattern.test(afterConclusion)) {
              hasEnglishAfter = true;
              break;
            }
          }
          
          if (hasEnglishAfter) {
            // Удаляем все после заключения
            cleanedResponse = cleanedResponse.substring(0, conclusionMatch.index + conclusionMatch[0].length);
          }
        }
        
        // Удаляем все английские разделы в любом месте документа (включая внутри отчета)
        // Сначала находим границы правильного отчета (от раздела 1 до раздела 6)
        const section1Pattern = /###\s*1[\.\)]?\s*Executive\s+Summary/i;
        const section6Pattern = /###\s*6[\.\)]?\s*Заключение/i;
        const section1Match = cleanedResponse.match(section1Pattern);
        const section6Match = cleanedResponse.match(section6Pattern);
        
        let reportStart = 0;
        let reportEnd = cleanedResponse.length;
        
        if (section1Match && section1Match.index !== undefined) {
          reportStart = section1Match.index;
        }
        if (section6Match && section6Match.index !== undefined) {
          // Находим конец раздела 6
          const afterSection6 = cleanedResponse.substring(section6Match.index);
          const endMatch = afterSection6.match(/###\s*6[\.\)]?\s*Заключение[\s\S]*?(?=\n###\s*[1-6]|\n##\s+[^#]|\n---|$)/i);
          if (endMatch) {
            reportEnd = section6Match.index + endMatch[0].length;
          }
        }
        
        // Удаляем английские разделы ВНУТРИ отчета (между разделами 1-6)
        for (const pattern of englishPatterns) {
          const matches = [...cleanedResponse.matchAll(pattern)];
          for (const match of matches) {
            if (match.index !== undefined) {
              // Пропускаем, если это часть правильного отчета (Executive Summary в разделе 1)
              const beforeMatch = cleanedResponse.substring(Math.max(0, match.index - 100), match.index);
              if (beforeMatch.includes('### 1') || beforeMatch.includes('### 1.')) {
                continue; // Это правильный раздел
              }
              
              // Удаляем английский раздел, если он внутри отчета (между разделами 1-6)
              if (match.index >= reportStart && match.index < reportEnd) {
                // Находим конец английского раздела
                const afterMatch = cleanedResponse.substring(match.index);
                const endMatch = afterMatch.match(/##\s+[^\n]*\n[\s\S]*?(?=\n###\s*[1-6]|\n##\s+[^#]|\n---|$)/);
                if (endMatch) {
                  cleanedResponse = cleanedResponse.substring(0, match.index) + cleanedResponse.substring(match.index + endMatch[0].length);
                  // Обновляем границы после удаления
                  reportEnd -= endMatch[0].length;
                } else {
                  cleanedResponse = cleanedResponse.substring(0, match.index);
                  reportEnd = match.index;
                }
                continue;
              }
              
              // Удаляем английский раздел вне отчета
              const afterMatch = cleanedResponse.substring(match.index);
              const endMatch = afterMatch.match(/##\s+[^\n]*\n[\s\S]*?(?=\n##|$)/);
              if (endMatch) {
                cleanedResponse = cleanedResponse.substring(0, match.index) + cleanedResponse.substring(match.index + endMatch[0].length);
              } else {
                cleanedResponse = cleanedResponse.substring(0, match.index);
              }
            }
          }
        }
        
        // ВАЖНО: НЕ удаляем раздел "📊 Детальные результаты анализа" - это русский контент!
        // Удаляем только английские заголовки разделов
        
        // Удаляем английские разделы с заголовками типа "Summary of Findings", "Technical Details" и т.д.
        // ВАЖНО: Удаляем все английские заголовки разделов, которые попадают из исходных файлов
        const englishSectionHeaders = [
          /##\s*Summary\s+of\s+Findings/gi,
          /##\s*Technical\s+Details/gi,
          /##\s*[A-Z][a-z]+\s+Vulnerability/gi,
          /##\s*[A-Z][a-z]+\s+Bypass/gi,
          /##\s*[A-Z][a-z]+\s+Access/gi,
          /##\s*[A-Z][a-z]+\s+Endpoint/gi,
          /##\s*Vulnerable\s+location/gi,
          /##\s*Overview/gi,
          /##\s*Impact/gi,
          /##\s*Severity/gi,
          /##\s*Prerequisites/gi,
          /##\s*Notes/gi,
          // Конкретные заголовки из исходных файлов
          /##\s*Security\s+Assessment\s+Report/gi,
          /##\s*Authentication\s+Exploitation\s+Evidence/gi,
          /##\s*Authentication\s+Analysis\s+Report/gi,
          /##\s*Authorization\s+Analysis\s+Report/gi,
          /##\s*Penetration\s+Test\s+Scope\s+&\s+Boundaries/gi,
          /##\s*Injection\s+Analysis\s+Report/gi,
          /##\s*Pre-Reconnaissance\s+Report/gi,
          /##\s*Reconnaissance\s+Deliverable/gi,
          /##\s*SSRF\s+Analysis\s+Report/gi,
          /##\s*Cross-Site\s+Scripting\s+\(XSS\)\s+Analysis\s+Report/gi,
          /##\s*XSS\s+Analysis\s+Report/gi,
          // Общие паттерны для английских заголовков
          /##\s*[A-Z][a-z\s]+Analysis\s+Report/gi,
          /##\s*[A-Z][a-z\s]+Exploitation\s+Evidence/gi,
          /##\s*[A-Z][a-z\s]+Deliverable/gi,
          /##\s*[A-Z][a-z\s]+Report/gi,
          /##\s*[A-Z][a-z\s]+Summary/gi
        ];
        
        for (const pattern of englishSectionHeaders) {
          const matches = [...cleanedResponse.matchAll(pattern)];
          for (const match of matches) {
            if (match.index !== undefined) {
              // Проверяем, не является ли это частью правильного отчета
              const beforeMatch = cleanedResponse.substring(Math.max(0, match.index - 200), match.index);
              if (beforeMatch.includes('### 1') || beforeMatch.includes('### 2') || beforeMatch.includes('### 3') || 
                  beforeMatch.includes('### 4') || beforeMatch.includes('### 5') || beforeMatch.includes('### 6') ||
                  beforeMatch.includes('ПОЛНЫЙ ОТЧЕТ')) {
                // Это может быть частью правильного отчета, пропускаем
                continue;
              }
              
              // Удаляем английский раздел до следующего ## или ###
              const afterMatch = cleanedResponse.substring(match.index);
              const endMatch = afterMatch.match(/##\s+[^\n]*\n[\s\S]*?(?=\n###\s*[1-6]|\n##\s+[^#]|\n---|$)/);
              if (endMatch) {
                cleanedResponse = cleanedResponse.substring(0, match.index) + cleanedResponse.substring(match.index + endMatch[0].length);
              } else {
                cleanedResponse = cleanedResponse.substring(0, match.index);
              }
            }
          }
        }
        
        // Удаляем старые разделы 1-4 если они есть (КРАТКИЙ СПИСОК, ДЭШБОРД, ЦЕПОЧКА)
        const oldSections = [
          /##?\s*1[\.\)]\s*КРАТКИЙ\s+СПИСОК/gi,
          /##?\s*2[\.\)]\s*ПОДРОБНЫЙ\s+ДЭШБОРД/gi,
          /##?\s*3[\.\)]\s*ПОШАГОВАЯ\s+ЦЕПОЧКА/gi
        ];
        
        for (const pattern of oldSections) {
          const matches = [...cleanedResponse.matchAll(pattern)];
          if (matches.length > 0) {
            // Удаляем эти разделы
            for (let i = matches.length - 1; i >= 0; i--) {
              const match = matches[i];
              const nextMatch = i < matches.length - 1 ? matches[i + 1] : null;
              const endIndex = nextMatch ? nextMatch.index : cleanedResponse.length;
              cleanedResponse = cleanedResponse.substring(0, match.index) + cleanedResponse.substring(endIndex);
            }
          }
        }
        
        // Удаляем повторы разделов - находим все разделы 1-6 и оставляем только первый цикл
        const sectionPatterns = [
          { pattern: /###\s*1[\.\)]?\s*Executive\s+Summary/i, name: 'Executive Summary' },
          { pattern: /###\s*2[\.\)]?\s*Методология/i, name: 'Методология' },
          { pattern: /###\s*3[\.\)]?\s*Детальный\s+анализ/i, name: 'Детальный анализ' },
          { pattern: /###\s*4[\.\)]?\s*Оценка\s+рисков/i, name: 'Оценка рисков' },
          { pattern: /###\s*5[\.\)]?\s*Рекомендации/i, name: 'Рекомендации' },
          { pattern: /###\s*6[\.\)]?\s*Заключение/i, name: 'Заключение' }
        ];
        
        // Находим первое вхождение каждого раздела
        const firstOccurrences: number[] = [];
        for (const section of sectionPatterns) {
          const match = cleanedResponse.match(section.pattern);
          if (match && match.index !== undefined) {
            firstOccurrences.push(match.index);
          }
        }
        
        // Если нашли все разделы, удаляем все что после последнего (Заключение)
        if (firstOccurrences.length === sectionPatterns.length) {
          const lastSectionIndex = firstOccurrences[firstOccurrences.length - 1];
          const lastSectionMatch = cleanedResponse.substring(lastSectionIndex).match(sectionPatterns[sectionPatterns.length - 1].pattern);
          if (lastSectionMatch) {
            // Находим конец раздела "Заключение"
            const afterLastSection = cleanedResponse.substring(lastSectionIndex + lastSectionMatch[0].length);
            const endMatch = afterLastSection.match(/[\s\S]*?(?=\n##|$)/);
            if (endMatch) {
              const endIndex = lastSectionIndex + lastSectionMatch[0].length + endMatch[0].length;
              cleanedResponse = cleanedResponse.substring(0, endIndex);
            }
          }
        }
        
        // Убеждаемся, что отчет начинается с "ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА"
        if (!cleanedResponse.match(/^##\s*ПОЛНЫЙ\s+ОТЧЕТ\s+ПО\s+РЕЗУЛЬТАТАМ\s+ПЕНТЕСТА/i)) {
          // Если не начинается с правильного заголовка, добавляем его
          const firstSectionMatch = cleanedResponse.match(/###\s*1[\.\)]?\s*Executive\s+Summary/i);
          if (firstSectionMatch && firstSectionMatch.index !== undefined) {
            cleanedResponse = '## ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА\n\n' + cleanedResponse.substring(firstSectionMatch.index);
          }
        }
        
        cleanedResponse = cleanedResponse.trim();
        
        return cleanedResponse + '\n\n---\n\n*Отчет сгенерирован с использованием Claude AI на основе анализа всех файлов результатов пентеста.*';
  }

  /**
   * Очистить финальный отчет от всех английских разделов
   * ВАЖНО: НЕ удаляем русский контент!
   */
  private cleanFinalReport(report: string): string {
    let cleaned = report;
    
    // ВАЖНО: НЕ удаляем раздел "📊 Детальные результаты анализа" - это русский контент!
    // Удаляем только английские заголовки разделов и их содержимое
    const englishHeaders = [
      /##\s*Security\s+Assessment\s+Report/gi,
      /##\s*Authentication\s+Exploitation\s+Evidence/gi,
      /##\s*Authentication\s+Analysis\s+Report/gi,
      /##\s*Authorization\s+Analysis\s+Report/gi,
      /##\s*Penetration\s+Test\s+Scope\s+&\s+Boundaries/gi,
      /##\s*Injection\s+Analysis\s+Report/gi,
      /##\s*Pre-Reconnaissance\s+Report/gi,
      /##\s*Reconnaissance\s+Deliverable/gi,
      /##\s*SSRF\s+Analysis\s+Report/gi,
      /##\s*Cross-Site\s+Scripting\s+\(XSS\)\s+Analysis\s+Report/gi,
      /##\s*XSS\s+Analysis\s+Report/gi,
      /##\s*Summary\s+of\s+Findings/gi,
      /##\s*Technical\s+Details/gi,
      /##\s*[A-Z][a-z\s]+Analysis\s+Report/gi,
      /##\s*[A-Z][a-z\s]+Exploitation\s+Evidence/gi,
      /##\s*[A-Z][a-z\s]+Deliverable/gi
    ];
    
    for (const pattern of englishHeaders) {
      const matches = [...cleaned.matchAll(pattern)];
      for (let i = matches.length - 1; i >= 0; i--) {
        const match = matches[i];
        if (match.index !== undefined) {
          // Находим конец этого раздела (до следующего ## или ###)
          const afterMatch = cleaned.substring(match.index);
          const endMatch = afterMatch.match(/##\s+[^\n]*\n[\s\S]*?(?=\n##\s+[^#]|\n###\s+[^#]|\n---|$)/);
          if (endMatch) {
            cleaned = cleaned.substring(0, match.index) + cleaned.substring(match.index + endMatch[0].length);
          } else {
            cleaned = cleaned.substring(0, match.index);
          }
        }
      }
    }
    
    return cleaned;
  }

  /**
   * Простая генерация цепочки взлома без AI (fallback)
   */
  private generateAttackChainSimple(content: string, targetUrl: string): string {
    // Извлекаем информацию об уязвимостях и создаем цепочку
    const vulnerabilities = this.extractVulnerabilities(content);
    
    if (vulnerabilities.length === 0) {
      return `### Результат анализа

Целевой сервис **${targetUrl}** был проанализирован, но явных уязвимостей, позволяющих построить цепочку взлома, не обнаружено.

**Рекомендации:**
- Проверьте доступность сервиса
- Убедитесь, что предоставлен исходный код для white-box анализа
- Проверьте логи пентеста для дополнительной информации
`;
    }

    let attackChain = `### Обнаружено уязвимостей: ${vulnerabilities.length}

`;

    vulnerabilities.forEach((vuln, index) => {
      attackChain += `#### Шаг ${index + 1}: ${vuln.title}

**Тип уязвимости:** ${vuln.type}  
**Критичность:** ${vuln.severity}  
**Расположение:** ${vuln.location || 'Не указано'}

**Описание:**
${vuln.description}

${vuln.proofOfConcept ? `**Proof of Concept:**
\`\`\`
${vuln.proofOfConcept}
\`\`\`
` : ''}

${vuln.recommendation ? `**Рекомендация по исправлению:**
${vuln.recommendation}
` : ''}

---

`;
    });

    return attackChain;
  }

  /**
   * Извлечь информацию об уязвимостях из содержимого
   */
  private extractVulnerabilities(content: string): Array<{
    title: string;
    type: string;
    severity: string;
    location?: string;
    description: string;
    proofOfConcept?: string;
    recommendation?: string;
  }> {
    const vulnerabilities: Array<{
      title: string;
      type: string;
      severity: string;
      location?: string;
      description: string;
      proofOfConcept?: string;
      recommendation?: string;
    }> = [];

    // Ищем паттерны уязвимостей в тексте
    const vulnPatterns = [
      /AUTH-VULN-(\d+).*?(CRITICAL|HIGH|MEDIUM|LOW)/gi,
      /XSS.*?(CRITICAL|HIGH|MEDIUM|LOW)/gi,
      /SQL.*?Injection.*?(CRITICAL|HIGH|MEDIUM|LOW)/gi,
      /SSRF.*?(CRITICAL|HIGH|MEDIUM|LOW)/gi,
    ];

    // Простой парсинг для демонстрации
    // В реальности можно использовать более сложный парсинг
    const lines = content.split('\n');
    let currentVuln: any = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Ищем заголовки уязвимостей
      if (line.match(/^###?\s+(AUTH-VULN|XSS|SQL|SSRF|Injection)/i)) {
        if (currentVuln) {
          vulnerabilities.push(currentVuln);
        }
        currentVuln = {
          title: line.replace(/^###?\s+/, '').trim(),
          type: this.extractVulnType(line),
          severity: this.extractSeverity(line) || 'MEDIUM',
          description: '',
        };
      } else if (currentVuln) {
        // Собираем описание
        if (line.match(/^\*\*Описание:\*\*|^\*\*Summary:\*\*/i)) {
          let desc = '';
          for (let j = i + 1; j < lines.length && j < i + 10; j++) {
            if (lines[j].trim() && !lines[j].match(/^\*\*/)) {
              desc += lines[j] + '\n';
            } else {
              break;
            }
          }
          currentVuln.description = desc.trim();
        }

        // Ищем Proof of Concept
        if (line.match(/Proof of Concept|PoC|Exploitation Steps/i)) {
          let poc = '';
          for (let j = i + 1; j < lines.length && j < i + 30; j++) {
            if (lines[j].trim()) {
              poc += lines[j] + '\n';
            } else if (lines[j].trim() === '' && poc.length > 50) {
              break;
            }
          }
          currentVuln.proofOfConcept = poc.trim();
        }

        // Ищем рекомендации
        if (line.match(/Recommendation|Рекомендация|Fix/i)) {
          let rec = '';
          for (let j = i + 1; j < lines.length && j < i + 10; j++) {
            if (lines[j].trim()) {
              rec += lines[j] + '\n';
            } else {
              break;
            }
          }
          currentVuln.recommendation = rec.trim();
        }
      }
    }

    if (currentVuln) {
      vulnerabilities.push(currentVuln);
    }

    return vulnerabilities;
  }

  private extractVulnType(line: string): string {
    if (line.match(/AUTH/i)) return 'Authentication';
    if (line.match(/XSS/i)) return 'Cross-Site Scripting';
    if (line.match(/SQL/i)) return 'SQL Injection';
    if (line.match(/SSRF/i)) return 'Server-Side Request Forgery';
    return 'Unknown';
  }

  private extractSeverity(line: string): string | null {
    const match = line.match(/(CRITICAL|HIGH|MEDIUM|LOW)/i);
    return match ? match[1].toUpperCase() : null;
  }

  /**
   * Получить все файлы отчетов из папки deliverables
   */
  private getAllReportFiles(deliverablesDir: string): Array<{ name: string; path: string }> {
    const files: Array<{ name: string; path: string }> = [];

    if (!existsSync(deliverablesDir)) {
      return files;
    }

    const items = readdirSync(deliverablesDir);

    for (const item of items) {
      const itemPath = join(deliverablesDir, item);
      const stat = statSync(itemPath);

      if (stat.isFile() && (item.endsWith('.md') || item.endsWith('.txt'))) {
        files.push({
          name: item,
          path: itemPath,
        });
      }
    }

    // Сортируем: сначала comprehensive report, потом остальные
    files.sort((a, b) => {
      if (a.name.includes('comprehensive')) return -1;
      if (b.name.includes('comprehensive')) return 1;
      return a.name.localeCompare(b.name);
    });

    return files;
  }

  /**
   * Конвертировать Markdown в HTML
   */
  private async markdownToHtml(markdown: string, pentest: any): Promise<string> {
    // Настраиваем marked
    marked.setOptions({
      gfm: true,
      breaks: true,
    });

    const htmlContent = marked.parse(markdown);

    const html = `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет о пентесте: ${pentest.targetUrl}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #fff;
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #dc2626;
            border-bottom: 3px solid #dc2626;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        h2 {
            color: #1f2937;
            margin-top: 40px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }
        h3 {
            color: #374151;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        h4 {
            color: #4b5563;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #d1d5db;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f3f4f6;
            font-weight: 600;
        }
        code {
            background-color: #f3f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        pre {
            background-color: #1f2937;
            color: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
        }
        pre code {
            background-color: transparent;
            padding: 0;
            color: inherit;
        }
        blockquote {
            border-left: 4px solid #dc2626;
            padding-left: 20px;
            margin: 20px 0;
            color: #6b7280;
            font-style: italic;
        }
        ul, ol {
            margin: 15px 0;
            padding-left: 30px;
        }
        li {
            margin: 8px 0;
        }
        .severity-critical {
            color: #dc2626;
            font-weight: 600;
        }
        .severity-high {
            color: #ea580c;
            font-weight: 600;
        }
        .severity-medium {
            color: #f59e0b;
            font-weight: 600;
        }
        .severity-low {
            color: #3b82f6;
            font-weight: 600;
        }
        hr {
            border: none;
            border-top: 2px solid #e5e7eb;
            margin: 40px 0;
        }
        .footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    ${htmlContent}
    <div class="footer">
        <p><strong>© 2026 Pentest.red | Enterprise Security Platform</strong></p>
        <p>Отчет сгенерирован автоматически AI Penetration Testing Platform</p>
    </div>
</body>
</html>`;

    return html;
  }

  /**
   * Конвертировать HTML в PDF
   */
  private async htmlToPdf(html: string, pentestId: string): Promise<string> {
    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    try {
      const page = await browser.newPage();
      await page.setContent(html, { waitUntil: 'networkid0' });

      const pdfPath = join(this.REPORTS_DIR, `pentest-${pentestId}-${Date.now()}.pdf`);

      await page.pdf({
        path: pdfPath,
        format: 'A4',
        printBackground: true,
        margin: {
          top: '20mm',
          right: '15mm',
          bottom: '20mm',
          left: '15mm',
        },
      });

      return pdfPath;
    } finally {
      await browser.close();
    }
  }

  /**
   * Получить путь к последнему сгенерированному PDF
   */
  getLatestPdfPath(pentestId: string): string | null {
    if (!existsSync(this.REPORTS_DIR)) {
      return null;
    }

    const files = readdirSync(this.REPORTS_DIR)
      .filter(f => f.startsWith(`pentest-${pentestId}-`) && f.endsWith('.pdf'))
      .map(f => ({
        name: f,
        path: join(this.REPORTS_DIR, f),
        time: statSync(join(this.REPORTS_DIR, f)).mtime.getTime(),
      }))
      .sort((a, b) => b.time - a.time);

    return files.length > 0 ? files[0].path : null;
  }
}

export const pdfReportService = new PdfReportService();

