import { test, expect } from '../fixtures/auth.fixture';

test('debug html notes page', async ({ studentPage: page }) => {
  const consoleLogs: string[] = [];
  page.on('console', msg => {
    const text = msg.text();
    consoleLogs.push(`[${msg.type()}] ${text}`);
    console.log(`[${msg.type()}] ${text}`);
  });
  page.on('pageerror', error => {
    console.log('[PAGE ERROR]', error.message);
  });

  await page.goto('/html-notes');
  await page.waitForTimeout(5000);

  console.log('CONSOLE LOGS COUNT:', consoleLogs.length);
});
