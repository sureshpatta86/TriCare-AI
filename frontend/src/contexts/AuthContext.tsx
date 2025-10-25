'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api-client';
import { User, LoginCredentials, RegisterData, TokenResponse, AuthContextType } from '@/types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'tricare_access_token';
const REFRESH_TOKEN_KEY = 'tricare_refresh_token';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from token on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        try {
          // Set token in axios defaults
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Fetch user data
          const response = await api.get<User>('/api/auth/me');
          setUser(response.data);
        } catch (error) {
          // Token invalid or expired, try to refresh
          await tryRefreshToken();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const tryRefreshToken = async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      clearTokens();
      return;
    }

    try {
      const response = await api.post<TokenResponse>('/api/auth/refresh', {
        refresh_token: refreshToken
      });

      const { access_token, refresh_token: new_refresh_token } = response.data;
      
      localStorage.setItem(TOKEN_KEY, access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, new_refresh_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // Fetch user data
      const userResponse = await api.get<User>('/api/auth/me');
      setUser(userResponse.data);
    } catch (error) {
      clearTokens();
    }
  };

  const clearTokens = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const login = async (credentials: LoginCredentials) => {
    const response = await api.post<TokenResponse>('/api/auth/login', credentials);
    const { access_token, refresh_token } = response.data;

    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

    // Fetch user data
    const userResponse = await api.get<User>('/api/auth/me');
    setUser(userResponse.data);
  };

  const register = async (data: RegisterData) => {
    await api.post('/api/auth/register', data);
    
    // Auto-login after registration
    await login({
      email: data.email,
      password: data.password
    });
  };

  const logout = () => {
    clearTokens();
  };

  const updateProfile = async (data: Partial<User>) => {
    const response = await api.put<User>('/api/auth/me', data);
    setUser(response.data);
  };

  const refreshToken = async () => {
    await tryRefreshToken();
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateProfile,
    refreshToken
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
