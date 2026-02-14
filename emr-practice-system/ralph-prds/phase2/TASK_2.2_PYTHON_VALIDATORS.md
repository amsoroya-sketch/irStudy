# TASK 2.2: Python Rule-Based Validators

**Task ID**: TASK_2.2
**Phase**: Phase 2 - Validation Layer
**Estimated Time**: 10 hours
**Prerequisites**: Backend setup (Python 3.11, FastAPI)
**Dependencies**: FastAPI, Pydantic, Australian PBS/MBS databases

---

## Overview

Create Python validators for **Layer 2 validation** (rule-based, <1s) with Australian clinical compliance (PBS, MBS, TGA). These validators enforce complex rules that require database lookups and business logic.

**Reference**: See `/home/dev/Development/irStudy/emr-practice-system/design-specs/MASTER_EMR_PRD.md` section on Validation Architecture.

---

## Validators to Create

### 1. PBS Prescription Validator (3 hours)

**File**: `/home/dev/Development/irStudy/backend/src/validators/pbs_validator.py`

```python
"""
PBS (Pharmaceutical Benefits Scheme) Prescription Validator
Validates prescriptions against Australian PBS rules
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PBSRestriction(BaseModel):
    """PBS restriction criteria"""
    code: str
    description: str
    requires_authority: bool
    streamlined_authority: bool
    criteria: List[str]


class PBSMedication(BaseModel):
    """PBS medication entry"""
    pbs_code: str
    drug_name: str
    max_quantity: int
    max_repeats: int
    restrictions: List[PBSRestriction]
    authority_required: bool
    safety_net_eligible: bool


class ValidationError(BaseModel):
    """Validation error"""
    field: str
    message: str
    severity: str = Field(default="error")  # error, warning, info
    suggestion: Optional[str] = None


class PBSValidator:
    """
    Validates prescriptions against PBS rules

    Rules enforced:
    1. PBS code validity
    2. Quantity within PBS limits
    3. Repeats within PBS limits
    4. Authority requirements
    5. Restriction criteria
    6. Drug interactions
    7. Contraindications
    """

    def __init__(self, pbs_database: Dict[str, PBSMedication]):
        """
        Initialize with PBS database

        Args:
            pbs_database: Dictionary of PBS medications keyed by PBS code
        """
        self.pbs_db = pbs_database

    def validate_prescription(self, prescription: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single prescription

        Args:
            prescription: Prescription data

        Returns:
            Validation result with errors and warnings
        """
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []
        suggestions: List[str] = []

        # Extract prescription details
        pbs_code = prescription.get('pbsCode')
        quantity = prescription.get('quantity', 0)
        repeats = prescription.get('repeats', 0)
        authority_number = prescription.get('authorityNumber')
        indication = prescription.get('indication', '')

        # PBS code validation
        if pbs_code:
            pbs_entry = self.pbs_db.get(pbs_code)

            if not pbs_entry:
                errors.append(ValidationError(
                    field='pbsCode',
                    message=f'Invalid PBS code: {pbs_code}',
                    severity='error',
                    suggestion='Check PBS schedule for correct code'
                ))
            else:
                # Validate quantity
                if quantity > pbs_entry.max_quantity:
                    errors.append(ValidationError(
                        field='quantity',
                        message=f'Quantity ({quantity}) exceeds PBS maximum ({pbs_entry.max_quantity})',
                        severity='error',
                        suggestion=f'Reduce quantity to {pbs_entry.max_quantity} or request authority'
                    ))

                # Validate repeats
                if repeats > pbs_entry.max_repeats:
                    errors.append(ValidationError(
                        field='repeats',
                        message=f'Repeats ({repeats}) exceeds PBS maximum ({pbs_entry.max_repeats})',
                        severity='error',
                        suggestion=f'Maximum {pbs_entry.max_repeats} repeats allowed'
                    ))

                # Authority validation
                if pbs_entry.authority_required and not authority_number:
                    errors.append(ValidationError(
                        field='authorityNumber',
                        message='PBS authority number required for this medication',
                        severity='error',
                        suggestion='Obtain authority via phone (1800 888 333) or online'
                    ))

                # Restriction criteria
                for restriction in pbs_entry.restrictions:
                    if not self._check_restriction(restriction, indication):
                        warnings.append(ValidationError(
                            field='indication',
                            message=f'Indication may not meet PBS restriction: {restriction.description}',
                            severity='warning',
                            suggestion='Verify patient meets PBS criteria'
                        ))

        # Brand vs generic check
        if prescription.get('brandName') and not prescription.get('brandSubstitutionNotPermitted'):
            suggestions.append('Consider prescribing by generic name unless brand substitution not permitted')

        return {
            'is_valid': len(errors) == 0,
            'errors': [e.dict() for e in errors],
            'warnings': [w.dict() for w in warnings],
            'suggestions': suggestions,
            'pbs_compliant': len(errors) == 0
        }

    def _check_restriction(self, restriction: PBSRestriction, indication: str) -> bool:
        """
        Check if indication meets restriction criteria

        Args:
            restriction: PBS restriction
            indication: Prescription indication

        Returns:
            True if likely meets criteria (simple keyword matching)
        """
        # Simple keyword matching - in production, use NLP or rule engine
        indication_lower = indication.lower()

        for criterion in restriction.criteria:
            if any(keyword in indication_lower for keyword in criterion.lower().split()):
                return True

        return False

    def validate_batch(self, prescriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate multiple prescriptions and check for drug interactions

        Args:
            prescriptions: List of prescription data

        Returns:
            Combined validation result
        """
        all_errors = []
        all_warnings = []
        all_suggestions = []

        # Validate each prescription
        for idx, prescription in enumerate(prescriptions):
            result = self.validate_prescription(prescription)

            # Prefix field names with index
            for error in result['errors']:
                error['field'] = f'prescriptions[{idx}].{error["field"]}'
                all_errors.append(error)

            for warning in result['warnings']:
                warning['field'] = f'prescriptions[{idx}].{warning["field"]}'
                all_warnings.append(warning)

            all_suggestions.extend(result['suggestions'])

        # Check drug interactions
        interactions = self._check_drug_interactions(prescriptions)
        all_warnings.extend(interactions)

        return {
            'is_valid': len(all_errors) == 0,
            'errors': all_errors,
            'warnings': all_warnings,
            'suggestions': list(set(all_suggestions)),  # Remove duplicates
            'batch_size': len(prescriptions)
        }

    def _check_drug_interactions(self, prescriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check for drug-drug interactions

        Args:
            prescriptions: List of prescriptions

        Returns:
            List of interaction warnings
        """
        warnings = []

        # Common interaction pairs (simplified - use proper database in production)
        known_interactions = {
            ('warfarin', 'aspirin'): 'Increased bleeding risk',
            ('warfarin', 'nsaid'): 'Increased bleeding risk',
            ('ace_inhibitor', 'potassium_sparing_diuretic'): 'Hyperkalaemia risk',
            ('ssri', 'tramadol'): 'Serotonin syndrome risk',
        }

        medications = [p.get('medication', '').lower() for p in prescriptions]

        for (drug1, drug2), risk in known_interactions.items():
            if any(drug1 in med for med in medications) and any(drug2 in med for med in medications):
                warnings.append({
                    'field': 'prescriptions',
                    'message': f'Potential drug interaction: {risk}',
                    'severity': 'warning',
                    'suggestion': 'Review interaction and consider alternatives or monitoring'
                })

        return warnings


# Example PBS database (simplified - load from actual PBS data in production)
MOCK_PBS_DATABASE = {
    '01234A': PBSMedication(
        pbs_code='01234A',
        drug_name='Amoxicillin 500mg capsules',
        max_quantity=20,
        max_repeats=1,
        restrictions=[],
        authority_required=False,
        safety_net_eligible=True
    ),
    '02345B': PBSMedication(
        pbs_code='02345B',
        drug_name='Atorvastatin 40mg tablets',
        max_quantity=30,
        max_repeats=5,
        restrictions=[],
        authority_required=False,
        safety_net_eligible=True
    ),
    '03456C': PBSMedication(
        pbs_code='03456C',
        drug_name='Adalimumab 40mg injection',
        max_quantity=2,
        max_repeats=5,
        restrictions=[
            PBSRestriction(
                code='R001',
                description='Rheumatoid arthritis - severe active disease',
                requires_authority=True,
                streamlined_authority=False,
                criteria=['rheumatoid arthritis', 'failed methotrexate', 'DAS28 > 5.1']
            )
        ],
        authority_required=True,
        safety_net_eligible=True
    )
}


# Usage example
if __name__ == '__main__':
    validator = PBSValidator(MOCK_PBS_DATABASE)

    test_prescription = {
        'medication': 'Amoxicillin',
        'pbsCode': '01234A',
        'quantity': 20,
        'repeats': 1,
        'indication': 'Community acquired pneumonia'
    }

    result = validator.validate_prescription(test_prescription)
    print(result)
```

---

### 2. MBS Pathology Validator (3 hours)

**File**: `/home/dev/Development/irStudy/backend/src/validators/mbs_validator.py`

```python
"""
MBS (Medicare Benefits Schedule) Pathology Validator
Validates pathology orders against Australian MBS rules
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel


class MBSPathologyItem(BaseModel):
    """MBS pathology item"""
    mbs_code: str
    test_name: str
    category: str
    fee: float
    bulk_bill_eligible: bool
    restrictions: List[str]
    frequency_rules: Optional[Dict[str, Any]] = None  # e.g., {'max_per_year': 2}


class MBSValidator:
    """
    Validates pathology orders against MBS rules

    Rules enforced:
    1. MBS code validity
    2. Clinical indication adequacy
    3. Frequency restrictions
    4. Bulk billing eligibility
    5. Duplicate test prevention
    6. Inappropriate test combinations
    """

    def __init__(self, mbs_database: Dict[str, MBSPathologyItem]):
        """
        Initialize with MBS database

        Args:
            mbs_database: Dictionary of MBS items keyed by MBS code
        """
        self.mbs_db = mbs_database

    def validate_pathology_order(
        self,
        order: Dict[str, Any],
        recent_tests: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Validate a pathology order

        Args:
            order: Pathology order data
            recent_tests: Recent tests for frequency checking

        Returns:
            Validation result
        """
        errors = []
        warnings = []
        suggestions = []

        mbs_code = order.get('mbsCode')
        clinical_indication = order.get('clinicalIndication', '')
        urgency = order.get('urgency', 'routine')
        test_name = order.get('testName', '')

        # MBS code validation
        if mbs_code:
            mbs_item = self.mbs_db.get(mbs_code)

            if not mbs_item:
                errors.append({
                    'field': 'mbsCode',
                    'message': f'Invalid MBS code: {mbs_code}',
                    'severity': 'error'
                })
            else:
                # Clinical indication check
                if len(clinical_indication) < 10:
                    errors.append({
                        'field': 'clinicalIndication',
                        'message': 'Clinical indication too brief - must justify test',
                        'severity': 'error',
                        'suggestion': 'Provide specific clinical reason for test'
                    })

                # Frequency restrictions
                if recent_tests and mbs_item.frequency_rules:
                    freq_violation = self._check_frequency(
                        mbs_item,
                        recent_tests,
                        test_name
                    )

                    if freq_violation:
                        warnings.append({
                            'field': 'mbsCode',
                            'message': freq_violation,
                            'severity': 'warning'
                        })

                # Bulk billing
                if order.get('bulkBilled', False) and not mbs_item.bulk_bill_eligible:
                    errors.append({
                        'field': 'bulkBilled',
                        'message': 'This test is not eligible for bulk billing',
                        'severity': 'error'
                    })

        # Urgency validation
        if urgency == 'stat' and len(order.get('clinicalNotes', '')) < 10:
            errors.append({
                'field': 'clinicalNotes',
                'message': 'STAT orders require detailed clinical justification',
                'severity': 'error',
                'suggestion': 'Explain why urgent processing is medically necessary'
            })

        # Provider number validation
        provider_number = order.get('providerNumber', '')
        if provider_number and not self._validate_provider_number(provider_number):
            errors.append({
                'field': 'providerNumber',
                'message': 'Invalid Australian provider number format',
                'severity': 'error'
            })

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions,
            'mbs_compliant': len(errors) == 0
        }

    def validate_batch(
        self,
        orders: List[Dict[str, Any]],
        recent_tests: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Validate batch of pathology orders

        Args:
            orders: List of pathology orders
            recent_tests: Recent tests for frequency checking

        Returns:
            Combined validation result
        """
        all_errors = []
        all_warnings = []
        all_suggestions = []

        # Validate each order
        for idx, order in enumerate(orders):
            result = self.validate_pathology_order(order, recent_tests)

            for error in result['errors']:
                error['field'] = f'orders[{idx}].{error["field"]}'
                all_errors.append(error)

            for warning in result['warnings']:
                warning['field'] = f'orders[{idx}].{warning["field"]}'
                all_warnings.append(warning)

            all_suggestions.extend(result['suggestions'])

        # Check for duplicate tests
        duplicates = self._check_duplicates(orders)
        all_warnings.extend(duplicates)

        # Check for inappropriate combinations
        inappropriate = self._check_inappropriate_combinations(orders)
        all_warnings.extend(inappropriate)

        return {
            'is_valid': len(all_errors) == 0,
            'errors': all_errors,
            'warnings': all_warnings,
            'suggestions': list(set(all_suggestions)),
            'batch_size': len(orders)
        }

    def _check_frequency(
        self,
        mbs_item: MBSPathologyItem,
        recent_tests: List[Dict[str, Any]],
        test_name: str
    ) -> Optional[str]:
        """Check if test violates frequency rules"""
        if not mbs_item.frequency_rules:
            return None

        max_per_year = mbs_item.frequency_rules.get('max_per_year')
        if max_per_year:
            # Count recent tests within 1 year
            one_year_ago = datetime.now() - timedelta(days=365)
            recent_count = sum(
                1 for test in recent_tests
                if test.get('testName') == test_name
                and datetime.fromisoformat(test.get('requestedDate', '')) > one_year_ago
            )

            if recent_count >= max_per_year:
                return f'Test frequency exceeded: maximum {max_per_year} per year (found {recent_count} recent)'

        return None

    def _validate_provider_number(self, provider_number: str) -> bool:
        """Validate Australian provider number format"""
        import re
        # Australian provider numbers: 6-8 digits optionally followed by 1-2 letters
        pattern = r'^\d{6,8}[A-Z]{0,2}$'
        return bool(re.match(pattern, provider_number))

    def _check_duplicates(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for duplicate tests in batch"""
        warnings = []
        test_names = [order.get('testName', '').lower() for order in orders]

        seen = set()
        for idx, name in enumerate(test_names):
            if name in seen:
                warnings.append({
                    'field': f'orders[{idx}].testName',
                    'message': f'Duplicate test in batch: {name}',
                    'severity': 'warning'
                })
            seen.add(name)

        return warnings

    def _check_inappropriate_combinations(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for clinically inappropriate test combinations"""
        warnings = []

        # Example: Don't order both TSH and Free T4 as initial thyroid screen
        test_names = {order.get('testName', '').lower() for order in orders}

        if 'tsh' in test_names and 'free t4' in test_names:
            warnings.append({
                'field': 'orders',
                'message': 'Consider TSH alone as initial thyroid screen (more cost-effective)',
                'severity': 'info'
            })

        return warnings


# Example MBS database
MOCK_MBS_DATABASE = {
    '65070': MBSPathologyItem(
        mbs_code='65070',
        test_name='Full Blood Count',
        category='haematology',
        fee=16.90,
        bulk_bill_eligible=True,
        restrictions=[],
        frequency_rules=None
    ),
    '66512': MBSPathologyItem(
        mbs_code='66512',
        test_name='TSH',
        category='biochemistry',
        fee=16.90,
        bulk_bill_eligible=True,
        restrictions=[],
        frequency_rules={'max_per_year': 2}
    ),
    '66695': MBSPathologyItem(
        mbs_code='66695',
        test_name='Vitamin D',
        category='biochemistry',
        fee=30.05,
        bulk_bill_eligible=False,
        restrictions=['Clinical deficiency suspected'],
        frequency_rules={'max_per_year': 1}
    )
}
```

---

### 3. Clinical Documentation Validator (2 hours)

**File**: `/home/dev/Development/irStudy/backend/src/validators/documentation_validator.py`

```python
"""
Clinical Documentation Validator
Validates SOAP notes for completeness and quality
"""

from typing import Dict, Any, List
import re


class DocumentationValidator:
    """
    Validates clinical documentation quality

    Rules enforced:
    1. Completeness of SOAP sections
    2. Appropriate detail level
    3. Clinical reasoning present
    4. Follow-up documented
    5. Safety-netting included
    6. Red flags addressed
    """

    def validate_soap_note(self, soap_note: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate SOAP note completeness and quality

        Args:
            soap_note: SOAP note data

        Returns:
            Validation result
        """
        errors = []
        warnings = []
        suggestions = []
        score = 100

        # Validate Subjective section
        subjective = soap_note.get('subjective', {})
        subj_result = self._validate_subjective(subjective)
        errors.extend(subj_result['errors'])
        warnings.extend(subj_result['warnings'])
        score -= subj_result['penalty']

        # Validate Objective section
        objective = soap_note.get('objective', {})
        obj_result = self._validate_objective(objective)
        errors.extend(obj_result['errors'])
        warnings.extend(obj_result['warnings'])
        score -= obj_result['penalty']

        # Validate Assessment section
        assessment = soap_note.get('assessment', {})
        assess_result = self._validate_assessment(assessment)
        errors.extend(assess_result['errors'])
        warnings.extend(assess_result['warnings'])
        score -= assess_result['penalty']

        # Validate Plan section
        plan = soap_note.get('plan', {})
        plan_result = self._validate_plan(plan)
        errors.extend(plan_result['errors'])
        warnings.extend(plan_result['warnings'])
        score -= plan_result['penalty']

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions,
            'documentation_score': max(0, score),
            'completeness': self._calculate_completeness(soap_note)
        }

    def _validate_subjective(self, subjective: Dict[str, Any]) -> Dict[str, Any]:
        """Validate subjective section"""
        errors = []
        warnings = []
        penalty = 0

        hpi = subjective.get('hpi', '')

        # Check for key elements (OLDCARTS)
        elements = {
            'onset': ['started', 'began', 'commenced', 'first noticed'],
            'location': ['left', 'right', 'bilateral', 'radiates'],
            'duration': ['hours', 'days', 'weeks', 'months', 'minutes'],
            'character': ['sharp', 'dull', 'aching', 'burning', 'stabbing'],
            'aggravating': ['worse', 'aggravated', 'exacerbated'],
            'relieving': ['better', 'relieved', 'improved'],
            'timing': ['constant', 'intermittent', 'comes and goes'],
            'severity': ['mild', 'moderate', 'severe', '/10']
        }

        missing_elements = []
        for element, keywords in elements.items():
            if not any(keyword in hpi.lower() for keyword in keywords):
                missing_elements.append(element)

        if len(missing_elements) > 3:
            warnings.append({
                'field': 'subjective.hpi',
                'message': f'HPI missing key elements: {", ".join(missing_elements[:3])}',
                'severity': 'warning',
                'suggestion': 'Consider OLDCARTS mnemonic for complete history'
            })
            penalty += 10

        return {'errors': errors, 'warnings': warnings, 'penalty': penalty}

    def _validate_objective(self, objective: Dict[str, Any]) -> Dict[str, Any]:
        """Validate objective section"""
        errors = []
        warnings = []
        penalty = 0

        vitals = objective.get('vitalSigns', {})

        # Check for abnormal vitals not addressed
        abnormal_vitals = []

        temp = vitals.get('temperature', 37.0)
        if temp < 36.0 or temp > 38.0:
            abnormal_vitals.append(f'Temperature {temp}°C')

        hr = vitals.get('heartRate', 75)
        if hr < 60 or hr > 100:
            abnormal_vitals.append(f'Heart rate {hr} bpm')

        if abnormal_vitals:
            warnings.append({
                'field': 'objective',
                'message': f'Abnormal vitals noted: {", ".join(abnormal_vitals)}',
                'severity': 'info',
                'suggestion': 'Ensure abnormal findings are addressed in assessment'
            })

        return {'errors': errors, 'warnings': warnings, 'penalty': penalty}

    def _validate_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Validate assessment section"""
        errors = []
        warnings = []
        penalty = 0

        reasoning = assessment.get('clinicalReasoning', '')

        # Check for differential diagnosis
        if 'differential' not in reasoning.lower():
            warnings.append({
                'field': 'assessment.clinicalReasoning',
                'message': 'No differential diagnosis documented',
                'severity': 'warning',
                'suggestion': 'Document alternative diagnoses considered'
            })
            penalty += 15

        return {'errors': errors, 'warnings': warnings, 'penalty': penalty}

    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate plan section"""
        errors = []
        warnings = []
        penalty = 0

        follow_up = plan.get('followUp', '')

        # Check for safety-netting
        safetynetting = plan.get('safetynetting', '')
        if len(safetynetting) < 20:
            warnings.append({
                'field': 'plan.safetynetting',
                'message': 'Inadequate safety-netting advice',
                'severity': 'warning',
                'suggestion': 'Include red flags and when to re-present'
            })
            penalty += 10

        return {'errors': errors, 'warnings': warnings, 'penalty': penalty}

    def _calculate_completeness(self, soap_note: Dict[str, Any]) -> float:
        """Calculate overall completeness percentage"""
        required_fields = [
            'subjective.chiefComplaint',
            'subjective.hpi',
            'objective.vitalSigns',
            'objective.generalAppearance',
            'assessment.primaryDiagnosis',
            'assessment.clinicalReasoning',
            'plan.followUp'
        ]

        completed = 0
        for field_path in required_fields:
            parts = field_path.split('.')
            value = soap_note

            for part in parts:
                value = value.get(part, {})

            if value and (isinstance(value, str) and len(value) > 0 or isinstance(value, dict)):
                completed += 1

        return (completed / len(required_fields)) * 100
```

---

### 4. Validation API Endpoint (2 hours)

**File**: `/home/dev/Development/irStudy/backend/src/api/v1/validation.py`

```python
"""
Validation API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from src.validators.pbs_validator import PBSValidator, MOCK_PBS_DATABASE
from src.validators.mbs_validator import MBSValidator, MOCK_MBS_DATABASE
from src.validators.documentation_validator import DocumentationValidator


router = APIRouter(prefix='/api/v1/validation', tags=['validation'])

# Initialize validators
pbs_validator = PBSValidator(MOCK_PBS_DATABASE)
mbs_validator = MBSValidator(MOCK_MBS_DATABASE)
doc_validator = DocumentationValidator()


class ValidationRequest(BaseModel):
    """Validation request"""
    type: str  # 'soap', 'prescription', 'pathology'
    data: Dict[str, Any]
    layers: List[str] = ['python']  # ['client', 'python', 'ai']


class ValidationResponse(BaseModel):
    """Validation response"""
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    suggestions: List[str]
    score: Optional[float] = None


@router.post('/validate', response_model=ValidationResponse)
async def validate_data(request: ValidationRequest):
    """
    Validate data based on type

    Args:
        request: Validation request

    Returns:
        Validation result
    """
    if request.type == 'soap':
        result = doc_validator.validate_soap_note(request.data)
        return ValidationResponse(
            is_valid=result['is_valid'],
            errors=result['errors'],
            warnings=result['warnings'],
            suggestions=result.get('suggestions', []),
            score=result.get('documentation_score')
        )

    elif request.type == 'prescription':
        result = pbs_validator.validate_prescription(request.data)
        return ValidationResponse(
            is_valid=result['is_valid'],
            errors=result['errors'],
            warnings=result['warnings'],
            suggestions=result.get('suggestions', [])
        )

    elif request.type == 'pathology':
        result = mbs_validator.validate_pathology_order(request.data)
        return ValidationResponse(
            is_valid=result['is_valid'],
            errors=result['errors'],
            warnings=result['warnings'],
            suggestions=result.get('suggestions', [])
        )

    else:
        raise HTTPException(status_code=400, detail=f'Unknown validation type: {request.type}')


@router.post('/validate/batch')
async def validate_batch(request: ValidationRequest):
    """Validate batch of items"""
    if request.type == 'prescription':
        prescriptions = request.data.get('prescriptions', [])
        result = pbs_validator.validate_batch(prescriptions)
        return result

    elif request.type == 'pathology':
        orders = request.data.get('orders', [])
        result = mbs_validator.validate_batch(orders)
        return result

    else:
        raise HTTPException(status_code=400, detail='Batch validation only for prescriptions/pathology')
```

---

## Validation Checklist

Before marking this task complete, verify:

- [ ] PBS Validator:
  - [ ] Validates PBS codes
  - [ ] Checks quantity limits
  - [ ] Checks repeat limits
  - [ ] Validates authority requirements
  - [ ] Checks restriction criteria
  - [ ] Detects drug interactions
- [ ] MBS Validator:
  - [ ] Validates MBS codes
  - [ ] Checks clinical indication adequacy
  - [ ] Enforces frequency rules
  - [ ] Validates provider numbers
  - [ ] Detects duplicate tests
  - [ ] Flags inappropriate combinations
- [ ] Documentation Validator:
  - [ ] Checks SOAP completeness
  - [ ] Validates key elements (OLDCARTS)
  - [ ] Checks differential diagnosis
  - [ ] Validates safety-netting
  - [ ] Calculates documentation score
- [ ] API endpoints work correctly
- [ ] All validators return consistent error format
- [ ] No Python errors
- [ ] Type hints correct
- [ ] Tests pass (if created)

---

## Time Breakdown

- PBS Prescription Validator: 3 hours
- MBS Pathology Validator: 3 hours
- Clinical Documentation Validator: 2 hours
- Validation API Endpoints: 2 hours
- **Total**: 10 hours

---

## Next Steps

After completing this task:
1. Proceed to **TASK_2.3_AI_VALIDATION.md** (Claude AI validation - Layer 3)

---

**Last Updated**: 2026-02-03
**Status**: Ready for Implementation
