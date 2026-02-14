/**
 * User Test Fixtures
 * Mock user data for Student, Educator, and Admin roles
 */

export interface TestUser {
  email: string;
  password: string;
  fullName: string;
  role: 'student' | 'educator' | 'admin';
  id: number;
  permissions: string[];
}

/**
 * Student Test User
 * Has basic permissions: view and attempt MCQs/OSCEs, view own progress
 */
export const STUDENT_USER: TestUser = {
  email: process.env.STUDENT_EMAIL || 'student@test.com',
  password: process.env.STUDENT_PASSWORD || 'Student123!@#',
  fullName: process.env.STUDENT_FULLNAME || 'Test Student',
  role: 'student',
  id: 1,
  permissions: [
    'mcq.view',
    'mcq.attempt',
    'osce.view',
    'osce.attempt',
    'progress.view.own',
    'studycard.view',
  ],
};

/**
 * Educator Test User
 * Has additional permissions: create/update/delete content, view all progress, grade
 */
export const EDUCATOR_USER: TestUser = {
  email: process.env.EDUCATOR_EMAIL || 'educator@test.com',
  password: process.env.EDUCATOR_PASSWORD || 'Educator123!@#',
  fullName: process.env.EDUCATOR_FULLNAME || 'Test Educator',
  role: 'educator',
  id: 2,
  permissions: [
    // Student permissions
    'mcq.view',
    'mcq.attempt',
    'osce.view',
    'osce.attempt',
    'progress.view.own',
    'studycard.view',
    // Educator-specific permissions
    'mcq.create',
    'mcq.update',
    'mcq.delete',
    'osce.create',
    'osce.update',
    'osce.delete',
    'studycard.create',
    'studycard.update',
    'studycard.delete',
    'progress.view.all',
    'progress.grade',
  ],
};

/**
 * Admin Test User
 * Has all permissions including user management and system configuration
 */
export const ADMIN_USER: TestUser = {
  email: process.env.ADMIN_EMAIL || 'admin@test.com',
  password: process.env.ADMIN_PASSWORD || 'Admin123!@#',
  fullName: process.env.ADMIN_FULLNAME || 'Test Admin',
  role: 'admin',
  id: 3,
  permissions: [
    // All educator permissions
    'mcq.view',
    'mcq.create',
    'mcq.update',
    'mcq.delete',
    'mcq.attempt',
    'osce.view',
    'osce.create',
    'osce.update',
    'osce.delete',
    'osce.attempt',
    'progress.view.own',
    'progress.view.all',
    'progress.grade',
    'studycard.view',
    'studycard.create',
    'studycard.update',
    'studycard.delete',
    // Admin-specific permissions
    'user.view',
    'user.create',
    'user.update',
    'user.delete',
    'admin.panel',
    'system.config',
  ],
};

/**
 * Get user by role
 */
export function getUserByRole(role: 'student' | 'educator' | 'admin'): TestUser {
  switch (role) {
    case 'student':
      return STUDENT_USER;
    case 'educator':
      return EDUCATOR_USER;
    case 'admin':
      return ADMIN_USER;
  }
}

/**
 * Invalid user credentials for negative testing
 */
export const INVALID_USER = {
  email: 'invalid@test.com',
  password: 'WrongPassword123!',
  fullName: 'Invalid User',
};

/**
 * User with weak password (for validation testing)
 */
export const WEAK_PASSWORD_USER = {
  email: 'weak@test.com',
  password: 'weak',
  fullName: 'Weak Password User',
};

/**
 * User with invalid email format
 */
export const INVALID_EMAIL_USER = {
  email: 'invalid-email',
  password: 'ValidPassword123!',
  fullName: 'Invalid Email User',
};
