import { Link, useLocation } from 'react-router-dom';
import { 
  FiServer, 
  FiShield, 
  FiFileText, 
  FiBarChart2, 
  FiInfo,
  FiChevronLeft,
  FiChevronRight
} from 'react-icons/fi';
import { useState } from 'react';

interface MenuItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

const menuItems: MenuItem[] = [
  { path: '/services', label: 'Сервисы', icon: <FiServer /> },
  { path: '/pentests', label: 'Пентесты', icon: <FiShield /> },
  { path: '/reports', label: 'Отчеты', icon: <FiFileText /> },
  { path: '/business-analysis', label: 'Бизнес анализ', icon: <FiBarChart2 /> },
  { path: '/about', label: 'О сервисе', icon: <FiInfo /> },
];

interface SidebarProps {
  onCollapseChange?: (collapsed: boolean) => void;
}

export default function Sidebar({ onCollapseChange }: SidebarProps) {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  const handleToggle = () => {
    const newCollapsed = !collapsed;
    setCollapsed(newCollapsed);
    onCollapseChange?.(newCollapsed);
  };

  return (
    <div
      className={`bg-gray-900 border-r border-gray-800 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      } flex flex-col h-screen fixed left-0 top-0 z-50`}
    >
      {/* Logo */}
      <div className="p-4 border-b border-gray-800 flex items-center justify-between">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-red-600 to-red-800 rounded-lg flex items-center justify-center">
              <FiShield className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="text-white font-bold text-sm">
                Pentest<span className="text-red-600">.red</span>
              </div>
              <div className="text-gray-400 text-xs">ENTERPRISE</div>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 bg-gradient-to-br from-red-600 to-red-800 rounded-lg flex items-center justify-center mx-auto">
            <FiShield className="w-5 h-5 text-white" />
          </div>
        )}
        <button
          onClick={handleToggle}
          className="text-gray-400 hover:text-white transition-colors p-1 rounded hover:bg-gray-800"
        >
          {collapsed ? <FiChevronRight /> : <FiChevronLeft />}
        </button>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                isActive
                  ? 'bg-red-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`}
              title={collapsed ? item.label : undefined}
            >
              <span className="text-xl flex-shrink-0">{item.icon}</span>
              {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}

