# Security Penetration Test Fixes - Quick Reference

**Last Updated**: 2026-05-24  
**Status**: 16/16 failing → Target: 16/16 passing  
**Estimated Effort**: 11 hours (1.5 days)

---

## Test Failure Summary

| Test | Status | Root Cause | Fix Time | Priority |
|------|--------|------------|----------|----------|
| test_sql_injection_in_session_query | FAIL | No query param validation | 30 min | P0 |
| test_sql_injection_in_soap_note | FAIL | SOAP schema too strict | 2 hrs* | P0 |
| test_sql_injection_in_user_search | FAIL | Missing endpoint | 1 hr | P0 |
| test_xss_in_soap_note | FAIL | SOAP schema too strict | 2 hrs* | P2 |
| test_xss_in_validation_feedback | FAIL | SOAP schema too strict | 2 hrs* | P2 |
| test_csrf_with_jwt_auth | FAIL | Endpoint routing issue | 30 min | P1 |
| test_csrf_missing_authorization_header | FAIL | Endpoint routing issue | 30 min | P1 |
| test_user_cannot_access_other_users_sessions | FAIL | Endpoint routing issue | 30 min | P0 |
| test_user_cannot_update_other_users_sessions | FAIL | Endpoint routing issue | 30 min | P0 |
| test_user_cannot_delete_other_users_sessions | FAIL | Endpoint routing issue | 30 min | P0 |
| test_student_cannot_access_admin_endpoints | FAIL | Missing endpoint | 1 hr | P0 |
| test_prompt_injection_in_soap_note | FAIL | SOAP schema too strict | 2 hrs* | P2 |
| test_jailbreak_attempt_in_soap_note | FAIL | SOAP schema too strict | 2 hrs* | P2 |
| test_rate_limit_on_validation_endpoint | FAIL | No rate limiting | 1 hr | P3 |
| test_jwt_tokens_not_logged | FAIL | Test fixture error | 15 min | P3 |
| test_xxe_not_applicable_json_api | FAIL | No XXE middleware | 30 min | P3 |

*Same fix (SOAP validation) affects 5 tests total

---

## Immediate Action Plan

### Step 1: SOAP Validation Fix (2 hours) → Fixes 5 tests

**File**: `/home/dev/Development/irStudy/backend/src/api/v1/emr/schemas.py`

**Find**:
```python
class SOAPNoteDict(BaseModel):
    subjective: str = Field(..., regex="^[a-zA-Z0-9\\s.,!?-]+$")  # Too strict!
```

**Replace with**:
```python
class SOAPNoteDict(BaseModel):
    subjective: str = Field(..., min_length=1, max_length=5000)  # Accept all text
    objective: str = Field(..., min_length=1, max_length=5000)
    assessment: str = Field(..., min_length=1, max_length=5000)
    plan: str = Field(..., min_length=1, max_length=5000)
```

**Tests Fixed**: 5/16 (31%)
- test_sql_injection_in_soap_note
- test_xss_in_soap_note
- test_xss_in_validation_feedback
- test_prompt_injection_in_soap_note
- test_jailbreak_attempt_in_soap_note

---

### Step 2: SQL Injection Query Param (30 min) → Fixes 1 test

**File**: `/home/dev/Development/irStudy/backend/src/api/v1/emr/sessions.py`

**Add before @router.get("/sessions")**:
```python
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class SessionListParams(BaseModel):
    user_id: Optional[UUID] = None  # UUID validation prevents SQL injection
    status: Optional[str] = Field(None, regex="^(in_progress|graded|cancelled)$")
    specialty: Optional[str] = None
```

**Update endpoint**:
```python
@router.get("/sessions")
async def list_sessions(
    params: SessionListParams = Depends(),  # Add this
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(EMRSession).filter(EMRSession.user_id == current_user.id)
    
    if params.status:
        query = query.filter(EMRSession.status == params.status)
    
    return query.all()
```

**Tests Fixed**: 1/16 (6%)
- test_sql_injection_in_session_query

---

### Step 3: Investigate Endpoint Routing (30 min) → Could fix 6 tests

**File**: `/home/dev/Development/irStudy/backend/src/main.py`

**Check router registration**:
```python
# Verify this exists and is correct
from src.api.v1.emr.router import router as emr_router

app.include_router(emr_router, prefix="/api/v1")
```

**Test manually**:
```bash
curl -X POST http://localhost:8001/api/v1/emr/sessions/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"emr_system": "epic"}'
```

**Expected**: 200/201 (success) or 422 (validation error)  
**If getting**: 404 → Router config issue → Fix prefix/path

**Tests Fixed (if successful)**: 6/16 (37%)
- test_csrf_with_jwt_auth
- test_csrf_missing_authorization_header
- test_user_cannot_access_other_users_sessions
- test_user_cannot_update_other_users_sessions
- test_user_cannot_delete_other_users_sessions

---

### Step 4: Create User Search Endpoint (1 hour) → Fixes 1 test

**File**: `/home/dev/Development/irStudy/backend/src/api/v1/users.py` (NEW)

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.db.base import get_db
from src.auth.dependencies import get_current_user
from src.db.models import User
import re

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/search")
async def search_users(
    query: str = Query(..., min_length=1, max_length=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search users by name or email (SQL injection safe)"""
    # Sanitize: remove SQL special characters
    sanitized = re.sub(r'[^a-zA-Z0-9\s@.]', '', query)
    
    if not sanitized:
        return []  # Empty results for invalid queries
    
    # SQLAlchemy ORM prevents SQL injection
    results = db.query(User).filter(
        (User.full_name.ilike(f"%{sanitized}%")) |
        (User.email.ilike(f"%{sanitized}%"))
    ).limit(10).all()
    
    return [{"id": str(u.id), "name": u.full_name, "email": u.email} for u in results]
```

**Register in main.py**:
```python
from src.api.v1.users import router as users_router
app.include_router(users_router, prefix="/api/v1")
```

**Tests Fixed**: 1/16 (6%)
- test_sql_injection_in_user_search

---

### Step 5: Create Admin Endpoint (1 hour) → Fixes 1 test

**File**: `/home/dev/Development/irStudy/backend/src/api/v1/admin.py` (NEW)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.base import get_db
from src.auth.dependencies import get_current_user
from src.db.models import User, UserRole

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users")
async def list_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint (requires EDUCATOR role)"""
    if current_user.role != UserRole.EDUCATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = db.query(User).all()
    return [{"id": str(u.id), "email": u.email, "role": u.role.value} for u in users]
```

**Register in main.py**:
```python
from src.api.v1.admin import router as admin_router
app.include_router(admin_router, prefix="/api/v1")
```

**Tests Fixed**: 1/16 (6%)
- test_student_cannot_access_admin_endpoints

---

### Step 6: Add Rate Limiting (1 hour) → Fixes 1 test

**File**: `/home/dev/Development/irStudy/backend/requirements.txt`

Add:
```
slowapi==0.1.9
```

Install:
```bash
pip install slowapi==0.1.9
```

**File**: `/home/dev/Development/irStudy/backend/src/main.py`

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**File**: `/home/dev/Development/irStudy/backend/src/api/v1/emr/sessions.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@router.post("/sessions/{session_id}/submit")
@limiter.limit("5/minute")  # Add this decorator
async def submit_session(
    request: Request,  # Add this parameter
    session_id: UUID,
    data: SubmitSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # ... existing code
```

**Tests Fixed**: 1/16 (6%)
- test_rate_limit_on_validation_endpoint

---

### Step 7: Add XXE Middleware (30 min) → Fixes 1 test

**File**: `/home/dev/Development/irStudy/backend/src/middleware/content_type.py` (NEW)

```python
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

class ContentTypeValidationMiddleware(BaseHTTPMiddleware):
    """Reject XML content (XXE prevention)"""
    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            
            if "xml" in content_type.lower():
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="XML not supported. Use application/json."
                )
        
        return await call_next(request)
```

**Register in main.py**:
```python
from src.middleware.content_type import ContentTypeValidationMiddleware
app.add_middleware(ContentTypeValidationMiddleware)
```

**Tests Fixed**: 1/16 (6%)
- test_xxe_not_applicable_json_api

---

### Step 8: Fix Test Fixture (15 min) → Fixes 1 test

**File**: `/home/dev/Development/irStudy/backend/tests/security/test_penetration.py`

**Find**:
```python
def test_jwt_tokens_not_logged(self, client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student1@test.com", "password": "TestPassword123!@#"}
    )
```

**Replace with**:
```python
def test_jwt_tokens_not_logged(self, client, security_test_user1):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": security_test_user1.email, "password": "TestPassword123!@#"}
    )
```

**Tests Fixed**: 1/16 (6%)
- test_jwt_tokens_not_logged

---

## Testing Commands

### After Each Fix
```bash
# Test specific category
bash run_tests.sh tests/security/test_penetration.py::TestSQLInjection -v
bash run_tests.sh tests/security/test_penetration.py::TestXSS -v
bash run_tests.sh tests/security/test_penetration.py::TestAuthorizationBypass -v
```

### After All Fixes
```bash
# All penetration tests
bash run_tests.sh tests/security/test_penetration.py -v

# Full test suite
bash run_tests.sh
```

---

## Expected Progress

| After Step | Tests Passing | % Complete | Cumulative Time |
|------------|---------------|------------|-----------------|
| 1 (SOAP) | 5/16 | 31% | 2 hours |
| 2 (SQL query) | 6/16 | 37% | 2.5 hours |
| 3 (Routing) | 12/16 | 75% | 3 hours |
| 4 (User search) | 13/16 | 81% | 4 hours |
| 5 (Admin) | 14/16 | 87% | 5 hours |
| 6 (Rate limit) | 15/16 | 94% | 6 hours |
| 7 (XXE) | 16/16 | 100% | 6.5 hours |
| 8 (Test fix) | 16/16 | 100% | 6.75 hours |

---

## Checklist

**Phase 1: Critical Fixes (3 hours)**
- [ ] Fix SOAP validation schema (Step 1) - 2 hours
- [ ] Fix SQL injection query param (Step 2) - 30 min
- [ ] Investigate endpoint routing (Step 3) - 30 min
- [ ] Run tests → Expect 11-12/16 passing

**Phase 2: Missing Endpoints (2 hours)**
- [ ] Create user search endpoint (Step 4) - 1 hour
- [ ] Create admin endpoint (Step 5) - 1 hour
- [ ] Run tests → Expect 13-14/16 passing

**Phase 3: Security Features (2 hours)**
- [ ] Add rate limiting (Step 6) - 1 hour
- [ ] Add XXE middleware (Step 7) - 30 min
- [ ] Fix test fixture (Step 8) - 15 min
- [ ] Run tests → Expect 16/16 passing

**Final Validation**
- [ ] All penetration tests passing (16/16)
- [ ] Full test suite passing (685/685)
- [ ] No new failures introduced

---

## Quick Debug Guide

### If SOAP tests still fail after Step 1:
```bash
# Check schema file
grep -A 10 "class SOAPNoteDict" /home/dev/Development/irStudy/backend/src/api/v1/emr/schemas.py

# Should NOT see regex patterns, only min_length/max_length
```

### If endpoint routing tests fail after Step 3:
```bash
# Check router registration
grep -A 5 "include_router.*emr" /home/dev/Development/irStudy/backend/src/main.py

# Manual test
curl -X POST http://localhost:8001/api/v1/emr/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"emr_system": "epic"}'
# Should get 401 (auth required), NOT 404
```

### If rate limiting test fails after Step 6:
```bash
# Verify SlowAPI installed
pip list | grep slowapi

# Check limiter registered
grep -A 3 "Limiter" /home/dev/Development/irStudy/backend/src/main.py
```

---

## Files Modified Summary

**New Files (3)**:
1. `/src/api/v1/users.py`
2. `/src/api/v1/admin.py`
3. `/src/middleware/content_type.py`

**Modified Files (5)**:
1. `/src/api/v1/emr/schemas.py` (SOAP validation)
2. `/src/api/v1/emr/sessions.py` (query params + rate limiting)
3. `/src/main.py` (register routers + middleware)
4. `/requirements.txt` (add slowapi)
5. `/tests/security/test_penetration.py` (test fixture)

---

## Success Criteria

- 16/16 penetration tests passing
- 685/685 overall tests passing
- No security vulnerabilities introduced
- Code reviewed and documented

---

**For detailed analysis**: See `SECURITY_ANALYSIS_EXECUTIVE_SUMMARY.md`  
**For implementation details**: See `SECURITY_IMPLEMENTATION_PLAN.md`
