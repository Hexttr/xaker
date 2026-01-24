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
  (window as any).__DEBUG__?.log('[App] Компонент App рендерится');
  // Определяем базовый путь: /app в production, / в development
  // Используем window.location для определения окружения
  const basename = window.location.hostname === 'localhost' ? '/' : '/app';
  (window as any).__DEBUG__?.log('[App] basename:', basename);
  
  return (
    <BrowserRouter basename={basename}>
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
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








