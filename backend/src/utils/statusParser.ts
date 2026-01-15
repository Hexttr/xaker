// Утилита для парсинга статуса из логов Shannon

/**
 * Парсит текущий статус пентеста из логов
 * Возвращает человекочитаемый статус на русском языке
 */
export function parseStatusFromLogs(logs: Array<{ message: string }>): string {
  if (logs.length === 0) {
    return 'Инициализация...';
  }

  // Берем последние 20 логов для анализа
  const recentLogs = logs.slice(-20);
  const lastLog = logs[logs.length - 1]?.message || '';

  // Поиск фаз (PHASE)
  if (lastLog.includes('PHASE 1:') || lastLog.includes('PRE-RECONNAISSANCE')) {
    return '📡 Фаза 1: Предварительная разведка';
  }
  if (lastLog.includes('PHASE 2:') || lastLog.includes('RECONNAISSANCE')) {
    return '🔍 Фаза 2: Разведка';
  }
  if (lastLog.includes('PHASE 3:') || lastLog.includes('ANALYSIS')) {
    return '📊 Фаза 3: Анализ уязвимостей';
  }
  if (lastLog.includes('PHASE 4:') || lastLog.includes('EXPLOITATION')) {
    return '⚡ Фаза 4: Эксплуатация уязвимостей';
  }
  if (lastLog.includes('PHASE 5:') || lastLog.includes('REPORTING')) {
    return '📝 Фаза 5: Генерация отчета';
  }

  // Поиск агентов
  if (lastLog.includes('Pre-recon') || lastLog.includes('pre-recon')) {
    return '🔍 Предварительная разведка';
  }
  if (lastLog.includes('Code analysis') || lastLog.includes('code-analysis')) {
    return '📄 Анализ кода';
  }
  if (lastLog.includes('Auth analysis') || lastLog.includes('auth-analysis')) {
    return '🔐 Анализ аутентификации';
  }
  if (lastLog.includes('XSS analysis') || lastLog.includes('xss')) {
    return '🛡️ Поиск XSS уязвимостей';
  }
  if (lastLog.includes('Injection analysis') || lastLog.includes('injection')) {
    return '💉 Поиск SQL инъекций';
  }
  if (lastLog.includes('SSRF analysis') || lastLog.includes('ssrf')) {
    return '🌐 Поиск SSRF уязвимостей';
  }
  if (lastLog.includes('Auth exploitation') || lastLog.includes('auth-exploit')) {
    return '🧪 Тестирование аутентификации';
  }
  if (lastLog.includes('XSS exploitation') || lastLog.includes('xss-exploit')) {
    return '🧪 Тестирование XSS';
  }
  if (lastLog.includes('Injection exploitation') || lastLog.includes('injection-exploit')) {
    return '🧪 Тестирование SQL инъекций';
  }

  // Поиск операций
  if (lastLog.includes('Running') || lastLog.includes('running')) {
    if (lastLog.includes('scan') || lastLog.includes('сканирование')) {
      return '🔍 Сканирование системы...';
    }
    if (lastLog.includes('analysis') || lastLog.includes('анализ')) {
      return '📊 Анализ данных...';
    }
    if (lastLog.includes('test') || lastLog.includes('тест')) {
      return '🧪 Тестирование...';
    }
    return '⚙️ Выполнение операции...';
  }

  // Инициализация
  if (lastLog.includes('Initializing') || lastLog.includes('Инициализация')) {
    return '🔧 Инициализация системы...';
  }

  // Завершение
  if (lastLog.includes('COMPLETED') || lastLog.includes('завершен') || lastLog.includes('успешно')) {
    return '✅ Пентест завершен';
  }

  // Ошибки
  if (lastLog.includes('ERROR') || lastLog.includes('Ошибка') || lastLog.includes('failed')) {
    return '❌ Ошибка выполнения';
  }

  // По умолчанию
  return '⚙️ Выполнение пентеста...';
}


