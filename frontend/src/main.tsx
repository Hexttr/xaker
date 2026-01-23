console.log('main.tsx: Starting module execution');

import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
console.log('main.tsx: React and QueryClient imported');

console.log('main.tsx: About to import App...');
import App from './App';
console.log('main.tsx: App imported, type:', typeof App, 'value:', App);

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

try {
  console.log('main.tsx: Creating App component...');
  const appElement = <App />;
  console.log('main.tsx: App element created');
  
  console.log('main.tsx: Wrapping in providers...');
  const wrappedApp = (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        {appElement}
      </QueryClientProvider>
    </React.StrictMode>
  );
  console.log('main.tsx: Wrapped app created');
  
  console.log('main.tsx: Calling root.render...');
  root.render(wrappedApp);
  console.log('main.tsx: Render called successfully');
} catch (error) {
  console.error('main.tsx: ERROR during render:', error);
  root.render(<div style={{color: 'white', padding: '20px', backgroundColor: 'red'}}>Render Error: {String(error)}</div>);
}

// Проверка через таймаут
setTimeout(() => {
  const rootContent = document.getElementById('root')?.innerHTML;
  console.log('main.tsx: Root content after 1s:', rootContent?.substring(0, 200));
  console.log('main.tsx: Root children count:', document.getElementById('root')?.children.length);
}, 1000);








