# irStudy Project-Specific Constraints

## Project Overview

**Context**: irStudy platform has **two integrated systems** (EMR Practice + AI OSCE Simulation) sharing infrastructure.

**CRITICAL**: When working on irStudy, agents MUST coordinate across systems to prevent conflicts.

---

## Cross-System Implementation Workflow

### 🔗 Required Reading Before Any Task

1. **Master Plan** (overall platform view):
   - Read: `/home/dev/Development/irStudy/COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md`

2. **Shared Infrastructure Spec** (if exists):
   - Read: `/home/dev/Development/irStudy/SHARED_INFRASTRUCTURE_SPEC.md`
   - Contains: Vault keys, Redis namespaces, JWT format, security standards

3. **System-Specific Docs**:
   - EMR: `/home/dev/Development/irStudy/COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md`
   - AI OSCE: `/home/dev/Development/irStudy/ai-osce-ralph-prds/IMPLEMENTATION_STATUS.md`

### 📋 Sequential Implementation Protocol

**Step 1: Shared Infrastructure FIRST** (BLOCKS everything else)
```
PM reads COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md
  ↓
Identify shared infrastructure tasks (Vault, Redis, security tests)
  ↓
Delegate to security-compliance-expert (Vault + HTTPS + JWT)
  ↓
Validate: 0 hardcoded credentials, 35 security tests pass
  ↓
Delegate to rust-ffi-expert (Redis architecture)
  ↓
Validate: Redis operational, namespaces configured (emr:* vs osce:*)
  ↓
CHECKPOINT: Shared infrastructure COMPLETE → Proceed to system-specific work
```

**Step 2: System-Specific Implementation** (can run in parallel)
```
EMR Implementation (rust-ffi-expert, flutter-desktop-expert)
  ↓ (parallel)
AI OSCE Implementation (rust-ffi-expert, aba-clinical-expert, flutter-desktop-expert)
  ↓
CHECKPOINT: Both systems reference SHARED_INFRASTRUCTURE_SPEC.md
CHECKPOINT: No duplicate Vault keys, no Redis namespace collisions
  ↓
Validate each system independently before integration
```

**Step 3: Integration Layer** (requires both systems complete)
```
Delegate to rust-ffi-expert: OSCE-to-EMR converter
  ↓
Delegate to flutter-desktop-expert: Unified progress dashboard
  ↓
Delegate to testing-qa-expert: Cross-system E2E tests
  ↓
CHECKPOINT: 12 integration tests pass (100%)
  ↓
Final validation: All 500+ tests pass across platform
```

### ⚠️ Anti-Patterns to Avoid

**❌ DON'T**: Delegate EMR and AI OSCE tasks simultaneously without shared infrastructure
**✅ DO**: Complete Week 1 (shared infrastructure) before delegating system-specific tasks

**❌ DON'T**: Let agents create separate Vault setups, Redis configs, or security tests
**✅ DO**: Reference SHARED_INFRASTRUCTURE_SPEC.md in all agent prompts

**❌ DON'T**: Assume both systems can use different JWT formats or security headers
**✅ DO**: Enforce unified standards (9 security headers, same JWT claims)

**❌ DON'T**: Allow `user_progress` table extensions without coordination
**✅ DO**: Combined Alembic migration adding EMR + OSCE columns together

### 🎯 Delegation Template for Cross-System Work

```markdown
Agent Task: [Specific task for EMR or AI OSCE]

CROSS-SYSTEM CONSTRAINTS:
1. **MUST READ FIRST**:
   - COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md (understand integration)
   - SHARED_INFRASTRUCTURE_SPEC.md (reuse existing patterns)

2. **Shared Infrastructure** (DO NOT recreate):
   - Vault: Use existing key hierarchy (see VAULT_INTEGRATION.md)
   - Redis: Use assigned namespace (emr:* OR osce:*)
   - JWT: Use unified token format (see SHARED_INFRASTRUCTURE_SPEC.md)
   - Security: Extend existing test suite (backend/tests/test_security/)

3. **Validation Checklist**:
   - [ ] No duplicate infrastructure (Vault, Redis, security tests)
   - [ ] Namespace conflicts checked (Redis keys, database tables)
   - [ ] Security standards aligned (same encryption, HTTPS headers)
   - [ ] Cross-references added (link to integration PRDs if applicable)

4. **Integration Points**:
   - If extending `user_progress`: Coordinate with other system's migration
   - If using Claude API: Check shared rate limit (90 req/min total)
   - If creating dashboard: Consider unified view (EMR + OSCE metrics)

EXAMPLE (correct coordination):
[Provide specific example from SHARED_INFRASTRUCTURE_SPEC.md]
```

### 📊 Quality Gates for Cross-System Work

Before marking work COMPLETE:
- [ ] No duplicate infrastructure created (Vault, Redis, security)
- [ ] Shared components referenced, not recreated
- [ ] Integration tests added if systems interact
- [ ] Documentation cross-references updated
- [ ] Master plan STATUS updated (week completed, deliverables checked off)

---

## Technology Stack

### Frontend
- Flutter Desktop (Material Design 3)
- Riverpod 2.6+ for state management
- WCAG 2.2 AA accessibility compliance

### Backend
- FastAPI (Python)
- PostgreSQL with SQLAlchemy
- Redis for caching
- Rust FFI for performance-critical operations

### Security
- HashiCorp Vault for secrets management
- SQLCipher for database encryption
- JWT authentication
- 9 required security headers (HTTPS, CSP, HSTS, etc.)

### Testing Requirements
- 100% test pass rate (mandatory)
- ≥70% code coverage
- Unit tests (pytest/jest)
- Integration tests
- E2E tests (Playwright)

---

## 0 - DISCOVERY & CODE REUSE (Ponytail Strategy)

**Ponytail Principle**: Every line of code that doesn't need to exist saves tokens, time, and errors.

### Section 0 in PRDs (MANDATORY as of 2026-07-01)

All PRDs executed by Ralph MUST include **Section 0: DISCOVERY** that documents:
- Existing code search results
- Reusable components identified
- Python packages considered
- TypeScript/React libraries evaluated
- Medical content sources (RAG, Qdrant)
- Decision to reuse vs. create new

**Example Section 0 for irStudy**:
```markdown
## 0 - DISCOVERY

### Existing Code Search
- ✅ FOUND: FastAPI router pattern in `backend/src/api/routers/patient_router.py`
- ✅ FOUND: React component pattern in `frontend/src/components/PatientCard.tsx`
- ❌ NOT FOUND: OSCE session management (new domain)

### Reuse Decisions
1. **FastAPI Router**: Reuse `patient_router.py` structure (SQLAlchemy + dependency injection)
2. **React Components**: Reuse `PatientCard.tsx` patterns (TypeScript + hooks)
3. **RAG Content**: Search Qdrant for existing medical content before creating new

### Packages Considered
- `fastapi: ^0.115.0` ✅ ALREADY INSTALLED
- `sqlalchemy: ^2.0.0` ✅ ALREADY INSTALLED
- `react: ^18.2.0` ✅ ALREADY INSTALLED
```

### Discovery Commands (Run BEFORE Creating Code)

**Python/FastAPI Backend Search**:
```bash
# Search for existing routers
find backend/src/api/routers -name "*.py"

# Search for existing models
find backend/src/models -name "*.py"

# Check for similar endpoints
grep -r "@router\." backend/src/api/

# Check for existing database operations
grep -r "session.query\|session.add" backend/src/

# Check installed Python packages
cat backend/requirements.txt | grep [package-name]
```

**TypeScript/React Frontend Search**:
```bash
# Search for existing components
find frontend/src/components -name "*.tsx"

# Search for existing hooks
find frontend/src/hooks -name "*.ts"

# Check for similar API calls
grep -r "axios.get\|fetch(" frontend/src/

# Check for existing state management
grep -r "useState\|useContext\|useReducer" frontend/src/

# Check installed npm packages
cat frontend/package.json | grep [package-name]
```

**Medical Content/RAG Search**:
```bash
# Search Qdrant for existing medical content
curl -X POST "http://localhost:6333/collections/amc_blueprints/points/search" \
  -H "Content-Type: application/json" \
  -d '{"vector": [...], "limit": 5}'

# Check existing citations
grep -r "qdrant_point_id\|citation" backend/data/

# Check for similar conditions
find backend/data/amc_blueprints -name "*condition-name*.json"
```

### Code Reuse Checklist (Complete BEFORE Creating New Code)

**Python/FastAPI Backend**:
- [ ] Does this router exist? → Search `backend/src/api/routers/`
- [ ] Does this model exist? → Search `backend/src/models/`
- [ ] Does this endpoint exist? → Grep for `@router.get`, `@router.post`
- [ ] Is there a Python package? → Check requirements.txt, PyPI
- [ ] Can I extend existing code? → Prefer extension over duplication

**TypeScript/React Frontend**:
- [ ] Does this component exist? → Search `frontend/src/components/`
- [ ] Does this hook exist? → Search `frontend/src/hooks/`
- [ ] Does this API call exist? → Grep for axios/fetch calls
- [ ] Is there an npm package? → Check package.json, npmjs.com
- [ ] Can I reuse existing state management? → Check context/hooks

**Medical Content/RAG**:
- [ ] Does this condition exist in Qdrant? → Search RAG database
- [ ] Does this citation exist? → Check backend/data/
- [ ] Can I extend existing content? → Prefer augmentation over recreation

### Anti-Patterns (NEVER DO THIS)

❌ **Creating new router without discovery**:
```python
# WRONG: Creating new router without checking if similar exists
@router.post("/my-new-endpoint")
async def my_endpoint(): ...
```

✅ **Correct approach**:
```bash
# FIRST: Search for existing routers
find backend/src/api/routers -name "*patient*.py"
grep -r "@router.post.*patient" backend/

# THEN: Reuse pattern if found, or create new with justification
```

❌ **Duplicating React components**:
```tsx
// WRONG: Creating new PatientCard when one exists
export function MyPatientCard() { ... }
```

✅ **Correct approach**:
```bash
# FIRST: Search for existing components
find frontend/src/components -name "*Patient*.tsx"

# THEN: Reuse or extend existing implementation
```

### Integration with Ralph PRDs

**All PRDs executed by Ralph MUST**:
1. Include Section 0 (DISCOVERY) documenting search results
2. Justify new code creation (explain why reuse wasn't possible)
3. Reference existing patterns (FastAPI routers, React components, RAG content)
4. Follow established project patterns (cross-system coordination, security)

---

## irStudy-Specific Code Patterns

### Python/FastAPI Backend Patterns (MUST FOLLOW)

**Router Structure** (Reuse this pattern):
```python
# CORRECT: Standard router pattern
# backend/src/api/routers/patient_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Patient
from src.schemas import PatientCreate, PatientResponse

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])

@router.post("/", response_model=PatientResponse, status_code=201)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    """Create new patient record."""
    try:
        db_patient = Patient(**patient.dict())
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# WRONG: Hardcoded connection strings, no dependency injection
async def create_patient(patient: dict):
    conn = psycopg2.connect("postgresql://...")  # ❌ VIOLATION
```

**SQLAlchemy Model Pattern**:
```python
# CORRECT: Model with proper relationships
# backend/src/models/patient.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    encounters = relationship("Encounter", back_populates="patient")
```

**Alembic Migration Pattern**:
```python
# CORRECT: Alembic migration with rollback
# backend/alembic/versions/001_add_patients_table.py

def upgrade():
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('patients')
```

### TypeScript/React Frontend Patterns (MUST FOLLOW)

**Component Structure** (Reuse this pattern):
```tsx
// CORRECT: TypeScript component with proper typing
// frontend/src/components/PatientCard.tsx

import React, { useState, useEffect } from 'react';
import { Patient } from '@/types/patient';
import { fetchPatient } from '@/api/patientApi';

interface PatientCardProps {
  patientId: number;
  onSelect?: (patient: Patient) => void;
}

export const PatientCard: React.FC<PatientCardProps> = ({
  patientId,
  onSelect
}) => {
  const [patient, setPatient] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPatient = async () => {
      try {
        const data = await fetchPatient(patientId);
        setPatient(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    loadPatient();
  }, [patientId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!patient) return null;

  return (
    <div className="patient-card" onClick={() => onSelect?.(patient)}>
      <h3>{patient.name}</h3>
      <p>Age: {patient.age}</p>
    </div>
  );
};

// WRONG: No TypeScript types, hardcoded URLs
export function PatientCard(props) {  // ❌ No type safety
  const [data, setData] = useState(null);

  fetch('http://localhost:8001/patients')  // ❌ Hardcoded URL
    .then(res => res.json())
    .then(setData);

  return <div>{data?.name}</div>;
}
```

**API Client Pattern**:
```typescript
// CORRECT: Typed API client with error handling
// frontend/src/api/patientApi.ts

import axios from 'axios';
import { Patient, PatientCreate } from '@/types/patient';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8001';

export const patientApi = {
  async fetchAll(): Promise<Patient[]> {
    const response = await axios.get<Patient[]>(`${API_BASE}/api/v1/patients`);
    return response.data;
  },

  async create(patient: PatientCreate): Promise<Patient> {
    const response = await axios.post<Patient>(
      `${API_BASE}/api/v1/patients`,
      patient
    );
    return response.data;
  },
};

// WRONG: No types, no error handling
export function getPatients() {
  return fetch('/api/patients').then(r => r.json());  // ❌ No types
}
```

**Custom Hook Pattern**:
```typescript
// CORRECT: Reusable custom hook
// frontend/src/hooks/usePatient.ts

import { useState, useEffect } from 'react';
import { Patient } from '@/types/patient';
import { patientApi } from '@/api/patientApi';

export function usePatient(patientId: number) {
  const [patient, setPatient] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadPatient = async () => {
      try {
        setLoading(true);
        const data = await patientApi.fetchById(patientId);
        setPatient(data);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setLoading(false);
      }
    };

    loadPatient();
  }, [patientId]);

  return { patient, loading, error };
}

// Usage in component:
const { patient, loading, error } = usePatient(123);
```

### Flutter Provider Pattern (MUST FOLLOW)

```dart
// CORRECT: Use databaseConfigProvider for all FFI calls
final dbConfig = ref.read(databaseConfigProvider);
await ffi.method(
  userId: dbConfig.userId,
  dbPath: dbConfig.dbPath,
  dbKey: dbConfig.dbKey,
);

// WRONG: Never hardcode credentials
await ffi.method(
  userId: 'mock-user-id',  // ❌ VIOLATION
  dbPath: '/path/to/db',   // ❌ VIOLATION
  dbKey: 'hardcoded-key',  // ❌ VIOLATION
);
```

### Redis Namespace Convention

```python
# EMR system uses emr:* prefix
redis_client.set("emr:patient:123", data)

# OSCE system uses osce:* prefix
redis_client.set("osce:session:456", data)
```

### RAG Content Requirements

All medical content MUST:
- Include `qdrant_point_id` (UUID) for traceability
- Cite Australian medical sources (≥60% of content)
- Link to source documents (no hallucinations)
- Pass reference verification checks

**Example**:
```json
{
  "red_flags": [
    {
      "flag": "Sudden-onset severe headache",
      "citation": {
        "source": "Talley & O'Connor Clinical Examination 9th Ed",
        "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
        "page": "p. 412"
      }
    }
  ]
}
```

---

## Project-Specific Validation Commands

```bash
# Frontend validation (from /home/dev/Development/irStudy/frontend)
cd /home/dev/Development/irStudy/frontend
npx tsc --noEmit  # Expected: 0 errors
npm run lint      # Expected: 0 errors
npm test          # Expected: 100% pass rate

# Backend validation (from /home/dev/Development/irStudy/backend)
cd /home/dev/Development/irStudy/backend
pytest --cov      # Expected: ≥70% coverage, 100% pass rate
python -m pylint src/  # Expected: score ≥9.0/10

# Security validation
grep -r "hardcoded\|localhost\|ws://" /home/dev/Development/irStudy/frontend/src/
# Expected: 0 matches

# Performance validation
curl -w "@curl-format.txt" "http://localhost:8001/api/v1/patient-personas"
# Expected: <200ms (p95)

# Flutter desktop build
cd /home/dev/Development/irStudy/frontend
flutter analyze   # Expected: 0 issues
flutter build linux  # Expected: successful build
```

---

**Last Updated:** 2026-03-29
**Version:** 1.0
**Project:** irStudy Platform (EMR + AI OSCE)
