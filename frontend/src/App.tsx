console.log('App.tsx: Module loading...');

// Простейший тест - без импортов
function App() {
  console.log('App: Function called!');
  console.log('App: Returning simple div...');
  
  return (
    <div style={{color: 'white', padding: '20px', backgroundColor: 'blue', minHeight: '100vh', fontSize: '24px'}}>
      <h1>✅ App is working!</h1>
      <p>Pathname: {window.location.pathname}</p>
      <p>If you see this, React is rendering correctly!</p>
    </div>
  );
}

console.log('App.tsx: Function defined, exporting...');

export default App;








