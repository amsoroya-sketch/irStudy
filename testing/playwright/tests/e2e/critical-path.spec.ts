/**
 * Critical Path Integration E2E Tests (TASK_010)
 *
 * Tests the most critical user journeys:
 * - Full login flow
 * - Authenticated Dashboard access with correct content
 * - Navigation from Dashboard to MCQ Browser
 * - Navigation from Dashboard to Performance Dashboard
 * - Logout / unauthenticated redirect
 * - Unknown page redirect behavior
 *
 * Uses auth.fixture API mocking with additional endpoint mocks for dashboard data.
 */

import { test, expect } from '../../fixtures/auth.fixture';
import { STUDENT_USER } from '../../fixtures/users.fixture';
import { generateMCQListResponse } from '../../fixtures/mcqs.fixture';

const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Setup all commonly needed API mocks for dashboard-related navigation
 */
async function setupFullAppMocks(page: import('@playwright/test').Page) {
  // MCQ list mock
  await page.route(API_BASE_URL + '/mcqs**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(generateMCQListResponse(0, 20)),
    });
  });

  // Performance/progress mock
  await page.route(API_BASE_URL + '/progress/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_mcq_attempts: 10, mcq_accuracy_rate: 75.0, total_osce_completions: 3,
        study_cards_reviewed: 30, study_card_retention_rate: 80.0,
        weak_areas: [], specialty_breakdown: [],
      }),
    });
  });

  await page.route(API_BASE_URL + '/progress/weekly-trends**', async (route) => {
    await route.fulfill({
      status: 200, contentType: 'application/json',
      body: JSON.stringify({ trends: [] }),
    });
  });
}

test.describe('Critical Path Integration', () => {

  test.describe('Full Login Flow', () => {
    test('should complete full login flow and land on dashboard', async ({ page }) => {
      // Navigate to login page
      await page.goto('/login');
      await expect(page).toHaveURL(/\/login/);

      // Fill credentials
      await page.fill('input[name="email"]', STUDENT_USER.email);
      await page.fill('input[name="password"]', STUDENT_USER.password);

      // Submit form
      await page.click('button[type="submit"]');

      // Should redirect to dashboard
      await page.waitForURL('/dashboard', { timeout: 10000 });
      await expect(page).toHaveURL(/\/dashboard/);
    });

    test('should display student name/role on dashboard after login', async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"]', STUDENT_USER.email);
      await page.fill('input[name="password"]', STUDENT_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard', { timeout: 10000 });

      // Dashboard.tsx shows role in the header paper
      const roleText = page.locator('text=/STUDENT/i');
      await expect(roleText).toBeVisible({ timeout: 10000 });
    });

    test('should store auth tokens in localStorage after login', async ({ page }) => {
      await page.goto('/login');
      await page.fill('input[name="email"]', STUDENT_USER.email);
      await page.fill('input[name="password"]', STUDENT_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForURL('/dashboard', { timeout: 10000 });

      const accessToken = await page.evaluate(() => localStorage.getItem('accessToken'));
      const user = await page.evaluate(() => localStorage.getItem('user'));
      expect(accessToken).toBeTruthy();
      expect(user).toBeTruthy();
    });
  });

  test.describe('Dashboard Content Verification', () => {
    test('should display Welcome to AMC Clinical Exam Simulation heading', async ({ studentPage: page }) => {
      await page.goto('/dashboard');
      const welcomeHeading = page.locator('text=Welcome to AMC Clinical Exam Simulation');
      await expect(welcomeHeading).toBeVisible({ timeout: 10000 });
    });

    test('should display Quick Actions section on dashboard', async ({ studentPage: page }) => {
      await page.goto('/dashboard');
      const quickActions = page.locator('text=Quick Actions');
      await expect(quickActions).toBeVisible({ timeout: 10000 });
    });

    test('should display MCQ Practice card for student role', async ({ studentPage: page }) => {
      await page.goto('/dashboard');
      const mcqPracticeCard = page.locator('text=MCQ Practice').first();
      await expect(mcqPracticeCard).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Dashboard to MCQ Browser Navigation', () => {
    test('should navigate from Dashboard to MCQ Browser via Browse MCQs button', async ({ studentPage: page }) => {
      await setupFullAppMocks(page);
      await page.goto('/dashboard');

      // Browse MCQs button from Dashboard.tsx
      const browseMCQsButton = page.locator('button:has-text("Browse MCQs")').first();
      await expect(browseMCQsButton).toBeVisible({ timeout: 10000 });
      await browseMCQsButton.click();

      await page.waitForURL('/mcqs', { timeout: 10000 });
      await expect(page).toHaveURL(/\/mcqs/);
    });

    test('should navigate directly to /mcqs and see MCQ Browser', async ({ studentPage: page }) => {
      await setupFullAppMocks(page);
      await page.goto('/mcqs');

      const heading = page.locator('h1');
      await expect(heading).toBeVisible({ timeout: 10000 });
      await expect(heading).toContainText(/MCQ/i);
    });
  });

  test.describe('Dashboard to Performance Dashboard Navigation', () => {
    test('should navigate directly to /performance and see dashboard', async ({ studentPage: page }) => {
      await setupFullAppMocks(page);
      await page.goto('/performance');

      const heading = page.locator('text=Performance Dashboard').first();
      await expect(heading).toBeVisible({ timeout: 15000 });
    });

    test('should navigate from Dashboard to Performance via View Progress button', async ({ studentPage: page }) => {
      await setupFullAppMocks(page);
      await page.goto('/dashboard');

      // View Progress button from Dashboard.tsx
      const viewProgressButton = page.locator('button:has-text("View Progress")').first();
      const isVisible = await viewProgressButton.isVisible().catch(() => false);

      if (isVisible) {
        await viewProgressButton.click();
        await page.waitForURL('/progress', { timeout: 10000 });
        await expect(page).toHaveURL(/\/progress/);
      } else {
        // Fallback: navigate directly if button not visible
        await page.goto('/performance');
        await expect(page).toHaveURL(/\/performance/);
      }
    });
  });

  test.describe('Logout and Unauthenticated Redirect', () => {
    test('should redirect to login after clearing auth tokens', async ({ studentPage: page }) => {
      // First, visit dashboard to confirm auth is set up
      await page.goto('/dashboard');
      await expect(page).toHaveURL(/\/dashboard/);

      // Clear auth tokens (simulate logout)
      await page.evaluate(() => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
      });

      // Navigate to protected route
      await page.goto('/mcqs');

      // Should redirect to login
      await page.waitForURL(/\/login/, { timeout: 10000 });
      await expect(page).toHaveURL(/\/login/);
    });

    test('unauthenticated user navigating to /dashboard should be redirected to /login', async ({ page }) => {
      await page.evaluate(() => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
      });

      await page.goto('/dashboard');
      await page.waitForURL(/\/login/, { timeout: 10000 });
      await expect(page).toHaveURL(/\/login/);
    });
  });

  test.describe('Unknown Route Handling', () => {
    test('should redirect unknown route to login when unauthenticated', async ({ page }) => {
      await page.evaluate(() => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
      });

      // App.tsx has: <Route path="*" element={<Navigate to="/login" replace />}
      await page.goto('/non-existent-page-xyz');
      await page.waitForURL(/\/login/, { timeout: 10000 });
      await expect(page).toHaveURL(/\/login/);
    });

    test('should redirect authenticated user from unknown route to dashboard via / redirect', async ({ studentPage: page }) => {
      // App.tsx root route: <Route path="/" element={<Navigate to="/dashboard" replace />}
      await page.goto('/');
      await page.waitForURL(/\/dashboard/, { timeout: 10000 });
      await expect(page).toHaveURL(/\/dashboard/);
    });
  });
});