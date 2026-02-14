# Testing Strategy Product Requirements Document

**Version**: 1.0
**Date**: 2026-02-02
**Product**: EMR Practice System - Testing & Quality Assurance
**Objective**: Ensure 100% test pass rate with ≥70% coverage

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Testing Pyramid](#testing-pyramid)
3. [Frontend Testing](#frontend-testing)
4. [Backend Testing](#backend-testing)
5. [Integration Testing](#integration-testing)
6. [E2E Testing](#e2e-testing)
7. [Validation Testing](#validation-testing)
8. [Performance Testing](#performance-testing)
9. [Security Testing](#security-testing)
10. [CI/CD Integration](#cicd-integration)

---

## Testing Philosophy

### Core Principles

1. **Test-Driven Development (TDD)**: Write tests before implementation
2. **100% Test Pass Rate**: Zero tolerance for failing tests
3. **≥70% Code Coverage**: Minimum threshold for all modules
4. **Fast Feedback**: Tests complete in <2 minutes
5. **Isolated Tests**: No test dependencies or shared state
6. **Meaningful Assertions**: Tests verify behavior, not implementation

### Quality Gates

```
Code Commit → Unit Tests → Integration Tests → E2E Tests → Deploy
     ↓            ↓              ↓                 ↓
   PASS        PASS           PASS              PASS (required)
```

**Deployment Requirement**: All quality gates must pass before deployment.

---

## Testing Pyramid

```
           /\
          /E2E\            5% - End-to-end scenarios
         /------\
        /Integration\      15% - API + Database + Services
       /------------\
      / Unit Tests   \     80% - Individual functions/components
     /----------------\
```

### Target Distribution

| Test Type | Percentage | Count (Approx) | Purpose |
|-----------|-----------|----------------|---------|
| Unit Tests | 80% | ~400 tests | Fast, isolated, specific |
| Integration Tests | 15% | ~75 tests | API endpoints, database, services |
| E2E Tests | 5% | ~25 tests | Critical user workflows |

---

## Frontend Testing

### Technology Stack

```json
{
  "testing-library/react": "^14.1.2",
  "testing-library/jest-dom": "^6.1.5",
  "testing-library/user-event": "^14.5.1",
  "vitest": "^1.1.0",
  "jsdom": "^23.0.1",
  "@vitest/ui": "^1.1.0",
  "vitest-mock-extended": "^1.3.1"
}
```

### 1. Component Unit Tests

**Test All Components In Isolation**

```typescript
// Example: CernerSidebar.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CernerSidebar } from './CernerSidebar';

describe('CernerSidebar', () => {
  it('renders all navigation items', () => {
    render(
      <CernerSidebar
        currentPath="/cerner"
        onNavigate={vi.fn()}
        sessionId="test-session"
      />
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('SOAP Notes')).toBeInTheDocument();
    expect(screen.getByText('Prescriptions')).toBeInTheDocument();
  });

  it('highlights active navigation item', () => {
    render(
      <CernerSidebar
        currentPath="/cerner/soap-notes"
        onNavigate={vi.fn()}
        sessionId="test-session"
      />
    );

    const soapNotesItem = screen.getByText('SOAP Notes').closest('button');
    expect(soapNotesItem).toHaveClass('active');
  });

  it('calls onNavigate when item clicked', () => {
    const handleNavigate = vi.fn();

    render(
      <CernerSidebar
        currentPath="/cerner"
        onNavigate={handleNavigate}
        sessionId="test-session"
      />
    );

    fireEvent.click(screen.getByText('Prescriptions'));
    expect(handleNavigate).toHaveBeenCalledWith('/cerner/prescriptions');
  });

  it('displays session timer', () => {
    render(
      <CernerSidebar
        currentPath="/cerner"
        onNavigate={vi.fn()}
        sessionId="test-session"
      />
    );

    expect(screen.getByText(/Time:/)).toBeInTheDocument();
  });
});
```

### 2. Custom Hook Tests

```typescript
// Example: useAutoSave.test.ts

import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useAutoSave } from './useAutoSave';

describe('useAutoSave', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('does not save immediately on data change', () => {
    const saveFn = vi.fn();
    const { rerender } = renderHook(
      ({ data }) => useAutoSave(data, saveFn, 30000),
      { initialProps: { data: { content: 'initial' } } }
    );

    rerender({ data: { content: 'updated' } });

    expect(saveFn).not.toHaveBeenCalled();
  });

  it('saves after debounce delay', async () => {
    const saveFn = vi.fn();
    const { rerender } = renderHook(
      ({ data }) => useAutoSave(data, saveFn, 30000),
      { initialProps: { data: { content: 'initial' } } }
    );

    rerender({ data: { content: 'updated' } });

    act(() => {
      vi.advanceTimersByTime(30000);
    });

    expect(saveFn).toHaveBeenCalledWith({ content: 'updated' });
  });

  it('cancels pending save on unmount', () => {
    const saveFn = vi.fn();
    const { rerender, unmount } = renderHook(
      ({ data }) => useAutoSave(data, saveFn, 30000),
      { initialProps: { data: { content: 'initial' } } }
    );

    rerender({ data: { content: 'updated' } });
    unmount();

    act(() => {
      vi.advanceTimersByTime(30000);
    });

    expect(saveFn).not.toHaveBeenCalled();
  });
});
```

### 3. Form Validation Tests (Zod Schemas)

```typescript
// Example: soapNoteSchema.test.ts

import { describe, it, expect } from 'vitest';
import { soapNoteSchema } from './schemas';

describe('soapNoteSchema', () => {
  describe('subjective section', () => {
    it('requires chief complaint minimum 5 characters', () => {
      const result = soapNoteSchema.safeParse({
        sessionId: 'uuid',
        patientId: 'uuid',
        subjective: {
          chiefComplaint: 'Pain',  // Only 4 characters
          // ... other required fields
        }
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain('at least 5 characters');
      }
    });

    it('accepts valid chief complaint', () => {
      const result = soapNoteSchema.shape.subjective.shape.chiefComplaint.safeParse(
        'Chest pain radiating to left arm'
      );

      expect(result.success).toBe(true);
    });

    it('rejects chief complaint starting with lowercase', () => {
      const result = soapNoteSchema.shape.subjective.shape.chiefComplaint.safeParse(
        'chest pain'
      );

      expect(result.success).toBe(false);
    });
  });

  describe('vital signs', () => {
    it('rejects temperature outside valid range', () => {
      const result = soapNoteSchema.shape.objective.shape.vitalSigns.safeParse({
        temperature: 45,  // Too high
        heartRate: 75,
        bloodPressure: { systolic: 120, diastolic: 80 },
        respiratoryRate: 16,
        oxygenSaturation: 98
      });

      expect(result.success).toBe(false);
    });

    it('ensures systolic > diastolic', () => {
      const result = soapNoteSchema.shape.objective.shape.vitalSigns.safeParse({
        temperature: 37,
        heartRate: 75,
        bloodPressure: { systolic: 80, diastolic: 120 },  // Invalid
        respiratoryRate: 16,
        oxygenSaturation: 98
      });

      expect(result.success).toBe(false);
    });
  });
});
```

### 4. State Management Tests (Zustand)

```typescript
// Example: emrSessionStore.test.ts

import { describe, it, expect, beforeEach } from 'vitest';
import { useEMRSessionStore } from './emrSessionStore';
import { act, renderHook } from '@testing-library/react';

describe('EMRSessionStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useEMRSessionStore.setState({
      sessionId: null,
      patient: null,
      soapNote: {},
      prescriptions: [],
      validationResult: null
    });
  });

  it('initializes with null session', () => {
    const { result } = renderHook(() => useEMRSessionStore());
    expect(result.current.sessionId).toBeNull();
  });

  it('sets patient data', () => {
    const { result } = renderHook(() => useEMRSessionStore());

    act(() => {
      result.current.setPatient({
        id: 'patient-123',
        name: 'John Doe',
        age: 45,
        sex: 'M'
      });
    });

    expect(result.current.patient?.name).toBe('John Doe');
  });

  it('updates SOAP note section', () => {
    const { result } = renderHook(() => useEMRSessionStore());

    act(() => {
      result.current.updateSOAPNote('subjective', {
        chiefComplaint: 'Chest pain'
      });
    });

    expect(result.current.soapNote.subjective?.chiefComplaint).toBe('Chest pain');
  });

  it('adds prescription to list', () => {
    const { result } = renderHook(() => useEMRSessionStore());

    act(() => {
      result.current.addPrescription({
        medicationId: 'med-123',
        medicationName: 'Paracetamol'
      });
    });

    expect(result.current.prescriptions).toHaveLength(1);
    expect(result.current.prescriptions[0].medicationName).toBe('Paracetamol');
  });
});
```

### Frontend Testing Checklist

- [ ] All UI components have unit tests
- [ ] All custom hooks tested
- [ ] All Zod schemas validated
- [ ] Zustand stores tested
- [ ] Form submissions tested
- [ ] Error states tested
- [ ] Loading states tested
- [ ] Accessibility tested (aria labels, keyboard navigation)
- [ ] Responsive design tested (mobile/tablet/desktop)
- [ ] Browser compatibility tested (Chrome, Firefox, Safari, Edge)

---

## Backend Testing

### Technology Stack

```python
# requirements-dev.txt
pytest==7.4.3
pytest-asyncio==0.23.2
pytest-cov==4.1.0
httpx==0.25.2
faker==21.0.0
freezegun==1.4.0
```

### 1. Unit Tests (Services & Validators)

```python
# tests/test_validation/test_pbs_validator.py

import pytest
from src.validation.pbs_validator import PBSValidator, ValidationError

class TestPBSValidator:
    """Test PBS medication validator"""

    @pytest.fixture
    def validator(self):
        return PBSValidator()

    @pytest.fixture
    def patient_allergies(self):
        return [
            {
                "allergen": "Penicillin",
                "reaction": "Anaphylaxis",
                "severity": "severe"
            }
        ]

    def test_valid_prescription_passes(self, validator):
        """Test valid prescription passes validation"""

        medications = [{
            "pbs_code": "1234A",
            "name": "Paracetamol",
            "quantity": 50,
            "repeats": 3
        }]

        errors = validator.validate_prescription(
            medications=medications,
            patient_allergies=[],
            patient_conditions=[],
            patient_medications=[],
            patient_age=45
        )

        assert len(errors) == 0

    def test_exceeds_quantity_limit(self, validator):
        """Test quantity exceeding PBS limit triggers warning"""

        medications = [{
            "pbs_code": "1234A",
            "name": "Paracetamol",
            "quantity": 150,  # Exceeds limit of 100
            "repeats": 3
        }]

        errors = validator.validate_prescription(
            medications=medications,
            patient_allergies=[],
            patient_conditions=[],
            patient_medications=[],
            patient_age=45
        )

        assert any(e.category == 'pbs_compliance' and 'quantity' in e.message.lower()
                  for e in errors)

    def test_exceeds_repeats_limit(self, validator):
        """Test repeats exceeding PBS limit triggers error"""

        medications = [{
            "pbs_code": "1234A",
            "name": "Paracetamol",
            "quantity": 50,
            "repeats": 6  # Exceeds limit of 5
        }]

        errors = validator.validate_prescription(
            medications=medications,
            patient_allergies=[],
            patient_conditions=[],
            patient_medications=[],
            patient_age=45
        )

        assert any(e.severity == 'error' and 'repeats' in e.message.lower()
                  for e in errors)

    def test_detects_allergy_contraindication(self, validator, patient_allergies):
        """Test allergy contraindication detection"""

        medications = [{
            "pbs_code": "5678B",
            "name": "Amoxicillin",  # Penicillin-based
            "quantity": 30,
            "repeats": 0
        }]

        errors = validator.validate_prescription(
            medications=medications,
            patient_allergies=patient_allergies,
            patient_conditions=[],
            patient_medications=[],
            patient_age=45
        )

        assert any(e.severity == 'error' and 'contraindicated' in e.message.lower()
                  for e in errors)

    def test_pregnancy_category_check(self, validator):
        """Test pregnancy category warnings"""

        medications = [{
            "pbs_code": "9012C",
            "name": "Metformin",
            "quantity": 100,
            "repeats": 5
        }]

        errors = validator.validate_prescription(
            medications=medications,
            patient_allergies=[],
            patient_conditions=[],
            patient_medications=[],
            patient_age=30,
            patient_pregnant=True
        )

        # Metformin is Category C - should warn
        assert any('pregnancy' in e.message.lower() for e in errors)
```

### 2. API Integration Tests

```python
# tests/test_api/test_sessions.py

import pytest
from httpx import AsyncClient
from src.main import app
from src.models.user import User
from src.services.auth_service import AuthService
from datetime import timedelta

@pytest.fixture
async def client():
    """Test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_token(db_session):
    """Create test user and return auth token"""

    # Create test user
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=AuthService.get_password_hash("testpass123")
    )
    db_session.add(user)
    await db_session.commit()

    # Generate token
    token = AuthService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(hours=1)
    )

    return token

@pytest.mark.asyncio
class TestSessionAPI:
    """Test EMR session API endpoints"""

    async def test_create_session(self, client, auth_token):
        """Test creating new EMR session"""

        response = await client.post(
            "/api/v1/sessions",
            json={
                "emr_type": "cerner",
                "scenario_id": None,
                "patient_id": "patient-123"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert data["emr_type"] == "cerner"
        assert "expires_at" in data

    async def test_create_session_requires_auth(self, client):
        """Test session creation requires authentication"""

        response = await client.post(
            "/api/v1/sessions",
            json={
                "emr_type": "cerner",
                "patient_id": "patient-123"
            }
        )

        assert response.status_code == 401

    async def test_get_session(self, client, auth_token):
        """Test retrieving session details"""

        # First create session
        create_response = await client.post(
            "/api/v1/sessions",
            json={
                "emr_type": "epic",
                "patient_id": "patient-123"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        session_id = create_response.json()["session_id"]

        # Then retrieve it
        get_response = await client.get(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["session_id"] == session_id
        assert data["status"] == "active"

    async def test_complete_session(self, client, auth_token):
        """Test completing session"""

        # Create session
        create_response = await client.post(
            "/api/v1/sessions",
            json={
                "emr_type": "cerner",
                "patient_id": "patient-123"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        session_id = create_response.json()["session_id"]

        # Complete session
        complete_response = await client.post(
            f"/api/v1/sessions/{session_id}/complete",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert complete_response.status_code == 200
        data = complete_response.json()
        assert data["status"] == "completed"
        assert "completed_at" in data
```

### 3. Database Tests

```python
# tests/test_models/test_soap_note.py

import pytest
from src.models.soap_note import SOAPNote
from src.models.session import EMRSession
from src.models.user import User
from datetime import datetime

@pytest.mark.asyncio
class TestSOAPNoteModel:
    """Test SOAP note database model"""

    async def test_create_soap_note(self, db_session):
        """Test creating SOAP note in database"""

        soap_note = SOAPNote(
            session_id="session-123",
            patient_id="patient-123",
            subjective={
                "chief_complaint": "Chest pain",
                "hpi": "45F presents with..."
            },
            objective={
                "vital_signs": {
                    "temperature": 37.2,
                    "heart_rate": 88
                }
            },
            assessment={
                "working_diagnosis": "Unstable angina"
            },
            plan={
                "investigations": []
            }
        )

        db_session.add(soap_note)
        await db_session.commit()

        assert soap_note.id is not None
        assert soap_note.created_at is not None

    async def test_soap_note_auto_save_timestamp(self, db_session):
        """Test auto-save updates last_updated timestamp"""

        soap_note = SOAPNote(
            session_id="session-123",
            patient_id="patient-123",
            subjective={"chief_complaint": "Pain"},
            objective={"vital_signs": {}},
            assessment={"working_diagnosis": "TBD"},
            plan={"investigations": []}
        )

        db_session.add(soap_note)
        await db_session.commit()

        original_updated = soap_note.last_updated

        # Simulate auto-save update
        soap_note.subjective["hpi"] = "Updated HPI content"
        await db_session.commit()

        assert soap_note.last_updated > original_updated
```

### Backend Testing Checklist

- [ ] All validators tested (PBS, MBS, clinical safety)
- [ ] All API endpoints tested
- [ ] Authentication & authorization tested
- [ ] Database models tested
- [ ] Services tested (auth, validation, AI)
- [ ] Error handling tested
- [ ] Database transactions tested
- [ ] Edge cases tested (null values, boundary conditions)
- [ ] Performance tested (response times meet SLAs)

---

## Integration Testing

### Full Workflow Integration Tests

```typescript
// tests/integration/soap-note-workflow.test.ts

import { describe, it, expect, beforeAll } from 'vitest';
import { createSession, createSOAPNote, validateSOAPNote } from '@/api';

describe('SOAP Note Workflow Integration', () => {
  let sessionId: string;
  let authToken: string;

  beforeAll(async () => {
    // Login and get token
    const loginResponse = await fetch('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'testpass123'
      })
    });

    const { access_token } = await loginResponse.json();
    authToken = access_token;

    // Create session
    const sessionResponse = await createSession({
      emr_type: 'cerner',
      patient_id: 'patient-123'
    }, authToken);

    sessionId = sessionResponse.session_id;
  });

  it('completes full SOAP note workflow with validation', async () => {
    // 1. Create SOAP note
    const soapNote = await createSOAPNote({
      session_id: sessionId,
      patient_id: 'patient-123',
      subjective: {
        chief_complaint: 'Chest pain radiating to left arm',
        hpi: '45F presents with acute onset chest pain...',
        // ... complete data
      },
      objective: {
        vital_signs: {
          temperature: 37.2,
          heart_rate: 88,
          blood_pressure: { systolic: 142, diastolic: 86 },
          respiratory_rate: 16,
          oxygen_saturation: 98
        },
        // ... complete data
      },
      assessment: {
        working_diagnosis: 'Unstable angina',
        differential_diagnoses: ['ACS', 'GERD', 'MSK pain'],
        clinical_reasoning: 'Patient presents with...'
      },
      plan: {
        investigations: [{
          type: 'pathology',
          test: 'Troponin',
          mbs_item_number: '66800',
          indication: 'Rule out ACS',
          urgency: 'urgent'
        }],
        // ... complete data
      }
    }, authToken);

    expect(soapNote.soap_note_id).toBeDefined();

    // 2. Validate SOAP note (Layer 1 + 2 + 3)
    const validationResult = await validateSOAPNote(
      soapNote.soap_note_id,
      'full',
      authToken
    );

    // Layer 1 should pass (Zod validation)
    expect(validationResult.layers.layer1.status).toBe('passed');

    // Layer 2 should pass (no clinical red flags)
    expect(validationResult.layers.layer2.status).toBe('passed');

    // Layer 3 AI validation should return scores
    expect(validationResult.layers.layer3.ai_result.overall_score).toBeGreaterThan(0);
    expect(validationResult.overall_score).toBeGreaterThan(0);

    // Validation should complete within SLA
    expect(validationResult.total_duration_ms).toBeLessThan(10000);  // <10 seconds
  });
});
```

---

## E2E Testing

### Technology Stack

```json
{
  "@playwright/test": "^1.40.1"
}
```

### Critical User Workflows

```typescript
// tests/e2e/complete-emr-session.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Complete EMR Practice Session', () => {
  test('student completes Cerner EMR session successfully', async ({ page }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'student@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');

    // 2. Start Cerner EMR session
    await page.click('text=Start EMR Practice');
    await page.click('text=Cerner PowerChart');

    await expect(page).toHaveURL(/\/cerner/);
    await expect(page.locator('.cerner-sidebar')).toBeVisible();

    // 3. Navigate to SOAP Notes
    await page.click('text=SOAP Notes');

    // 4. Write SOAP note
    await page.fill('[name="subjective.chief_complaint"]', 'Chest pain radiating to arm');
    await page.fill('[name="subjective.hpi"]', '45F presents with acute onset chest pain starting 2 hours ago...');

    // Wait for auto-save
    await expect(page.locator('text=Saved')).toBeVisible({ timeout: 35000 });

    // 5. Fill vital signs
    await page.fill('[name="objective.vital_signs.temperature"]', '37.2');
    await page.fill('[name="objective.vital_signs.heart_rate"]', '88');

    // 6. Request validation
    await page.click('text=Validate');

    // Wait for Layer 1 validation (instant)
    await expect(page.locator('.validation-layer1.passed')).toBeVisible({ timeout: 1000 });

    // Wait for Layer 2 validation (<1s)
    await expect(page.locator('.validation-layer2.passed')).toBeVisible({ timeout: 2000 });

    // Wait for Layer 3 AI validation (3-5s)
    await expect(page.locator('.validation-layer3.completed')).toBeVisible({ timeout: 10000 });

    // 7. Check validation score
    const overallScore = await page.locator('.overall-score').textContent();
    expect(parseInt(overallScore!)).toBeGreaterThan(0);

    // 8. Complete session
    await page.click('text=Complete Session');

    await expect(page).toHaveURL(/\/session-summary/);
    await expect(page.locator('text=Session Completed')).toBeVisible();
  });

  test('validates prescription with PBS compliance', async ({ page }) => {
    // Login and navigate to prescriptions
    await page.goto('/cerner/prescriptions');

    // Search PBS medication
    await page.fill('[placeholder*="Search PBS"]', 'Paracetamol');
    await page.click('text=Paracetamol 500mg');

    // Fill prescription form
    await page.selectOption('[name="route"]', 'PO');
    await page.selectOption('[name="frequency"]', 'QID');
    await page.fill('[name="quantity"]', '100');
    await page.fill('[name="repeats"]', '5');
    await page.fill('[name="indication"]', 'Chronic pain management');

    // Submit for validation
    await page.click('text=Validate Prescription');

    // Wait for PBS validation
    await expect(page.locator('.pbs-validation.passed')).toBeVisible({ timeout: 2000 });

    // Check no errors
    await expect(page.locator('.validation-error')).toHaveCount(0);
  });
});
```

---

## Validation Testing

### PBS Validator Test Cases

```python
# Minimum 50 test cases for PBS validator

test_cases = [
    # Quantity validation
    ("exceeds_max_quantity", {"quantity": 150}, "error"),
    ("at_max_quantity", {"quantity": 100}, "pass"),

    # Repeats validation
    ("exceeds_max_repeats", {"repeats": 6}, "error"),
    ("at_max_repeats", {"repeats": 5}, "pass"),

    # Allergy checking
    ("penicillin_allergy_amoxicillin", {...}, "error"),
    ("sulfa_allergy_bactrim", {...}, "error"),

    # Pregnancy categories
    ("category_d_pregnant", {...}, "error"),
    ("category_x_pregnant", {...}, "error"),
    ("category_c_pregnant", {...}, "warning"),

    # Drug interactions
    ("warfarin_aspirin", {...}, "warning"),
    ("metformin_contrast", {...}, "warning"),

    # Age-based dosing
    ("paediatric_dose_check", {"age": 8}, "info"),
    ("elderly_dose_adjustment", {"age": 75}, "info"),

    # Authority requirements
    ("authority_required_missing_code", {...}, "error"),
    ("authority_required_with_code", {...}, "pass"),

    # ... 40+ more test cases
]
```

---

## Performance Testing

### Load Testing with Locust

```python
# tests/performance/locustfile.py

from locust import HttpUser, task, between

class EMRPracticeUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Login and get token"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        self.token = response.json()["access_token"]

    @task(10)
    def create_session(self):
        """Create EMR session (most common)"""
        self.client.post("/api/v1/sessions", json={
            "emr_type": "cerner",
            "patient_id": "patient-123"
        }, headers={"Authorization": f"Bearer {self.token}"})

    @task(5)
    def validate_soap_note(self):
        """Validate SOAP note"""
        self.client.post("/api/v1/validation/soap-note", json={
            "soap_note_id": "note-123",
            "validation_level": "full"
        }, headers={"Authorization": f"Bearer {self.token}"})

    @task(3)
    def get_progress(self):
        """Get user progress"""
        self.client.get("/api/v1/progress/user",
                       headers={"Authorization": f"Bearer {self.token}"})
```

**Performance Targets:**
- 100 concurrent users
- <1s response time for 95th percentile
- <2% error rate

---

## Security Testing

### 1. Authentication Tests

```python
def test_jwt_token_expiration():
    """Test expired JWT tokens are rejected"""
    # Create expired token
    expired_token = create_token(expires_delta=timedelta(seconds=-1))

    response = client.get("/api/v1/sessions",
                         headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401

def test_invalid_jwt_signature():
    """Test tampered JWT tokens are rejected"""
    # Create token with wrong signature
    tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"

    response = client.get("/api/v1/sessions",
                         headers={"Authorization": f"Bearer {tampered_token}"})

    assert response.status_code == 401
```

### 2. SQL Injection Tests

```python
def test_sql_injection_prevention():
    """Test API prevents SQL injection"""
    malicious_input = "'; DROP TABLE users; --"

    response = client.post("/api/v1/soap-notes", json={
        "subjective": {
            "chief_complaint": malicious_input
        }
    })

    # Should either validate input or return 422, not 500
    assert response.status_code != 500
```

### 3. XSS Prevention Tests

```typescript
it('sanitizes XSS attempts in user input', () => {
  const maliciousInput = '<script>alert("XSS")</script>';

  render(<SOAPNoteEditor />);
  const textarea = screen.getByRole('textbox');

  fireEvent.change(textarea, { target: { value: maliciousInput } });

  // Should be escaped or sanitized
  expect(textarea.value).not.toContain('<script>');
});
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml

name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Run unit tests
        working-directory: ./frontend
        run: npm run test:unit -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json

  backend-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run pytest
        working-directory: ./backend
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Testing Checklist

### Pre-Deployment Checklist

- [ ] All unit tests passing (100%)
- [ ] All integration tests passing
- [ ] All E2E tests passing
- [ ] Code coverage ≥70%
- [ ] No critical security vulnerabilities
- [ ] Performance tests meet SLAs
- [ ] PBS validator tested with 50+ cases
- [ ] MBS validator tested with 30+ cases
- [ ] AI validation tested with sample notes
- [ ] Authentication & authorization tested
- [ ] Error handling tested
- [ ] Edge cases tested
- [ ] Browser compatibility tested
- [ ] Accessibility tested (WCAG 2.1 AA)
- [ ] Load testing completed (100 concurrent users)

---

**Document Version**: 1.0
**Last Updated**: 2026-02-02
**Status**: ✅ Ready for Implementation
**Target**: 100% test pass rate, ≥70% coverage

