import { useState } from 'react';
import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-black flex">
      <Sidebar onCollapseChange={setSidebarCollapsed} />
      <div className={`flex-1 transition-all duration-300 ${sidebarCollapsed ? 'ml-[84px]' : 'ml-64'}`}>
        <Outlet />
      </div>
    </div>
  );
}

