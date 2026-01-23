import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Принудительно создаем стили для сетчатого фона, чтобы они не были удалены при сборке
  // Используем более яркие линии для лучшей видимости (0.25 вместо 0.2)
  const gridStyle: React.CSSProperties = {
    backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.25) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.25) 1px, transparent 1px)',
    backgroundSize: '60px 60px',
    backgroundPosition: '0 0',
    position: 'absolute',
    top: '0',
    left: '0',
    right: '0',
    bottom: '0',
    width: '100%',
    height: '100%',
    zIndex: 0,
    pointerEvents: 'none',
    opacity: 1
  };

  return (
    <div className="min-h-screen bg-black flex relative">
      {/* Grid Background - сетчатый фон как на landing page */}
      <div 
        style={gridStyle}
        data-testid="grid-background"
        aria-hidden="true"
      />
      
      <Sidebar onCollapseChange={setSidebarCollapsed} />
      <div className={`flex-1 transition-all duration-300 relative z-10 ${sidebarCollapsed ? 'ml-[84px]' : 'ml-64'}`}>
        <Outlet />
      </div>
    </div>
  );
}

