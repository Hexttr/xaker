import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-black flex relative">
      {/* Grid Background - сетчатый фон как на landing page */}
      <div className="absolute inset-0 bg-grid-dark opacity-60 pointer-events-none z-0" style={{
        backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.12) 1px, transparent 1px)',
        backgroundSize: '60px 60px'
      }} />
      
      <Sidebar onCollapseChange={setSidebarCollapsed} />
      <div className={`flex-1 transition-all duration-300 relative z-10 ${sidebarCollapsed ? 'ml-[84px]' : 'ml-64'}`}>
        <Outlet />
      </div>
    </div>
  );
}

