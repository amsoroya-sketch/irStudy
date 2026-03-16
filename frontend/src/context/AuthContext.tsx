/**
 * Authentication Context
 * Manages user authentication state, tokens, and login/logout
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axiosInstance from '../utils/axiosInstance';
import {
  User,
  AuthState,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
} from '../types/auth';

// ============================================================
// Context Type
// ============================================================

interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

// ============================================================
// Create Context
// ============================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================================
// Auth Provider Component
// ============================================================

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    token: null,
    refreshToken: null,
    isLoading: true,
    error: null,
  });

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    const userStr = localStorage.getItem('user');

    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        setAuthState({
          user,
          isAuthenticated: true,
          token,
          refreshToken,
          isLoading: false,
          error: null,
        });
      } catch (err) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        setAuthState((prev) => ({ ...prev, isLoading: false }));
      }
    } else {
      setAuthState((prev) => ({ ...prev, isLoading: false }));
    }
  }, []);

  // Login function
  const login = async (credentials: LoginRequest) => {
    try {
      setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));

      const response = await axiosInstance.post<LoginResponse>(
        '/auth/login',
        {
          email: credentials.email,
          password: credentials.password,
        }
      );

      const { access_token, refresh_token } = response.data;

      // Fetch user data
      const userResponse = await axiosInstance.get<User>(
        '/users/me',
        {
          headers: { Authorization: `Bearer ${access_token}` },
        }
      );

      const user = userResponse.data;

      // Store tokens and user info
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      localStorage.setItem('user', JSON.stringify(user));

      // Remember me functionality
      if (credentials.rememberMe) {
        localStorage.setItem('rememberMe', 'true');
      }

      setAuthState({
        user,
        isAuthenticated: true,
        token: access_token,
        refreshToken: refresh_token,
        isLoading: false,
        error: null,
      });
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail ||
        err.message ||
        'Login failed. Please try again.';

      setAuthState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));

      throw new Error(errorMessage);
    }
  };

  // Register function
  const register = async (data: RegisterRequest) => {
    try {
      setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));

      await axiosInstance.post<RegisterResponse>(
        '/auth/register',
        {
          email: data.email,
          password: data.password,
          full_name: data.fullName,
        }
      );

      setAuthState((prev) => ({
        ...prev,
        isLoading: false,
        error: null,
      }));
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail ||
        err.message ||
        'Registration failed. Please try again.';

      setAuthState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));

      throw new Error(errorMessage);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    localStorage.removeItem('rememberMe');

    setAuthState({
      user: null,
      isAuthenticated: false,
      token: null,
      refreshToken: null,
      isLoading: false,
      error: null,
    });
  };

  // Clear error
  const clearError = () => {
    setAuthState((prev) => ({ ...prev, error: null }));
  };

  // Provide context
  return (
    <AuthContext.Provider
      value={{
        ...authState,
        login,
        register,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// ============================================================
// useAuth Hook
// ============================================================

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export default AuthContext;
