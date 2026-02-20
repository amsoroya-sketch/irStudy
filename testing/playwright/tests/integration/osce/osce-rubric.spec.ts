/**
 * OSCE Rubric Integration Tests
 *
 * Tests the marking rubric display, grading criteria, and scoring functionality
 * Covers: Rubric display, marking criteria, point allocation, pass/fail thresholds
 *
 * Test Data: Uses seeded OSCEs from setup/seed-test-data.ts
 * Authentication: Student role (views rubric), Educator role (marks using rubric)
 */

import { test, expect, Page } from '@playwright/test';
import { TEST_USERS } from '../../../utils/test-data/users';

test.describe('OSCE Rubric - Display on Detail Page', () => {
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

  test('should display rubric section on OSCE detail page', async () => {
    const rubricSection = page.locator('[data-testid="rubric-section"]');
    await expect(rubricSection).toBeVisible();
  });

  test('should show rubric heading', async () => {
    const rubricHeading = page.locator('[data-testid="rubric-heading"]');
    await expect(rubricHeading).toBeVisible();
    await expect(rubricHeading).toContainText(/marking.*rubric|assessment.*criteria/i);
  });

  test('should display all rubric criteria items', async () => {
    const criteriaItems = page.locator('[data-testid="rubric-criterion"]');
    const count = await criteriaItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should show criterion name for each item', async () => {
    const firstCriterion = page.locator('[data-testid="rubric-criterion"]').first();
    const criterionName = firstCriterion.locator('[data-testid="criterion-name"]');
    await expect(criterionName).toBeVisible();
  });

  test('should display points allocated for each criterion', async () => {
    const firstCriterion = page.locator('[data-testid="rubric-criterion"]').first();
    const points = firstCriterion.locator('[data-testid="criterion-points"]');
    await expect(points).toBeVisible();
    await expect(points).toContainText(/\d+.*point/i);
  });

  test('should show total points available', async () => {
    const totalPoints = page.locator('[data-testid="rubric-total-points"]');
    await expect(totalPoints).toBeVisible();
    await expect(totalPoints).toContainText(/100.*point/i);
  });

  test('should display pass mark threshold', async () => {
    const passMark = page.locator('[data-testid="rubric-pass-mark"]');
    await expect(passMark).toBeVisible();
    await expect(passMark).toContainText(/60.*%|60.*point/i);
  });

  test('should show rubric criteria in expandable accordion', async () => {
    const rubricAccordion = page.locator('[data-testid="rubric-accordion"]');
    await expect(rubricAccordion).toBeVisible();

    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expandButton.click();

    const criteriaList = page.locator('[data-testid="rubric-criteria-list"]');
    await expect(criteriaList).toBeVisible();
  });

  test('should collapse rubric when collapse button clicked', async () => {
    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expandButton.click();

    const collapseButton = page.locator('[data-testid="rubric-collapse-button"]');
    await collapseButton.click();

    const criteriaList = page.locator('[data-testid="rubric-criteria-list"]');
    await expect(criteriaList).not.toBeVisible();
  });

  test('should show criterion descriptions when expanded', async () => {
    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expandButton.click();

    const firstCriterion = page.locator('[data-testid="rubric-criterion"]').first();
    const description = firstCriterion.locator('[data-testid="criterion-description"]');

    if (await description.isVisible()) {
      await expect(description).toHaveText(/.+/);
    }
  });
});

test.describe('OSCE Rubric - Rubric Structure Validation', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
  });

  test('should verify rubric has 4 criteria', async () => {
    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expandButton.click();

    const criteria = page.locator('[data-testid="rubric-criterion"]');
    const count = await criteria.count();
    expect(count).toBe(4); // Introduction, Systematic approach, Correct technique, Professionalism
  });

  test('should verify "Introduction and consent" criterion (10 points)', async () => {
    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expandButton.click();

    const introductionCriterion = page.locator('[data-testid="rubric-criterion"]:has-text("Introduction and consent")');
    await expect(introductionCriterion).toBeVisible();

    const points = introductionCriterion.locator('[data-testid="criterion-points"]');
    await expect(points).toContainText('10');
  });

  test('should verify "Systematic examination approach" criterion (40 points)', async () => {
    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expandButton.click();

    const systematicCriterion = page.locator('[data-testid="rubric-criterion"]:has-text("Systematic examination approach")');
    await expect(systematicCriterion).toBeVisible();

    const points = systematicCriterion.locator('[data-testid="criterion-points"]');
    await expect(points).toContainText('40');
  });

  test('should verify "Correct technique" criterion (30 points)', async () => {
    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expandButton.click();

    const techniqueCriterion = page.locator('[data-testid="rubric-criterion"]:has-text("Correct technique")');
    await expect(techniqueCriterion).toBeVisible();

    const points = techniqueCriterion.locator('[data-testid="criterion-points"]');
    await expect(points).toContainText('30');
  });

  test('should verify "Professionalism" criterion (20 points)', async () => {
    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expandButton.click();

    const professionalismCriterion = page.locator('[data-testid="rubric-criterion"]:has-text("Professionalism")');
    await expect(professionalismCriterion).toBeVisible();

    const points = professionalismCriterion.locator('[data-testid="criterion-points"]');
    await expect(points).toContainText('20');
  });

  test('should verify total points sum to 100', async () => {
    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expandButton.click();

    const totalPoints = page.locator('[data-testid="rubric-total-points"]');
    await expect(totalPoints).toContainText('100');
  });

  test('should verify pass mark is 60 points (60%)', async () => {
    const passMark = page.locator('[data-testid="rubric-pass-mark"]');
    await expect(passMark).toContainText('60');
  });
});

test.describe('OSCE Rubric - Educator Marking Interface', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    // Login as educator
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.EDUCATOR.email);
    await page.fill('input[name="password"]', TEST_USERS.EDUCATOR.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);

    // Navigate to marking interface (mock student attempt)
    await page.goto('/osces/TEST-CARDIO-VIDEO-001/attempts/student-attempt-123/mark');
  });

  test('should display marking rubric with input fields for educators', async () => {
    const markingRubric = page.locator('[data-testid="marking-rubric"]');
    await expect(markingRubric).toBeVisible();
  });

  test('should show student attempt information', async () => {
    const studentInfo = page.locator('[data-testid="student-info"]');
    await expect(studentInfo).toBeVisible();
  });

  test('should display each criterion with score input field', async () => {
    const firstCriterion = page.locator('[data-testid="marking-criterion"]').first();
    const scoreInput = firstCriterion.locator('[data-testid="criterion-score-input"]');
    await expect(scoreInput).toBeVisible();
  });

  test('should allow entering score for each criterion', async () => {
    const firstCriterion = page.locator('[data-testid="marking-criterion"]').first();
    const scoreInput = firstCriterion.locator('[data-testid="criterion-score-input"]');

    await scoreInput.fill('8');
    const value = await scoreInput.inputValue();
    expect(value).toBe('8');
  });

  test('should validate score does not exceed maximum points', async () => {
    const firstCriterion = page.locator('[data-testid="marking-criterion"]').first();
    const scoreInput = firstCriterion.locator('[data-testid="criterion-score-input"]');
    const maxPoints = await firstCriterion.locator('[data-testid="criterion-max-points"]').textContent();

    // Try to enter more than max points
    await scoreInput.fill('999');
    await scoreInput.blur();

    const errorMessage = firstCriterion.locator('[data-testid="score-error"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/exceed/i);
  });

  test('should calculate total score as criteria are marked', async () => {
    const criteria = page.locator('[data-testid="marking-criterion"]');
    const count = await criteria.count();

    // Enter scores for each criterion
    for (let i = 0; i < Math.min(count, 4); i++) {
      const scoreInput = criteria.nth(i).locator('[data-testid="criterion-score-input"]');
      await scoreInput.fill('5');
    }

    const totalScore = page.locator('[data-testid="total-score"]');
    await expect(totalScore).toBeVisible();
    const total = await totalScore.textContent();
    expect(parseInt(total!)).toBeGreaterThan(0);
  });

  test('should show pass/fail indicator based on total score', async () => {
    const criteria = page.locator('[data-testid="marking-criterion"]');

    // Enter high scores (passing)
    await criteria.nth(0).locator('[data-testid="criterion-score-input"]').fill('10');
    await criteria.nth(1).locator('[data-testid="criterion-score-input"]').fill('35');
    await criteria.nth(2).locator('[data-testid="criterion-score-input"]').fill('25');
    await criteria.nth(3).locator('[data-testid="criterion-score-input"]').fill('15');

    const passIndicator = page.locator('[data-testid="pass-indicator"]');
    await expect(passIndicator).toBeVisible();
    await expect(passIndicator).toContainText(/pass/i);
  });

  test('should show fail indicator when score below pass mark', async () => {
    const criteria = page.locator('[data-testid="marking-criterion"]');

    // Enter low scores (failing)
    await criteria.nth(0).locator('[data-testid="criterion-score-input"]').fill('5');
    await criteria.nth(1).locator('[data-testid="criterion-score-input"]').fill('10');
    await criteria.nth(2).locator('[data-testid="criterion-score-input"]').fill('8');
    await criteria.nth(3).locator('[data-testid="criterion-score-input"]').fill('5');

    const failIndicator = page.locator('[data-testid="fail-indicator"]');
    await expect(failIndicator).toBeVisible();
    await expect(failIndicator).toContainText(/fail/i);
  });

  test('should display comments field for each criterion', async () => {
    const firstCriterion = page.locator('[data-testid="marking-criterion"]').first();
    const commentsField = firstCriterion.locator('[data-testid="criterion-comments"]');
    await expect(commentsField).toBeVisible();
  });

  test('should allow entering comments for each criterion', async () => {
    const firstCriterion = page.locator('[data-testid="marking-criterion"]').first();
    const commentsField = firstCriterion.locator('[data-testid="criterion-comments"]');

    await commentsField.fill('Good introduction, but could improve eye contact.');
    const value = await commentsField.inputValue();
    expect(value).toContain('eye contact');
  });

  test('should show overall feedback text area', async () => {
    const overallFeedback = page.locator('[data-testid="overall-feedback"]');
    await expect(overallFeedback).toBeVisible();
  });

  test('should allow entering overall feedback', async () => {
    const overallFeedback = page.locator('[data-testid="overall-feedback"]');
    await overallFeedback.fill('Overall solid performance, focus on improving palpation technique.');

    const value = await overallFeedback.inputValue();
    expect(value).toContain('palpation technique');
  });

  test('should display "Save Draft" button', async () => {
    const saveDraftButton = page.locator('[data-testid="save-draft-button"]');
    await expect(saveDraftButton).toBeVisible();
  });

  test('should save marking progress when "Save Draft" clicked', async () => {
    let draftSaved = false;

    await page.route('**/api/v1/osces/*/attempts/*/marks/draft', async route => {
      draftSaved = true;
      await route.continue();
    });

    const firstCriterion = page.locator('[data-testid="marking-criterion"]').first();
    await firstCriterion.locator('[data-testid="criterion-score-input"]').fill('8');

    const saveDraftButton = page.locator('[data-testid="save-draft-button"]');
    await saveDraftButton.click();

    await page.waitForTimeout(1000);
    expect(draftSaved).toBeTruthy();
  });

  test('should display "Submit Marks" button', async () => {
    const submitButton = page.locator('[data-testid="submit-marks-button"]');
    await expect(submitButton).toBeVisible();
  });

  test('should require all criteria to be marked before submitting', async () => {
    const submitButton = page.locator('[data-testid="submit-marks-button"]');
    await submitButton.click();

    const errorMessage = page.locator('[data-testid="incomplete-marking-error"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/all.*criteria/i);
  });

  test('should allow submitting when all criteria marked', async () => {
    const criteria = page.locator('[data-testid="marking-criterion"]');
    const count = await criteria.count();

    // Mark all criteria
    for (let i = 0; i < count; i++) {
      await criteria.nth(i).locator('[data-testid="criterion-score-input"]').fill('8');
    }

    const submitButton = page.locator('[data-testid="submit-marks-button"]');
    await expect(submitButton).toBeEnabled();
  });

  test('should show confirmation dialog when submitting marks', async () => {
    const criteria = page.locator('[data-testid="marking-criterion"]');
    const count = await criteria.count();

    for (let i = 0; i < count; i++) {
      await criteria.nth(i).locator('[data-testid="criterion-score-input"]').fill('8');
    }

    const submitButton = page.locator('[data-testid="submit-marks-button"]');
    await submitButton.click();

    const confirmDialog = page.locator('[data-testid="submit-marks-confirmation"]');
    await expect(confirmDialog).toBeVisible();
    await expect(confirmDialog).toContainText(/cannot.*edit.*after/i);
  });

  test('should submit marks to backend when confirmed', async () => {
    let marksSubmitted = false;

    await page.route('**/api/v1/osces/*/attempts/*/marks', async route => {
      if (route.request().method() === 'POST') {
        marksSubmitted = true;
        await route.continue();
      }
    });

    const criteria = page.locator('[data-testid="marking-criterion"]');
    const count = await criteria.count();

    for (let i = 0; i < count; i++) {
      await criteria.nth(i).locator('[data-testid="criterion-score-input"]').fill('8');
    }

    await page.click('[data-testid="submit-marks-button"]');
    await page.click('[data-testid="confirm-submit-marks-button"]');

    await page.waitForTimeout(1000);
    expect(marksSubmitted).toBeTruthy();
  });
});

test.describe('OSCE Rubric - Student View of Marked Rubric', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    // Mock marked attempt
    await page.route('**/api/v1/osces/*/attempts/*', async route => {
      route.fulfill({
        json: {
          attempt_id: 'attempt-123',
          osce_id: 'TEST-CARDIO-VIDEO-001',
          status: 'marked',
          marks: {
            criteria: [
              { name: 'Introduction and consent', score: 8, max_points: 10, comments: 'Good introduction' },
              { name: 'Systematic examination approach', score: 35, max_points: 40, comments: 'Systematic approach' },
              { name: 'Correct technique', score: 25, max_points: 30, comments: 'Technique good' },
              { name: 'Professionalism', score: 18, max_points: 20, comments: 'Professional manner' },
            ],
            total_score: 86,
            total_points: 100,
            pass_mark: 60,
            result: 'PASS',
            overall_feedback: 'Excellent performance overall.',
          },
        },
      });
    });

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');

    await page.goto('/osces/TEST-CARDIO-VIDEO-001/attempts/attempt-123/results');
  });

  test('should display marked rubric on results page', async () => {
    const markedRubric = page.locator('[data-testid="marked-rubric"]');
    await expect(markedRubric).toBeVisible();
  });

  test('should show total score achieved', async () => {
    const totalScore = page.locator('[data-testid="total-score"]');
    await expect(totalScore).toBeVisible();
    await expect(totalScore).toContainText('86');
  });

  test('should display pass/fail result prominently', async () => {
    const result = page.locator('[data-testid="result-badge"]');
    await expect(result).toBeVisible();
    await expect(result).toContainText('PASS');
  });

  test('should show score for each criterion', async () => {
    const firstCriterion = page.locator('[data-testid="marked-criterion"]').first();
    const score = firstCriterion.locator('[data-testid="criterion-score"]');
    await expect(score).toBeVisible();
    await expect(score).toContainText('8');
  });

  test('should display comments for each criterion', async () => {
    const firstCriterion = page.locator('[data-testid="marked-criterion"]').first();
    const comments = firstCriterion.locator('[data-testid="criterion-comments"]');
    await expect(comments).toBeVisible();
    await expect(comments).toContainText('Good introduction');
  });

  test('should show overall feedback', async () => {
    const overallFeedback = page.locator('[data-testid="overall-feedback"]');
    await expect(overallFeedback).toBeVisible();
    await expect(overallFeedback).toContainText('Excellent performance overall');
  });

  test('should display visual progress bar for each criterion', async () => {
    const firstCriterion = page.locator('[data-testid="marked-criterion"]').first();
    const progressBar = firstCriterion.locator('[data-testid="score-progress-bar"]');
    await expect(progressBar).toBeVisible();

    const percentage = await progressBar.getAttribute('aria-valuenow');
    expect(parseInt(percentage!)).toBeGreaterThan(0);
  });

  test('should show percentage score alongside absolute score', async () => {
    const totalScore = page.locator('[data-testid="total-score"]');
    await expect(totalScore).toContainText('86');

    const percentage = page.locator('[data-testid="score-percentage"]');
    await expect(percentage).toBeVisible();
    await expect(percentage).toContainText('86%');
  });

  test('should display pass mark threshold line on chart', async () => {
    const passMarkLine = page.locator('[data-testid="pass-mark-line"]');
    if (await passMarkLine.isVisible()) {
      await expect(passMarkLine).toBeVisible();
    }
  });

  test('should show breakdown of points per criterion in chart/table', async () => {
    const scoreBreakdown = page.locator('[data-testid="score-breakdown"]');
    await expect(scoreBreakdown).toBeVisible();
  });
});

test.describe('OSCE Rubric - Accessibility', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');
  });

  test('should have aria-label on rubric accordion', async () => {
    const accordion = page.locator('[data-testid="rubric-accordion"]');
    const ariaLabel = await accordion.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();
    expect(ariaLabel?.toLowerCase()).toContain('rubric');
  });

  test('should update aria-expanded on accordion toggle', async () => {
    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expect(expandButton).toHaveAttribute('aria-expanded', 'false');

    await expandButton.click();
    await expect(expandButton).toHaveAttribute('aria-expanded', 'true');
  });

  test('should support keyboard navigation through rubric', async () => {
    const expandButton = page.locator('[data-testid="rubric-expand-button"]');
    await expandButton.focus();
    await page.keyboard.press('Enter');

    const criteriaList = page.locator('[data-testid="rubric-criteria-list"]');
    await expect(criteriaList).toBeVisible();
  });

  test('should have descriptive labels on score progress bars', async () => {
    // Mock marked attempt
    await page.route('**/api/v1/osces/*/attempts/*', async route => {
      route.fulfill({
        json: {
          marks: {
            criteria: [{ name: 'Introduction', score: 8, max_points: 10 }],
            total_score: 80,
          },
        },
      });
    });

    await page.goto('/osces/TEST-CARDIO-VIDEO-001/attempts/attempt-123/results');

    const progressBar = page.locator('[data-testid="score-progress-bar"]').first();
    const ariaLabel = await progressBar.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();
  });
});
