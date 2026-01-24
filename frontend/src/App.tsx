import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Services from './pages/Services';
import Pentests from './pages/Pentests';
import Reports from './pages/Reports';
import Analytics from './pages/Analytics';
import About from './pages/About';
import './App.css';

function App() {
  // Логируем ДО любых операций
  try {
    (window as any).__DEBUG__?.log('[App] Компонент App рендерится - НАЧАЛО');
    console.log('[App] Компонент App рендерится - НАЧАЛО (console.log)');
  } catch (e) {
    console.error('[App] Ошибка при логировании:', e);
  }
  
  // Определяем базовый путь: /app в production, / в development
  // Используем window.location для определения окружения
  const basename = window.location.hostname === 'localhost' ? '/' : '/app';
  
  try {
    (window as any).__DEBUG__?.log('[App] basename:', basename);
    console.log('[App] basename:', basename);
  } catch (e) {
    console.error('[App] Ошибка при логировании basename:', e);
  }
  
  return (
    <BrowserRouter basename={basename}>
      <Routes>
        <Route
          path="/"
          element={<Layout />}
        >
          <Route index element={<Home />} />
          <Route path="services" element={<Services />} />
          <Route path="pentests" element={<Pentests />} />
          <Route path="reports" element={<Reports />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="about" element={<About />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;








