import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  username: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  (window as any).__DEBUG__?.log('[AuthContext] AuthProvider монтируется');
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Загружаем токен из localStorage при монтировании
  useEffect(() => {
    const checkAuth = async () => {
      (window as any).__DEBUG__?.log('[AuthContext] Проверка аутентификации...');
      const storedToken = localStorage.getItem('authToken');
      (window as any).__DEBUG__?.log('[AuthContext] Токен в localStorage:', storedToken ? 'найден' : 'не найден');
      
      if (storedToken) {
        setToken(storedToken);
        // Проверяем валидность токена
        await verifyToken(storedToken);
      } else {
        // Нет токена - точно не авторизован
        (window as any).__DEBUG__?.log('[AuthContext] Токен не найден, пользователь не авторизован');
        setToken(null);
        setUser(null);
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  // Проверка валидности токена
  const verifyToken = async (tokenToVerify: string) => {
    try {
      console.log('[AuthContext] Проверка токена...');
      const response = await fetch('/api/auth/verify', {
        headers: {
          'Authorization': `Bearer ${tokenToVerify}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('[AuthContext] Токен валиден, пользователь:', data.user);
        setUser(data.user);
        setToken(tokenToVerify);
      } else {
        // Токен невалиден, удаляем
        console.log('[AuthContext] Токен невалиден, удаляем');
        localStorage.removeItem('authToken');
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      console.error('[AuthContext] Ошибка при проверке токена:', error);
      localStorage.removeItem('authToken');
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
      console.log('[AuthContext] Проверка завершена, isLoading = false');
    }
  };

  // Логин
  const login = async (username: string, password: string) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Ошибка при входе');
      }

      // Сохраняем токен и пользователя
      localStorage.setItem('authToken', data.token);
      setToken(data.token);
      setUser(data.user);
    } catch (error: any) {
      console.error('Ошибка при входе:', error);
      throw error;
    }
  };

  // Логаут
  const logout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        login,
        logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

