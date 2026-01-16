const { join } = require('path');
const { existsSync, readFileSync, readdirSync, statSync } = require('fs');
const { marked } = require('marked');
const puppeteer = require('puppeteer');
const Anthropic = require('@anthropic-ai/sdk');

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

  // Генерируем детальную цепочку взлома с AI
  const attackChain = await generateAttackChainWithAI(allContent, pentest.targetUrl, deliverablesDir);

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
${limitedContent}

Создай детальную цепочку взлома в формате Markdown.`;

  try {
    console.log('   🤖 Генерирую цепочку взлома через Claude AI...');
    const anthropic = new Anthropic({
      apiKey: apiKey,
    });

    const message = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 8000,
      messages: [
        {
          role: 'user',
          content: prompt,
        },
      ],
    });

    const attackChain = message.content[0].type === 'text' ? message.content[0].text : '';

    return `### 🎯 Детальная цепочка взлома (Attack Chain)

${attackChain}

---

*Цепочка взлома сгенерирована с использованием Claude AI на основе анализа всех файлов результатов пентеста.*
`;
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

