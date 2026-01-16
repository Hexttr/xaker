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

    // Генерируем отчет с промптом для цепочки взлома
    const attackChain = await this.generateAttackChain(allContent, pentest.targetUrl, deliverablesDir);
    
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

## 🎯 Детальная цепочка взлома (Attack Chain)

${attackChain}

---

## 📊 Детальные результаты анализа

${allContent}

---

## ⚖️ Правовая информация

Данный отчет создан в рамках авторизованного тестирования на проникновение. Все найденные уязвимости должны быть использованы исключительно для улучшения безопасности системы.

---

**© 2026 Pentest.red | Enterprise Security Platform**

*Дата создания отчета: ${new Date().toLocaleString('ru-RU')}*

*Отчет сгенерирован автоматически AI Penetration Testing Platform*
`;

    return report;
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

    const prompt = `Ты эксперт по кибербезопасности и пентестингу. Проанализируй все предоставленные файлы с результатами пентеста и создай МАКСИМАЛЬНО ПОДРОБНУЮ цепочку взлома (attack chain) для сервиса ${targetUrl}.

ТРЕБОВАНИЯ:
1. Создай пошаговую цепочку взлома, описывающую КАК ИМЕННО можно взломать этот сервис
2. Каждый шаг должен быть максимально подробным с конкретными командами, URL, payloads
3. Включи все найденные уязвимости в логическую последовательность атаки
4. Для каждой уязвимости предоставь:
   - Детальное описание как её эксплуатировать
   - Конкретные команды/запросы для эксплуатации
   - Proof-of-concept примеры
   - Как эта уязвимость связана с другими в цепочке
5. Опиши полный путь от начальной разведки до полного компрометирования системы
6. Используй формат Markdown с четкой структурой

ФАЙЛЫ С РЕЗУЛЬТАТАМИ ПЕНТЕСТА:
${allFilesContent.substring(0, 200000)} // Ограничиваем размер для API

Создай детальную цепочку взлома в формате Markdown.`;

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
        
        for await (const message of query({ prompt, options })) {
          if (message.type === 'assistant') {
            // В Shannon результат берется из assistant сообщения
            if (message.content) {
              for (const content of message.content) {
                if (content.type === 'text') {
                  result = content.text;
                  fullResponse = result;
                }
              }
            }
          } else if (message.type === 'text-delta' || message.type === 'text') {
            // Также собираем текстовые дельты
            const text = typeof message.text === 'string' ? message.text : '';
            if (text) {
              fullResponse += text;
            }
          }
        }

        // Восстанавливаем оригинальные значения прокси
        if (originalHttpProxy) process.env.HTTP_PROXY = originalHttpProxy;
        else delete process.env.HTTP_PROXY;
        if (originalHttpsProxy) process.env.HTTPS_PROXY = originalHttpsProxy;
        else delete process.env.HTTPS_PROXY;

        const finalResponse = result || fullResponse;

        return `### 🎯 Детальная цепочка взлома (Attack Chain)

${finalResponse}

---

*Цепочка взлома сгенерирована с использованием Claude AI на основе анализа всех файлов результатов пентеста.*
`;
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

