console.log('main.tsx: Starting module execution');

import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import './index.css';

console.log('main.tsx: All imports completed');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 минут - данные считаются свежими
      gcTime: 10 * 60 * 1000, // 10 минут - время хранения в кэше (было cacheTime)
      refetchOnMount: false, // Не делать запрос при монтировании, если данные в кэше
      refetchOnWindowFocus: false, // Не делать запрос при фокусе окна
      refetchOnReconnect: true, // Делать запрос только при переподключении
    },
  },
});

console.log('main.tsx: QueryClient created');

const rootElement = document.getElementById('root');
console.log('main.tsx: Root element:', rootElement);

if (!rootElement) {
  console.error('main.tsx: Root element not found!');
  throw new Error('Root element not found!');
}

console.log('main.tsx: Creating root...');
const root = ReactDOM.createRoot(rootElement);
console.log('main.tsx: Root created, rendering...');

root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
console.log('main.tsx: Render called successfully');








