import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

/**
 * Утилита для логирования процесса генерации отчетов в файл
 */
class ReportLogger {
  private logs: string[] = [];
  private readonly LOGS_DIR = join(process.cwd(), 'backend', 'report-logs');

  constructor() {
    if (!existsSync(this.LOGS_DIR)) {
      mkdirSync(this.LOGS_DIR, { recursive: true });
    }
  }

  log(message: string): void {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}`;
    this.logs.push(logMessage);
    console.log(message); // Также выводим в консоль
  }

  error(message: string, error?: any): void {
    const timestamp = new Date().toISOString();
    let errorMessage = `[${timestamp}] ❌ ${message}`;
    if (error) {
      errorMessage += `\n   Тип: ${error?.constructor?.name || 'Unknown'}`;
      errorMessage += `\n   Сообщение: ${error?.message || String(error)}`;
      if (error?.stack) {
        errorMessage += `\n   Stack: ${error.stack}`;
      }
    }
    this.logs.push(errorMessage);
    console.error(message, error); // Также выводим в консоль
  }

  warn(message: string): void {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ⚠️  ${message}`;
    this.logs.push(logMessage);
    console.warn(message); // Также выводим в консоль
  }

  saveToFile(pentestId: string): string {
    const filename = `report-generation-${pentestId}-${Date.now()}.log`;
    const filepath = join(this.LOGS_DIR, filename);
    const content = this.logs.join('\n');
    writeFileSync(filepath, content, 'utf-8');
    return filepath;
  }

  clear(): void {
    this.logs = [];
  }
}

export const reportLogger = new ReportLogger();

