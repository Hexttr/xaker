import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import App from './App';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 минут - данные считаются свежими
      gcTime: 10 * 60 * 1000, // 10 минут - время хранения в кэше (было cacheTime)
      refetchOnMount: false, // Не делать запрос при монтировании, если данные в кэше
      refetchOnWindowFocus: false, // Не делать запрос при фокусе окна
      refetchOnReconnect: false, // Не делать запрос при переподключении (отключаем автоматический refetch)
      retry: false, // Отключаем повторные попытки при ошибках
    },
  },
});

// АГРЕССИВНАЯ очистка Service Workers при загрузке React
if ('serviceWorker' in navigator) {
  // Удаляем все регистрации
  navigator.serviceWorker.getRegistrations().then(function(registrations) {
    console.log('[React] Найдено Service Workers:', registrations.length);
    registrations.forEach(function(registration) {
      registration.unregister().then(function(success) {
        console.log('[React] Service Worker удален:', success);
      }).catch(function(error) {
        console.error('[React] Ошибка удаления:', error);
      });
    });
  });
  
  // Очищаем кэши
  if ('caches' in window) {
    caches.keys().then(function(names) {
      console.log('[React] Найдено кэшей:', names.length);
      names.forEach(function(name) {
        caches.delete(name);
      });
    });
  }
}

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element not found!');
}

// Логи, которые не удаляются при минификации
declare global {
  interface Window {
    __DEBUG__?: {
      log: (...args: any[]) => void;
    };
  }
}

window.__DEBUG__ = window.__DEBUG__ || {
  log: function(...args: any[]) {
    console.log('[DEBUG]', ...args);
  }
};

window.__DEBUG__.log('[main.tsx] Инициализация приложения...');

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </QueryClientProvider>
  </React.StrictMode>
);

window.__DEBUG__?.log('[main.tsx] Приложение инициализировано');








