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

  const prompt = `Ты эксперт по кибербезопасности и пентестингу. Проанализируй все предоставленные файлы с результатами пентеста и создай МАКСИМАЛЬНО ПОДРОБНЫЙ ОТЧЕТ для сервиса ${targetUrl}. Отчет должен быть написан на русском языке.

ВАЖНО: Отчет должен состоять ТОЛЬКО из 4 разделов, БЕЗ ПОВТОРОВ. Каждый раздел должен быть представлен ОДИН РАЗ.

1. КРАТКИЙ СПИСОК НАЙДЕННЫХ УЯЗВИМОСТЕЙ
   - Перечисли все найденные уязвимости с указанием типа, критичности (CRITICAL/HIGH/MEDIUM/LOW) и кратким описанием
   - Для каждой уязвимости укажи: ID (если есть), тип, критичность, расположение (URL/эндпоинт)
   - Используй таблицу или структурированный список

2. ПОДРОБНЫЙ ДЭШБОРД СО ВСЕМИ НАЙДЕННЫМИ МЕТРИКАМИ ТЕСТОВ, ПОПЫТОК И Т.Д.
   - Количество выполненных тестов по каждому типу уязвимости
   - Количество успешных/неуспешных попыток эксплуатации
   - Статистика по типам атак (XSS, SQL Injection, SSRF, Authentication и т.д.)
   - Метрики производительности (время выполнения, количество запросов)
   - Любые другие количественные показатели из результатов пентеста
   - Используй таблицы и графики (в текстовом формате) для наглядности

3. ПОШАГОВАЯ ЦЕПОЧКА ПОТЕНЦИАЛЬНОГО ВЗЛОМА ${targetUrl}
   - Создай детальную пошаговую цепочку взлома, описывающую КАК ИМЕННО можно взломать этот сервис
   - Каждый шаг должен быть максимально подробным с конкретными командами, URL, payloads
   - Включи все найденные уязвимости в логическую последовательность атаки
   - Для каждой уязвимости в цепочке предоставь:
     * Детальное описание как её эксплуатировать
     * Конкретные команды/запросы для эксплуатации
     * Proof-of-concept примеры
     * Как эта уязвимость связана с другими в цепочке
   - Опиши полный путь от начальной разведки до полного компрометирования системы

4. ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ПО ПРОВЕДЕННОМУ ПЕНТЕСТУ
   - Общая информация о пентесте (дата, длительность, методология)
   - Детальное описание каждой найденной уязвимости с полным контекстом
   - Рекомендации по исправлению для каждой уязвимости
   - Оценка рисков и бизнес-влияния
   - Дополнительные наблюдения и выводы

ТРЕБОВАНИЯ К ФОРМАТУ:
- Используй формат Markdown с четкой структурой
- Используй заголовки ## для разделов 1-4 (НЕ используй заголовок "Детальный AI-отчет о пентесте")
- Используй списки, таблицы для лучшей читаемости
- Все примеры кода и команды оформляй в блоки кода
- Будь максимально подробным и конкретным
- НЕ ДУБЛИРУЙ разделы - каждый раздел должен быть представлен только один раз
- НЕ добавляй разделы "Детальные результаты анализа" или "Authentication Analysis Report" - они не нужны

ФАЙЛЫ С РЕЗУЛЬТАТАМИ ПЕНТЕСТА:
${limitedContent}

Создай детальный отчет в формате Markdown на русском языке. Отчет должен содержать ТОЛЬКО 4 раздела, указанных выше, БЕЗ ПОВТОРОВ.`;

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

    // Убираем заголовок "Детальный AI-отчет о пентесте" если он есть в ответе
    let cleanedReport = attackChain;
    
    // Удаляем заголовок если он есть
    cleanedReport = cleanedReport.replace(/^##?\s*🎯\s*Детальный\s+AI-отчет\s+о\s+пентесте\s*\n*/i, '');
    cleanedReport = cleanedReport.replace(/^##?\s*🎯\s*Детальный\s+отчет\s+о\s+пентесте\s*\n*/i, '');
    
    // Удаляем раздел "Детальные результаты анализа" и все что ниже
    const analysisSectionIndex = cleanedReport.indexOf('## 📊 Детальные результаты анализа');
    if (analysisSectionIndex !== -1) {
      cleanedReport = cleanedReport.substring(0, analysisSectionIndex);
    }
    
    // Удаляем разделы "Authentication Analysis Report" и подобные
    const authReportIndex = cleanedReport.indexOf('## Authentication Analysis Report');
    if (authReportIndex !== -1) {
      cleanedReport = cleanedReport.substring(0, authReportIndex);
    }
    
    // Удаляем повторы разделов 1-4 (если они повторяются)
    const sections = [
      /##?\s*1[\.\)]\s*КРАТКИЙ\s+СПИСОК/gi,
      /##?\s*2[\.\)]\s*ПОДРОБНЫЙ\s+ДЭШБОРД/gi,
      /##?\s*3[\.\)]\s*ПОШАГОВАЯ\s+ЦЕПОЧКА/gi,
      /##?\s*4[\.\)]\s*ДЕТАЛЬНАЯ\s+ИНФОРМАЦИЯ/gi
    ];
    
    let firstCycleEnd = cleanedReport.length;
    for (let i = 0; i < sections.length; i++) {
      const matches = [...cleanedReport.matchAll(sections[i])];
      if (matches.length > 1) {
        // Найден повтор - берем только до начала второго вхождения
        firstCycleEnd = Math.min(firstCycleEnd, matches[1].index);
      }
    }
    
    if (firstCycleEnd < cleanedReport.length) {
      cleanedReport = cleanedReport.substring(0, firstCycleEnd);
      cleanedReport = cleanedReport.trim();
    }
    
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

