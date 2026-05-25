# PRD: EMR Validation Endpoints Implementation

**PRD ID**: PRD-EMR-VAL-001
**Created**: 2026-05-23
**Status**: READY FOR IMPLEMENTATION
**Priority**: HIGH
**Estimated Effort**: 4-6 hours
**Expected Impact**: +16 tests (88.8% → 91.1% pass rate)

---

## 1. Executive Summary

### Objective
Implement 3 EMR validation endpoints to provide real-time feedback on student clinical documentation using a 3-layer validation approach (Pydantic → Python → AI).

### Success Criteria
- [ ] All 16 validation tests passing (100%)
- [ ] 3 endpoints implemented and functional
- [ ] Claude API integration working
- [ ] PBS drug database lookup operational
- [ ] MBS pathology codes validated
- [ ] <500ms p95 response time
- [ ] Australian medical standards enforced

### Current Status
- Tests exist: 16 tests in `tests/test_api/test_emr/test_emr_validation.py`
- Tests failing: All return 404 (endpoints not implemented)
- API routes: Not registered in router
- Business logic: Not implemented

---

## 2. Technical Specification

### 2.1 Endpoints to Implement

#### Endpoint 1: SOAP Note Validation
```
POST /api/v1/emr/validation/soap-note
```

**Request Schema**:
```python
class SOAPNoteValidationRequest(BaseModel):
    session_id: str  # UUID of EMR session
    soap_note: SOAPNoteSubmit  # From existing schema
    patient_context: dict  # Patient demographics, history

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "soap_note": {
                    "subjective": "55yo M with sudden onset chest pain...",
                    "objective": "BP 145/90, HR 98, irregular pulse...",
                    "assessment": "Acute Coronary Syndrome - Inferior STEMI",
                    "plan": "Aspirin 300mg stat, morphine 5mg IV..."
                },
                "patient_context": {
                    "age": 55,
                    "sex": "M",
                    "presenting_complaint": "Chest pain",
                    "specialty": "cardiology"
                }
            }
        }
    )
```

**Response Schema**:
```python
class ValidationResult(BaseModel):
    overall_score: float  # 0-15 (AMC scale)
    passed: bool  # >= 9/15
    category_scores: Dict[str, float]  # 5 AMC categories × 3 marks
    feedback: List[ValidationFeedback]
    australian_compliance: AustralianComplianceCheck
    processing_time_ms: int

class ValidationFeedback(BaseModel):
    category: str  # "history_examination", "clinical_reasoning", etc.
    score: float  # 0-3
    strengths: List[str]
    improvements: List[str]
    citations: List[str]  # eTG references

class AustralianComplianceCheck(BaseModel):
    terminology_correct: bool  # "paracetamol" not "acetaminophen"
    etg_compliant: bool  # Follows eTG guidelines
    pbs_aware: bool  # Mentions PBS restrictions if applicable
    issues: List[str]
```

**3-Layer Validation**:
1. **Layer 1 (Pydantic)**: Schema validation, required fields
2. **Layer 2 (Python)**: Business logic, terminology checks, completeness
3. **Layer 3 (AI - Claude)**: Clinical reasoning, eTG compliance, AMC rubric scoring

#### Endpoint 2: Prescription Validation
```
POST /api/v1/emr/validation/prescription
```

**Request Schema**:
```python
class PrescriptionValidationRequest(BaseModel):
    prescription: PrescriptionSubmit  # From existing schema
    patient_context: dict
    indication: str  # Clinical justification

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prescription": {
                    "medication": "Aspirin",
                    "dose": "100mg",
                    "frequency": "daily",
                    "duration": "ongoing",
                    "clinical_notes": "Secondary prevention post-STEMI"
                },
                "patient_context": {
                    "age": 58,
                    "allergies": ["Penicillin"],
                    "current_medications": ["Atorvastatin 40mg"],
                    "diagnosis": "Acute Coronary Syndrome"
                },
                "indication": "Secondary prevention following inferior STEMI"
            }
        }
    )
```

**Response Schema**:
```python
class PrescriptionValidationResult(BaseModel):
    approved: bool
    safety_score: float  # 0-10
    pbs_compliance: PBSComplianceCheck
    drug_interactions: List[DrugInteraction]
    dose_appropriateness: DoseCheck
    feedback: List[str]

class PBSComplianceCheck(BaseModel):
    pbs_listed: bool
    authority_required: bool
    restrictions_met: bool
    max_repeats: int
    patient_copay: Optional[float]  # Australian PBS copay

class DrugInteraction(BaseModel):
    severity: str  # "minor", "moderate", "severe"
    interacting_drug: str
    effect: str
    recommendation: str

class DoseCheck(BaseModel):
    within_range: bool
    recommended_dose: str
    patient_specific_factors: List[str]  # Age, renal function, etc.
```

**PBS Database Lookup**:
- Integration with PBS API or local database
- Australian drug name validation
- Authority script requirements
- Generic vs brand name handling

#### Endpoint 3: Pathology Order Validation
```
POST /api/v1/emr/validation/pathology-order
```

**Request Schema**:
```python
class PathologyOrderValidationRequest(BaseModel):
    tests_ordered: List[str]  # Test names
    indication: str
    patient_context: dict
    urgency: str  # "routine", "urgent", "stat"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tests_ordered": ["FBC", "UEC", "Troponin", "D-dimer"],
                "indication": "Chest pain, ?ACS, ?PE",
                "patient_context": {
                    "age": 65,
                    "presenting_complaint": "Chest pain and dyspnoea",
                    "risk_factors": ["Smoking", "Hypertension"]
                },
                "urgency": "urgent"
            }
        }
    )
```

**Response Schema**:
```python
class PathologyValidationResult(BaseModel):
    appropriateness_score: float  # 0-10
    mbs_items: List[MBSItem]
    overuse_warnings: List[str]
    missing_tests: List[str]  # Recommended additional tests
    cost_estimate: float  # Australian MBS rebate
    feedback: str

class MBSItem(BaseModel):
    test_name: str
    mbs_item_number: str
    rebate_amount: float
    bulk_billable: bool
    notes: str
```

**MBS Database**:
- MBS item number lookup
- Appropriate use criteria
- Cost estimation
- Overuse detection (e.g., daily troponins)

---

## 3. Implementation Plan

### Phase 1: Schema Definitions (30 minutes)

**File**: `src/api/v1/emr/validation_schemas.py` (NEW)

**Tasks**:
1. Create request/response schemas for all 3 endpoints
2. Add Pydantic V2 validators
3. Add Australian terminology validators
4. Define AMC rubric categories
5. Add example payloads

**Validation**:
```bash
# Import test
python -c "from src.api.v1.emr.validation_schemas import *; print('Schemas OK')"
```

### Phase 2: Business Logic Layer (1.5 hours)

**File**: `src/services/emr_validation_service.py` (NEW)

**Tasks**:
1. **SOAP Note Validator**:
   - Completeness checker (all SOAP sections present)
   - Terminology validator (Australian vs American)
   - Red flag detector (chest pain + cardiac risk factors)
   - eTG guideline checker

2. **Prescription Validator**:
   - PBS database integration
   - Drug interaction checker
   - Dose range validator
   - Australian drug name validator

3. **Pathology Validator**:
   - MBS item lookup
   - Appropriateness checker
   - Overuse detector
   - Cost calculator

**Example Implementation**:
```python
class EMRValidationService:
    def __init__(self):
        self.pbs_db = load_pbs_database()
        self.mbs_db = load_mbs_database()
        self.etg_guidelines = load_etg_guidelines()

    async def validate_soap_note(
        self,
        soap_note: SOAPNoteSubmit,
        patient_context: dict
    ) -> SOAPNoteValidationResult:
        # Layer 1: Pydantic (already done)

        # Layer 2: Python business logic
        completeness = self._check_completeness(soap_note)
        terminology = self._check_australian_terminology(soap_note)
        red_flags = self._detect_red_flags(soap_note, patient_context)

        # Layer 3: AI validation (Claude)
        ai_feedback = await self._get_claude_validation(
            soap_note,
            patient_context,
            self.etg_guidelines
        )

        return self._combine_validation_results(
            completeness, terminology, red_flags, ai_feedback
        )
```

**Validation**:
```bash
# Unit tests
pytest tests/test_services/test_emr_validation_service.py -v
```

### Phase 3: Claude API Integration (1 hour)

**File**: `src/ai/clinical_validator.py` (NEW)

**Tasks**:
1. Create Claude prompt templates for each validation type
2. Implement streaming response handling
3. Add retry logic with exponential backoff
4. Parse Claude JSON responses
5. Add caching for common validations

**Example Prompt Template**:
```python
SOAP_VALIDATION_PROMPT = """
You are an Australian medical educator assessing a medical student's SOAP note.

Patient Context:
{patient_context}

Student's SOAP Note:
{soap_note}

Australian Guidelines (eTG):
{etg_guidelines}

Assess using AMC Clinical Examination rubric (15 marks total):
1. History & Examination (0-3): Completeness, relevance, red flags
2. Clinical Reasoning (0-3): Differential diagnosis, appropriate investigations
3. Communication (0-3): Clear documentation, patient-centered language
4. Safety (0-3): Red flag recognition, appropriate urgency, harm prevention
5. Professionalism (0-3): eTG compliance, Australian terminology, evidence-based

Return JSON:
{{
  "overall_score": 12.5,
  "category_scores": {{
    "history_examination": 2.5,
    "clinical_reasoning": 2.5,
    "communication": 2.5,
    "safety": 3.0,
    "professionalism": 2.0
  }},
  "feedback": [
    {{
      "category": "history_examination",
      "strengths": ["Complete cardiac risk factor assessment"],
      "improvements": ["Missing pain radiation details"],
      "citations": ["eTG Cardiovascular - Acute Coronary Syndromes"]
    }}
  ],
  "australian_compliance": {{
    "terminology_correct": true,
    "etg_compliant": true,
    "pbs_aware": true,
    "issues": []
  }}
}}
"""
```

**Validation**:
```bash
# Integration test
pytest tests/test_ai/test_clinical_validator.py -v
```

### Phase 4: API Router Implementation (30 minutes)

**File**: `src/api/v1/emr/validation.py` (UPDATE - currently exists but has no endpoints)

**Tasks**:
1. Import schemas and services
2. Implement 3 endpoint handlers
3. Add rate limiting (10 requests/minute per user)
4. Add response caching (5 minute TTL)
5. Add authentication middleware
6. Add request logging

**Example Implementation**:
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi_limiter.depends import RateLimiter
from src.api.v1.emr.validation_schemas import *
from src.services.emr_validation_service import EMRValidationService
from src.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/validation", tags=["EMR Validation"])

@router.post(
    "/soap-note",
    response_model=SOAPNoteValidationResult,
    dependencies=[Depends(RateLimiter(times=10, minutes=1))]
)
async def validate_soap_note(
    request: SOAPNoteValidationRequest,
    current_user: User = Depends(get_current_active_user),
    validation_service: EMRValidationService = Depends()
):
    """
    Validate SOAP note using 3-layer approach:
    1. Schema validation (Pydantic)
    2. Business logic (Python)
    3. Clinical reasoning (Claude AI)

    Returns AMC rubric scores and detailed feedback.
    """
    start_time = time.time()

    try:
        result = await validation_service.validate_soap_note(
            soap_note=request.soap_note,
            patient_context=request.patient_context
        )

        result.processing_time_ms = int((time.time() - start_time) * 1000)

        return result

    except Exception as e:
        logger.error(f"SOAP validation failed: {e}")
        raise HTTPException(500, "Validation service unavailable")
```

**Validation**:
```bash
# Router import test
python -c "from src.api.v1.emr.validation import router; print('Router OK')"
```

### Phase 5: Test Fixes (1 hour)

**File**: `tests/test_api/test_emr/test_emr_validation.py` (UPDATE)

**Tasks**:
1. Update mock fixtures to match new schemas
2. Add Claude API mocking
3. Fix PBS/MBS database mocking
4. Update assertions for new response formats
5. Add latency tests
6. Add rate limiting tests

**Example Test Update**:
```python
# BEFORE (FAILS - endpoint doesn't exist)
def test_validate_soap_note_success_high_score(client, auth_headers):
    response = client.post("/api/v1/emr/validation/soap-note", ...)
    assert response.status_code == 404  # ❌ Not Found

# AFTER (PASSES - endpoint implemented)
@patch("src.services.emr_validation_service.ClaudeClient")
def test_validate_soap_note_success_high_score(
    mock_claude, client, auth_headers, mock_soap_note, mock_patient
):
    # Mock Claude response
    mock_claude.return_value.messages.create.return_value = {
        "content": [{"text": json.dumps({
            "overall_score": 12.5,
            "category_scores": {...},
            "feedback": [...]
        })}]
    }

    response = client.post(
        "/api/v1/emr/validation/soap-note",
        json={
            "session_id": str(uuid.uuid4()),
            "soap_note": mock_soap_note,
            "patient_context": mock_patient
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] >= 9.0  # Pass threshold
    assert "category_scores" in data
    assert len(data["feedback"]) > 0
```

**Validation**:
```bash
pytest tests/test_api/test_emr/test_emr_validation.py -v
# Expected: 16/16 passing
```

### Phase 6: Integration & Documentation (30 minutes)

**Tasks**:
1. Register validation router in main router
2. Update OpenAPI documentation
3. Add example requests/responses
4. Update COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md
5. Create validation endpoint guide
6. Add monitoring/logging

**File Updates**:
- `src/api/v1/router.py` - Add validation router
- `docs/api/emr-validation.md` - Endpoint documentation
- `COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md` - Update status

---

## 4. Dependencies & Resources

### External APIs
- **Claude API** (Sonnet 4.5): Clinical validation
- **PBS API** (optional): Real-time drug lookups
- **MBS API** (optional): Real-time pathology lookups

### Databases
- **PBS Database**: Australian drug formulary (CSV/JSON)
  - Source: https://www.pbs.gov.au/info/publication/schedule/archive
  - ~4000 drugs with pricing, restrictions

- **MBS Database**: Medicare Benefits Schedule (CSV/JSON)
  - Source: http://www9.health.gov.au/mbs/search.cfm
  - ~5700 items with rebates, rules

- **eTG Guidelines**: Therapeutic Guidelines (Text extracts)
  - Source: https://tgldcdp.tg.org.au/ (requires subscription)
  - Cardiovascular, Respiratory, etc.

### Libraries
```python
# requirements.txt additions
anthropic==0.25.0  # Claude API client
redis==5.0.0  # Response caching
fastapi-limiter==0.1.5  # Rate limiting
```

---

## 5. Testing Strategy

### Unit Tests (30 tests)
- Schema validation (10 tests)
- Business logic validators (10 tests)
- Claude prompt formatting (5 tests)
- PBS/MBS lookups (5 tests)

### Integration Tests (16 tests - existing)
- SOAP note validation (6 tests)
- Prescription validation (5 tests)
- Pathology order validation (5 tests)

### Performance Tests (3 tests)
- p95 latency <500ms
- Rate limiting enforcement
- Cache hit rate >80%

---

## 6. Risks & Mitigation

### Risk 1: Claude API Latency
**Impact**: Validation takes >500ms
**Mitigation**:
- Implement response caching (Redis)
- Use Claude's batch API for non-real-time validation
- Add timeout with graceful degradation

### Risk 2: PBS/MBS Data Availability
**Impact**: Can't validate Australian compliance
**Mitigation**:
- Bundle static database snapshot
- Fallback to basic drug name checking
- Manual database updates quarterly

### Risk 3: eTG Guidelines Copyright
**Impact**: Can't redistribute full guidelines
**Mitigation**:
- Use guideline summaries only
- Reference eTG by title, not full text
- Link to eTG website for students

---

## 7. Success Metrics

### Functional
- [ ] 16/16 validation tests passing
- [ ] 3 endpoints responding 200 OK
- [ ] Claude API integration working
- [ ] PBS/MBS lookups functional

### Performance
- [ ] p95 latency <500ms
- [ ] p99 latency <1000ms
- [ ] Cache hit rate >80%
- [ ] Rate limiting prevents abuse

### Quality
- [ ] Zero errors in error log
- [ ] Australian terminology enforced
- [ ] AMC rubric scoring accurate
- [ ] eTG citations present

---

## 8. Rollout Plan

### Step 1: Schema + Router (1 hour)
- Implement schemas
- Add empty endpoint handlers
- Return 501 Not Implemented with proper schema

### Step 2: Layer 2 Validation (1.5 hours)
- Implement Python business logic
- PBS/MBS database integration
- Return validation results without AI

### Step 3: Layer 3 AI (1 hour)
- Claude API integration
- Combine Layer 2 + Layer 3 results
- Full validation pipeline working

### Step 4: Test Fixes (1 hour)
- Update test fixtures
- Mock external APIs
- All 16 tests passing

### Step 5: Polish (30 min)
- Documentation
- Monitoring
- Cache tuning

---

## 9. Acceptance Criteria

**Definition of Done**:
- [ ] All 16 validation tests passing (100%)
- [ ] 3 endpoints implemented and documented
- [ ] Claude API integration complete
- [ ] PBS/MBS databases integrated
- [ ] Rate limiting configured
- [ ] Response caching working
- [ ] OpenAPI docs updated
- [ ] Test pass rate: 625/686 (91.1%) ✅ **90% MILESTONE EXCEEDED**
- [ ] Zero errors maintained
- [ ] Code reviewed and merged

---

## 10. Timeline

| Phase | Duration | Cumulative | Deliverable |
|-------|----------|------------|-------------|
| Phase 1: Schemas | 30 min | 0:30 | validation_schemas.py |
| Phase 2: Business Logic | 1.5 hours | 2:00 | emr_validation_service.py |
| Phase 3: Claude API | 1 hour | 3:00 | clinical_validator.py |
| Phase 4: API Router | 30 min | 3:30 | validation.py updated |
| Phase 5: Test Fixes | 1 hour | 4:30 | 16/16 tests passing |
| Phase 6: Integration | 30 min | 5:00 | Documentation complete |

**Total Estimated Time**: 5 hours
**Buffer for Issues**: 1 hour
**Total**: **6 hours maximum**

---

**Status**: READY FOR IMPLEMENTATION
**Next Action**: Create validation_schemas.py and begin Phase 1
**Expected Outcome**: 91.1% test pass rate (+2.3% from current 88.8%)
