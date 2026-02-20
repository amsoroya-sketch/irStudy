/**
 * Mobile Responsive E2E Tests (TASK_010)
 *
 * Tests the application at mobile viewport (390 x 844 - iPhone 12 dimensions).
 * Verifies Dashboard, MCQ Browser, navigation, touch targets, Login page, and no horizontal overflow.
 */

import { test, expect } from '../../fixtures/auth.fixture';
import { generateMCQListResponse } from '../../fixtures/mcqs.fixture';

const API_BASE_URL = 'http://localhost:8000/api/v1';
const MOBILE_VIEWPORT = { width: 390, height: 844 };

async function setupMCQApiMock(page: import('@playwright/test').Page) {
  await page.route(API_BASE_URL + '/mcqs**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(generateMCQListResponse(0, 20)),
    });
  });
}

async function setupDashboardApiMock(page: import('@playwright/test').Page) {
  await page.route(API_BASE_URL + '/progress/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_mcq_attempts: 10, mcq_accuracy_rate: 70.0, total_osce_completions: 5,
        study_cards_reviewed: 50, study_card_retention_rate: 80.0,
        weak_areas: [], specialty_breakdown: [],
      }),
    });
  });
  await page.route(API_BASE_URL + '/progress/weekly-trends**', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ trends: [] }) });
  });
}

test.describe('Mobile Responsive Design 390 x 844', () => {

  test.describe('Dashboard Page on Mobile', () => {
    test('should render Dashboard correctly on mobile viewport', async ({ studentPage: page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/dashboard');
      const welcomeText = page.locator('text=Welcome to AMC Clinical Exam Simulation');
      await expect(welcomeText).toBeVisible({ timeout: 10000 });
    });

    test('should not have horizontal overflow on Dashboard mobile', async ({ studentPage: page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/dashboard');
      await page.waitForTimeout(1000);
      const hasOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
      expect(hasOverflow).toBe(false);
    });

    test('should display Quick Actions cards on mobile', async ({ studentPage: page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/dashboard');
      const mcqCard = page.locator('text=MCQ Practice').first();
      await expect(mcqCard).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('MCQ Browser Page on Mobile', () => {
    test('should render MCQ Browser correctly on mobile viewport', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/mcqs');
      await expect(page.locator('h1')).toBeVisible({ timeout: 10000 });
      await expect(page.locator('h1')).toContainText(/MCQ Practice Browser/i);
    });

    test('should not have horizontal overflow on MCQ Browser mobile', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/mcqs');
      await page.waitForTimeout(1500);
      const hasOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
      expect(hasOverflow).toBe(false);
    });

    test('should display filter controls on mobile', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/mcqs');
      const searchField = page.locator('input[placeholder="Search questions..."]');
      await expect(searchField).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Mobile Bottom Navigation', () => {
    test('should render MobileBottomNav on mobile viewport', async ({ studentPage: page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/dashboard');
      const bottomNav = page.locator('[role="navigation"][aria-label="Bottom navigation"]');
      await expect(bottomNav).toBeVisible({ timeout: 10000 });
    });

    test('should display Home nav item in bottom navigation', async ({ studentPage: page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/dashboard');
      await expect(page.locator('[aria-label="Home"]').first()).toBeVisible({ timeout: 10000 });
    });

    test('should display Practice nav item in bottom navigation', async ({ studentPage: page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/dashboard');
      await expect(page.locator('[aria-label="Practice"]').first()).toBeVisible({ timeout: 10000 });
    });

    test('should display Progress nav item in bottom navigation', async ({ studentPage: page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/dashboard');
      await expect(page.locator('[aria-label="Progress"]').first()).toBeVisible({ timeout: 10000 });
    });

    test('should NOT render MobileBottomNav on desktop viewport', async ({ studentPage: page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.goto('/dashboard');
      const bottomNav = page.locator('[role="navigation"][aria-label="Bottom navigation"]');
      await expect(bottomNav).not.toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Touch Target Sizes', () => {
    test('nav buttons should have touch targets at least 44px tall', async ({ studentPage: page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/dashboard');
      const navActions = page.locator('.MuiBottomNavigationAction-root');
      const count = await navActions.count();
      if (count > 0) {
        const box = await navActions.first().boundingBox();
        if (box) {
          expect(box.height).toBeGreaterThanOrEqual(44);
        }
      }
    });

    test('submit button on login page should have touch target at least 44px', async ({ page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/login');
      const submitButton = page.locator('button[type="submit"]');
      const box = await submitButton.boundingBox();
      if (box) {
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    });
  });

  test.describe('Login Page on Mobile', () => {
    test('should render Login page correctly on mobile viewport', async ({ page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/login');
      await expect(page.locator('input[name="email"]').first()).toBeVisible({ timeout: 10000 });
      await expect(page.locator('input[name="password"]').first()).toBeVisible({ timeout: 10000 });
      await expect(page.locator('button[type="submit"]').first()).toBeVisible({ timeout: 10000 });
    });

    test('should not have horizontal overflow on Login page mobile', async ({ page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/login');
      await page.waitForTimeout(500);
      const hasOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
      expect(hasOverflow).toBe(false);
    });
  });

  test.describe('Responsive Container', () => {
    test('body should not exceed viewport width on mobile', async ({ studentPage: page }) => {
      await page.setViewportSize(MOBILE_VIEWPORT);
      await page.goto('/dashboard');
      await page.waitForTimeout(1000);
      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      expect(bodyWidth).toBeLessThanOrEqual(MOBILE_VIEWPORT.width + 1);
    });
  });
});