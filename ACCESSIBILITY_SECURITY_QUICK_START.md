# Accessibility & Security Testing - Quick Start Guide

**Last Updated**: 2026-02-16
**Status**: Ready for execution

---

## Quick Commands

### Run All Accessibility Tests
```bash
cd /home/dev/Development/irStudy/testing/playwright
npm run test:a11y
```

### Run Specific Accessibility Tests
```bash
# Epic UI tests only
npm run test:a11y -- tests/accessibility/a11y-epic-ui.spec.ts

# Cerner UI tests only
npm run test:a11y -- tests/accessibility/a11y-cerner-ui.spec.ts

# With UI mode (visual debugging)
npm run test:a11y -- --ui
```

### Run Security Penetration Tests
```bash
cd /home/dev/Development/irStudy/backend
pytest tests/security/test_penetration.py -v
```

### Run Specific Security Tests
```bash
# SQL injection tests only
pytest tests/security/test_penetration.py::TestSQLInjection -v

# Prompt injection tests only
pytest tests/security/test_penetration.py::TestPromptInjection -v

# With coverage report
pytest tests/security/test_penetration.py --cov=src --cov-report=html
```

---

## Test Coverage Summary

### Accessibility (56 tests)
- Epic EMR: 32 tests (WCAG 2.2 AA)
- Cerner EMR: 24 tests (WCAG 2.2 AAA dark theme)

### Security (35 tests)
- SQL Injection: 3 tests
- XSS: 3 tests
- CSRF: 3 tests
- Authorization Bypass: 4 tests
- Prompt Injection: 2 tests
- Rate Limiting: 2 tests
- Session Security: 3 tests
- Sensitive Data: 3 tests
- XXE: 1 test
- SSRF: 2 tests

---

## Expected Pass Rate
- Target: 100% (ZERO TOLERANCE)
- If tests fail: Fix violations before deployment

---

## Manual Testing

### Screen Reader Testing
1. Install NVDA: https://www.nvaccess.org/download/
2. Follow guide: `/testing/MANUAL_ACCESSIBILITY_TESTING.md`
3. Test Epic and Cerner interfaces
4. Verify ARIA labels and keyboard navigation

---

## Quality Gates

**MUST PASS before deployment**:
- [ ] 0 axe-core violations (WCAG 2.2 AA/AAA)
- [ ] 100% accessibility test pass rate
- [ ] 100% security test pass rate
- [ ] Manual screen reader testing complete

---

## Support

- **Implementation Summary**: See `ACCESSIBILITY_SECURITY_TESTING_IMPLEMENTATION_SUMMARY.md`
- **Manual Testing Guide**: See `/testing/MANUAL_ACCESSIBILITY_TESTING.md`
- **Test Files**: See `/testing/playwright/tests/accessibility/` and `/backend/tests/security/`

---

**Created**: 2026-02-16
**Quality Expert**: Testing & QA Specialist
