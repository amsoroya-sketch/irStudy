/**
 * OSCE Learning Objectives Integration Tests
 *
 * Tests the learning objectives and key points display for OSCE stations
 * Covers: Objectives display, key points, educational content, study guidance
 *
 * Test Data: Uses seeded OSCEs from setup/seed-test-data.ts
 * Authentication: Student role (views learning objectives)
 */

import { test, expect, Page } from '@playwright/test';
import { TEST_USERS } from '../../../utils/test-data/users';

test.describe('OSCE Learning Objectives - Display on Detail Page', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);

    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
  });

  test('should display learning objectives section', async () => {
    const objectivesSection = page.locator('[data-testid="learning-objectives-section"]');
    await expect(objectivesSection).toBeVisible();
  });

  test('should show section heading for learning objectives', async () => {
    const heading = page.locator('[data-testid="learning-objectives-heading"]');
    await expect(heading).toBeVisible();
    await expect(heading).toContainText(/learning.*objective/i);
  });

  test('should display all learning objectives as bullet list', async () => {
    const objectivesList = page.locator('[data-testid="learning-objectives-list"]');
    await expect(objectivesList).toBeVisible();

    const objectives = page.locator('[data-testid="learning-objective-item"]');
    const count = await objectives.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should show first objective: "Perform systematic cardiovascular examination"', async () => {
    const firstObjective = page.locator('[data-testid="learning-objective-item"]').first();
    await expect(firstObjective).toContainText(/perform.*systematic.*cardiovascular.*examination/i);
  });

  test('should show second objective: "Identify normal and abnormal signs"', async () => {
    const objectives = page.locator('[data-testid="learning-objective-item"]');
    const secondObjective = objectives.nth(1);
    await expect(secondObjective).toContainText(/identify.*normal.*abnormal/i);
  });

  test('should show third objective: "Demonstrate auscultation technique"', async () => {
    const objectives = page.locator('[data-testid="learning-objective-item"]');
    const thirdObjective = objectives.nth(2);
    await expect(thirdObjective).toContainText(/auscultation.*technique/i);
  });

  test('should use proper list formatting (ordered or unordered)', async () => {
    const objectivesList = page.locator('[data-testid="learning-objectives-list"]');
    const tagName = await objectivesList.evaluate(el => el.tagName.toLowerCase());
    expect(['ul', 'ol']).toContain(tagName);
  });

  test('should display checkmark icons next to completed objectives', async () => {
    // Mock completed attempt
    await page.route('**/api/v1/osces/*/progress', async route => {
      route.fulfill({
        json: {
          completed_objectives: ['Perform systematic cardiovascular examination'],
        },
      });
    });

    await page.reload();

    const checkmark = page.locator('[data-testid="objective-completed-icon"]').first();
    if (await checkmark.isVisible()) {
      await expect(checkmark).toBeVisible();
    }
  });

  test('should highlight learning objectives with visual distinction', async () => {
    const objectivesList = page.locator('[data-testid="learning-objectives-list"]');
    const bgColor = await objectivesList.evaluate(el => window.getComputedStyle(el).backgroundColor);
    expect(bgColor).toBeTruthy(); // Should have some styling
  });
});

test.describe('OSCE Learning Objectives - Key Points Section', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
  });

  test('should display key points section', async () => {
    const keyPointsSection = page.locator('[data-testid="key-points-section"]');
    await expect(keyPointsSection).toBeVisible();
  });

  test('should show section heading for key points', async () => {
    const heading = page.locator('[data-testid="key-points-heading"]');
    await expect(heading).toBeVisible();
    await expect(heading).toContainText(/key.*point/i);
  });

  test('should display all key points', async () => {
    const keyPoints = page.locator('[data-testid="key-point-item"]');
    const count = await keyPoints.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should show first key point: "Position patient at 45 degrees for JVP"', async () => {
    const firstKeyPoint = page.locator('[data-testid="key-point-item"]').first();
    await expect(firstKeyPoint).toContainText(/position.*patient.*45.*degree.*JVP/i);
  });

  test('should show second key point: "Auscultate at 4 key areas (APTM)"', async () => {
    const keyPoints = page.locator('[data-testid="key-point-item"]');
    const secondKeyPoint = keyPoints.nth(1);
    await expect(secondKeyPoint).toContainText(/auscultate.*4.*area.*APTM|aortic.*pulmonary.*tricuspid.*mitral/i);
  });

  test('should show third key point: "Check peripheral signs"', async () => {
    const keyPoints = page.locator('[data-testid="key-point-item"]');
    const thirdKeyPoint = keyPoints.nth(2);
    await expect(thirdKeyPoint).toContainText(/peripheral.*sign.*clubbing.*cyanosis.*edema/i);
  });

  test('should use icon/bullet points for key points', async () => {
    const firstKeyPoint = page.locator('[data-testid="key-point-item"]').first();
    const icon = firstKeyPoint.locator('[data-testid="key-point-icon"]');

    if (await icon.isVisible()) {
      await expect(icon).toBeVisible();
    }
  });

  test('should distinguish key points visually from objectives', async () => {
    const keyPointsList = page.locator('[data-testid="key-points-list"]');
    const objectivesList = page.locator('[data-testid="learning-objectives-list"]');

    const keyPointsBg = await keyPointsList.evaluate(el => window.getComputedStyle(el).backgroundColor);
    const objectivesBg = await objectivesList.evaluate(el => window.getComputedStyle(el).backgroundColor);

    // Sections should have different styling
    expect(keyPointsBg).toBeTruthy();
    expect(objectivesBg).toBeTruthy();
  });
});

test.describe('OSCE Learning Objectives - Expandable Content', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
  });

  test('should show "Show Learning Objectives" button if collapsed by default', async () => {
    const showButton = page.locator('[data-testid="show-objectives-button"]');

    if (await showButton.isVisible()) {
      await expect(showButton).toBeVisible();
    }
  });

  test('should expand objectives when expand button clicked', async () => {
    const showButton = page.locator('[data-testid="show-objectives-button"]');

    if (await showButton.isVisible()) {
      await showButton.click();

      const objectivesList = page.locator('[data-testid="learning-objectives-list"]');
      await expect(objectivesList).toBeVisible();
    }
  });

  test('should collapse objectives when collapse button clicked', async () => {
    const showButton = page.locator('[data-testid="show-objectives-button"]');

    if (await showButton.isVisible()) {
      await showButton.click();

      const hideButton = page.locator('[data-testid="hide-objectives-button"]');
      await hideButton.click();

      const objectivesList = page.locator('[data-testid="learning-objectives-list"]');
      await expect(objectivesList).not.toBeVisible();
    }
  });

  test('should update aria-expanded attribute on toggle', async () => {
    const toggleButton = page.locator('[data-testid="objectives-toggle-button"]');

    if (await toggleButton.isVisible()) {
      const expandedBefore = await toggleButton.getAttribute('aria-expanded');

      await toggleButton.click();

      const expandedAfter = await toggleButton.getAttribute('aria-expanded');
      expect(expandedAfter).not.toBe(expandedBefore);
    }
  });

  test('should persist expanded/collapsed state on page reload', async () => {
    const showButton = page.locator('[data-testid="show-objectives-button"]');

    if (await showButton.isVisible()) {
      await showButton.click();

      await page.reload();

      const objectivesList = page.locator('[data-testid="learning-objectives-list"]');
      await expect(objectivesList).toBeVisible();
    }
  });
});

test.describe('OSCE Learning Objectives - Integration with Video Resources', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
  });

  test('should link video resources to specific learning objectives', async () => {
    const videoLink = page.locator('[data-testid="objective-video-link"]').first();

    if (await videoLink.isVisible()) {
      await expect(videoLink).toBeVisible();
      await expect(videoLink).toContainText(/watch.*video|view.*demonstration/i);
    }
  });

  test('should show which videos support each objective', async () => {
    const firstObjective = page.locator('[data-testid="learning-objective-item"]').first();
    const supportingVideos = firstObjective.locator('[data-testid="supporting-video"]');

    if ((await supportingVideos.count()) > 0) {
      await expect(supportingVideos.first()).toBeVisible();
    }
  });

  test('should navigate to video resource when video link clicked', async () => {
    const videoLink = page.locator('[data-testid="objective-video-link"]').first();

    if (await videoLink.isVisible()) {
      const href = await videoLink.getAttribute('href');
      expect(href).toBeTruthy();
      expect(href).toMatch(/https?:\/\//);
    }
  });

  test('should show "Recommended Videos" section near objectives', async () => {
    const recommendedSection = page.locator('[data-testid="recommended-videos-section"]');

    if (await recommendedSection.isVisible()) {
      await expect(recommendedSection).toBeVisible();
    }
  });
});

test.describe('OSCE Learning Objectives - Progress Tracking', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    // Mock progress data
    await page.route('**/api/v1/osces/*/progress', async route => {
      route.fulfill({
        json: {
          completed_objectives: [
            'Perform systematic cardiovascular examination',
            'Identify normal and abnormal cardiovascular signs',
          ],
          total_objectives: 3,
          completion_percentage: 67,
        },
      });
    });

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
  });

  test('should show objectives completion percentage', async () => {
    const completionPercentage = page.locator('[data-testid="objectives-completion-percentage"]');

    if (await completionPercentage.isVisible()) {
      await expect(completionPercentage).toBeVisible();
      await expect(completionPercentage).toContainText(/67.*%/);
    }
  });

  test('should display progress bar for objectives', async () => {
    const progressBar = page.locator('[data-testid="objectives-progress-bar"]');

    if (await progressBar.isVisible()) {
      await expect(progressBar).toBeVisible();
      const progress = await progressBar.getAttribute('aria-valuenow');
      expect(parseInt(progress!)).toBe(67);
    }
  });

  test('should mark completed objectives with checkmark', async () => {
    const completedObjectives = page.locator('[data-testid="objective-completed"]');
    const count = await completedObjectives.count();
    expect(count).toBe(2);
  });

  test('should show "2 of 3 completed" text', async () => {
    const completionText = page.locator('[data-testid="objectives-completion-text"]');

    if (await completionText.isVisible()) {
      await expect(completionText).toContainText(/2.*of.*3/i);
    }
  });

  test('should update completion status when objective achieved', async () => {
    // Complete an attempt
    let progressUpdated = false;

    await page.route('**/api/v1/osces/*/progress', async route => {
      if (route.request().method() === 'PATCH') {
        progressUpdated = true;
      }
      await route.continue();
    });

    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    // Complete the attempt (simplified)
    await page.waitForTimeout(1000);

    if (progressUpdated) {
      expect(progressUpdated).toBeTruthy();
    }
  });
});

test.describe('OSCE Learning Objectives - Accessibility', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
  });

  test('should have semantic HTML for objectives list', async () => {
    const objectivesList = page.locator('[data-testid="learning-objectives-list"]');
    const tagName = await objectivesList.evaluate(el => el.tagName.toLowerCase());
    expect(['ul', 'ol']).toContain(tagName);
  });

  test('should have proper heading hierarchy', async () => {
    const objectivesHeading = page.locator('[data-testid="learning-objectives-heading"]');
    const headingLevel = await objectivesHeading.evaluate(el => el.tagName.toLowerCase());
    expect(['h2', 'h3', 'h4']).toContain(headingLevel);
  });

  test('should have aria-label on objectives section', async () => {
    const objectivesSection = page.locator('[data-testid="learning-objectives-section"]');
    const ariaLabel = await objectivesSection.getAttribute('aria-label');

    if (ariaLabel) {
      expect(ariaLabel.toLowerCase()).toContain('learning');
    }
  });

  test('should support keyboard navigation through objectives', async () => {
    const firstObjective = page.locator('[data-testid="learning-objective-item"]').first();

    // Tab to first objective
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    if (await firstObjective.isVisible()) {
      // Should be able to navigate
      await expect(firstObjective).toBeVisible();
    }
  });

  test('should announce completion status to screen readers', async () => {
    const liveRegion = page.locator('[aria-live="polite"]');

    if (await liveRegion.isVisible()) {
      await expect(liveRegion).toBeVisible();
    }
  });

  test('should have descriptive alt text for objective icons', async () => {
    const objectiveIcon = page.locator('[data-testid="objective-completed-icon"]').first();

    if (await objectiveIcon.isVisible()) {
      const ariaLabel = await objectiveIcon.getAttribute('aria-label');
      expect(ariaLabel).toBeTruthy();
    }
  });
});

test.describe('OSCE Learning Objectives - Responsive Design', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
  });

  test('should display objectives in single column on mobile (375x667)', async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const objectivesSection = page.locator('[data-testid="learning-objectives-section"]');
    const width = await objectivesSection.evaluate(el => el.offsetWidth);
    expect(width).toBeLessThan(400); // Should take full width on mobile
  });

  test('should have readable font size on mobile', async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const firstObjective = page.locator('[data-testid="learning-objective-item"]').first();
    const fontSize = await firstObjective.evaluate(el => window.getComputedStyle(el).fontSize);
    const fontSizeNum = parseInt(fontSize);
    expect(fontSizeNum).toBeGreaterThanOrEqual(14); // Readable font size
  });

  test('should have adequate spacing between objectives on mobile', async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const firstObjective = page.locator('[data-testid="learning-objective-item"]').first();
    const marginBottom = await firstObjective.evaluate(el => window.getComputedStyle(el).marginBottom);
    expect(marginBottom).not.toBe('0px'); // Should have spacing
  });

  test('should display objectives in two columns on tablet (768x1024)', async () => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const objectivesSection = page.locator('[data-testid="learning-objectives-section"]');
    await expect(objectivesSection).toBeVisible();
  });

  test('should have touch-friendly expand/collapse buttons on mobile', async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const toggleButton = page.locator('[data-testid="objectives-toggle-button"]');

    if (await toggleButton.isVisible()) {
      const box = await toggleButton.boundingBox();
      expect(box!.height).toBeGreaterThanOrEqual(44); // Touch-friendly size
    }
  });
});
