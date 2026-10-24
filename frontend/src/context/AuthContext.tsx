import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../api/client';
import { User, UserRole } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username_or_email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  demoLogin: (role: UserRole) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = api.getToken();
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const currentUser = await api.getMe();
        setUser(currentUser);
      } catch (err) {
        console.error('Failed to restore session:', err);
        api.setToken(null);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const login = async (username_or_email: string, password: string) => {
    const res = await api.login(username_or_email, password);
    setUser(res.user);
  };

  const register = async (data: any) => {
    const newUser = await api.register(data);
    await login(newUser.email, data.password);
  };

  const logout = () => {
    api.setToken(null);
    setUser(null);
  };

  const demoLogin = async (role: UserRole) => {
    let email = 'customer@fooddelivery.local';
    let pass = 'Password123!';

    if (role === 'RESTAURANT') {
      email = 'restaurant@fooddelivery.local';
      pass = 'Password123!';
    } else if (role === 'DELIVERY_AGENT') {
      email = 'agent@fooddelivery.local';
      pass = 'Password123!';
    } else if (role === 'ADMIN') {
      email = 'admin@fooddelivery.local';
      pass = 'AdminPassword123!';
    }

    await login(email, pass);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, demoLogin }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
