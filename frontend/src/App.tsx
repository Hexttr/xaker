import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Services from './pages/Services';
import Pentests from './pages/Pentests';
import Reports from './pages/Reports';
import Analytics from './pages/Analytics';
import About from './pages/About';
import './App.css';

function App() {
  // Определяем базовый путь: /app в production, / в development
  // В production сборке Vite автоматически устанавливает import.meta.env.PROD = true
  // Но для надежности проверяем также mode
  const basename = (import.meta.env.PROD || import.meta.env.MODE === 'production') ? '/app' : '/';
  
  return (
    <BrowserRouter basename={basename}>
      <Routes>
        <Route path="/" element={<Layout />}>
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








