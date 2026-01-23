console.log('App.tsx: Module loading...');

// Простой тест - сначала без импортов
function App() {
  console.log('App: Function called!');
  
  return (
    <div style={{color: 'white', padding: '20px', backgroundColor: 'blue', minHeight: '100vh'}}>
      <h1>App is working!</h1>
      <p>Pathname: {window.location.pathname}</p>
    </div>
  );
}

// Пробуем импортировать после определения функции
console.log('App.tsx: Importing BrowserRouter...');
import { BrowserRouter, Routes, Route } from 'react-router-dom';
console.log('App.tsx: BrowserRouter imported');

console.log('App.tsx: Importing Layout...');
let Layout;
try {
  Layout = require('./components/Layout').default;
  console.log('App.tsx: Layout imported');
} catch (e) {
  console.error('App.tsx: Error importing Layout:', e);
}

console.log('App.tsx: Importing Home...');
let Home;
try {
  Home = require('./pages/Home').default;
  console.log('App.tsx: Home imported');
} catch (e) {
  console.error('App.tsx: Error importing Home:', e);
}

import './App.css';
console.log('App.tsx: All imports completed');

export default App;








