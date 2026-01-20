import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Services from './pages/Services';
import Pentests from './pages/Pentests';
import Reports from './pages/Reports';
import BusinessAnalysis from './pages/BusinessAnalysis';
import About from './pages/About';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/services" replace />} />
          <Route path="services" element={<Services />} />
          <Route path="pentests" element={<Pentests />} />
          <Route path="reports" element={<Reports />} />
          <Route path="business-analysis" element={<BusinessAnalysis />} />
          <Route path="about" element={<About />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;








