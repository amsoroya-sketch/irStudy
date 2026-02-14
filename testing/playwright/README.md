# Playwright E2E Testing for AMC Clinical Exam Simulation

**Comprehensive end-to-end testing suite with RBAC, accessibility, and MCP integration**

---

## Table of Contents

1. [Overview](#overview)
2. [Setup & Installation](#setup--installation)
3. [Running Tests](#running-tests)
4. [Test Structure](#test-structure)
5. [Writing New Tests](#writing-new-tests)
6. [Best Practices](#best-practices)
7. [CI/CD Integration](#cicd-integration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This testing suite provides comprehensive end-to-end testing for the AMC Clinical Exam Simulation platform, covering:

- ✅ **Authentication Flows**: Login, registration, logout, token refresh
- ✅ **RBAC (Role-Based Access Control)**: Student, Educator, Admin permissions
- ✅ **MCQ Practice**: Browse, filter, attempt, feedback
- ✅ **Dashboard**: Role-based UI rendering
- ✅ **Accessibility**: WCAG 2.1 AA compliance
- ✅ **E2E User Journeys**: Complete flows from registration to MCQ completion

### Test Coverage

- **Total Test Cases**: 113+
- **Authentication Tests**: 26 test cases
- **RBAC Tests**: 36 test cases
- **MCQ Flow Tests**: 24 test cases
- **Dashboard Tests**: 9 test cases
- **E2E Tests**: 3 comprehensive journeys
- **Accessibility Tests**: 15 test cases

### Technology Stack

- **Playwright v1.48+**: Cross-browser testing (Chromium, Firefox, WebKit)
- **TypeScript**: Type-safe test code
- **MSW (Mock Service Worker)**: API mocking for consistent tests
- **Axe-core**: Accessibility testing
- **Faker.js**: Test data generation

---

## Setup & Installation

### Prerequisites

- Node.js >= 18.0.0
- npm or yarn
- Frontend application running on `http://localhost:5173`
- Backend API running on `http://localhost:8001`

### Installation Steps

```bash
# Navigate to testing directory
cd /home/dev/Development/irStudy/testing/playwright

# Install dependencies
npm install

# Install Playwright browsers (Chromium, Firefox, WebKit)
npx playwright install --with-deps

# Or use shortcut
npm run install:browsers
```

### Environment Configuration

Copy `.env.test` and configure test environment variables:

```bash
# Already configured, but you can modify:
BASE_URL=http://localhost:5173
API_BASE_URL=http://localhost:8001/api/v1

# Test user credentials
STUDENT_EMAIL=student@test.com
STUDENT_PASSWORD=Student123!@#

EDUCATOR_EMAIL=educator@test.com
EDUCATOR_PASSWORD=Educator123!@#

ADMIN_EMAIL=admin@test.com
ADMIN_PASSWORD=Admin123!@#
```

---

## Running Tests

### Run All Tests

```bash
npm test
```

### Run Tests by Category

```bash
# Authentication tests only
npm run test:auth

# RBAC permission tests
npm run test:rbac

# MCQ flow tests
npm run test:mcq

# E2E user journeys
npm run test:e2e

# Accessibility tests
npm run test:a11y
```

### Run Tests by Role

```bash
# Student role tests
npm run test:student

# Educator role tests
npm run test:educator

# Admin role tests
npm run test:admin
```

### Interactive UI Mode

```bash
# Run tests with Playwright UI (recommended for debugging)
npm run test:ui
```

### Headed Mode (See Browser)

```bash
# Run tests with visible browser
npm run test:headed
```

### Debug Mode

```bash
# Run tests in debug mode (step through tests)
npm run test:debug
```

### View Test Report

```bash
# Open HTML test report
npm run test:report
```

### Codegen (Record Tests)

```bash
# Launch Playwright codegen for recording user interactions
npm run test:codegen
```

---

## Test Structure

### Directory Layout

```
testing/playwright/
├── fixtures/               # Test fixtures and helpers
│   ├── auth.fixture.ts     # Authentication contexts (student/educator/admin)
│   ├── users.fixture.ts    # Test user data
│   └── mcqs.fixture.ts     # Sample MCQ data
├── mocks/                  # API mocking
│   ├── handlers.ts         # MSW request handlers
│   ├── server.ts           # MSW server setup
│   └── responses/          # Mock API responses
├── tests/                  # Test suites
│   ├── auth/               # Authentication tests
│   │   ├── login.spec.ts
│   │   ├── register.spec.ts
│   │   ├── logout.spec.ts
│   │   └── token-refresh.spec.ts
│   ├── rbac/               # RBAC permission tests
│   │   ├── student-permissions.spec.ts
│   │   ├── educator-permissions.spec.ts
│   │   ├── admin-permissions.spec.ts
│   │   └── permission-guard.spec.ts
│   ├── mcq/                # MCQ flow tests
│   │   ├── mcq-browser.spec.ts
│   │   ├── mcq-attempt.spec.ts
│   │   └── mcq-feedback.spec.ts
│   ├── dashboard/          # Dashboard tests
│   │   └── dashboard.spec.ts
│   ├── e2e/                # End-to-end tests
│   │   ├── student-journey.spec.ts
│   │   ├── educator-journey.spec.ts
│   │   └── admin-journey.spec.ts
│   └── accessibility/      # Accessibility tests
│       ├── login-a11y.spec.ts
│       ├── mcq-browser-a11y.spec.ts
│       └── keyboard-nav.spec.ts
├── utils/                  # Utility functions
│   ├── test-helpers.ts     # Helper functions
│   ├── selectors.ts        # Page object selectors
│   └── assertions.ts       # Custom assertions
├── reports/                # Test results (HTML, JSON, JUnit)
├── playwright.config.ts    # Playwright configuration
├── package.json            # Dependencies and scripts
└── README.md               # This file
```

---

## Writing New Tests

### Example Test Structure

```typescript
import { test, expect } from '../../fixtures/auth.fixture';
import { STUDENT_USER } from '../../fixtures/users.fixture';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
    await page.goto('/path');
  });

  test('should do something', async ({ page }) => {
    // Arrange
    const button = page.locator('button:has-text("Click Me")');

    // Act
    await button.click();

    // Assert
    await expect(page).toHaveURL('/new-path');
  });
});
```

### Using Authenticated Contexts

```typescript
// Student authenticated page
test('student test', async ({ studentPage }) => {
  await studentPage.goto('/dashboard');
  // studentPage is already authenticated as student
});

// Educator authenticated page
test('educator test', async ({ educatorPage }) => {
  await educatorPage.goto('/mcqs/create');
  // educatorPage is already authenticated as educator
});

// Admin authenticated page
test('admin test', async ({ adminPage }) => {
  await adminPage.goto('/admin');
  // adminPage is already authenticated as admin
});
```

### Testing RBAC with PermissionGuard

```typescript
test('should hide create button for students', async ({ studentPage }) => {
  await studentPage.goto('/mcqs');

  // Student should NOT see create button (no MCQ_CREATE permission)
  const createButton = studentPage.locator('button:has-text("Create MCQ")');
  await expect(createButton).not.toBeVisible();
});

test('should show create button for educators', async ({ educatorPage }) => {
  await educatorPage.goto('/mcqs');

  // Educator SHOULD see create button (has MCQ_CREATE permission)
  const createButton = educatorPage.locator('button:has-text("Create MCQ")');
  await expect(createButton).toBeVisible();
});
```

---

## Best Practices

### 1. Use Fixtures for Authentication

**✅ Good:**
```typescript
test('test', async ({ studentPage }) => {
  await studentPage.goto('/dashboard');
});
```

**❌ Bad:**
```typescript
test('test', async ({ page }) => {
  await page.goto('/login');
  await page.fill('email', 'student@test.com');
  await page.fill('password', 'password');
  await page.click('submit');
  await page.goto('/dashboard');
});
```

### 2. Use Data-Testid for Stable Selectors

**✅ Good:**
```typescript
const mcqCard = page.locator('[data-testid="mcq-card"]');
```

**❌ Bad:**
```typescript
const mcqCard = page.locator('div.css-xyz-123');
```

### 3. Wait for API Responses

**✅ Good:**
```typescript
const response = await page.waitForResponse('/api/v1/mcqs');
const data = await response.json();
expect(data.items).toHaveLength(20);
```

**❌ Bad:**
```typescript
await page.waitForTimeout(2000); // Brittle timing
```

### 4. Test User Flows, Not Implementation

**✅ Good:**
```typescript
test('student can attempt MCQ', async ({ studentPage }) => {
  await studentPage.goto('/mcqs/1/attempt');
  await studentPage.locator('input[value="A"]').check();
  await studentPage.locator('button:has-text("Submit")').click();
  await expect(studentPage.locator('[role="alert"]')).toBeVisible();
});
```

**❌ Bad:**
```typescript
test('useState sets selectedAnswer', async ({ page }) => {
  // Testing internal implementation
});
```

### 5. Use Descriptive Test Names

**✅ Good:**
```typescript
test('should show error when submitting MCQ without selecting answer', async ({ page }) => {
  // ...
});
```

**❌ Bad:**
```typescript
test('MCQ test 1', async ({ page }) => {
  // ...
});
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Playwright Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18

      - name: Install dependencies
        run: |
          cd testing/playwright
          npm ci

      - name: Install Playwright Browsers
        run: |
          cd testing/playwright
          npx playwright install --with-deps

      - name: Run Playwright tests
        run: |
          cd testing/playwright
          npm run test:ci

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: testing/playwright/reports/
          retention-days: 30
```

---

## Troubleshooting

### Tests Failing Locally

**Issue**: Tests pass in CI but fail locally

**Solution**:
1. Ensure frontend and backend are running
2. Check environment variables in `.env.test`
3. Clear browser cache: `npx playwright cache clear`
4. Reinstall browsers: `npx playwright install --with-deps`

### Authentication Tests Failing

**Issue**: Login tests fail with "Invalid credentials"

**Solution**:
1. Verify test users exist in database
2. Check `STUDENT_EMAIL` and `STUDENT_PASSWORD` in `.env.test`
3. Ensure backend is running and accessible
4. Check API base URL: `API_BASE_URL=http://localhost:8001/api/v1`

### Timeout Errors

**Issue**: Tests timeout waiting for elements

**Solution**:
```typescript
// Increase timeout for specific test
test('slow test', async ({ page }) => {
  test.setTimeout(120000); // 2 minutes
  await page.goto('/slow-page');
});

// Or globally in playwright.config.ts
timeout: 60000, // 1 minute
```

### RBAC Tests Failing

**Issue**: Permission guards not working as expected

**Solution**:
1. Verify permissions API returns correct data: `GET /api/v1/permissions/me`
2. Check user role in fixture: `STUDENT_USER.role === 'student'`
3. Ensure PermissionGuard component is implemented correctly
4. Check React Query cache: permissions should be cached for 5 minutes

### Screenshots Not Captured

**Issue**: Screenshots not saved on failure

**Solution**:
```typescript
// In playwright.config.ts
use: {
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
}
```

---

## Advanced Features

### Parallel Execution

Tests run in parallel by default. To control parallelism:

```bash
# Run with 4 workers
npx playwright test --workers=4

# Run serially (1 worker)
npx playwright test --workers=1
```

### Test Sharding (for CI)

```bash
# Shard 1 of 4
npx playwright test --shard=1/4

# Shard 2 of 4
npx playwright test --shard=2/4
```

### Visual Regression Testing

```typescript
await expect(page).toHaveScreenshot('dashboard.png');
```

### Network Interception

```typescript
// Mock API response
await page.route('**/api/v1/mcqs', (route) => {
  route.fulfill({
    status: 200,
    body: JSON.stringify({ items: [], total: 0 }),
  });
});
```

---

## Test Metrics & Reporting

After running tests, view the HTML report:

```bash
npm run test:report
```

The report includes:
- ✅ Test pass/fail status
- ⏱️ Execution time
- 📸 Screenshots on failure
- 🎥 Videos on failure
- 📊 Test coverage by feature

---

## Contributing

When adding new tests:

1. Follow the existing structure in `/tests/`
2. Use descriptive test names
3. Add test to appropriate category (auth, rbac, mcq, etc.)
4. Document complex test scenarios
5. Ensure tests pass locally before committing

---

## Support & Resources

- **Playwright Docs**: https://playwright.dev
- **Project README**: `/home/dev/Development/irStudy/README.md`
- **Frontend Docs**: `/home/dev/Development/irStudy/FRONTEND_IMPLEMENTATION_COMPLETE.md`
- **Backend API Docs**: `/home/dev/Development/irStudy/WEEK3_COMPLETE_SUMMARY.md`

---

**Last Updated**: 2026-02-07
**Test Suite Version**: 1.0.0
**Status**: ✅ Ready for Use
