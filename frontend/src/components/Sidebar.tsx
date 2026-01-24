import { Link, useLocation } from 'react-router-dom';
import { 
  FiServer, 
  FiShield, 
  FiFileText, 
  FiBarChart2, 
  FiInfo,
  FiChevronLeft,
  FiChevronRight,
  FiHome
} from 'react-icons/fi';
import { useState } from 'react';
import Logo from './Logo';

interface MenuItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

const menuItems: MenuItem[] = [
  { path: '/', label: 'Главная', icon: <FiHome /> },
  { path: '/services', label: 'Сервисы', icon: <FiServer /> },
  { path: '/pentests', label: 'Пентесты', icon: <FiShield /> },
  { path: '/reports', label: 'Отчеты', icon: <FiFileText /> },
  { path: '/analytics', label: 'Аналитика', icon: <FiBarChart2 /> },
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
        collapsed ? 'w-[84px]' : 'w-64'
      } flex flex-col h-screen fixed left-0 top-0 z-50`}
    >
      {/* Logo */}
      <Link to="/" className="p-4 border-b border-gray-800 flex items-center justify-center hover:bg-gray-800/50 transition-colors">
        {collapsed ? (
          <Logo size="md" showText={false} />
        ) : (
          <Logo size="md" showText={true} />
        )}
      </Link>

      {/* Menu Items */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = item.path === '/' 
            ? location.pathname === '/' 
            : location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                isActive
                  ? 'bg-red-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              } ${collapsed ? 'justify-center' : ''}`}
              title={collapsed ? item.label : undefined}
            >
              <span className="text-xl flex-shrink-0">{item.icon}</span>
              {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Collapse Button */}
      <div className="p-4 border-t border-gray-800">
        <button
          onClick={handleToggle}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800 hover:text-white transition-colors ${
            collapsed ? 'justify-center' : ''
          }`}
          title={collapsed ? 'Развернуть' : 'Свернуть'}
        >
          <span className="text-xl flex-shrink-0">
            {collapsed ? <FiChevronRight /> : <FiChevronLeft />}
          </span>
          {!collapsed && <span className="text-sm font-medium">Свернуть</span>}
        </button>
      </div>
    </div>
  );
}

