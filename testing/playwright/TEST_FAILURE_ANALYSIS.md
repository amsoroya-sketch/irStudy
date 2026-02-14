# Playwright Test Failure Analysis

**Date**: 2026-02-08
**Status**: 10/20 tests passing (50% pass rate) 🎯
**Goal**: Fix remaining 10 failures to achieve 100% pass rate

---

## Test Results Summary

### ✅ PASSING TESTS (10/20 = 50%)

1. ✅ **Test #1**: should display login form with all required elements
2. ✅ **Test #14**: should auto-redirect if already authenticated
3. ✅ **Test #27**: should show error for password < 12 characters
4. ✅ **Test #28**: should show error for password without uppercase letter
5. ✅ **Test #29**: should show error for password without number
6. ✅ **Test #30**: should show error for password without special character
7. ✅ **Test #31**: should disable submit button while loading
8. ✅ **Test #35**: should navigate to registration page via link
9. ✅ **Test #36**: should navigate to forgot password page
10. ✅ **Test (unlisted)**: Additional password validation test

---

## ❌ FAILING TESTS (10/20 = 50%)

### Category 1: Test Expectations Mismatch (1 test)

#### Test #2: should have proper ARIA labels and accessibility attributes
**Error**: Submit button is disabled (expected: enabled)
**Root Cause**: Test expects button enabled on empty form, but Login component correctly disables it when form is invalid
**Fix**: Update test to fill form fields first, then check button is enabled

---

### Category 2: Backend API Not Running (4 tests)

#### Test #5, #8, #11: Login flow tests
**Error**: `TimeoutError: page.waitForURL('/dashboard')` - 30s timeout
**Root Cause**: Backend not running, login API call fails, no redirect occurs
**Options**:
1. Fix backend DATABASE_PASSWORD and start it
2. **Implement MSW mocks** (recommended - faster, more reliable for testing)

**Tests Affected**:
- Test #5: should successfully login with student credentials
- Test #8: should successfully login with educator credentials
- Test #11: should persist session with "Remember me" checked

---

### Category 3: Validation Error Messages (3 tests)

#### Test #15, #18, #21: Validation error messages
**Error**: Expected text not found (e.g., `/invalid.*email/i`)
**Root Cause**: Frontend validation messages don't match test expectations exactly

**Affected Tests**:
- Test #15: should show error for invalid email format
- Test #18: should show error for empty email
- Test #21: should show error for empty password

**Current Behavior**: Validation works, but message text differs
**Fix**: Update validation messages in `utils/validation.ts` to match test expectations OR update test expectations

---

### Category 4: Network Error Handling (1 test)

#### Test #32: should show error alert on network failure
**Error**: Network error alert not showing
**Root Cause**: Need to verify error handling in AuthContext
**Fix**: Check if network errors properly bubble up and display in UI

---

### Category 5: Keyboard Accessibility (2 tests)

#### Test #37, #40: Keyboard navigation tests
**Error**: Timeouts (10s+) suggesting element focus/interaction issues
**Root Cause**: Tab navigation or Enter key submission not working as expected
**Fix**: Investigate tab order and keyboard event handlers

---

## Issue Priority

### P0 - Critical (Fix First)
1. **Test #2**: Update test expectations (5 min fix)
2. **MSW Mock Implementation**: Mock backend API (30-45 min)

### P1 - High (Fix Second)
3. **Validation Messages**: Align messages with tests (15 min)
4. **Network Error Handling**: Verify error display (10 min)

### P2 - Medium (Fix Third)
5. **Keyboard Accessibility**: Debug tab/enter behavior (20 min)

---

## Detailed Fix Plan

### Fix #1: Test #2 - Submit Button Enabled Check

**Current Test Code** (login.spec.ts:47):
```typescript
const submitButton = page.locator('button[type="submit"]');
await expect(submitButton).toBeEnabled();  // ❌ Fails - button disabled on empty form
```

**Fix Option A - Update Test** (Recommended):
```typescript
// Fill form first, then check button is enabled
await page.fill('input[name="email"]', 'test@example.com');
await page.fill('input[name="password"]', 'ValidPassword123!');

const submitButton = page.locator('button[type="submit"]');
await expect(submitButton).toBeEnabled();  // ✅ Should pass now
```

**Fix Option B - Update Frontend**:
Keep button enabled, validate on submit instead (NOT recommended - worse UX)

---

### Fix #2: Implement MSW Mocks for Backend API

**Install MSW**:
```bash
cd /home/dev/Development/irStudy/testing/playwright
npm install -D msw@latest
```

**Create Mock Handlers** (`testing/playwright/mocks/handlers.ts`):
```typescript
import { http, HttpResponse } from 'msw';

export const handlers = [
  // Mock login endpoint
  http.post('http://localhost:8000/api/v1/auth/login', async ({ request }) => {
    const body = await request.json();

    // Mock successful login
    if (body.email === 'student@test.com' && body.password === 'Student123!@#') {
      return HttpResponse.json({
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'student@test.com',
          full_name: 'Test Student',
          role: 'student',
        },
      });
    }

    // Mock invalid credentials
    return HttpResponse.json(
      { detail: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  // Mock permissions endpoint
  http.get('http://localhost:8000/api/v1/permissions/me', () => {
    return HttpResponse.json({
      role: 'student',
      permissions: ['mcq.view', 'mcq.attempt', 'osce.view', 'osce.attempt', 'progress.view.own', 'studycard.view'],
    });
  }),
];
```

**Setup MSW in Tests** (`testing/playwright/playwright.config.ts`):
```typescript
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

export const server = setupServer(...handlers);

// Start server before all tests
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

---

### Fix #3: Validation Error Messages

**Read Current Validation** (`frontend/src/utils/validation.ts`):
Need to check exact error messages and align with test expectations

**Expected Messages** (from tests):
- Invalid email: `/invalid.*email/i` → "Invalid email" or "Invalid email address"
- Empty email: `/email.*required/i` → "Email is required"
- Empty password: `/password.*required/i` → "Password is required"

**Update validation.ts** to match these patterns

---

### Fix #4: Network Error Handling

**Check AuthContext** (`frontend/src/context/AuthContext.tsx`):
```typescript
// Verify login function catches network errors
const login = async (credentials) => {
  try {
    const response = await loginAPI(credentials);
    // ...
  } catch (error) {
    setAuthState(prev => ({
      ...prev,
      isLoading: false,
      error: error.response?.data?.detail || 'Network error occurred',  // ✅ Should show error
    }));
  }
};
```

**Verify Error Display** (`frontend/src/pages/Login.tsx`):
```typescript
{error && <Alert severity="error">{error}</Alert>}  // ✅ Should display
```

---

### Fix #5: Keyboard Accessibility

**Test #37 Issue**: Tab navigation timing out

**Possible Causes**:
1. Tab order not set correctly
2. Focus trap not working
3. Elements not focusable

**Investigation Steps**:
1. Check if form inputs have `tabIndex` set
2. Verify no `tabIndex="-1"` on interactive elements
3. Test manual tab navigation in browser

**Test #40 Issue**: Enter key not submitting form

**Possible Causes**:
1. Form not handling `onSubmit` event
2. Button `type="submit"` not working
3. Keyboard event listener interfering

**Fix**: Ensure form has `<form onSubmit={handleSubmit}>` and button has `type="submit"`

---

## Expected Improvements After Fixes

| Fix | Tests Fixed | New Pass Rate |
|-----|-------------|---------------|
| Current | 10/20 | 50% |
| Fix #1 (Test expectations) | +1 | 55% |
| Fix #2 (MSW mocks) | +4 | 75% |
| Fix #3 (Validation messages) | +3 | 90% |
| Fix #4 (Network errors) | +1 | 95% |
| Fix #5 (Keyboard) | +2 | **100%** ✅ |

---

## Implementation Order

### Step 1: Quick Wins (15 min)
1. Fix Test #2 - Update test to fill form first
2. Check validation messages and align

**Expected Result**: 55-60% pass rate

### Step 2: MSW Implementation (45 min)
1. Install MSW
2. Create mock handlers
3. Set up in Playwright config
4. Test login flows

**Expected Result**: 75-80% pass rate

### Step 3: Polish (30 min)
1. Fix network error handling
2. Debug keyboard accessibility
3. Run full test suite

**Expected Result**: 90-100% pass rate

---

## Files to Modify

1. `testing/playwright/tests/auth/login.spec.ts` - Update test #2
2. `testing/playwright/mocks/handlers.ts` - Create MSW mocks (NEW FILE)
3. `testing/playwright/playwright.config.ts` - Setup MSW server
4. `frontend/src/utils/validation.ts` - Align error messages
5. `frontend/src/context/AuthContext.tsx` - Verify error handling
6. `frontend/src/pages/Login.tsx` - Check keyboard handlers

---

## Success Criteria

- ✅ >= 18/20 tests passing (90%+)
- ✅ All validation tests pass
- ✅ All navigation tests pass
- ✅ Login flow works with MSW mocks
- ✅ Keyboard accessibility functional

---

**Created**: 2026-02-08
**Current Status**: 50% pass rate (10/20)
**Target**: 100% pass rate (20/20)
**Estimated Time**: 1.5-2 hours for all fixes

🎯 **Next Action**: Start with Fix #1 (quick win - update test #2)**
