# TASK 2.3: AI Validation (Claude)

**Task ID**: TASK_2.3
**Phase**: Phase 2 - Validation Layer
**Estimated Time**: 6 hours
**Prerequisites**: Backend setup, Anthropic API key
**Dependencies**: Anthropic Python SDK, FastAPI

---

## Overview

Create AI-powered validation using Claude 3.5 Sonnet for **Layer 3 validation** (AI-based, 3-5s) with educational feedback. This layer provides deep clinical reasoning assessment and personalized learning feedback.

**Reference**: See `/home/dev/Development/irStudy/emr-practice-system/design-specs/MASTER_EMR_PRD.md` section on AI Validation.

---

## AI Validators to Create

### 1. Claude AI Validator Service (3 hours)

**File**: `/home/dev/Development/irStudy/backend/src/validators/ai_validator.py`

```python
"""
AI Validator using Claude 3.5 Sonnet
Provides deep clinical reasoning assessment and educational feedback
"""

import os
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
import json


class AIValidationResult:
    """AI validation result"""

    def __init__(self, data: Dict[str, Any]):
        self.clinical_accuracy = data.get('clinical_accuracy', 0)
        self.documentation_quality = data.get('documentation_quality', 0)
        self.completeness = data.get('completeness', 0)
        self.feedback = data.get('feedback', '')
        self.strengths = data.get('strengths', [])
        self.areas_for_improvement = data.get('areas_for_improvement', [])
        self.learning_points = data.get('learning_points', [])
        self.overall_score = data.get('overall_score', 0)


class AIValidator:
    """
    AI-powered validator using Claude 3.5 Sonnet

    Provides:
    1. Clinical reasoning assessment
    2. Documentation quality evaluation
    3. Educational feedback
    4. Personalized learning recommendations
    5. ICRP-specific guidance for IMGs
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI validator

        Args:
            api_key: Anthropic API key (defaults to env variable)
        """
        self.client = Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        self.model = 'claude-3-5-sonnet-20241022'

    async def validate_soap_note(
        self,
        soap_note: Dict[str, Any],
        patient_scenario: Optional[Dict[str, Any]] = None
    ) -> AIValidationResult:
        """
        Validate SOAP note with AI analysis

        Args:
            soap_note: SOAP note data
            patient_scenario: Patient scenario/OSCE case details

        Returns:
            AI validation result with educational feedback
        """
        prompt = self._build_soap_validation_prompt(soap_note, patient_scenario)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent evaluation
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )

            # Parse JSON response
            content = response.content[0].text
            result_data = json.loads(content)

            return AIValidationResult(result_data)

        except Exception as e:
            # Fallback result if AI fails
            return AIValidationResult({
                'clinical_accuracy': 70,
                'documentation_quality': 70,
                'completeness': 70,
                'feedback': f'AI validation unavailable: {str(e)}',
                'overall_score': 70
            })

    def _build_soap_validation_prompt(
        self,
        soap_note: Dict[str, Any],
        patient_scenario: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for SOAP note validation"""
        prompt = f"""You are an experienced Australian medical educator assessing an IMG (International Medical Graduate) preparing for ICRP (Intern Clinical Readiness Program).

**Task**: Evaluate the following SOAP note for clinical accuracy, documentation quality, and completeness. Provide educational feedback suitable for ICRP preparation.

**Patient Scenario**:
{json.dumps(patient_scenario, indent=2) if patient_scenario else 'Not provided'}

**SOAP Note Submitted**:
{json.dumps(soap_note, indent=2)}

**Evaluation Criteria**:

1. **Clinical Accuracy** (0-100):
   - Appropriate differential diagnosis
   - Logical clinical reasoning
   - Evidence-based management
   - Australian clinical guidelines compliance

2. **Documentation Quality** (0-100):
   - SOAP structure adherence
   - Clarity and professionalism
   - Appropriate detail level
   - Australian medical record standards

3. **Completeness** (0-100):
   - All relevant history elements (OLDCARTS)
   - Appropriate physical examination
   - Differential diagnosis documented
   - Complete management plan
   - Safety-netting and follow-up

**Output Format** (strict JSON):
```json
{{
  "clinical_accuracy": <score 0-100>,
  "documentation_quality": <score 0-100>,
  "completeness": <score 0-100>,
  "overall_score": <average score 0-100>,
  "feedback": "<2-3 paragraphs of constructive feedback>",
  "strengths": [
    "<strength 1>",
    "<strength 2>",
    "<strength 3>"
  ],
  "areas_for_improvement": [
    "<area 1 with specific suggestion>",
    "<area 2 with specific suggestion>",
    "<area 3 with specific suggestion>"
  ],
  "learning_points": [
    "<key learning point 1 with reference to Australian guidelines>",
    "<key learning point 2>",
    "<key learning point 3>"
  ]
}}
```

**Important**:
- Be constructive and educational, not punitive
- Reference Australian clinical guidelines (eTG, Therapeutic Guidelines)
- Consider ICRP competency standards
- Provide specific, actionable feedback
- Use Australian medical terminology and spelling

Return ONLY the JSON object, no other text."""

        return prompt

    async def validate_prescription(
        self,
        prescription: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> AIValidationResult:
        """
        Validate prescription with AI analysis

        Args:
            prescription: Prescription data
            patient_context: Patient demographics, allergies, comorbidities

        Returns:
            AI validation result
        """
        prompt = self._build_prescription_validation_prompt(prescription, patient_context)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )

            content = response.content[0].text
            result_data = json.loads(content)

            return AIValidationResult(result_data)

        except Exception as e:
            return AIValidationResult({
                'clinical_accuracy': 70,
                'overall_score': 70,
                'feedback': f'AI validation unavailable: {str(e)}'
            })

    def _build_prescription_validation_prompt(
        self,
        prescription: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for prescription validation"""
        prompt = f"""You are an Australian clinical pharmacologist assessing a prescription for educational purposes (ICRP preparation).

**Patient Context**:
{json.dumps(patient_context, indent=2) if patient_context else 'Not provided'}

**Prescription**:
{json.dumps(prescription, indent=2)}

**Evaluate**:
1. Appropriateness for indication
2. Dose and frequency correctness
3. PBS compliance (if applicable)
4. Safety considerations (contraindications, interactions)
5. Patient counseling points

**Output Format** (strict JSON):
```json
{{
  "clinical_accuracy": <score 0-100>,
  "overall_score": <score 0-100>,
  "feedback": "<1-2 paragraphs>",
  "strengths": ["<strength>"],
  "areas_for_improvement": ["<specific suggestion>"],
  "learning_points": [
    "<PBS restriction guidance if applicable>",
    "<Safety counseling point>",
    "<Australian prescribing guideline reference>"
  ]
}}
```

Reference Australian Medicines Handbook and PBS restrictions. Return ONLY JSON."""

        return prompt

    async def validate_pathology_order(
        self,
        pathology_order: Dict[str, Any],
        clinical_context: Optional[Dict[str, Any]] = None
    ) -> AIValidationResult:
        """
        Validate pathology order with AI analysis

        Args:
            pathology_order: Pathology order data
            clinical_context: Clinical indication and patient details

        Returns:
            AI validation result
        """
        prompt = self._build_pathology_validation_prompt(pathology_order, clinical_context)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )

            content = response.content[0].text
            result_data = json.loads(content)

            return AIValidationResult(result_data)

        except Exception as e:
            return AIValidationResult({
                'clinical_accuracy': 70,
                'overall_score': 70,
                'feedback': f'AI validation unavailable: {str(e)}'
            })

    def _build_pathology_validation_prompt(
        self,
        pathology_order: Dict[str, Any],
        clinical_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for pathology order validation"""
        prompt = f"""You are an Australian pathology specialist assessing a pathology request for educational purposes.

**Clinical Context**:
{json.dumps(clinical_context, indent=2) if clinical_context else 'Not provided'}

**Pathology Order**:
{json.dumps(pathology_order, indent=2)}

**Evaluate**:
1. Clinical appropriateness
2. MBS compliance
3. Cost-effectiveness
4. Adequacy of clinical indication
5. Test selection (right test for right indication)

**Output Format** (strict JSON):
```json
{{
  "clinical_accuracy": <score 0-100>,
  "overall_score": <score 0-100>,
  "feedback": "<1-2 paragraphs>",
  "strengths": ["<strength>"],
  "areas_for_improvement": ["<suggestion>"],
  "learning_points": [
    "<MBS item guidance>",
    "<Cost-effective alternative if applicable>",
    "<Choosing Wisely Australia recommendation if applicable>"
  ]
}}
```

Reference MBS pathology rules and Choosing Wisely Australia. Return ONLY JSON."""

        return prompt


# Example usage
if __name__ == '__main__':
    import asyncio

    async def test_validator():
        validator = AIValidator()

        test_soap = {
            'subjective': {
                'chiefComplaint': 'Chest pain',
                'hpi': 'Patient presents with 2 hours of central chest pain...'
            },
            'objective': {
                'vitalSigns': {
                    'temperature': 37.0,
                    'heartRate': 85,
                    'bloodPressureSystolic': 130,
                    'bloodPressureDiastolic': 80
                }
            },
            'assessment': {
                'primaryDiagnosis': 'Suspected ACS',
                'clinicalReasoning': 'Cardiac chest pain...'
            },
            'plan': {
                'investigations': 'ECG, troponin, CXR',
                'followUp': 'Cardiology review'
            }
        }

        result = await validator.validate_soap_note(test_soap)
        print(f"Score: {result.overall_score}")
        print(f"Feedback: {result.feedback}")

    asyncio.run(test_validator())
```

---

### 2. AI Validation API Endpoint (1.5 hours)

**File**: `/home/dev/Development/irStudy/backend/src/api/v1/ai_validation.py`

```python
"""
AI Validation API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

from src.validators.ai_validator import AIValidator


router = APIRouter(prefix='/api/v1/ai-validation', tags=['ai-validation'])

# Initialize AI validator
ai_validator = AIValidator()


class AIValidationRequest(BaseModel):
    """AI validation request"""
    type: str  # 'soap', 'prescription', 'pathology'
    data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class AIValidationResponse(BaseModel):
    """AI validation response"""
    clinical_accuracy: float
    documentation_quality: Optional[float] = None
    completeness: Optional[float] = None
    overall_score: float
    feedback: str
    strengths: list[str]
    areas_for_improvement: list[str]
    learning_points: list[str]


@router.post('/validate', response_model=AIValidationResponse)
async def ai_validate(request: AIValidationRequest):
    """
    Validate with AI (Claude 3.5 Sonnet)

    Args:
        request: AI validation request

    Returns:
        AI validation result with educational feedback
    """
    try:
        if request.type == 'soap':
            result = await ai_validator.validate_soap_note(
                request.data,
                request.context
            )

        elif request.type == 'prescription':
            result = await ai_validator.validate_prescription(
                request.data,
                request.context
            )

        elif request.type == 'pathology':
            result = await ai_validator.validate_pathology_order(
                request.data,
                request.context
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f'Unknown validation type: {request.type}'
            )

        return AIValidationResponse(
            clinical_accuracy=result.clinical_accuracy,
            documentation_quality=result.documentation_quality,
            completeness=result.completeness,
            overall_score=result.overall_score,
            feedback=result.feedback,
            strengths=result.strengths,
            areas_for_improvement=result.areas_for_improvement,
            learning_points=result.learning_points
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'AI validation failed: {str(e)}'
        )


@router.get('/health')
async def ai_health_check():
    """Check if AI validation service is available"""
    try:
        # Simple test to verify API key is configured
        if not ai_validator.client.api_key:
            return {
                'status': 'unavailable',
                'message': 'Anthropic API key not configured'
            }

        return {
            'status': 'available',
            'model': ai_validator.model
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
```

---

### 3. Combined Validation Pipeline (1.5 hours)

**File**: `/home/dev/Development/irStudy/backend/src/validators/validation_pipeline.py`

```python
"""
Combined 3-layer validation pipeline
Orchestrates client, Python, and AI validation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from src.validators.pbs_validator import PBSValidator, MOCK_PBS_DATABASE
from src.validators.mbs_validator import MBSValidator, MOCK_MBS_DATABASE
from src.validators.documentation_validator import DocumentationValidator
from src.validators.ai_validator import AIValidator


class ValidationPipeline:
    """
    Orchestrates 3-layer validation:
    - Layer 1: Client-side Zod (<50ms) - already done in frontend
    - Layer 2: Python rule-based (<1s)
    - Layer 3: AI Claude (3-5s)
    """

    def __init__(self):
        self.pbs_validator = PBSValidator(MOCK_PBS_DATABASE)
        self.mbs_validator = MBSValidator(MOCK_MBS_DATABASE)
        self.doc_validator = DocumentationValidator()
        self.ai_validator = AIValidator()

    async def validate_soap_note(
        self,
        soap_note: Dict[str, Any],
        layers: List[str] = ['python', 'ai'],
        patient_scenario: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate SOAP note through specified layers

        Args:
            soap_note: SOAP note data
            layers: Validation layers to use
            patient_scenario: OSCE scenario details

        Returns:
            Combined validation result
        """
        results = {
            'validation_layers': layers,
            'started_at': datetime.now().isoformat(),
            'python_validation': None,
            'ai_validation': None,
            'combined_score': 0,
            'is_valid': True
        }

        # Layer 2: Python validation
        if 'python' in layers:
            python_result = self.doc_validator.validate_soap_note(soap_note)
            results['python_validation'] = python_result
            results['is_valid'] = results['is_valid'] and python_result['is_valid']

        # Layer 3: AI validation
        if 'ai' in layers:
            ai_result = await self.ai_validator.validate_soap_note(
                soap_note,
                patient_scenario
            )
            results['ai_validation'] = {
                'clinical_accuracy': ai_result.clinical_accuracy,
                'documentation_quality': ai_result.documentation_quality,
                'completeness': ai_result.completeness,
                'overall_score': ai_result.overall_score,
                'feedback': ai_result.feedback,
                'strengths': ai_result.strengths,
                'areas_for_improvement': ai_result.areas_for_improvement,
                'learning_points': ai_result.learning_points
            }

        # Calculate combined score
        scores = []
        if results['python_validation']:
            scores.append(results['python_validation'].get('documentation_score', 0))
        if results['ai_validation']:
            scores.append(results['ai_validation']['overall_score'])

        results['combined_score'] = sum(scores) / len(scores) if scores else 0
        results['completed_at'] = datetime.now().isoformat()

        return results

    async def validate_prescription(
        self,
        prescription: Dict[str, Any],
        layers: List[str] = ['python', 'ai'],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate prescription through specified layers"""
        results = {
            'validation_layers': layers,
            'started_at': datetime.now().isoformat(),
            'python_validation': None,
            'ai_validation': None,
            'is_valid': True
        }

        # Layer 2: Python (PBS validation)
        if 'python' in layers:
            python_result = self.pbs_validator.validate_prescription(prescription)
            results['python_validation'] = python_result
            results['is_valid'] = results['is_valid'] and python_result['is_valid']

        # Layer 3: AI validation
        if 'ai' in layers:
            ai_result = await self.ai_validator.validate_prescription(
                prescription,
                patient_context
            )
            results['ai_validation'] = {
                'clinical_accuracy': ai_result.clinical_accuracy,
                'overall_score': ai_result.overall_score,
                'feedback': ai_result.feedback,
                'strengths': ai_result.strengths,
                'areas_for_improvement': ai_result.areas_for_improvement,
                'learning_points': ai_result.learning_points
            }

        results['completed_at'] = datetime.now().isoformat()
        return results

    async def validate_pathology_order(
        self,
        pathology_order: Dict[str, Any],
        layers: List[str] = ['python', 'ai'],
        clinical_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate pathology order through specified layers"""
        results = {
            'validation_layers': layers,
            'started_at': datetime.now().isoformat(),
            'python_validation': None,
            'ai_validation': None,
            'is_valid': True
        }

        # Layer 2: Python (MBS validation)
        if 'python' in layers:
            python_result = self.mbs_validator.validate_pathology_order(pathology_order)
            results['python_validation'] = python_result
            results['is_valid'] = results['is_valid'] and python_result['is_valid']

        # Layer 3: AI validation
        if 'ai' in layers:
            ai_result = await self.ai_validator.validate_pathology_order(
                pathology_order,
                clinical_context
            )
            results['ai_validation'] = {
                'clinical_accuracy': ai_result.clinical_accuracy,
                'overall_score': ai_result.overall_score,
                'feedback': ai_result.feedback,
                'strengths': ai_result.strengths,
                'areas_for_improvement': ai_result.areas_for_improvement,
                'learning_points': ai_result.learning_points
            }

        results['completed_at'] = datetime.now().isoformat()
        return results
```

---

## Environment Configuration

**File**: `/home/dev/Development/irStudy/backend/.env.example`

```bash
# Anthropic API
ANTHROPIC_API_KEY=your_api_key_here

# Validation settings
AI_VALIDATION_ENABLED=true
AI_VALIDATION_TIMEOUT=10  # seconds
AI_VALIDATION_MODEL=claude-3-5-sonnet-20241022

# Rate limiting (for cost control)
AI_VALIDATION_MAX_REQUESTS_PER_DAY=1000
AI_VALIDATION_MAX_REQUESTS_PER_USER=100
```

---

## Validation Checklist

Before marking this task complete, verify:

- [ ] AI Validator class created
- [ ] SOAP note validation working
- [ ] Prescription validation working
- [ ] Pathology order validation working
- [ ] JSON response parsing correct
- [ ] Error handling for API failures
- [ ] Fallback results when AI unavailable
- [ ] API endpoints created
- [ ] Health check endpoint working
- [ ] Combined validation pipeline working
- [ ] All 3 layers orchestrated correctly
- [ ] Environment variables configured
- [ ] Anthropic API key tested
- [ ] No Python errors
- [ ] Async/await used correctly
- [ ] Rate limiting considered

---

## Performance Targets

- AI validation response time: **3-5 seconds**
- Fallback to Python-only if AI > 10 seconds
- Cache AI results for identical inputs (optional optimization)
- Cost control: Max 1000 AI validations/day

---

## Time Breakdown

- Claude AI Validator Service: 3 hours
- AI Validation API Endpoint: 1.5 hours
- Combined Validation Pipeline: 1.5 hours
- **Total**: 6 hours

---

## Phase 2 Complete!

After completing this task, Phase 2 (Validation Layer) is complete. Next steps:

1. **Phase 3**: Backend (TASK_3.1 - TASK_3.4)
2. **Phase 4**: Integration (TASK_4.1 - TASK_4.2)

---

**Last Updated**: 2026-02-03
**Status**: Ready for Implementation
