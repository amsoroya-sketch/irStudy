"""
AI Validator using Kimi 2.5 (Free Alternative to Claude)
Provides deep clinical reasoning assessment and educational feedback
"""

import os
from typing import Dict, Any, List, Optional
import json

from src.ai_router.kimi_adapter import KimiAdapter


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


class AIValidatorKimi:
    """
    AI-powered validator using Kimi 2.5 (FREE)

    Provides:
    1. Clinical reasoning assessment
    2. Documentation quality evaluation
    3. Educational feedback
    4. Personalized learning recommendations
    5. ICRP-specific guidance for IMGs

    Uses Kimi 2.5 instead of Claude for FREE usage
    """

    def __init__(self, kimi_api_key: Optional[str] = None):
        """
        Initialize AI validator with Kimi

        Args:
            kimi_api_key: Kimi API key (defaults to env variable)
        """
        self.adapter = KimiAdapter(kimi_api_key=kimi_api_key or os.getenv('KIMI_API_KEY'))
        self.model = 'moonshot-v1-128k'  # Kimi's best model

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
            response = await self.adapter.create_message(
                model='claude-3-5-sonnet-20241022',  # Will be mapped to Kimi model
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )

            # Extract text from response
            content = response.get('content', [{}])[0]
            text = content.get('text', '{}')

            # Parse JSON response
            result_data = json.loads(text)

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
            response = await self.adapter.create_message(
                model='claude-3-5-sonnet-20241022',
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )

            content = response.get('content', [{}])[0]
            text = content.get('text', '{}')
            result_data = json.loads(text)

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
            response = await self.adapter.create_message(
                model='claude-3-5-sonnet-20241022',
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )

            content = response.get('content', [{}])[0]
            text = content.get('text', '{}')
            result_data = json.loads(text)

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

    async def close(self):
        """Close adapter connection"""
        await self.adapter.close()


# Example usage
if __name__ == '__main__':
    import asyncio

    async def test_validator():
        validator = AIValidatorKimi()

        test_soap = {
            'subjective': {
                'chiefComplaint': 'Chest pain',
                'hpi': 'Patient presents with 2 hours of central chest pain, sharp in nature, radiating to left arm. Associated with shortness of breath and diaphoresis. No previous episodes. Risk factors: smoker, hypertension.'
            },
            'objective': {
                'vitalSigns': {
                    'temperature': 37.0,
                    'heartRate': 95,
                    'bloodPressureSystolic': 145,
                    'bloodPressureDiastolic': 90,
                    'respiratoryRate': 18,
                    'oxygenSaturation': 97
                },
                'generalAppearance': 'Anxious, diaphoretic',
                'cardiovascularExam': 'Regular rhythm, no murmurs'
            },
            'assessment': {
                'primaryDiagnosis': 'Suspected acute coronary syndrome',
                'clinicalReasoning': 'Cardiac chest pain with typical features and risk factors. Differential includes ACS, pulmonary embolism, aortic dissection.'
            },
            'plan': {
                'investigations': 'ECG, troponin, CXR, FBC, UEC',
                'medications': 'Aspirin 300mg stat, GTN sublingual PRN',
                'followUp': 'Cardiology review, serial troponins'
            }
        }

        result = await validator.validate_soap_note(test_soap)
        print(f"Overall Score: {result.overall_score}")
        print(f"Clinical Accuracy: {result.clinical_accuracy}")
        print(f"\nFeedback:\n{result.feedback}")
        print(f"\nStrengths:")
        for strength in result.strengths:
            print(f"  - {strength}")
        print(f"\nAreas for Improvement:")
        for area in result.areas_for_improvement:
            print(f"  - {area}")

        await validator.close()

    asyncio.run(test_validator())
