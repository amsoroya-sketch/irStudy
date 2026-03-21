# Week 1 Critical Implementation Plan

**Created**: 2026-03-16
**Status**: Awaiting Approval
**Execution Time**: ~2-3 hours
**Agent Delegation**: Using Agent OS Expert Agents

---

## 🎯 Overview

Execute all 3 Week 1 critical tasks using specialized expert agents:
1. **Fix QA Validator** (Security + Testing agents) - 30 min
2. **Database Insertion** (Rust FFI + Security agents) - 1 hour
3. **Frontend Integration** (Flutter Desktop agent) - 1-2 hours

---

## 📋 Task 1: Fix QA Validator Schema

### Agent Assignment
**Primary**: `testing-qa-expert` (QA validation specialist)
**Secondary**: `security-compliance-expert` (Code review)

### Objective
Fix schema mismatch: `expected_diagnosis` → `diagnosis` in `qa_validator.py`

### Detailed Steps

#### Step 1.1: Backup Original File
```bash
cp clinical-content-prds/validation-system/qa_validator.py \
   clinical-content-prds/validation-system/qa_validator.py.backup.$(date +%Y%m%d_%H%M%S)
```

#### Step 1.2: Apply Fix
**Agent Prompt for testing-qa-expert**:
```
TASK: Fix QA Validator Schema Mismatch

FILE: clinical-content-prds/validation-system/qa_validator.py

PROBLEM:
- Line 129: Required fields include "expected_diagnosis"
- Line 215: Code reads persona.get("expected_diagnosis", "")
- Actual personas use "diagnosis" field (not "expected_diagnosis")

FIX REQUIRED:
1. Replace "expected_diagnosis" with "diagnosis" in:
   - Line 129 (required_fields list)
   - Line 215 (_gate_4_clinical_accuracy method)
2. Add backward compatibility (support both field names)

IMPLEMENTATION:
```python
# Line 215 - Add backward compatibility
diagnosis = persona.get("diagnosis") or persona.get("expected_diagnosis", "")
if diagnosis:
    diagnosis = diagnosis.lower()
```

CONSTRAINTS (from PROJECT_CONSTRAINTS.md):
- MUST maintain 100% test pass rate
- MUST run `pytest` on validation code
- MUST verify 0 errors before returning

VALIDATION:
1. Run QA validator on sample persona
2. Verify no AttributeError
3. Check all 13 gates execute
4. Test with both old and new schema

SUCCESS CRITERIA:
- [ ] QA validator runs without errors
- [ ] All 207 personas validate successfully
- [ ] Backward compatibility maintained
- [ ] Tests pass (100% pass rate)
```

#### Step 1.3: Validation Commands
```bash
# Test single persona
python3 -c "
import sys
sys.path.insert(0, 'clinical-content-prds/validation-system')
from qa_validator import PersonaQAValidator
import json

validator = PersonaQAValidator()
with open('clinical-content-prds/validation-system/batch1_personas/cardiology_001_stemi_male_65_persona.json') as f:
    result = validator.validate_single_persona(json.load(f))

print(f'Pass: {result[\"overall_pass\"]}')
print(f'Score: {result[\"quality_score\"]}/100')
gates_passed = sum(1 for g in result['gates'].values() if g['status'] == 'PASS')
print(f'Gates: {gates_passed}/13')
"

# Test all personas (sample 10)
python3 -c "
import sys, json, random
from pathlib import Path
sys.path.insert(0, 'clinical-content-prds/validation-system')
from qa_validator import PersonaQAValidator

validator = PersonaQAValidator()
files = list(Path('clinical-content-prds/validation-system/batch1_personas').glob('*.json'))
sample = random.sample(files, 10)

passed = 0
for f in sample:
    with open(f) as fp:
        result = validator.validate_single_persona(json.load(fp))
    if result['overall_pass']:
        passed += 1

print(f'Passed: {passed}/10')
"
```

### Expected Output
```
✅ QA validator fixed
✅ All 13 gates working
✅ 10/10 sample personas pass
✅ Quality scores 75-95/100
```

---

## 📋 Task 2: Database Insertion - Load 207 Personas

### Agent Assignment
**Primary**: `rust-ffi-expert` (Database operations, memory safety)
**Secondary**: `security-compliance-expert` (Credential validation)

### Objective
Load all 207 RAG-verified personas into PostgreSQL database

### Detailed Steps

#### Step 2.1: Verify Database Connection
```bash
# Check PostgreSQL is running
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c "SELECT version();"
```

#### Step 2.2: Review Insertion Script
**Agent Prompt for rust-ffi-expert**:
```
TASK: Execute Database Insertion - 207 Patient Personas

FILE: scripts/insert_batch1_personas.py (already created by Ralph)

REQUIREMENTS:
1. Review the existing script
2. Verify database credentials are secure (not hardcoded)
3. Execute insertion of all 207 personas
4. Validate data integrity

CONSTRAINTS (from PROJECT_CONSTRAINTS.md):
- NEVER hardcode database credentials
- MUST use environment variables or config file
- MUST implement transaction rollback on errors
- MUST verify 0 PHI leaks (synthetic data only)

DATABASE CREDENTIALS (check these sources):
- Environment variable: DATABASE_PASSWORD
- Vault: VAULT_ADDR=http://localhost:8200
- Config file: backend/.env

EXECUTION STEPS:
1. Read the script: scripts/insert_batch1_personas.py
2. Verify credential handling (no hardcoded passwords)
3. Create database schema if not exists
4. Insert all 207 personas with transaction safety
5. Verify insertion count matches 207

VALIDATION:
```sql
-- After insertion
SELECT COUNT(*) FROM patient_personas;
-- Expected: 207

SELECT specialty, difficulty, COUNT(*)
FROM patient_personas
GROUP BY specialty, difficulty
ORDER BY specialty, difficulty;
-- Expected: 15 rows (5 specialties × 3 difficulties)

SELECT
    jsonb_array_length(persona_data->'symptoms') as avg_symptoms,
    COUNT(*) as persona_count
FROM patient_personas
GROUP BY jsonb_array_length(persona_data->'symptoms');
-- Expected: Multiple rows, avg 5-10 symptoms per persona
```

SUCCESS CRITERIA:
- [ ] 207 personas inserted successfully
- [ ] No hardcoded credentials found
- [ ] All database queries return expected results
- [ ] Data integrity verified (JSON fields intact)
```

#### Step 2.3: Execute Insertion
```bash
cd /home/dev/Development/irStudy
source backend/venv/bin/activate

# Check for hardcoded credentials first (security)
grep -r "password\|secret" scripts/insert_batch1_personas.py | grep -v "^#" || echo "✅ No hardcoded credentials"

# Execute insertion
python3 scripts/insert_batch1_personas.py
```

#### Step 2.4: Verification Queries
```bash
# Count check
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c \
  "SELECT COUNT(*) as total FROM patient_personas;"

# Specialty distribution
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c \
  "SELECT specialty, COUNT(*) FROM patient_personas GROUP BY specialty ORDER BY specialty;"

# Sample persona retrieval
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c \
  "SELECT persona_id, name, specialty, diagnosis
   FROM patient_personas
   WHERE persona_id = 'cardiology_001_stemi_male_65';"

# Verify JSON data integrity
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c \
  "SELECT
     persona_id,
     jsonb_array_length(persona_data->'symptoms') as symptom_count,
     jsonb_array_length(persona_data->'management_plan') as mgmt_count
   FROM patient_personas
   LIMIT 5;"
```

### Expected Output
```
✅ Database connected
✅ 207 personas inserted
✅ No credential violations
✅ Data integrity verified
✅ All queries return expected results
```

---

## 📋 Task 3: Frontend Integration - Persona Selector

### Agent Assignment
**Primary**: `flutter-desktop-expert` (Riverpod state, Material Design 3)
**Secondary**: `security-compliance-expert` (API security review)

### Objective
Update frontend to display all 207 personas with filtering

### Detailed Steps

#### Step 3.1: Backend API Endpoints
**Agent Prompt for flutter-desktop-expert**:
```
TASK: Create Backend API for Persona Access

FILES TO CREATE/MODIFY:
1. backend/src/api/v1/personas.py (new file)
2. backend/src/api/v1/router.py (add personas router)

REQUIREMENTS:
- GET /api/v1/personas - List all personas with filters
- GET /api/v1/personas/{persona_id} - Get single persona detail
- Query parameters: specialty, difficulty, search, skip, limit
- Response model: Pydantic schemas

CONSTRAINTS (from PROJECT_CONSTRAINTS.md):
- MUST use Pydantic for validation
- MUST implement pagination (skip/limit)
- MUST sanitize search inputs (prevent SQL injection)
- MUST follow REST API best practices

API ENDPOINT SPECIFICATION:

```python
# backend/src/api/v1/personas.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel, Field

router = APIRouter(prefix="/personas", tags=["personas"])

class PersonaListItem(BaseModel):
    id: int
    persona_id: str
    name: str
    age: int
    gender: str
    specialty: str
    diagnosis: str
    difficulty: str

class PersonaDetail(BaseModel):
    # Full persona data including all fields
    pass

@router.get("/", response_model=List[PersonaListItem])
async def get_personas(
    specialty: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Get list of patient personas with optional filters

    Filters:
    - specialty: Cardiology, Emergency, General Practice, Pediatrics, Respiratory
    - difficulty: Easy, Medium, Hard
    - search: Search in name or diagnosis (case-insensitive)
    - skip: Pagination offset
    - limit: Results per page (max 200)
    """
    # Implementation here
    pass

@router.get("/{persona_id}")
async def get_persona_detail(persona_id: str):
    """Get full persona data including symptoms, management, etc."""
    # Implementation here
    pass
```

VALIDATION:
```bash
# Test API endpoints
curl http://localhost:8000/api/v1/personas | jq '. | length'
# Expected: 50 (default limit)

curl "http://localhost:8000/api/v1/personas?specialty=Cardiology" | jq '. | length'
# Expected: 45

curl http://localhost:8000/api/v1/personas/cardiology_001_stemi_male_65 | jq '.name'
# Expected: "Robert Chen" or similar
```

SUCCESS CRITERIA:
- [ ] API endpoints created
- [ ] Filtering works correctly
- [ ] Pagination implemented
- [ ] No SQL injection vulnerabilities
- [ ] API tests pass
```

#### Step 3.2: Frontend UI Components
**Agent Prompt for flutter-desktop-expert** (continued):
```
TASK: Update Frontend Persona Selector

FILES TO MODIFY:
1. frontend/src/services/api.ts - Add persona API calls
2. frontend/src/pages/OSCEPractice.tsx - Update persona selector
3. frontend/src/components/PersonaFilter.tsx - New filter component

CONSTRAINTS (from PROJECT_CONSTRAINTS.md):
- MUST use Riverpod 2.6+ for state management
- MUST implement Material Design 3 components
- MUST meet WCAG 2.2 AA accessibility
- MUST use TypeScript strict mode

IMPLEMENTATION:

1. API Service (frontend/src/services/api.ts):
```typescript
export interface PersonaListItem {
  id: number;
  persona_id: string;
  name: string;
  age: number;
  gender: string;
  specialty: string;
  diagnosis: string;
  difficulty: string;
}

export const getPersonas = async (params?: {
  specialty?: string;
  difficulty?: string;
  search?: string;
}): Promise<PersonaListItem[]> => {
  const response = await axiosInstance.get('/personas', { params });
  return response.data;
};

export const getPersonaDetail = async (personaId: string): Promise<any> => {
  const response = await axiosInstance.get(`/personas/${personaId}`);
  return response.data;
};
```

2. OSCE Practice Page (frontend/src/pages/OSCEPractice.tsx):
```typescript
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getPersonas, getPersonaDetail } from '../services/api';

export const OSCEPractice = () => {
  const [filters, setFilters] = useState({
    specialty: '',
    difficulty: '',
    search: ''
  });
  const [selectedPersonaId, setSelectedPersonaId] = useState('');

  // Fetch persona list
  const { data: personas, isLoading } = useQuery({
    queryKey: ['personas', filters],
    queryFn: () => getPersonas(filters)
  });

  // Fetch selected persona detail
  const { data: personaDetail } = useQuery({
    queryKey: ['persona-detail', selectedPersonaId],
    queryFn: () => getPersonaDetail(selectedPersonaId),
    enabled: !!selectedPersonaId
  });

  return (
    <div className="osce-practice">
      {/* Filter controls */}
      <PersonaFilter
        filters={filters}
        onFilterChange={setFilters}
      />

      {/* Persona selector */}
      <select
        value={selectedPersonaId}
        onChange={(e) => setSelectedPersonaId(e.target.value)}
        aria-label="Select patient persona"
      >
        <option value="">-- Select a patient ({personas?.length || 0} available) --</option>
        {personas?.map((p) => (
          <option key={p.persona_id} value={p.persona_id}>
            {p.name} - {p.diagnosis} ({p.difficulty})
          </option>
        ))}
      </select>

      {/* Display selected persona */}
      {personaDetail && <PersonaDisplay persona={personaDetail} />}
    </div>
  );
};
```

VALIDATION:
- [ ] Dropdown shows 207 personas
- [ ] Filters update dropdown instantly
- [ ] Search returns relevant results
- [ ] Persona detail loads correctly
- [ ] No accessibility violations (WCAG 2.2 AA)
- [ ] TypeScript compiles with 0 errors

SUCCESS CRITERIA:
- [ ] All components render without errors
- [ ] User can filter by specialty, difficulty
- [ ] User can search by name/diagnosis
- [ ] Selected persona displays full details
- [ ] UI responsive (<100ms filter updates)
```

### Expected Output
```
✅ API endpoints working
✅ Frontend components updated
✅ All 207 personas accessible
✅ Filtering functional
✅ 0 TypeScript errors
✅ WCAG 2.2 AA compliant
```

---

## 🔄 Execution Workflow

### Phase 1: Task 1 (QA Validator) - 30 min
1. Delegate to `testing-qa-expert` agent
2. Agent reads constraints
3. Agent applies fix with backward compatibility
4. Agent runs validation tests
5. Agent reports results

### Phase 2: Task 2 (Database) - 1 hour
1. Delegate to `rust-ffi-expert` agent
2. Agent verifies no hardcoded credentials
3. Agent executes insertion script
4. Agent runs verification queries
5. Agent reports results

### Phase 3: Task 3 (Frontend) - 1-2 hours
1. Delegate to `flutter-desktop-expert` agent (backend API)
2. Agent creates API endpoints
3. Agent tests endpoints
4. Delegate to `flutter-desktop-expert` agent (frontend UI)
5. Agent updates components
6. Agent verifies TypeScript compilation
7. Agent reports results

### Parallel Execution (where possible)
- Task 1 and Task 2 can run in parallel (independent)
- Task 3 backend can start while Task 2 is verifying
- Task 3 frontend requires Task 3 backend complete

---

## ✅ Success Criteria (All Tasks)

### Quality Gates
- [ ] 0 hardcoded credentials (security scan)
- [ ] 100% test pass rate (pytest)
- [ ] 0 TypeScript errors (npm run type-check)
- [ ] 207 personas in database
- [ ] All 207 personas accessible via UI
- [ ] WCAG 2.2 AA accessibility compliance

### Functional Requirements
- [ ] QA validator runs on all personas
- [ ] Database queries return expected results
- [ ] API endpoints respond correctly
- [ ] Frontend filters work
- [ ] End-to-end user flow works

### Performance Targets
- [ ] QA validation: <5 sec per persona
- [ ] Database insertion: <30 seconds total
- [ ] API response time: <100ms (p95)
- [ ] UI filter updates: <100ms

---

## 🚨 Rollback Plan

If any task fails:

### Task 1 Rollback
```bash
# Restore original validator
cp clinical-content-prds/validation-system/qa_validator.py.backup.* \
   clinical-content-prds/validation-system/qa_validator.py
```

### Task 2 Rollback
```bash
# Delete inserted personas
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c \
  "DELETE FROM patient_personas WHERE persona_id LIKE '%_persona';"
```

### Task 3 Rollback
```bash
# Revert git changes
git checkout backend/src/api/v1/personas.py
git checkout backend/src/api/v1/router.py
git checkout frontend/src/pages/OSCEPractice.tsx
git checkout frontend/src/services/api.ts
```

---

## 📊 Estimated Timeline

| Task | Agent | Time | Dependencies |
|------|-------|------|--------------|
| **Task 1** | testing-qa-expert | 30 min | None |
| **Task 2** | rust-ffi-expert | 1 hour | None |
| **Task 3A** | flutter-desktop-expert | 45 min | Task 2 (for testing) |
| **Task 3B** | flutter-desktop-expert | 1 hour | Task 3A |
| **TOTAL** | - | **2-3 hours** | - |

---

## 🎯 Approval Required

Before proceeding, please confirm:
1. ✅ Execute Task 1 (Fix QA Validator)?
2. ✅ Execute Task 2 (Database Insertion)?
3. ✅ Execute Task 3 (Frontend Integration)?
4. ✅ Use Agent OS expert agents for execution?
5. ✅ Follow all constraints from PROJECT_CONSTRAINTS.md?

**Awaiting user approval to proceed...**
