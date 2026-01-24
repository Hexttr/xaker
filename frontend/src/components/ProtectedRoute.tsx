import { ReactNode } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoginModal from './LoginModal';
import { useState, useEffect } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(true); // Показываем сразу

  useEffect(() => {
    // Логирование для отладки
    console.log('[ProtectedRoute] isLoading:', isLoading, 'isAuthenticated:', isAuthenticated);
    
    // Показываем модалку логина, если не загружается и не авторизован
    if (!isLoading) {
      if (!isAuthenticated) {
        console.log('[ProtectedRoute] Показываем модалку логина');
        setShowLoginModal(true);
      } else {
        console.log('[ProtectedRoute] Пользователь авторизован, скрываем модалку');
        setShowLoginModal(false);
      }
    }
  }, [isLoading, isAuthenticated]);

  // Показываем загрузку во время проверки токена
  if (isLoading) {
    console.log('[ProtectedRoute] Показываем загрузку');
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  // Блокируем доступ, если не авторизован
  if (!isAuthenticated) {
    console.log('[ProtectedRoute] Блокируем доступ - пользователь не авторизован');
    return (
      <>
        <LoginModal
          isOpen={showLoginModal}
          onClose={() => {
            // Не позволяем закрыть модалку без логина
            console.log('[ProtectedRoute] Попытка закрыть модалку - игнорируем');
          }}
          onSuccess={() => {
            console.log('[ProtectedRoute] Успешный вход, скрываем модалку');
            setShowLoginModal(false);
            // После успешного входа компонент перерендерится и покажет children
          }}
        />
        {/* Показываем пустой экран - не рендерим children без авторизации */}
        <div className="min-h-screen bg-black flex items-center justify-center">
          <div className="text-white text-center">
            <p className="text-xl mb-4">Authentication Required</p>
            <p className="text-gray-400">Please log in to access this page</p>
          </div>
        </div>
      </>
    );
  }

  // Показываем контент только если авторизован
  console.log('[ProtectedRoute] Пользователь авторизован, показываем контент');
  return <>{children}</>;
};

export default ProtectedRoute;
