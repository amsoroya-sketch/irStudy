# Phase 2: Validation Architecture - Implementation Plan

**Phase**: Phase 2 - Validation Layer Implementation
**Duration**: ~25 hours estimated (6 + 10 + 6 + 2 hours per task)
**Status**: ⏳ Ready for Implementation
**Dependency**: Phase 1 (Frontend & Components) Complete

---

## Overview

Phase 2 implements the complete three-layer validation architecture for the EMR practice system, ensuring robust clinical documentation, Australian compliance, and medical accuracy. The validation system progresses from instant client-side checks through sophisticated rule-based logic to AI-powered clinical reasoning.

**Architecture:**
```
User Input (SOAP Note, Prescription, Pathology)
    ↓
Layer 1: Client-Side (Zod) - <50ms
    ↓ (if pass)
Layer 2: Rule-Based (Python) - <1 second
    ↓ (if no critical errors)
Layer 3: AI (Claude 3.5 Sonnet) - 3-5 seconds
    ↓
Unified API Response
    ↓
Frontend Validation UI
```

---

## Task Breakdown

### TASK 2.1: Client-Side Validation - Zod Schemas (Layer 1)
**Duration**: 6 hours
**Status**: ⏳ Not Started
**File**: `TASK_2.1_Zod_Schemas.md`

**Deliverables:**
- 5 schema files (SOAP, prescription, pathology, laboratory, composite)
- 3 utility files (validators, formatting, types)
- 1 configuration file
- 500+ lines of tests (100+ test cases)

**Key Requirements:**
- <50ms validation response time
- Australian terminology enforcement (paracetamol not acetaminophen)
- PBS code format validation (\d{4}[A-Z])
- MBS item number validation (5 digits exactly)
- 95%+ code coverage

**Agent Delegation**: `frontend-typescript-expert`

**Acceptance Criteria**:
- ✅ All schemas compile without TypeScript errors
- ✅ 100+ test cases passing
- ✅ Coverage ≥95%
- ✅ All validations <50ms
- ✅ Ready for Layer 2 consumption

---

### TASK 2.2: Rule-Based Validation - PBS/MBS Validators (Layer 2)
**Duration**: 10 hours
**Status**: ⏳ Not Started (depends on TASK 2.1)
**File**: `TASK_2.2_PBS_MBS_Validators.md`

**Deliverables:**
- 5 validator modules (PBS, MBS, clinical safety, prescription, pathology)
- 3 mock database files (medications, tests, interactions)
- 2 utility files (results, initialization)
- 500+ lines of tests (≥150 test cases)

**Key Requirements:**
- <1 second validation response time
- Drug interaction matrix (≥15 critical interactions)
- Clinical red flags (≥10 patterns: ACS, stroke, sepsis, anaphylaxis, suicide)
- ≥70% test coverage
- Australian medication standards (TGA, PBS)

**Agent Delegation**: `python-clinical-expert`

**Acceptance Criteria**:
- ✅ All validators functional
- ✅ 15+ drug interactions implemented
- ✅ 10+ red flags detected
- ✅ ≥150 test cases passing
- ✅ Coverage ≥70%
- ✅ All validations <1 second
- ✅ Ready for Layer 3 consumption

---

### TASK 2.3: AI-Powered Clinical Validation (Layer 3)
**Duration**: 6 hours
**Status**: ⏳ Not Started (depends on TASK 2.2)
**File**: `TASK_2.3_AI_Validation.md`

**Deliverables:**
- Core validator module with 6+ methods
- System prompts for SOAP/prescription/pathology validation
- RAG integration module
- Error handling with retry logic
- Response type dataclasses
- Configuration file
- 400+ lines of tests (100+ test cases)

**Key Requirements:**
- 3-5 second response time (with timeout handling)
- Claude 3.5 Sonnet integration
- RAG context from irStudy knowledge base
- Structured JSON output with validation
- Personalized educational feedback for students
- Graceful degradation on API failures

**Agent Delegation**: `ai-clinical-expert` + `python-llm-integration-expert`

**Acceptance Criteria**:
- ✅ ClaudeValidator implemented with all methods
- ✅ SOAP/prescription/pathology validation working
- ✅ Educational feedback personalized
- ✅ RAG integration functional
- ✅ 100+ test cases passing
- ✅ Coverage ≥70%
- ✅ P95 response time <5 seconds
- ✅ Graceful error handling

---

### TASK 2.4: Unified Validation API (Orchestration)
**Duration**: 2 hours
**Status**: ⏳ Not Started (depends on TASK 2.3)
**File**: `TASK_2.4_Unified_Validation_API.md`

**Deliverables:**
- 4 API endpoints (SOAP, prescription, pathology, session)
- Orchestration service
- Request/response type definitions
- Error handling and exceptions
- 400+ lines of tests (100+ test cases)

**Key Requirements:**
- Proper layer sequencing (1 → 2 → 3)
- Skip Layer 3 on critical errors
- Cross-component compatibility checking
- Timing metrics for each layer
- Graceful degradation on failures
- ≥70% test coverage

**Agent Delegation**: `backend-api-expert`

**Acceptance Criteria**:
- ✅ All 4 endpoints implemented
- ✅ Layer sequencing correct
- ✅ Combined error aggregation
- ✅ Cross-component checks working
- ✅ 100+ test cases passing
- ✅ Coverage ≥70%
- ✅ P95 response time <5 seconds

---

## Architecture Overview

### Layer 1: Client-Side Validation (Zod)
**Location**: `/emr-frontend/src/schemas/`
**Technology**: TypeScript + Zod
**Response Time**: <50ms
**Scope**: Format, required fields, data types

**Validates:**
- SOAP note structure and section lengths
- Prescription format and limits
- Pathology order format and codes
- Australian terminology

### Layer 2: Rule-Based Validation (Python)
**Location**: `/backend/src/validators/`
**Technology**: Python + FastAPI
**Response Time**: <1 second
**Scope**: Business logic, Australian compliance, clinical safety

**Validates:**
- PBS/MBS compliance and codes
- Drug interactions (≥15 critical)
- Clinical red flags (≥10 patterns)
- Allergy conflicts and contraindications

### Layer 3: AI-Powered Validation (Claude)
**Location**: `/backend/src/validators/ai_validator_claude.py`
**Technology**: Claude 3.5 Sonnet + RAG
**Response Time**: 3-5 seconds
**Scope**: Clinical reasoning, educational feedback, completeness assessment

**Validates:**
- SOAP note quality and completeness
- Prescription appropriateness and dosing
- Pathology order clinical alignment
- Documentation quality and compliance
- Generates personalized student feedback

### Unified API
**Location**: `/backend/src/api/v1/validation.py`
**Technology**: FastAPI
**Endpoints**:
- `POST /api/v1/validation/soap-note`
- `POST /api/v1/validation/prescription`
- `POST /api/v1/validation/pathology-order`
- `POST /api/v1/validation/session` (batch)

---

## Implementation Timeline

### Week 1
- **Days 1-2**: TASK 2.1 (Zod Schemas) - 6 hours
- **Days 3-5**: TASK 2.2 (PBS/MBS Validators) - 10 hours

### Week 2
- **Days 1-2**: TASK 2.3 (Claude AI Validator) - 6 hours
- **Day 3**: TASK 2.4 (Unified API) - 2 hours
- **Days 3-5**: Integration & QA testing - remaining time

### Total: ~25 hours of implementation + integration/QA

---

## Key Files & Directory Structure

### Frontend Schemas
```
emr-frontend/src/
├── schemas/
│   ├── soap-note.schema.ts (180+ lines)
│   ├── prescription.schema.ts (160+ lines)
│   ├── pathology-order.schema.ts (140+ lines)
│   ├── laboratory-tests.schema.ts (120+ lines)
│   └── composite.schema.ts (80+ lines)
├── utils/
│   ├── schema-validators.ts (100+ lines)
│   ├── validation-formatting.ts (60+ lines)
│   └── validation.types.ts (80+ lines) [or in types/]
├── types/
│   └── validation.types.ts (80+ lines)
├── config/
│   └── validation.config.ts (50+ lines)
└── __tests__/schemas/
    ├── soap-note.schema.test.ts (80 tests)
    ├── prescription.schema.test.ts (100 tests)
    ├── pathology-order.schema.test.ts (60 tests)
    ├── laboratory-tests.schema.test.ts (40 tests)
    └── composite.schema.test.ts (30 tests)
```

### Backend Validators
```
backend/src/validators/
├── __init__.py (30+ lines)
├── validation_result.py (60+ lines)
├── pbs_validator.py (220+ lines)
├── mbs_validator.py (200+ lines)
├── clinical_safety_validator.py (180+ lines)
├── prescription_validator.py (100+ lines)
├── pathology_validator.py (80+ lines)
├── ai_validator_claude.py (280+ lines)
├── ai_prompts.py (150+ lines)
├── rag_integration.py (100+ lines)
├── ai_error_handler.py (80+ lines)
├── ai_response_types.py (100+ lines)
├── ai_config.py (60+ lines)
├── validation_exceptions.py (40+ lines)
└── mock_databases/
    ├── pbs_medications.json (400+ lines, 20+ meds)
    ├── mbs_tests.json (300+ lines, 15+ tests)
    └── drug_interactions.json (150+ lines, 15+ interactions)

backend/src/api/v1/
├── validation.py (250+ lines, 4 endpoints)

backend/src/schemas/
├── validation_schemas.py (120+ lines)

backend/src/services/
├── validation_orchestrator.py (200+ lines)

backend/tests/validators/
├── test_pbs_validator.py (200+ lines)
├── test_mbs_validator.py (150+ lines)
├── test_clinical_safety_validator.py (180+ lines)
├── test_ai_validator_claude.py (200+ lines)
├── test_ai_prompts.py (80+ lines)
├── test_rag_integration.py (60+ lines)
└── conftest.py (enhancements)

backend/tests/api/
├── test_validation_endpoints.py (250+ lines)

backend/tests/services/
├── test_validation_orchestrator.py (150+ lines)
```

---

## Validation Metrics

### Coverage Targets
- **Frontend (Zod)**: ≥95% coverage
- **Backend (Rules)**: ≥70% coverage
- **Backend (AI)**: ≥70% coverage
- **API**: ≥70% coverage

### Performance Targets
| Layer | Target | Measurement |
|-------|--------|-------------|
| Layer 1 (Zod) | <50ms | Per validation |
| Layer 2 (Rules) | <1 sec | Per validation |
| Layer 3 (AI) | 3-5 sec | Per validation (with timeout) |
| Combined | <6 sec | Total (P95) |

### Test Coverage
- **Layer 1**: 310+ test cases (100+ unique)
- **Layer 2**: 150+ test cases (including drug interactions & red flags)
- **Layer 3**: 100+ test cases (including RAG and error scenarios)
- **API**: 100+ test cases (layer sequencing, cross-component)
- **Total**: 660+ test cases

---

## Success Criteria for Phase 2 Completion

### Functionality
- ✅ All 4 task files completed with detailed specs
- ✅ All code modules implemented and functional
- ✅ All tests passing (660+ tests)
- ✅ Code coverage ≥70% across backend, ≥95% frontend
- ✅ No TypeScript errors in frontend
- ✅ No unhandled exceptions in backend

### Performance
- ✅ Layer 1: All validations <50ms
- ✅ Layer 2: All validations <1 second
- ✅ Layer 3: P95 <5 seconds, P99 <10 seconds
- ✅ Combined: P95 <6 seconds total

### Quality
- ✅ 15+ drug interactions implemented and tested
- ✅ 10+ clinical red flags implemented and tested
- ✅ Australian terminology enforcement (100+ drugs)
- ✅ PBS code format validation working
- ✅ MBS item number validation working
- ✅ Educational feedback personalized for students

### Integration
- ✅ All layers properly sequenced
- ✅ Layer 1 failure skips layers 2+3
- ✅ Layer 2 critical errors skip layer 3
- ✅ Layer 3 timeout doesn't block result
- ✅ Cross-component compatibility checking working
- ✅ API endpoints returning proper ValidationResponse

### Documentation
- ✅ All 4 task files completed with agent delegation prompts
- ✅ README with architecture overview
- ✅ All code well-commented with docstrings
- ✅ Validation rules documented
- ✅ Test cases well-organized and descriptive

---

## Dependencies & Prerequisites

### External Services
- **Anthropic API**: Claude 3.5 Sonnet access (for Layer 3)
- **irStudy RAG System**: Knowledge base queries (for Layer 3 context)

### Libraries
- **Frontend**: Zod ^3.22.4, TypeScript 5.3+
- **Backend**: FastAPI 0.109.0, Anthropic SDK ^0.18.1, pytest ^7.4, pytest-cov ^4.1
- **Data**: JSON mock databases (included in project)

### Previous Phases
- **Phase 1**: Frontend components complete
- **Phase 0**: Backend infrastructure (FastAPI, auth) working

---

## Execution Workflow

### Agent Delegation Order
1. **TASK 2.1**: Assign to `frontend-typescript-expert`
   - Deliver Zod schemas with 95%+ coverage
   - Validate all tests passing before moving on

2. **TASK 2.2**: Assign to `python-clinical-expert` (after 2.1 complete)
   - Deliver rule validators with ≥70% coverage
   - Ensure <1 second performance
   - Validate drug interaction matrix complete

3. **TASK 2.3**: Assign to `ai-clinical-expert` + `python-llm-integration-expert` (after 2.2 complete)
   - Deliver Claude integration with proper error handling
   - Ensure 3-5 second response time
   - Validate educational feedback quality

4. **TASK 2.4**: Assign to `backend-api-expert` (after 2.3 complete)
   - Deliver unified API orchestrating all layers
   - Ensure proper sequencing and branching
   - Validate cross-component checking

### PM Validation Points
- After each task: Verify coverage and performance targets met
- After 2.4: Run full integration test to confirm all layers work together
- Before Phase 3: Confirm API ready for frontend integration

---

## Common Pitfalls to Avoid

1. **Don't skip Layer 1 validation**
   - Frontend validation is critical for UX
   - Reduces backend load

2. **Don't hardcode medication/test data**
   - Use mock databases for easy updates
   - Plan for future database integration

3. **Don't ignore Australian context**
   - Project explicitly requires AMC standards (not ICRP)
   - PBS/MBS formats are Australia-specific

4. **Don't skip error handling**
   - Layer 3 (AI) can fail - have fallback to Layer 1+2
   - User should never see broken error page

5. **Don't ignore ICRP student focus**
   - Educational feedback is key differentiator
   - Tailor feedback to training level and learning goals

---

## References & Documentation

### Related Documents
- **PRD**: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md`
- **Validation Rules**: `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md`
- **Phase 1**: `/home/dev/Development/irStudy/emr-practice-system/implementation-plan/phase1-frontend/`

### Clinical References
- **Australian Standards**: AMC Clinical Examination, TGA, PBS, NHMRC
- **Drug Interactions**: TGA contraindication database
- **Clinical Red Flags**: Emergency medicine and acute care protocols

### Technology Documentation
- **Zod**: https://zod.dev/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Claude API**: https://docs.anthropic.com/
- **Pydantic**: https://docs.pydantic.dev/

---

## Contact & Support

### For Task Questions
- Review the individual task file (TASK_X.Y_*.md)
- Check the agent delegation prompt within the file
- Contact PM with specific clarifications

### For Clinical Questions
- Reference Australian medical standards (AMC, TGA, PBS)
- Consult irStudy knowledge base (RAG system)
- Contact medical advisor for complex cases

### For Technical Questions
- Refer to tool documentation links above
- Check project constraints in PROJECT_CONSTRAINTS.md
- Contact technical lead for architecture decisions

---

**Phase 2 Status**: ⏳ Ready for Implementation
**Next Phase**: Phase 3 (UI/Integration & QA Testing)
**Est. Completion**: 2-3 weeks with parallel task execution

---

*Last Updated: 2026-02-05*
*Version: 1.0*
*Author: PM (Claude Code)*
