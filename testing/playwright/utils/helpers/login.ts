/**
 * Test Helper: Login
 * Reusable login function for integration tests
 */

import { Page, expect } from '@playwright/test';

export interface LoginCredentials {
  email: string;
  password: string;
}

/**
 * Perform login and wait for redirect to dashboard
 *
 * This function handles the form validation requirements:
 * - Fills email and triggers blur to validate
 * - Fills password and triggers blur to validate
 * - Waits for submit button to be enabled
 * - Clicks submit and waits for dashboard redirect
 *
 * @param page - Playwright Page object
 * @param credentials - User credentials (email, password)
 */
export async function login(page: Page, credentials: LoginCredentials): Promise<void> {
  await page.goto('/login');

  // Fill and blur email to trigger validation
  const emailInput = page.locator('input[name="email"]');
  await emailInput.fill(credentials.email);
  await emailInput.blur();

  // Fill and blur password to trigger validation
  const passwordInput = page.locator('input[name="password"]');
  await passwordInput.fill(credentials.password);
  await passwordInput.blur();

  // Wait for button to be enabled, then click
  const submitButton = page.locator('button[type="submit"]');
  await expect(submitButton).toBeEnabled({ timeout: 5000 });
  await submitButton.click();

  // Wait for redirect to dashboard
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
}
