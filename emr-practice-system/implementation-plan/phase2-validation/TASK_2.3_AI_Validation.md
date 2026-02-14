# TASK 2.3: AI-Powered Clinical Validation - Claude Integration (Layer 3)

**Phase**: Phase 2 - Validation Architecture
**Estimated Hours**: 6 hours
**Dependencies**: TASK_2.2 Complete (Rule validators), Anthropic SDK ^0.18.1, Claude 3.5 Sonnet access, RAG system setup
**Agent Type**: `ai-clinical-expert` + `python-llm-integration-expert`
**Status**: ⏳ Not Started

---

## Overview

Implement the third and deepest validation layer using Claude 3.5 Sonnet for comprehensive clinical reasoning assessment. This layer provides sophisticated evaluation of SOAP note quality, clinical appropriateness of prescriptions, educational feedback for ICRP students, and Australian medical compliance checking. Combines RAG (Retrieval-Augmented Generation) with the irStudy medical knowledge base for context-aware validation with 3-5 second response times and structured JSON output.

---

## Deliverables

### Core AI Validation Module

#### 1. `/backend/src/validators/ai_validator_claude.py` (280+ lines)

**Class: ClaudeValidator**

- **`__init__(api_key: str, rag_client: RAGClient, model: str = "claude-3-5-sonnet-20241022")`**
  - Initialize Anthropic client
  - Connect to RAG system
  - Load system prompts from config
  - Set model parameters (temperature=0.3 for consistency)

- **`validate_soap_note(soap_note: SOAPNote, patient: Patient, context: Dict[str, Any] = None) -> AIValidationResult`**
  - Input: Complete SOAP note, patient demographics, optional previous notes
  - RAG Query: "SOAP note documentation standards for [chief_complaint]"
  - System Prompt: SOAP validation prompt (see below)
  - Claude Analysis:
    - Content completeness (all 4 sections present)
    - Section quality (depth, clarity, clinical reasoning)
    - Differential diagnosis appropriateness
    - Investigation plan alignment with assessment
    - Australian clinical standards compliance
    - Potential gaps or missed diagnoses
    - Patient safety considerations
  - Output: JSON structured response with:
    - overall_score (0-100)
    - section_scores: {subjective: 0-100, objective: 0-100, assessment: 0-100, plan: 0-100}
    - strengths: List[str] (3-5 items)
    - areas_for_improvement: List[str] (3-5 items)
    - missing_elements: List[str] (if any)
    - australian_compliance: {compliant: bool, issues: List[str]}
    - educational_feedback: str (for student learning)
    - red_flags_identified: List[str] (clinical concerns)
    - confidence_score: float (0.0-1.0)
    - validation_time_ms: float

- **`validate_prescription_appropriateness(prescription: Prescription, soap_note: SOAPNote, patient: Patient) -> AIValidationResult`**
  - Input: Prescription, supporting SOAP note, patient data
  - RAG Query: "Appropriate medication management for [diagnosis]"
  - Claude Analysis:
    - Alignment with documented diagnosis
    - Dose appropriateness for patient age/weight/renal function
    - Indication clarity and completeness
    - Duration of therapy appropriate
    - Safety monitoring requirements
    - Interaction check (though Layer 2 checked this)
    - Alternative medications if more appropriate
    - Patient counseling needs
  - Output: JSON with:
    - appropriate (bool)
    - score (0-100)
    - rationale: str
    - dosing_notes: str
    - monitoring_requirements: List[str]
    - patient_education: List[str]
    - alternatives_considered: List[str]
    - red_flags: List[str]
    - educational_feedback: str

- **`validate_pathology_order(order: PathologyOrder, soap_note: SOAPNote, patient: Patient) -> AIValidationResult`**
  - Input: Pathology order, SOAP note context, patient data
  - RAG Query: "Diagnostic workup for [chief_complaint]"
  - Claude Analysis:
    - Relevance to stated diagnosis
    - Completeness of diagnostic approach
    - Redundancy (ordering duplicate tests)
    - Appropriateness for patient age/comorbidities
    - Timing and urgency assessment
    - Expected yield of each test
    - Any missing tests that would be helpful
  - Output: JSON with:
    - appropriate (bool)
    - score (0-100)
    - clinical_reasoning: str
    - test_appropriateness: Dict[str, str]
    - missing_tests: List[str]
    - redundant_tests: List[str]
    - specimen_collection_advice: str
    - interpretation_guidance: str
    - educational_feedback: str

- **`validate_clinical_documentation_quality(session_data: SessionData) -> DocumentationQualityResult`**
  - Input: Complete session (SOAP + prescriptions + pathology + labs)
  - Checks:
    - SOAP note completeness (uses validateSOAPNote)
    - Prescription documentation (indication clarity)
    - Diagnostic plan coherence
    - Assessment-plan alignment
    - Safety considerations documented
    - Patient education points clear
    - Follow-up plan complete
    - Legal/medico-legal compliance
  - Output: JSON with:
    - overall_quality_score (0-100)
    - component_scores: Dict[str, int]
    - documentation_strengths: List[str]
    - documentation_gaps: List[str]
    - compliance_issues: List[str]
    - risk_factors: List[str]
    - recommendations: List[str]

- **`generate_educational_feedback(session_data: SessionData, student_profile: Dict[str, Any]) -> EducationalFeedback`**
  - Input: Complete session, student's learning profile (weak areas, stage of training)
  - RAG Query: "ICRP training objectives and competency standards"
  - Claude Analysis:
    - Aligned with student's current level (junior/senior trainee)
    - Specific learning points from this case
    - Common mistakes avoided in this session
    - Suggestions for improvement
    - Recommended practice areas
    - Resources/references for learning
  - Output: JSON with:
    - key_learning_points: List[str]
    - mastered_skills: List[str]
    - areas_for_development: List[str]
    - mistakes_avoided: List[str]
    - next_practice_focus: str
    - recommended_resources: List[Dict[str, str]]  # {title, reference, why}
    - coaching_tips: List[str]

- **`batch_validate_sessions(sessions: List[SessionData], concurrent: bool = False) -> List[AIValidationResult]`**
  - Validate multiple sessions
  - Optional concurrent processing (with rate limiting)
  - Progress callback for long operations
  - Error handling and recovery

### System Prompts Configuration

#### 2. `/backend/src/validators/ai_prompts.py` (150+ lines)

```python
SOAP_VALIDATION_PROMPT = """
You are an expert clinical educator assessing medical student documentation for the ICRP (Australian medical qualification).

Evaluate the provided SOAP note based on these criteria:

## Subjective Section (target score: 0-25 points)
- Chief complaint: Clear, concise, <10 words
- HPI: Detailed narrative covering onset, progression, severity, associated symptoms (min 50 chars)
- Timeline: Clear chronological presentation
- Relevant positives and negatives: Thoroughness of questioning
- Past medical history: Relevant items documented
- Medications: Current medications with doses and frequencies
- Allergies: All allergies documented with reaction severity
- Social history: Occupation, smoking, alcohol, drug use as relevant

## Objective Section (target score: 0-25 points)
- Vital signs: All 6 vitals present (BP, HR, RR, Temp, O2Sat, Weight)
- Physical examination: Systematic approach to all relevant systems
- Abnormalities documented: Specific findings, not generic descriptors
- Investigations: Lab/imaging results if available, properly interpreted
- Assessment of severity: Based on vital signs and examination findings

## Assessment Section (target score: 0-25 points)
- Primary diagnosis: ICD-10 code provided, clinically appropriate
- Differential diagnosis: 2-5 alternatives, properly ranked by likelihood
- Clinical reasoning: Justification for diagnosis based on findings
- Risk stratification: Explicit assessment of severity/urgency
- Safety considerations: Identified risks or special precautions

## Plan Section (target score: 0-25 points)
- Investigations: Aligned with assessment, appropriate urgency/frequency
- Prescriptions: Dosing appropriate for age/weight/renal function
- Referrals: Appropriate specialty, timeframe specified
- Follow-up: Return visit timeframe clear, contingency plans noted
- Patient education: Safety-net advice, red flag symptoms, medication counseling
- Monitoring: What needs to be monitored and how often

## Australian Compliance Checklist
- Uses AMC Clinical Examination standards (not ICRP terminology)
- Terminology is Australian (paracetamol not acetaminophen)
- References Australian guidelines if applicable
- Considers Australian prevalence of conditions
- Appropriate for Australian healthcare context

## Output Format
Return ONLY valid JSON (no markdown, no explanation) with this structure:
{
  "overall_score": <0-100>,
  "section_scores": {
    "subjective": <0-25>,
    "objective": <0-25>,
    "assessment": <0-25>,
    "plan": <0-25>
  },
  "strengths": [<3-5 specific positives>],
  "areas_for_improvement": [<3-5 specific areas to improve>],
  "missing_elements": [<list of gaps if any>],
  "australian_compliance": {
    "compliant": <bool>,
    "issues": [<list of compliance issues if any>]
  },
  "educational_feedback": "<personalized feedback for student learning>",
  "red_flags_identified": [<any clinical safety concerns>],
  "confidence_score": <0.0-1.0>,
  "validation_time_ms": <actual validation duration>
}

Now evaluate this SOAP note:
[SOAP_NOTE_HERE]
"""

PRESCRIPTION_VALIDATION_PROMPT = """
You are an experienced pharmacist reviewing medication prescriptions for appropriateness.

Evaluate the prescription in the context of the patient's diagnosis and clinical situation.

## Evaluation Criteria
1. **Indication Alignment**: Does the medication match the stated diagnosis?
2. **Dose Appropriateness**: Is the dose correct for patient age/weight/renal function?
3. **Frequency**: Is the frequency appropriate for the medication and condition?
4. **Duration**: Is the treatment duration appropriate?
5. **Route**: Is the route of administration appropriate?
6. **Monitoring**: What monitoring is required?
7. **Patient Safety**: Are there contraindications or special precautions?
8. **Alternatives**: Are there better alternatives?

## Australian Compliance
- Is medication on PBS?
- Does it have any authority restrictions?
- Is the dose within PBS limits?
- Are there Australian-specific guidelines?

## Output Format
Return ONLY valid JSON with this structure:
{
  "appropriate": <bool>,
  "score": <0-100>,
  "rationale": "<explanation of assessment>",
  "dosing_notes": "<whether dose is appropriate>",
  "monitoring_requirements": [<required monitoring>],
  "patient_education": [<what patient should know>],
  "alternatives_considered": [<other medications that could work>],
  "red_flags": [<any safety concerns>],
  "educational_feedback": "<feedback for prescriber>"
}

Prescription to evaluate:
[PRESCRIPTION_HERE]

Clinical context:
[SOAP_NOTE_HERE]

Patient data:
[PATIENT_DATA_HERE]
"""

PATHOLOGY_VALIDATION_PROMPT = """
You are an expert pathologist/diagnostician reviewing orders for diagnostic investigations.

Evaluate the appropriateness and completeness of the pathology order.

## Evaluation Criteria
1. **Relevance**: Does the test help clarify the diagnosis?
2. **Completeness**: Are all necessary tests ordered?
3. **Redundancy**: Are any tests duplicated or unnecessary?
4. **Appropriateness**: Is the test appropriate for patient age/comorbidities?
5. **Urgency**: Is the urgency level appropriate?
6. **Specimen Type**: Is the correct specimen being collected?
7. **Special Handling**: Are special handling requirements documented?

## Test-Specific Considerations
- Lipid panel: Requires fasting, once per 12 months for routine screening
- Hemoglobin A1C: No fasting required, good for diabetes monitoring
- Troponin: Time-sensitive for cardiac assessment
- Blood culture: Requires proper sterile technique
- UEC: Check for renal function, electrolyte abnormalities

## Output Format
Return ONLY valid JSON with this structure:
{
  "appropriate": <bool>,
  "score": <0-100>,
  "clinical_reasoning": "<why these tests are appropriate>",
  "test_appropriateness": {
    "<test_name>": "<assessment of this test>"
  },
  "missing_tests": [<tests that should be considered>],
  "redundant_tests": [<tests that are unnecessary>],
  "specimen_collection_advice": "<guidance for phlebotomist>",
  "interpretation_guidance": "<what findings might mean>",
  "educational_feedback": "<feedback for clinician>"
}

Order to evaluate:
[PATHOLOGY_ORDER_HERE]

Clinical context:
[SOAP_NOTE_HERE]

Patient data:
[PATIENT_DATA_HERE]
"""
```

### RAG Integration Module

#### 3. `/backend/src/validators/rag_integration.py` (100+ lines)

**Class: RAGContextRetriever**

```python
class RAGContextRetriever:
    """Retrieves relevant medical knowledge from irStudy RAG system."""

    def __init__(self, rag_client: RAGClient):
        self.rag = rag_client

    def get_condition_context(self, chief_complaint: str, diagnosis: str) -> str:
        """Retrieve diagnostic and management info for condition."""
        # Query: "Diagnosis and management of [diagnosis]"
        # Return: Relevant clinical guidelines, pathophysiology, investigations

    def get_medication_context(self, medication_name: str) -> str:
        """Retrieve medication information from knowledge base."""
        # Query: "Medication review [medication_name]"
        # Return: Indications, contraindications, dosing, interactions

    def get_pathology_context(self, test_name: str, patient_age: int) -> str:
        """Retrieve pathology test information."""
        # Query: "Pathology test [test_name]"
        # Return: Indications, interpretation, normal values, special handling

    def get_differential_context(self, chief_complaint: str) -> str:
        """Retrieve differential diagnosis guidance."""
        # Query: "Differential diagnosis of [chief_complaint]"
        # Return: Common and serious diagnoses, key discriminating features

    def get_guidelines_context(self, topic: str) -> str:
        """Retrieve Australian clinical guidelines."""
        # Query: "Australian clinical guidelines [topic]"
        # Return: TGA, AMC, NHMRC recommendations
```

### Error Handling & Rate Limiting

#### 4. `/backend/src/validators/ai_error_handler.py` (80+ lines)

```python
class AIValidationError(Exception):
    """Base exception for AI validation errors."""
    pass

class APITimeoutError(AIValidationError):
    """Claude API request timed out."""
    pass

class APIRateLimitError(AIValidationError):
    """Hit API rate limit."""
    pass

class MalformedResponseError(AIValidationError):
    """Claude returned invalid JSON."""
    pass

def handle_api_error(error: Exception, retry_count: int = 0, max_retries: int = 3) -> bool:
    """Handle API errors with exponential backoff."""
    if isinstance(error, APIRateLimitError) and retry_count < max_retries:
        wait_time = 2 ** retry_count  # 1, 2, 4 seconds
        sleep(wait_time)
        return True  # Signal to retry
    elif isinstance(error, APITimeoutError):
        # Return partial result without AI validation
        return False  # Signal to skip AI validation, return Layer 2 result only
    elif isinstance(error, MalformedResponseError):
        # Log and return generic response
        return False

def validate_json_response(response: str) -> Dict[str, Any]:
    """Parse and validate Claude's JSON response."""
    try:
        data = json.loads(response)
        # Validate required fields
        required = ["overall_score", "strengths", "areas_for_improvement"]
        for field in required:
            if field not in data:
                raise MalformedResponseError(f"Missing required field: {field}")
        return data
    except json.JSONDecodeError as e:
        raise MalformedResponseError(f"Invalid JSON: {e}")
```

### Response Types

#### 5. `/backend/src/validators/ai_response_types.py` (100+ lines)

```python
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AIValidationResult:
    """Result from Claude validation."""
    success: bool
    overall_score: Optional[int]  # 0-100
    section_scores: Optional[Dict[str, int]]  # For SOAP validation
    strengths: List[str]
    areas_for_improvement: List[str]
    missing_elements: List[str]
    australian_compliance: Dict[str, any]
    educational_feedback: str
    red_flags: List[str]
    confidence_score: Optional[float]  # 0.0-1.0
    validation_time_ms: float
    error: Optional[str] = None  # If validation failed

@dataclass
class EducationalFeedback:
    """Educational feedback for student."""
    key_learning_points: List[str]
    mastered_skills: List[str]
    areas_for_development: List[str]
    mistakes_avoided: List[str]
    next_practice_focus: str
    recommended_resources: List[Dict[str, str]]
    coaching_tips: List[str]

@dataclass
class DocumentationQualityResult:
    """Overall documentation quality assessment."""
    overall_quality_score: int  # 0-100
    component_scores: Dict[str, int]
    strengths: List[str]
    gaps: List[str]
    compliance_issues: List[str]
    risk_factors: List[str]
    recommendations: List[str]
```

### Configuration & Constants

#### 6. `/backend/src/validators/ai_config.py` (60+ lines)

```python
# Model Configuration
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
TEMPERATURE = 0.3  # Lower = more consistent
MAX_TOKENS = 2000

# Timeout Configuration
API_TIMEOUT_SECONDS = 30  # 30 second timeout for API calls
VALIDATION_TIMEOUT_SECONDS = 45  # 45 second total timeout (includes retries)
RATE_LIMIT_RETRY_ATTEMPTS = 3
RATE_LIMIT_RETRY_BACKOFF_SECONDS = [1, 2, 4]  # Exponential backoff

# RAG Configuration
RAG_QUERY_TOP_K = 5
RAG_MAX_CONTEXT_TOKENS = 1000

# Scoring Thresholds
SCORE_EXCELLENT = 90
SCORE_GOOD = 75
SCORE_ADEQUATE = 60
SCORE_NEEDS_IMPROVEMENT = 40

# System Prompts
SOAP_SYSTEM_PROMPT = """..."""  # Defined in ai_prompts.py
PRESCRIPTION_SYSTEM_PROMPT = """..."""
PATHOLOGY_SYSTEM_PROMPT = """..."""
```

### Testing Files

#### 7. `/backend/tests/validators/test_ai_validator_claude.py` (200+ lines)

```python
import pytest
from unittest.mock import Mock, patch
from validators.ai_validator_claude import ClaudeValidator

class TestClaudeValidator:
    """Test Claude-based validation."""

    @pytest.fixture
    def validator(self):
        """Create validator with mocked API."""
        with patch('validators.ai_validator_claude.Anthropic'):
            return ClaudeValidator(api_key='test-key')

    @pytest.fixture
    def sample_soap_note(self):
        """Sample valid SOAP note."""
        return {
            "subjective": {
                "chief_complaint": "Chest pain",
                "hpi": "Patient presents with acute onset chest pain for 2 hours...",
                "pmh": ["Hypertension", "Diabetes"],
                "medications": [...],
                "allergies": [...]
            },
            "objective": {...},
            "assessment": {...},
            "plan": {...}
        }

    def test_validate_soap_note_success(self, validator, sample_soap_note):
        """Test successful SOAP validation."""
        # Mock Claude response
        with patch.object(validator, '_call_claude_api') as mock_api:
            mock_api.return_value = {
                "overall_score": 85,
                "section_scores": {...},
                "strengths": [...],
                "areas_for_improvement": [...],
                "australian_compliance": {...}
            }

            result = validator.validate_soap_note(sample_soap_note, {})
            assert result.success
            assert result.overall_score == 85

    def test_api_timeout_handling(self, validator):
        """Test timeout error handling."""
        with patch.object(validator, '_call_claude_api') as mock_api:
            mock_api.side_effect = Timeout()
            result = validator.validate_soap_note({}, {})
            assert not result.success
            assert "timeout" in result.error.lower()

    def test_rate_limit_retry(self, validator):
        """Test rate limit retry with backoff."""
        with patch.object(validator, '_call_claude_api') as mock_api:
            mock_api.side_effect = [
                RateLimitError(),
                {"overall_score": 75, ...}
            ]
            result = validator.validate_soap_note({}, {})
            assert result.success  # Should succeed after retry

    def test_malformed_json_response(self, validator):
        """Test handling of invalid JSON from Claude."""
        with patch.object(validator, '_call_claude_api') as mock_api:
            mock_api.return_value = "This is not JSON"
            result = validator.validate_soap_note({}, {})
            assert not result.success

    def test_educational_feedback_generation(self, validator, sample_soap_note):
        """Test educational feedback for student."""
        with patch.object(validator, '_call_claude_api'):
            feedback = validator.generate_educational_feedback(
                {...},
                student_profile={"level": "junior_trainee", "weak_areas": ["Differential diagnosis"]}
            )
            assert "key_learning_points" in feedback
            assert "areas_for_development" in feedback
```

#### 8. `/backend/tests/validators/test_ai_prompts.py` (80+ lines)
- Test system prompts are valid
- Test prompt injection prevention
- Test RAG context insertion

#### 9. `/backend/tests/validators/test_rag_integration.py` (60+ lines)
- Test RAG queries work
- Test context retrieval
- Test handling of missing context

#### 10. `/backend/tests/validators/conftest.py` - Enhanced (50 lines)
- Mock Anthropic client
- Mock RAG client
- Sample responses from Claude

---

## Detailed Requirements

### Requirement 1: 3-5 Second Response Time

**Specification:**
Complete AI validation within 3-5 seconds, including API call and response parsing.

**Response Time Budget:**
- RAG query: 500-800ms
- Claude API call: 1500-2500ms
- Response parsing/validation: 200-400ms
- Network overhead: 200-300ms
- **Total: 3000-5000ms**

**Optimization Strategies:**
- Parallel RAG queries (if independent)
- Streaming API responses (process as they arrive)
- Cache frequent queries (e.g., same diagnosis)
- Timeout with graceful degradation (return Layer 2 only)

**Acceptance Criteria:**
- [ ] P95 response time <5 seconds
- [ ] P99 response time <10 seconds
- [ ] Timeout handling doesn't block user
- [ ] Graceful fallback to Layer 2 if timeout

### Requirement 2: Structured JSON Output

**Specification:**
Claude must return strictly formatted JSON that can be parsed and consumed by frontend.

**Schema Validation:**
```python
# All responses must match these structures exactly
SOAP_RESPONSE_SCHEMA = {
    "overall_score": int (0-100),
    "section_scores": {
        "subjective": int,
        "objective": int,
        "assessment": int,
        "plan": int
    },
    "strengths": List[str],
    "areas_for_improvement": List[str],
    "missing_elements": List[str],
    "australian_compliance": {
        "compliant": bool,
        "issues": List[str]
    },
    "educational_feedback": str,
    "red_flags_identified": List[str],
    "confidence_score": float (0.0-1.0)
}
```

**Acceptance Criteria:**
- [ ] All responses validate against schema
- [ ] No malformed JSON responses
- [ ] All required fields present
- [ ] Type validation on all fields

### Requirement 3: RAG Context Integration

**Specification:**
Integrate with irStudy RAG system to provide knowledge base context for Claude.

**RAG Queries to Support:**
- "SOAP note standards for [diagnosis]"
- "Differential diagnosis of [chief_complaint]"
- "Management guidelines for [diagnosis]"
- "Medication review for [drug_name]"
- "Pathology testing for [symptom]"
- "Australian clinical guidelines on [topic]"

**Context Window:**
- Include top 5 most relevant passages from knowledge base
- Limit to ~1000 tokens of context
- Prioritize Australian sources

**Acceptance Criteria:**
- [ ] RAG queries return relevant results
- [ ] Context properly injected into prompts
- [ ] No hallucinations despite context
- [ ] Context citations preserved

### Requirement 4: Educational Feedback for Students

**Specification:**
Generate personalized feedback aligned with student's training level and learning goals.

**Feedback Components:**
1. **Key Learning Points**: What should student focus on from this case
2. **Mastered Skills**: What the student did well
3. **Areas for Development**: Specific gaps to work on
4. **Mistakes Avoided**: What the student didn't make wrong
5. **Next Practice Focus**: Recommended next step
6. **Resources**: Recommended readings/references
7. **Coaching Tips**: Specific advice for improvement

**Personalization:**
- Adapt feedback based on student level (junior/senior trainee)
- Reference weak areas from student profile
- Provide scaffolded learning path
- Connect to ICRP training objectives

**Acceptance Criteria:**
- [ ] Feedback adapts to student level
- [ ] Specific and actionable (not generic)
- [ ] References learning objectives
- [ ] Recommends appropriate resources

### Requirement 5: Robust Error Handling & Recovery

**Specification:**
Handle API failures gracefully with retry logic and fallback strategies.

**Error Scenarios:**
1. **Rate Limit** (429 status)
   - Retry with exponential backoff (1s, 2s, 4s)
   - Max 3 retries
   - If still fails, return Layer 2 result only

2. **Timeout** (>30 seconds)
   - Cancel request after 30s
   - Return Layer 2 validation result immediately
   - Log timeout for monitoring

3. **Invalid Response** (malformed JSON)
   - Log full response for debugging
   - Return error with Layer 2 result
   - Alert ops/monitoring system

4. **API Error** (500, other errors)
   - Return Layer 2 result
   - Log error for investigation
   - Don't block user submission

5. **Network Error** (connection refused)
   - Retry up to 3 times
   - Return Layer 2 result on failure

**Acceptance Criteria:**
- [ ] No unhandled exceptions
- [ ] All errors logged with context
- [ ] Graceful fallback to Layer 2
- [ ] User not blocked on API failure
- [ ] Monitoring/alerting in place

---

## Acceptance Criteria

### Functionality
- [ ] ClaudeValidator class with 6+ methods implemented
- [ ] validate_soap_note() works with structured output
- [ ] validate_prescription_appropriateness() works with recommendations
- [ ] validate_pathology_order() works with test assessment
- [ ] validate_clinical_documentation_quality() comprehensive assessment
- [ ] generate_educational_feedback() personalized for students
- [ ] RAG context retrieval working
- [ ] Error handling for all failure scenarios

### Performance
- [ ] P95 response time <5 seconds
- [ ] P99 response time <10 seconds
- [ ] Timeout handling doesn't block user
- [ ] Graceful fallback to Layer 2

### Response Quality
- [ ] All responses valid JSON
- [ ] All required fields present
- [ ] Scores properly distributed (not all 100 or all 50)
- [ ] Feedback is specific and actionable
- [ ] Red flags identified when appropriate
- [ ] Educational feedback scaffolded to student level

### Integration
- [ ] Works with Layer 1 (Zod) types
- [ ] Works with Layer 2 (Rule validators) output
- [ ] RAG system properly integrated
- [ ] Unified API can orchestrate all 3 layers

### Testing
- [ ] 100+ test cases covering happy path and error scenarios
- [ ] Coverage ≥70% (pytest-cov)
- [ ] Mock Claude API for tests
- [ ] Mock RAG client for tests
- [ ] Performance benchmarks included

### Reliability
- [ ] Retry logic working correctly
- [ ] Error handling comprehensive
- [ ] No unhandled exceptions
- [ ] Logging for debugging
- [ ] Monitoring/alerting ready

---

## Testing Requirements

### Unit Tests

```python
def test_soap_validation_good_note():
    """Test validation of a high-quality SOAP note."""
    validator = ClaudeValidator(mock_api_key)
    result = validator.validate_soap_note(good_soap_note, patient_data)
    assert result.success
    assert result.overall_score >= 80

def test_soap_validation_poor_note():
    """Test validation of a low-quality SOAP note."""
    result = validator.validate_soap_note(poor_soap_note, patient_data)
    assert result.success
    assert result.overall_score < 60
    assert len(result.areas_for_improvement) > 0

def test_rate_limit_retry_succeeds():
    """Test retry after rate limit."""
    with patch('anthropic.Anthropic.messages.create') as mock_api:
        mock_api.side_effect = [
            RateLimitError(),
            RateLimitError(),
            {"content": [{"text": json.dumps(valid_response)}]}
        ]
        result = validator.validate_soap_note(note, patient)
        assert result.success
        assert mock_api.call_count == 3

def test_timeout_returns_layer2_result():
    """Test timeout returns Layer 2 validation only."""
    with patch('anthropic.Anthropic.messages.create') as mock_api:
        mock_api.side_effect = Timeout()
        result = validator.validate_soap_note(note, patient)
        # Should have Layer 2 result, not Layer 3
        assert "layer2_result" in result or not result.success
```

### Integration Tests
```python
def test_rag_context_improves_feedback():
    """Test that RAG context improves Claude feedback."""
    # Without RAG context
    result1 = validator.validate_soap_note(note, patient, use_rag=False)
    # With RAG context
    result2 = validator.validate_soap_note(note, patient, use_rag=True)
    # Both should succeed, but RAG version might be more detailed
    assert result1.success and result2.success
```

---

## Reference PRD Sections

### Backend API PRD
**Section**: Layer 3: AI-Powered Clinical Validation (Claude)
**Link**: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md`

### Validation Rules
**Link**: `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md`
**Sections**:
- Layer 3: AI-Powered Clinical Validation
- RAG Integration
- Educational Feedback

---

## Agent OS Delegation Prompt

```markdown
## TASK: Implement AI-Powered Clinical Validation (Claude 3.5 Sonnet)

### Context
You are implementing Layer 3 of a 3-layer validation architecture for an EMR practice system. This layer must:
1. Validate SOAP note quality using Claude 3.5 Sonnet
2. Assess prescription appropriateness with clinical reasoning
3. Evaluate pathology order completeness
4. Generate personalized educational feedback for students
5. Integrate with irStudy RAG knowledge base
6. Complete validation in 3-5 seconds
7. Provide structured JSON output
8. Handle API failures gracefully

### Pre-Implementation Checklist
- [ ] Read PROJECT_CONSTRAINTS.md (esp. Australian compliance and ICRP student focus)
- [ ] Review TASK_2.1 (Zod schemas) and TASK_2.2 (Rule validators)
- [ ] Check irStudy RAG system setup and query API
- [ ] Verify Anthropic SDK installed (^0.18.1)
- [ ] Review Claude 3.5 Sonnet model ID: claude-3-5-sonnet-20241022

### Deliverables

1. **Core AI Validator (280+ lines)**
   - `/backend/src/validators/ai_validator_claude.py`
   - ClaudeValidator class with:
     - __init__(api_key, rag_client): Initialize with API key and RAG
     - validate_soap_note(soap, patient, context=None): SOAP validation
       - Returns: overall_score (0-100), section_scores, strengths, improvements, australian_compliance, educational_feedback, red_flags, confidence
     - validate_prescription_appropriateness(prescription, soap, patient): Prescription assessment
       - Returns: appropriate (bool), score, rationale, dosing_notes, monitoring, alternatives, red_flags, feedback
     - validate_pathology_order(order, soap, patient): Order assessment
       - Returns: appropriate (bool), score, clinical_reasoning, missing_tests, redundant_tests, guidance
     - validate_clinical_documentation_quality(session_data): Overall quality assessment
       - Returns: overall_score, component_scores, strengths, gaps, compliance_issues, risks, recommendations
     - generate_educational_feedback(session_data, student_profile): Personalized student feedback
       - Returns: learning_points, mastered_skills, areas_for_development, mistakes_avoided, next_focus, resources, tips
     - batch_validate_sessions(sessions, concurrent=False): Validate multiple with rate limiting

2. **System Prompts (150+ lines)**
   - `/backend/src/validators/ai_prompts.py`
   - SOAP_VALIDATION_PROMPT: Evaluate SOAP completeness, quality, Australian compliance
   - PRESCRIPTION_VALIDATION_PROMPT: Evaluate prescription appropriateness
   - PATHOLOGY_VALIDATION_PROMPT: Evaluate pathology order completeness
   - Each prompt includes:
     - Context and evaluation criteria
     - Output format (JSON structure)
     - Scoring guidelines

3. **RAG Integration (100+ lines)**
   - `/backend/src/validators/rag_integration.py`
   - RAGContextRetriever class:
     - get_condition_context(chief_complaint, diagnosis): Guidelines for diagnosis
     - get_medication_context(medication): Drug info from knowledge base
     - get_pathology_context(test, age): Test indications/interpretation
     - get_differential_context(chief_complaint): Differential diagnosis guidance
     - get_guidelines_context(topic): Australian clinical guidelines

4. **Error Handling (80+ lines)**
   - `/backend/src/validators/ai_error_handler.py`
   - AIValidationError, APITimeoutError, APIRateLimitError, MalformedResponseError
   - handle_api_error(error, retry_count, max_retries): Exponential backoff retry
   - validate_json_response(response): JSON validation + required fields check
   - Retry logic: 1s, 2s, 4s delays on rate limit (max 3)

5. **Response Types (100+ lines)**
   - `/backend/src/validators/ai_response_types.py`
   - AIValidationResult dataclass
   - EducationalFeedback dataclass
   - DocumentationQualityResult dataclass
   - All serializable to JSON

6. **Configuration (60+ lines)**
   - `/backend/src/validators/ai_config.py`
   - CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
   - TEMPERATURE = 0.3
   - MAX_TOKENS = 2000
   - API_TIMEOUT_SECONDS = 30
   - Validation timeout = 45 seconds total
   - Rate limit retry backoff: [1, 2, 4] seconds
   - System prompts

7. **Tests (400+ lines, ≥70% coverage)**
   - `/backend/tests/validators/test_ai_validator_claude.py` (200+ lines)
     - test_validate_soap_note_success: Happy path
     - test_validate_prescription_appropriateness: Prescription validation
     - test_validate_pathology_order: Order validation
     - test_api_timeout_handling: Timeout returns Layer 2 result
     - test_rate_limit_retry: Retry succeeds on retry
     - test_malformed_json_response: Handle invalid JSON
     - test_educational_feedback_generation: Student feedback
     - test_batch_validate_sessions: Multiple sessions

   - `/backend/tests/validators/test_ai_prompts.py` (80+ lines)
     - Prompts are valid strings
     - Prompt injection prevention
     - Context insertion works

   - `/backend/tests/validators/test_rag_integration.py` (60+ lines)
     - RAG queries work
     - Context retrieval
     - Handling missing context

   - `/backend/tests/validators/conftest.py` (additions)
     - Mock Anthropic client
     - Mock RAG client
     - Sample Claude responses
     - Sample SOAP notes, prescriptions, pathology orders

### Critical Constraints

1. **Performance**: 3-5 second response time
   - RAG: 500-800ms
   - Claude API: 1500-2500ms
   - Parsing: 200-400ms
   - Total: <5 seconds
   - P95 <5s, P99 <10s

2. **Output Format**: Strictly structured JSON
   - All responses must validate against schema
   - Required fields present
   - Type validation on all fields
   - No markdown or explanation, just JSON

3. **RAG Integration**: Use irStudy knowledge base
   - Query top 5 most relevant passages
   - Limit context to ~1000 tokens
   - Prioritize Australian sources
   - Include citations if available

4. **Educational Feedback**: Personalized for students
   - Adapt to student level (junior/senior trainee)
   - Reference weak areas from profile
   - Provide scaffolded learning path
   - Connect to ICRP training objectives
   - Specific and actionable (not generic)

5. **Error Handling**: Graceful degradation
   - Rate limit: Retry with backoff (1s, 2s, 4s), max 3
   - Timeout: Return Layer 2 result immediately
   - Invalid JSON: Log and return error
   - Network: Retry up to 3 times
   - Never block user on API failure

6. **Australian Compliance**:
   - Use AMC Clinical Examination standards
   - Terminology is Australian (paracetamol, not acetaminophen)
   - Reference Australian guidelines (TGA, NHMRC)
   - Consider Australian healthcare context

### Validation Checklist (Agent Must Complete Before Returning)

- [ ] ClaudeValidator class created with all 6+ methods
- [ ] All system prompts created and validated
- [ ] RAG integration working: get_condition_context, get_medication_context, etc.
- [ ] Error handler: retry logic, timeout handling, JSON validation
- [ ] Response types: AIValidationResult, EducationalFeedback, DocumentationQualityResult
- [ ] Configuration file: model, timeouts, retry backoff, prompts
- [ ] validate_soap_note returns: overall_score, section_scores, strengths, improvements, compliance, feedback
- [ ] validate_prescription_appropriateness returns: appropriate, score, rationale, alternatives, red_flags
- [ ] validate_pathology_order returns: appropriate, score, missing/redundant tests
- [ ] generate_educational_feedback returns: learning_points, areas_for_development, resources
- [ ] batch_validate_sessions with rate limiting for multiple requests
- [ ] 100+ test cases written: pytest
- [ ] Coverage ≥70%: pytest --cov=src/validators --cov-report=term
- [ ] Mock Anthropic client in tests (no real API calls)
- [ ] Mock RAG client in tests
- [ ] P95 response time <5 seconds (measured in benchmarks)
- [ ] P99 response time <10 seconds
- [ ] Timeout handling returns Layer 2 result gracefully
- [ ] Rate limit retry succeeds on retry (mocked)
- [ ] All responses validate against schema
- [ ] Educational feedback is personalized and specific
- [ ] No unhandled exceptions
- [ ] All code follows PEP 8: pylint (target)
- [ ] Type hints on all functions
- [ ] Docstrings on all public methods
- [ ] Error messages clear and logged
- [ ] AIValidationResult serializable to JSON
- [ ] Ready to be called from unified API endpoint (TASK_2.4)

### Success Criteria (PM Will Validate)
- 0 pytest failures
- ≥70% code coverage
- 3-5 second response time (P95 <5s, P99 <10s)
- All responses valid JSON with required fields
- Graceful fallback to Layer 2 on timeout
- Rate limit retry working
- Educational feedback adapts to student level
- Ready for unified validation endpoint

### File Structure to Verify
```
backend/src/validators/
├── ai_validator_claude.py
├── ai_prompts.py
├── rag_integration.py
├── ai_error_handler.py
├── ai_response_types.py
└── ai_config.py

backend/tests/validators/
├── test_ai_validator_claude.py
├── test_ai_prompts.py
├── test_rag_integration.py
└── conftest.py (modifications)
```

### Next Steps After Completion
- TASK_2.4 will create unified validation API endpoint
- Frontend will call /api/v1/validation/soap-note which orchestrates all 3 layers
- Results will be displayed in frontend validation UI

### Environment Variables Needed
```
ANTHROPIC_API_KEY=sk-...
RAG_API_URL=http://localhost:8002/rag/query
RAG_API_KEY=...
```

### Questions Before Starting?
Contact PM for:
- RAG system query API details
- Claude model parameter recommendations
- Specific feedback examples for different student levels
- Performance profiling requirements
```

---

## Implementation Notes

### Architecture Patterns

1. **Dependency Injection**
   - RAG client passed to ClaudeValidator
   - API key from environment
   - Allows mocking for tests

2. **Prompt Engineering**
   - Use JSON mode in Claude API (if available)
   - Include explicit format instructions in prompts
   - Validate responses against schema
   - Use temperature=0.3 for consistency

3. **Context Window Management**
   - Limit RAG context to ~1000 tokens
   - Prioritize most relevant passages
   - Include source/reference in context
   - Let Claude cite sources

### Common Pitfalls to Avoid

1. **Don't trust Claude's JSON output implicitly**
   - Always validate response structure
   - Check for required fields
   - Validate data types
   - Have fallback/default values

2. **Don't make RAG queries too broad**
   - Specific queries get better results
   - "SOAP note standards for chest pain" better than "SOAP notes"
   - Include diagnosis/chief complaint in query

3. **Don't ignore timeouts**
   - Set timeout on API call (30 seconds)
   - Return Layer 2 result immediately if timeout
   - Don't retry on timeout
   - Log for monitoring

4. **Don't over-prompt the model**
   - Claude is good at following format instructions
   - Clear examples of desired JSON format
   - System prompt separate from user prompt
   - Keep prompts focused

---

## Progress Tracking

### Milestone 1: Core Validator & Prompts (2 hours)
- [ ] Create ClaudeValidator class
- [ ] Define SOAP validation prompt
- [ ] Define prescription validation prompt
- [ ] Define pathology validation prompt
- [ ] Implement validate_soap_note()
- [ ] Implement validate_prescription_appropriateness()

### Milestone 2: Additional Validators & RAG (1.5 hours)
- [ ] Implement validate_pathology_order()
- [ ] Implement validate_clinical_documentation_quality()
- [ ] Implement generate_educational_feedback()
- [ ] Create RAG integration module
- [ ] Test RAG context retrieval

### Milestone 3: Error Handling & Response Types (1 hour)
- [ ] Create error handler with retry logic
- [ ] Create response type dataclasses
- [ ] Create configuration file
- [ ] Implement timeout handling
- [ ] Implement rate limit retry

### Milestone 4: Testing & Optimization (1.5 hours)
- [ ] Write 100+ test cases
- [ ] Mock Anthropic API
- [ ] Mock RAG client
- [ ] Achieve ≥70% coverage
- [ ] Performance benchmarking
- [ ] Document test cases

---

**Status**: ⏳ Ready for Agent Delegation
**Next Task**: TASK_2.4_Unified_Validation_API.md (depends on TASK_2.3 completion)
**Review Checklist**: PM validates response quality and <5 second performance before TASK_2.4
