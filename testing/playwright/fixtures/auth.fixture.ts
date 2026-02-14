/**
 * Authentication Test Fixtures
 * Provides authenticated browser contexts for different user roles
 */

import { test as base, Page, BrowserContext } from '@playwright/test';
import { STUDENT_USER, EDUCATOR_USER, ADMIN_USER, TestUser } from './users.fixture';

const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Extended test fixtures with authentication helpers
 */
export type AuthFixtures = {
  studentPage: Page;
  educatorPage: Page;
  adminPage: Page;
  authenticatedPage: (user: TestUser) => Promise<Page>;
  mockApi: void;
};

/**
 * Setup API mocking for all tests
 */
async function setupApiMocking(page: Page) {
  // Mock login endpoint
  await page.route(`${API_BASE_URL}/auth/login`, async (route, request) => {
    const body = request.postDataJSON();

    // Mock student login
    if (body.email === 'student@test.com' && body.password === 'Student123!@#') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          accessToken: 'mock-student-access-token',  // Frontend expects camelCase
          refreshToken: 'mock-student-refresh-token',
          tokenType: 'bearer',
        }),
      });
      return;
    }

    // Mock educator login
    if (body.email === 'educator@test.com' && body.password === 'Educator123!@#') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          accessToken: 'mock-educator-access-token',  // Frontend expects camelCase
          refreshToken: 'mock-educator-refresh-token',
          tokenType: 'bearer',
        }),
      });
      return;
    }

    // Mock invalid credentials
    await route.fulfill({
      status: 401,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Invalid credentials' }),
    });
  });

  // Mock /users/me endpoint (required by AuthContext after login)
  await page.route(`${API_BASE_URL}/users/me`, async (route, request) => {
    const auth = request.headers()['authorization'];

    if (auth?.includes('mock-student-access-token')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          email: 'student@test.com',
          fullName: 'Test Student',
          role: 'student',
          isVerified: true,
          isActive: true,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }),
      });
      return;
    }

    if (auth?.includes('mock-educator-access-token')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 2,
          email: 'educator@test.com',
          fullName: 'Test Educator',
          role: 'educator',
          isVerified: true,
          isActive: true,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }),
      });
      return;
    }

    await route.fulfill({
      status: 401,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Unauthorized' }),
    });
  });

  // Mock token refresh endpoint (to prevent axios interceptor from hanging)
  await page.route(`${API_BASE_URL}/auth/refresh`, async (route) => {
    await route.fulfill({
      status: 401,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Refresh token invalid or expired' }),
    });
  });

  // Mock permissions endpoint
  await page.route(`${API_BASE_URL}/permissions/me`, async (route, request) => {
    const auth = request.headers()['authorization'];

    if (auth?.includes('mock-student-access-token')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          role: 'student',
          permissions: [
            'mcq.view', 'mcq.attempt', 'osce.view',
            'osce.attempt', 'progress.view.own', 'studycard.view',
          ],
        }),
      });
      return;
    }

    if (auth?.includes('mock-educator-access-token')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          role: 'educator',
          permissions: [
            'mcq.view', 'mcq.attempt', 'mcq.create', 'mcq.update', 'mcq.delete',
            'osce.view', 'osce.attempt', 'osce.create', 'osce.update', 'osce.delete',
            'progress.view.all', 'progress.view.own', 'progress.grade',
            'studycard.view', 'studycard.create',
          ],
        }),
      });
      return;
    }

    await route.fulfill({
      status: 401,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Unauthorized' }),
    });
  });
}

/**
 * Extend Playwright test with authentication fixtures
 */
export const test = base.extend<AuthFixtures>({
  /**
   * Mock API - auto-enabled for all tests
   */
  mockApi: [async ({ page }, use) => {
    await setupApiMocking(page);
    await use();
  }, { auto: true }],
  /**
   * Student authenticated page
   */
  studentPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    // Set mock authentication tokens
    await setAuthTokens(page, STUDENT_USER);

    await use(page);
    await context.close();
  },

  /**
   * Educator authenticated page
   */
  educatorPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await setAuthTokens(page, EDUCATOR_USER);

    await use(page);
    await context.close();
  },

  /**
   * Admin authenticated page
   */
  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await setAuthTokens(page, ADMIN_USER);

    await use(page);
    await context.close();
  },

  /**
   * Generic authenticated page for any user
   */
  authenticatedPage: async ({ browser }, use) => {
    const authenticateAs = async (user: TestUser): Promise<Page> => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await setAuthTokens(page, user);
      return page;
    };

    await use(authenticateAs);
  },
});

/**
 * Set authentication tokens in localStorage
 */
async function setAuthTokens(page: Page, user: TestUser) {
  await page.goto('/');

  // Mock JWT tokens (in real test, these would come from API)
  const mockAccessToken = generateMockJWT(user);
  const mockRefreshToken = generateMockJWT(user, 7 * 24 * 60 * 60); // 7 days

  await page.evaluate(
    ({ user, accessToken, refreshToken }) => {
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('user', JSON.stringify(user));
    },
    { user, accessToken: mockAccessToken, refreshToken: mockRefreshToken }
  );
}

/**
 * Generate mock JWT token (for testing purposes only)
 * In real tests, you'd use tokens from the backend
 */
function generateMockJWT(user: TestUser, expiresInSeconds: number = 15 * 60): string {
  const header = Buffer.from(
    JSON.stringify({ alg: 'HS256', typ: 'JWT' })
  ).toString('base64url');

  const payload = Buffer.from(
    JSON.stringify({
      sub: user.id,
      email: user.email,
      role: user.role,
      exp: Math.floor(Date.now() / 1000) + expiresInSeconds,
      iat: Math.floor(Date.now() / 1000),
    })
  ).toString('base64url');

  const signature = 'mock-signature';

  return `${header}.${payload}.${signature}`;
}

/**
 * Helper: Login via UI (for E2E tests that need real login flow)
 */
export async function loginViaUI(page: Page, email: string, password: string) {
  await page.goto('/login');
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');

  // Wait for redirect to dashboard
  await page.waitForURL('/dashboard');
}

/**
 * Helper: Logout
 */
export async function logout(page: Page) {
  // Clear localStorage
  await page.evaluate(() => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  });

  await page.goto('/login');
}

/**
 * Helper: Check if user is authenticated
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  return page.evaluate(() => {
    const token = localStorage.getItem('accessToken');
    return token !== null;
  });
}

/**
 * Helper: Get current user from localStorage
 */
export async function getCurrentUser(page: Page): Promise<TestUser | null> {
  return page.evaluate(() => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  });
}

export { expect } from '@playwright/test';
