const { join } = require('path');
const { existsSync, readFileSync, readdirSync, statSync } = require('fs');
const { marked } = require('marked');
const puppeteer = require('puppeteer');
const { query } = require('@anthropic-ai/claude-agent-sdk');

// ID пентестов
const TEST_2_ID = '19fc79c3-ecc1-4463-ac00-06b8f1f621fa';
const TEST_4_ID = '7dd2333d-0f8f-4cc5-8945-f50ac3919264';

// Загружаем данные пентестов
function loadPentestData(pentestId) {
  const dataPath = join(__dirname, 'pentests-data', `${pentestId}.json`);
  if (!existsSync(dataPath)) {
    throw new Error(`Файл данных пентеста не найден: ${dataPath}`);
  }
  const data = JSON.parse(readFileSync(dataPath, 'utf-8'));
  return data.pentest;
}

// Получить все файлы отчетов
function getAllReportFiles(deliverablesDir) {
  const files = [];
  if (!existsSync(deliverablesDir)) {
    return files;
  }
  const items = readdirSync(deliverablesDir);
  for (const item of items) {
    const itemPath = join(deliverablesDir, item);
    const stat = statSync(itemPath);
    if (stat.isFile() && (item.endsWith('.md') || item.endsWith('.txt'))) {
      files.push({ name: item, path: itemPath });
    }
  }
  files.sort((a, b) => {
    if (a.name.includes('comprehensive')) return -1;
    if (b.name.includes('comprehensive')) return 1;
    return a.name.localeCompare(b.name);
  });
  return files;
}

// Генерировать Markdown отчет
async function generateMarkdownReport(pentestId, pentest, deliverablesDir) {
  const files = getAllReportFiles(deliverablesDir);
  let allContent = '';
  
  for (const file of files) {
    try {
      const content = readFileSync(file.path, 'utf-8');
      allContent += `\n\n## ${file.name}\n\n${content}\n\n`;
    } catch (error) {
      console.error(`Ошибка чтения файла ${file.path}:`, error);
    }
  }

  // Генерируем детальный AI-отчет
  const aiReport = await generateAttackChainWithAI(allContent, pentest.targetUrl, deliverablesDir);

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

// Генерировать детальную цепочку взлома с использованием Claude AI
async function generateAttackChainWithAI(content, targetUrl, deliverablesDir) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  
  if (!apiKey || apiKey === 'your_api_key_here') {
    console.log('   ⚠️  ANTHROPIC_API_KEY не установлен, используется простая генерация');
    return generateAttackChainSimple(content, targetUrl);
  }

  const files = getAllReportFiles(deliverablesDir);
  let allFilesContent = '';
  for (const file of files) {
    try {
      const fileContent = readFileSync(file.path, 'utf-8');
      allFilesContent += `\n\n=== ${file.name} ===\n\n${fileContent}\n\n`;
    } catch (error) {
      // Игнорируем ошибки
    }
  }

  // Ограничиваем размер для API (200k символов)
  const limitedContent = allFilesContent.substring(0, 200000);

  const prompt = `Ты эксперт по кибербезопасности и пентестингу. Проанализируй все предоставленные файлы с результатами пентеста и создай ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА для сервиса ${targetUrl}. Отчет должен быть написан на русском языке в БИЗНЕС-ФОРМАТЕ.

ВАЖНО: Создай ТОЛЬКО ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА. НЕ создавай дополнительные разделы, списки уязвимостей, дэшборды или цепочки взлома отдельно.

СТРУКТУРА ОТЧЕТА (БИЗНЕС-ФОРМАТ):

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
   Для КАЖДОЙ найденной уязвимости предоставь:
   - **Название уязвимости** (четкое и понятное)
   - **Критичность** (CRITICAL/HIGH/MEDIUM/LOW)
   - **Расположение** (URL, эндпоинт, компонент)
   - **Детальное описание** (что именно не так, почему это проблема)
   - **Техническое описание** (как воспроизвести, proof-of-concept)
   - **Бизнес-влияние** (какой ущерб может быть нанесен)
   - **Рекомендации по исправлению** (конкретные шаги для устранения)
   - **Оценка сложности исправления** (простая/средняя/сложная)

### 4. Оценка рисков
   - Общая оценка рисков для бизнеса
   - Приоритизация уязвимостей по бизнес-критичности
   - Потенциальный ущерб от эксплуатации уязвимостей
   - Временные рамки для исправления критических уязвимостей

### 5. Рекомендации и план действий
   - Общие рекомендации по улучшению безопасности
   - План действий по устранению уязвимостей (приоритизированный)
   - Рекомендации по долгосрочному улучшению безопасности
   - Best practices для предотвращения подобных уязвимостей

### 6. Заключение
   - Общие выводы по результатам пентеста
   - Оценка текущего состояния безопасности
   - Рекомендации по дальнейшему мониторингу

ТРЕБОВАНИЯ К БИЗНЕС-ФОРМАТУ:
- Профессиональный, структурированный язык
- Используй заголовки ## и ### для структурирования
- Используй таблицы для сравнения и статистики
- Используй списки для рекомендаций
- Все примеры кода и команды оформляй в блоки кода
- Будь максимально подробным и конкретным
- НЕ ДУБЛИРУЙ информацию
- НЕ создавай дополнительные разделы вне указанной структуры
- Фокус на бизнес-ценности и практических рекомендациях
- ОТЧЕТ ДОЛЖЕН БЫТЬ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ
- НЕ добавляй английские разделы, заголовки или документацию
- НЕ добавляй разделы "Authentication Analysis Report", "Security Assessment Report" и подобные
- НЕ добавляй техническую документацию на английском языке

ФАЙЛЫ С РЕЗУЛЬТАТАМИ ПЕНТЕСТА:
${limitedContent}

Создай ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА в бизнес-формате на русском языке. Отчет должен содержать ТОЛЬКО указанную структуру, БЕЗ ПОВТОРОВ, лишних разделов и английской документации.`;

  try {
    console.log('   🤖 Генерирую цепочку взлома через Claude AI...');
    
    // Настраиваем прокси для VPN (как в Shannon)
    const proxyUrl = process.env.HTTP_PROXY || process.env.HTTPS_PROXY || process.env.http_proxy || process.env.https_proxy || 'http://127.0.0.1:12334';
    
    if (proxyUrl) {
      console.log(`   🌐 Используется прокси: ${proxyUrl}`);
      // Устанавливаем переменные окружения для прокси
      process.env.HTTP_PROXY = proxyUrl;
      process.env.HTTPS_PROXY = proxyUrl;
    }
    
    // Опции для query (как в Shannon)
    const options = {
      apiKey: apiKey,
      model: 'claude-sonnet-4-5-20250929', // Используем ту же модель, что и Shannon
      maxTurns: 50, // Ограничиваем количество поворотов для генерации отчета
      cwd: deliverablesDir, // Рабочая директория
      permissionMode: 'bypassPermissions', // Обходим проверки разрешений
    };

    // Используем query из Claude Agent SDK (как в Shannon)
    let fullResponse = '';
    let result = null;
    let messageCount = 0;
    
    console.log('   📡 Отправляю запрос к Claude AI...');
    for await (const message of query({ prompt, options })) {
      messageCount++;
      
      // Обрабатываем сообщение типа 'result' - это финальный результат (как в Shannon)
      if (message.type === 'result') {
        // В Shannon результат берется из resultMessage.result
        if (message.result && typeof message.result === 'string') {
          // Добавляем к накопленному ответу, а не заменяем
          if (fullResponse && !fullResponse.includes(message.result)) {
            fullResponse += '\n\n' + message.result;
          } else if (!fullResponse) {
            fullResponse = message.result;
          }
          result = fullResponse;
          console.log(`   ✅ Получен финальный результат из result.result (${message.result.length} символов)`);
        } else if (message.content) {
          if (typeof message.content === 'string') {
            if (fullResponse && !fullResponse.includes(message.content)) {
              fullResponse += '\n\n' + message.content;
            } else if (!fullResponse) {
              fullResponse = message.content;
            }
            result = fullResponse;
            console.log(`   ✅ Получен результат из result.content (${message.content.length} символов)`);
          }
        } else if (message.text) {
          if (fullResponse && !fullResponse.includes(message.text)) {
            fullResponse += '\n\n' + message.text;
          } else if (!fullResponse) {
            fullResponse = message.text;
          }
          result = fullResponse;
          console.log(`   ✅ Получен результат из result.text (${message.text.length} символов)`);
        }
      } else if (message.type === 'assistant') {
        // В Shannon также собираем из assistant сообщений - ВАЖНО: собираем ВСЕ сообщения
        if (message.message && message.message.content) {
          const content = Array.isArray(message.message.content)
            ? message.message.content.map((c) => c.text || JSON.stringify(c)).join('\n')
            : String(message.message.content);
          if (content && typeof content === 'string' && content.trim().length > 0) {
            // Добавляем к накопленному ответу
            fullResponse += content + '\n\n';
            console.log(`   ✅ Получен текст из assistant.message.content (${content.length} символов, всего: ${fullResponse.length})`);
          }
        } else if (message.content && Array.isArray(message.content)) {
          for (const content of message.content) {
            if (content.type === 'text' && content.text && content.text.trim().length > 0) {
              fullResponse += content.text + '\n\n';
              console.log(`   ✅ Получен текст из assistant.content[] (${content.text.length} символов, всего: ${fullResponse.length})`);
            }
          }
        }
      }
    }

    console.log(`   📊 Всего сообщений: ${messageCount}, Длина ответа: ${fullResponse.length}`);
    
    const attackChain = result || fullResponse;
    
    if (!attackChain || attackChain.trim().length === 0) {
      console.log('   ⚠️  Цепочка взлома пуста, используется fallback');
      return generateAttackChainSimple(content, targetUrl);
    }
    
    console.log(`   ✅ Цепочка взлома сгенерирована (${attackChain.length} символов)`);

    // Очищаем ответ от лишних разделов - оставляем ТОЛЬКО "ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА"
    let cleanedReport = attackChain;
    
    // Находим начало "ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА"
    const fullReportPattern = /##\s*ПОЛНЫЙ\s+ОТЧЕТ\s+ПО\s+РЕЗУЛЬТАТАМ\s+ПЕНТЕСТА/i;
    const fullReportMatch = cleanedReport.match(fullReportPattern);
    
    if (fullReportMatch && fullReportMatch.index !== undefined) {
      // Удаляем все что до начала отчета
      cleanedReport = cleanedReport.substring(fullReportMatch.index);
    } else {
      // Если не нашли точный заголовок, ищем альтернативные варианты
      const altPatterns = [
        /##\s*ПОЛНЫЙ\s+ОТЧЕТ/i,
        /##\s*ОТЧЕТ\s+ПО\s+РЕЗУЛЬТАТАМ/i,
        /###\s*1[\.\)]?\s*Executive\s+Summary/i
      ];
      
      for (const pattern of altPatterns) {
        const match = cleanedReport.match(pattern);
        if (match && match.index !== undefined) {
          // Ищем начало отчета (может быть немного выше)
          const startIndex = Math.max(0, match.index - 200);
          cleanedReport = cleanedReport.substring(startIndex);
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
      cleanedReport = cleanedReport.replace(pattern, '');
    }
    
    // Находим конец отчета - ищем раздел "Заключение" (раздел 6)
    const conclusionPattern = /###\s*6[\.\)]?\s*Заключение/i;
    const conclusionMatch = cleanedReport.match(conclusionPattern);
    
    if (conclusionMatch && conclusionMatch.index !== undefined) {
      // Находим конец раздела "Заключение" - до следующего ## или до конца
      const afterConclusion = cleanedReport.substring(conclusionMatch.index);
      const endMatch = afterConclusion.match(/###\s*6[\.\)]?\s*Заключение[\s\S]*?(?=\n##\s+[^#]|\n---|$)/i);
      
      if (endMatch) {
        const endIndex = conclusionMatch.index + endMatch[0].length;
        cleanedReport = cleanedReport.substring(0, endIndex);
      } else {
        // Если не нашли конец, берем до следующего ## или до конца
        const nextSectionMatch = afterConclusion.match(/###\s*6[\.\)]?\s*Заключение[\s\S]*?(?=\n##|$)/i);
        if (nextSectionMatch) {
          const endIndex = conclusionMatch.index + nextSectionMatch[0].length;
          cleanedReport = cleanedReport.substring(0, endIndex);
        }
      }
    }
    
    // Удаляем все английские разделы после заключения
    const englishPatterns = [
      /##\s*[A-Z][a-z\s]+Report/gi,
      /##\s*Authentication\s+Analysis/gi,
      /##\s*Security\s+Assessment/gi,
      /##\s*Detailed\s+Analysis/gi,
      /##\s*[A-Z][a-z\s]+Dashboard/gi
    ];
    
    for (const pattern of englishPatterns) {
      const matches = [...cleanedReport.matchAll(pattern)];
      for (const match of matches) {
        if (match.index !== undefined) {
          // Удаляем английский раздел до следующего ## или до конца
          const afterMatch = cleanedReport.substring(match.index);
          const endMatch = afterMatch.match(/##\s+[^\n]*\n[\s\S]*?(?=\n##|$)/);
          if (endMatch) {
            cleanedReport = cleanedReport.substring(0, match.index) + cleanedReport.substring(match.index + endMatch[0].length);
          } else {
            cleanedReport = cleanedReport.substring(0, match.index);
          }
        }
      }
    }
    
    // Удаляем раздел "Детальные результаты анализа" и все что ниже
    const analysisSectionIndex = cleanedReport.indexOf('## 📊 Детальные результаты анализа');
    if (analysisSectionIndex !== -1) {
      cleanedReport = cleanedReport.substring(0, analysisSectionIndex);
    }
    
    // Удаляем старые разделы 1-4 если они есть (КРАТКИЙ СПИСОК, ДЭШБОРД, ЦЕПОЧКА)
    const oldSections = [
      /##?\s*1[\.\)]\s*КРАТКИЙ\s+СПИСОК/gi,
      /##?\s*2[\.\)]\s*ПОДРОБНЫЙ\s+ДЭШБОРД/gi,
      /##?\s*3[\.\)]\s*ПОШАГОВАЯ\s+ЦЕПОЧКА/gi
    ];
    
    for (const pattern of oldSections) {
      const matches = [...cleanedReport.matchAll(pattern)];
      if (matches.length > 0) {
        // Удаляем эти разделы
        for (let i = matches.length - 1; i >= 0; i--) {
          const match = matches[i];
          const nextMatch = i < matches.length - 1 ? matches[i + 1] : null;
          const endIndex = nextMatch ? nextMatch.index : cleanedReport.length;
          cleanedReport = cleanedReport.substring(0, match.index) + cleanedReport.substring(endIndex);
        }
      }
    }
    
    // Убеждаемся, что отчет начинается с "ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА"
    if (!cleanedReport.match(/^##\s*ПОЛНЫЙ\s+ОТЧЕТ\s+ПО\s+РЕЗУЛЬТАТАМ\s+ПЕНТЕСТА/i)) {
      // Если не начинается с правильного заголовка, добавляем его
      const firstSectionMatch = cleanedReport.match(/###\s*1[\.\)]?\s*Executive\s+Summary/i);
      if (firstSectionMatch && firstSectionMatch.index !== undefined) {
        cleanedReport = '## ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА\n\n' + cleanedReport.substring(firstSectionMatch.index);
      }
    }
    
    cleanedReport = cleanedReport.trim();
    
    return cleanedReport + '\n\n---\n\n*Отчет сгенерирован с использованием Claude AI на основе анализа всех файлов результатов пентеста.*';
  } catch (error) {
    console.error(`   ❌ Ошибка при генерации через AI: ${error.message}`);
    console.log('   ⚠️  Использую простую генерацию без AI');
    return generateAttackChainSimple(content, targetUrl);
  }
}

// Простая генерация цепочки взлома без AI (fallback)
function generateAttackChainSimple(content, targetUrl) {
  // Простая реализация - извлекаем основные уязвимости
  const vulnMatches = content.match(/AUTH-VULN-\d+|XSS|SQL.*?Injection|SSRF/gi);
  const vulnerabilities = vulnMatches ? [...new Set(vulnMatches)] : [];

  if (vulnerabilities.length === 0) {
    return `### Результат анализа

Целевой сервис **${targetUrl}** был проанализирован. Детальная цепочка взлома будет доступна при использовании Claude AI (установите ANTHROPIC_API_KEY).

**Рекомендации:**
- Установите ANTHROPIC_API_KEY для генерации детальной цепочки взлома через AI
- Проверьте логи пентеста для дополнительной информации
`;
  }

  return `### Обнаружено уязвимостей: ${vulnerabilities.length}

Для генерации детальной цепочки взлома установите ANTHROPIC_API_KEY и используйте AI-анализ.

**Найденные типы уязвимостей:**
${vulnerabilities.map(v => `- ${v}`).join('\n')}

---
`;
}

// Конвертировать Markdown в HTML
async function markdownToHtml(markdown, pentest) {
  marked.setOptions({ gfm: true, breaks: true });
  const htmlContent = marked.parse(markdown);

  const html = `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет о пентесте: ${pentest.targetUrl}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #fff;
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 { color: #dc2626; border-bottom: 3px solid #dc2626; padding-bottom: 10px; margin-bottom: 30px; }
        h2 { color: #1f2937; margin-top: 40px; margin-bottom: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }
        h3 { color: #374151; margin-top: 30px; margin-bottom: 15px; }
        h4 { color: #4b5563; margin-top: 20px; margin-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #d1d5db; padding: 12px; text-align: left; }
        th { background-color: #f3f4f6; font-weight: 600; }
        code { background-color: #f3f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 0.9em; }
        pre { background-color: #1f2937; color: #f9fafb; padding: 20px; border-radius: 8px; overflow-x: auto; margin: 20px 0; }
        pre code { background-color: transparent; padding: 0; color: inherit; }
        blockquote { border-left: 4px solid #dc2626; padding-left: 20px; margin: 20px 0; color: #6b7280; font-style: italic; }
        ul, ol { margin: 15px 0; padding-left: 30px; }
        li { margin: 8px 0; }
        hr { border: none; border-top: 2px solid #e5e7eb; margin: 40px 0; }
        .footer { margin-top: 60px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 0.9em; }
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

// Конвертировать HTML в PDF
async function htmlToPdf(html, pentestId) {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle0' });

    const reportsDir = join(__dirname, 'reports');
    if (!existsSync(reportsDir)) {
      require('fs').mkdirSync(reportsDir, { recursive: true });
    }

    const pdfPath = join(reportsDir, `pentest-${pentestId}-${Date.now()}.pdf`);

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

// Главная функция
async function main() {
  const pentestIds = process.argv.slice(2);
  
  if (pentestIds.length === 0) {
    console.log('Использование: node generate-pdf.js <pentest-id1> [pentest-id2] ...');
    console.log('Пример: node generate-pdf.js 19fc79c3-ecc1-4463-ac00-06b8f1f621fa 7dd2333d-0f8f-4cc5-8945-f50ac3919264');
    console.log('\nИли используйте предустановленные тесты:');
    console.log('  node generate-pdf.js --test2 --test4');
    process.exit(1);
  }

  let idsToProcess = [];
  
  if (pentestIds.includes('--test2')) {
    idsToProcess.push(TEST_2_ID);
  }
  if (pentestIds.includes('--test4')) {
    idsToProcess.push(TEST_4_ID);
  }
  
  // Добавляем явно указанные ID
  idsToProcess.push(...pentestIds.filter(id => !id.startsWith('--')));

  if (idsToProcess.length === 0) {
    console.log('❌ Не указаны ID пентестов для генерации');
    process.exit(1);
  }

  console.log(`\n🚀 Генерация PDF отчетов для ${idsToProcess.length} пентестов...\n`);

  for (const pentestId of idsToProcess) {
    try {
      console.log(`📄 Генерация отчета для пентеста: ${pentestId}`);
      
      const pentest = loadPentestData(pentestId);
      console.log(`   Название: ${pentest.name}`);
      console.log(`   URL: ${pentest.targetUrl}`);
      
      const pentestDir = join(__dirname, 'pentests', pentestId);
      const deliverablesDir = join(pentestDir, 'deliverables');
      
      if (!existsSync(deliverablesDir)) {
        throw new Error(`Папка deliverables не найдена: ${deliverablesDir}`);
      }
      
      const markdown = await generateMarkdownReport(pentestId, pentest, deliverablesDir);
      const html = await markdownToHtml(markdown, pentest);
      const pdfPath = await htmlToPdf(html, pentestId);
      
      console.log(`   ✅ PDF успешно сгенерирован: ${pdfPath}\n`);
    } catch (error) {
      console.error(`   ❌ Ошибка: ${error.message}\n`);
    }
  }

  console.log('✅ Генерация завершена!');
}

main().catch(console.error);

