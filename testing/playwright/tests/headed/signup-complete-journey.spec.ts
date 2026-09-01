/**
 * Headed UI Test: Complete User Journey Starting from Signup
 *
 * This test runs against the REAL backend (localhost:8001) and frontend (localhost:5173)
 * in HEADED mode so you can watch the browser automation live.
 *
 * Run with:
 *   npx playwright test tests/headed/signup-complete-journey.spec.ts --headed --project=chromium
 *
 * Or with xvfb for virtual display:
 *   xvfb-run npx playwright test tests/headed/signup-complete-journey.spec.ts --headed --project=chromium
 */

import { test, expect, Page } from '@playwright/test';

// Static test user (shared across the journey)
const TEST_USER = {
  fullName: `Headed User ${Date.now()}`,
  email: `headed.user.${Date.now()}@medical.edu.au`,
  password: 'SecurePass123!',
};

/**
 * Helper: Fill MUI TextField by clicking, typing, then blurring
 */
async function fillMuiField(page: Page, label: string, value: string) {
  const input = page.getByRole('textbox', { name: label, exact: true });
  await input.click();
  await input.fill(value);
  await input.blur();
  // Give React state a moment to update
  await page.waitForTimeout(300);
}

test('🎭 Headed: Complete User Journey (Signup → Dashboard → Modules)', async ({ page }) => {
  test.setTimeout(120000); // 2 minutes for full journey
  console.log(`\n🧪 Starting headed journey for: ${TEST_USER.email}`);

  // ═══════════════════════════════════════════════════════════════
  // STEP 1: SIGNUP
  // ═══════════════════════════════════════════════════════════════
  console.log('\n📍 STEP 1: Signup');
  await page.goto('/register');
  await expect(page.getByRole('heading', { name: 'Create Account' })).toBeVisible();

  await fillMuiField(page, 'Full Name', TEST_USER.fullName);
  await fillMuiField(page, 'Email Address', TEST_USER.email);
  await fillMuiField(page, 'Password', TEST_USER.password);
  await fillMuiField(page, 'Confirm Password', TEST_USER.password);
  await page.locator('input[name="acceptTerms"]').check();

  await page.locator('button[type="submit"]').click();
  await expect(page.locator('text=/Registration successful/i')).toBeVisible({ timeout: 10000 });
  await page.screenshot({ path: 'test-results/headed/01-signup-success.png' });
  console.log('✅ Signup successful');

  // Verify email in database so login works (email verification gate)
  console.log('📧 Verifying email in database...');
  const { execSync } = require('child_process');
  execSync(
    `PGPASSWORD=3K4cnsyxYOOHGzCcxmOesU7PExXHCMaH psql -h localhost -p 5433 -U postgres -d irstudy_medical -c "UPDATE users SET is_verified = true WHERE email = '${TEST_USER.email}';"`,
    { stdio: 'ignore' }
  );
  console.log('✅ Email verified in DB');

  // ═══════════════════════════════════════════════════════════════
  // STEP 2: LOGIN
  // ═══════════════════════════════════════════════════════════════
  console.log('\n📍 STEP 2: Login');
  await page.goto('/login');
  await expect(page.locator('button:has-text("Sign In")')).toBeVisible();

  await fillMuiField(page, 'Email Address', TEST_USER.email);
  await fillMuiField(page, 'Password', TEST_USER.password);
  await page.locator('button[type="submit"]').click();

  await page.waitForURL('/dashboard', { timeout: 15000 });
  await expect(page).toHaveURL('/dashboard');

  const accessToken = await page.evaluate(() => localStorage.getItem('accessToken'));
  expect(accessToken).toBeTruthy();

  await page.screenshot({ path: 'test-results/headed/02-login-dashboard.png', fullPage: true });
  console.log('✅ Login successful, on dashboard');

  // ═══════════════════════════════════════════════════════════════
  // STEP 3: DASHBOARD NAVIGATION
  // ═══════════════════════════════════════════════════════════════
  console.log('\n📍 STEP 3: Dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' }).first()).toBeVisible({ timeout: 10000 });
  await page.screenshot({ path: 'test-results/headed/03-dashboard.png', fullPage: true });
  console.log('✅ Dashboard verified');

  // ═══════════════════════════════════════════════════════════════
  // STEP 4: MCQ BROWSER
  // ═══════════════════════════════════════════════════════════════
  console.log('\n📍 STEP 4: MCQ Browser');
  await page.goto('/mcqs');
  await expect(page).toHaveURL('/mcqs');
  await page.screenshot({ path: 'test-results/headed/04-mcq-browser.png', fullPage: true });
  console.log('✅ MCQ browser verified');

  // ═══════════════════════════════════════════════════════════════
  // STEP 5: OSCE PRACTICE
  // ═══════════════════════════════════════════════════════════════
  console.log('\n📍 STEP 5: OSCE Practice');
  await page.goto('/osce-practice');
  await expect(page).toHaveURL('/osce-practice');
  await page.screenshot({ path: 'test-results/headed/05-osce-practice.png', fullPage: true });
  console.log('✅ OSCE practice verified');

  // ═══════════════════════════════════════════════════════════════
  // STEP 6: EMR MODULE
  // ═══════════════════════════════════════════════════════════════
  console.log('\n📍 STEP 6: EMR Start');
  await page.goto('/emr/start');
  await expect(page).toHaveURL('/emr/start');
  await page.screenshot({ path: 'test-results/headed/06-emr-start.png', fullPage: true });
  console.log('✅ EMR start verified');

  // ═══════════════════════════════════════════════════════════════
  // STEP 7: PERFORMANCE DASHBOARD
  // ═══════════════════════════════════════════════════════════════
  console.log('\n📍 STEP 7: Performance Dashboard');
  await page.goto('/performance');
  await expect(page).toHaveURL('/performance');
  await page.screenshot({ path: 'test-results/headed/07-performance.png', fullPage: true });
  console.log('✅ Performance dashboard verified');

  // ═══════════════════════════════════════════════════════════════
  // STEP 8: LOGOUT
  // ═══════════════════════════════════════════════════════════════
  console.log('\n📍 STEP 8: Logout');
  // Clear auth tokens and navigate to a protected route
  // to verify redirect to login page
  await page.evaluate(() => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  });
  // Navigate to protected route - should redirect to login
  await page.goto('/dashboard');
  await page.waitForURL('/login', { timeout: 10000 });
  await expect(page).toHaveURL('/login');
  await page.screenshot({ path: 'test-results/headed/08-logout.png' });
  console.log('✅ Logout successful');

  console.log('\n🎉 FULL JOURNEY COMPLETE');
});
