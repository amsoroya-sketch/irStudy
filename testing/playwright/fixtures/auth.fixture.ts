/**
 * Authentication Test Fixtures - TASK_010 Fixed
 * Fix 1: Login mock returns access_token (snake_case) to match AuthContext.tsx line 93:
 *   const { access_token, refresh_token } = response.data;
 * Fix 2: API mocking added to studentPage/educatorPage/adminPage new contexts
 * Fix 3: Progress and MCQ endpoints mocked to prevent loading state timeouts
 */

import { test as base, Page } from '@playwright/test';
import { STUDENT_USER, EDUCATOR_USER, ADMIN_USER, TestUser } from './users.fixture';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export type AuthFixtures = {
  studentPage: Page;
  educatorPage: Page;
  adminPage: Page;
  authenticatedPage: (user: TestUser) => Promise<Page>;
  mockApi: void;
};

/**
 * Setup all required API mocks for a page context.
 * Must be called before page navigation in new contexts (studentPage, etc.).
 */
async function setupApiMocking(page: Page) {
  // /auth/login - returns snake_case matching AuthContext.tsx LoginResponse interface
  await page.route(API_BASE_URL + '/auth/login', async (route, request) => {
    const body = request.postDataJSON();
    if (body.email === 'student@test.com' && body.password === 'Student123!@#') {
      await route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-student-access-token',
          refresh_token: 'mock-student-refresh-token',
          token_type: 'bearer',
          expires_in: 900,
        }),
      });
      return;
    }
    if (body.email === 'educator@test.com' && body.password === 'Educator123!@#') {
      await route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-educator-access-token',
          refresh_token: 'mock-educator-refresh-token',
          token_type: 'bearer',
          expires_in: 900,
        }),
      });
      return;
    }
    await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Invalid credentials' }) });
  });

  // /users/me - required by AuthContext after login
  await page.route(API_BASE_URL + '/users/me', async (route, request) => {
    const auth = request.headers()['authorization'] || '';
    if (auth.includes('mock-educator-access-token')) {
      await route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({ id: 2, email: 'educator@test.com', fullName: 'Test Educator', role: 'educator', isVerified: true, isActive: true, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() }),
      });
      return;
    }
    // Any Bearer token (including mock JWT from setAuthTokens) gets student profile
    if (auth.startsWith('Bearer ') && auth.length > 20) {
      await route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({ id: 1, email: 'student@test.com', fullName: 'Test Student', role: 'student', isVerified: true, isActive: true, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() }),
      });
      return;
    }
    await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Unauthorized' }) });
  });

  // /auth/refresh - return 401 to prevent axios interceptor from hanging
  await page.route(API_BASE_URL + '/auth/refresh', async (route) => {
    await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Refresh token invalid or expired' }) });
  });

  // /permissions/me - required by usePermissions hook (Dashboard, ProtectedRoute)
  await page.route(API_BASE_URL + '/permissions/me', async (route, request) => {
    const auth = request.headers()['authorization'] || '';
    if (auth.includes('mock-educator-access-token')) {
      await route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({ role: 'educator', permissions: ['mcq.view', 'mcq.attempt', 'mcq.create', 'mcq.update', 'mcq.delete', 'osce.view', 'osce.attempt', 'osce.create', 'progress.view.all', 'progress.view.own', 'studycard.view', 'studycard.create'] }),
      });
      return;
    }
    if (auth.startsWith('Bearer ') && auth.length > 10) {
      await route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({ role: 'student', permissions: ['mcq.view', 'mcq.attempt', 'osce.view', 'osce.attempt', 'progress.view.own', 'studycard.view'] }),
      });
      return;
    }
    await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Unauthorized' }) });
  });

  // /progress/me - required by PerformanceDashboard
  await page.route(API_BASE_URL + '/progress/me', async (route) => {
    await route.fulfill({
      status: 200, contentType: 'application/json',
      body: JSON.stringify({
        total_mcq_attempts: 42, mcq_accuracy_rate: 78.5,
        total_osce_completions: 15, study_cards_reviewed: 120,
        study_card_retention_rate: 85.0,
        weak_areas: ['Cardiology', 'Psychiatry'],
        specialty_breakdown: [{ specialty: 'Cardiology', attempts: 20, accuracy: 65.0 }],
      }),
    });
  });

  // /progress/weekly-trends - required by PerformanceDashboard charts
  await page.route(API_BASE_URL + '/progress/weekly-trends*', async (route) => {
    await route.fulfill({
      status: 200, contentType: 'application/json',
      body: JSON.stringify({ trends: [{ week: '2026-W01', attempts: 10, accuracy: 70.0 }, { week: '2026-W02', attempts: 15, accuracy: 80.0 }] }),
    });
  });

  // /mcqs - required by MCQ Browser
  await page.route(API_BASE_URL + '/mcqs*', async (route, request) => {
    const url = new URL(request.url());
    const skip = parseInt(url.searchParams.get('skip') || '0', 10);
    const limit = parseInt(url.searchParams.get('limit') || '20', 10);
    const mockItems = Array.from({ length: Math.min(limit, 3) }, (_, i) => ({
      id: skip + i + 1,
      question: 'A patient presents with acute chest pain radiating to the left arm. What is the most appropriate initial management?',
      option_a: 'Aspirin 300mg chewed immediately',
      option_b: 'Paracetamol 1g orally',
      option_c: 'Wait for ECG results',
      option_d: 'Order chest X-ray first',
      option_e: 'Call cardiology',
      correct_answer: 'A',
      explanation: 'Aspirin inhibits platelet aggregation and is first-line for suspected ACS per AMC guidelines.',
      category: 'Cardiology',
      difficulty: 'medium',
      tags: ['AMC', 'Cardiology', 'Emergency'],
      citation: 'AMC Clinical Examination, 8th Edition, Chapter 12',
    }));
    await route.fulfill({
      status: 200, contentType: 'application/json',
      body: JSON.stringify({ items: mockItems, total: 3, skip, limit }),
    });
  });
}

/**
 * Extend Playwright test with authentication fixtures
 */
export const test = base.extend<AuthFixtures>({
  /**
   * Mock API - auto-enabled for tests using default page fixture
   */
  mockApi: [async ({ page }, use) => {
    await setupApiMocking(page);
    await use();
  }, { auto: true }],

  /**
   * Student authenticated page
   * Creates new browser context with API mocking and student auth in localStorage
   */
  studentPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await setupApiMocking(page);
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
    await setupApiMocking(page);
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
    await setupApiMocking(page);
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
      await setupApiMocking(page);
      await setAuthTokens(page, user);
      return page;
    };
    await use(authenticateAs);
  },
});

/**
 * Set authentication tokens in localStorage
 * Must navigate to the app first to access the correct localStorage scope
 */
async function setAuthTokens(page: Page, user: TestUser) {
  await page.goto('/');
  const mockAccessToken = generateMockJWT(user);
  const mockRefreshToken = generateMockJWT(user, 7 * 24 * 60 * 60);
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
 * Generate mock JWT token for testing
 */
function generateMockJWT(user: TestUser, expiresInSeconds: number = 15 * 60): string {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const payload = Buffer.from(JSON.stringify({
    sub: user.id, email: user.email, role: user.role,
    exp: Math.floor(Date.now() / 1000) + expiresInSeconds,
    iat: Math.floor(Date.now() / 1000),
  })).toString('base64url');
  return header + '.' + payload + '.mock-signature';
}

export async function loginViaUI(page: Page, email: string, password: string) {
  await page.goto('/login');
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard', { timeout: 15000 });
}

export async function logout(page: Page) {
  await page.evaluate(() => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  });
  await page.goto('/login');
}

export async function isAuthenticated(page: Page): Promise<boolean> {
  return page.evaluate(() => localStorage.getItem('accessToken') !== null);
}

export async function getCurrentUser(page: Page): Promise<TestUser | null> {
  return page.evaluate(() => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  });
}

export { expect } from '@playwright/test';
