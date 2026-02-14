# TASK 2.4: Unified Validation API Orchestration (Layer Orchestration)

**Phase**: Phase 2 - Validation Architecture
**Estimated Hours**: 2 hours
**Dependencies**: TASK_2.1, TASK_2.2, TASK_2.3 Complete (All 3 layers implemented)
**Agent Type**: `backend-api-expert`
**Status**: ⏳ Not Started

---

## Overview

Create the unified API orchestration layer that coordinates all three validation layers, executing them in sequence (Layer 1 → Layer 2 → Layer 3) with intelligent branching logic. If critical errors are detected in Layer 2, skip Layer 3. Returns comprehensive ValidationResult containing results from all layers executed plus timing metrics. Provides single endpoint for frontend clients to perform complete validation without managing layer complexity.

---

## Deliverables

### API Endpoint Implementation

#### 1. `/backend/src/api/v1/validation.py` (250+ lines)

**FastAPI Router: validation_router**

```python
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from ..models import ValidationRequest, ValidationResponse, SOAPNote, Prescription, PathologyOrder
from ..validators import (
    soapNoteSchema, prescriptionSchema, pathologyOrderSchema,  # Layer 1
    PBSValidator, MBSValidator, ClinicalSafetyValidator,      # Layer 2
    ClaudeValidator                                              # Layer 3
)
from ..auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/validation", tags=["validation"])
```

**Endpoints to Create:**

1. **POST /api/v1/validation/soap-note** (150+ lines)
   ```python
   @router.post("/soap-note", response_model=ValidationResponse)
   async def validate_soap_note(
       request: ValidateSoapNoteRequest,
       user=Depends(get_current_user),
       background_tasks: BackgroundTasks = None
   ) -> ValidationResponse:
       """
       Validate SOAP note through all 3 layers.

       Layer 1 (Client-side): Format & structure validation
       Layer 2 (Rule-based): Clinical safety, red flags
       Layer 3 (AI): Clinical reasoning, completeness assessment

       Args:
           request: SOAP note data + validation flags
           user: Authenticated user
           background_tasks: For logging/telemetry

       Returns:
           ValidationResponse with results from all layers executed
       """
       # Validation request structure:
       # {
       #   "soap_note": {...},
       #   "patient": {...},
       #   "skip_layer_3": bool,  # Optional: skip AI validation if false
       #   "include_educational_feedback": bool  # Optional: generate student feedback
       # }

       # Response structure:
       # {
       #   "success": bool,
       #   "overall_valid": bool,
       #   "layers_executed": ["layer1", "layer2", "layer3"],
       #   "layer1_result": {...},
       #   "layer2_result": {...},
       #   "layer3_result": {...},  // Optional
       #   "combined_errors": [...],
       #   "combined_warnings": [...],
       #   "timing": {
       #     "layer1_ms": float,
       #     "layer2_ms": float,
       #     "layer3_ms": float,
       #     "total_ms": float
       #   },
       #   "user_id": str,
       #   "timestamp": datetime
       # }
   ```

   **Logic Flow:**
   ```
   1. Parse and validate request
   2. LAYER 1: Zod schema validation
      └─ If fails, return Layer 1 errors only
   3. LAYER 2: Rule-based validation
      ├─ PBS validation
      ├─ Clinical safety checks
      └─ Check for critical errors
   4. LAYER 3 DECISION:
      ├─ If skip_layer_3=true → Return Layer 1+2 result
      ├─ If Layer 2 has CRITICAL errors → Skip Layer 3, return Layer 1+2
      └─ Else → Execute Layer 3
   5. Return combined result with timing
   ```

2. **POST /api/v1/validation/prescription** (120+ lines)
   ```python
   @router.post("/prescription", response_model=ValidationResponse)
   async def validate_prescription(
       request: ValidatePrescriptionRequest,
       user=Depends(get_current_user)
   ) -> ValidationResponse:
       """
       Validate prescription through all 3 layers.

       Args:
           request: {
               "prescription": {...},
               "soap_note": {...},  // For context
               "patient": {...},
               "skip_layer_3": bool
           }

       Returns:
           ValidationResponse with combined results
       """
   ```

   **Logic Flow:** Same structure as SOAP validation

3. **POST /api/v1/validation/pathology-order** (100+ lines)
   ```python
   @router.post("/pathology-order", response_model=ValidationResponse)
   async def validate_pathology_order(
       request: ValidatePathologyOrderRequest,
       user=Depends(get_current_user)
   ) -> ValidationResponse:
       """
       Validate pathology order through all 3 layers.

       Args:
           request: {
               "pathology_order": {...},
               "soap_note": {...},  // For context
               "patient": {...},
               "skip_layer_3": bool
           }

       Returns:
           ValidationResponse with combined results
       """
   ```

4. **POST /api/v1/validation/session** (180+ lines)
   ```python
   @router.post("/session", response_model=BatchValidationResponse)
   async def validate_session(
       request: ValidateSessionRequest,
       user=Depends(get_current_user)
   ) -> BatchValidationResponse:
       """
       Validate entire EMR session (SOAP + prescriptions + pathology).

       Orchestrates validation of all components and checks cross-component compatibility.

       Args:
           request: {
               "soap_note": {...},
               "prescriptions": [...],
               "pathology_orders": [...],
               "patient": {...},
               "skip_layer_3": bool
           }

       Returns:
           BatchValidationResponse with:
               - soap_note_validation: ValidationResult
               - prescription_validations: List[ValidationResult]
               - pathology_validations: List[ValidationResult]
               - combined_validation: ValidationResult (cross-component checks)
               - ready_for_submission: bool
               - critical_issues: List[str]
       """

       # Validate each component
       # Check cross-component compatibility:
       #   - All prescriptions have indications in assessment
       #   - All investigations justified by assessment
       #   - No duplicate medications
       #   - No duplicate pathology tests
       #   - Prescriptions appropriate for documented diagnosis
       #   - Pathology appropriate for documented diagnosis
   ```

### Request/Response Types

#### 2. `/backend/src/schemas/validation_schemas.py` (120+ lines)

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class LayerName(str, Enum):
    LAYER1 = "layer1"
    LAYER2 = "layer2"
    LAYER3 = "layer3"

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class ValidationIssue(BaseModel):
    """Single validation issue."""
    field: str  # e.g., "subjective.chiefComplaint"
    message: str
    severity: SeverityLevel
    layer: LayerName
    suggested_value: Optional[str] = None

class ValidateSoapNoteRequest(BaseModel):
    """Request to validate SOAP note."""
    soap_note: dict  # SOAP note data
    patient: dict  # Patient demographics
    skip_layer_3: bool = False
    include_educational_feedback: bool = False

class ValidatePrescriptionRequest(BaseModel):
    """Request to validate prescription."""
    prescription: dict
    soap_note: dict  # For context
    patient: dict
    skip_layer_3: bool = False

class ValidatePathologyOrderRequest(BaseModel):
    """Request to validate pathology order."""
    pathology_order: dict
    soap_note: dict
    patient: dict
    skip_layer_3: bool = False

class ValidateSessionRequest(BaseModel):
    """Request to validate entire session."""
    soap_note: dict
    prescriptions: List[dict]
    pathology_orders: List[dict]
    patient: dict
    skip_layer_3: bool = False

class LayerResult(BaseModel):
    """Result from single layer."""
    layer: LayerName
    success: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    score: Optional[int] = None  # For Layer 3 only (0-100)
    data: Optional[Dict[str, Any]] = None
    execution_time_ms: float

class ValidationResponse(BaseModel):
    """Unified response from all layers."""
    success: bool
    overall_valid: bool  # All layers passed
    layers_executed: List[LayerName]
    layer1_result: Optional[LayerResult] = None
    layer2_result: Optional[LayerResult] = None
    layer3_result: Optional[LayerResult] = None
    combined_errors: List[ValidationIssue]
    combined_warnings: List[ValidationIssue]
    timing: Dict[str, float]  # {"layer1_ms": 5, "layer2_ms": 150, ...}
    ready_for_submission: bool
    user_id: str
    timestamp: datetime

class BatchValidationResponse(BaseModel):
    """Response for batch validation (entire session)."""
    success: bool
    soap_note_result: ValidationResponse
    prescription_results: List[ValidationResponse]
    pathology_results: List[ValidationResponse]
    combined_issues: List[ValidationIssue]
    cross_component_issues: List[ValidationIssue]
    ready_for_submission: bool
    submission_blocking_issues: List[str]
    warnings_acknowledged: Optional[bool] = None
    user_id: str
    timestamp: datetime
```

### Orchestration Service

#### 3. `/backend/src/services/validation_orchestrator.py` (200+ lines)

```python
import time
from typing import List, Dict, Optional, Tuple
from ..validators import (
    soapNoteSchema, prescriptionSchema, pathologyOrderSchema,
    PBSValidator, MBSValidator, ClinicalSafetyValidator,
    ClaudeValidator,
    ValidationIssue, SeverityLevel, LayerName, LayerResult, ValidationResponse
)
from ..models import SOAPNote, Prescription, PathologyOrder, Patient

class ValidationOrchestrator:
    """Orchestrates validation across all 3 layers."""

    def __init__(self, claude_validator: ClaudeValidator):
        self.layer2_validators = {
            "pbs": PBSValidator(),
            "mbs": MBSValidator(),
            "safety": ClinicalSafetyValidator()
        }
        self.layer3_validator = claude_validator

    def validate_soap_note(
        self,
        soap_note: dict,
        patient: dict,
        skip_layer_3: bool = False,
        include_feedback: bool = False
    ) -> ValidationResponse:
        """
        Orchestrate SOAP note validation across layers.

        Layer 1: Zod schema validation
        Layer 2: Clinical safety rules
        Layer 3: AI assessment (if not skipped and no critical errors)
        """
        start_time = time.time()
        layers_executed = []
        all_results = {}

        # LAYER 1: Client-side validation
        layer1_start = time.time()
        layer1_result = self._validate_layer1_soap(soap_note)
        layer1_time = (time.time() - layer1_start) * 1000
        layers_executed.append(LayerName.LAYER1)
        all_results["layer1"] = layer1_result

        # If Layer 1 fails, return immediately
        if not layer1_result.success:
            return self._build_response(
                layers_executed,
                all_results,
                time.time() - start_time
            )

        # LAYER 2: Rule-based validation
        layer2_start = time.time()
        layer2_result = self._validate_layer2_soap(soap_note, patient)
        layer2_time = (time.time() - layer2_start) * 1000
        layers_executed.append(LayerName.LAYER2)
        all_results["layer2"] = layer2_result

        # LAYER 3: AI validation (if appropriate)
        layer3_result = None
        layer3_time = 0

        if not skip_layer_3 and not layer2_result.has_critical_errors():
            layer3_start = time.time()
            try:
                layer3_result = self._validate_layer3_soap(
                    soap_note,
                    patient,
                    include_feedback
                )
                layer3_time = (time.time() - layer3_start) * 1000
                layers_executed.append(LayerName.LAYER3)
                all_results["layer3"] = layer3_result
            except Exception as e:
                # Log error but don't block - return Layer 1+2 result
                logger.error(f"Layer 3 validation failed: {e}")
                layer3_result = None

        return self._build_response(
            layers_executed,
            all_results,
            time.time() - start_time,
            {
                "layer1_ms": layer1_time,
                "layer2_ms": layer2_time,
                "layer3_ms": layer3_time
            }
        )

    def validate_prescription(
        self,
        prescription: dict,
        soap_note: dict,
        patient: dict,
        skip_layer_3: bool = False
    ) -> ValidationResponse:
        """Orchestrate prescription validation."""
        # Similar structure to validate_soap_note
        ...

    def validate_pathology_order(
        self,
        order: dict,
        soap_note: dict,
        patient: dict,
        skip_layer_3: bool = False
    ) -> ValidationResponse:
        """Orchestrate pathology order validation."""
        # Similar structure
        ...

    def validate_session(
        self,
        soap_note: dict,
        prescriptions: List[dict],
        pathology_orders: List[dict],
        patient: dict,
        skip_layer_3: bool = False
    ) -> Dict:
        """
        Validate entire session and cross-component compatibility.

        Returns batch result with:
        - Individual validations for each component
        - Cross-component compatibility checks
        - Overall readiness for submission
        """
        # Validate each component
        soap_result = self.validate_soap_note(soap_note, patient, skip_layer_3)

        prescription_results = [
            self.validate_prescription(p, soap_note, patient, skip_layer_3)
            for p in prescriptions
        ]

        pathology_results = [
            self.validate_pathology_order(o, soap_note, patient, skip_layer_3)
            for o in pathology_orders
        ]

        # Check cross-component compatibility
        cross_component_issues = self._check_cross_component_compatibility(
            soap_note,
            prescriptions,
            pathology_orders,
            patient
        )

        # Determine readiness
        ready = (
            soap_result.overall_valid and
            all(r.overall_valid for r in prescription_results) and
            all(r.overall_valid for r in pathology_results) and
            len(cross_component_issues) == 0
        )

        return {
            "soap_note_result": soap_result,
            "prescription_results": prescription_results,
            "pathology_results": pathology_results,
            "cross_component_issues": cross_component_issues,
            "ready_for_submission": ready
        }

    # Helper methods

    def _validate_layer1_soap(self, data: dict) -> LayerResult:
        """Validate using Zod schema."""
        # Parse with soapNoteSchema
        # Return LayerResult

    def _validate_layer2_soap(self, soap_note: dict, patient: dict) -> LayerResult:
        """Validate clinical safety rules."""
        # Run safety validator, PBS (if medications), etc.
        # Return LayerResult

    def _validate_layer3_soap(
        self,
        soap_note: dict,
        patient: dict,
        include_feedback: bool = False
    ) -> LayerResult:
        """Validate using Claude AI."""
        # Run ClaudeValidator.validate_soap_note()
        # Include educational feedback if requested
        # Return LayerResult

    def _check_cross_component_compatibility(
        self,
        soap_note: dict,
        prescriptions: List[dict],
        pathology_orders: List[dict],
        patient: dict
    ) -> List[ValidationIssue]:
        """
        Check compatibility between components.

        - All prescriptions have indications in assessment
        - All investigations ordered in plan
        - No duplicate medications
        - No duplicate tests
        - Prescriptions match diagnosis
        - Investigations match diagnosis
        """
        issues = []

        # Check prescriptions against assessment
        assessment_text = soap_note.get("assessment", {}).get("diagnosis", "")
        for prescription in prescriptions:
            indication = prescription.get("indication", "")
            # Ensure indication relates to diagnosis
            if not self._indication_matches_diagnosis(indication, assessment_text):
                issues.append(ValidationIssue(
                    field="prescription.indication",
                    message=f"Indication '{indication}' doesn't match documented diagnosis",
                    severity=SeverityLevel.WARNING,
                    layer=LayerName.LAYER2
                ))

        # Check for duplicates
        med_names = [p.get("medication") for p in prescriptions]
        if len(med_names) != len(set(med_names)):
            issues.append(ValidationIssue(
                field="prescriptions",
                message="Duplicate medications detected",
                severity=SeverityLevel.CRITICAL,
                layer=LayerName.LAYER2
            ))

        return issues

    def _indication_matches_diagnosis(self, indication: str, diagnosis: str) -> bool:
        """Simple check: ensure some overlap between indication and diagnosis."""
        # This could be enhanced with NLP/RAG
        return any(word in diagnosis.lower() for word in indication.lower().split())

    def _build_response(
        self,
        layers_executed: List[LayerName],
        results: Dict,
        total_time_ms: float,
        timing_breakdown: Optional[Dict] = None
    ) -> ValidationResponse:
        """Combine results from all executed layers."""
        # Aggregate errors and warnings
        # Build ValidationResponse
        ...
```

### Error Handling & Monitoring

#### 4. `/backend/src/validators/validation_exceptions.py` (40+ lines)

```python
class ValidationException(Exception):
    """Base exception for validation errors."""
    pass

class Layer1ValidationException(ValidationException):
    """Schema validation failed."""
    pass

class Layer2ValidationException(ValidationException):
    """Rule-based validation failed."""
    pass

class Layer3ValidationException(ValidationException):
    """AI validation failed."""
    pass

class ValidationTimeoutException(ValidationException):
    """Validation timed out."""
    pass
```

### Testing Files

#### 5. `/backend/tests/api/test_validation_endpoints.py` (250+ lines)

```python
import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

class TestSOAPValidationEndpoint:
    """Test POST /api/v1/validation/soap-note."""

    def test_valid_soap_returns_layer_results(self, auth_token):
        """Test valid SOAP note returns results from all layers."""
        response = client.post(
            "/api/v1/validation/soap-note",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "soap_note": valid_soap_note(),
                "patient": valid_patient_data(),
                "skip_layer_3": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["overall_valid"] is True
        assert "layer1_result" in data
        assert "layer2_result" in data
        assert "layer3_result" in data

    def test_invalid_soap_returns_layer1_errors(self, auth_token):
        """Test invalid SOAP returns Layer 1 errors only."""
        response = client.post(
            "/api/v1/validation/soap-note",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "soap_note": invalid_soap_note(),  # Missing required fields
                "patient": valid_patient_data()
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["overall_valid"] is False
        assert "layer1_result" in data
        assert data["layer1_result"]["success"] is False
        # Layer 2+ should not have executed
        assert "layer2_result" not in data or data["layer2_result"] is None

    def test_skip_layer3_flag(self, auth_token):
        """Test skip_layer_3=true skips AI validation."""
        response = client.post(
            "/api/v1/validation/soap-note",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "soap_note": valid_soap_note(),
                "patient": valid_patient_data(),
                "skip_layer_3": True
            }
        )
        data = response.json()
        assert "layer3_result" not in data["layers_executed"]

    def test_timing_breakdown(self, auth_token):
        """Test response includes timing for each layer."""
        response = client.post(
            "/api/v1/validation/soap-note",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "soap_note": valid_soap_note(),
                "patient": valid_patient_data()
            }
        )
        data = response.json()
        assert "timing" in data
        assert "layer1_ms" in data["timing"]
        assert "layer2_ms" in data["timing"]
        assert "layer3_ms" in data["timing"]
        assert "total_ms" in data["timing"]

class TestPrescriptionValidationEndpoint:
    """Test POST /api/v1/validation/prescription."""

    def test_valid_prescription(self, auth_token):
        """Test valid prescription passes all layers."""
        response = client.post(
            "/api/v1/validation/prescription",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "prescription": valid_prescription(),
                "soap_note": valid_soap_note(),
                "patient": valid_patient_data()
            }
        )
        assert response.status_code == 200
        assert response.json()["overall_valid"] is True

class TestSessionValidationEndpoint:
    """Test POST /api/v1/validation/session."""

    def test_session_validation_comprehensive(self, auth_token):
        """Test validation of entire session."""
        response = client.post(
            "/api/v1/validation/session",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "soap_note": valid_soap_note(),
                "prescriptions": [valid_prescription()],
                "pathology_orders": [valid_pathology_order()],
                "patient": valid_patient_data()
            }
        )
        data = response.json()
        assert "soap_note_result" in data
        assert "prescription_results" in data
        assert "pathology_results" in data
        assert "cross_component_issues" in data
        assert "ready_for_submission" in data

    def test_session_cross_component_validation(self, auth_token):
        """Test cross-component compatibility checks."""
        # Prescription indication doesn't match diagnosis
        response = client.post(
            "/api/v1/validation/session",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "soap_note": {"assessment": {"diagnosis": "Hypertension"}},
                "prescriptions": [
                    {"medication": "Amoxicillin", "indication": "Respiratory infection"}
                ],
                "pathology_orders": [],
                "patient": valid_patient_data()
            }
        )
        data = response.json()
        assert len(data["cross_component_issues"]) > 0
```

#### 6. `/backend/tests/services/test_validation_orchestrator.py` (150+ lines)

```python
import pytest
from services.validation_orchestrator import ValidationOrchestrator

class TestValidationOrchestrator:
    """Test validation orchestration logic."""

    def test_layer1_failure_skips_layers2_3(self):
        """Test Layer 1 failure returns immediately."""
        orchestrator = ValidationOrchestrator(mock_claude)
        response = orchestrator.validate_soap_note(
            invalid_soap_note(),
            patient_data()
        )
        assert response.overall_valid is False
        assert LayerName.LAYER2 not in response.layers_executed
        assert LayerName.LAYER3 not in response.layers_executed

    def test_layer2_critical_errors_skip_layer3(self):
        """Test Layer 2 critical errors skip Layer 3."""
        orchestrator = ValidationOrchestrator(mock_claude)
        # Create SOAP that passes Layer 1 but has Layer 2 critical errors
        response = orchestrator.validate_soap_note(
            soap_with_critical_error(),
            patient_data()
        )
        assert LayerName.LAYER3 not in response.layers_executed

    def test_all_layers_execute_on_success(self):
        """Test all layers execute when earlier layers pass."""
        response = orchestrator.validate_soap_note(
            valid_soap_note(),
            patient_data()
        )
        assert len(response.layers_executed) == 3

    def test_cross_component_duplicate_detection(self):
        """Test cross-component check detects duplicates."""
        issues = orchestrator._check_cross_component_compatibility(
            valid_soap_note(),
            [
                valid_prescription(medication="Paracetamol"),
                valid_prescription(medication="Paracetamol")  # Duplicate
            ],
            [],
            patient_data()
        )
        assert any("duplicate" in issue.message.lower() for issue in issues)
```

---

## Detailed Requirements

### Requirement 1: Proper Layer Sequencing

**Specification:**
Execute layers in sequence with intelligent branching based on results.

**Execution Logic:**
```
Layer 1 (Zod)
  ├─ If FAIL → Return Layer 1 only
  └─ If PASS ↓
    Layer 2 (Rules)
      ├─ If NO CRITICAL errors ↓
      │  Layer 3 (AI) [if not skipped]
      │    └─ Always return result (even if times out)
      └─ If CRITICAL errors → Skip Layer 3
```

**Acceptance Criteria:**
- [ ] Layer 1 failure returns immediately
- [ ] Layer 2 critical errors skip Layer 3
- [ ] Layer 3 timeout doesn't block Layer 1+2 result
- [ ] All executed layers included in response
- [ ] Correct layer ordering in layers_executed list

### Requirement 2: Comprehensive Error Aggregation

**Specification:**
Combine errors from all layers into single view with proper attribution.

**Aggregation Strategy:**
- Track which layer each error came from
- Sort by severity (CRITICAL first)
- Group by field/category
- Preserve original error messages with layer context
- Provide suggestions from appropriate layer

**Acceptance Criteria:**
- [ ] All layer errors aggregated
- [ ] Layer attribution maintained
- [ ] Sorted by severity
- [ ] No duplicate errors
- [ ] Clear which layer reported each issue

### Requirement 3: Cross-Component Compatibility Checks

**Specification:**
Verify session components are compatible and aligned.

**Compatibility Checks:**
- Prescriptions have indications that match assessment
- Investigations listed in plan match ordered pathology
- No duplicate medications
- No duplicate pathology tests
- Prescription medications appropriate for diagnosis
- Pathology tests appropriate for diagnosis
- Patient allergies respected in all prescriptions

**Acceptance Criteria:**
- [ ] All compatibility checks implemented
- [ ] Detects duplicate prescriptions
- [ ] Detects duplicate pathology orders
- [ ] Identifies misaligned prescriptions/diagnosis
- [ ] Respects allergy constraints
- [ ] Clear messaging on each violation

### Requirement 4: Timing Metrics & Performance Tracking

**Specification:**
Track and report execution time for each layer and total.

**Metrics to Track:**
```json
{
  "timing": {
    "layer1_ms": 5,
    "layer2_ms": 145,
    "layer3_ms": 2850,
    "total_ms": 3000
  }
}
```

**Performance Targets:**
- Layer 1: <50ms
- Layer 2: <1000ms
- Layer 3: <5000ms (with graceful timeout)
- Total: <6000ms

**Acceptance Criteria:**
- [ ] All layers report execution time
- [ ] Timing breakdown in response
- [ ] Timing accurate to within 10%
- [ ] Total time = sum of layers (approximately)
- [ ] Timeout behavior doesn't hang response

### Requirement 5: Graceful Degradation on Failures

**Specification:**
Handle failures in any layer without blocking user submission.

**Failure Scenarios:**
1. **Layer 1 Failure**: Return immediately with errors
2. **Layer 2 Failure**: Should not happen (rules should work), but if it does, return Layer 1 only
3. **Layer 3 Timeout**: Return Layer 1+2 with note about timeout
4. **Layer 3 API Error**: Return Layer 1+2 with note about API error
5. **Invalid JSON from AI**: Return Layer 1+2 with note about parsing error

**Acceptance Criteria:**
- [ ] No unhandled exceptions
- [ ] All errors logged properly
- [ ] User always gets result (not blank page)
- [ ] Clear indication of what failed
- [ ] Still provide feedback from successful layers

---

## Acceptance Criteria

### Functionality
- [ ] All 4 endpoints implemented: soap-note, prescription, pathology-order, session
- [ ] Layer 1 → 2 → 3 sequencing works correctly
- [ ] Intelligent branching (skip Layer 3 on critical errors)
- [ ] Combined errors from all layers
- [ ] Cross-component compatibility checking
- [ ] Timing metrics for each layer and total
- [ ] Graceful degradation on failures
- [ ] All endpoints return consistent ValidationResponse structure

### API Design
- [ ] Request/response models well-defined
- [ ] Proper HTTP status codes (200 for validation, 400 for bad request, 401 for auth)
- [ ] Clear error messages
- [ ] Documentation/docstrings on all endpoints
- [ ] OpenAPI/Swagger auto-generated and accurate

### Integration
- [ ] Orchestrator properly calls Layer 1, 2, and 3 validators
- [ ] Receives Zod ValidationResult from Layer 1
- [ ] Receives Python ValidationResult from Layer 2
- [ ] Receives Claude ValidationResult from Layer 3
- [ ] Combines results correctly
- [ ] All validators initialize properly at startup

### Testing
- [ ] 100+ test cases covering:
     - Valid data (all layers pass)
     - Invalid data (Layer 1 fails)
     - Layer 2 critical errors (skip Layer 3)
     - Layer 3 timeout (return Layer 1+2)
     - Cross-component violations
     - Timing metrics
- [ ] Coverage ≥70%
- [ ] Tests mock all external dependencies
- [ ] Performance tests ensure <5 second response

### Performance
- [ ] P95 response time <5 seconds
- [ ] Layer 3 timeout doesn't exceed 45 seconds total
- [ ] All endpoints return in <6 seconds worst case
- [ ] Timing breakdown accurate

### Error Handling
- [ ] No unhandled exceptions in endpoints
- [ ] All errors logged with context
- [ ] User always gets result (graceful fallback)
- [ ] Clear error messages in response
- [ ] Proper HTTP error codes

---

## Reference PRD Sections

### Backend API PRD
**Section**: Validation API Endpoints
**Link**: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md`

### Complete Validation Rules
**Link**: `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md`

---

## Agent OS Delegation Prompt

```markdown
## TASK: Implement Unified Validation API (Layer Orchestration)

### Context
You are implementing the orchestration layer that ties together all 3 validation layers (Zod, Python rules, Claude AI) into unified API endpoints. This layer must:
1. Execute validation in sequence: Layer 1 → Layer 2 → Layer 3
2. Skip Layer 3 if Layer 2 has critical errors
3. Return combined results with timing metrics
4. Check cross-component compatibility for entire sessions
5. Handle failures gracefully (always return result)
6. Provide single endpoint for frontend clients

### Pre-Implementation Checklist
- [ ] TASK_2.1 (Zod schemas) complete and working
- [ ] TASK_2.2 (Rule validators) complete with ≥70% coverage
- [ ] TASK_2.3 (Claude validator) complete and tested
- [ ] All validators importable and functional
- [ ] Backend API infrastructure working (FastAPI, auth, etc.)

### Deliverables

1. **API Endpoints (4 endpoints, 650+ lines total)**
   - `/backend/src/api/v1/validation.py`
   - POST /api/v1/validation/soap-note
     - Input: soap_note, patient, skip_layer_3, include_educational_feedback
     - Output: ValidationResponse with Layer 1+2+3 results
   - POST /api/v1/validation/prescription
     - Input: prescription, soap_note, patient, skip_layer_3
     - Output: ValidationResponse
   - POST /api/v1/validation/pathology-order
     - Input: pathology_order, soap_note, patient, skip_layer_3
     - Output: ValidationResponse
   - POST /api/v1/validation/session
     - Input: soap_note, prescriptions[], pathology_orders[], patient, skip_layer_3
     - Output: BatchValidationResponse with individual results + cross-component checks

2. **Request/Response Types (120+ lines)**
   - `/backend/src/schemas/validation_schemas.py`
   - ValidateSoapNoteRequest, ValidatePrescriptionRequest, etc.
   - ValidationIssue, LayerResult, ValidationResponse
   - BatchValidationResponse
   - All properly typed with Pydantic

3. **Orchestration Service (200+ lines)**
   - `/backend/src/services/validation_orchestrator.py`
   - ValidationOrchestrator class:
     - validate_soap_note(soap, patient, skip_layer3): Sequence layers
     - validate_prescription(prescription, soap, patient, skip_layer3)
     - validate_pathology_order(order, soap, patient, skip_layer3)
     - validate_session(soap, prescriptions[], orders[], patient, skip_layer3)
     - _validate_layer1_*(): Call Zod validators
     - _validate_layer2_*(): Call rule validators
     - _validate_layer3_*(): Call Claude validator
     - _check_cross_component_compatibility(): Duplicate/misalignment checks
     - _build_response(): Aggregate results

4. **Error Handling (40+ lines)**
   - `/backend/src/validators/validation_exceptions.py`
   - Custom exceptions for each layer
   - Proper exception hierarchy

5. **Tests (400+ lines, ≥70% coverage)**
   - `/backend/tests/api/test_validation_endpoints.py` (250+ lines)
     - test_valid_soap_returns_layer_results
     - test_invalid_soap_returns_layer1_errors
     - test_skip_layer3_flag
     - test_timing_breakdown
     - test_valid_prescription, test_valid_pathology
     - test_session_validation_comprehensive
     - test_session_cross_component_validation
     - test_layer1_failure_skips_layer2_3
     - test_layer2_critical_skips_layer3
     - test_all_layers_execute_on_success

   - `/backend/tests/services/test_validation_orchestrator.py` (150+ lines)
     - All orchestration logic tested
     - Cross-component detection tests
     - Timing metric tests

### Critical Constraints

1. **Layer Sequencing**:
   - Layer 1 → 2 → 3 in order
   - Layer 1 fail: return immediately, don't run 2+3
   - Layer 2 critical errors: skip Layer 3
   - Layer 3 timeout/error: return Layer 1+2 anyway

2. **Response Format**:
   - Always return ValidationResponse (consistent structure)
   - Include layers_executed (which layers actually ran)
   - Aggregate errors with layer attribution
   - Include timing breakdown

3. **Cross-Component Checks**:
   - Duplicate prescriptions/tests detection
   - Indication-to-diagnosis alignment
   - Allergy conflict checking across all prescriptions
   - Clear messaging on violations

4. **Performance**:
   - P95 <5 seconds total
   - Layer 3 timeout doesn't exceed 45 seconds
   - Timing metrics accurate
   - No blocking on any layer

5. **Error Handling**:
   - No unhandled exceptions
   - All errors logged with context
   - Graceful fallback (never return blank/error page)
   - User always gets response

### Validation Checklist (Agent Must Complete Before Returning)

- [ ] All 4 endpoints created and functional
- [ ] POST /api/v1/validation/soap-note working
- [ ] POST /api/v1/validation/prescription working
- [ ] POST /api/v1/validation/pathology-order working
- [ ] POST /api/v1/validation/session working with batch results
- [ ] Layer 1 validator (Zod) integrated and called
- [ ] Layer 2 validators (PBS, MBS, Safety) integrated and called
- [ ] Layer 3 validator (Claude) integrated and called
- [ ] Layer sequencing correct: 1 → 2 → 3
- [ ] Layer 1 failure returns immediately (doesn't run 2+3)
- [ ] Layer 2 critical errors skip Layer 3
- [ ] Layer 3 timeout/error doesn't block Layer 1+2 result
- [ ] Combined errors aggregated from all layers
- [ ] Layer attribution on each error
- [ ] Errors sorted by severity (CRITICAL first)
- [ ] Cross-component compatibility checks working
- [ ] Duplicate detection (medications, tests)
- [ ] Indication-to-diagnosis alignment checking
- [ ] Timing metrics for each layer and total
- [ ] Timing accuracy verified
- [ ] All request/response types defined with Pydantic
- [ ] Request validation working (bad requests return 400)
- [ ] Authentication required (401 if no token)
- [ ] Session validation returns individual + combined results
- [ ] ready_for_submission flag accurate
- [ ] 100+ test cases written: pytest
- [ ] Coverage ≥70%: pytest --cov
- [ ] All tests pass: pytest
- [ ] Mock validators in tests (no real API calls)
- [ ] Performance tests verify <5 second P95
- [ ] Timeout handling tested
- [ ] Error scenarios tested (Layer 1 fail, Layer 3 timeout, etc.)
- [ ] OpenAPI/Swagger documentation auto-generated
- [ ] Docstrings on all endpoints
- [ ] Error messages clear and actionable
- [ ] No unhandled exceptions
- [ ] Logging for all failures
- [ ] All dependencies imported and working

### Success Criteria (PM Will Validate)
- 0 test failures
- ≥70% code coverage
- P95 response time <5 seconds
- All 4 endpoints working
- Correct layer sequencing
- Graceful error handling
- Clear validation feedback to user
- Ready to integrate with frontend

### File Structure to Verify
```
backend/src/
├── api/
│   └── v1/
│       └── validation.py (4 endpoints)
├── schemas/
│   └── validation_schemas.py (request/response types)
├── services/
│   └── validation_orchestrator.py (orchestration logic)
└── validators/
    └── validation_exceptions.py

backend/tests/
├── api/
│   └── test_validation_endpoints.py
└── services/
    └── test_validation_orchestrator.py
```

### Next Steps After Completion
- Phase 2 Validation complete
- Frontend ready to integrate with validation endpoints
- Move to Phase 3 (UI/Integration) or Phase 4 (Deployment)
```

---

## Implementation Notes

### API Design Patterns

1. **Consistent Response Format**
   - Always return same ValidationResponse structure
   - Include layers_executed to show what ran
   - Aggregate errors with layer attribution
   - Include timing for performance monitoring

2. **Error Attribution**
   - Every error includes which layer reported it
   - Helps user understand source of issue
   - Useful for debugging

3. **Graceful Degradation**
   - If Layer 3 fails, return Layer 1+2 result anyway
   - If Layer 2 fails (shouldn't happen), return Layer 1 + error
   - Never block user on any validation layer

### Testing Strategy

1. **Happy Path Tests**
   - Valid data passes all layers
   - Timing metrics present
   - All results returned

2. **Error Path Tests**
   - Invalid Layer 1: Skip 2+3
   - Invalid Layer 2: Skip 3
   - Invalid Layer 3: Return 1+2 anyway
   - Timeouts: Return 1+2

3. **Cross-Component Tests**
   - Duplicate detection
   - Indication alignment
   - Allergy conflicts

4. **Performance Tests**
   - Each endpoint <5 seconds
   - Timing breakdown accurate
   - Concurrent requests handled

---

## Progress Tracking

### Milestone 1: API Endpoints (1 hour)
- [ ] Create validation.py router
- [ ] Implement SOAP note endpoint
- [ ] Implement prescription endpoint
- [ ] Implement pathology endpoint
- [ ] Implement session endpoint

### Milestone 2: Orchestration Service (0.5 hours)
- [ ] Create ValidationOrchestrator class
- [ ] Implement layer sequencing logic
- [ ] Implement layer branching (skip on critical errors)
- [ ] Implement cross-component checks
- [ ] Implement error aggregation

### Milestone 3: Types & Error Handling (0.3 hours)
- [ ] Create validation request/response types
- [ ] Create validation exceptions
- [ ] Implement error handling in endpoints

### Milestone 4: Testing & Documentation (0.2 hours)
- [ ] Write 100+ tests
- [ ] Achieve ≥70% coverage
- [ ] Document endpoints
- [ ] Verify OpenAPI generation

---

## Files to Create/Modify

### Create
```
/backend/src/api/v1/validation.py
/backend/src/schemas/validation_schemas.py
/backend/src/services/validation_orchestrator.py
/backend/src/validators/validation_exceptions.py
/backend/tests/api/test_validation_endpoints.py
/backend/tests/services/test_validation_orchestrator.py
```

### Modify
```
/backend/src/main.py
  - Import validation router
  - Include router in FastAPI app

/backend/requirements.txt
  - Verify pydantic installed
  - Verify pytest installed
```

---

**Status**: ⏳ Ready for Agent Delegation
**Prerequisite**: TASK_2.1, TASK_2.2, TASK_2.3 all complete
**Review Checklist**: PM validates layer sequencing and <5 second performance before Phase 2 completion
