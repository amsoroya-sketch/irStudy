/**
 * Playwright API Mocking Fixtures
 * Uses native page.route() for reliable request interception
 */

import { test as base, Page } from '@playwright/test';

const API_BASE_URL = 'http://localhost:8000/api/v1';

interface MockApiFixtures {
  mockApi: void;
}

/**
 * Mock API responses for authentication and RBAC testing
 */
export const test = base.extend<MockApiFixtures>({
  mockApi: [async ({ page }, use) => {
    console.log('[Mock API] Setting up request interception...');

    // Mock login endpoint
    await page.route(`${API_BASE_URL}/auth/login`, async (route, request) => {
      console.log('[Mock API] Intercepted login request');

      const body = request.postDataJSON();
      console.log('[Mock API] Login credentials:', body.email);

      // Mock student login
      if (body.email === 'student@test.com' && body.password === 'Student123!@#') {
        console.log('[Mock API] Returning student credentials');
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            access_token: 'mock-student-access-token',
            refresh_token: 'mock-student-refresh-token',
            token_type: 'bearer',
            user: {
              id: 1,
              email: 'student@test.com',
              full_name: 'Test Student',
              role: 'student',
              is_verified: true,
              is_active: true,
              created_at: new Date().toISOString(),
            },
          }),
        });
        return;
      }

      // Mock educator login
      if (body.email === 'educator@test.com' && body.password === 'Educator123!@#') {
        console.log('[Mock API] Returning educator credentials');
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            access_token: 'mock-educator-access-token',
            refresh_token: 'mock-educator-refresh-token',
            token_type: 'bearer',
            user: {
              id: 2,
              email: 'educator@test.com',
              full_name: 'Test Educator',
              role: 'educator',
              is_verified: true,
              is_active: true,
              created_at: new Date().toISOString(),
            },
          }),
        });
        return;
      }

      // Mock invalid credentials
      console.log('[Mock API] Returning 401 - Invalid credentials');
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid credentials' }),
      });
    });

    // Mock permissions endpoint
    await page.route(`${API_BASE_URL}/permissions/me`, async (route, request) => {
      console.log('[Mock API] Intercepted permissions request');

      const auth = request.headers()['authorization'];
      console.log('[Mock API] Auth header:', auth ? 'present' : 'missing');

      if (auth?.includes('mock-student-access-token')) {
        console.log('[Mock API] Returning student permissions');
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            role: 'student',
            permissions: [
              'mcq.view',
              'mcq.attempt',
              'osce.view',
              'osce.attempt',
              'progress.view.own',
              'studycard.view',
            ],
          }),
        });
        return;
      }

      if (auth?.includes('mock-educator-access-token')) {
        console.log('[Mock API] Returning educator permissions');
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            role: 'educator',
            permissions: [
              'mcq.view', 'mcq.attempt', 'mcq.create', 'mcq.update', 'mcq.delete',
              'osce.view', 'osce.attempt', 'osce.create', 'osce.update', 'osce.delete',
              'progress.view.all', 'progress.view.own', 'progress.grade',
              'studycard.view', 'studycard.create',
            ],
          }),
        });
        return;
      }

      console.log('[Mock API] Returning 401 - Unauthorized');
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Unauthorized' }),
      });
    });

    // Mock MCQ list endpoint
    await page.route(`${API_BASE_URL}/mcqs**`, async (route, request) => {
      console.log('[Mock API] Intercepted MCQ list request');

      const auth = request.headers()['authorization'];

      if (auth?.includes('mock-student-access-token') || auth?.includes('mock-educator-access-token')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [],
            total: 0,
            page: 1,
            size: 10,
          }),
        });
        return;
      }

      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Unauthorized' }),
      });
    });

    // Mock OSCE list endpoint
    await page.route(`${API_BASE_URL}/osces**`, async (route, request) => {
      console.log('[Mock API] Intercepted OSCE list request');

      const auth = request.headers()['authorization'];

      if (auth?.includes('mock-student-access-token') || auth?.includes('mock-educator-access-token')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [],
            total: 0,
            page: 1,
            size: 10,
          }),
        });
        return;
      }

      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Unauthorized' }),
      });
    });

    // Mock progress endpoint
    await page.route(`${API_BASE_URL}/progress/me`, async (route, request) => {
      console.log('[Mock API] Intercepted progress request');

      const auth = request.headers()['authorization'];

      if (auth?.includes('mock-student-access-token') || auth?.includes('mock-educator-access-token')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            user_id: 1,
            mcq_completed: 0,
            mcq_total: 0,
            osce_completed: 0,
            osce_total: 0,
            average_score: 0,
          }),
        });
        return;
      }

      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Unauthorized' }),
      });
    });

    console.log('[Mock API] All routes registered successfully');

    // Proceed with the test
    await use();

    // Cleanup
    console.log('[Mock API] Cleaning up request interception');
  }, { auto: true }],
});

export { expect } from '@playwright/test';
