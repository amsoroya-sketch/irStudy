/**
 * Test User Fixtures
 * Predefined test users for different roles
 */

export interface TestUser {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: 'STUDENT' | 'EDUCATOR' | 'ADMIN';
  isActive: boolean;
  isVerified: boolean;
}

export const TEST_USERS: {
  STUDENT: TestUser;
  EDUCATOR: TestUser;
  ADMIN: TestUser;
  INACTIVE: TestUser;
  UNVERIFIED: TestUser;
} = {
  STUDENT: {
    email: 'student@test.com',
    password: 'Student123!@#',
    firstName: 'John',
    lastName: 'Student',
    role: 'STUDENT',
    isActive: true,
    isVerified: true,
  },
  EDUCATOR: {
    email: 'educator@test.com',
    password: 'Educator123!@#',
    firstName: 'Jane',
    lastName: 'Educator',
    role: 'EDUCATOR',
    isActive: true,
    isVerified: true,
  },
  ADMIN: {
    email: 'admin@test.com',
    password: 'Admin123!@#',
    firstName: 'Alice',
    lastName: 'Admin',
    role: 'ADMIN',
    isActive: true,
    isVerified: true,
  },
  INACTIVE: {
    email: 'inactive@test.com',
    password: 'Inactive123!@#',
    firstName: 'Bob',
    lastName: 'Inactive',
    role: 'STUDENT',
    isActive: false,
    isVerified: true,
  },
  UNVERIFIED: {
    email: 'unverified@test.com',
    password: 'Unverified123!@#',
    firstName: 'Charlie',
    lastName: 'Unverified',
    role: 'STUDENT',
    isActive: true,
    isVerified: false,
  },
};

/**
 * Invalid users for negative testing
 */
export const INVALID_USERS = {
  WRONG_PASSWORD: {
    email: 'student@test.com',
    password: 'WrongPassword123!@#',
  },
  NONEXISTENT: {
    email: 'nonexistent@test.com',
    password: 'Nonexistent123!@#',
  },
  WEAK_PASSWORD: {
    email: 'weak@test.com',
    password: '123',  // Too weak
  },
  INVALID_EMAIL: {
    email: 'not-an-email',
    password: 'Valid123!@#',
  },
};
