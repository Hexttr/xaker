console.log('App.tsx: Module loading...');

console.log('App.tsx: Importing BrowserRouter...');
import { BrowserRouter, Routes, Route } from 'react-router-dom';
console.log('App.tsx: BrowserRouter imported');

console.log('App.tsx: Importing Layout...');
import Layout from './components/Layout';
console.log('App.tsx: Layout imported');

console.log('App.tsx: Importing Home...');
import Home from './pages/Home';
console.log('App.tsx: Home imported');

console.log('App.tsx: Importing other pages...');
import Services from './pages/Services';
import Pentests from './pages/Pentests';
import Reports from './pages/Reports';
import Analytics from './pages/Analytics';
import About from './pages/About';
import './App.css';
console.log('App.tsx: All imports completed');

function App() {
  console.log('App: Function called!');
  
  // Определяем базовый путь на основе текущего URL
  // Если путь начинается с /app, используем /app как basename
  // Иначе используем / (для development)
  const pathname = window.location.pathname;
  const basename = pathname.startsWith('/app') ? '/app' : '/';
  
  // Логируем для отладки
  console.log('App: pathname =', pathname, 'basename =', basename);
  console.log('App: Component rendering...');
  
  try {
    console.log('App: Creating BrowserRouter...');
    const router = (
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
    console.log('App: Router created, returning...');
    return router;
  } catch (error) {
    console.error('App: Error rendering:', error);
    return <div style={{color: 'white', padding: '20px', backgroundColor: 'red'}}>Error: {String(error)}</div>;
  }
}

export default App;








