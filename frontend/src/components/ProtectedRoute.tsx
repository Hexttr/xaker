import { ReactNode } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoginModal from './LoginModal';
import { useState, useEffect } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(false);

  useEffect(() => {
    // Показываем модалку логина, если не загружается и не авторизован
    if (!isLoading) {
      if (!isAuthenticated) {
        setShowLoginModal(true);
      } else {
        setShowLoginModal(false);
      }
    }
  }, [isLoading, isAuthenticated]);

  if (isLoading) {
    // Показываем загрузку во время проверки токена
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        <LoginModal
          isOpen={showLoginModal}
          onClose={() => {
            // Не позволяем закрыть модалку без логина
            // Можно закрыть только после успешного входа
          }}
          onSuccess={() => {
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

  return <>{children}</>;
};

export default ProtectedRoute;
