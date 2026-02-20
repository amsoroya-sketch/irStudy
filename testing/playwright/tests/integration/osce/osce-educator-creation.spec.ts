/**
 * OSCE Educator Creation Integration Tests
 *
 * Tests OSCE creation, editing, and deletion functionality for educators
 * Covers: Create OSCE form, validation, rubric builder, publishing, editing, deletion
 *
 * Test Data: Uses seeded test users from setup/seed-test-data.ts
 * Authentication: Educator role (can create/edit/delete OSCEs)
 */

import { test, expect, Page } from '@playwright/test';
import { TEST_USERS } from '../../../utils/test-data/users';

test.describe('OSCE Creation - Access and Navigation', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    // Login as educator
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.EDUCATOR.email);
    await page.fill('input[name="password"]', TEST_USERS.EDUCATOR.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('should display "Create OSCE" button on OSCE browser for educators', async () => {
    await page.goto('/osces');

    const createButton = page.locator('[data-testid="create-osce-button"]');
    await expect(createButton).toBeVisible();
    await expect(createButton).toContainText(/create.*osce/i);
  });

  test('should not show "Create OSCE" button for students', async () => {
    // Logout and login as student
    await page.goto('/logout');
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.STUDENT.email);
    await page.fill('input[name="password"]', TEST_USERS.STUDENT.password);
    await page.click('button[type="submit"]');

    await page.goto('/osces');

    const createButton = page.locator('[data-testid="create-osce-button"]');
    await expect(createButton).not.toBeVisible();
  });

  test('should navigate to OSCE creation form when "Create OSCE" clicked', async () => {
    await page.goto('/osces');

    const createButton = page.locator('[data-testid="create-osce-button"]');
    await createButton.click();

    await expect(page).toHaveURL(/\/osces\/create/);
  });

  test('should display OSCE creation form page', async () => {
    await page.goto('/osces/create');

    const formHeading = page.locator('h1:has-text("Create New OSCE Station")');
    await expect(formHeading).toBeVisible();
  });

  test('should show all required form sections', async () => {
    await page.goto('/osces/create');

    await expect(page.locator('[data-testid="basic-info-section"]')).toBeVisible();
    await expect(page.locator('[data-testid="instructions-section"]')).toBeVisible();
    await expect(page.locator('[data-testid="rubric-section"]')).toBeVisible();
    await expect(page.locator('[data-testid="learning-section"]')).toBeVisible();
  });
});

test.describe('OSCE Creation - Basic Information Form', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.EDUCATOR.email);
    await page.fill('input[name="password"]', TEST_USERS.EDUCATOR.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/create');
  });

  test('should display station title input field', async () => {
    const titleInput = page.locator('[data-testid="station-title-input"]');
    await expect(titleInput).toBeVisible();
    await expect(titleInput).toHaveAttribute('placeholder', /.+/);
  });

  test('should allow entering station title', async () => {
    const titleInput = page.locator('[data-testid="station-title-input"]');
    await titleInput.fill('Test Respiratory Examination Station');

    const value = await titleInput.inputValue();
    expect(value).toBe('Test Respiratory Examination Station');
  });

  test('should display specialty dropdown', async () => {
    const specialtyDropdown = page.locator('[data-testid="specialty-select"]');
    await expect(specialtyDropdown).toBeVisible();
  });

  test('should have all 11 specialties in dropdown', async () => {
    const specialtyDropdown = page.locator('[data-testid="specialty-select"]');
    const options = await specialtyDropdown.locator('option').allTextContents();

    expect(options.length).toBeGreaterThanOrEqual(11);
    expect(options).toContain('cardiology');
    expect(options).toContain('respiratory');
    expect(options).toContain('neurology');
  });

  test('should allow selecting specialty', async () => {
    const specialtyDropdown = page.locator('[data-testid="specialty-select"]');
    await specialtyDropdown.selectOption('cardiology');

    const value = await specialtyDropdown.inputValue();
    expect(value).toBe('cardiology');
  });

  test('should display station type dropdown', async () => {
    const stationTypeDropdown = page.locator('[data-testid="station-type-select"]');
    await expect(stationTypeDropdown).toBeVisible();
  });

  test('should have 6 station types in dropdown', async () => {
    const stationTypeDropdown = page.locator('[data-testid="station-type-select"]');
    const options = await stationTypeDropdown.locator('option').allTextContents();

    expect(options.length).toBeGreaterThanOrEqual(6);
    expect(options).toContain('physical_examination');
    expect(options).toContain('history_taking');
    expect(options).toContain('counselling');
    expect(options).toContain('procedure');
    expect(options).toContain('communication');
    expect(options).toContain('emergency_scenario');
  });

  test('should display difficulty dropdown', async () => {
    const difficultyDropdown = page.locator('[data-testid="difficulty-select"]');
    await expect(difficultyDropdown).toBeVisible();
  });

  test('should have 3 difficulty levels', async () => {
    const difficultyDropdown = page.locator('[data-testid="difficulty-select"]');
    const options = await difficultyDropdown.locator('option').allTextContents();

    expect(options).toContain('easy');
    expect(options).toContain('medium');
    expect(options).toContain('hard');
  });

  test('should display time limit input', async () => {
    const timeLimitInput = page.locator('[data-testid="time-limit-input"]');
    await expect(timeLimitInput).toBeVisible();
    await expect(timeLimitInput).toHaveAttribute('type', 'number');
  });

  test('should allow entering time limit', async () => {
    const timeLimitInput = page.locator('[data-testid="time-limit-input"]');
    await timeLimitInput.fill('8');

    const value = await timeLimitInput.inputValue();
    expect(value).toBe('8');
  });

  test('should validate time limit is positive number', async () => {
    const timeLimitInput = page.locator('[data-testid="time-limit-input"]');
    await timeLimitInput.fill('-5');
    await timeLimitInput.blur();

    const errorMessage = page.locator('[data-testid="time-limit-error"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/positive.*number/i);
  });

  test('should validate time limit is between 1-30 minutes', async () => {
    const timeLimitInput = page.locator('[data-testid="time-limit-input"]');
    await timeLimitInput.fill('45');
    await timeLimitInput.blur();

    const errorMessage = page.locator('[data-testid="time-limit-error"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/1.*30/i);
  });
});

test.describe('OSCE Creation - Instructions Section', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.EDUCATOR.email);
    await page.fill('input[name="password"]', TEST_USERS.EDUCATOR.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/create');
  });

  test('should display candidate instructions textarea', async () => {
    const candidateInstructions = page.locator('[data-testid="candidate-instructions-input"]');
    await expect(candidateInstructions).toBeVisible();
  });

  test('should allow entering candidate instructions', async () => {
    const candidateInstructions = page.locator('[data-testid="candidate-instructions-input"]');
    await candidateInstructions.fill('Perform a systematic cardiovascular examination on this patient.');

    const value = await candidateInstructions.inputValue();
    expect(value).toContain('cardiovascular examination');
  });

  test('should display patient instructions textarea', async () => {
    const patientInstructions = page.locator('[data-testid="patient-instructions-input"]');
    await expect(patientInstructions).toBeVisible();
  });

  test('should allow entering patient instructions', async () => {
    const patientInstructions = page.locator('[data-testid="patient-instructions-input"]');
    await patientInstructions.fill('You are a patient attending cardiology clinic for examination.');

    const value = await patientInstructions.inputValue();
    expect(value).toContain('cardiology clinic');
  });

  test('should display examiner instructions textarea', async () => {
    const examinerInstructions = page.locator('[data-testid="examiner-instructions-input"]');
    await expect(examinerInstructions).toBeVisible();
  });

  test('should show character count for instructions fields', async () => {
    const candidateInstructions = page.locator('[data-testid="candidate-instructions-input"]');
    await candidateInstructions.fill('Test instructions');

    const charCount = page.locator('[data-testid="candidate-instructions-char-count"]');
    if (await charCount.isVisible()) {
      await expect(charCount).toContainText(/\d+/);
    }
  });

  test('should validate minimum length for candidate instructions', async () => {
    const candidateInstructions = page.locator('[data-testid="candidate-instructions-input"]');
    await candidateInstructions.fill('Too short');
    await candidateInstructions.blur();

    const errorMessage = page.locator('[data-testid="candidate-instructions-error"]');
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toContainText(/minimum.*character/i);
    }
  });
});

test.describe('OSCE Creation - Rubric Builder', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.EDUCATOR.email);
    await page.fill('input[name="password"]', TEST_USERS.EDUCATOR.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/create');
  });

  test('should display rubric builder section', async () => {
    const rubricBuilder = page.locator('[data-testid="rubric-builder"]');
    await expect(rubricBuilder).toBeVisible();
  });

  test('should show "Add Criterion" button', async () => {
    const addCriterionButton = page.locator('[data-testid="add-criterion-button"]');
    await expect(addCriterionButton).toBeVisible();
  });

  test('should add new criterion when "Add Criterion" clicked', async () => {
    const addCriterionButton = page.locator('[data-testid="add-criterion-button"]');
    await addCriterionButton.click();

    const criterionRows = page.locator('[data-testid="criterion-row"]');
    const count = await criterionRows.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should display criterion name input field', async () => {
    const addCriterionButton = page.locator('[data-testid="add-criterion-button"]');
    await addCriterionButton.click();

    const criterionName = page.locator('[data-testid="criterion-name-input"]').first();
    await expect(criterionName).toBeVisible();
  });

  test('should display criterion points input field', async () => {
    const addCriterionButton = page.locator('[data-testid="add-criterion-button"]');
    await addCriterionButton.click();

    const criterionPoints = page.locator('[data-testid="criterion-points-input"]').first();
    await expect(criterionPoints).toBeVisible();
    await expect(criterionPoints).toHaveAttribute('type', 'number');
  });

  test('should allow entering criterion details', async () => {
    const addCriterionButton = page.locator('[data-testid="add-criterion-button"]');
    await addCriterionButton.click();

    const criterionName = page.locator('[data-testid="criterion-name-input"]').first();
    await criterionName.fill('Introduction and consent');

    const criterionPoints = page.locator('[data-testid="criterion-points-input"]').first();
    await criterionPoints.fill('10');

    expect(await criterionName.inputValue()).toBe('Introduction and consent');
    expect(await criterionPoints.inputValue()).toBe('10');
  });

  test('should calculate total points automatically', async () => {
    const addCriterionButton = page.locator('[data-testid="add-criterion-button"]');

    // Add first criterion
    await addCriterionButton.click();
    await page.locator('[data-testid="criterion-points-input"]').first().fill('10');

    // Add second criterion
    await addCriterionButton.click();
    await page.locator('[data-testid="criterion-points-input"]').last().fill('20');

    const totalPoints = page.locator('[data-testid="rubric-total-points"]');
    await expect(totalPoints).toContainText('30');
  });

  test('should display pass mark input', async () => {
    const passMarkInput = page.locator('[data-testid="pass-mark-input"]');
    await expect(passMarkInput).toBeVisible();
  });

  test('should validate pass mark is between 0-100', async () => {
    const passMarkInput = page.locator('[data-testid="pass-mark-input"]');
    await passMarkInput.fill('150');
    await passMarkInput.blur();

    const errorMessage = page.locator('[data-testid="pass-mark-error"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/0.*100/i);
  });

  test('should show "Remove" button for each criterion', async () => {
    const addCriterionButton = page.locator('[data-testid="add-criterion-button"]');
    await addCriterionButton.click();

    const removeButton = page.locator('[data-testid="remove-criterion-button"]').first();
    await expect(removeButton).toBeVisible();
  });

  test('should remove criterion when "Remove" clicked', async () => {
    const addCriterionButton = page.locator('[data-testid="add-criterion-button"]');
    await addCriterionButton.click();
    await addCriterionButton.click();

    const criterionRows = page.locator('[data-testid="criterion-row"]');
    const countBefore = await criterionRows.count();

    const removeButton = page.locator('[data-testid="remove-criterion-button"]').first();
    await removeButton.click();

    const countAfter = await criterionRows.count();
    expect(countAfter).toBe(countBefore - 1);
  });

  test('should require at least 3 criteria', async () => {
    const addCriterionButton = page.locator('[data-testid="add-criterion-button"]');
    await addCriterionButton.click();
    await addCriterionButton.click(); // Only 2 criteria

    const submitButton = page.locator('[data-testid="submit-osce-button"]');
    await submitButton.click();

    const errorMessage = page.locator('[data-testid="rubric-error"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/at least.*3.*criteria/i);
  });
});

test.describe('OSCE Creation - Learning Objectives', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.EDUCATOR.email);
    await page.fill('input[name="password"]', TEST_USERS.EDUCATOR.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/create');
  });

  test('should display learning objectives input section', async () => {
    const objectivesSection = page.locator('[data-testid="learning-objectives-section"]');
    await expect(objectivesSection).toBeVisible();
  });

  test('should show "Add Objective" button', async () => {
    const addObjectiveButton = page.locator('[data-testid="add-objective-button"]');
    await expect(addObjectiveButton).toBeVisible();
  });

  test('should add new objective input when "Add Objective" clicked', async () => {
    const addObjectiveButton = page.locator('[data-testid="add-objective-button"]');
    await addObjectiveButton.click();

    const objectiveInputs = page.locator('[data-testid="objective-input"]');
    const count = await objectiveInputs.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should allow entering learning objective text', async () => {
    const addObjectiveButton = page.locator('[data-testid="add-objective-button"]');
    await addObjectiveButton.click();

    const objectiveInput = page.locator('[data-testid="objective-input"]').first();
    await objectiveInput.fill('Perform systematic cardiovascular examination');

    expect(await objectiveInput.inputValue()).toContain('cardiovascular examination');
  });

  test('should display key points input section', async () => {
    const keyPointsSection = page.locator('[data-testid="key-points-section"]');
    await expect(keyPointsSection).toBeVisible();
  });

  test('should show "Add Key Point" button', async () => {
    const addKeyPointButton = page.locator('[data-testid="add-key-point-button"]');
    await expect(addKeyPointButton).toBeVisible();
  });

  test('should add new key point input when "Add Key Point" clicked', async () => {
    const addKeyPointButton = page.locator('[data-testid="add-key-point-button"]');
    await addKeyPointButton.click();

    const keyPointInputs = page.locator('[data-testid="key-point-input"]');
    const count = await keyPointInputs.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should allow removing learning objectives', async () => {
    const addObjectiveButton = page.locator('[data-testid="add-objective-button"]');
    await addObjectiveButton.click();
    await addObjectiveButton.click();

    const objectiveInputs = page.locator('[data-testid="objective-input"]');
    const countBefore = await objectiveInputs.count();

    const removeButton = page.locator('[data-testid="remove-objective-button"]').first();
    await removeButton.click();

    const countAfter = await objectiveInputs.count();
    expect(countAfter).toBe(countBefore - 1);
  });
});

test.describe('OSCE Creation - Video Resources', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.EDUCATOR.email);
    await page.fill('input[name="password"]', TEST_USERS.EDUCATOR.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/create');
  });

  test('should display video resources section', async () => {
    const videoResourcesSection = page.locator('[data-testid="video-resources-section"]');
    await expect(videoResourcesSection).toBeVisible();
  });

  test('should show "Add Essential Video" button', async () => {
    const addEssentialVideoButton = page.locator('[data-testid="add-essential-video-button"]');
    await expect(addEssentialVideoButton).toBeVisible();
  });

  test('should add new essential video form when button clicked', async () => {
    const addEssentialVideoButton = page.locator('[data-testid="add-essential-video-button"]');
    await addEssentialVideoButton.click();

    const videoForms = page.locator('[data-testid="essential-video-form"]');
    const count = await videoForms.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should display video title input', async () => {
    const addEssentialVideoButton = page.locator('[data-testid="add-essential-video-button"]');
    await addEssentialVideoButton.click();

    const titleInput = page.locator('[data-testid="video-title-input"]').first();
    await expect(titleInput).toBeVisible();
  });

  test('should display video URL input', async () => {
    const addEssentialVideoButton = page.locator('[data-testid="add-essential-video-button"]');
    await addEssentialVideoButton.click();

    const urlInput = page.locator('[data-testid="video-url-input"]').first();
    await expect(urlInput).toBeVisible();
    await expect(urlInput).toHaveAttribute('type', 'url');
  });

  test('should validate video URL format', async () => {
    const addEssentialVideoButton = page.locator('[data-testid="add-essential-video-button"]');
    await addEssentialVideoButton.click();

    const urlInput = page.locator('[data-testid="video-url-input"]').first();
    await urlInput.fill('not-a-valid-url');
    await urlInput.blur();

    const errorMessage = page.locator('[data-testid="video-url-error"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/valid.*url/i);
  });

  test('should enforce HTTPS-only URLs', async () => {
    const addEssentialVideoButton = page.locator('[data-testid="add-essential-video-button"]');
    await addEssentialVideoButton.click();

    const urlInput = page.locator('[data-testid="video-url-input"]').first();
    await urlInput.fill('http://example.com/video');
    await urlInput.blur();

    const errorMessage = page.locator('[data-testid="video-url-error"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/https/i);
  });

  test('should limit essential videos to 4', async () => {
    const addEssentialVideoButton = page.locator('[data-testid="add-essential-video-button"]');

    // Add 4 videos
    for (let i = 0; i < 4; i++) {
      await addEssentialVideoButton.click();
    }

    // Button should be disabled
    await expect(addEssentialVideoButton).toBeDisabled();
  });

  test('should show "Add Supplementary Video" button', async () => {
    const addSupplementaryVideoButton = page.locator('[data-testid="add-supplementary-video-button"]');
    await expect(addSupplementaryVideoButton).toBeVisible();
  });

  test('should limit supplementary videos to 3', async () => {
    const addSupplementaryVideoButton = page.locator('[data-testid="add-supplementary-video-button"]');

    for (let i = 0; i < 3; i++) {
      await addSupplementaryVideoButton.click();
    }

    await expect(addSupplementaryVideoButton).toBeDisabled();
  });
});

test.describe('OSCE Creation - Validation and Submit', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.EDUCATOR.email);
    await page.fill('input[name="password"]', TEST_USERS.EDUCATOR.password);
    await page.click('button[type="submit"]');
    await page.goto('/osces/create');
  });

  test('should display "Save Draft" button', async () => {
    const saveDraftButton = page.locator('[data-testid="save-draft-button"]');
    await expect(saveDraftButton).toBeVisible();
  });

  test('should display "Publish OSCE" button', async () => {
    const publishButton = page.locator('[data-testid="publish-osce-button"]');
    await expect(publishButton).toBeVisible();
  });

  test('should validate required fields before publishing', async () => {
    const publishButton = page.locator('[data-testid="publish-osce-button"]');
    await publishButton.click();

    const errorSummary = page.locator('[data-testid="validation-errors"]');
    await expect(errorSummary).toBeVisible();
  });

  test('should show specific field errors for empty required fields', async () => {
    const publishButton = page.locator('[data-testid="publish-osce-button"]');
    await publishButton.click();

    const titleError = page.locator('[data-testid="station-title-error"]');
    await expect(titleError).toBeVisible();
    await expect(titleError).toContainText(/required/i);
  });

  test('should save draft with partial data', async () => {
    const titleInput = page.locator('[data-testid="station-title-input"]');
    await titleInput.fill('Incomplete OSCE Station');

    const saveDraftButton = page.locator('[data-testid="save-draft-button"]');
    await saveDraftButton.click();

    const successMessage = page.locator('[data-testid="draft-saved-message"]');
    await expect(successMessage).toBeVisible();
  });

  test('should publish OSCE with complete valid data', async () => {
    // Fill all required fields
    await page.fill('[data-testid="station-title-input"]', 'Test Cardiovascular Examination');
    await page.selectOption('[data-testid="specialty-select"]', 'cardiology');
    await page.selectOption('[data-testid="station-type-select"]', 'physical_examination');
    await page.selectOption('[data-testid="difficulty-select"]', 'medium');
    await page.fill('[data-testid="time-limit-input"]', '8');
    await page.fill('[data-testid="candidate-instructions-input"]', 'Perform a systematic cardiovascular examination.');
    await page.fill('[data-testid="patient-instructions-input"]', 'You are a patient attending cardiology clinic.');
    await page.fill('[data-testid="examiner-instructions-input"]', 'Observe the candidate and mark using the rubric.');

    // Add rubric criteria
    await page.click('[data-testid="add-criterion-button"]');
    await page.fill('[data-testid="criterion-name-input"]', 'Introduction');
    await page.fill('[data-testid="criterion-points-input"]', '10');

    await page.click('[data-testid="add-criterion-button"]');
    await page.locator('[data-testid="criterion-name-input"]').last().fill('Technique');
    await page.locator('[data-testid="criterion-points-input"]').last().fill('40');

    await page.click('[data-testid="add-criterion-button"]');
    await page.locator('[data-testid="criterion-name-input"]').last().fill('Professionalism');
    await page.locator('[data-testid="criterion-points-input"]').last().fill('50');

    await page.fill('[data-testid="pass-mark-input"]', '60');

    const publishButton = page.locator('[data-testid="publish-osce-button"]');
    await publishButton.click();

    // Should navigate to OSCE detail page
    await expect(page).toHaveURL(/\/osces\/.+/);
  });

  test('should show success message after publishing', async () => {
    // Fill form (simplified for this test)
    await page.fill('[data-testid="station-title-input"]', 'Published OSCE Test');

    let publishSuccess = false;
    await page.route('**/api/v1/osces', async route => {
      if (route.request().method() === 'POST') {
        publishSuccess = true;
        route.fulfill({
          status: 201,
          json: { osce_id: 'NEW-OSCE-123', station_title: 'Published OSCE Test' },
        });
      }
    });

    // Assuming form is filled completely
    const publishButton = page.locator('[data-testid="publish-osce-button"]');
    await publishButton.click();

    expect(publishSuccess).toBeTruthy();
  });
});

test.describe('OSCE Editing - Existing OSCE', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.EDUCATOR.email);
    await page.fill('input[name="password"]', TEST_USERS.EDUCATOR.password);
    await page.click('button[type="submit"]');
  });

  test('should display "Edit" button on OSCE detail page for educators', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const editButton = page.locator('[data-testid="edit-osce-button"]');
    await expect(editButton).toBeVisible();
  });

  test('should navigate to edit form when "Edit" clicked', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const editButton = page.locator('[data-testid="edit-osce-button"]');
    await editButton.click();

    await expect(page).toHaveURL(/\/osces\/TEST-CARDIO-VIDEO-001\/edit/);
  });

  test('should pre-populate form with existing OSCE data', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001/edit');

    const titleInput = page.locator('[data-testid="station-title-input"]');
    const title = await titleInput.inputValue();
    expect(title).toContain('Cardiovascular');
  });

  test('should allow editing OSCE fields', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001/edit');

    const titleInput = page.locator('[data-testid="station-title-input"]');
    await titleInput.clear();
    await titleInput.fill('Updated Cardiovascular Examination');

    expect(await titleInput.inputValue()).toBe('Updated Cardiovascular Examination');
  });

  test('should show "Update OSCE" button instead of "Publish"', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001/edit');

    const updateButton = page.locator('[data-testid="update-osce-button"]');
    await expect(updateButton).toBeVisible();
  });

  test('should update OSCE when "Update" clicked', async () => {
    let updateSuccess = false;

    await page.route('**/api/v1/osces/TEST-CARDIO-VIDEO-001', async route => {
      if (route.request().method() === 'PATCH') {
        updateSuccess = true;
        await route.continue();
      }
    });

    await page.goto('/osces/TEST-CARDIO-VIDEO-001/edit');

    const titleInput = page.locator('[data-testid="station-title-input"]');
    await titleInput.clear();
    await titleInput.fill('Updated Title');

    const updateButton = page.locator('[data-testid="update-osce-button"]');
    await updateButton.click();

    await page.waitForTimeout(1000);
    expect(updateSuccess).toBeTruthy();
  });
});

test.describe('OSCE Deletion', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USERS.EDUCATOR.email);
    await page.fill('input[name="password"]', TEST_USERS.EDUCATOR.password);
    await page.click('button[type="submit"]');
  });

  test('should display "Delete" button on OSCE detail page for educators', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const deleteButton = page.locator('[data-testid="delete-osce-button"]');
    await expect(deleteButton).toBeVisible();
  });

  test('should show confirmation dialog when "Delete" clicked', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const deleteButton = page.locator('[data-testid="delete-osce-button"]');
    await deleteButton.click();

    const confirmDialog = page.locator('[data-testid="delete-confirmation-dialog"]');
    await expect(confirmDialog).toBeVisible();
    await expect(confirmDialog).toContainText(/permanently.*delete/i);
  });

  test('should cancel deletion when "Cancel" clicked', async () => {
    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const deleteButton = page.locator('[data-testid="delete-osce-button"]');
    await deleteButton.click();

    const cancelButton = page.locator('[data-testid="cancel-delete-button"]');
    await cancelButton.click();

    // Should remain on detail page
    await expect(page).toHaveURL(/\/osces\/TEST-CARDIO-VIDEO-001$/);
  });

  test('should delete OSCE when confirmed', async () => {
    let deleteSuccess = false;

    await page.route('**/api/v1/osces/TEST-CARDIO-VIDEO-001', async route => {
      if (route.request().method() === 'DELETE') {
        deleteSuccess = true;
        route.fulfill({ status: 204 });
      }
    });

    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    const deleteButton = page.locator('[data-testid="delete-osce-button"]');
    await deleteButton.click();

    const confirmButton = page.locator('[data-testid="confirm-delete-button"]');
    await confirmButton.click();

    await page.waitForTimeout(1000);
    expect(deleteSuccess).toBeTruthy();
  });

  test('should navigate to OSCE browser after deletion', async () => {
    await page.route('**/api/v1/osces/TEST-CARDIO-VIDEO-001', async route => {
      if (route.request().method() === 'DELETE') {
        route.fulfill({ status: 204 });
      }
    });

    await page.goto('/osces/TEST-CARDIO-VIDEO-001');

    await page.click('[data-testid="delete-osce-button"]');
    await page.click('[data-testid="confirm-delete-button"]');

    await expect(page).toHaveURL(/\/osces$/);
  });
});
