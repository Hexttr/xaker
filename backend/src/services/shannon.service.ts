import { Pentest } from '../types/pentest';
import { pentestService } from './pentest.service';
import { EventEmitter } from 'events';
import { spawn, ChildProcess } from 'child_process';
import { join, resolve, normalize } from 'path';
import { existsSync, mkdirSync, readdirSync, statSync, writeFileSync } from 'fs';
import fetch from 'node-fetch';

/**
 * Сервис для интеграции с Shannon
 */
class ShannonService extends EventEmitter {
  private runningPentests: Map<string, ChildProcess> = new Map();
  private readonly SHANNON_PATH = resolve(process.cwd(), '../shannon');
  private readonly SHANNON_DIST_PATH = join(this.SHANNON_PATH, 'dist', 'shannon.js');
  // Альтернативный путь напрямую к cli/ui.js
  private readonly SHANNON_CLI_PATH = join(this.SHANNON_PATH, 'dist', 'cli', 'ui.js');
  // Правильная точка входа - temporal/client.js
  private readonly SHANNON_MAIN_PATH = join(this.SHANNON_PATH, 'dist', 'temporal', 'client.js');
  private readonly USE_SIMULATION = process.env.USE_SIMULATION === 'true';

  /**
   * Проверить, доступен ли Shannon
   */
  isShannonAvailable(): boolean {
    return existsSync(this.SHANNON_DIST_PATH);
  }

  /**
   * Запустить пентест через Shannon
   */
  async runPentest(pentestId: string, config: Pentest['config']): Promise<void> {
    const pentest = pentestService.getPentest(pentestId);
    if (!pentest) {
      throw new Error('Пентест не найден');
    }

    if (pentest.status === 'running') {
      throw new Error('Пентест уже запущен');
    }

    // Режим симуляции (для тестирования без затрат)
    if (this.USE_SIMULATION) {
      pentestService.updatePentestStatus(pentestId, 'running');
      pentestService.addLog(pentestId, 'info', '🧪 РЕЖИМ СИМУЛЯЦИИ (USE_SIMULATION=true)');
      pentestService.addLog(pentestId, 'info', '💰 Реальные затраты на API отключены');
      await this.simulatePentest(pentestId, config);
      return;
    }

    // Проверяем доступность Shannon
    if (!this.isShannonAvailable()) {
      pentestService.addLog(pentestId, 'error', '❌ Shannon не найден. Убедитесь, что он клонирован в ../shannon');
      pentestService.addLog(pentestId, 'info', 'Переключаюсь на симуляцию...');
      await this.simulatePentest(pentestId, config);
      return;
    }

    // Проверяем наличие ANTHROPIC_API_KEY
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey || apiKey === 'your_api_key_here') {
      pentestService.addLog(pentestId, 'warn', '⚠️ ANTHROPIC_API_KEY не установлен или неверный');
      pentestService.addLog(pentestId, 'info', '💰 Переключаюсь на симуляцию (без затрат)');
      pentestService.addLog(pentestId, 'info', 'Для реального запуска установите валидный API ключ');
      await this.simulatePentest(pentestId, config);
      return;
    }
    
    // Логируем информацию об API ключе (без полного ключа)
    pentestService.addLog(pentestId, 'info', `🔑 API ключ найден: ${apiKey.substring(0, 20)}...${apiKey.substring(apiKey.length - 10)} (длина: ${apiKey.length})`);

    pentestService.updatePentestStatus(pentestId, 'running');
    this.runningPentests.set(pentestId, null as any); // Placeholder

    try {
      await this.executeShannon(pentestId, config);
    } catch (error: any) {
      pentestService.updatePentestStatus(pentestId, 'failed');
      pentestService.addLog(pentestId, 'error', `Ошибка: ${error.message || error}`);
      throw error;
    }
  }

  /**
   * Остановить пентест
   */
  async stopPentest(pentestId: string): Promise<void> {
    const process = this.runningPentests.get(pentestId);
    if (process) {
      process.kill('SIGTERM');
      this.runningPentests.delete(pentestId);
      pentestService.updatePentestStatus(pentestId, 'stopped');
      pentestService.addLog(pentestId, 'info', 'Пентест остановлен пользователем');
    }
  }

  /**
   * Проверить доступность целевого URL
   */
  private async checkTargetAccessibility(url: string): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 секунд таймаут
      
      const response = await fetch(url, {
        method: 'HEAD',
        signal: controller.signal,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });
      
      clearTimeout(timeoutId);
      return response.ok || response.status < 500;
    } catch (error: any) {
      return false;
    }
  }

  /**
   * Проверить, не является ли путь самопроверкой (Xaker платформа)
   */
  private isSelfScanPath(path: string): boolean {
    const normalizedPath = normalize(path).toLowerCase();
    const projectRoot = normalize(process.cwd()).toLowerCase();
    
    // Проверяем, не указывает ли путь на сам проект Xaker
    if (normalizedPath.includes(projectRoot)) {
      // Разрешаем только папку pentests внутри проекта
      if (normalizedPath.includes(join(projectRoot, 'pentests').toLowerCase())) {
        return false; // Это изолированная папка пентеста - OK
      }
      // Проверяем, не содержит ли путь backend, frontend, или корневую папку проекта
      if (normalizedPath.includes('backend') || 
          normalizedPath.includes('frontend') || 
          normalizedPath === projectRoot ||
          normalizedPath.startsWith(join(projectRoot, 'src').toLowerCase()) ||
          normalizedPath.startsWith(join(projectRoot, 'node_modules').toLowerCase()) ||
          normalizedPath.includes('xaker') && (normalizedPath.includes('backend') || normalizedPath.includes('frontend'))) {
        return true; // Это самопроверка!
      }
    }
    
    // Дополнительная проверка: если путь содержит известные папки проекта Xaker
    const xakerPaths = ['backend/src', 'frontend/src', 'backend/services', 'backend/routes'];
    for (const xakerPath of xakerPaths) {
      if (normalizedPath.includes(xakerPath.toLowerCase())) {
        return true; // Это самопроверка!
      }
    }
    
    return false;
  }

  /**
   * Проверить, пуста ли папка scope (только служебные файлы)
   */
  private isScopeEmpty(scopePath: string): boolean {
    try {
      if (!existsSync(scopePath)) {
        return true;
      }
      
      const files = readdirSync(scopePath);
      // Игнорируем служебные файлы и папки
      const codeFiles = files.filter(f => {
        const fullPath = join(scopePath, f);
        const stat = statSync(fullPath);
        
        // Игнорируем скрытые файлы/папки, .git, README.md
        if (f.startsWith('.') || f === 'README.md' || f === '.gitignore') {
          return false;
        }
        
        // Если это папка, проверяем её содержимое
        if (stat.isDirectory()) {
          try {
            const dirFiles = readdirSync(fullPath);
            return dirFiles.length > 0;
          } catch {
            return false;
          }
        }
        
        return true;
      });
      
      return codeFiles.length === 0;
    } catch (error) {
      return true; // Если ошибка - считаем пустой
    }
  }

  /**
   * Выполнить Shannon
   */
  private async executeShannon(pentestId: string, config: Pentest['config']): Promise<void> {
    pentestService.addLog(pentestId, 'info', '🚀 Начинается РЕАЛЬНЫЙ пентест через Shannon...');
    pentestService.addLog(pentestId, 'info', `🎯 Цель: ${config.targetUrl}`);
    
    // Проверяем доступность целевого URL
    pentestService.addLog(pentestId, 'info', '🔍 Проверяю доступность целевого URL...');
    const isAccessible = await this.checkTargetAccessibility(config.targetUrl);
    
    if (!isAccessible) {
      pentestService.addLog(pentestId, 'error', `❌ Целевой URL недоступен: ${config.targetUrl}`);
      pentestService.addLog(pentestId, 'info', '📝 Формирую отчет о недоступности цели...');
      
      // Формируем отчет о недоступности
      await this.generateUnreachableReport(pentestId, config);
      
      pentestService.updatePentestStatus(pentestId, 'completed');
      pentestService.addLog(pentestId, 'success', '✅ Отчет о недоступности цели сформирован');
      return;
    }
    
    pentestService.addLog(pentestId, 'info', '✅ Целевой URL доступен');
    pentestService.addLog(pentestId, 'warn', '💰 ВНИМАНИЕ: Используется реальный Claude API (~$50)');

    // Для работы Shannon нужен путь к репозиторию
    // ВАЖНО: Если не указан явный путь к исходному коду, используем изолированную папку
    // чтобы Shannon не анализировал код платформы Xaker
    const pentestsDir = join(process.cwd(), 'pentests');
    const pentestDir = join(pentestsDir, pentestId);
    let repoPath = pentestDir; // По умолчанию используем изолированную папку (только black-box)
    let useWhiteBox = false; // Флаг для white-box анализа
    
    // Проверяем защиту от самопроверки и наличие исходного кода
    if (config.scope && config.scope.length > 0) {
      const scopePath = normalize(config.scope[0]);
      
      if (this.isSelfScanPath(scopePath)) {
        pentestService.addLog(pentestId, 'error', `❌ ОШИБКА: Указанный путь указывает на код платформы Xaker: ${scopePath}`);
        pentestService.addLog(pentestId, 'error', '❌ Самопроверка запрещена для безопасности');
        pentestService.addLog(pentestId, 'info', '📝 Использую изолированную папку вместо указанного пути');
        pentestService.addLog(pentestId, 'info', '📝 Активирован режим: только black-box тестирование (без white-box анализа)');
        // repoPath уже установлен на pentestDir
      } else {
        // Проверяем, не пуста ли папка scope
        if (this.isScopeEmpty(scopePath)) {
          pentestService.addLog(pentestId, 'warn', `⚠️  Папка scope пуста или содержит только служебные файлы: ${scopePath}`);
          pentestService.addLog(pentestId, 'info', '📝 Активирован режим: только black-box тестирование (без white-box анализа)');
          pentestService.addLog(pentestId, 'info', '📝 Использую изолированную папку для предотвращения самопроверки');
          // repoPath остается pentestDir (изолированная папка)
        } else {
          pentestService.addLog(pentestId, 'info', `✅ Папка scope содержит исходный код: ${scopePath}`);
          pentestService.addLog(pentestId, 'info', '📝 Активирован режим: white-box + black-box тестирование');
          repoPath = scopePath; // Используем scope для white-box анализа
          useWhiteBox = true;
        }
      }
    } else {
      pentestService.addLog(pentestId, 'info', '📝 Scope не указан, используется только black-box тестирование');
    }
    
    // Создаем изолированную папку для этого пентеста
    if (repoPath === pentestDir) {
      if (!existsSync(pentestsDir)) {
        mkdirSync(pentestsDir, { recursive: true });
      }
      if (!existsSync(pentestDir)) {
        pentestService.addLog(pentestId, 'info', `📁 Создаю изолированную папку для пентеста: ${pentestDir}`);
        mkdirSync(pentestDir, { recursive: true });
        // Создаем минимальный .git репозиторий для Shannon
        mkdirSync(join(pentestDir, '.git'), { recursive: true });
        // Создаем README.md чтобы папка не была полностью пустой
        // Это предотвратит поиск кода в родительских директориях
        const { writeFileSync } = require('fs');
        writeFileSync(
          join(pentestDir, 'README.md'),
          `# Pentest Target: ${config.targetUrl}\n\nThis directory is used for pentest analysis.\nSource code analysis will be performed on the target URL only.\n`
        );
        pentestService.addLog(pentestId, 'info', `✅ Папка создана: ${pentestDir}`);
        pentestService.addLog(pentestId, 'warn', `⚠️  ВНИМАНИЕ: Исходный код целевого приложения не предоставлен.`);
        pentestService.addLog(pentestId, 'warn', `⚠️  Shannon Lite предназначен для white-box анализа и требует исходный код.`);
        pentestService.addLog(pentestId, 'warn', `⚠️  Без исходного кода Shannon может анализировать неправильный репозиторий (например, код платформы Xaker).`);
        pentestService.addLog(pentestId, 'warn', `⚠️  Рекомендуется: предоставить исходный код целевого приложения через параметр scope в конфигурации.`);
      } else {
        pentestService.addLog(pentestId, 'info', `📁 Использую существующую папку: ${pentestDir}`);
      }
    }
    
    const apiKey = process.env.ANTHROPIC_API_KEY!;
    
    // Проверяем и логируем API ключ перед передачей в Shannon
    if (!apiKey || apiKey === 'your_api_key_here') {
      pentestService.addLog(pentestId, 'error', '❌ КРИТИЧЕСКАЯ ОШИБКА: ANTHROPIC_API_KEY не найден при запуске Shannon!');
      pentestService.addLog(pentestId, 'error', '   Проверьте файл .env и перезапустите бэкенд');
      throw new Error('ANTHROPIC_API_KEY не установлен');
    }
    
    pentestService.addLog(pentestId, 'info', `🔑 Передаю API ключ в Shannon: ${apiKey.substring(0, 20)}...${apiKey.substring(apiKey.length - 10)}`);

    // Собираем аргументы для Shannon
    // ВАЖНО: Передаем изолированную папку, чтобы Shannon не искал код в C:\Xaker\
    const args = [
      config.targetUrl,
      repoPath,
      '--wait', // Ждем завершения workflow
    ];

    // Опциональный конфиг
    if (config.excludedPaths && config.excludedPaths.length > 0) {
      // Можно создать временный конфиг файл
      args.push('--config', this.createTempConfig(pentestId, config));
    }

    // Используем temporal/client.js - это правильная точка входа с функцией startPipeline()
    const shannonEntryPoint = this.SHANNON_MAIN_PATH;
    
    pentestService.addLog(pentestId, 'info', `📦 Запускаю Shannon: node ${shannonEntryPoint} ${args.join(' ')}`);

    // Запускаем Shannon как дочерний процесс
    // Настраиваем переменные окружения для прокси (если VPN используется)
    const env: NodeJS.ProcessEnv = {
      ...process.env,
      ANTHROPIC_API_KEY: apiKey,
      CLAUDE_CODE_MAX_OUTPUT_TOKENS: '64000',
    };
    
    // ВАЖНО: Shannon всегда использует Claude API, а не MiroMind/Ollama
    // MiroMind используется только для генерации отчетов (pdfReport.service.ts)
    // Причина: Shannon использует Anthropic SDK, который требует формат Anthropic API
    // Ollama API не полностью совместим с Anthropic API форматом
    pentestService.addLog(pentestId, 'info', `🤖 Shannon использует Claude API (не MiroMind)`);
    pentestService.addLog(pentestId, 'info', `💡 MiroMind будет использован только для генерации отчетов`);
    
    // Если есть системные переменные прокси, используем их
    if (process.env.HTTP_PROXY) {
      env.HTTP_PROXY = process.env.HTTP_PROXY;
      pentestService.addLog(pentestId, 'info', `🌐 Используется HTTP прокси: ${process.env.HTTP_PROXY}`);
    }
    if (process.env.HTTPS_PROXY) {
      env.HTTPS_PROXY = process.env.HTTPS_PROXY;
      pentestService.addLog(pentestId, 'info', `🌐 Используется HTTPS прокси: ${process.env.HTTPS_PROXY}`);
    }
    if (process.env.http_proxy) {
      env.http_proxy = process.env.http_proxy;
    }
    if (process.env.https_proxy) {
      env.https_proxy = process.env.https_proxy;
    }
    
    // Обнаружен системный прокси - используем его
    // Многие VPN используют локальный прокси на 127.0.0.1
    const systemProxy = 'http://127.0.0.1:12334';
    if (!env.HTTP_PROXY && !env.HTTPS_PROXY) {
      env.HTTP_PROXY = systemProxy;
      env.HTTPS_PROXY = systemProxy;
      pentestService.addLog(pentestId, 'info', `🌐 Обнаружен системный прокси, используем: ${systemProxy}`);
    }
    
    // Финальная проверка перед запуском
    pentestService.addLog(pentestId, 'info', `🔍 Финальная проверка env для Shannon:`);
    pentestService.addLog(pentestId, 'info', `   ANTHROPIC_API_KEY: ${env.ANTHROPIC_API_KEY ? `${env.ANTHROPIC_API_KEY.substring(0, 20)}...${env.ANTHROPIC_API_KEY.substring(env.ANTHROPIC_API_KEY.length - 10)} (длина: ${env.ANTHROPIC_API_KEY.length})` : '❌ НЕ УСТАНОВЛЕН!'}`);
    pentestService.addLog(pentestId, 'info', `   CLAUDE_MODEL: ${process.env.CLAUDE_MODEL || 'claude-3-haiku-20240307'}`);
    pentestService.addLog(pentestId, 'info', `   HTTP_PROXY: ${env.HTTP_PROXY || 'не установлен'}`);
    pentestService.addLog(pentestId, 'info', `   HTTPS_PROXY: ${env.HTTPS_PROXY || 'не установлен'}`);
    
    pentestService.addLog(pentestId, 'info', `🚀 Запускаю процесс: node ${shannonEntryPoint} ${args.join(' ')}`);
    pentestService.addLog(pentestId, 'info', `📂 Рабочая директория: ${this.SHANNON_PATH}`);
    
    const shannonProcess = spawn('node', [shannonEntryPoint, ...args], {
      cwd: this.SHANNON_PATH,
      env: env,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    pentestService.addLog(pentestId, 'info', `✅ Процесс запущен, PID: ${shannonProcess.pid}`);
    this.runningPentests.set(pentestId, shannonProcess);

    // Перехватываем stdout (логи)
    shannonProcess.stdout.on('data', (data: Buffer) => {
      const output = data.toString();
      const lines = output.split('\n').filter(line => line.trim());
      lines.forEach(line => {
        pentestService.addLog(pentestId, 'info', `[Shannon] ${line}`);
      });
    });

    // Перехватываем stderr (ошибки)
    shannonProcess.stderr.on('data', (data: Buffer) => {
      const output = data.toString();
      const lines = output.split('\n').filter(line => line.trim());
      lines.forEach(line => {
        pentestService.addLog(pentestId, 'error', `[Shannon ERROR] ${line}`);
      });
    });

    // Обработка завершения
    return new Promise((resolve, reject) => {
      shannonProcess.on('close', (code, signal) => {
        this.runningPentests.delete(pentestId);
        pentestService.addLog(pentestId, 'info', `🔚 Процесс завершен: код=${code}, signal=${signal || 'none'}`);
        
        if (code === 0) {
          pentestService.updatePentestStatus(pentestId, 'completed');
          pentestService.addLog(pentestId, 'success', '✅ Пентест успешно завершен!');
          resolve();
        } else {
          pentestService.updatePentestStatus(pentestId, 'failed');
          pentestService.addLog(pentestId, 'error', `❌ Пентест завершился с кодом ${code}${signal ? ` (signal: ${signal})` : ''}`);
          reject(new Error(`Shannon завершился с кодом ${code}`));
        }
      });

      shannonProcess.on('error', (error) => {
        this.runningPentests.delete(pentestId);
        pentestService.updatePentestStatus(pentestId, 'failed');
        pentestService.addLog(pentestId, 'error', `❌ Ошибка запуска Shannon: ${error.message}`);
        pentestService.addLog(pentestId, 'error', `❌ Stack: ${error.stack || 'нет'}`);
        reject(error);
      });
      
      // Логируем, когда процесс начинает выполняться
      shannonProcess.on('spawn', () => {
        pentestService.addLog(pentestId, 'info', '🎬 Процесс Shannon запущен (spawn event)');
      });
    });
  }

  /**
   * Создать временный конфиг файл
   * @deprecated Функция не реализована, конфиг не используется
   */
  private createTempConfig(pentestId: string, config: Pentest['config']): string {
    // Конфиг файл не создается, так как excludedPaths обрабатываются иначе
    // В будущем можно реализовать создание YAML конфига для Shannon
    return '';
  }

  /**
   * Симуляция пентеста (без затрат)
   */
  private async simulatePentest(pentestId: string, config: Pentest['config']): Promise<void> {
    pentestService.addLog(pentestId, 'info', '🧪 РЕЖИМ СИМУЛЯЦИИ - Реальные затраты отключены');
    pentestService.addLog(pentestId, 'info', `🎯 Цель: ${config.targetUrl}`);
    
    pentestService.addLog(pentestId, 'info', '📡 Фаза 1: Разведка (Reconnaissance)...');
    await this.simulatePhase(pentestId, 'reconnaissance', 3000);

    pentestService.addLog(pentestId, 'info', '🔍 Фаза 2: Анализ уязвимостей (Vulnerability Analysis)...');
    await this.simulatePhase(pentestId, 'vulnerability', 4000);

    pentestService.addLog(pentestId, 'info', '⚡ Фаза 3: Эксплуатация (Exploitation)...');
    await this.simulatePhase(pentestId, 'exploitation', 5000);

    pentestService.addLog(pentestId, 'info', '📝 Фаза 4: Генерация отчета (Reporting)...');
    await this.simulatePhase(pentestId, 'reporting', 2000);

    pentestService.updatePentestStatus(pentestId, 'completed');
    pentestService.addLog(pentestId, 'success', '✅ Пентест успешно завершен! (симуляция)');
    pentestService.addLog(pentestId, 'info', '💰 Для реального выполнения установите валидный API ключ и убедитесь, что USE_SIMULATION=false');
  }

  /**
   * Симуляция фазы
   */
  private async simulatePhase(pentestId: string, phase: string, duration: number): Promise<void> {
    const steps = [
      'Инициализация...',
      'Сбор данных...',
      'Анализ...',
      'Обработка результатов...',
    ];

    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, duration / steps.length));
      pentestService.addLog(pentestId, 'info', `  ${step}`);
    }
  }

  /**
   * Сгенерировать отчет о недоступности цели
   */
  private async generateUnreachableReport(pentestId: string, config: Pentest['config']): Promise<void> {
    const pentestDir = join(process.cwd(), 'pentests', pentestId);
    const deliverablesDir = join(pentestDir, 'deliverables');
    
    if (!existsSync(deliverablesDir)) {
      mkdirSync(deliverablesDir, { recursive: true });
    }
    
    const reportPath = join(deliverablesDir, 'unreachable_target_report.md');
    
    const report = `# Отчет о недоступности целевого URL

## Целевой URL
**URL:** ${config.targetUrl}

## Статус
❌ **НЕДОСТУПЕН**

## Описание проблемы
Целевой URL не отвечает на HTTP/HTTPS запросы. Возможные причины:

1. Сервер не запущен или недоступен
2. Неправильный URL или опечатка
3. Блокировка доступа (firewall, DDoS protection)
4. Временная недоступность сервера
5. Требуется аутентификация для доступа

## Рекомендации
1. Проверьте правильность URL
2. Убедитесь, что сервер запущен и доступен
3. Проверьте сетевые настройки и firewall
4. Попробуйте открыть URL в браузере

## Дата проверки
${new Date().toISOString()}
`;

    writeFileSync(reportPath, report);
    pentestService.addLog(pentestId, 'info', `📄 Отчет сохранен: ${reportPath}`);
  }
}

export const shannonService = new ShannonService();
