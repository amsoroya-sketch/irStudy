# Plan to Reach 90% Test Pass Rate Milestone

**Date**: 2026-05-23
**Current Status**: 592/686 passing (86.3%)
**Target**: 618/686 passing (90.0%)
**Gap**: 26 tests

---

## Strategy Overview

Based on investigation, `test_emr_api.py` has import issues and cannot be collected by pytest. The "20 failing EMR Dashboard tests" from earlier runs may have been from a different test file or stale data.

**Revised Strategy**: Target smaller, achievable modules first

---

## Phase 1: Quick Wins (Target: 89.2%)

### 1.1 EMR Sessions Duplicate Tests (5 tests)
**File**: `tests/test_api/test_emr/test_emr_sessions.py`
**Current**: 5 failing
**Expected**: Similar to other duplicate test fixes

**Issues to Fix**:
- JWT authentication
- Schema field alignment
- Test fixture updates

**Estimated Time**: 30 minutes
**Impact**: 592 → 597 (87.0%)

### 1.2 Study Card Optimization (2 tests)
**File**: `tests/test_api/test_study_card_optimization.py`
**Current**: 2 failing
**Expected**: Endpoint integration issues

**Issues to Fix**:
- Endpoint routing
- Response schema alignment

**Estimated Time**: 30 minutes
**Impact**: 597 → 599 (87.3%)

---

## Phase 2: Medium Impact (Target: 88-89%)

### 2.1 HTTPS Middleware Tests (5 tests)
**File**: `tests/test_middleware/test_https.py`
**Current**: 5 failing
**Expected**: Security header validation

**Issues to Fix**:
- HTTPS redirect testing
- Security header presence
- HSTS configuration

**Estimated Time**: 45 minutes
**Impact**: 599 → 604 (88.0%)

### 2.2 GDPR Endpoints (3 tests)
**File**: `tests/test_api/test_gdpr.py`
**Current**: 3 failing
**Expected**: Data privacy endpoints

**Issues to Fix**:
- Data export functionality
- Data deletion validation
- Privacy policy compliance

**Estimated Time**: 45 minutes
**Impact**: 604 → 607 (88.5%)

### 2.3 User Verification (2 tests)
**File**: `tests/test_user_verification.py`
**Current**: 2 failing (expired token tests)
**Expected**: Token expiry validation

**Issues to Fix**:
- Email verification token expiry
- Password reset token expiry

**Estimated Time**: 30 minutes
**Impact**: 607 → 609 (88.8%)

---

## Phase 3: Reach 90% Milestone

### 3.1 EMR Validation Endpoints (16 tests)
**File**: `tests/test_api/test_emr/test_emr_validation.py`
**Current**: 16 failing
**Expected**: 3-layer validation (Pydantic + Python + AI)

**Issues to Fix**:
- Validation endpoint routing
- Schema expectations
- AI validation mocking

**Estimated Time**: 1-2 hours
**Impact**: 609 → 625 (91.1%) ✅ **90% MILESTONE ACHIEVED**

---

## Alternative Path (If EMR Validation Complex)

### Security Tests Subset (Select tests)
**File**: `tests/security/test_penetration.py`
**Current**: 16 failing
**Target**: Fix easiest 10 tests

**Possible Quick Wins**:
- SQL injection prevention (likely passing with SQLAlchemy)
- XSS prevention (likely passing with FastAPI escaping)
- CSRF token validation

**Estimated Time**: 1-1.5 hours
**Impact**: 609 → 619 (90.3%) ✅ **90% MILESTONE ACHIEVED**

---

## Execution Plan (Recommended Order)

### Session 1: Quick Wins (2 hours)
1. **EMR Sessions duplicates** (30 min) → 597 passing
2. **Study Card Optimization** (30 min) → 599 passing
3. **User Verification** (30 min) → 601 passing
4. **HTTPS Middleware** (45 min) → 606 passing

**Checkpoint**: 606/686 (88.3%)

### Session 2: Push to 90% (2 hours)
5. **GDPR** (45 min) → 609 passing
6. **EMR Validation** (1-2 hours) → 625 passing ✅ **90% ACHIEVED**

**Alternative**: Security tests subset (1-1.5 hours) → 619 passing ✅ **90% ACHIEVED**

---

## Total Estimated Time

**Minimum**: 3-4 hours (Quick wins + Security subset)
**Maximum**: 4-5 hours (Quick wins + Full EMR Validation)

---

## Risk Assessment

### Low Risk (High Success Probability)
- ✅ EMR Sessions duplicates (similar to completed work)
- ✅ Study Card Optimization (endpoint fixes)
- ✅ User Verification (token expiry)

### Medium Risk
- ⚠️ HTTPS Middleware (infrastructure testing)
- ⚠️ GDPR (privacy compliance)
- ⚠️ Security subset (depends on actual implementation)

### High Risk
- ❌ EMR Validation (complex 3-layer validation)
- ❌ Full Security suite (16 tests, penetration testing)
- ❌ Mock Exams (authentication mocking issues)

---

## Success Criteria

### Phase 1 Complete (Quick Wins)
- [ ] 606/686 tests passing (88.3%)
- [ ] Zero errors maintained
- [ ] All quick win modules at 100%

### Phase 2 Complete (90% Milestone)
- [ ] 618+ tests passing (90.0%)
- [ ] Zero errors maintained
- [ ] Comprehensive documentation created
- [ ] Session summary published

---

## Fallback Strategy

If EMR Validation or Security tests prove too complex:

1. **Stop at 88-89%** - Still excellent progress
2. **Document blockers** - Identify why tests fail
3. **Create PRDs** - Comprehensive specs for remaining work
4. **Recommend refactoring** - If tests reveal architectural issues

**Note**: 88.3% (606 tests) is still a massive achievement from 76.4% start.

---

## Next Action

**Immediate**: Start with EMR Sessions duplicate tests (5 tests, 30 min estimate)

**Command**:
```bash
pytest tests/test_api/test_emr/test_emr_sessions.py -v
```

**Expected**: Similar issues to MCQ/OSCE duplicates (JWT auth, schema alignment)

---

**Created**: 2026-05-23
**Status**: Ready to execute
**Target**: 90% pass rate (618+ tests)
**Method**: Incremental phases with clear checkpoints
