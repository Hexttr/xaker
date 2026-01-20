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

// Очистить отчет от английских разделов и повторов, а также удалить рассуждения Claude
function cleanReportFromEnglishSections(response) {
  let cleanedReport = response;
  
  // УДАЛЯЕМ все рассуждения Claude перед началом отчета
  // Ищем начало реального отчета: "### 1. Executive Summary" или "## ПОЛНЫЙ ОТЧЕТ"
  const reportStartPatterns = [
    /###\s*1[\.\)]?\s*Executive\s+Summary/i,
    /##\s*ПОЛНЫЙ\s+ОТЧЕТ\s+ПО\s+РЕЗУЛЬТАТАМ\s+ПЕНТЕСТА/i,
    /##\s*ПОЛНЫЙ\s+ОТЧЕТ/i,
    /##\s*ОТЧЕТ\s+ПО\s+РЕЗУЛЬТАТАМ/i
  ];
  
  let reportStartIndex = -1;
  for (const pattern of reportStartPatterns) {
    const match = cleanedReport.match(pattern);
    if (match && match.index !== undefined) {
      reportStartIndex = match.index;
      break;
    }
  }
  
  // Если нашли начало отчета - удаляем все что до него (рассуждения Claude)
  if (reportStartIndex > 0) {
    // Ищем текст до начала отчета - удаляем весь контент до первого найденного паттерна
    cleanedReport = cleanedReport.substring(reportStartIndex);
  }
  
  // Находим начало "ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА" (если есть)
  const fullReportPattern = /##\s*ПОЛНЫЙ\s+ОТЧЕТ\s+ПО\s+РЕЗУЛЬТАТАМ\s+ПЕНТЕСТА/i;
  const fullReportMatch = cleanedReport.match(fullReportPattern);
  
  if (fullReportMatch && fullReportMatch.index !== undefined) {
    cleanedReport = cleanedReport.substring(fullReportMatch.index);
  }
  
  // Удаляем английские разделы в начале
  const englishSections = [
    /^[^#]*##\s*[A-Z][a-z]+.*?(?=##\s*ПОЛНЫЙ\s+ОТЧЕТ|###\s*1[\.\)]?\s*Executive)/is,
    /^[^#]*##\s*Executive\s+Summary.*?(?=##\s*ПОЛНЫЙ\s+ОТЧЕТ|###\s*1[\.\)]?\s*Executive)/is,
    /^[^#]*##\s*[A-Z][a-z\s]+Report.*?(?=##\s*ПОЛНЫЙ\s+ОТЧЕТ|###\s*1[\.\)]?\s*Executive)/is
  ];
  
  for (const pattern of englishSections) {
    cleanedReport = cleanedReport.replace(pattern, '');
  }
  
  // Находим конец отчета - раздел "Заключение" (раздел 6)
  const conclusionPattern = /###\s*6[\.\)]?\s*Заключение/i;
  const conclusionMatch = cleanedReport.match(conclusionPattern);
  
  if (conclusionMatch && conclusionMatch.index !== undefined) {
    const afterConclusion = cleanedReport.substring(conclusionMatch.index);
    const endMatch = afterConclusion.match(/###\s*6[\.\)]?\s*Заключение[\s\S]*?(?=\n##\s+[^#]|\n---|$)/i);
    
    if (endMatch) {
      const endIndex = conclusionMatch.index + endMatch[0].length;
      cleanedReport = cleanedReport.substring(0, endIndex);
    } else {
      const nextSectionMatch = afterConclusion.match(/###\s*6[\.\)]?\s*Заключение[\s\S]*?(?=\n##|$)/i);
      if (nextSectionMatch) {
        const endIndex = conclusionMatch.index + nextSectionMatch[0].length;
        cleanedReport = cleanedReport.substring(0, endIndex);
      }
    }
  }
  
  // Удаляем английские разделы после заключения
  // ВАЖНО: Добавляем конкретные заголовки из исходных файлов
  const englishPatterns = [
    /##\s*[A-Z][a-z\s]+Report/gi,
    /##\s*Authentication\s+Analysis/gi,
    /##\s*Security\s+Assessment/gi,
    /##\s*Detailed\s+Analysis/gi,
    /##\s*[A-Z][a-z\s]+Dashboard/gi,
    /##\s*Executive\s+Summary/gi,
    /##\s*[A-Z][a-z\s]+Analysis/gi,
    /##\s*Summary\s+of\s+Findings/gi,
    /##\s*Technical\s+Details/gi,
    /##\s*[A-Z][a-z\s]+Vulnerability/gi,
    /##\s*[A-Z][a-z\s]+Bypass/gi,
    /##\s*[A-Z][a-z\s]+Access/gi,
    /##\s*[A-Z][a-z\s]+Endpoint/gi,
    /##\s*Vulnerable\s+location/gi,
    /##\s*Overview/gi,
    /##\s*Impact/gi,
    /##\s*Severity/gi,
    /##\s*Prerequisites/gi,
    /##\s*Notes/gi,
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
  
  if (conclusionMatch && conclusionMatch.index !== undefined) {
    const afterConclusion = cleanedReport.substring(conclusionMatch.index + conclusionMatch[0].length);
    let hasEnglishAfter = false;
    for (const pattern of englishPatterns) {
      if (pattern.test(afterConclusion)) {
        hasEnglishAfter = true;
        break;
      }
    }
    
    if (hasEnglishAfter) {
      cleanedReport = cleanedReport.substring(0, conclusionMatch.index + conclusionMatch[0].length);
    }
  }
  
  // Удаляем английские разделы внутри отчета
  const section1Pattern = /###\s*1[\.\)]?\s*Executive\s+Summary/i;
  const section6Pattern = /###\s*6[\.\)]?\s*Заключение/i;
  const section1Match = cleanedReport.match(section1Pattern);
  const section6Match = cleanedReport.match(section6Pattern);
  
  let reportStart = 0;
  let reportEnd = cleanedReport.length;
  
  if (section1Match && section1Match.index !== undefined) {
    reportStart = section1Match.index;
  }
  if (section6Match && section6Match.index !== undefined) {
    const afterSection6 = cleanedReport.substring(section6Match.index);
    const endMatch = afterSection6.match(/###\s*6[\.\)]?\s*Заключение[\s\S]*?(?=\n###\s*[1-6]|\n##\s+[^#]|\n---|$)/i);
    if (endMatch) {
      reportEnd = section6Match.index + endMatch[0].length;
    }
  }
  
  for (const pattern of englishPatterns) {
    const matches = [...cleanedReport.matchAll(pattern)];
    for (const match of matches) {
      if (match.index !== undefined) {
        const beforeMatch = cleanedReport.substring(Math.max(0, match.index - 100), match.index);
        if (beforeMatch.includes('### 1') || beforeMatch.includes('### 1.')) {
          continue;
        }
        
        if (match.index >= reportStart && match.index < reportEnd) {
          const afterMatch = cleanedReport.substring(match.index);
          const endMatch = afterMatch.match(/##\s+[^\n]*\n[\s\S]*?(?=\n###\s*[1-6]|\n##\s+[^#]|\n---|$)/);
          if (endMatch) {
            cleanedReport = cleanedReport.substring(0, match.index) + cleanedReport.substring(match.index + endMatch[0].length);
            reportEnd -= endMatch[0].length;
          } else {
            cleanedReport = cleanedReport.substring(0, match.index);
            reportEnd = match.index;
          }
          continue;
        }
        
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
  
  // ВАЖНО: НЕ удаляем раздел "📊 Детальные результаты анализа" - это русский контент!
  // Удаляем только английские заголовки разделов
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
    /##\s*Notes/gi
  ];
  
  for (const pattern of englishSectionHeaders) {
    const matches = [...cleanedReport.matchAll(pattern)];
    for (const match of matches) {
      if (match.index !== undefined) {
        const beforeMatch = cleanedReport.substring(Math.max(0, match.index - 200), match.index);
        if (beforeMatch.includes('### 1') || beforeMatch.includes('### 2') || beforeMatch.includes('### 3') || 
            beforeMatch.includes('### 4') || beforeMatch.includes('### 5') || beforeMatch.includes('### 6') ||
            beforeMatch.includes('ПОЛНЫЙ ОТЧЕТ')) {
          continue;
        }
        
        const afterMatch = cleanedReport.substring(match.index);
        const endMatch = afterMatch.match(/##\s+[^\n]*\n[\s\S]*?(?=\n###\s*[1-6]|\n##\s+[^#]|\n---|$)/);
        if (endMatch) {
          cleanedReport = cleanedReport.substring(0, match.index) + cleanedReport.substring(match.index + endMatch[0].length);
        } else {
          cleanedReport = cleanedReport.substring(0, match.index);
        }
      }
    }
  }
  
  // Удаляем старые разделы 1-4
  const oldSections = [
    /##?\s*1[\.\)]\s*КРАТКИЙ\s+СПИСОК/gi,
    /##?\s*2[\.\)]\s*ПОДРОБНЫЙ\s+ДЭШБОРД/gi,
    /##?\s*3[\.\)]\s*ПОШАГОВАЯ\s+ЦЕПОЧКА/gi
  ];
  
  for (const pattern of oldSections) {
    const matches = [...cleanedReport.matchAll(pattern)];
    if (matches.length > 0) {
      for (let i = matches.length - 1; i >= 0; i--) {
        const match = matches[i];
        const nextMatch = i < matches.length - 1 ? matches[i + 1] : null;
        const endIndex = nextMatch ? nextMatch.index : cleanedReport.length;
        cleanedReport = cleanedReport.substring(0, match.index) + cleanedReport.substring(endIndex);
      }
    }
  }
  
  // Удаляем повторы разделов 1-6
  const sectionPatterns = [
    { pattern: /###\s*1[\.\)]?\s*Executive\s+Summary/i, name: 'Executive Summary' },
    { pattern: /###\s*2[\.\)]?\s*Методология/i, name: 'Методология' },
    { pattern: /###\s*3[\.\)]?\s*Детальный\s+анализ/i, name: 'Детальный анализ' },
    { pattern: /###\s*4[\.\)]?\s*Оценка\s+рисков/i, name: 'Оценка рисков' },
    { pattern: /###\s*5[\.\)]?\s*Рекомендации/i, name: 'Рекомендации' },
    { pattern: /###\s*6[\.\)]?\s*Заключение/i, name: 'Заключение' }
  ];
  
  const firstOccurrences = [];
  for (const section of sectionPatterns) {
    const match = cleanedReport.match(section.pattern);
    if (match && match.index !== undefined) {
      firstOccurrences.push(match.index);
    }
  }
  
  if (firstOccurrences.length === sectionPatterns.length) {
    const lastSectionIndex = firstOccurrences[firstOccurrences.length - 1];
    const lastSectionMatch = cleanedReport.substring(lastSectionIndex).match(sectionPatterns[sectionPatterns.length - 1].pattern);
    if (lastSectionMatch) {
      const afterLastSection = cleanedReport.substring(lastSectionIndex + lastSectionMatch[0].length);
      const endMatch = afterLastSection.match(/[\s\S]*?(?=\n##|$)/);
      if (endMatch) {
        const endIndex = lastSectionIndex + lastSectionMatch[0].length + endMatch[0].length;
        cleanedReport = cleanedReport.substring(0, endIndex);
      }
    }
  }
  
  // Убеждаемся, что отчет начинается с "ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА"
  if (!cleanedReport.match(/^##\s*ПОЛНЫЙ\s+ОТЧЕТ\s+ПО\s+РЕЗУЛЬТАТАМ\s+ПЕНТЕСТА/i)) {
    const firstSectionMatch = cleanedReport.match(/###\s*1[\.\)]?\s*Executive\s+Summary/i);
    if (firstSectionMatch && firstSectionMatch.index !== undefined) {
      cleanedReport = '## ПОЛНЫЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА\n\n' + cleanedReport.substring(firstSectionMatch.index);
    }
  }
  
  cleanedReport = cleanedReport.trim();
  
  return cleanedReport + '\n\n---\n\n*Отчет сгенерирован с использованием Claude AI на основе анализа всех файлов результатов пентеста.*';
}

// Очистить финальный отчет от всех английских разделов
// ВАЖНО: НЕ удаляем русский контент!
function cleanFinalReport(report) {
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
  let aiReport = await generateAttackChainWithAI(allContent, pentest.targetUrl, deliverablesDir);
  
  // Применяем очистку к результату независимо от источника (AI или fallback)
  aiReport = cleanReportFromEnglishSections(aiReport);

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

## 🔗 Цепочка взлома

${await generateAttackChainSection(allContent, pentest.targetUrl, deliverablesDir)}

---

${aiReport}

---

## 📊 Детальные результаты анализа

${await generateDetailedAnalysis(allContent, pentest.targetUrl, deliverablesDir)}

---

## ⚖️ Правовая информация

Данный отчет создан в рамках авторизованного тестирования на проникновение. Все найденные уязвимости должны быть использованы исключительно для улучшения безопасности системы.

---

**© 2026 Pentest.red | Enterprise Security Platform**

*Дата создания отчета: ${new Date().toLocaleString('ru-RU')}*

*Отчет сгенерирован автоматически AI Penetration Testing Platform`
;

  // ВАЖНО: Применяем очистку ко всему финальному отчету для удаления английских разделов
  return cleanFinalReport(report);
}

// Генерировать краткий детальный анализ через AI (вместо копирования всех файлов)
async function generateDetailedAnalysis(allContent, targetUrl, deliverablesDir) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  
  if (!apiKey || apiKey === 'your_api_key_here') {
    return 'Детальный анализ доступен при использовании Claude AI (установите ANTHROPIC_API_KEY).';
  }

  const prompt = `Ты эксперт по кибербезопасности. На основе анализа файлов результатов пентеста создай КРАТКИЙ детальный анализ (максимум 2000 слов, только на русском языке).

ВАЖНО:
- НЕ копируй фрагменты файлов, код или команды
- Кратко опиши КЛЮЧЕВЫЕ моменты из анализа файлов
- Включи только САМОЕ ВАЖНОЕ: основные уязвимости, их влияние, рекомендации
- Используй правильное форматирование Markdown: заголовки, списки, абзацы
- Каждый абзац - отдельная строка с пустой строкой между абзацами
- Используй ### для подразделов, **жирный** для важного, списки для перечислений

Файлы для анализа:
${allContent.substring(0, 100000)}

Создай краткий структурированный анализ на русском языке.`;

  try {
    const proxyUrl = process.env.HTTP_PROXY || process.env.HTTPS_PROXY || 'http://127.0.0.1:12334';
    if (proxyUrl) {
      process.env.HTTP_PROXY = proxyUrl;
      process.env.HTTPS_PROXY = proxyUrl;
    }

    const options = {
      apiKey: apiKey,
      model: 'claude-sonnet-4-5-20250929',
      maxTurns: 30,
      cwd: deliverablesDir,
      permissionMode: 'bypassPermissions',
    };

    let fullResponse = '';
    let result = null;
    let messageCount = 0;
    
    for await (const message of query({ prompt, options })) {
      messageCount++;
      
      if (message.type === 'result') {
        if (message.result && typeof message.result === 'string') {
          fullResponse = message.result;
          result = fullResponse;
        }
      } else if (message.type === 'assistant') {
        const assistantMsg = message;
        if (assistantMsg.message && assistantMsg.message.content) {
          const content = Array.isArray(assistantMsg.message.content)
            ? assistantMsg.message.content.map((c) => c.text || JSON.stringify(c)).join('\n')
            : String(assistantMsg.message.content);
          if (content && typeof content === 'string' && content.trim().length > 0) {
            fullResponse += content + '\n\n';
          }
        }
      }
    }
    
    let finalResponse = result || fullResponse;
    
    // Ограничиваем размер до 2000 слов (~15000 символов)
    const MAX_LENGTH = 15000;
    if (finalResponse.length > MAX_LENGTH) {
      finalResponse = finalResponse.substring(0, MAX_LENGTH);
      const lastSentenceEnd = Math.max(
        finalResponse.lastIndexOf('.'),
        finalResponse.lastIndexOf('!'),
        finalResponse.lastIndexOf('?')
      );
      if (lastSentenceEnd > MAX_LENGTH * 0.8) {
        finalResponse = finalResponse.substring(0, lastSentenceEnd + 1);
      }
    }
    
    return finalResponse || 'Детальный анализ недоступен.';
  } catch (error) {
    console.error('   ⚠️  Ошибка при генерации детального анализа:', error.message);
    return 'Детальный анализ недоступен из-за ошибки генерации.';
  }
}

// Генерировать раздел "Цепочка взлома" отдельно
async function generateAttackChainSection(allContent, targetUrl, deliverablesDir) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  
  if (!apiKey || apiKey === 'your_api_key_here') {
    return generateAttackChainSimple(allContent, targetUrl);
  }

  const prompt = `Ты эксперт по кибербезопасности. На основе анализа файлов результатов пентеста создай ДЕТАЛЬНУЮ ЦЕПОЧКУ ВЗЛОМА (attack chain) для сервиса ${targetUrl}.

ВАЖНО:
- Опиши пошаговую последовательность атакующих действий
- Покажи как одна уязвимость может привести к другой (эскалация)
- Опиши реальный сценарий эксплуатации найденных уязвимостей
- Используй правильное форматирование Markdown: заголовки, списки, нумерация
- Максимум 3000 слов, только на русском языке
- НЕ копируй фрагменты файлов - описывай своими словами

Файлы для анализа:
${allContent.substring(0, 100000)}

Создай детальную цепочку взлома с пошаговым описанием.`;

  try {
    const proxyUrl = process.env.HTTP_PROXY || process.env.HTTPS_PROXY || 'http://127.0.0.1:12334';
    if (proxyUrl) {
      process.env.HTTP_PROXY = proxyUrl;
      process.env.HTTPS_PROXY = proxyUrl;
    }

    const options = {
      apiKey: apiKey,
      model: 'claude-sonnet-4-5-20250929',
      maxTurns: 30,
      cwd: deliverablesDir,
      permissionMode: 'bypassPermissions',
    };

    let fullResponse = '';
    let result = null;
    
    for await (const message of query({ prompt, options })) {
      if (message.type === 'result') {
        if (message.result && typeof message.result === 'string') {
          fullResponse = message.result;
          result = fullResponse;
        }
      } else if (message.type === 'assistant') {
        const assistantMsg = message;
        if (assistantMsg.message && assistantMsg.message.content) {
          const content = Array.isArray(assistantMsg.message.content)
            ? assistantMsg.message.content.map((c) => c.text || JSON.stringify(c)).join('\n')
            : String(assistantMsg.message.content);
          if (content && typeof content === 'string' && content.trim().length > 0) {
            fullResponse += content + '\n\n';
          }
        }
      }
    }
    
    let finalResponse = result || fullResponse;
    
    // Удаляем рассуждения Claude перед началом цепочки взлома
    const chainStartPatterns = [
      /###\s*Цепочка\s+взлома/i,
      /##\s*Цепочка\s+взлома/i,
      /###\s*Шаг\s*1/i,
      /###\s*Этап\s*1/i,
      /\*\*Шаг\s*1/i,
      /\*\*Этап\s*1/i
    ];
    
    let chainStartIndex = -1;
    for (const pattern of chainStartPatterns) {
      const match = finalResponse.match(pattern);
      if (match && match.index !== undefined) {
        chainStartIndex = match.index;
        break;
      }
    }
    
    if (chainStartIndex > 0) {
      finalResponse = finalResponse.substring(chainStartIndex);
    }
    
    // Ограничиваем размер
    const MAX_LENGTH = 20000;
    if (finalResponse.length > MAX_LENGTH) {
      finalResponse = finalResponse.substring(0, MAX_LENGTH);
      const lastSentenceEnd = Math.max(
        finalResponse.lastIndexOf('.'),
        finalResponse.lastIndexOf('!'),
        finalResponse.lastIndexOf('?')
      );
      if (lastSentenceEnd > MAX_LENGTH * 0.8) {
        finalResponse = finalResponse.substring(0, lastSentenceEnd + 1);
      }
    }
    
    return finalResponse || 'Цепочка взлома недоступна.';
  } catch (error) {
    console.error('   ⚠️  Ошибка при генерации цепочки взлома:', error.message);
    return generateAttackChainSimple(allContent, targetUrl);
  }
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

  const prompt = `Ты эксперт по кибербезопасности и пентестингу. Проанализируй все предоставленные файлы с результатами пентеста и создай КРАТКИЙ ОТЧЕТ ПО РЕЗУЛЬТАТАМ ПЕНТЕСТА для сервиса ${targetUrl}.

🚨 КРИТИЧЕСКИ ВАЖНО - ОГРАНИЧЕНИЕ ОБЪЕМА:
1. ОТЧЕТ ДОЛЖЕН БЫТЬ КРАТКИМ НА 10-15 ЛИСТОВ (не более 3000-4000 слов)
2. НЕ копируй фрагменты файлов в итоговый отчет
3. Включай только САМЫЕ ВАЖНЫЕ уязвимости (критические и высокие)
4. Делай описания КРАТКИМИ (2-3 предложения максимум на пункт)
5. Не дублируй информацию между разделами
6. Убирай все лишние детали и технические подробности, оставляй только суть

КРИТИЧЕСКИ ВАЖНЫЕ ТРЕБОВАНИЯ:
1. ВСЕ РАЗДЕЛЫ ОТЧЕТА ДОЛЖНЫ БЫТЬ НАПИСАНЫ НА РУССКОМ ЯЗЫКЕ


СТРУКТУРА ОТЧЕТА (создай ТОЛЬКО эти 6 разделов, БЕЗ ПОВТОРОВ):

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
   Для КАЖДОЙ критической/высокой уязвимости предоставь КРАТКО (ВСЕ НА РУССКОМ ЯЗЫКЕ, МАКСИМУМ 2-3 ПРЕДЛОЖЕНИЯ НА ПУНКТ):
   - **Название уязвимости** (кратко, можно указать английское название в скобках)
   - **Критичность** (КРИТИЧЕСКАЯ/ВЫСОКАЯ или CRITICAL/HIGH - включай только их)
   - **Расположение** (коротко - URL или эндпоинт)
   - **Краткое описание** (1-2 предложения - что не так и почему это проблема) - ТОЛЬКО НА РУССКОМ
   - **Бизнес-влияние** (1 предложение - какой ущерб) - ТОЛЬКО НА РУССКОМ
   - **Рекомендации** (1-2 предложения - как исправить) - ТОЛЬКО НА РУССКОМ
   
   ВАЖНО: Включай только критические и высокие уязвимости. Средние и низкие пропускай для краткости отчета.

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


ФАЙЛЫ С РЕЗУЛЬТАТАМИ ПЕНТЕСТА:
${limitedContent}

💡 НАПОМИНАНИЕ О КРАТКОСТИ:
- Отчет должен быть на 10-15 листов (не более 3000-4000 слов)
- Включай только критические/высокие уязвимости
- Каждое описание - максимум 2-3 предложения
- НЕ копируй фрагменты файлов - анализируй и кратко пересказывай своими словами
- Фокусируйся на самом важном - что нужно исправить в первую очередь`;

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
    console.log(`   📏 Размер AI-ответа в символах: ${fullResponse.length}, в словах (примерно): ${fullResponse.split(/\s+/).length}`);
    
    let attackChain = result || fullResponse;
    
    if (!attackChain || attackChain.trim().length === 0) {
      console.log('   ⚠️  Цепочка взлома пуста, используется fallback');
      return generateAttackChainSimple(content, targetUrl);
    }
    
    // КРИТИЧЕСКИ ВАЖНО: Обрезаем ответ, если он слишком большой
    const MAX_RESPONSE_LENGTH = 15000; // Максимум 15000 символов (~2000 слов, ~10-15 страниц)
    if (attackChain.length > MAX_RESPONSE_LENGTH) {
      console.log(`   ⚠️  Ответ от AI слишком большой (${attackChain.length} символов), обрезаю до ${MAX_RESPONSE_LENGTH}...`);
      attackChain = attackChain.substring(0, MAX_RESPONSE_LENGTH);
      // Обрезаем до последнего предложения
      const lastSentenceEnd = Math.max(
        attackChain.lastIndexOf('.'),
        attackChain.lastIndexOf('!'),
        attackChain.lastIndexOf('?')
      );
      if (lastSentenceEnd > MAX_RESPONSE_LENGTH * 0.8) {
        attackChain = attackChain.substring(0, lastSentenceEnd + 1);
        console.log(`   ✅ Обрезано до ${attackChain.length} символов (до последнего предложения)`);
      }
    }
    
    console.log(`   ✅ Цепочка взлома сгенерирована (${attackChain.length} символов после обрезания)`);

    // Очищаем ответ от лишних разделов - применяем функцию очистки
    return cleanReportFromEnglishSections(attackChain);
  } catch (error) {
    console.error('   ❌ Ошибка при генерации через AI:', error.message);
    console.log('   ⚠️  Использую простую генерацию без AI');
    const fallbackResult = generateAttackChainSimple(content, targetUrl);
    // Применяем очистку и к fallback результату
    return cleanReportFromEnglishSections(fallbackResult);
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
  // Улучшаем обработку markdown: включаем переносы строк и GFM расширения
  marked.setOptions({ 
    gfm: true, 
    breaks: true,  // Переносы строк превращаются в <br>
    pedantic: false,
    sanitize: false,
    smartLists: true,
    smartypants: true
  });
  
  // Предобработка: убеждаемся что есть правильные переносы строк между абзацами
  let processedMarkdown = markdown
    .replace(/\n{3,}/g, '\n\n')  // Множественные переносы -> двойные
    .replace(/([.!?])\s+([А-ЯЁA-Z])/g, '$1\n\n$2');  // Перенос после точки перед заглавной буквой
  
  const htmlContent = marked.parse(processedMarkdown);

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
        p { margin: 12px 0; text-align: justify; }
        p:first-child { margin-top: 0; }
        p:last-child { margin-bottom: 0; }
        hr { border: none; border-top: 2px solid #e5e7eb; margin: 40px 0; }
        /* Улучшаем форматирование абзацев и списков */
        h2 + p, h3 + p, h4 + p { margin-top: 8px; }
        /* Правильные переносы строк для markdown */
        br { display: block; content: ''; margin-top: 8px; }
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

