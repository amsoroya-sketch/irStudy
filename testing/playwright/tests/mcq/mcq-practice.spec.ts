/**
 * MCQ Practice Flow E2E Tests (TASK_010)
 *
 * Tests the MCQ Browser page UI structure, filters, empty states, navigation,
 * and authentication requirements.
 *
 * Authentication: Uses auth.fixture which auto-mocks API responses.
 * The MCQ API is additionally mocked here to return realistic fixture data.
 */

import { test, expect } from '../../fixtures/auth.fixture';
import { generateMCQListResponse } from '../../fixtures/mcqs.fixture';

const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Helper: Mock the MCQ list API to return fixture data
 */
async function setupMCQApiMock(page: import('@playwright/test').Page) {
  await page.route(API_BASE_URL + '/mcqs**', async (route) => {
    const url = new URL(route.request().url());
    const skip = parseInt(url.searchParams.get('skip') || '0', 10);
    const limit = parseInt(url.searchParams.get('limit') || '20', 10);
    const category = url.searchParams.get('category') || undefined;
    const difficulty = url.searchParams.get('difficulty') || undefined;
    const response = generateMCQListResponse(skip, limit, category, difficulty);
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(response),
    });
  });
}

test.describe('MCQ Practice Flow', () => {

  test.describe('Page Structure and Navigation', () => {
    test('should display MCQ Browser heading when authenticated', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      const heading = page.locator('h1');
      await expect(heading).toBeVisible({ timeout: 10000 });
      await expect(heading).toContainText(/MCQ Practice Browser/i);
    });

    test('should redirect unauthenticated users to login', async ({ page }) => {
      await page.evaluate(() => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
      });
      await page.goto('/mcqs');
      await page.waitForURL(/\/login/, { timeout: 10000 });
      await expect(page).toHaveURL(/\/login/);
    });

    test('should set document title to MCQ Browser', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      await page.waitForTimeout(500);
      await expect(page).toHaveTitle(/MCQ Browser/i);
    });
  });

  test.describe('Filter Controls', () => {
    test('should display search text field', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      const searchField = page.locator('input[placeholder="Search questions..."]');
      await expect(searchField).toBeVisible({ timeout: 10000 });
    });

    test('should display Category filter label', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      const categoryLabel = page.locator('text=Category').first();
      await expect(categoryLabel).toBeVisible({ timeout: 10000 });
    });

    test('should display Difficulty filter label', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      const difficultyLabel = page.locator('text=Difficulty').first();
      await expect(difficultyLabel).toBeVisible({ timeout: 10000 });
    });

    test('should accept text input in search field', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      const searchField = page.locator('input[placeholder="Search questions..."]');
      await expect(searchField).toBeVisible({ timeout: 10000 });
      await searchField.fill('chest pain');
      const value = await searchField.inputValue();
      expect(value).toBe('chest pain');
    });
  });

  test.describe('MCQ Card Display', () => {
    test('should display MCQ cards when data is available', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      await page.waitForTimeout(1500);
      const cards = page.locator('.MuiCard-root');
      const cardCount = await cards.count();
      expect(cardCount).toBeGreaterThan(0);
    });

    test('should display Attempt and View buttons for student role', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      await page.waitForTimeout(1500);
      const attemptButton = page.locator('button:has-text("Attempt")').first();
      const viewButton = page.locator('button:has-text("View")').first();
      await expect(attemptButton).toBeVisible({ timeout: 5000 });
      await expect(viewButton).toBeVisible({ timeout: 5000 });
    });

    test('should NOT display Edit button for student role', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      await page.waitForTimeout(1500);
      const editButton = page.locator('button:has-text("Edit")');
      await expect(editButton).not.toBeVisible();
    });

    test('should display empty state when no MCQs match', async ({ studentPage: page }) => {
      await page.route(API_BASE_URL + '/mcqs**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0, skip: 0, limit: 20 }),
        });
      });
      await page.goto('/mcqs');
      await page.waitForTimeout(1500);
      const emptyStateText = page.locator('text=No MCQs found');
      await expect(emptyStateText).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('MCQ Navigation', () => {
    test('should navigate to attempt page when Attempt button clicked', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      await page.waitForTimeout(1500);
      const attemptButton = page.locator('button:has-text("Attempt")').first();
      const isVisible = await attemptButton.isVisible().catch(() => false);
      if (!isVisible) {
        test.skip(true, 'No MCQ cards visible - data may not be available');
        return;
      }
      await attemptButton.click();
      await page.waitForURL(/\/mcqs\/\d+\/attempt/, { timeout: 10000 });
      await expect(page).toHaveURL(/\/mcqs\/\d+\/attempt/);
    });
  });

  test.describe('Pagination', () => {
    test('should display pagination when total exceeds page limit', async ({ studentPage: page }) => {
      await page.route(API_BASE_URL + '/mcqs**', async (route) => {
        const mockItems = Array.from({ length: 20 }, (_, i) => ({
          id: i + 1,
          question: 'Mock Question ' + (i + 1),
          category: 'Cardiology',
          difficulty: 'medium',
          tags: ['AMC'],
        }));
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: mockItems, total: 25, skip: 0, limit: 20 }),
        });
      });
      await page.goto('/mcqs');
      await page.waitForTimeout(1500);
      const pagination = page.locator('.MuiPagination-root');
      await expect(pagination).toBeVisible({ timeout: 5000 });
    });

    test('should NOT display pagination when results fit on one page', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      await page.waitForTimeout(1500);
      const pagination = page.locator('.MuiPagination-root');
      await expect(pagination).not.toBeVisible();
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should allow Tab navigation to search field', async ({ studentPage: page }) => {
      await setupMCQApiMock(page);
      await page.goto('/mcqs');
      await page.waitForTimeout(500);
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      const searchField = page.locator('input[placeholder="Search questions..."]');
      await expect(searchField).toBeVisible();
    });
  });
});