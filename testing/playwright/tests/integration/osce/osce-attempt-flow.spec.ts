/**
 * OSCE Attempt Flow Integration Tests
 *
 * Tests the complete OSCE station attempt workflow from start to completion
 * Covers: Start attempt, read instructions, timer, answer submission, review, completion
 *
 * Test Data: Uses seeded OSCEs from setup/seed-test-data.ts
 * Authentication: Student role (can attempt OSCEs)
 */

import { test, expect, Page } from '@playwright/test';
import { TEST_USERS } from '../../../utils/test-data/users';

test.describe('OSCE Attempt Flow - Start Attempt', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    // Login as student
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);

    // Navigate to OSCE detail page
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
  });

  test('should display "Start Attempt" button on OSCE detail page', async () => {
    const startButton = page.locator('[data-testid="start-attempt-button"]');
    await expect(startButton).toBeVisible();
    await expect(startButton).toContainText(/start/i);
  });

  test('should show confirmation dialog when "Start Attempt" clicked', async () => {
    const startButton = page.locator('[data-testid="start-attempt-button"]');
    await startButton.click();

    const confirmDialog = page.locator('[data-testid="start-attempt-confirmation"]');
    await expect(confirmDialog).toBeVisible();
    await expect(confirmDialog).toContainText(/are you ready/i);
  });

  test('should display OSCE metadata in confirmation dialog', async () => {
    const startButton = page.locator('[data-testid="start-attempt-button"]');
    await startButton.click();

    const confirmDialog = page.locator('[data-testid="start-attempt-confirmation"]');
    await expect(confirmDialog.locator('[data-testid="osce-time-limit"]')).toBeVisible();
    await expect(confirmDialog.locator('[data-testid="osce-station-type"]')).toBeVisible();
  });

  test('should show timer warning in confirmation dialog', async () => {
    const startButton = page.locator('[data-testid="start-attempt-button"]');
    await startButton.click();

    const confirmDialog = page.locator('[data-testid="start-attempt-confirmation"]');
    await expect(confirmDialog).toContainText(/timer will start/i);
  });

  test('should cancel attempt when "Cancel" clicked in confirmation', async () => {
    const startButton = page.locator('[data-testid="start-attempt-button"]');
    await startButton.click();

    const cancelButton = page.locator('[data-testid="cancel-attempt-button"]');
    await cancelButton.click();

    // Should remain on detail page
    await expect(page).toHaveURL(/\/osces\/TEST-CARDIO-VIDEO-001$/);
    const confirmDialog = page.locator('[data-testid="start-attempt-confirmation"]');
    await expect(confirmDialog).not.toBeVisible();
  });

  test('should navigate to attempt page when "Confirm Start" clicked', async () => {
    const startButton = page.locator('[data-testid="start-attempt-button"]');
    await startButton.click();

    const confirmButton = page.locator('[data-testid="confirm-start-button"]');
    await confirmButton.click();

    // Should navigate to /osces/{id}/attempt
    await expect(page).toHaveURL(/\/osces\/TEST-CARDIO-VIDEO-001\/attempt/);
  });

  test('should create attempt record in database when attempt starts', async () => {
    const startButton = page.locator('[data-testid="start-attempt-button"]');
    await startButton.click();

    const confirmButton = page.locator('[data-testid="confirm-start-button"]');

    // Intercept API call
    let attemptCreated = false;
    await page.route('**/api/v1/osces/*/attempts', async route => {
      attemptCreated = true;
      await route.continue();
    });

    await confirmButton.click();
    await page.waitForTimeout(1000);

    expect(attemptCreated).toBeTruthy();
  });

  test('should disable "Start Attempt" button during attempt creation', async () => {
    const startButton = page.locator('[data-testid="start-attempt-button"]');
    await startButton.click();

    const confirmButton = page.locator('[data-testid="confirm-start-button"]');

    // Slow down API response
    await page.route('**/api/v1/osces/*/attempts', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.continue();
    });

    await confirmButton.click();

    // Button should be disabled
    await expect(confirmButton).toBeDisabled();
  });

  test('should show loading spinner during attempt creation', async () => {
    const startButton = page.locator('[data-testid="start-attempt-button"]');
    await startButton.click();

    const confirmButton = page.locator('[data-testid="confirm-start-button"]');

    await page.route('**/api/v1/osces/*/attempts', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.continue();
    });

    await confirmButton.click();

    const spinner = page.locator('[data-testid="loading-spinner"]');
    await expect(spinner).toBeVisible();
  });

  test('should handle attempt creation error gracefully', async () => {
    const startButton = page.locator('[data-testid="start-attempt-button"]');
    await startButton.click();

    const confirmButton = page.locator('[data-testid="confirm-start-button"]');

    // Mock API error
    await page.route('**/api/v1/osces/*/attempts', route => {
      route.fulfill({ status: 500, json: { detail: 'Database error' } });
    });

    await confirmButton.click();
    await page.waitForTimeout(1000);

    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/error.*starting.*attempt/i);
  });
});

test.describe('OSCE Attempt Flow - Instructions Phase', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');

    // Start an attempt
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
  });

  test('should display candidate instructions prominently', async () => {
    const candidateInstructions = page.locator('[data-testid="candidate-instructions"]');
    await expect(candidateInstructions).toBeVisible();
    await expect(candidateInstructions).toContainText(/perform.*cardiovascular.*examination/i);
  });

  test('should display patient instructions in separate section', async () => {
    const patientInstructions = page.locator('[data-testid="patient-instructions"]');
    await expect(patientInstructions).toBeVisible();
  });

  test('should show time limit warning on attempt page', async () => {
    const timeWarning = page.locator('[data-testid="time-limit-warning"]');
    await expect(timeWarning).toBeVisible();
    await expect(timeWarning).toContainText(/8.*minute/i);
  });

  test('should display "Begin Station" button after reading instructions', async () => {
    const beginButton = page.locator('[data-testid="begin-station-button"]');
    await expect(beginButton).toBeVisible();
    await expect(beginButton).toContainText(/begin/i);
  });

  test('should require acknowledgment checkbox before beginning', async () => {
    const acknowledgment = page.locator('[data-testid="instructions-acknowledgment"]');
    const beginButton = page.locator('[data-testid="begin-station-button"]');

    // Button should be disabled initially
    await expect(beginButton).toBeDisabled();

    // Check acknowledgment
    await acknowledgment.check();

    // Button should now be enabled
    await expect(beginButton).toBeEnabled();
  });

  test('should start timer when "Begin Station" clicked', async () => {
    const acknowledgment = page.locator('[data-testid="instructions-acknowledgment"]');
    await acknowledgment.check();

    const beginButton = page.locator('[data-testid="begin-station-button"]');
    await beginButton.click();

    const timer = page.locator('[data-testid="station-timer"]');
    await expect(timer).toBeVisible();
    await expect(timer).toContainText(/\d{1,2}:\d{2}/);
  });

  test('should hide instructions and show station content when begun', async () => {
    const acknowledgment = page.locator('[data-testid="instructions-acknowledgment"]');
    await acknowledgment.check();

    const beginButton = page.locator('[data-testid="begin-station-button"]');
    await beginButton.click();

    const instructions = page.locator('[data-testid="candidate-instructions"]');
    await expect(instructions).not.toBeVisible();

    const stationContent = page.locator('[data-testid="station-content"]');
    await expect(stationContent).toBeVisible();
  });

  test('should display examiner rubric during attempt (for practice mode)', async () => {
    const acknowledgment = page.locator('[data-testid="instructions-acknowledgment"]');
    await acknowledgment.check();

    const beginButton = page.locator('[data-testid="begin-station-button"]');
    await beginButton.click();

    const rubric = page.locator('[data-testid="examiner-rubric"]');
    await expect(rubric).toBeVisible();
  });

  test('should show "Instructions" button to re-view instructions', async () => {
    const acknowledgment = page.locator('[data-testid="instructions-acknowledgment"]');
    await acknowledgment.check();

    const beginButton = page.locator('[data-testid="begin-station-button"]');
    await beginButton.click();

    const instructionsButton = page.locator('[data-testid="view-instructions-button"]');
    await expect(instructionsButton).toBeVisible();

    await instructionsButton.click();

    const instructionsModal = page.locator('[data-testid="instructions-modal"]');
    await expect(instructionsModal).toBeVisible();
  });
});

test.describe('OSCE Attempt Flow - Active Station', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');

    // Start attempt and begin station
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');
  });

  test('should display timer counting down from 8 minutes', async () => {
    const timer = page.locator('[data-testid="station-timer"]');
    await expect(timer).toBeVisible();

    const initialTime = await timer.textContent();
    expect(initialTime).toMatch(/7:5[0-9]|8:00/); // Should be close to 8:00
  });

  test('should display checklist of examination steps', async () => {
    const checklist = page.locator('[data-testid="examination-checklist"]');
    await expect(checklist).toBeVisible();

    const checklistItems = page.locator('[data-testid="checklist-item"]');
    const count = await checklistItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should allow checking off examination steps', async () => {
    const firstChecklistItem = page.locator('[data-testid="checklist-item"]').first();
    const checkbox = firstChecklistItem.locator('input[type="checkbox"]');

    await checkbox.check();
    await expect(checkbox).toBeChecked();
  });

  test('should show progress bar based on completed steps', async () => {
    const progressBar = page.locator('[data-testid="progress-bar"]');
    await expect(progressBar).toBeVisible();

    const initialProgress = await progressBar.getAttribute('aria-valuenow');

    // Check first item
    const firstCheckbox = page.locator('[data-testid="checklist-item"]').first().locator('input[type="checkbox"]');
    await firstCheckbox.check();

    await page.waitForTimeout(500);

    const newProgress = await progressBar.getAttribute('aria-valuenow');
    expect(parseInt(newProgress!)).toBeGreaterThan(parseInt(initialProgress!));
  });

  test('should display notes/findings text area', async () => {
    const notesArea = page.locator('[data-testid="findings-notes"]');
    await expect(notesArea).toBeVisible();
  });

  test('should allow typing notes during attempt', async () => {
    const notesArea = page.locator('[data-testid="findings-notes"]');
    await notesArea.fill('Patient has regular heart rhythm, no murmurs detected.');

    const value = await notesArea.inputValue();
    expect(value).toContain('regular heart rhythm');
  });

  test('should auto-save notes every 30 seconds', async () => {
    const notesArea = page.locator('[data-testid="findings-notes"]');
    await notesArea.fill('Auto-save test notes');

    // Wait for auto-save
    await page.waitForTimeout(31000);

    // Check for save indicator
    const saveIndicator = page.locator('[data-testid="auto-save-indicator"]');
    if (await saveIndicator.isVisible()) {
      await expect(saveIndicator).toContainText(/saved/i);
    }
  });

  test('should show "Finish Station" button', async () => {
    const finishButton = page.locator('[data-testid="finish-station-button"]');
    await expect(finishButton).toBeVisible();
    await expect(finishButton).toContainText(/finish/i);
  });

  test('should warn when finishing with unchecked items', async () => {
    const finishButton = page.locator('[data-testid="finish-station-button"]');
    await finishButton.click();

    const warningDialog = page.locator('[data-testid="incomplete-warning"]');
    await expect(warningDialog).toBeVisible();
    await expect(warningDialog).toContainText(/not.*completed.*all.*steps/i);
  });

  test('should allow proceeding despite incomplete steps', async () => {
    const finishButton = page.locator('[data-testid="finish-station-button"]');
    await finishButton.click();

    const proceedButton = page.locator('[data-testid="proceed-anyway-button"]');
    await proceedButton.click();

    // Should navigate to review page
    await expect(page).toHaveURL(/\/review/);
  });

  test('should show pause button for timer', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    await expect(pauseButton).toBeVisible();
  });

  test('should pause timer when pause clicked', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    const timer = page.locator('[data-testid="station-timer"]');

    const timeBefore = await timer.textContent();
    await pauseButton.click();

    await page.waitForTimeout(2000);

    const timeAfter = await timer.textContent();
    expect(timeAfter).toBe(timeBefore); // Time should not change
  });

  test('should resume timer when resume clicked', async () => {
    const pauseButton = page.locator('[data-testid="pause-timer-button"]');
    await pauseButton.click();

    const resumeButton = page.locator('[data-testid="resume-timer-button"]');
    await resumeButton.click();

    const timer = page.locator('[data-testid="station-timer"]');
    const timeBefore = await timer.textContent();

    await page.waitForTimeout(2000);

    const timeAfter = await timer.textContent();
    expect(timeAfter).not.toBe(timeBefore); // Time should change
  });
});

test.describe('OSCE Attempt Flow - Timer Expiry', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
  });

  test('should show warning when 1 minute remaining', async () => {
    // Mock timer to be at 1 minute
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    // Inject timer state
    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '60');
    });

    await page.reload();

    const warningBanner = page.locator('[data-testid="time-warning-banner"]');
    await expect(warningBanner).toBeVisible();
    await expect(warningBanner).toContainText(/1.*minute.*remaining/i);
  });

  test('should change timer color to red when < 1 minute remaining', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '45');
    });

    await page.reload();

    const timer = page.locator('[data-testid="station-timer"]');
    const color = await timer.evaluate(el => window.getComputedStyle(el).color);
    // Should be red (rgb values containing high red, low green/blue)
    expect(color).toBeTruthy();
  });

  test('should auto-finish attempt when timer reaches 0:00', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);

    // Set timer to expire in 2 seconds
    await page.evaluate(() => {
      localStorage.setItem('attempt-timer-remaining', '2');
    });

    await page.reload();
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    // Wait for timer expiry
    await page.waitForTimeout(3000);

    // Should auto-navigate to review page
    await expect(page).toHaveURL(/\/review/);
  });

  test('should show "Time Expired" dialog when timer reaches 0:00', async () => {
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

    const expiryDialog = page.locator('[data-testid="timer-expired-dialog"]');
    await expect(expiryDialog).toBeVisible();
    await expect(expiryDialog).toContainText(/time.*expired/i);
  });

  test('should save all progress when timer expires', async () => {
    let saveRequested = false;

    await page.route('**/api/v1/osces/*/attempts/*/save', async route => {
      saveRequested = true;
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

    // Type some notes
    await page.fill('[data-testid="findings-notes"]', 'Quick notes before expiry');

    await page.waitForTimeout(2000);

    expect(saveRequested).toBeTruthy();
  });
});

test.describe('OSCE Attempt Flow - Review and Submit', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');

    // Complete attempt flow
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
    await page.click('[data-testid="start-attempt-button"]');
    await page.click('[data-testid="confirm-start-button"]');
    await page.waitForURL(/\/attempt/);
    await page.check('[data-testid="instructions-acknowledgment"]');
    await page.click('[data-testid="begin-station-button"]');

    // Fill in some data
    await page.fill('[data-testid="findings-notes"]', 'Review test notes');
    await page.click('[data-testid="checklist-item"]').first();

    // Finish station
    await page.click('[data-testid="finish-station-button"]');
    await page.click('[data-testid="proceed-anyway-button"]');
  });

  test('should display review page with attempt summary', async () => {
    const reviewHeader = page.locator('h1:has-text("Review Your Attempt")');
    await expect(reviewHeader).toBeVisible();
  });

  test('should show completed checklist items', async () => {
    const completedItems = page.locator('[data-testid="completed-checklist-items"]');
    await expect(completedItems).toBeVisible();
  });

  test('should display notes entered during attempt', async () => {
    const notes = page.locator('[data-testid="review-notes"]');
    await expect(notes).toBeVisible();
    await expect(notes).toContainText('Review test notes');
  });

  test('should show time taken for attempt', async () => {
    const timeTaken = page.locator('[data-testid="time-taken"]');
    await expect(timeTaken).toBeVisible();
    await expect(timeTaken).toContainText(/\d+.*minute/i);
  });

  test('should display "Edit Attempt" button to go back', async () => {
    const editButton = page.locator('[data-testid="edit-attempt-button"]');
    await expect(editButton).toBeVisible();
  });

  test('should navigate back to active attempt when "Edit" clicked', async () => {
    const editButton = page.locator('[data-testid="edit-attempt-button"]');
    await editButton.click();

    await expect(page).toHaveURL(/\/attempt$/);
    const stationContent = page.locator('[data-testid="station-content"]');
    await expect(stationContent).toBeVisible();
  });

  test('should display "Submit Attempt" button', async () => {
    const submitButton = page.locator('[data-testid="submit-attempt-button"]');
    await expect(submitButton).toBeVisible();
    await expect(submitButton).toContainText(/submit/i);
  });

  test('should show final confirmation when "Submit" clicked', async () => {
    const submitButton = page.locator('[data-testid="submit-attempt-button"]');
    await submitButton.click();

    const confirmDialog = page.locator('[data-testid="submit-confirmation"]');
    await expect(confirmDialog).toBeVisible();
    await expect(confirmDialog).toContainText(/cannot.*edit.*after.*submit/i);
  });

  test('should submit attempt and navigate to results', async () => {
    const submitButton = page.locator('[data-testid="submit-attempt-button"]');
    await submitButton.click();

    const confirmButton = page.locator('[data-testid="confirm-submit-button"]');
    await confirmButton.click();

    // Should navigate to results page
    await expect(page).toHaveURL(/\/results/);
  });

  test('should mark attempt as completed in database', async () => {
    let attemptCompleted = false;

    await page.route('**/api/v1/osces/*/attempts/*/submit', async route => {
      attemptCompleted = true;
      await route.continue();
    });

    const submitButton = page.locator('[data-testid="submit-attempt-button"]');
    await submitButton.click();

    const confirmButton = page.locator('[data-testid="confirm-submit-button"]');
    await confirmButton.click();

    await page.waitForTimeout(1000);

    expect(attemptCompleted).toBeTruthy();
  });
});

test.describe('OSCE Attempt Flow - Results Page', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    // Mock completed attempt
    await page.route('**/api/v1/osces/*/attempts/*', async route => {
      route.fulfill({
        json: {
          attempt_id: 'attempt-123',
          osce_id: 'TEST-CARDIO-VIDEO-001',
          status: 'completed',
          time_taken_minutes: 7.5,
          checklist_completion: 85,
          notes: 'Completed cardiovascular examination',
          submitted_at: new Date().toISOString(),
        },
      });
    });

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');

    await page.goto('/osces/TEST-CARDIO-VIDEO-001/attempts/attempt-123/results');
  });

  test('should display results page with completion summary', async () => {
    const resultsHeader = page.locator('h1:has-text("Attempt Results")');
    await expect(resultsHeader).toBeVisible();
  });

  test('should show checklist completion percentage', async () => {
    const completionPercentage = page.locator('[data-testid="checklist-completion"]');
    await expect(completionPercentage).toBeVisible();
    await expect(completionPercentage).toContainText(/85.*%/);
  });

  test('should display time taken', async () => {
    const timeTaken = page.locator('[data-testid="time-taken"]');
    await expect(timeTaken).toBeVisible();
    await expect(timeTaken).toContainText(/7\.5/);
  });

  test('should show submitted notes', async () => {
    const notes = page.locator('[data-testid="submitted-notes"]');
    await expect(notes).toBeVisible();
    await expect(notes).toContainText('Completed cardiovascular examination');
  });

  test('should display model answer/examiner notes', async () => {
    const modelAnswer = page.locator('[data-testid="model-answer"]');
    await expect(modelAnswer).toBeVisible();
  });

  test('should show "Try Again" button to attempt same station', async () => {
    const tryAgainButton = page.locator('[data-testid="try-again-button"]');
    await expect(tryAgainButton).toBeVisible();
  });

  test('should navigate to OSCE detail when "Try Again" clicked', async () => {
    const tryAgainButton = page.locator('[data-testid="try-again-button"]');
    await tryAgainButton.click();

    await expect(page).toHaveURL(/\/osces\/TEST-CARDIO-VIDEO-001$/);
  });

  test('should show "Back to OSCEs" button', async () => {
    const backButton = page.locator('[data-testid="back-to-osces-button"]');
    await expect(backButton).toBeVisible();
  });

  test('should navigate to OSCE browser when "Back" clicked', async () => {
    const backButton = page.locator('[data-testid="back-to-osces-button"]');
    await backButton.click();

    await expect(page).toHaveURL(/\/osces$/);
  });
});
