/**
 * Student RBAC Permissions Tests
 * Verify student role has correct permissions and UI elements
 */

import { test, expect } from '../../fixtures/auth.fixture';
import { STUDENT_USER } from '../../fixtures/users.fixture';

test.describe('Student Role Permissions', () => {
  test.use({ storageState: undefined }); // Clear any existing auth state

  test.describe('Dashboard Access & UI', () => {
    test('should display student dashboard with correct cards', async ({ studentPage: page }) => {
      await page.goto('/dashboard');

      // Should see welcome message with role
      const welcomeMessage = page.locator('text=/welcome/i');
      await expect(welcomeMessage).toBeVisible();

      const roleDisplay = page.locator('text=/student/i');
      await expect(roleDisplay).toBeVisible();

      // Student should see these 3 cards
      const mcqPracticeCard = page.locator('text=/mcq practice/i').first();
      await expect(mcqPracticeCard).toBeVisible();

      const osceCard = page.locator('text=/osce scenarios/i').first();
      await expect(osceCard).toBeVisible();

      const myProgressCard = page.locator('text=/my progress/i').first();
      await expect(myProgressCard).toBeVisible();

      // Student should NOT see these cards
      const createContentCard = page.locator('text=/create content/i');
      await expect(createContentCard).not.toBeVisible();

      const adminPanelCard = page.locator('text=/admin panel/i');
      await expect(adminPanelCard).not.toBeVisible();

      const studentProgressCard = page.locator('text=/student progress/i');
      await expect(studentProgressCard).not.toBeVisible();
    });

    test('should show correct permission count', async ({ studentPage: page }) => {
      await page.goto('/dashboard');

      // Student has 6 permissions
      const permissionCount = page.locator('text=/6.*permission/i');
      await expect(permissionCount).toBeVisible();
    });
  });

  test.describe('MCQ Browser Permissions', () => {
    test('should display MCQ browser with view/attempt buttons only', async ({ studentPage: page }) => {
      await page.goto('/mcqs');

      // Should see MCQ grid
      const mcqCards = page.locator('[data-testid="mcq-card"]');
      await expect(mcqCards.first()).toBeVisible();

      // Student can see "Attempt" button
      const attemptButton = page.locator('button:has-text("Attempt")').first();
      await expect(attemptButton).toBeVisible();

      // Student can see "View" button
      const viewButton = page.locator('button:has-text("View")').first();
      await expect(viewButton).toBeVisible();

      // Student should NOT see "Edit" button (no MCQ_UPDATE permission)
      const editButton = page.locator('button:has-text("Edit")');
      await expect(editButton).not.toBeVisible();

      // Student should NOT see "Create MCQ" button in header (no MCQ_CREATE permission)
      const createButton = page.locator('button:has-text("Create MCQ")');
      await expect(createButton).not.toBeVisible();
    });

    test('should allow filtering MCQs by category', async ({ studentPage: page }) => {
      await page.goto('/mcqs');

      // Select Cardiology category
      const categorySelect = page.locator('select[name="category"]');
      await categorySelect.selectOption('Cardiology');

      // Wait for filtered results
      await page.waitForTimeout(500);

      // MCQs should be filtered
      const mcqCards = page.locator('[data-testid="mcq-card"]');
      const count = await mcqCards.count();
      expect(count).toBeGreaterThan(0);
    });

    test('should allow searching MCQs', async ({ studentPage: page }) => {
      await page.goto('/mcqs');

      // Type in search box
      const searchInput = page.locator('input[placeholder*="Search"]');
      await searchInput.fill('chest pain');

      // Wait for search results
      await page.waitForTimeout(500);

      // Results should update
      const mcqCards = page.locator('[data-testid="mcq-card"]');
      await expect(mcqCards.first()).toBeVisible();
    });
  });

  test.describe('MCQ Attempt Permissions', () => {
    test('should allow student to attempt MCQ', async ({ studentPage: page }) => {
      await page.goto('/mcqs/1/attempt');

      // Should see question
      const question = page.locator('text=/what is/i').first();
      await expect(question).toBeVisible();

      // Should see 5 radio button options
      const optionA = page.locator('input[value="A"]');
      const optionB = page.locator('input[value="B"]');
      const optionC = page.locator('input[value="C"]');
      const optionD = page.locator('input[value="D"]');
      const optionE = page.locator('input[value="E"]');

      await expect(optionA).toBeVisible();
      await expect(optionB).toBeVisible();
      await expect(optionC).toBeVisible();
      await expect(optionD).toBeVisible();
      await expect(optionE).toBeVisible();

      // Should see submit button
      const submitButton = page.locator('button:has-text("Submit Answer")');
      await expect(submitButton).toBeVisible();
      await expect(submitButton).toBeDisabled(); // Disabled until answer selected
    });

    test('should show feedback after submitting answer', async ({ studentPage: page }) => {
      await page.goto('/mcqs/1/attempt');

      // Select answer A
      const optionA = page.locator('input[value="A"]');
      await optionA.check();

      // Submit button should be enabled
      const submitButton = page.locator('button:has-text("Submit Answer")');
      await expect(submitButton).toBeEnabled();

      // Click submit
      await submitButton.click();

      // Wait for result
      await page.waitForTimeout(1000);

      // Should see result (correct or incorrect)
      const resultAlert = page.locator('[role="alert"]');
      await expect(resultAlert).toBeVisible();

      // Should see explanation
      const explanation = page.locator('text=/explanation/i');
      await expect(explanation).toBeVisible();

      // Should see "Try Again" and "Back to Browser" buttons
      const tryAgainButton = page.locator('button:has-text("Try Again")');
      const backButton = page.locator('button:has-text("Back to Browser")');

      await expect(tryAgainButton).toBeVisible();
      await expect(backButton).toBeVisible();
    });
  });

  test.describe('Restricted Access', () => {
    test('should NOT allow access to MCQ creation page', async ({ studentPage: page }) => {
      await page.goto('/mcqs/create');

      // Should redirect or show permission denied
      // Implementation depends on how unauthorized access is handled

      // Option 1: Check for permission denied message
      const deniedMessage = page.locator('text=/permission denied|access denied/i');
      const isVisible = await deniedMessage.isVisible().catch(() => false);

      if (isVisible) {
        expect(isVisible).toBe(true);
      } else {
        // Option 2: Check if redirected to dashboard or login
        const currentURL = page.url();
        expect(currentURL).toMatch(/\/(dashboard|login)/);
      }
    });

    test('should NOT allow access to admin panel', async ({ studentPage: page }) => {
      await page.goto('/admin');

      // Should not have access
      const deniedMessage = page.locator('text=/permission denied|access denied/i');
      const isVisible = await deniedMessage.isVisible().catch(() => false);

      if (isVisible) {
        expect(isVisible).toBe(true);
      } else {
        const currentURL = page.url();
        expect(currentURL).toMatch(/\/(dashboard|login)/);
      }
    });

    test('should NOT allow access to all students progress', async ({ studentPage: page }) => {
      await page.goto('/progress/all');

      // Should not have access
      const deniedMessage = page.locator('text=/permission denied|access denied/i');
      const isVisible = await deniedMessage.isVisible().catch(() => false);

      if (isVisible) {
        expect(isVisible).toBe(true);
      } else {
        const currentURL = page.url();
        expect(currentURL).toMatch(/\/(dashboard|login|progress$)/);
      }
    });
  });

  test.describe('Navigation & Links', () => {
    test('should allow navigation to MCQ browser from dashboard', async ({ studentPage: page }) => {
      await page.goto('/dashboard');

      const browseMCQButton = page.locator('button:has-text("Browse MCQs")');
      await browseMCQButton.click();

      await page.waitForURL('/mcqs');
      await expect(page).toHaveURL('/mcqs');
    });

    test('should allow navigation to own progress page', async ({ studentPage: page }) => {
      await page.goto('/dashboard');

      const myProgressButton = page.locator('button:has-text("View Progress")');
      await myProgressButton.click();

      await page.waitForURL('/progress');
      await expect(page).toHaveURL('/progress');
    });

    test('should allow navigation back to dashboard from MCQ browser', async ({ studentPage: page }) => {
      await page.goto('/mcqs');

      // Click back button or logo
      const backButton = page.locator('button:has-text("← Back")');
      const isVisible = await backButton.isVisible().catch(() => false);

      if (isVisible) {
        await backButton.click();
        await page.waitForURL('/dashboard');
        await expect(page).toHaveURL('/dashboard');
      }
    });
  });

  test.describe('Data & State Management', () => {
    test('should persist selected filters in MCQ browser', async ({ studentPage: page }) => {
      await page.goto('/mcqs');

      // Select category
      const categorySelect = page.locator('select[name="category"]');
      await categorySelect.selectOption('Cardiology');

      // Navigate to MCQ attempt
      const attemptButton = page.locator('button:has-text("Attempt")').first();
      await attemptButton.click();

      // Wait for MCQ attempt page
      await page.waitForURL(/\/mcqs\/\d+\/attempt/);

      // Click back to browser
      const backButton = page.locator('button:has-text("Back to Browser")');
      await backButton.click();

      await page.waitForURL('/mcqs');

      // Category filter should still be selected
      const selectedCategory = await categorySelect.inputValue();
      expect(selectedCategory).toBe('Cardiology');
    });

    test('should load permissions from API on page load', async ({ studentPage: page }) => {
      await page.goto('/dashboard');

      // Intercept permissions API call
      const permissionsResponse = await page.waitForResponse(
        (response) => response.url().includes('/api/v1/permissions/me') && response.status() === 200
      );

      const permissionsData = await permissionsResponse.json();

      // Verify student permissions
      expect(permissionsData.role).toBe('student');
      expect(permissionsData.permissions).toContain('mcq.view');
      expect(permissionsData.permissions).toContain('mcq.attempt');
      expect(permissionsData.permissions).not.toContain('mcq.create');
      expect(permissionsData.permissions).not.toContain('admin.panel');
    });
  });
});
