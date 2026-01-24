import { Router, Request, Response } from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const router = Router();

// Простой endpoint для деплоя через HTTP
// Использование: POST /api/deploy с заголовком X-Deploy-Token
router.post('/', async (req: Request, res: Response) => {
  try {
    // Проверка токена
    const deployToken = req.headers['x-deploy-token'] as string;
    const expectedToken = process.env.DEPLOY_TOKEN || 'change-me-in-production';
    
    if (deployToken !== expectedToken) {
      return res.status(401).json({ 
        error: 'Unauthorized',
        message: 'Invalid deploy token' 
      });
    }
    
    console.log('🚀 Deploy request received');
    
    // Выполняем деплой команды
    const commands = [
      'cd /root/xaker && git pull origin prod',
      'cd /root/xaker/backend && npm run build',
      'pm2 restart xaker-backend || (cd /root/xaker/backend && pm2 start npm --name xaker-backend -- run start)'
    ];
    
    const results: any[] = [];
    
    for (const cmd of commands) {
      try {
        console.log(`Executing: ${cmd}`);
        const { stdout, stderr } = await execAsync(cmd, { 
          timeout: 300000, // 5 minutes
          maxBuffer: 10 * 1024 * 1024 // 10MB
        });
        results.push({
          command: cmd,
          success: true,
          stdout: stdout.substring(0, 5000), // Limit output
          stderr: stderr.substring(0, 5000)
        });
      } catch (error: any) {
        results.push({
          command: cmd,
          success: false,
          error: error.message,
          stdout: error.stdout?.substring(0, 5000),
          stderr: error.stderr?.substring(0, 5000)
        });
      }
    }
    
    // Проверяем статус
    try {
      const { stdout: status } = await execAsync('pm2 status xaker-backend');
      results.push({
        command: 'pm2 status',
        success: true,
        stdout: status
      });
    } catch (error: any) {
      results.push({
        command: 'pm2 status',
        success: false,
        error: error.message
      });
    }
    
    res.json({
      success: true,
      timestamp: new Date().toISOString(),
      results
    });
  } catch (error: any) {
    console.error('Deploy error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

export default router;

