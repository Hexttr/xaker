const pdfParse = require('pdf-parse');
const fs = require('fs');
const path = require('path');

async function analyzePDF() {
  const pdfPath = 'C:/Users/User/Downloads/pentest-report-cddf1019-3fac-4164-aa5d-f7efbaa636bc.pdf';
  
  try {
    console.log('📄 Читаю PDF файл...');
    const dataBuffer = fs.readFileSync(pdfPath);
    const data = await pdfParse(dataBuffer);
    
    console.log(`\n📊 Информация о PDF:`);
    console.log(`   Страниц: ${data.numpages}`);
    console.log(`   Размер текста: ${data.text.length} символов`);
    console.log(`   Примерно слов: ${data.text.split(/\s+/).length}`);
    
    // Разбиваем на разделы
    const sections = data.text.split(/\n\s*\n/).filter(s => s.trim().length > 0);
    console.log(`\n📋 Найдено разделов: ${sections.length}`);
    
    // Ищем возможные лишние разделы
    console.log(`\n🔍 Анализ содержимого:\n`);
    
    const lines = data.text.split('\n');
    let currentSection = '';
    const sectionsMap = new Map();
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Определяем заголовки разделов
      if (line.match(/^#+\s+|^##\s+|^###\s+|^[А-ЯЁ][А-ЯЁ\s]+$/)) {
        if (line.length < 100 && line.length > 3) {
          currentSection = line;
          if (!sectionsMap.has(currentSection)) {
            sectionsMap.set(currentSection, []);
          }
        }
      }
      
      if (currentSection && line) {
        sectionsMap.get(currentSection).push(line);
      }
    }
    
    console.log(`\n📑 Структура документа:`);
    let sectionNum = 1;
    for (const [section, content] of sectionsMap.entries()) {
      const contentText = content.join(' ');
      console.log(`\n${sectionNum}. ${section.substring(0, 80)}`);
      console.log(`   Размер: ${contentText.length} символов`);
      console.log(`   Строк: ${content.length}`);
      
      // Проверяем на возможные проблемы
      if (contentText.includes('Executive Summary') && contentText.includes('Краткое резюме')) {
        console.log(`   ⚠️  Возможное дублирование: есть и английский, и русский вариант`);
      }
      if (contentText.length < 50) {
        console.log(`   ⚠️  Очень короткий раздел - возможно лишний`);
      }
      if (contentText.match(/TODO|FIXME|TEMP|ВРЕМЕННО/i)) {
        console.log(`   ⚠️  Содержит временные пометки`);
      }
      
      sectionNum++;
    }
    
    // Ищем повторяющиеся блоки
    console.log(`\n🔎 Поиск повторяющихся блоков...`);
    const textLower = data.text.toLowerCase();
    const commonPhrases = [
      'файлы shannon',
      'используй только для анализа',
      'не копируй',
      'executive summary',
      'краткое резюме',
      'цепочка атаки',
      'proof of concept'
    ];
    
    for (const phrase of commonPhrases) {
      const matches = (textLower.match(new RegExp(phrase, 'gi')) || []).length;
      if (matches > 3) {
        console.log(`   ⚠️  Фраза "${phrase}" встречается ${matches} раз - возможно дублирование`);
      }
    }
    
    // Сохраняем полный текст для анализа
    const outputPath = path.join(__dirname, 'pdf-analysis-output.txt');
    fs.writeFileSync(outputPath, data.text, 'utf-8');
    console.log(`\n✅ Полный текст сохранен в: ${outputPath}`);
    
    // Показываем первые 2000 символов для быстрого просмотра
    console.log(`\n📝 Первые 2000 символов документа:\n`);
    console.log(data.text.substring(0, 2000));
    console.log(`\n... (остальное в файле)`);
    
  } catch (error) {
    console.error('❌ Ошибка при анализе PDF:', error);
  }
}

analyzePDF();

