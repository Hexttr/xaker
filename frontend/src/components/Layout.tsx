import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-black flex relative">
      {/* Grid Background */}
      <div className="absolute inset-0 bg-grid-dark opacity-50 pointer-events-none" />
      
      <Sidebar onCollapseChange={setSidebarCollapsed} />
      <div className={`flex-1 transition-all duration-300 relative z-10 ${sidebarCollapsed ? 'ml-[84px]' : 'ml-64'}`}>
        <Outlet />
      </div>
    </div>
  );
}

