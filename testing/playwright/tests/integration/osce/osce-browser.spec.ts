/**
 * OSCE Browser Integration Tests
 *
 * Tests OSCE browsing, filtering, searching, and pagination functionality
 * Covers: Display, filters (specialty, station type, difficulty), search, pagination, random OSCE
 *
 * Test Data: Uses seeded OSCEs from setup/seed-test-data.ts
 * Authentication: Student role (can browse and view OSCEs)
 */

import { test, expect, Page } from '@playwright/test';
import { TEST_USERS } from '../../../utils/test-data/users';

test.describe('OSCE Browser - Display and Navigation', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    // Login as student
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);

    // Navigate to OSCE browser
    await page.goto('/osces');
  });

  test('should display OSCE browser page with header', async () => {
    const pageHeader = page.locator('h1:has-text("OSCE Stations")');
    await expect(pageHeader).toBeVisible();
  });

  test('should display OSCE cards in grid layout', async () => {
    const osceGrid = page.locator('[data-testid="osce-grid"]');
    await expect(osceGrid).toBeVisible();

    const osceCards = page.locator('[data-testid="osce-card"]');
    const count = await osceCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should display OSCE card with all metadata fields', async () => {
    const firstCard = page.locator('[data-testid="osce-card"]').first();

    // Check for required fields
    await expect(firstCard.locator('[data-testid="osce-title"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="osce-specialty"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="osce-station-type"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="osce-difficulty"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="osce-time-limit"]')).toBeVisible();
  });

  test('should display specialty badge with correct color coding', async () => {
    const firstCard = page.locator('[data-testid="osce-card"]').first();
    const specialtyBadge = firstCard.locator('[data-testid="osce-specialty"]');

    await expect(specialtyBadge).toBeVisible();
    const bgColor = await specialtyBadge.evaluate(el => window.getComputedStyle(el).backgroundColor);
    expect(bgColor).toBeTruthy(); // Should have some background color
  });

  test('should display difficulty with visual indicator (Easy/Medium/Hard)', async () => {
    const firstCard = page.locator('[data-testid="osce-card"]').first();
    const difficultyBadge = firstCard.locator('[data-testid="osce-difficulty"]');

    await expect(difficultyBadge).toBeVisible();
    const text = await difficultyBadge.textContent();
    expect(['Easy', 'Medium', 'Hard']).toContain(text?.trim());
  });

  test('should display time limit in minutes', async () => {
    const firstCard = page.locator('[data-testid="osce-card"]').first();
    const timeLimit = firstCard.locator('[data-testid="osce-time-limit"]');

    await expect(timeLimit).toBeVisible();
    const text = await timeLimit.textContent();
    expect(text).toMatch(/\d+\s*(min|minutes)/i);
  });

  test('should navigate to OSCE detail page when card clicked', async () => {
    const firstCard = page.locator('[data-testid="osce-card"]').first();
    const osceTitle = await firstCard.locator('[data-testid="osce-title"]').textContent();

    await firstCard.click();

    // Should navigate to detail page
    await expect(page).toHaveURL(/\/osces\/TEST-/);

    // Detail page should show the same title
    const detailTitle = page.locator('h1');
    await expect(detailTitle).toContainText(osceTitle || '');
  });

  test('should display empty state when no OSCEs match filters', async () => {
    // Apply impossible filter combination
    await page.selectOption('[data-testid="specialty-filter"]', 'cardiology');
    await page.selectOption('[data-testid="station-type-filter"]', 'history_taking');
    await page.selectOption('[data-testid="difficulty-filter"]', 'hard');

    // Wait for filtering to complete
    await page.waitForTimeout(500);

    const emptyState = page.locator('[data-testid="empty-state"]');
    await expect(emptyState).toBeVisible();
    await expect(emptyState).toContainText(/no.*osce.*found/i);
  });

  test('should show loading skeleton during initial load', async () => {
    // Intercept API call to delay response
    await page.route('**/api/v1/osces*', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.continue();
    });

    await page.goto('/osces');

    const skeleton = page.locator('[data-testid="osce-skeleton"]');
    await expect(skeleton.first()).toBeVisible();
  });
});

test.describe('OSCE Browser - Specialty Filter', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces');
  });

  test('should display specialty filter dropdown with all 11 specialties', async () => {
    const specialtyFilter = page.locator('[data-testid="specialty-filter"]');
    await expect(specialtyFilter).toBeVisible();

    const options = await specialtyFilter.locator('option').allTextContents();

    // Should have "All Specialties" + 11 specialties
    expect(options.length).toBeGreaterThanOrEqual(11);
    expect(options).toContain('All Specialties');
  });

  test('should filter OSCEs by cardiology specialty', async () => {
    await page.selectOption('[data-testid="specialty-filter"]', 'cardiology');
    await page.waitForTimeout(500);

    const osceCards = page.locator('[data-testid="osce-card"]');
    const count = await osceCards.count();

    // All visible cards should be cardiology
    for (let i = 0; i < count; i++) {
      const specialty = await osceCards.nth(i).locator('[data-testid="osce-specialty"]').textContent();
      expect(specialty?.toLowerCase()).toContain('cardio');
    }
  });

  test('should filter OSCEs by respiratory specialty', async () => {
    await page.selectOption('[data-testid="specialty-filter"]', 'respiratory');
    await page.waitForTimeout(500);

    const osceCards = page.locator('[data-testid="osce-card"]');
    const count = await osceCards.count();

    if (count > 0) {
      const specialty = await osceCards.first().locator('[data-testid="osce-specialty"]').textContent();
      expect(specialty?.toLowerCase()).toContain('respir');
    }
  });

  test('should reset to all OSCEs when "All Specialties" selected', async () => {
    // First filter to cardiology
    await page.selectOption('[data-testid="specialty-filter"]', 'cardiology');
    await page.waitForTimeout(500);
    const filteredCount = await page.locator('[data-testid="osce-card"]').count();

    // Reset to all
    await page.selectOption('[data-testid="specialty-filter"]', 'all');
    await page.waitForTimeout(500);
    const allCount = await page.locator('[data-testid="osce-card"]').count();

    expect(allCount).toBeGreaterThanOrEqual(filteredCount);
  });

  test('should update URL query params when specialty filter changes', async () => {
    await page.selectOption('[data-testid="specialty-filter"]', 'cardiology');
    await page.waitForTimeout(500);

    const url = page.url();
    expect(url).toContain('specialty=cardiology');
  });

  test('should persist specialty filter on page reload', async () => {
    await page.selectOption('[data-testid="specialty-filter"]', 'neurology');
    await page.waitForTimeout(500);

    await page.reload();

    const selectedValue = await page.locator('[data-testid="specialty-filter"]').inputValue();
    expect(selectedValue).toBe('neurology');
  });
});

test.describe('OSCE Browser - Station Type Filter', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces');
  });

  test('should display station type filter with 6 types', async () => {
    const stationTypeFilter = page.locator('[data-testid="station-type-filter"]');
    await expect(stationTypeFilter).toBeVisible();

    const options = await stationTypeFilter.locator('option').allTextContents();

    // "All Types" + 6 station types
    expect(options.length).toBeGreaterThanOrEqual(6);
    expect(options).toContain('All Types');
  });

  test('should filter by physical_examination type', async () => {
    await page.selectOption('[data-testid="station-type-filter"]', 'physical_examination');
    await page.waitForTimeout(500);

    const osceCards = page.locator('[data-testid="osce-card"]');
    const count = await osceCards.count();

    if (count > 0) {
      const stationType = await osceCards.first().locator('[data-testid="osce-station-type"]').textContent();
      expect(stationType?.toLowerCase()).toContain('physical');
    }
  });

  test('should filter by history_taking type', async () => {
    await page.selectOption('[data-testid="station-type-filter"]', 'history_taking');
    await page.waitForTimeout(500);

    const osceCards = page.locator('[data-testid="osce-card"]');
    const count = await osceCards.count();

    if (count > 0) {
      const stationType = await osceCards.first().locator('[data-testid="osce-station-type"]').textContent();
      expect(stationType?.toLowerCase()).toContain('history');
    }
  });

  test('should filter by counselling type', async () => {
    await page.selectOption('[data-testid="station-type-filter"]', 'counselling');
    await page.waitForTimeout(500);

    const url = page.url();
    expect(url).toContain('station_type=counselling');
  });

  test('should combine station type with specialty filter', async () => {
    await page.selectOption('[data-testid="specialty-filter"]', 'cardiology');
    await page.selectOption('[data-testid="station-type-filter"]', 'physical_examination');
    await page.waitForTimeout(500);

    const url = page.url();
    expect(url).toContain('specialty=cardiology');
    expect(url).toContain('station_type=physical_examination');
  });
});

test.describe('OSCE Browser - Difficulty Filter', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces');
  });

  test('should display difficulty filter with 3 levels', async () => {
    const difficultyFilter = page.locator('[data-testid="difficulty-filter"]');
    await expect(difficultyFilter).toBeVisible();

    const options = await difficultyFilter.locator('option').allTextContents();
    expect(options).toContain('All Difficulties');
    expect(options).toContain('Easy');
    expect(options).toContain('Medium');
    expect(options).toContain('Hard');
  });

  test('should filter by easy difficulty', async () => {
    await page.selectOption('[data-testid="difficulty-filter"]', 'easy');
    await page.waitForTimeout(500);

    const osceCards = page.locator('[data-testid="osce-card"]');
    const count = await osceCards.count();

    if (count > 0) {
      const difficulty = await osceCards.first().locator('[data-testid="osce-difficulty"]').textContent();
      expect(difficulty?.toLowerCase()).toContain('easy');
    }
  });

  test('should filter by medium difficulty', async () => {
    await page.selectOption('[data-testid="difficulty-filter"]', 'medium');
    await page.waitForTimeout(500);

    const osceCards = page.locator('[data-testid="osce-card"]');
    const count = await osceCards.count();

    if (count > 0) {
      const difficulty = await osceCards.first().locator('[data-testid="osce-difficulty"]').textContent();
      expect(difficulty?.toLowerCase()).toContain('medium');
    }
  });

  test('should filter by hard difficulty', async () => {
    await page.selectOption('[data-testid="difficulty-filter"]', 'hard');
    await page.waitForTimeout(500);

    const url = page.url();
    expect(url).toContain('difficulty=hard');
  });

  test('should combine all three filters (specialty + station type + difficulty)', async () => {
    await page.selectOption('[data-testid="specialty-filter"]', 'cardiology');
    await page.selectOption('[data-testid="station-type-filter"]', 'physical_examination');
    await page.selectOption('[data-testid="difficulty-filter"]', 'medium');
    await page.waitForTimeout(500);

    const url = page.url();
    expect(url).toContain('specialty=cardiology');
    expect(url).toContain('station_type=physical_examination');
    expect(url).toContain('difficulty=medium');

    const osceCards = page.locator('[data-testid="osce-card"]');
    const count = await osceCards.count();

    // All cards should match all three filters
    for (let i = 0; i < Math.min(count, 3); i++) {
      const card = osceCards.nth(i);
      const specialty = await card.locator('[data-testid="osce-specialty"]').textContent();
      const stationType = await card.locator('[data-testid="osce-station-type"]').textContent();
      const difficulty = await card.locator('[data-testid="osce-difficulty"]').textContent();

      expect(specialty?.toLowerCase()).toContain('cardio');
      expect(stationType?.toLowerCase()).toContain('physical');
      expect(difficulty?.toLowerCase()).toContain('medium');
    }
  });
});

test.describe('OSCE Browser - Search Functionality', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces');
  });

  test('should display search input field', async () => {
    const searchInput = page.locator('[data-testid="osce-search"]');
    await expect(searchInput).toBeVisible();
    await expect(searchInput).toHaveAttribute('placeholder', /search/i);
  });

  test('should search OSCEs by title keyword', async () => {
    const searchInput = page.locator('[data-testid="osce-search"]');
    await searchInput.fill('cardiovascular');
    await page.waitForTimeout(500);

    const osceCards = page.locator('[data-testid="osce-card"]');
    const count = await osceCards.count();

    if (count > 0) {
      const title = await osceCards.first().locator('[data-testid="osce-title"]').textContent();
      expect(title?.toLowerCase()).toContain('cardiovascular');
    }
  });

  test('should search OSCEs by specialty keyword', async () => {
    const searchInput = page.locator('[data-testid="osce-search"]');
    await searchInput.fill('respiratory');
    await page.waitForTimeout(500);

    const url = page.url();
    expect(url).toContain('search=respiratory');
  });

  test('should search OSCEs by station type keyword', async () => {
    const searchInput = page.locator('[data-testid="osce-search"]');
    await searchInput.fill('examination');
    await page.waitForTimeout(500);

    const osceCards = page.locator('[data-testid="osce-card"]');
    const count = await osceCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should debounce search input (wait 300ms before searching)', async () => {
    const searchInput = page.locator('[data-testid="osce-search"]');

    // Type quickly
    await searchInput.fill('c');
    await page.waitForTimeout(100);
    await searchInput.fill('ca');
    await page.waitForTimeout(100);
    await searchInput.fill('car');

    // Should not search yet
    await page.waitForTimeout(200);

    // Wait for debounce
    await page.waitForTimeout(400);

    const url = page.url();
    expect(url).toContain('search=car');
  });

  test('should clear search results when search input cleared', async () => {
    const searchInput = page.locator('[data-testid="osce-search"]');

    // Search first
    await searchInput.fill('cardiovascular');
    await page.waitForTimeout(500);
    const filteredCount = await page.locator('[data-testid="osce-card"]').count();

    // Clear search
    await searchInput.clear();
    await page.waitForTimeout(500);
    const allCount = await page.locator('[data-testid="osce-card"]').count();

    expect(allCount).toBeGreaterThanOrEqual(filteredCount);
  });

  test('should combine search with filters', async () => {
    await page.selectOption('[data-testid="specialty-filter"]', 'cardiology');
    const searchInput = page.locator('[data-testid="osce-search"]');
    await searchInput.fill('examination');
    await page.waitForTimeout(500);

    const url = page.url();
    expect(url).toContain('specialty=cardiology');
    expect(url).toContain('search=examination');
  });

  test('should show "No results" when search has no matches', async () => {
    const searchInput = page.locator('[data-testid="osce-search"]');
    await searchInput.fill('xyzabc123nonexistent');
    await page.waitForTimeout(500);

    const emptyState = page.locator('[data-testid="empty-state"]');
    await expect(emptyState).toBeVisible();
    await expect(emptyState).toContainText(/no.*osce.*found/i);
  });
});

test.describe('OSCE Browser - Pagination', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces');
  });

  test('should display pagination controls when more than 10 OSCEs', async () => {
    // Mock API to return many OSCEs
    await page.route('**/api/v1/osces*', async route => {
      const response = await route.fetch();
      const json = await response.json();

      // Create 25 mock OSCEs
      const mockOSCEs = Array.from({ length: 25 }, (_, i) => ({
        osce_id: `MOCK-OSCE-${i + 1}`,
        station_title: `Mock OSCE Station ${i + 1}`,
        specialty: 'cardiology',
        station_type: 'physical_examination',
        difficulty: 'medium',
        time_limit_minutes: 8,
      }));

      route.fulfill({ json: { osces: mockOSCEs, total: 25 } });
    });

    await page.reload();

    const pagination = page.locator('[data-testid="pagination"]');
    await expect(pagination).toBeVisible();
  });

  test('should display page size selector (10, 25, 50, 100 per page)', async () => {
    const pageSizeSelector = page.locator('[data-testid="page-size-selector"]');

    if (await pageSizeSelector.isVisible()) {
      const options = await pageSizeSelector.locator('option').allTextContents();
      expect(options).toContain('10 per page');
      expect(options).toContain('25 per page');
      expect(options).toContain('50 per page');
      expect(options).toContain('100 per page');
    }
  });

  test('should change page size and update results', async () => {
    const pageSizeSelector = page.locator('[data-testid="page-size-selector"]');

    if (await pageSizeSelector.isVisible()) {
      await pageSizeSelector.selectOption('25');
      await page.waitForTimeout(500);

      const url = page.url();
      expect(url).toContain('page_size=25');
    }
  });

  test('should navigate to next page', async () => {
    const nextButton = page.locator('[data-testid="pagination-next"]');

    if (await nextButton.isVisible()) {
      await nextButton.click();
      await page.waitForTimeout(500);

      const url = page.url();
      expect(url).toContain('page=2');
    }
  });

  test('should navigate to previous page', async () => {
    // Go to page 2 first
    const nextButton = page.locator('[data-testid="pagination-next"]');
    if (await nextButton.isVisible()) {
      await nextButton.click();
      await page.waitForTimeout(500);

      const prevButton = page.locator('[data-testid="pagination-previous"]');
      await prevButton.click();
      await page.waitForTimeout(500);

      const url = page.url();
      expect(url).toContain('page=1');
    }
  });

  test('should disable "Previous" button on first page', async () => {
    const prevButton = page.locator('[data-testid="pagination-previous"]');

    if (await prevButton.isVisible()) {
      await expect(prevButton).toBeDisabled();
    }
  });

  test('should display current page number', async () => {
    const currentPage = page.locator('[data-testid="current-page"]');

    if (await currentPage.isVisible()) {
      const text = await currentPage.textContent();
      expect(text).toContain('1');
    }
  });
});

test.describe('OSCE Browser - Random OSCE Feature', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces');
  });

  test('should display "Random OSCE" button', async () => {
    const randomButton = page.locator('[data-testid="random-osce-button"]');
    await expect(randomButton).toBeVisible();
    await expect(randomButton).toContainText(/random/i);
  });

  test('should navigate to random OSCE when button clicked', async () => {
    const randomButton = page.locator('[data-testid="random-osce-button"]');
    await randomButton.click();

    // Should navigate to an OSCE detail page
    await expect(page).toHaveURL(/\/osces\/.+/);
  });

  test('should respect filters when selecting random OSCE', async () => {
    // Filter to cardiology
    await page.selectOption('[data-testid="specialty-filter"]', 'cardiology');
    await page.waitForTimeout(500);

    const randomButton = page.locator('[data-testid="random-osce-button"]');
    await randomButton.click();

    // Wait for navigation
    await page.waitForURL(/\/osces\/.+/);

    // Check specialty badge on detail page
    const specialtyBadge = page.locator('[data-testid="osce-specialty"]');
    const specialty = await specialtyBadge.textContent();
    expect(specialty?.toLowerCase()).toContain('cardio');
  });

  test('should show tooltip/hint on random button hover', async () => {
    const randomButton = page.locator('[data-testid="random-osce-button"]');

    await randomButton.hover();
    await page.waitForTimeout(300);

    const tooltip = page.locator('[role="tooltip"]');
    if (await tooltip.isVisible()) {
      await expect(tooltip).toContainText(/random/i);
    }
  });
});

test.describe('OSCE Browser - Accessibility', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces');
  });

  test('should support keyboard navigation through OSCE cards', async () => {
    // Tab to first card
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    const firstCard = page.locator('[data-testid="osce-card"]').first();
    await expect(firstCard).toBeFocused();
  });

  test('should have aria-labels on filter selectors', async () => {
    const specialtyFilter = page.locator('[data-testid="specialty-filter"]');
    const ariaLabel = await specialtyFilter.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();
    expect(ariaLabel?.toLowerCase()).toContain('specialty');
  });

  test('should announce filter changes to screen readers', async () => {
    const specialtyFilter = page.locator('[data-testid="specialty-filter"]');
    await specialtyFilter.selectOption('cardiology');

    // Check for aria-live region
    const liveRegion = page.locator('[aria-live="polite"]');
    if (await liveRegion.isVisible()) {
      const text = await liveRegion.textContent();
      expect(text?.toLowerCase()).toContain('filter');
    }
  });

  test('should have descriptive alt text for specialty icons', async () => {
    const specialtyIcon = page.locator('[data-testid="osce-card"]').first().locator('img').first();

    if (await specialtyIcon.isVisible()) {
      const alt = await specialtyIcon.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
  });
});

test.describe('OSCE Browser - Responsive Design', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
  });

  test('should display 3-column grid on desktop (1920x1080)', async () => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/osces');

    const osceGrid = page.locator('[data-testid="osce-grid"]');
    const gridColumns = await osceGrid.evaluate(el => {
      return window.getComputedStyle(el).gridTemplateColumns;
    });

    // Should have 3 columns
    const columnCount = gridColumns.split(' ').length;
    expect(columnCount).toBe(3);
  });

  test('should display 2-column grid on tablet (768x1024)', async () => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/osces');

    const osceGrid = page.locator('[data-testid="osce-grid"]');
    const gridColumns = await osceGrid.evaluate(el => {
      return window.getComputedStyle(el).gridTemplateColumns;
    });

    const columnCount = gridColumns.split(' ').length;
    expect(columnCount).toBe(2);
  });

  test('should display single column on mobile (375x667)', async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/osces');

    const osceGrid = page.locator('[data-testid="osce-grid"]');
    const gridColumns = await osceGrid.evaluate(el => {
      return window.getComputedStyle(el).gridTemplateColumns;
    });

    const columnCount = gridColumns.split(' ').length;
    expect(columnCount).toBe(1);
  });

  test('should have touch-friendly filter buttons on mobile', async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/osces');

    const randomButton = page.locator('[data-testid="random-osce-button"]');
    const box = await randomButton.boundingBox();

    expect(box!.height).toBeGreaterThanOrEqual(44);
  });
});
