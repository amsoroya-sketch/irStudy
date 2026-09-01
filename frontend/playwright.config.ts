import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright config for frontend e2e tests (PRD-EMR-PRACTICE-003).
 *
 * Only picks up *.spec.ts under tests/ so it never collides with the Vitest
 * component tests (*.test.tsx). Runs against the seeded dev stack; the base URL
 * is configurable via PLAYWRIGHT_BASE_URL (defaults to the Vite dev server).
 */
export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: 'list',
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
