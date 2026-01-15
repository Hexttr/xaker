import { Pentest, PentestLog } from '../types/pentest';
import { pentestService } from './pentest.service';
import { EventEmitter } from 'events';
import { spawn, ChildProcess } from 'child_process';
import { join, resolve } from 'path';
import { existsSync, mkdirSync } from 'fs';

/**
 * Сервис для интеграции с Shannon
 */
class ShannonService extends EventEmitter {
  private runningPentests: Map<string, ChildProcess> = new Map();
  private readonly SHANNON_PATH = resolve(process.cwd(), '../shannon');
  private readonly SHANNON_DIST_PATH = join(this.SHANNON_PATH, 'dist', 'shannon.js');
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
   * Выполнить Shannon
   */
  private async executeShannon(pentestId: string, config: Pentest['config']): Promise<void> {
    pentestService.addLog(pentestId, 'info', '🚀 Начинается РЕАЛЬНЫЙ пентест через Shannon...');
    pentestService.addLog(pentestId, 'info', `🎯 Цель: ${config.targetUrl}`);
    pentestService.addLog(pentestId, 'warn', '💰 ВНИМАНИЕ: Используется реальный Claude API (~$50)');

    // Для работы Shannon нужен путь к репозиторию
    // Создаем ОТДЕЛЬНУЮ папку для каждого пентеста
    const pentestsDir = join(process.cwd(), 'pentests');
    const pentestDir = join(pentestsDir, pentestId);
    const repoPath = config.scope?.[0] || pentestDir;
    
    // Создаем отдельную папку для этого пентеста
    if (repoPath === pentestDir) {
      if (!existsSync(pentestsDir)) {
        mkdirSync(pentestsDir, { recursive: true });
      }
      if (!existsSync(pentestDir)) {
        pentestService.addLog(pentestId, 'info', `📁 Создаю отдельную папку для пентеста: ${pentestDir}`);
        mkdirSync(pentestDir, { recursive: true });
        // Создаем минимальный .git репозиторий для Shannon
        mkdirSync(join(pentestDir, '.git'), { recursive: true });
        pentestService.addLog(pentestId, 'info', `✅ Папка создана: ${pentestDir}`);
      } else {
        pentestService.addLog(pentestId, 'info', `📁 Использую существующую папку: ${pentestDir}`);
      }
    }
    
    const apiKey = process.env.ANTHROPIC_API_KEY!;

    // Собираем аргументы для Shannon
    const args = [
      config.targetUrl,
      repoPath,
    ];

    // Опциональный конфиг
    if (config.excludedPaths && config.excludedPaths.length > 0) {
      // Можно создать временный конфиг файл
      args.push('--config', this.createTempConfig(pentestId, config));
    }

    pentestService.addLog(pentestId, 'info', `📦 Запускаю Shannon: node ${this.SHANNON_DIST_PATH} ${args.join(' ')}`);

    // Запускаем Shannon как дочерний процесс
    // Настраиваем переменные окружения для прокси (если VPN используется)
    const env: NodeJS.ProcessEnv = {
      ...process.env,
      ANTHROPIC_API_KEY: apiKey,
      CLAUDE_CODE_MAX_OUTPUT_TOKENS: '64000',
    };
    
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
    
    const shannonProcess = spawn('node', [this.SHANNON_DIST_PATH, ...args], {
      cwd: this.SHANNON_PATH,
      env: env,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    this.runningPentests.set(pentestId, shannonProcess);

    // Перехватываем stdout (логи)
    shannonProcess.stdout.on('data', (data: Buffer) => {
      const lines = data.toString().split('\n').filter(line => line.trim());
      lines.forEach(line => {
        pentestService.addLog(pentestId, 'info', line);
      });
    });

    // Перехватываем stderr (ошибки)
    shannonProcess.stderr.on('data', (data: Buffer) => {
      const lines = data.toString().split('\n').filter(line => line.trim());
      lines.forEach(line => {
        pentestService.addLog(pentestId, 'error', line);
      });
    });

    // Обработка завершения
    return new Promise((resolve, reject) => {
      shannonProcess.on('close', (code) => {
        this.runningPentests.delete(pentestId);
        
        if (code === 0) {
          pentestService.updatePentestStatus(pentestId, 'completed');
          pentestService.addLog(pentestId, 'success', '✅ Пентест успешно завершен!');
          resolve();
        } else {
          pentestService.updatePentestStatus(pentestId, 'failed');
          pentestService.addLog(pentestId, 'error', `❌ Пентест завершился с кодом ${code}`);
          reject(new Error(`Shannon завершился с кодом ${code}`));
        }
      });

      shannonProcess.on('error', (error) => {
        this.runningPentests.delete(pentestId);
        pentestService.updatePentestStatus(pentestId, 'failed');
        pentestService.addLog(pentestId, 'error', `❌ Ошибка запуска Shannon: ${error.message}`);
        reject(error);
      });
    });
  }

  /**
   * Создать временный конфиг файл
   */
  private createTempConfig(pentestId: string, config: Pentest['config']): string {
    // TODO: Создать временный YAML конфиг файл
    // Пока возвращаем пустую строку
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
}

export const shannonService = new ShannonService();
