/**
 * Performance Dashboard E2E Tests (TASK_010)
 *
 * Tests PerformanceDashboard page: authentication, stat cards, gauge, charts, load time, mobile.
 * API endpoints are mocked to ensure reliable testing without live backend.
 */

import { test, expect } from '../../fixtures/auth.fixture';

const API_BASE_URL = 'http://localhost:8000/api/v1';

async function setupDashboardApiMock(page: import('@playwright/test').Page) {
  await page.route(API_BASE_URL + '/progress/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_mcq_attempts: 42,
        mcq_accuracy_rate: 78.5,
        total_osce_completions: 15,
        study_cards_reviewed: 120,
        study_card_retention_rate: 85.0,
        weak_areas: ['Cardiology', 'Psychiatry'],
        specialty_breakdown: [
          { specialty: 'Cardiology', attempts: 20, accuracy: 65.0 },
          { specialty: 'Respiratory', attempts: 15, accuracy: 86.7 },
        ],
      }),
    });
  });

  await page.route(API_BASE_URL + '/progress/weekly-trends**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        trends: [
          { week: '2026-W01', attempts: 10, accuracy: 70.0 },
          { week: '2026-W02', attempts: 15, accuracy: 80.0 },
          { week: '2026-W03', attempts: 12, accuracy: 75.0 },
          { week: '2026-W04', attempts: 20, accuracy: 85.0 },
        ],
      }),
    });
  });
}

test.describe('Performance Dashboard', () => {

  test.describe('Authentication and Access Control', () => {
    test('should redirect unauthenticated users to login', async ({ page }) => {
      await page.evaluate(() => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
      });
      await page.goto('/performance');
      await page.waitForURL(/\/login/, { timeout: 10000 });
      await expect(page).toHaveURL(/\/login/);
    });

    test('should allow authenticated student to access performance dashboard', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.goto('/performance');
      await page.waitForTimeout(500);
      await expect(page).not.toHaveURL(/\/login/);
    });
  });

  test.describe('Page Structure', () => {
    test('should display Performance Dashboard heading', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.goto('/performance');
      const heading = page.locator('text=Performance Dashboard').first();
      await expect(heading).toBeVisible({ timeout: 15000 });
    });

    test('should set document title to Performance Dashboard', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.goto('/performance');
      await page.waitForTimeout(1000);
      await expect(page).toHaveTitle(/Performance Dashboard/i);
    });
  });

  test.describe('Stat Cards Section', () => {
    test('should display MCQ Attempts stat card', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.goto('/performance');
      await expect(page.locator('text=MCQ Attempts').first()).toBeVisible({ timeout: 15000 });
    });

    test('should display OSCE Completions stat card', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.goto('/performance');
      await expect(page.locator('text=OSCE Completions').first()).toBeVisible({ timeout: 15000 });
    });

    test('should display Study Cards stat card', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.goto('/performance');
      await expect(page.locator('text=Study Cards').first()).toBeVisible({ timeout: 15000 });
    });

    test('should display Weak Areas stat card', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.goto('/performance');
      await expect(page.locator('text=Weak Areas').first()).toBeVisible({ timeout: 15000 });
    });
  });

  test.describe('Exam Readiness and Chart Sections', () => {
    test('should render content past loading state', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.goto('/performance');
      await expect(page.locator('[aria-label="Loading dashboard data"]').first()).not.toBeVisible({ timeout: 15000 });
      await expect(page.locator('.MuiContainer-root').first()).toBeVisible();
    });

    test('should render MUI Paper containers after data loads', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.goto('/performance');
      await page.waitForTimeout(2000);
      const count = await page.locator('.MuiPaper-root').count();
      expect(count).toBeGreaterThan(0);
    });
  });

  test.describe('Loading and Error States', () => {
    test('should show loading spinner while fetching data', async ({ studentPage: page }) => {
      await page.route(API_BASE_URL + '/progress/me', async (route) => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            total_mcq_attempts: 0, mcq_accuracy_rate: 0, total_osce_completions: 0,
            study_cards_reviewed: 0, study_card_retention_rate: 0,
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
      const navPromise = page.goto('/performance');
      await expect(page.locator('[aria-label="Loading dashboard data"]').first()).toBeVisible({ timeout: 5000 });
      await navPromise;
    });

    test('should remain on performance URL even with API error', async ({ studentPage: page }) => {
      await page.route(API_BASE_URL + '/progress/me', async (route) => {
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Internal server error' }) });
      });
      await page.route(API_BASE_URL + '/progress/weekly-trends**', async (route) => {
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Internal server error' }) });
      });
      await page.goto('/performance');
      await page.waitForTimeout(3000);
      await expect(page).toHaveURL(/\/performance/);
    });
  });

  test.describe('Performance Page Load Time', () => {
    test('should load and render within 5 seconds', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      const startTime = Date.now();
      await page.goto('/performance');
      await expect(page.locator('text=Performance Dashboard').first()).toBeVisible({ timeout: 10000 });
      expect(Date.now() - startTime).toBeLessThan(5000);
    });
  });

  test.describe('Mobile Responsive Layout', () => {
    test('should render heading at mobile viewport 375px wide', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.setViewportSize({ width: 375, height: 812 });
      await page.goto('/performance');
      await expect(page.locator('text=Performance Dashboard').first()).toBeVisible({ timeout: 15000 });
    });

    test('should not have horizontal overflow on mobile 375px', async ({ studentPage: page }) => {
      await setupDashboardApiMock(page);
      await page.setViewportSize({ width: 375, height: 812 });
      await page.goto('/performance');
      await page.waitForTimeout(2000);
      const hasOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      expect(hasOverflow).toBe(false);
    });
  });
});
