/**
 * HTML OSCE Notes Browser Integration Tests
 *
 * Tests HTML notes browsing, filtering, search, and content viewer
 * Authentication: Uses auth.fixture with API mocking
 */

import { test, expect } from '../../fixtures/auth.fixture';

const MOCK_NOTES = [
  {
    note_id: 'HTML-MED-001',
    title: 'Emergency OSCE Notes - Anaphylaxis Management',
    specialty: 'Medicine',
    category: 'Emergency',
    file_size_kb: 16,
    estimated_reading_minutes: 6,
    topics: ['Anaphylaxis', 'Emergency Management', 'ABCDE Approach'],
    preview_text: 'Emergency OSCE Notes - Anaphylaxis Management...',
  },
  {
    note_id: 'HTML-MED-002',
    title: 'History Taking - Chest Pain',
    specialty: 'Medicine',
    category: 'History',
    file_size_kb: 12,
    estimated_reading_minutes: 5,
    topics: ['Chest Pain', 'History Taking', 'Cardiology'],
    preview_text: 'Comprehensive guide to history taking for chest pain presentations...',
  },
  {
    note_id: 'HTML-SURG-001',
    title: 'Pre-operative Assessment',
    specialty: 'Surgery',
    category: 'Physical Examination',
    file_size_kb: 14,
    estimated_reading_minutes: 7,
    topics: ['Pre-op', 'Assessment', 'Surgery'],
    preview_text: 'Pre-operative assessment checklist and common pitfalls...',
  },
  {
    note_id: 'HTML-PSY-001',
    title: 'Mental State Examination',
    specialty: 'Psychiatry',
    category: 'Examination',
    file_size_kb: 18,
    estimated_reading_minutes: 8,
    topics: ['MSE', 'Psychiatry', 'Examination'],
    preview_text: 'Structured approach to the mental state examination...',
  },
];

const MOCK_SPECIALTIES = [
  { specialty: 'Medicine', count: 18 },
  { specialty: 'Mock OSCE Stations', count: 19 },
  { specialty: 'Ethics & Communication', count: 6 },
  { specialty: 'Surgery', count: 5 },
  { specialty: 'Psychiatry', count: 5 },
  { specialty: 'Paediatrics', count: 5 },
  { specialty: 'Obstetrics & Gynecology', count: 5 },
];

/**
 * Mock HTML Notes API responses
 */
async function setupHTMLNotesApiMock(page: import('@playwright/test').Page) {
  await page.route('**/api/v1/html-notes/**', async (route, request) => {
    const url = request.url();

    // Specialties list endpoint
    if (url.includes('/specialties/list')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_SPECIALTIES),
      });
      return;
    }

    // Content endpoint
    if (url.includes('/content')) {
      const noteId = url.split('/html-notes/')[1]?.split('/')[0] || 'unknown';
      await route.fulfill({
        status: 200,
        contentType: 'text/html',
        body: `<html><head><title>Note ${noteId}</title></head><body><h1>Emergency OSCE Notes</h1><p>Test content for ${noteId}</p></body></html>`,
      });
      return;
    }

    // Single note metadata
    const singleNoteMatch = url.match(/\/html-notes\/([^/?]+)$/);
    if (singleNoteMatch) {
      const noteId = singleNoteMatch[1];
      const note = MOCK_NOTES.find(n => n.note_id === noteId) || MOCK_NOTES[0];
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(note),
      });
      return;
    }

    // Default: list notes
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_NOTES),
    });
  });
}

test.describe('HTML OSCE Notes Browser', () => {

  test('should display HTML Notes heading when authenticated', async ({ studentPage: page }) => {
    await setupHTMLNotesApiMock(page);
    await page.goto('/html-notes');
    await page.waitForTimeout(2000);
    const heading = page.locator('h1');
    await expect(heading).toBeVisible({ timeout: 10000 });
    await expect(heading).toContainText(/HTML OSCE Notes/i);
  });

  test('should redirect unauthenticated users to login', async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    });
    await page.goto('/html-notes');
    await page.waitForTimeout(2000);
    await expect(page).toHaveURL(/\/login/);
  });

  test('should display note cards when data is available', async ({ studentPage: page }) => {
    await setupHTMLNotesApiMock(page);
    await page.goto('/html-notes');
    await page.waitForTimeout(2000);
    const cards = page.locator('.MuiCard-root');
    await expect(cards.first()).toBeVisible({ timeout: 5000 });
    const cardCount = await cards.count();
    expect(cardCount).toBeGreaterThan(0);
  });

  test('should display search and filter controls', async ({ studentPage: page }) => {
    await setupHTMLNotesApiMock(page);
    await page.goto('/html-notes');
    await page.waitForTimeout(2000);
    await expect(page.locator('input[placeholder*="Search by title"]')).toBeVisible();
    await expect(page.locator('text=Specialty').first()).toBeVisible();
    await expect(page.locator('text=Category').first()).toBeVisible();
  });

  test('should open viewer dialog when card clicked', async ({ studentPage: page }) => {
    await setupHTMLNotesApiMock(page);
    await page.goto('/html-notes');
    await page.waitForTimeout(2000);
    const firstCard = page.locator('.MuiCard-root').first();
    await firstCard.click();
    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible({ timeout: 5000 });
    await expect(dialog.locator('iframe')).toBeVisible();
  });

  test('should close viewer dialog when close button clicked', async ({ studentPage: page }) => {
    await setupHTMLNotesApiMock(page);
    await page.goto('/html-notes');
    await page.waitForTimeout(2000);
    const firstCard = page.locator('.MuiCard-root').first();
    await firstCard.click();
    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible({ timeout: 5000 });
    const closeButton = dialog.locator('button[aria-label="Close viewer"]');
    await closeButton.click();
    await expect(dialog).not.toBeVisible({ timeout: 5000 });
  });

  test('should show HTML Notes in dashboard ModuleStatsGrid', async ({ studentPage: page }) => {
    await setupHTMLNotesApiMock(page);
    await page.goto('/dashboard');
    await page.waitForTimeout(2000);
    const htmlNotesCard = page.locator('.MuiCard-root:has-text("HTML OSCE Notes")');
    await expect(htmlNotesCard).toBeVisible({ timeout: 5000 });
  });

  test('should show HTML Notes in MobileBottomNav on mobile', async ({ studentPage: page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await setupHTMLNotesApiMock(page);
    await page.goto('/html-notes');
    await page.waitForTimeout(1000);
    const nav = page.locator('[role="navigation"][aria-label*="bottom" i]');
    await expect(nav).toBeVisible({ timeout: 5000 });
    await expect(nav.locator('text=Notes')).toBeVisible();
  });

  test('should display empty state when no notes match search', async ({ studentPage: page }) => {
    await page.route('**/api/v1/html-notes/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) });
    });
    await page.goto('/html-notes');
    await page.waitForTimeout(2000);
    await expect(page.locator('text=No notes found')).toBeVisible({ timeout: 5000 });
  });
});
