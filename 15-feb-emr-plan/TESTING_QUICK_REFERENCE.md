# EMR Testing Quick Reference Guide

**For**: Backend developers, Frontend developers, PM
**Purpose**: Quick commands and patterns for running tests

---

## Backend Tests (pytest)

### Run All EMR Tests
```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate

# All EMR tests
pytest tests/test_api/test_emr/ -v

# With coverage report
pytest tests/test_api/test_emr/ -v --cov=src/api/v1/emr --cov-report=term-missing

# Generate HTML coverage report
pytest tests/test_api/test_emr/ --cov=src/api/v1/emr --cov-report=html
# Open coverage/index.html in browser
```

### Run Specific Test Files
```bash
# Sessions endpoint tests
pytest tests/test_api/test_emr/test_emr_sessions.py -v

# Validation endpoint tests  
pytest tests/test_api/test_emr/test_emr_validation.py -v
```

### Run Specific Test Cases
```bash
# Single test
pytest tests/test_api/test_emr/test_emr_sessions.py::test_start_session_success_cardiology -vv

# All tests matching pattern
pytest tests/test_api/test_emr/ -k "start_session" -v

# All tests for specific endpoint
pytest tests/test_api/test_emr/ -k "validate_soap" -v
```

### Debug Failed Tests
```bash
# Show full output (including print statements)
pytest tests/test_api/test_emr/ -v -s

# Stop at first failure
pytest tests/test_api/test_emr/ -v -x

# Drop into debugger on failure
pytest tests/test_api/test_emr/ -v --pdb
```

### Test Performance
```bash
# Show slowest 10 tests
pytest tests/test_api/test_emr/ -v --durations=10

# Fail tests slower than 5 seconds
pytest tests/test_api/test_emr/ -v --timeout=5
```

---

## Frontend Tests (Vitest) - PENDING IMPLEMENTATION

### Run All Frontend Tests
```bash
cd /home/dev/Development/irStudy/frontend

# Run once
npm test

# Watch mode (auto-rerun on file changes)
npm run test:watch

# With UI
npm run test:ui
```

### Run Specific Test Files
```bash
# Specific component
npm test -- EpicSidebar.test.tsx

# All EMR tests
npm test -- emr/epic
```

### Coverage
```bash
# With coverage report
npm test -- --coverage

# Coverage threshold enforcement
npm test -- --coverage --coverage.thresholds.lines=70
```

---

## E2E Tests (Playwright) - PENDING IMPLEMENTATION

### Run All E2E Tests
```bash
cd /home/dev/Development/irStudy/testing/playwright

# Headless mode (CI/CD)
BASE_URL=http://localhost:5173 npx playwright test tests/integration/emr/

# Headed mode (see browser)
BASE_URL=http://localhost:5173 npx playwright test tests/integration/emr/ --headed

# Specific browser
npx playwright test tests/integration/emr/ --project=chromium
```

### Debug E2E Tests
```bash
# Debug mode (pause execution)
npx playwright test tests/integration/emr/ --debug

# Generate test code (record actions)
npx playwright codegen http://localhost:5173/emr-practice
```

### View Test Reports
```bash
# HTML report
npx playwright show-report

# Screenshots/videos on failure (auto-generated in test-results/)
```

---

## Test Fixtures Quick Reference

### Mock Patients

```python
# In test functions, use fixtures:
def test_my_function(client, auth_headers, mock_patient_cardiology):
    # mock_patient_cardiology has:
    # - Full demographics (MRN, Medicare, age, gender)
    # - Vital signs (HR 95, BP 155/92, etc.)
    # - ECG: ST elevation in II,III,aVF
    # - Troponin I: 1.2 ng/mL
    # - Diagnosis: STEMI
    
    patient_id = mock_patient_cardiology["id"]
    # Use in test...
```

Available mock patients:
- `mock_patient_cardiology` - ACS/STEMI (58M, chest pain)
- `mock_patient_respiratory` - Acute asthma (32F, SOB)

### Mock Sessions

```python
def test_my_function(client, auth_headers, mock_session_in_progress):
    # mock_session_in_progress has:
    # - status: "in_progress"
    # - 15 minutes elapsed
    # - 2 auto-saves
    
    session_id = mock_session_in_progress["id"]
    # Use in test...
```

Available mock sessions:
- `mock_session_in_progress` - Active session
- `mock_session_graded` - Completed session (score 12.5/15)

### Mock SOAP Notes

```python
def test_my_function(client, auth_headers, valid_soap_note):
    # valid_soap_note has:
    # - Subjective: 300+ chars (SOCRATES pain assessment)
    # - Objective: Detailed exam findings
    # - Assessment: STEMI diagnosis with differential
    # - Plan: Immediate management (000, dual antiplatelet)
    
    response = client.post(
        "/api/v1/emr/sessions/{id}/submit",
        json={"final_soap_note": valid_soap_note, ...},
        headers=auth_headers
    )
```

Available SOAP notes:
- `valid_soap_note` - High-quality, complete SOAP note
- `incomplete_soap_note` - Invalid (all sections <20 chars)

### Authentication

```python
def test_my_function(client, auth_headers):
    # auth_headers contains valid JWT token
    response = client.get("/api/v1/emr/sessions", headers=auth_headers)
    assert response.status_code == 200
```

Available auth fixtures:
- `auth_headers` - Student user JWT
- `educator_headers` - Educator user JWT
- `other_user_headers` - Another student JWT (for testing 403 Forbidden)

---

## Expected Test Results (When Backend Complete)

### Success Output
```
tests/test_api/test_emr/test_emr_sessions.py::test_start_session_success_cardiology PASSED [  2%]
tests/test_api/test_emr/test_emr_sessions.py::test_start_session_specific_patient PASSED [  4%]
tests/test_api/test_emr/test_emr_sessions.py::test_start_session_no_patients_available PASSED [  6%]
...
tests/test_api/test_emr/test_emr_validation.py::test_validate_pathology_order_missing_indication PASSED [100%]

========================== 46 passed in 8.52s ==========================

Coverage:
  src/api/v1/emr/sessions.py     95%
  src/api/v1/emr/validation.py   88%
  src/agents/soap_validator.py   82%
  TOTAL                          87%   (Target: ≥70% ✅)
```

### Failure Output (Before Implementation)
```
tests/test_api/test_emr/test_emr_sessions.py::test_start_session_success_cardiology FAILED [  2%]
E   assert 404 == 201
E   AssertionError: Endpoint not implemented yet
```

---

## Common Test Patterns

### Testing POST Endpoint
```python
def test_create_resource(client, auth_headers):
    response = client.post(
        "/api/v1/emr/sessions/start",
        json={"specialty": "cardiology", "difficulty": "medium"},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "in_progress"
    assert "session_id" in data
```

### Testing GET Endpoint
```python
def test_get_resource(client, auth_headers, mock_session):
    session_id = mock_session["id"]
    
    response = client.get(
        f"/api/v1/emr/sessions/{session_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
```

### Testing PUT Endpoint (Update)
```python
def test_update_resource(client, auth_headers, mock_session):
    session_id = mock_session["id"]
    
    response = client.put(
        f"/api/v1/emr/sessions/{session_id}",
        json={"soap_note": {...}, "elapsed_time_seconds": 900},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["auto_save_count"] >= 1
```

### Testing Error Cases
```python
def test_endpoint_not_found(client, auth_headers):
    fake_id = str(uuid4())
    
    response = client.get(
        f"/api/v1/emr/sessions/{fake_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    error = response.json()
    assert "error" in error
    assert "not found" in error["error"]["message"].lower()
```

### Testing Unauthorized Access
```python
def test_endpoint_unauthorized(client):
    # No headers (no JWT token)
    response = client.get("/api/v1/emr/sessions")
    
    assert response.status_code == 401
```

### Testing Forbidden Access
```python
def test_endpoint_forbidden(client, other_user_headers, mock_session):
    # Try to access test_user's session with other_user's token
    session_id = mock_session["id"]
    
    response = client.get(
        f"/api/v1/emr/sessions/{session_id}",
        headers=other_user_headers
    )
    
    assert response.status_code == 403
```

---

## TDD Workflow

### RED → GREEN → REFACTOR

1. **RED**: Write failing test first
   ```bash
   pytest tests/test_api/test_emr/test_emr_sessions.py::test_start_session_success_cardiology -v
   # FAILED - Endpoint not implemented (404)
   ```

2. **GREEN**: Implement minimal code to pass
   ```python
   # backend/src/api/v1/emr/sessions.py
   @router.post("/start")
   async def start_session(...):
       # Minimal implementation
       return {"status": "in_progress", ...}
   ```
   
   ```bash
   pytest tests/test_api/test_emr/test_emr_sessions.py::test_start_session_success_cardiology -v
   # PASSED ✅
   ```

3. **REFACTOR**: Improve code quality
   ```python
   # Add caching, optimize queries, etc.
   # Tests still pass
   ```

---

## Continuous Integration (CI/CD)

### GitHub Actions Example (Future)
```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run pytest
        run: |
          cd backend
          pytest tests/test_api/test_emr/ -v --cov --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
```

---

## Debugging Tips

### Inspecting Test Database
```python
# Add to test:
def test_debug_database(db_session, mock_patient):
    # Breakpoint to inspect database
    import pdb; pdb.set_trace()
    
    # Query database manually
    patients = db_session.query(MockPatient).all()
    print(patients)
```

### Print Request/Response
```python
def test_debug_request(client, auth_headers):
    response = client.post("/api/v1/emr/sessions/start", ...)
    
    print(f"Status: {response.status_code}")
    print(f"Body: {response.json()}")
    print(f"Headers: {response.headers}")
```

### Disable Soft Assertions (Test Implementation Status)
```python
# Enable strict mode to fail on unimplemented endpoints
# Remove these comments in tests:
# NOTE: This will fail until backend EMR API is implemented
assert response.status_code == 201
```

---

## Test Maintenance

### Adding New Tests
1. Create test function in appropriate file
2. Use existing fixtures (or create new ones in conftest.py)
3. Follow naming convention: `test_<action>_<scenario>_<expected>`
4. Add comprehensive assertions
5. Test both success and error cases

### Updating Fixtures
1. Edit `/home/dev/Development/irStudy/backend/tests/test_api/test_emr/conftest.py`
2. Add new fixtures or modify existing ones
3. Run all tests to ensure no regressions

---

## Contact

**Questions about tests?**
- Backend tests: Review `/backend/tests/test_api/test_emr/`
- Test fixtures: See `conftest.py` for comprehensive mock data
- Implementation spec: See `/15-feb-emr-plan/API_SPECIFICATION.md`
- Report issues: Create GitHub issue with test failure output

---

**Last Updated**: 2026-02-15
**Status**: Backend tests complete, frontend/E2E tests pending
