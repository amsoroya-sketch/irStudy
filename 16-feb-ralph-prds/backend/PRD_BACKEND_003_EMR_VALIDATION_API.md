# PRD: EMR 3-Layer Validation API

**PRD ID**: PRD_BACKEND_003_EMR_VALIDATION_API
**Category**: Backend
**Priority**: P0-Critical (BLOCKS frontend validation display)
**Estimated Effort**: 12-16 hours
**Dependencies**: PRD_BACKEND_001 (Database), PRD_BACKEND_002 (Session API)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story
**As a** medical student practicing EMR documentation
**I want** instant, detailed feedback on my SOAP notes, prescriptions, and pathology orders
**So that** I can learn Australian medical standards, improve clinical reasoning, and prepare for AMC Clinical Examination

### Business Context
The Validation API is the **intelligence layer** of the EMR Practice System, providing:

1. **3-Layer Validation System** (Progressive Enhancement):
   - **Layer 1 (Zod - Client)**: <50ms - Instant field validation (character counts, required fields)
   - **Layer 2 (Python - Server)**: <1s - Australian compliance (PBS, MBS, terminology, safety checks)
   - **Layer 3 (Claude AI)**: 3-5s - Clinical reasoning (AMC 15-mark rubric, eTG/AMH alignment)

2. **SOAP Note Validation**:
   - Structural completeness (all 4 sections present, minimum length)
   - Clinical accuracy (diagnosis matches presentation)
   - Australian terminology (paracetamol not acetaminophen, 000 not 911)
   - Red flag identification (chest pain → ECG, headache → CT head)
   - Safety netting (follow-up plans, when to return)
   - AMC 15-mark rubric scoring (Communication 0-3, Clinical Reasoning 0-4, etc.)

3. **Prescription Validation**:
   - PBS compliance (medication listed, authority requirements)
   - Dose appropriateness (age, weight, renal/hepatic function)
   - Drug interactions (check against current medications)
   - Allergy checking (critical safety)
   - Indication completeness (PBS requirement)
   - Max 5 repeats enforcement

4. **Pathology Validation**:
   - MBS appropriateness (correct item number for indication)
   - Over-investigation detection (unnecessary tests)
   - Urgency appropriateness (Routine vs Urgent vs Emergency)
   - Indication completeness (minimum 10 characters)

5. **Australian Guideline Alignment**:
   - eTG (Therapeutic Guidelines) references
   - AMH (Australian Medicines Handbook) citations
   - AHPRA clinical documentation standards
   - NSW Health EMR protocols

This API must deliver **educational feedback** that helps students learn, not just pass/fail scoring.

### Success Metrics
- **Layer 1 (Zod) Latency**: <50ms (imperceptible to user)
- **Layer 2 (Python) Latency**: <1s (acceptable for real-time)
- **Layer 3 (Claude AI) Latency**: 3-5s (user sees "Analyzing..." spinner)
- **Validation Accuracy**: 90%+ agreement with human clinical educator
- **Feedback Quality**: 85%+ users rate feedback as "helpful" or "very helpful"
- **Australian Compliance Detection**: 95%+ accuracy (American terms flagged)
- **Red Flag Detection**: 100% for critical safety issues (chest pain, severe headache, sepsis)
- **Test Coverage**: ≥70% (unit + integration)
- **Test Pass Rate**: 100% (zero-tolerance)

### Scope
**In Scope**:
- 3-layer validation architecture (Zod schemas, Python validators, Claude AI agents)
- 3 validation endpoints (POST /validate/soap-note, POST /validate/prescription, POST /validate/pathology)
- SOAP note validator (AMC 15-mark rubric + Australian standards)
- Prescription validator (PBS compliance + safety checks)
- Pathology validator (MBS compliance + appropriateness)
- Australian terminology checker (paracetamol, salbutamol, adrenaline, 000)
- Red flag detection (chest pain, headache, sepsis, trauma, obstetric emergencies)
- eTG/AMH/AHPRA guideline integration (RAG retrieval from Qdrant)
- Validation result storage (emr_validation_results table)
- Feedback formatting (errors, warnings, insights, strengths, improvements)

**Out of Scope** (Future Iterations):
- Real-time validation during typing (only on submit)
- Machine learning model training (use Claude AI directly)
- Multi-language support (English only for AMC)
- Drug interaction database (use simple hardcoded list for MVP)
- Continuous learning from user feedback (manual improvement for MVP)

---

## A - ARCHITECTURE (How)

### Technical Approach
Build 3-layer validation system following separation of concerns:
- **Layer 1 (Zod)**: Client-side TypeScript schemas (handled by frontend PRDs)
- **Layer 2 (Python)**: FastAPI endpoints with rule-based validators
- **Layer 3 (Claude AI)**: Anthropic API integration with RAG context from Qdrant

Use existing patterns from OSCE validation (if exists) and RAG system (Qdrant with 9,950 medical chunks).

### System Design

#### Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React + MUI)                     │
│  User submits SOAP note + prescriptions + pathology          │
└────────────────────────┬────────────────────────────────────┘
                         │ POST /sessions/{id}/submit
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Session API (PRD_BACKEND_002)                   │
│  1. Save SOAP note to emr_soap_notes                         │
│  2. Save prescriptions to emr_prescriptions                  │
│  3. Save pathology orders to emr_pathology_orders            │
│  4. Mark session complete                                    │
└────────────────────────┬────────────────────────────────────┘
                         │ Trigger validation (async)
                         │
┌────────────────────────▼────────────────────────────────────┐
│           Validation API (THIS PRD - 3 Layers)               │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  LAYER 2: Python Validators (Rule-Based) <1s          │ │
│  │  - SOAPNoteValidator.validate_structure()             │ │
│  │  - PrescriptionValidator.validate_pbs_compliance()    │ │
│  │  - PathologyValidator.validate_mbs_appropriateness()  │ │
│  │  - AustralianTerminologyChecker.detect_violations()   │ │
│  │  - RedFlagDetector.check_safety_concerns()            │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │ If Layer 2 passes (no critical errors)
│                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  LAYER 3: Claude AI Validators (Clinical) 3-5s       │ │
│  │  - SOAPNoteAIValidator (AMC 15-mark rubric)           │ │
│  │  - PrescriptionAIValidator (clinical appropriateness) │ │
│  │  - PathologyAIValidator (investigation rationale)     │ │
│  │                                                        │ │
│  │  Integration:                                          │ │
│  │  - Anthropic API (claude-sonnet-4-5-20250929)         │ │
│  │  - RAG Context (Qdrant - eTG/AMH/AHPRA chunks)        │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Validation Result Aggregator                          │ │
│  │  - Combine Layer 2 + Layer 3 feedback                  │ │
│  │  - Calculate overall score (0-100)                     │ │
│  │  - Format feedback (errors, warnings, insights)        │ │
│  │  - Store in emr_validation_results table               │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              PostgreSQL Database                             │
│  - emr_validation_results (store feedback)                   │
│  - emr_soap_notes (update validation_score)                  │
│  - emr_prescriptions (update validation_score)               │
│  - emr_pathology_orders (update validation_score)            │
└──────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Qdrant Vector DB                           │
│  - 9,950 medical chunks (eTG, AMH, AHPRA)                    │
│  - Retrieve top 5 relevant chunks for RAG context            │
└──────────────────────────────────────────────────────────────┘
```

#### Data Flow: SOAP Note Validation
```
1. User submits session → POST /sessions/{id}/submit
   ↓
2. Session API saves SOAP note to database
   ↓
3. Session API triggers validation (async background task)
   ↓
4. Validation API → Layer 2 (Python Rules):
   - Check structure: All 4 sections present? Minimum 50 chars each?
   - Check Australian terminology: Any "acetaminophen" → Flag as error
   - Check red flags: "chest pain" in subjective → Check if ECG in plan
   - Check safety netting: Does plan include follow-up?
   ↓
   If Layer 2 finds CRITICAL errors (missing sections, American terms):
     → Return immediately (score: 0-40, status: "needs_revision")
   ↓
5. Validation API → Layer 3 (Claude AI):
   - Retrieve RAG context from Qdrant (top 5 chunks for patient's condition)
   - Build prompt:
     - Patient scenario
     - User's SOAP note
     - RAG context (eTG/AMH guidelines)
     - AMC 15-mark rubric
   - Call Claude API (claude-sonnet-4-5-20250929)
   - Parse JSON response:
     {
       "communication_score": 3,
       "clinical_reasoning_score": 3,
       "information_gathering_score": 3,
       "management_score": 2,
       "professionalism_score": 2,
       "total_amc_score": 13,
       "pass_status": true,
       "strengths": ["...", "...", "..."],
       "improvements": ["...", "...", "..."],
       "red_flags_identified": ["..."],
       "etg_alignment": true,
       "australian_compliant": true
     }
   ↓
6. Aggregate results:
   - Combine Layer 2 errors/warnings with Layer 3 feedback
   - Calculate overall_score: (Layer 2 score * 0.3) + (Layer 3 score * 0.7)
   - Format feedback JSON
   ↓
7. Store in emr_validation_results table:
   - validation_type: "soap_note"
   - validation_layer: 2 (one row), 3 (another row)
   - score, errors, warnings, insights
   ↓
8. Update emr_soap_notes.overall_validation_score
   ↓
9. Return validation_id to frontend
   ↓
10. Frontend polls GET /validation/{validation_id} until status="completed"
    ↓
11. Display feedback to user (red errors, yellow warnings, green insights)
```

### API Endpoints Specification

#### Endpoint 1: Validate SOAP Note
```python
POST /api/v1/emr/validate/soap-note
```

**Request Body**:
```python
class SOAPNoteValidationRequest(BaseModel):
    soap_note_id: str  # FK to emr_soap_notes.id
    patient_scenario_id: str  # For context

    # SOAP content (also in DB, but passed for convenience)
    subjective: str
    objective: str
    assessment: str
    plan: str

    # Validation options
    skip_ai: bool = False  # If True, only Layer 2 (faster for drafts)
    include_rag_context: bool = True  # Use Qdrant for Claude AI
```

**Response** (202 Accepted - Async):
```python
class ValidationQueueResponse(BaseModel):
    validation_id: str
    status: Literal["queued", "in_progress", "completed", "failed"]
    estimated_completion_seconds: int = 5
```

**Async Processing**:
- Background task runs Layer 2 → Layer 3
- User polls GET /validation/{validation_id}

---

#### Endpoint 2: Validate Prescription
```python
POST /api/v1/emr/validate/prescription
```

**Request Body**:
```python
class PrescriptionValidationRequest(BaseModel):
    prescription_id: str
    patient_scenario_id: str

    # Prescription details
    medication_name: str
    dose: str
    frequency: str
    route: str
    quantity: int
    repeats: int
    indication: str

    # Patient context for safety checks
    patient_age: int
    patient_allergies: List[str]
    patient_current_medications: List[str]
    patient_renal_function: Optional[str] = None  # "normal" | "impaired"
```

**Response** (200 OK - Synchronous):
```python
class PrescriptionValidationResponse(BaseModel):
    validation_score: float  # 0-100
    pbs_compliant: bool
    dose_appropriate: bool
    allergy_violation: bool

    errors: List[ValidationError]  # Critical (e.g., allergy violation)
    warnings: List[ValidationWarning]  # Non-critical (e.g., dose adjustment recommended)
    insights: List[ValidationInsight]  # Educational (e.g., PBS authority required)

    overall_status: Literal["safe", "needs_review", "unsafe"]

class ValidationError(BaseModel):
    field: str  # "medication_name", "dose", "allergy_check"
    message: str  # "CRITICAL: Patient allergic to Penicillin"
    severity: Literal["critical", "high", "medium"]
    suggestion: Optional[str]  # "Use alternative: Cephalexin"
```

**Validation Logic** (Layer 2 only - no AI needed):
1. PBS compliance check (medication in PBS database?)
2. Dose range validation (within BNF/AMH recommendations?)
3. Allergy cross-check (medication class vs patient allergies)
4. Drug interaction check (basic, e.g., warfarin + NSAIDs)
5. Repeats validation (≤5 as per PBS rules)
6. Indication completeness (≥5 characters)

---

#### Endpoint 3: Validate Pathology Order
```python
POST /api/v1/emr/validate/pathology
```

**Request Body**:
```python
class PathologyValidationRequest(BaseModel):
    pathology_order_id: str
    patient_scenario_id: str

    # Pathology details
    test_name: str
    urgency: Literal["Routine", "Urgent", "Emergency"]
    clinical_indication: str
    is_panel: bool
    panel_tests: List[str] = []

    # Patient context
    patient_presenting_complaint: str
    patient_diagnosis: Optional[str]
```

**Response** (200 OK):
```python
class PathologyValidationResponse(BaseModel):
    validation_score: float
    mbs_compliant: bool
    indication_appropriate: bool
    over_investigation_detected: bool
    urgency_appropriate: bool

    errors: List[ValidationError]
    warnings: List[ValidationWarning]
    insights: List[ValidationInsight]

    mbs_item_suggestion: Optional[str]  # "65070 for FBC"
```

**Validation Logic**:
1. MBS item number lookup (test_name → MBS code)
2. Indication appropriateness (clinical_indication matches diagnosis?)
3. Over-investigation check (e.g., ordering full panel when only FBC needed)
4. Urgency validation (e.g., "Emergency" troponin for chest pain → appropriate)

---

#### Endpoint 4: Get Validation Result
```python
GET /api/v1/emr/validation/{validation_id}
```

**Response** (200 OK):
```python
class ValidationResultResponse(BaseModel):
    validation_id: str
    validation_type: Literal["soap_note", "prescription", "pathology"]
    status: Literal["queued", "in_progress", "completed", "failed"]

    # If completed:
    overall_score: Optional[float]
    layer2_score: Optional[float]
    layer3_score: Optional[float]

    errors: List[ValidationError]
    warnings: List[ValidationWarning]
    insights: List[ValidationInsight]

    # SOAP note specific (if type="soap_note"):
    amc_rubric_scores: Optional[AMCRubricScores]
    strengths: List[str]
    improvements: List[str]

    # Performance metrics
    validation_latency_ms: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]

class AMCRubricScores(BaseModel):
    communication_score: int  # 0-3
    clinical_reasoning_score: int  # 0-4
    information_gathering_score: int  # 0-3
    management_score: int  # 0-3
    professionalism_score: int  # 0-2
    total_amc_score: int  # 0-15
    pass_status: bool  # ≥9/15
```

---

### Technology Stack
- **Framework**: FastAPI 0.109+
- **AI Integration**: Anthropic Python SDK (claude-sonnet-4-5-20250929)
- **RAG System**: Qdrant client (existing, 9,950 medical chunks)
- **Validation Libraries**:
  - Pydantic 2.5+ (schema validation)
  - Custom PBS database (JSON file with 4,000+ medications)
  - Custom MBS database (JSON file with common pathology codes)
- **Background Tasks**: FastAPI BackgroundTasks (for async Layer 3 validation)
- **Caching**: Redis (cache Claude API responses for identical SOAP notes)

### Integration Points
- **Integrates with**:
  - Session API (PRD_BACKEND_002) - triggered after session submit
  - Qdrant Vector DB (RAG context retrieval)
  - Anthropic API (Claude Sonnet 4.5)
  - PostgreSQL (emr_validation_results table)
- **Consumed by**:
  - Frontend validation display (PRD_FRONTEND_004)
  - Dashboard analytics (PRD_FRONTEND_003)

### Security Considerations
- [x] API key for Claude stored in Vault (NEVER hardcoded)
- [x] Rate limiting: 20 Claude API calls/minute per user (cost control)
- [x] Input sanitization (prevent prompt injection attacks)
- [x] JWT authentication on all endpoints
- [x] No PHI sent to Claude (anonymize patient names, use placeholders)
- [x] Audit logging (all validation requests logged with user_id, timestamp)

### Performance Requirements
- **Layer 2 (Python Rules)**: <1s for all validators
- **Layer 3 (Claude AI)**: 3-5s (acceptable with "Analyzing..." spinner)
- **Overall Validation**: <6s end-to-end (Layer 2 + Layer 3)
- **Qdrant RAG Retrieval**: <200ms (top 5 chunks)
- **Database Write**: <100ms (store validation result)
- **Concurrent Validations**: 50+ users simultaneously
- **Claude API Rate Limit**: 20 requests/minute (enforced by Redis)

---

## L - LOOP (Iterative Development)

### Phase 1: Layer 2 Validators (40% of effort, 5-6 hours)
**Goal**: Implement rule-based Python validators

**Tasks**:
1. Create validator base classes - 30 min
2. Implement SOAPNoteValidator (structure, terminology, red flags) - 2 hours
3. Implement PrescriptionValidator (PBS, dose, allergies) - 1.5 hours
4. Implement PathologyValidator (MBS, appropriateness) - 1 hour
5. Create AustralianTerminologyChecker - 1 hour

**Validation Gate**:
- [ ] All Layer 2 validators return structured feedback
- [ ] Australian terminology violations detected (100% accuracy on test cases)
- [ ] Red flags detected (chest pain → ECG check = 100% accuracy)
- [ ] PBS compliance checked (medication in database)
- [ ] Unit tests ≥70% coverage

---

### Phase 2: Layer 3 Claude AI Integration (40% of effort, 5-6 hours)
**Goal**: Integrate Claude Sonnet 4.5 with RAG context

**Tasks**:
1. Create Claude AI service wrapper - 1 hour
2. Implement RAG context retrieval (Qdrant) - 1.5 hours
3. Build SOAP note AI validator (AMC rubric prompt) - 2 hours
4. Implement prompt injection protection - 30 min
5. Add Redis caching for Claude responses - 1 hour

**Validation Gate**:
- [ ] Claude API integration working
- [ ] RAG context retrieved (<200ms)
- [ ] AMC 15-mark rubric scores returned
- [ ] Feedback is educational (strengths + improvements)
- [ ] Validation accuracy ≥85% vs human educator (test on 20 sample SOAP notes)

---

### Phase 3: API Endpoints + Testing (20% of effort, 2-4 hours)
**Goal**: Expose validation via REST APIs

**Tasks**:
1. Create FastAPI router - 30 min
2. Implement POST /validate/soap-note (async) - 1 hour
3. Implement POST /validate/prescription (sync) - 45 min
4. Implement GET /validation/{id} - 30 min
5. Write integration tests - 1.5 hours

**Validation Gate**:
- [ ] All 4 endpoints working
- [ ] Async validation queues correctly
- [ ] Frontend can poll for results
- [ ] Integration tests 100% pass rate
- [ ] Performance targets met (<6s total)

---

## P - PLAN (Detailed Implementation)

### Phase 1 Tasks

**Task 1.1**: Create Validator Base Classes
- **Effort**: 30 min
- **File**: `/backend/src/services/emr/validators/base.py`
- **Code**:
  ```python
  from abc import ABC, abstractmethod
  from pydantic import BaseModel
  from typing import List, Optional

  class ValidationError(BaseModel):
      field: str
      message: str
      severity: str = "high"  # "critical" | "high" | "medium" | "low"
      suggestion: Optional[str] = None

  class ValidationWarning(BaseModel):
      field: str
      message: str
      suggestion: Optional[str] = None

  class ValidationInsight(BaseModel):
      category: str  # "australian_standards" | "clinical_practice" | "safety"
      message: str
      reference: Optional[str] = None  # eTG, AMH, AHPRA reference

  class ValidationResult(BaseModel):
      score: float  # 0-100
      errors: List[ValidationError] = []
      warnings: List[ValidationWarning] = []
      insights: List[ValidationInsight] = []
      status: str = "pass"  # "pass" | "needs_review" | "fail"

  class BaseValidator(ABC):
      @abstractmethod
      def validate(self, data: dict) -> ValidationResult:
          pass
  ```

**Task 1.2**: Implement SOAPNoteValidator
- **Effort**: 2 hours
- **File**: `/backend/src/services/emr/validators/soap_note_validator.py`
- **Validation Rules**:
  ```python
  class SOAPNoteValidator(BaseValidator):
      def validate(self, data: dict) -> ValidationResult:
          result = ValidationResult(score=100.0)

          # Rule 1: Structure completeness
          if len(data.get("subjective", "")) < 50:
              result.errors.append(ValidationError(
                  field="subjective",
                  message="Subjective section too brief (minimum 50 characters)",
                  severity="high",
                  suggestion="Include: chief complaint, HPI, relevant PMHx, medications"
              ))
              result.score -= 20

          # Rule 2: Australian terminology
          american_terms = {
              "acetaminophen": "paracetamol",
              "epinephrine": "adrenaline",
              "albuterol": "salbutamol",
              "911": "000"
          }

          full_text = f"{data.get('subjective', '')} {data.get('objective', '')} {data.get('assessment', '')} {data.get('plan', '')}".lower()

          for american, australian in american_terms.items():
              if american in full_text:
                  result.errors.append(ValidationError(
                      field="terminology",
                      message=f"American term '{american}' used",
                      severity="critical" if american == "911" else "high",
                      suggestion=f"Use Australian term: '{australian}'"
                  ))
                  result.score -= 15

          # Rule 3: Red flag detection
          if "chest pain" in data.get("subjective", "").lower():
              plan_lower = data.get("plan", "").lower()
              if not any(keyword in plan_lower for keyword in ["ecg", "troponin", "cardiac", "cardiology"]):
                  result.warnings.append(ValidationWarning(
                      field="plan",
                      message="Chest pain red flag: ECG and troponin not mentioned",
                      suggestion="For chest pain: ECG, troponin, consider ACS protocol"
                  ))
                  result.score -= 10

          # Rule 4: Safety netting
          plan_lower = data.get("plan", "").lower()
          if not any(keyword in plan_lower for keyword in ["follow-up", "review", "return if", "safety netting"]):
              result.warnings.append(ValidationWarning(
                  field="plan",
                  message="No follow-up or safety netting mentioned",
                  suggestion="Include: when to return, red flags to watch for"
              ))
              result.score -= 5

          # Rule 5: PBS/MBS mention (if medications/investigations ordered)
          if any(keyword in plan_lower for keyword in ["medication", "prescription", "drug"]):
              if "pbs" not in full_text:
                  result.insights.append(ValidationInsight(
                      category="australian_standards",
                      message="Consider mentioning PBS compliance for prescriptions",
                      reference="PBS - Pharmaceutical Benefits Scheme"
                  ))

          # Set status based on score
          if result.score >= 70:
              result.status = "pass"
          elif result.score >= 50:
              result.status = "needs_review"
          else:
              result.status = "fail"

          return result
  ```

**Task 1.3**: Implement PrescriptionValidator
- **Effort**: 1.5 hours
- **File**: `/backend/src/services/emr/validators/prescription_validator.py`
- **PBS Database**: Load from `/backend/data/pbs_medications.json` (create CSV→JSON converter)
- **Validation Rules**:
  ```python
  class PrescriptionValidator(BaseValidator):
      def __init__(self):
          self.pbs_db = self._load_pbs_database()
          self.drug_interactions = self._load_interactions()

      def _load_pbs_database(self) -> dict:
          # Load PBS JSON: {medication_name: {pbs_code, max_dose, contraindications}}
          import json
          with open("/backend/data/pbs_medications.json") as f:
              return json.load(f)

      def validate(self, data: dict) -> ValidationResult:
          result = ValidationResult(score=100.0)

          medication = data.get("medication_name", "").lower()
          dose = data.get("dose", "")
          repeats = data.get("repeats", 0)
          indication = data.get("indication", "")
          allergies = data.get("patient_allergies", [])

          # Rule 1: PBS compliance
          if medication not in self.pbs_db:
              result.errors.append(ValidationError(
                  field="medication_name",
                  message=f"{medication} not found in PBS database",
                  severity="high",
                  suggestion="Check spelling or use generic name"
              ))
              result.score -= 30

          # Rule 2: Repeats validation
          if repeats > 5:
              result.errors.append(ValidationError(
                  field="repeats",
                  message=f"Repeats ({repeats}) exceeds PBS maximum (5)",
                  severity="critical",
                  suggestion="Reduce to maximum 5 repeats"
              ))
              result.score -= 20

          # Rule 3: Allergy check (CRITICAL)
          for allergy in allergies:
              if self._check_allergy_match(medication, allergy):
                  result.errors.append(ValidationError(
                      field="allergy_check",
                      message=f"CRITICAL: Patient allergic to {allergy}",
                      severity="critical",
                      suggestion=f"Do NOT prescribe {medication}. Consider alternative."
                  ))
                  result.score = 0  # Automatic fail
                  result.status = "unsafe"
                  return result  # Return immediately

          # Rule 4: Indication completeness
          if len(indication) < 5:
              result.errors.append(ValidationError(
                  field="indication",
                  message="Indication required (PBS requirement)",
                  severity="high",
                  suggestion="Provide clear indication (minimum 5 characters)"
              ))
              result.score -= 15

          # Rule 5: Australian terminology in medication name
          if any(term in medication for term in ["acetaminophen", "albuterol"]):
              result.errors.append(ValidationError(
                  field="medication_name",
                  message="American drug name used",
                  severity="high",
                  suggestion="Use Australian generic name (paracetamol, salbutamol)"
              ))
              result.score -= 15

          # Set status
          if result.score >= 80:
              result.status = "safe"
          elif result.score >= 60:
              result.status = "needs_review"
          else:
              result.status = "unsafe"

          return result

      def _check_allergy_match(self, medication: str, allergy: str) -> bool:
          # Simple matching (extend with drug class matching later)
          allergy_lower = allergy.lower()
          medication_lower = medication.lower()

          # Exact match
          if allergy_lower in medication_lower or medication_lower in allergy_lower:
              return True

          # Class matching (basic)
          penicillin_class = ["penicillin", "amoxicillin", "ampicillin", "flucloxacillin"]
          if allergy_lower in penicillin_class and medication_lower in penicillin_class:
              return True

          return False
  ```

**Task 1.4**: Implement PathologyValidator
- **Effort**: 1 hour
- **File**: `/backend/src/services/emr/validators/pathology_validator.py`
- **Validation Rules**: MBS compliance, over-investigation, urgency

**Task 1.5**: Create AustralianTerminologyChecker
- **Effort**: 1 hour
- **File**: `/backend/src/services/emr/validators/terminology_checker.py`
- **Comprehensive List**:
  ```python
  AUSTRALIAN_TERMINOLOGY = {
      # Medications
      "acetaminophen": "paracetamol",
      "epinephrine": "adrenaline",
      "albuterol": "salbutamol",
      "norepinephrine": "noradrenaline",

      # Medical terms
      "primary care physician": "GP (General Practitioner)",
      "operating room": "operating theatre",
      "ER": "ED (Emergency Department)",

      # Emergency
      "911": "000",

      # Units (informational)
      "mg/dL": "mmol/L (use SI units)",
      "Fahrenheit": "Celsius"
  }
  ```

---

### Phase 2 Tasks

**Task 2.1**: Create Claude AI Service Wrapper
- **Effort**: 1 hour
- **File**: `/backend/src/services/emr/claude_service.py`
- **Code**:
  ```python
  from anthropic import Anthropic
  import os
  import json
  from typing import Optional

  class ClaudeValidationService:
      def __init__(self):
          api_key = os.getenv("CLAUDE_API_KEY")  # From Vault
          if not api_key:
              raise ValueError("CLAUDE_API_KEY not found in environment")

          self.client = Anthropic(api_key=api_key)
          self.model = "claude-sonnet-4-5-20250929"
          self.max_tokens = 3000
          self.temperature = 0.2  # Low for consistency

      async def validate_soap_note(
          self,
          soap_note: dict,
          patient_scenario: dict,
          rag_context: Optional[str] = None
      ) -> dict:
          """
          Use Claude to validate SOAP note with AMC 15-mark rubric.
          Returns structured JSON feedback.
          """
          prompt = self._build_soap_note_prompt(soap_note, patient_scenario, rag_context)

          response = await self.client.messages.create(
              model=self.model,
              max_tokens=self.max_tokens,
              temperature=self.temperature,
              messages=[{"role": "user", "content": prompt}]
          )

          # Parse JSON from response
          feedback = self._parse_json_response(response.content[0].text)
          return feedback

      def _build_soap_note_prompt(self, soap_note, patient, rag_context):
          return f"""You are an experienced Australian clinical educator reviewing a medical student's SOAP note for AMC Clinical Examination preparation.

PATIENT SCENARIO:
Name: {patient['full_name']}
Age: {patient['age']}
Presenting Complaint: {patient['presenting_complaint']}
Clinical Scenario: {patient['clinical_scenario']}

STUDENT'S SOAP NOTE:
Subjective: {soap_note['subjective']}
Objective: {soap_note['objective']}
Assessment: {soap_note['assessment']}
Plan: {soap_note['plan']}

RELEVANT AUSTRALIAN GUIDELINES:
{rag_context or 'No specific guidelines retrieved'}

Evaluate this SOAP note using the AMC 15-mark rubric. Provide feedback in this JSON format:

{{
  "communication_score": <0-3>,
  "clinical_reasoning_score": <0-4>,
  "information_gathering_score": <0-3>,
  "management_score": <0-3>,
  "professionalism_score": <0-2>,
  "total_amc_score": <0-15>,
  "pass_status": <true if ≥9, false otherwise>,

  "strengths": [
    "Specific strength 1",
    "Specific strength 2",
    "Specific strength 3"
  ],

  "improvements": [
    "Specific area to improve 1",
    "Specific area to improve 2",
    "Specific area to improve 3"
  ],

  "red_flags_identified": [
    "Any critical safety concerns (or empty array if none)"
  ],

  "etg_alignment": <true/false - does plan align with eTG guidelines?>,
  "australian_terminology_correct": <true/false>,
  "safety_netting_present": <true/false>,

  "overall_feedback": "2-3 sentences of constructive feedback"
}}

Be specific, constructive, and educational. Focus on AMC Clinical Examination readiness and Australian medical standards."""

      def _parse_json_response(self, text: str) -> dict:
          # Extract JSON from markdown code blocks if present
          if "```json" in text:
              start = text.find("```json") + 7
              end = text.find("```", start)
              text = text[start:end].strip()
          elif "```" in text:
              start = text.find("```") + 3
              end = text.find("```", start)
              text = text[start:end].strip()

          try:
              return json.loads(text)
          except json.JSONDecodeError as e:
              raise ValueError(f"Failed to parse Claude response as JSON: {e}")
  ```

**Task 2.2**: Implement RAG Context Retrieval
- **Effort**: 1.5 hours
- **File**: `/backend/src/services/emr/rag_service.py`
- **Integration**: Use existing Qdrant client
- **Code**:
  ```python
  from qdrant_client import QdrantClient
  from typing import List

  class RAGService:
      def __init__(self):
          self.client = QdrantClient(host="localhost", port=6333)
          self.collection_name = "medical_guidelines"  # Existing collection

      async def get_relevant_context(
          self,
          query: str,
          top_k: int = 5,
          min_score: float = 0.65
      ) -> str:
          """
          Retrieve top K relevant medical guideline chunks from Qdrant.
          Returns formatted context string for Claude prompt.
          """
          # Search Qdrant
          results = self.client.search(
              collection_name=self.collection_name,
              query_text=query,
              limit=top_k,
              score_threshold=min_score
          )

          if not results:
              return "No specific Australian guidelines found for this condition."

          # Format results
          context_parts = []
          for i, result in enumerate(results, 1):
              source = result.payload.get("source", "Unknown")
              text = result.payload.get("text", "")
              score = result.score

              context_parts.append(f"{i}. [{source}] (Confidence: {score:.2f})\n{text}\n")

          return "\n".join(context_parts)
  ```

**Task 2.3**: Build SOAP Note AI Validator
- **Effort**: 2 hours
- **File**: `/backend/src/services/emr/validators/soap_note_ai_validator.py`
- **Integration**: Combine ClaudeService + RAGService
- **Code**:
  ```python
  class SOAPNoteAIValidator:
      def __init__(self):
          self.claude_service = ClaudeValidationService()
          self.rag_service = RAGService()

      async def validate(
          self,
          soap_note: dict,
          patient_scenario: dict,
          include_rag: bool = True
      ) -> dict:
          """
          Layer 3 validation: Use Claude AI with RAG context.
          Returns AMC rubric scores + educational feedback.
          """
          # Get RAG context
          rag_context = None
          if include_rag:
              query = f"{patient_scenario['presenting_complaint']} {soap_note['assessment']}"
              rag_context = await self.rag_service.get_relevant_context(query)

          # Call Claude
          feedback = await self.claude_service.validate_soap_note(
              soap_note=soap_note,
              patient_scenario=patient_scenario,
              rag_context=rag_context
          )

          return feedback
  ```

**Task 2.4**: Implement Prompt Injection Protection
- **Effort**: 30 min
- **Sanitization**: Remove potential injection attempts from user input

**Task 2.5**: Add Redis Caching
- **Effort**: 1 hour
- **Cache Key**: Hash of (soap_note content + patient_scenario_id)
- **TTL**: 1 hour (responses shouldn't change for same content)

---

### Phase 3 Tasks

**Task 3.1**: Create FastAPI Router
- **Effort**: 30 min
- **File**: `/backend/src/api/v1/emr/validation.py`

**Task 3.2**: Implement POST /validate/soap-note (Async)
- **Effort**: 1 hour
- **Background Task**: Queue Layer 3 validation

**Task 3.3**: Implement POST /validate/prescription (Sync)
- **Effort**: 45 min
- **No AI needed**: Layer 2 only (fast response)

**Task 3.4**: Implement GET /validation/{id}
- **Effort**: 30 min
- **Polling endpoint**: Return status + results when complete

**Task 3.5**: Write Integration Tests
- **Effort**: 1.5 hours
- **Test Cases**: 20+ scenarios (happy path, errors, AI validation accuracy)

---

### Timeline

| Day | Phase | Tasks | Hours | Deliverable |
|-----|-------|-------|-------|-------------|
| Day 1 | Phase 1 | 1.1-1.3 | 4h | Layer 2 validators (structure, PBS) |
| Day 2 | Phase 1 | 1.4-1.5 | 2h | Pathology + terminology validators |
| Day 3 AM | Phase 2 | 2.1-2.3 | 4.5h | Claude AI + RAG integration |
| Day 3 PM | Phase 2 | 2.4-2.5 | 1.5h | Security + caching |
| Day 4 | Phase 3 | 3.1-3.5 | 4h | API endpoints + tests |

**Total**: 3-4 days, 12-16 hours effort

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] Layer 2 validators detect Australian terminology violations (100% on test set)
- [ ] Layer 2 validators detect red flags (chest pain → ECG check = 100%)
- [ ] Layer 2 prescription validator detects allergy violations (100% critical)
- [ ] Layer 3 Claude AI returns AMC 15-mark rubric scores
- [ ] Layer 3 feedback is educational (strengths + improvements)
- [ ] RAG context retrieved from Qdrant (<200ms)
- [ ] Validation results stored in database
- [ ] All 4 API endpoints working

#### Quality Requirements
- [ ] **Test Coverage**: ≥70% (validators, AI service, endpoints)
- [ ] **Test Pass Rate**: 100%
- [ ] **AI Validation Accuracy**: ≥85% vs human educator (test on 20 SOAP notes)
- [ ] **Code Quality**: No linting errors, follows FastAPI patterns

#### Performance Requirements
- [ ] **Layer 2**: <1s for all validators
- [ ] **Layer 3**: 3-5s (Claude API call)
- [ ] **Overall**: <6s end-to-end
- [ ] **RAG Retrieval**: <200ms
- [ ] **Claude Rate Limit**: 20 requests/minute enforced

#### Security Requirements
- [ ] **Claude API Key**: Stored in Vault (NEVER hardcoded)
- [ ] **Prompt Injection**: Sanitization implemented
- [ ] **Rate Limiting**: Redis-based, 20 requests/min per user
- [ ] **PHI Protection**: No patient names sent to Claude (use placeholders)
- [ ] **Audit Logging**: All validation requests logged

#### Australian Medical Compliance
- [ ] **Terminology Detection**: 100% accuracy on American terms
- [ ] **eTG/AMH Integration**: RAG retrieves Australian guidelines
- [ ] **AMC Rubric**: 15-mark scoring implemented
- [ ] **PBS Compliance**: Medication database covers 4,000+ drugs
- [ ] **MBS Compliance**: Pathology codes validated

---

### Testing Requirements

#### Unit Tests (≥70% coverage)
```python
# Test Layer 2 - SOAPNoteValidator
def test_australian_terminology_detection():
    validator = SOAPNoteValidator()
    soap_note = {
        "subjective": "Patient took acetaminophen for pain",
        "objective": "BP normal",
        "assessment": "Headache",
        "plan": "Continue acetaminophen"
    }
    result = validator.validate(soap_note)

    # Should detect "acetaminophen" → suggest "paracetamol"
    assert len(result.errors) >= 1
    assert any("acetaminophen" in e.message.lower() for e in result.errors)
    assert any("paracetamol" in e.suggestion.lower() for e in result.errors)

def test_red_flag_chest_pain_ecg_missing():
    validator = SOAPNoteValidator()
    soap_note = {
        "subjective": "65M with chest pain radiating to left arm",
        "objective": "BP 150/90, HR 95",
        "assessment": "Possible cardiac event",
        "plan": "Admit to hospital"  # Missing ECG!
    }
    result = validator.validate(soap_note)

    # Should warn about missing ECG for chest pain
    assert len(result.warnings) >= 1
    assert any("ecg" in w.message.lower() or "troponin" in w.message.lower() for w in result.warnings)

# Test Layer 2 - PrescriptionValidator
def test_allergy_violation_critical():
    validator = PrescriptionValidator()
    prescription = {
        "medication_name": "amoxicillin",
        "dose": "500mg",
        "repeats": 0,
        "indication": "UTI",
        "patient_allergies": ["Penicillin"]
    }
    result = validator.validate(prescription)

    # Should be CRITICAL error, score = 0, status = "unsafe"
    assert result.score == 0
    assert result.status == "unsafe"
    assert any(e.severity == "critical" for e in result.errors)
    assert any("allergic" in e.message.lower() for e in result.errors)

# Test Layer 3 - Claude AI
@pytest.mark.asyncio
async def test_claude_ai_returns_amc_rubric():
    validator = SOAPNoteAIValidator()
    soap_note = {
        "subjective": "65M with chest pain...",
        "objective": "BP 150/90...",
        "assessment": "Likely ACS...",
        "plan": "ECG, troponin, aspirin..."
    }
    patient = {
        "full_name": "Test Patient",
        "age": 65,
        "presenting_complaint": "Chest pain",
        "clinical_scenario": "65M with cardiac risk factors..."
    }

    feedback = await validator.validate(soap_note, patient)

    # Should return AMC rubric scores
    assert "communication_score" in feedback
    assert "clinical_reasoning_score" in feedback
    assert "total_amc_score" in feedback
    assert 0 <= feedback["total_amc_score"] <= 15
    assert "strengths" in feedback
    assert "improvements" in feedback
```

#### Integration Tests (100% endpoint coverage)
```python
def test_api_validate_soap_note_async(client, auth_headers, test_soap_note):
    """Test POST /validate/soap-note triggers async validation"""
    response = client.post("/api/v1/emr/validate/soap-note", json={
        "soap_note_id": test_soap_note.id,
        "patient_scenario_id": test_soap_note.patient_scenario_id,
        "subjective": test_soap_note.subjective,
        "objective": test_soap_note.objective,
        "assessment": test_soap_note.assessment,
        "plan": test_soap_note.plan
    }, headers=auth_headers)

    assert response.status_code == 202
    data = response.json()
    assert "validation_id" in data
    assert data["status"] in ["queued", "in_progress"]

    # Poll until complete
    validation_id = data["validation_id"]
    for _ in range(10):  # Max 10 seconds
        time.sleep(1)
        poll_response = client.get(f"/api/v1/emr/validation/{validation_id}", headers=auth_headers)
        if poll_response.json()["status"] == "completed":
            break

    # Verify completed
    final_data = poll_response.json()
    assert final_data["status"] == "completed"
    assert "overall_score" in final_data
    assert "amc_rubric_scores" in final_data
```

#### AI Validation Accuracy Test (Manual)
```python
# Create 20 sample SOAP notes (10 good, 10 poor)
# Have human clinical educator score them (gold standard)
# Run through Claude AI validator
# Compare scores: target ≥85% agreement

def test_ai_validation_accuracy_vs_human():
    """
    Manual test: Compare Claude AI scores vs human educator.
    Run this before production deployment.
    """
    test_cases = load_gold_standard_soap_notes()  # 20 pre-scored notes

    validator = SOAPNoteAIValidator()
    agreements = 0

    for case in test_cases:
        ai_feedback = await validator.validate(case["soap_note"], case["patient"])
        human_score = case["human_amc_score"]
        ai_score = ai_feedback["total_amc_score"]

        # Agreement if within ±2 marks (13% tolerance)
        if abs(human_score - ai_score) <= 2:
            agreements += 1

    accuracy = agreements / len(test_cases)
    assert accuracy >= 0.85, f"AI accuracy {accuracy:.2%} below target 85%"
```

---

### Documentation Deliverables

#### 1. Validation Rules Documentation (`docs/EMR_VALIDATION_RULES.md`)
- Layer 2 rule explanations (all checks listed)
- Australian terminology violations (complete list)
- Red flag detection logic (all conditions)
- PBS/MBS compliance rules

#### 2. Claude AI Prompts (`docs/CLAUDE_AI_PROMPTS.md`)
- SOAP note validation prompt (full template)
- AMC rubric explanation
- Example inputs and outputs
- Prompt engineering best practices

#### 3. API Documentation (OpenAPI/Swagger)
- All 4 endpoints with examples
- Request/response schemas
- Error responses
- Rate limiting information

---

### Deployment Checklist

#### Pre-Deployment
- [ ] Claude API key configured in Vault
- [ ] Redis running (for rate limiting + caching)
- [ ] Qdrant connection verified (9,950 chunks)
- [ ] PBS medication database loaded (4,000+ drugs)
- [ ] MBS pathology codes loaded
- [ ] All tests passing (100%)
- [ ] AI validation accuracy ≥85% (tested on 20 samples)

#### Deployment
- [ ] Deploy validation API endpoints
- [ ] Monitor Claude API usage (cost tracking)
- [ ] Monitor rate limiting (20 req/min)
- [ ] Verify RAG retrieval working
- [ ] Run smoke tests in production

#### Post-Deployment
- [ ] Monitor validation latency (<6s)
- [ ] Monitor Claude API errors
- [ ] Monitor validation accuracy (user feedback)
- [ ] Track cost per validation (Claude API tokens)

---

### Success Validation

**This PRD is considered COMPLETE when**:
1. ✅ Layer 2 validators detect 100% of Australian terminology violations
2. ✅ Layer 2 detects 100% of red flags (chest pain, headache, sepsis)
3. ✅ Layer 3 Claude AI returns AMC 15-mark rubric scores
4. ✅ AI validation accuracy ≥85% vs human educator (20 test cases)
5. ✅ All 4 API endpoints working (SOAP, prescription, pathology, get result)
6. ✅ Performance targets met (<1s Layer 2, 3-5s Layer 3)
7. ✅ Rate limiting enforced (20 Claude calls/min)
8. ✅ Tests ≥70% coverage, 100% pass rate
9. ✅ Documentation complete (rules, prompts, API)
10. ✅ Frontend can display validation feedback (integrated with PRD_FRONTEND_004)

**Sign-off Required From**:
- [ ] Backend Engineer (implementation complete)
- [ ] PM Coordinator (requirements met)
- [ ] Security Expert (Claude API key in Vault, prompt injection protected)
- [ ] Clinical Expert (AI accuracy ≥85%, feedback is educational)
- [ ] Testing QA (test coverage + accuracy validated)

---

## 📎 Appendices

### Appendix A: Sample Claude AI Response
```json
{
  "communication_score": 3,
  "clinical_reasoning_score": 3,
  "information_gathering_score": 3,
  "management_score": 2,
  "professionalism_score": 2,
  "total_amc_score": 13,
  "pass_status": true,

  "strengths": [
    "Comprehensive history taking including OPQRST for chest pain",
    "Appropriate risk stratification (T2DM, HTN, ex-smoker, family history)",
    "Australian terminology used consistently (paracetamol, adrenaline, 000)"
  ],

  "improvements": [
    "Plan could include explicit safety netting (return if pain worsens, new symptoms)",
    "Consider mentioning PBS streamlined authority for ticagrelor",
    "Differential diagnoses could include aortic dissection risk factors assessment"
  ],

  "red_flags_identified": [],

  "etg_alignment": true,
  "australian_terminology_correct": true,
  "safety_netting_present": false,

  "overall_feedback": "Strong clinical reasoning and appropriate management of likely ACS. Documentation meets AHPRA standards. To improve to 'excellent' level, explicitly document safety netting and consider all serious differentials."
}
```

### Appendix B: PBS Medication Database Schema
```json
{
  "paracetamol": {
    "pbs_code": "1215K",
    "generic_name": "Paracetamol",
    "brand_names": ["Panadol", "Panamax"],
    "max_dose_adult": "4000mg/day",
    "max_dose_elderly": "3000mg/day",
    "contraindications": ["severe liver disease"],
    "pregnancy_category": "A",
    "streamlined_authority": false
  },
  "ticagrelor": {
    "pbs_code": "10882B",
    "generic_name": "Ticagrelor",
    "brand_names": ["Brilinta"],
    "max_dose_adult": "90mg BD",
    "contraindications": ["active bleeding", "intracranial haemorrhage"],
    "pregnancy_category": "B3",
    "streamlined_authority": true,
    "authority_indication": "Acute Coronary Syndrome"
  }
}
```

### Appendix C: MBS Pathology Codes
```json
{
  "65070": {
    "test_name": "FBC (Full Blood Count)",
    "description": "Haemoglobin, WCC, platelets, differential",
    "typical_indications": ["anaemia", "infection", "baseline"],
    "cost_estimate_aud": 16.50
  },
  "66512": {
    "test_name": "UEC (Urea, Electrolytes, Creatinine)",
    "description": "Sodium, potassium, urea, creatinine, eGFR",
    "typical_indications": ["AKI", "CKD", "electrolyte imbalance"],
    "cost_estimate_aud": 16.50
  },
  "66609": {
    "test_name": "Troponin I",
    "description": "Cardiac troponin I (high sensitivity)",
    "typical_indications": ["chest pain", "ACS", "MI"],
    "cost_estimate_aud": 36.00
  }
}
```

### Appendix D: Red Flag Detection Logic
```python
RED_FLAG_RULES = {
    "chest_pain": {
        "required_plan_keywords": ["ecg", "troponin", "cardiac", "cardiology", "acs"],
        "message": "Chest pain red flag: ECG and troponin not mentioned",
        "severity": "high"
    },
    "severe_headache": {
        "subjective_keywords": ["thunderclap", "worst headache", "sudden headache"],
        "required_plan_keywords": ["ct head", "imaging", "neurology"],
        "message": "Severe headache red flag: CT head not mentioned",
        "severity": "critical"
    },
    "sepsis_criteria": {
        "subjective_keywords": ["fever", "rigors", "hypotension", "confusion", "tachycardia"],
        "min_keywords": 2,
        "required_assessment": ["sepsis"],
        "message": "Possible sepsis not considered in assessment",
        "severity": "critical"
    }
}
```

### Appendix E: Related PRDs
- **Depends On**:
  - PRD_BACKEND_001 (Database - emr_validation_results table)
  - PRD_BACKEND_002 (Session API - triggers validation after submit)
- **Blocks**:
  - PRD_FRONTEND_004 (Validation Display - needs validation API to show feedback)
- **Related**:
  - PRD_TESTING_002 (AI Validation Accuracy Testing)
  - PRD_INTEGRATION_002 (Unified Progress - uses validation scores)

---

**Document Status**: Draft
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Approved By**: Pending
**Version**: 1.0
