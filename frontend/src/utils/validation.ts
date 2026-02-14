/**
 * Form validation utilities for authentication
 */

export const validateEmail = (email: string): string | null => {
  // Check for empty email first
  if (!email || email.trim() === '') {
    return 'Email is required';  // Matches test: /email.*required/i
  }
  
  // Check email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return 'Invalid email address';  // Matches test: /invalid.*email/i
  }
  
  return null;
};

export const validatePassword = (password: string): string | null => {
  if (!password || password.trim() === '') {
    return 'Password is required';  // Matches test: /password.*required/i
  }
  if (password.length < 12) {
    return 'Password must be at least 12 characters long';
  }
  if (!/[A-Z]/.test(password)) {
    return 'Password must contain at least one uppercase letter';
  }
  if (!/[a-z]/.test(password)) {
    return 'Password must contain at least one lowercase letter';
  }
  if (!/[0-9]/.test(password)) {
    return 'Password must contain at least one number';
  }
  if (!/[!@#$%^&*]/.test(password)) {
    return 'Password must contain at least one special character (!@#$%^&*)';
  }
  return null;
};

export const validatePasswordMatch = (
  password: string,
  confirmPassword: string
): string | null => {
  if (password !== confirmPassword) {
    return 'Passwords do not match';
  }
  return null;
};

export const validateFullName = (name: string): string | null => {
  if (!name || name.trim().length < 2) {
    return 'Full name must be at least 2 characters long';
  }
  if (name.trim().length > 255) {
    return 'Full name must not exceed 255 characters';
  }
  return null;
};

export const validateAcceptTerms = (accepted: boolean): string | null => {
  if (!accepted) {
    return 'You must accept the terms and conditions';
  }
  return null;
};

export const getPasswordStrength = (password: string): {
  score: number;
  label: string;
  color: 'error' | 'warning' | 'success';
} => {
  let score = 0;

  if (password.length >= 12) score++;
  if (password.length >= 16) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[!@#$%^&*]/.test(password)) score++;

  if (score <= 2) {
    return { score, label: 'Weak', color: 'error' };
  } else if (score <= 4) {
    return { score, label: 'Fair', color: 'warning' };
  } else {
    return { score, label: 'Strong', color: 'success' };
  }
};
