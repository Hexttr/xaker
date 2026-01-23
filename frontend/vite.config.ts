import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // В production всегда используем /app/, в development - /
  const base = mode === 'production' || process.env.NODE_ENV === 'production' ? '/app/' : '/';
  
  return {
    plugins: [react()],
    base,
    server: {
      port: 5173,
      host: '0.0.0.0',
      proxy: {
        '/api': {
          target: 'http://localhost:3000',
          changeOrigin: true,
        },
        '/socket.io': {
          target: 'http://localhost:3000',
          ws: true,
        },
      },
    },
  };
});

