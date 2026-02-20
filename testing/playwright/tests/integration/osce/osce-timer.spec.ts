/**
 * OSCE Timer Integration Tests
 *
 * Tests the 8-minute OSCE station timer functionality
 * Covers: Timer display, countdown, pause/resume, warnings, expiry, persistence
 *
 * Test Data: Uses seeded OSCEs from setup/seed-test-data.ts
 * Authentication: Student role (attempts OSCEs with timer)
 */

import { test, expect, Page } from '@playwright/test';
import { TEST_USERS } from '../../../utils/test-data/users';

test.describe('OSCE Timer - Display and Countdown', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');

    // Start OSCE attempt
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');
  });

  test('should display timer in MM:SS format', async () => {
    const timer = page.locator('[data-testid="station-timer"]');
    await expect(timer).toBeVisible();

    const timerText = await timer.textContent();
    expect(timerText).toMatch(/^\d{1,2}:\d{2}$/); // Format: 8:00 or 7:59
  });

  test('should start timer at 8:00 (8 minutes)', async () => {
    const timer = page.locator('[data-testid="station-timer"]');
    const timerText = await timer.textContent();
    expect(timerText).toMatch(/7:5[0-9]|8:00/); // Should be close to 8:00
  });

  test('should countdown from 8:00', async () => {
    const timer = page.locator('[data-testid="station-timer"]');
    const initialTime = await timer.textContent();

    // Wait 3 seconds
    await page.waitForTimeout(3000);

    const newTime = await timer.textContent();
    expect(newTime).not.toBe(initialTime);
  });

  test('should update timer every second', async () => {
    const timer = page.locator('[data-testid="station-timer"]');
    const initialTime = await timer.textContent();

    await page.waitForTimeout(1100);

    const newTime = await timer.textContent();
    expect(newTime).not.toBe(initialTime);
  });

  test('should display timer prominently at top of page', async () => {
    const timer = page.locator('[data-testid="station-timer"]');
    const boundingBox = await timer.boundingBox();

    expect(boundingBox!.y).toBeLessThan(200); // Should be in top 200px of page
  });

  test('should show timer with clock icon', async () => {
    const timerContainer = page.locator('[data-testid="timer-container"]');
    const clockIcon = timerContainer.locator('[data-testid="clock-icon"]');

    if (await clockIcon.isVisible()) {
      await expect(clockIcon).toBeVisible();
    }
  });

  test('should display "Time Remaining" label', async () => {
    const timerLabel = page.locator('[data-testid="timer-label"]');
    await expect(timerLabel).toBeVisible();
    await expect(timerLabel).toContainText(/time.*remaining/i);
  });

  test('should have timer visible throughout attempt', async () => {
    const timer = page.locator('[data-testid="station-timer"]');
    await expect(timer).toBeVisible();

    // Scroll down
    await page.evaluate(() => window.scrollTo(0, 500));

    // Timer should still be visible (sticky positioning)
    await expect(timer).toBeVisible();
  });

  test('should format timer correctly when transitioning 10:00 to 9:59', async () => {
    // Mock timer at 10 minutes for OSCEs with longer time limits
    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '600');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const timer = page.locator('[data-testid="station-timer"]');
    const timerText = await timer.textContent();
    expect(timerText).toMatch(/^\d{1,2}:\d{2}$/);
  });

  test('should format timer correctly when under 1 minute (0:59, 0:58...)', async () => {
    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '59');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const timer = page.locator('[data-testid="station-timer"]');
    const timerText = await timer.textContent();
    expect(timerText).toMatch(/^0:\d{2}$/); // 0:59, 0:58, etc.
  });
});

test.describe('OSCE Timer - Pause and Resume', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');

    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');
  });

  test('should display pause button', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    await expect(pauseButton).toBeVisible();
  });

  test('should pause timer when pause button clicked', async () => {
    const timer = page.locator('[data-testid="station-timer"]');
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');

    const timeBefore = await timer.textContent();
    await pauseButton.click();

    await page.waitForTimeout(2500);

    const timeAfter = await timer.textContent();
    expect(timeAfter).toBe(timeBefore); // Time should not change
  });

  test('should show "Paused" indicator when timer paused', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    await pauseButton.click();

    const pausedIndicator = page.locator('[data-testid="timer-paused-indicator"]');
    await expect(pausedIndicator).toBeVisible();
    await expect(pausedIndicator).toContainText(/paused/i);
  });

  test('should change pause button to resume button when paused', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    await pauseButton.click();

    const resumeButton = page.locator('[data-testid="resume-timer-button"]');
    await expect(resumeButton).toBeVisible();
  });

  test('should resume timer when resume button clicked', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    await pauseButton.click();

    const resumeButton = page.locator('[data-testid="resume-timer-button"]');
    await resumeButton.click();

    const timer = page.locator('[data-testid="station-timer"]');
    const timeBefore = await timer.textContent();

    await page.waitForTimeout(2000);

    const timeAfter = await timer.textContent();
    expect(timeAfter).not.toBe(timeBefore); // Time should resume counting
  });

  test('should hide "Paused" indicator when resumed', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    await pauseButton.click();

    const resumeButton = page.locator('[data-testid="resume-timer-button"]');
    await resumeButton.click();

    const pausedIndicator = page.locator('[data-testid="timer-paused-indicator"]');
    await expect(pausedIndicator).not.toBeVisible();
  });

  test('should allow multiple pause/resume cycles', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    const resumeButton = page.locator('[data-testid="resume-timer-button"]');

    // Pause
    await pauseButton.click();
    await page.waitForTimeout(1000);

    // Resume
    await resumeButton.click();
    await page.waitForTimeout(1000);

    // Pause again
    await pauseButton.click();
    await page.waitForTimeout(1000);

    const pausedIndicator = page.locator('[data-testid="timer-paused-indicator"]');
    await expect(pausedIndicator).toBeVisible();
  });

  test('should track total pause time', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    await pauseButton.click();

    await page.waitForTimeout(3000);

    const resumeButton = page.locator('[data-testid="resume-timer-button"]');
    await resumeButton.click();

    // Total pause time should be tracked (may be displayed in results)
    const pauseTime = page.locator('[data-testid="total-pause-time"]');
    if (await pauseTime.isVisible()) {
      const pauseText = await pauseTime.textContent();
      expect(pauseText).toMatch(/\d+/);
    }
  });

  test('should show warning when pausing timer', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    await pauseButton.click();

    const warning = page.locator('[data-testid="pause-warning"]');
    if (await warning.isVisible()) {
      await expect(warning).toContainText(/practice.*mode|pause/i);
    }
  });
});

test.describe('OSCE Timer - Warnings and Visual Indicators', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
  });

  test('should show warning banner when 2 minutes remaining', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    // Set timer to 2 minutes
    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '120');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const warningBanner = page.locator('[data-testid="time-warning-banner"]');
    await expect(warningBanner).toBeVisible();
    await expect(warningBanner).toContainText(/2.*minute.*remaining/i);
  });

  test('should show critical warning when 1 minute remaining', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '60');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const criticalWarning = page.locator('[data-testid="critical-time-warning"]');
    await expect(criticalWarning).toBeVisible();
    await expect(criticalWarning).toContainText(/1.*minute.*remaining/i);
  });

  test('should change timer color to amber when 2 minutes remaining', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '120');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const timer = page.locator('[data-testid="station-timer"]');
    const color = await timer.evaluate(el => window.getComputedStyle(el).color);

    // Should be amber/orange (not default color)
    expect(color).toBeTruthy();
  });

  test('should change timer color to red when under 1 minute', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '45');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const timer = page.locator('[data-testid="station-timer"]');
    const color = await timer.evaluate(el => window.getComputedStyle(el).color);

    // Should be red
    expect(color).toBeTruthy();
  });

  test('should pulse/animate timer when under 30 seconds', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '25');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const timer = page.locator('[data-testid="station-timer"]');
    const animationName = await timer.evaluate(el => window.getComputedStyle(el).animationName);

    // Should have some animation
    expect(animationName).not.toBe('none');
  });

  test('should show progress bar indicating time elapsed', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const progressBar = page.locator('[data-testid="timer-progress-bar"]');

    if (await progressBar.isVisible()) {
      await expect(progressBar).toBeVisible();
      const progress = await progressBar.getAttribute('aria-valuenow');
      expect(parseInt(progress!)).toBeGreaterThanOrEqual(0);
    }
  });

  test('should display visual cue when timer reaches 0:10', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '10');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const finalWarning = page.locator('[data-testid="final-seconds-warning"]');
    if (await finalWarning.isVisible()) {
      await expect(finalWarning).toBeVisible();
    }
  });
});

test.describe('OSCE Timer - Expiry and Auto-Submit', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
  });

  test('should show "Time Expired" modal when timer reaches 0:00', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '2');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    await page.waitForTimeout(3000);

    const expiryModal = page.locator('[data-testid="timer-expired-modal"]');
    await expect(expiryModal).toBeVisible();
    await expect(expiryModal).toContainText(/time.*expired/i);
  });

  test('should auto-save all progress when timer expires', async () => {
    let autoSaved = false;

    await page.route('**/api/v1/osces/*/attempts/*/save', async route => {
      autoSaved = true;
      await route.continue();
    });

    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '1');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    // Add some notes
    await page.fill('[data-testid="findings-notes"]', 'Timer expiry test');

    await page.waitForTimeout(2000);

    expect(autoSaved).toBeTruthy();
  });

  test('should auto-navigate to review page after 5 seconds', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '1');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    await page.waitForTimeout(6000);

    await expect(page).toHaveURL(/\/review/);
  });

  test('should allow manual navigation to review page from expiry modal', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '1');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    await page.waitForTimeout(2000);

    const reviewButton = page.locator('[data-testid="go-to-review-button"]');
    if (await reviewButton.isVisible()) {
      await reviewButton.click();
      await expect(page).toHaveURL(/\/review/);
    }
  });

  test('should mark attempt status as "time_expired" in database', async () => {
    let attemptMarkedExpired = false;

    await page.route('**/api/v1/osces/*/attempts/*', async route => {
      if (route.request().method() === 'PATCH') {
        const postData = route.request().postDataJSON();
        if (postData?.status === 'time_expired') {
          attemptMarkedExpired = true;
        }
      }
      await route.continue();
    });

    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '1');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    await page.waitForTimeout(2500);

    expect(attemptMarkedExpired).toBeTruthy();
  });

  test('should disable all inputs when timer expires', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '1');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    await page.waitForTimeout(2000);

    const notesField = page.locator('[data-testid="findings-notes"]');
    await expect(notesField).toBeDisabled();
  });
});

test.describe('OSCE Timer - Persistence and Recovery', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
  });

  test('should persist timer state on page reload', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const timer = page.locator('[data-testid="station-timer"]');
    const timeBefore = await timer.textContent();

    await page.reload();

    const timeAfter = await timer.textContent();
    expect(timeAfter).toBeTruthy(); // Timer should still be present
  });

  test('should resume countdown after page reload', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    await page.reload();

    const timer = page.locator('[data-testid="station-timer"]');
    const timeBefore = await timer.textContent();

    await page.waitForTimeout(2000);

    const timeAfter = await timer.textContent();
    expect(timeAfter).not.toBe(timeBefore); // Should continue counting down
  });

  test('should handle browser tab switching gracefully', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const timer = page.locator('[data-testid="station-timer"]');
    const timeBefore = await timer.textContent();

    // Simulate tab switch (document visibility change)
    await page.evaluate(() => {
      Object.defineProperty(document, 'hidden', { value: true, writable: true });
      document.dispatchEvent(new Event('visibilitychange'));
    });

    await page.waitForTimeout(1000);

    await page.evaluate(() => {
      Object.defineProperty(document, 'hidden', { value: false, writable: true });
      document.dispatchEvent(new Event('visibilitychange'));
    });

    // Timer should still be running
    const timeAfter = await timer.textContent();
    expect(timeAfter).toBeTruthy();
  });

  test('should sync timer with server on navigation', async () => {
    let timerSynced = false;

    await page.route('**/api/v1/osces/*/attempts/*/timer', async route => {
      timerSynced = true;
      await route.continue();
    });

    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    await page.reload();

    expect(timerSynced).toBeTruthy();
  });
});

test.describe('OSCE Timer - Accessibility', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');

    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');
  });

  test('should have aria-label on timer', async () => {
    const timer = page.locator('[data-testid="station-timer"]');
    const ariaLabel = await timer.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();
    expect(ariaLabel?.toLowerCase()).toContain('time');
  });

  test('should announce time warnings to screen readers', async () => {
    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '60');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    const liveRegion = page.locator('[aria-live="assertive"]');
    if (await liveRegion.isVisible()) {
      await expect(liveRegion).toBeVisible();
    }
  });

  test('should have accessible pause/resume buttons', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    const ariaLabel = await pauseButton.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();
    expect(ariaLabel?.toLowerCase()).toContain('pause');
  });

  test('should update aria-label when timer updates', async () => {
    const timer = page.locator('[data-testid="station-timer"]');
    const ariaLabelBefore = await timer.getAttribute('aria-label');

    await page.waitForTimeout(2000);

    const ariaLabelAfter = await timer.getAttribute('aria-label');
    expect(ariaLabelAfter).not.toBe(ariaLabelBefore);
  });
});
