/**
 * Authentication TypeScript types and interfaces
 * Defines User, AuthState, and API response structures
 */

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'student' | 'instructor' | 'admin';
  createdAt: string;
  updatedAt: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  acceptTerms: boolean;
}

export interface RegisterResponse {
  id: string;
  email: string;
  fullName: string;
  role: string;
  createdAt: string;
  updatedAt: string;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

export interface RefreshTokenResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface AuthError {
  code: string;
  message: string;
  field?: string;
}

export interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  fullName?: string;
  acceptTerms?: string;
  rememberMe?: string;
}

export interface FormTouched {
  email?: boolean;
  password?: boolean;
  confirmPassword?: boolean;
  fullName?: boolean;
  acceptTerms?: boolean;
}
