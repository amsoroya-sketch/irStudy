# TASK 2.2: Rule-Based Validation - PBS/MBS Validators (Layer 2)

**Phase**: Phase 2 - Validation Architecture
**Estimated Hours**: 10 hours
**Dependencies**: TASK_2.1 Complete (Zod schemas created), Python 3.11+, FastAPI environment
**Agent Type**: `python-clinical-expert`
**Status**: ⏳ Not Started

---

## Overview

Implement comprehensive rule-based validation layer using Python to enforce Australian pharmaceutical and clinical safety regulations. This layer validates business logic, drug interactions, contraindications, clinical safety rules, and PBS/MBS compliance that cannot be checked on the client side. Acts as the second line of defense with <1 second response times, using mock databases for 20+ medications and 15+ pathology tests.

---

## Deliverables

### Core Validator Modules

#### 1. `/backend/src/validators/pbs_validator.py` (220+ lines)
- **Class: PBSValidator**
  - `validate_medication_code(code: str) -> ValidationResult`
    - Format check: \d{4}[A-Z] (e.g., "1234A")
    - Checksum validation if applicable
    - Authority requirement check
    - Lifetime supply limit check
    - Return: code_valid (bool), requires_authority (bool), restrictions (list)

  - `validate_quantity(medication_code: str, quantity: int, patient_age: int) -> ValidationResult`
    - PBS quantity limits: depends on medication (insulin 100 units/day max typical)
    - Age-based quantity adjustments (pediatric, elderly)
    - Total cost check against patient co-payment limits
    - Warn if quantity >100 (user education)
    - Return: quantity_valid (bool), warnings (list), suggested_quantity (int)

  - `validate_repeats(medication_code: str, repeats: int) -> ValidationResult`
    - PBS maximum: 5 repeats per prescription (hard rule)
    - Authority-required medications: 0 repeats maximum
    - Some medications (contraceptives): allow unlimited repeats if S3
    - Warn if patient age <18 and quantity unusual
    - Return: repeats_valid (bool), max_allowed (int), warnings (list)

  - `check_drug_interaction(medication1: str, medication2: str, other_meds: List[str]) -> InteractionResult`
    - Critical interactions: CONTRAINDICATED
      - Warfarin + Aspirin → bleeding risk
      - Warfarin + NSAIDs → bleeding risk
      - MAOI + SSRIs → serotonin syndrome
      - ACE inhibitors + Potassium → hyperkalemia
      - Metformin + Contrast dye → renal failure
    - Moderate interactions: REQUIRES MONITORING
      - Warfarin + Amiodarone → increased INR
      - Beta blockers + Verapamil → heart block
      - Statins + Gemfibrozil → myopathy
    - Minor interactions: INFO ONLY
      - Aspirin + Caffeine
      - Levothyroxine + Iron (separate by 4 hours)
    - Return: severity (critical/moderate/minor), description, management

  - `check_allergy_conflict(medication_code: str, patient_allergies: List[str]) -> AllergyResult`
    - Exact match check: "Penicillin allergy" + Amoxicillin → conflict
    - Cross-reactivity check: "Penicillin allergy" + Cephalexin → possible cross-reactivity (5-10% risk)
    - Document severity of original allergy (rash vs. anaphylaxis)
    - Suggest alternatives if available
    - Return: has_conflict (bool), severity (mild/moderate/severe), alternatives (list)

  - `validate_prescriber_authority(prescriber_id: str, medication_code: str, patient_type: str) -> AuthorityResult`
    - Authority-required medications: prescriber must have number/code
    - Restricted prescriber classes: only specialists can prescribe (e.g., biologics)
    - Patient type restrictions: PBS item 1234 only for age >65
    - Return: authorized (bool), requirements (list), documentation_needed (bool)

- **Database Method: `load_pbs_database() -> Dict`**
  - Load from mock JSON file with 20+ medications
  - Each entry: code, name, strength, formulation, quantity_limit, repeats_max, authority_required, interactions, contraindications
  - Cache in memory for performance

#### 2. `/backend/src/validators/mbs_validator.py` (200+ lines)
- **Class: MBSValidator**
  - `validate_item_number(item_code: int) -> ValidationResult`
    - Format: exactly 5 digits (00001-99999)
    - Check against MBS database (sample of 100+ items)
    - Validate item status (active/inactive/superseded)
    - Return: valid (bool), item_name (str), description (str), restrictions (list)

  - `validate_frequency_limits(item_code: int, frequency: str, patient_age: int) -> ValidationResult`
    - Lipid panel: once per 12 months (warn if <12mo since last)
    - Blood pressure monitoring: variable by condition
    - Pathology tests: some can be weekly, some monthly
    - Pediatric pathology: age-adjusted frequency
    - Return: appropriate (bool), next_available_date (date), recommendations (str)

  - `validate_fasting_requirements(item_code: int, collection_time: str, fasting_status: bool) -> FastingResult`
    - Lipid panel: REQUIRES 9-12 hour fasting
    - UEC: fasting not required but preferred
    - Glucose: fasting required for diagnostic testing
    - Triglycerides: REQUIRES 12 hour fasting (eating raises triglycerides)
    - Liver function: no fasting required
    - Warn if fasting not done when required (affects interpretation)
    - Return: fasting_required (bool), reason (str), warning_if_not_fasted (str)

  - `validate_specimen_type(item_code: int, specimen: str) -> SpecimenResult`
    - Some tests require specific specimens:
      - Hemoglobin A1C: EDTA tube (purple top)
      - Coagulation: Citrate tube (blue top)
      - Blood culture: sterile bottles
      - Urine pregnancy: first morning urine or 2-hour specimen
    - Return: appropriate (bool), specimen_required (str), alternative_acceptable (bool)

  - `validate_clinician_indication(item_code: int, indication: str) -> IndicationResult`
    - Some MBS items require clinical justification
    - Indication must be ≥20 chars and relevant to test
    - Cross-check against common indications in database
    - Return: acceptable (bool), suggestions (list)

- **Database Method: `load_mbs_database() -> Dict`**
  - Sample of 100+ common MBS items
  - Each entry: code, name, cost, frequency_limit, fasting_requirement, specimen_type, requirements

#### 3. `/backend/src/validators/clinical_safety_validator.py` (180+ lines)
- **Class: ClinicalSafetyValidator**
  - `detect_red_flags(soap_note: SOAPNote) -> List[RedFlag]`
    - RED FLAGS (immediate action required):
      - Chest pain + cardiac risk factors → Rule out ACS, ECG needed
      - Sudden weakness/speech changes → Rule out stroke, ACTIVATE CODE STROKE
      - Severe headache + fever + neck stiffness → Meningitis, ACTIVATE CODE SEPSIS
      - Anaphylaxis presentation → ACTIVATE ANAPHYLAXIS PROTOCOL
      - Suicidal ideation with plan/intent → ACTIVATE SUICIDE PREVENTION
      - Seizure activity in young children → Rule out febrile convulsion vs. epilepsy
      - Severe hypoglycemia (<2.8 mmol/L) → Risk of seizure/coma

    - ORANGE FLAGS (urgent review within hours):
      - Severe dehydration with diarrhea in children
      - Severe asthma exacerbation (PEF <50%)
      - Acute abdomen with peritoneal signs
      - Sepsis (fever + SIRS criteria: HR>90, RR>20, WBC abnormal)
      - Acute coronary syndrome risk

    - YELLOW FLAGS (requires review before discharge):
      - Hypertension stage 2 (≥160/100)
      - Diabetic with BGL >20 mmol/L
      - New onset atrial fibrillation

  - Red flag detection logic:
    - Parse chief complaint and HPI for keywords
    - Cross-reference with vital signs (BP, HR, temp, RR)
    - Check examination findings
    - Flag combinations that suggest serious pathology
    - Return: flags (list), severity (RED/ORANGE/YELLOW), required_actions (list)

  - `validate_soap_completeness(soap_note: SOAPNote) -> CompletenessResult`
    - Subjective: includes HPI, PMH, current meds, allergies, social history
    - Objective: includes vitals, systems examination, investigations
    - Assessment: includes diagnosis (ICD-10), differential, reasoning
    - Plan: includes investigations, prescriptions, referrals, follow-up
    - Return: completeness_percentage (0-100), missing_components (list)

  - `validate_assessment_quality(assessment: str, diagnosis: str, differentials: List[str]) -> AssessmentQuality`
    - Diagnosis must be ICD-10 code format
    - Differential diagnosis should include 2-5 options
    - Clinical reasoning >50 chars and coherent
    - Reasoning should link findings to diagnosis
    - Return: quality_score (0-100), issues (list), suggestions (list)

  - `validate_plan_safety(plan: PlanSection, assessment: Assessment) -> PlanSafety`
    - Investigations should be ordered based on assessment
    - Prescriptions should match diagnosis
    - Refer to appropriate specialty for diagnosis
    - Follow-up timeframe appropriate for condition
    - Safety-net advice present and appropriate
    - Return: safety_score (0-100), concerns (list)

#### 4. `/backend/src/validators/prescription_validator.py` (100+ lines)
- **Class: PrescriptionValidator**
  - Orchestrates: PBSValidator + allergy checks + drug interactions
  - `validate_prescription(prescription: Prescription, patient: Patient) -> ValidationResult`
    - Calls: PBS validation, allergy check, interaction check, prescriber authority
    - Aggregates errors/warnings with severity levels
    - Return: overall_valid (bool), errors (list), warnings (list), requires_review (bool)

  - `validate_prescription_batch(prescriptions: List[Prescription], patient: Patient) -> BatchResult`
    - Check each prescription individually
    - Check interactions between all prescriptions
    - Check duplicate medications
    - Return: all_valid (bool), individual_results (list), interaction_results (list)

#### 5. `/backend/src/validators/pathology_validator.py` (80+ lines)
- **Class: PathologyValidator**
  - Orchestrates: MBSValidator + specimen/fasting validation
  - `validate_pathology_order(order: PathologyOrder, patient: Patient) -> ValidationResult`
    - Calls: MBS validation, specimen type check, fasting requirement check, indication validation
    - Return: valid (bool), warnings (list), instructions (str)

  - `validate_pathology_batch(orders: List[PathologyOrder], patient: Patient) -> BatchResult`
    - Check each order individually
    - Check for duplicate tests (same MBS item)
    - Check for conflicting specimen types (can't do hematology + microbiology in same tube)
    - Return: all_valid (bool), results (list)

### Mock Database Files

#### 6. `/backend/src/validators/mock_databases/pbs_medications.json` (400+ lines)
```json
{
  "medications": [
    {
      "code": "0001A",
      "name": "Paracetamol",
      "strength": "500mg",
      "formulation": "tablet",
      "quantity_limit": 1000,
      "repeats_max": 5,
      "authority_required": false,
      "restricted_age": null,
      "interactions": [
        {
          "with_medication": "Warfarin",
          "severity": "minor",
          "description": "Slight increase in INR possible"
        }
      ],
      "contraindications": [
        "Severe liver disease",
        "Acetaminophen allergy"
      ],
      "pbs_status": "active",
      "last_updated": "2025-01-01"
    },
    // ... 19+ more medications
  ]
}
```

**Medications to Include (20+ examples):**
- Paracetamol (acetaminophen equivalent) - 0001A
- Ibuprofen - 0002B
- Aspirin - 0003C
- Amoxicillin - 0100D
- Cephalexin - 0101E
- Warfarin - 0250F
- Metoprolol - 0300G
- Lisinopril - 0301H
- Amlodipine - 0302I
- Simvastatin - 0400J
- Atorvastatin - 0401K
- Metformin - 0500L
- Insulin (various types) - 0501M
- Levothyroxine - 0600N
- Amitriptyline - 0700O
- Sertraline (SSRI) - 0701P
- Salbutamol inhaler - 0800Q
- Omeprazole - 0900R
- Ranitidine - 0901S
- Prednisone - 1000T
- Phenytoin - 1100U

#### 7. `/backend/src/validators/mock_databases/mbs_tests.json` (300+ lines)
```json
{
  "tests": [
    {
      "code": "66589",
      "name": "Full Blood Count",
      "category": "Hematology",
      "cost": 25.50,
      "frequency_limit": "unrestricted",
      "fasting_required": false,
      "specimen_type": "EDTA tube",
      "clinical_indications": [
        "Anemia",
        "Infection",
        "Malignancy",
        "General checkup"
      ],
      "restrictions": "None"
    },
    // ... 14+ more tests
  ]
}
```

**Tests to Include (15+ examples):**
- FBC (Full Blood Count) - 66589 - Hematology - No fasting
- UEC (Urea, Electrolytes, Creatinine) - 66590 - Chemistry - No fasting required, preferred
- LFT (Liver Function Tests) - 66591 - Chemistry - No fasting
- Lipid Panel - 66592 - Chemistry - FASTING REQUIRED 9-12 hours
- Coagulation Screen - 66593 - Hematology - No fasting
- Thyroid Function Tests - 66594 - Endocrinology - No fasting
- Blood Glucose - 66595 - Biochemistry - Fasting required for diagnostic
- Hemoglobin A1C - 66596 - Biochemistry - No fasting
- PSA (Prostate) - 66597 - Oncology - No fasting (males >40)
- CA 19-9 (Cancer marker) - 66598 - Oncology - No fasting
- Blood Culture - 66599 - Microbiology - Sterile collection
- Urine Culture - 66600 - Microbiology - Midstream clean-catch
- Pregnancy Test (hCG) - 66601 - Biochemistry - No fasting
- Troponin (cardiac) - 66602 - Cardiology - No fasting (urgent)
- D-Dimer (thromboembolism) - 66603 - Hematology - No fasting

#### 8. `/backend/src/validators/mock_databases/drug_interactions.json` (150+ lines)
```json
{
  "critical_interactions": [
    {
      "drug1": "Warfarin",
      "drug2": "Aspirin",
      "mechanism": "Both inhibit platelet function and coagulation",
      "effect": "Increased bleeding risk",
      "management": "AVOID combination if possible. If necessary, monitor INR closely (weekly). Patient education on bleeding signs"
    },
    {
      "drug1": "Warfarin",
      "drug2": "NSAIDs",
      "mechanism": "NSAIDs inhibit platelet and increase warfarin levels",
      "effect": "Significantly increased bleeding risk",
      "management": "CONTRAINDICATED. Use acetaminophen instead for pain"
    },
    {
      "drug1": "MAOI",
      "drug2": "SSRI",
      "mechanism": "Both increase serotonin",
      "effect": "Serotonin syndrome (confusion, agitation, tremor, hyperthermia)",
      "management": "CONTRAINDICATED. Washout period required between drugs (2-5 weeks depending on SSRI)"
    },
    {
      "drug1": "ACE inhibitor",
      "drug2": "Potassium supplement",
      "mechanism": "Both increase potassium retention",
      "effect": "Hyperkalemia (dangerous cardiac arrhythmias)",
      "management": "Monitor potassium levels. Educate patient on potassium-rich diet avoidance"
    },
    {
      "drug1": "Metformin",
      "drug2": "Contrast dye",
      "mechanism": "Contrast dye impairs renal function, metformin accumulates",
      "effect": "Lactic acidosis (fatal)",
      "management": "Hold metformin 48 hours before and 48 hours after contrast. Renal function check"
    }
    // ... more interactions
  ],
  "moderate_interactions": [
    // Similar structure
  ]
}
```

### Utility & Helper Files

#### 9. `/backend/src/validators/validation_result.py` (60+ lines)
```python
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class ValidationIssue:
    field: str
    message: str
    severity: SeverityLevel
    suggestion: Optional[str]
    affected_items: Optional[List[str]]  # For batch operations

@dataclass
class ValidationResult:
    success: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
    validation_time_ms: float
    data: Optional[Dict[str, Any]] = None

    def has_critical_errors(self) -> bool:
        return any(e.severity == SeverityLevel.CRITICAL for e in self.errors)

    def error_count(self) -> int:
        return len(self.errors)

    def warning_count(self) -> int:
        return len(self.warnings)
```

#### 10. `/backend/src/validators/__init__.py` (30+ lines)
- Export all validators
- Validator factory function
- Load all mock databases on startup

### Testing Files

#### 11. `/backend/tests/validators/test_pbs_validator.py` (200+ lines)
- **Test Cases:**
  - test_valid_pbs_code_formats: 10+ valid codes
  - test_invalid_pbs_code_formats: 10+ invalid codes
  - test_quantity_limits: valid/invalid quantities
  - test_repeats_max_5: enforce 5 repeat maximum
  - test_drug_interactions_warfarin_aspirin: critical
  - test_drug_interactions_acei_potassium: critical
  - test_allergy_conflict_penicillin: exact match
  - test_allergy_cross_reactivity: penicillin-cephalosporin
  - test_prescriber_authority: authority requirements
  - Coverage: ≥70%

#### 12. `/backend/tests/validators/test_mbs_validator.py` (150+ lines)
- **Test Cases:**
  - test_valid_mbs_item_numbers: 5-digit format
  - test_frequency_lipid_limits: once per 12 months
  - test_fasting_lipid_required: must be marked fasting
  - test_fasting_uec_preferred: warning if not fasting
  - test_specimen_types: appropriate specimens
  - test_indication_validation: >20 chars, relevant
  - Coverage: ≥70%

#### 13. `/backend/tests/validators/test_clinical_safety_validator.py` (180+ lines)
- **Test Cases:**
  - test_red_flag_chest_pain_acs: detect ACS risk
  - test_red_flag_neuro_stroke: detect stroke signs
  - test_red_flag_sepsis_sirs: detect sepsis criteria
  - test_red_flag_anaphylaxis: detect anaphylaxis
  - test_red_flag_suicidal_ideation: detect suicide risk
  - test_orange_flag_dehydration_children: detect urgent conditions
  - test_soap_completeness: all 4 sections present
  - test_assessment_quality: ICD-10, differential, reasoning
  - test_plan_safety: investigations/prescriptions appropriate
  - Coverage: ≥70%

#### 14. `/backend/tests/validators/conftest.py` (50+ lines)
- Fixtures for mock databases
- Sample patient objects
- Sample SOAP notes, prescriptions, pathology orders
- Mock database context manager

---

## Detailed Requirements

### Requirement 1: <1 Second Response Time

**Specification:**
All Layer 2 validations must complete in <1 second, including database lookups and multiple validation checks.

**Performance Breakdown (target budget):**
- PBS validation: 100-200ms
- MBS validation: 50-100ms
- Drug interaction check: 150-250ms
- Clinical safety check: 100-200ms
- Allergy check: 50-100ms
- Total: <1000ms

**Implementation Strategy:**
- Load mock databases into memory on startup (not from file each request)
- Use hash tables for O(1) lookups
- Cache validation results for identical inputs
- Parallel processing if multiple validations (Python async)
- Return immediately if critical error found (skip remaining checks)

**Acceptance Criteria:**
- [ ] All validations complete in <1 second
- [ ] Mock databases cached in memory
- [ ] Performance benchmarks documented
- [ ] No timeout errors in test suite

### Requirement 2: Drug Interaction Matrix (15+ Critical Interactions)

**Specification:**
Identify and prevent dangerous drug combinations with clinical reasoning for each.

**Critical Interactions to Implement (minimum 15):**

1. **Warfarin + Aspirin** → Bleeding risk (both anticoagulant/antiplatelet)
2. **Warfarin + NSAIDs** → Severe bleeding risk
3. **MAOI + SSRI** → Serotonin syndrome
4. **ACE Inhibitor + Potassium supplement** → Hyperkalemia
5. **Metformin + Contrast dye** → Lactic acidosis
6. **Statins + Gemfibrozil** → Myopathy/rhabdomyolysis
7. **Beta blocker + Verapamil** → Heart block
8. **Quinolone + Theophylline** → Theophylline toxicity
9. **Lithium + NSAID** → Lithium toxicity
10. **ACE inhibitor + Spironolactone** → Hyperkalemia
11. **Methotrexate + NSAIDs** → Renal toxicity
12. **Finasteride + Dutasteride** → Duplicate therapy (not additive)
13. **Tramadol + SSRI** → Serotonin syndrome
14. **Levothyroxine + Iron supplement** → Reduced absorption
15. **Grapefruit juice + Statins** → Statin levels increase

**Acceptance Criteria:**
- [ ] 15+ critical interactions implemented
- [ ] Each interaction has severity level (critical/moderate/minor)
- [ ] Each interaction has clinical description and management
- [ ] All interactions tested with positive and negative cases
- [ ] Drug interaction database covers interactions from sample medications

### Requirement 3: Clinical Red Flags (≥10 Patterns)

**Specification:**
Detect dangerous clinical presentations requiring immediate action.

**Red Flags to Implement (minimum 10):**

1. **Chest Pain + Risk Factors** → Rule out ACS
   - "chest pain" OR "chest discomfort" OR "pressure" in HPI
   - Plus: age >40, smoker, hypertension, high cholesterol, diabetic
   - Action: ECG immediately, troponin, chest X-ray

2. **Sudden Neurological Deficit** → Rule out stroke
   - "sudden weakness" OR "speech changes" OR "facial droop" OR "sudden onset"
   - Action: ACTIVATE CODE STROKE, CT/MRI, neurology consult

3. **Fever + Neck Stiffness + Headache** → Meningitis
   - All 3 present
   - Action: ACTIVATE SEPSIS PROTOCOL, blood cultures, LP

4. **SIRS Criteria (2+ present)** → Potential sepsis
   - HR >90, RR >20, Temp >38°C, WBC abnormal
   - Action: Blood cultures, antibiotics, close monitoring

5. **Anaphylaxis Signs** → Life-threatening
   - Sudden onset + stridor/wheeze + hypotension + urticaria
   - Action: EPINEPHRINE IM immediately, airway assessment

6. **Suicidal Ideation + Plan/Intent** → Immediate risk
   - "suicidal thoughts" OR "wants to die" with "how" + "when"
   - Action: ACTIVATE SUICIDE PREVENTION, psychiatric emergency

7. **Severe Hypoglycemia** → Risk of seizure/coma
   - BGL <2.8 mmol/L
   - Action: Dextrose IV, frequent monitoring, endocrine consult

8. **Acute Abdomen + Peritoneal Signs** → Surgical emergency
   - Severe pain + guarding + rebound + fever
   - Action: Surgical consult, CT abdomen, IV fluids, NPO

9. **Status Epilepticus** → Life-threatening
   - Seizure >5 minutes OR multiple seizures without consciousness
   - Action: ACTIVATE SEIZURE PROTOCOL, benzodiazepines, airway management

10. **Severe Asthma (Life-threatening)** → Respiratory emergency
    - Peak flow <50%, stridor at rest, unable to speak in sentences
    - Action: HIGH-FLOW OXYGEN, salbutamol nebulized, steroids, ICU consideration

**Acceptance Criteria:**
- [ ] 10+ red flags implemented
- [ ] Red flag detection uses both keyword matching and vital signs
- [ ] Each red flag has associated action items
- [ ] All red flags tested with positive and negative cases
- [ ] Documentation of clinical reasoning for each flag

### Requirement 4: ≥70% Test Coverage

**Specification:**
Comprehensive testing of all validators with minimum 70% code coverage. Tests must cover normal cases, edge cases, and error conditions.

**Test Distribution:**
- PBS Validator: 40+ tests
- MBS Validator: 35+ tests
- Clinical Safety: 45+ tests
- Prescription/Pathology: 30+ tests
- Total: ≥150 tests

**Acceptance Criteria:**
- [ ] Coverage ≥70% measured with pytest-cov
- [ ] All public methods have test cases
- [ ] Edge cases tested (empty strings, null values, boundary values)
- [ ] Error conditions tested (invalid codes, missing data)
- [ ] Integration tests for validator combinations

### Requirement 5: Australian Medication & Compliance Standards

**Specification:**
All validators enforce Australian pharmaceutical standards per TGA, PBS, and AMC guidelines.

**Enforcement Points:**
- PBS codes match TGA format (\d{4}[A-Z])
- MBS items match actual Medicare Benefits Schedule format
- Medication interactions reflect TGA contraindication database
- Quantity limits align with PBS and TGA restrictions
- Australian terminology in error messages
- Age/renal function adjustments per Australian clinical guidelines

**Acceptance Criteria:**
- [ ] All PBS codes follow Australian format
- [ ] All MBS items valid format and realistic
- [ ] Interaction database based on TGA/ADA recommendations
- [ ] Error messages use Australian medical terminology
- [ ] Documentation cites TGA/PBS sources

---

## Acceptance Criteria

### Functionality
- [ ] PBSValidator with 6+ methods implemented and functional
- [ ] MBSValidator with 5+ methods implemented and functional
- [ ] ClinicalSafetyValidator detects ≥10 red flags
- [ ] PrescriptionValidator orchestrates PBS + allergy + interaction checks
- [ ] PathologyValidator orchestrates MBS + specimen + fasting checks
- [ ] Drug interaction matrix: ≥15 interactions implemented
- [ ] All validators return standardized ValidationResult objects
- [ ] All methods handle null/missing data gracefully

### Performance
- [ ] All validations <1 second per request
- [ ] Mock databases cached in memory
- [ ] No file I/O during validation
- [ ] Performance benchmarks run and documented
- [ ] Timeout handling implemented

### Testing
- [ ] ≥150 test cases written
- [ ] ≥70% code coverage (pytest-cov)
- [ ] All edge cases covered
- [ ] All error conditions covered
- [ ] Drug interaction tests: ≥15 critical interactions tested
- [ ] Red flag detection tests: ≥10 flags tested with positive/negative cases

### Code Quality
- [ ] Zero errors on `pytest` run
- [ ] Zero warnings on `pylint` (target)
- [ ] All code follows PEP 8 style guide
- [ ] Comprehensive docstrings on all methods
- [ ] Type hints on all function signatures
- [ ] Error messages clear and actionable

### Integration
- [ ] All validators importable from backend API
- [ ] ValidationResult type compatible with Zod schemas from Layer 1
- [ ] Can receive JSON data from client validation
- [ ] Returns JSON-serializable ValidationResult
- [ ] Ready for Layer 3 (Claude AI) to consume

### Australian Compliance
- [ ] PBS codes follow TGA format
- [ ] MBS items match actual schedule
- [ ] Interactions based on TGA database
- [ ] Error messages use Australian terminology
- [ ] Documentation cites authoritative sources

---

## Testing Requirements

### Unit Tests

```python
def test_pbs_code_validation():
    """Test PBS code format validation."""
    validator = PBSValidator()

    # Valid codes
    assert validator.validate_medication_code("1234A").valid
    assert validator.validate_medication_code("0001Z").valid

    # Invalid codes
    assert not validator.validate_medication_code("123A").valid
    assert not validator.validate_medication_code("1234a").valid
    assert not validator.validate_medication_code("1234").valid

def test_drug_interaction_warfarin_aspirin():
    """Test critical drug interaction detection."""
    validator = PBSValidator()
    result = validator.check_drug_interaction("Warfarin", "Aspirin", [])

    assert result.severity == "critical"
    assert "bleeding" in result.description.lower()
    assert len(result.management) > 0

def test_red_flag_chest_pain():
    """Test ACS red flag detection."""
    validator = ClinicalSafetyValidator()

    soap_note = {
        "subjective": {"chief_complaint": "Chest pain", ...},
        "objective": {"vitals": {"bp": "160/90", "hr": 110}},
        ...
    }

    flags = validator.detect_red_flags(soap_note)
    assert any(f.type == "ACS" for f in flags)
```

### Integration Tests
```python
def test_prescription_validation_with_interactions():
    """Test end-to-end prescription validation."""
    validator = PrescriptionValidator()

    patient = Patient(allergies=["Penicillin"])
    prescription = Prescription(
        medication="Warfarin",
        dose="5mg",
        current_meds=["Aspirin"]
    )

    result = validator.validate_prescription(prescription, patient)
    assert not result.success
    assert any("interaction" in w.message.lower() for w in result.warnings)
```

### Performance Tests
```python
import time

def test_validation_performance_under_1_second():
    """Ensure all validations complete <1 second."""
    validator = PrescriptionValidator()

    prescriptions = [generate_prescription() for _ in range(10)]
    patient = generate_patient()

    start = time.time()
    result = validator.validate_prescription_batch(prescriptions, patient)
    duration = time.time() - start

    assert duration < 1.0  # 1 second max
```

---

## Reference PRD Sections

### Backend API PRD
**Section**: Layer 2: Rule-Based Validation (Python)
**Link**: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md`

### Validation Rules
**Link**: `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md`
**Sections**:
- Layer 2: Rule-Based Validation (Python)
- Drug Interaction Matrix
- Clinical Red Flags

---

## Agent OS Delegation Prompt

```markdown
## TASK: Implement Rule-Based Validation Layer (Python PBS/MBS Validators)

### Context
You are implementing Layer 2 of a 3-layer validation architecture for an EMR practice system. This layer must:
1. Validate PBS/MBS compliance for Australian prescriptions and pathology orders
2. Enforce drug interactions, contraindications, and clinical safety rules
3. Detect clinical red flags requiring immediate action
4. Complete all validations in <1 second
5. Use mock databases (20+ medications, 15+ tests)
6. Achieve ≥70% test coverage
7. Follow Australian TGA and PBS standards

### Pre-Implementation Checklist
- [ ] Read PROJECT_CONSTRAINTS.md (esp. Australian medical accuracy section)
- [ ] Review `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md`
- [ ] Study TASK_2.1 Zod schemas to understand data structures
- [ ] Review mock database structure (PBS codes, MBS items)
- [ ] Check Layer 3 (Claude AI) requirements to ensure compatibility

### Deliverables

1. **Core Validator Modules (5 files, 700+ lines)**
   - `/backend/src/validators/pbs_validator.py` (220+ lines)
     - validate_medication_code(code): Check PBS format \d{4}[A-Z]
     - validate_quantity(code, qty, age): Check PBS quantity limits
     - validate_repeats(code, repeats): Enforce max 5 repeats
     - check_drug_interaction(med1, med2, other): Return severity/management
     - check_allergy_conflict(code, allergies): Cross-reactivity check
     - validate_prescriber_authority(prescriber, code, patient_type): Authority check

   - `/backend/src/validators/mbs_validator.py` (200+ lines)
     - validate_item_number(item): Exactly 5 digits (00001-99999)
     - validate_frequency_limits(item, frequency, age): Repeat frequency rules
     - validate_fasting_requirements(item, time, fasting_status): Lipid fasting required
     - validate_specimen_type(item, specimen): Appropriate collection type
     - validate_clinician_indication(item, indication): ≥20 chars, relevant

   - `/backend/src/validators/clinical_safety_validator.py` (180+ lines)
     - detect_red_flags(soap_note): Detect ≥10 RED/ORANGE/YELLOW flags
       - RED: Chest pain→ACS, Neuro→STROKE, Fever+Meningeal→SEPSIS, Anaphylaxis, Suicide, Status epilepticus, Severe asthma
       - ORANGE: Severe dehydration, Asthma exacerbation, Acute abdomen, Sepsis criteria, ACS risk
       - YELLOW: HTN stage 2, Severe hyperglycemia, New AFib
     - validate_soap_completeness(soap): Check S/O/A/P all present
     - validate_assessment_quality(assessment, diagnosis, differentials): ICD-10 + reasoning
     - validate_plan_safety(plan, assessment): Investigations/prescriptions/referrals appropriate

   - `/backend/src/validators/prescription_validator.py` (100+ lines)
     - Orchestrates: PBSValidator + allergy + interaction checks
     - validate_prescription(prescription, patient): All checks in sequence
     - validate_prescription_batch(prescriptions, patient): Check interactions between all

   - `/backend/src/validators/pathology_validator.py` (80+ lines)
     - Orchestrates: MBSValidator + specimen + fasting validation
     - validate_pathology_order(order, patient): All checks in sequence

2. **Mock Databases (3 files, 850+ lines)**
   - `/backend/src/validators/mock_databases/pbs_medications.json`
     - 20+ medications with code, strength, quantity_limit, repeats_max, interactions, contraindications
     - INCLUDE: Paracetamol, Ibuprofen, Aspirin, Amoxicillin, Cephalexin, Warfarin, Metoprolol, Lisinopril, Amlodipine, Simvastatin, Atorvastatin, Metformin, Insulin, Levothyroxine, Amitriptyline, Sertraline, Salbutamol, Omeprazole, Ranitidine, Prednisone, Phenytoin

   - `/backend/src/validators/mock_databases/mbs_tests.json`
     - 15+ pathology tests with code, name, cost, frequency_limit, fasting_required, specimen_type, indications
     - INCLUDE: FBC, UEC, LFT, Lipid Panel, Coagulation, TFT, Glucose, HbA1C, PSA, CA19-9, Blood Culture, Urine Culture, Pregnancy Test, Troponin, D-Dimer

   - `/backend/src/validators/mock_databases/drug_interactions.json`
     - ≥15 critical interactions (Warfarin+Aspirin, MAOI+SSRI, ACEi+K, Metformin+Contrast, etc.)
     - MUST include mechanism, effect, management for each

3. **Utility & Result Classes (2 files)**
   - `/backend/src/validators/validation_result.py` (60+ lines)
     - ValidationResult dataclass: success, errors, warnings, info, validation_time_ms, data
     - ValidationIssue class: field, message, severity, suggestion
     - SeverityLevel enum: CRITICAL, WARNING, INFO

   - `/backend/src/validators/__init__.py` (30+ lines)
     - Export all validators
     - load_mock_databases() function
     - ValidatorFactory or singleton pattern for shared databases

4. **Tests (5 files, 500+ lines, ≥70% coverage)**
   - `/backend/tests/validators/test_pbs_validator.py` (200+ lines)
     - test_valid_pbs_code_formats: ≥5 valid codes
     - test_invalid_pbs_code_formats: ≥5 invalid formats
     - test_quantity_limits: valid/invalid ranges
     - test_repeats_max_5: enforce 5 repeat maximum
     - test_drug_interaction_warfarin_aspirin: critical interaction
     - test_drug_interaction_acei_potassium: critical interaction
     - test_allergy_conflict_penicillin: exact match
     - test_allergy_cross_reactivity: penicillin-cephalosporin 5-10%
     - test_prescriber_authority: authority requirements
     - Coverage: ≥70%

   - `/backend/tests/validators/test_mbs_validator.py` (150+ lines)
     - test_valid_mbs_item_format: exactly 5 digits
     - test_frequency_lipid_limits: once per 12 months
     - test_fasting_lipid_required: warn if no fasting marked
     - test_fasting_uec_preferred: info if not fasting
     - test_specimen_types: appropriate collection type
     - test_indication_validation: ≥20 chars

   - `/backend/tests/validators/test_clinical_safety_validator.py` (180+ lines)
     - test_red_flag_chest_pain: ACS risk detection
     - test_red_flag_neuro_stroke: STROKE code detection
     - test_red_flag_meningitis: Fever+neck stiffness detection
     - test_red_flag_sirs_sepsis: SIRS criteria detection
     - test_red_flag_anaphylaxis: Anaphylaxis detection
     - test_red_flag_suicide: Suicidal ideation with plan
     - test_orange_flag_dehydration: Urgent conditions
     - test_soap_completeness: S/O/A/P all present
     - test_assessment_quality: ICD-10 + 2-5 differentials + reasoning
     - test_plan_safety: Investigations/prescriptions/referrals appropriate

   - `/backend/tests/validators/test_prescription_validator.py` (100+ lines)
     - End-to-end tests combining PBS + interaction + allergy checks

   - `/backend/tests/validators/conftest.py` (50+ lines)
     - Fixtures for mock databases
     - Sample patient, SOAP note, prescription, pathology order fixtures
     - Mock database context manager

### Critical Constraints

1. **Performance**: ALL validations <1 second total
   - Load databases into memory at startup (not per request)
   - Use hash tables for O(1) lookups
   - Parallel processing for independent checks
   - Cache results for identical inputs (optional optimization)
   - Return immediately if critical error found

2. **Drug Interactions**: Implement ≥15 critical interactions
   - Warfarin + Aspirin, Warfarin + NSAIDs, MAOI + SSRI, ACEi + K+, Metformin + Contrast, Statins + Gemfibrozil, Beta blocker + Verapamil, Quinolone + Theophylline, Lithium + NSAID, ACEi + Spironolactone, Methotrexate + NSAID, Tramadol + SSRI, Levothyroxine + Iron, Grapefruit + Statins
   - Each with severity, mechanism, effect, management

3. **Clinical Red Flags**: Detect ≥10 RED/ORANGE/YELLOW flags
   - RED: Chest pain+ACS, Neuro deficit+STROKE, Fever+Meningeal+SEPSIS, Anaphylaxis, Suicide+plan, Status seizures, Severe asthma
   - ORANGE: Severe dehydration, Asthma exacerbation, Acute abdomen, Sepsis (SIRS)
   - YELLOW: HTN stage 2, Severe hyperglycemia, New AFib

4. **Australian Compliance**:
   - PBS codes: \d{4}[A-Z] format
   - MBS items: exactly 5 digits
   - Interactions from TGA database
   - Australian terminology in errors

5. **Test Coverage**: ≥70% measured with pytest-cov
   - ≥150 test cases total
   - All public methods tested
   - Edge cases and error conditions
   - Performance tests included

### Validation Checklist (Agent Must Complete Before Returning)

- [ ] All 5 validator modules created and functional
- [ ] PBSValidator: 6 methods working (code, qty, repeats, interaction, allergy, authority)
- [ ] MBSValidator: 5 methods working (item, frequency, fasting, specimen, indication)
- [ ] ClinicalSafetyValidator: ≥10 red flags detected with RED/ORANGE/YELLOW levels
- [ ] Drug interactions: ≥15 critical interactions with mechanism/effect/management
- [ ] Mock databases: 20+ meds, 15+ tests, interaction matrix loaded
- [ ] Databases cached in memory at startup
- [ ] All validators return ValidationResult with proper structure
- [ ] ≥150 test cases written and passing: pytest
- [ ] Coverage ≥70%: pytest --cov=src/validators --cov-report=term
- [ ] Performance <1 second: All validation benchmarks pass
- [ ] No timeout errors, proper error handling
- [ ] All code follows PEP 8: pylint (target)
- [ ] Type hints on all functions
- [ ] Docstrings on all public methods
- [ ] Error messages clear and actionable
- [ ] ValidationResult serializable to JSON
- [ ] Ready for Layer 3 (Claude API) integration

### Success Criteria (PM Will Validate)
- 0 pytest failures
- ≥70% code coverage
- <1 second response time for all validations
- ≥15 drug interactions implemented and tested
- ≥10 clinical red flags implemented and tested
- Proper Australian compliance (PBS/MBS formats)
- Ready for unified API endpoint (Layer 3)

### File Structure to Verify
```
backend/src/validators/
├── __init__.py
├── validation_result.py
├── pbs_validator.py
├── mbs_validator.py
├── clinical_safety_validator.py
├── prescription_validator.py
├── pathology_validator.py
└── mock_databases/
    ├── pbs_medications.json
    ├── mbs_tests.json
    └── drug_interactions.json

backend/tests/validators/
├── conftest.py
├── test_pbs_validator.py
├── test_mbs_validator.py
├── test_clinical_safety_validator.py
├── test_prescription_validator.py
└── test_pathology_validator.py
```

### Next Steps After Completion
- Layer 3 will integrate Claude API for clinical reasoning validation
- Unified API endpoint will orchestrate all 3 layers
- Frontend will consume validation results from Layer 3 endpoint

### Questions Before Starting?
Contact PM with clarifications on:
- Specific TGA/PBS interaction database to reference
- Weighting/priority for red flags in ranking
- Performance optimization strategies
- Mock database extension requirements
```

---

## Implementation Notes

### Architecture Decisions

1. **Stateful Validators with Cached Databases**
   - Load mock databases once at application startup
   - Store in class attributes or module-level singletons
   - Each validation method reads from cache (not file)
   - Fast lookups: O(1) for code lookups, O(n) for interaction checks

2. **Progressive Validation**
   - Run quick checks first (format validation)
   - Run expensive checks later (interaction matrix)
   - Return immediately on critical error

3. **Severity Levels for Prioritization**
   - CRITICAL: Block submission (invalid PBS code, contraindication)
   - WARNING: Require acknowledgment (quantity >100, missing data)
   - INFO: Informational only (rare medication)

4. **Batch Processing Support**
   - Methods for validating single items and lists
   - Check interactions between ALL items in batch
   - Aggregate results with clear reporting

### Common Pitfalls to Avoid

1. **Don't make synchronous I/O calls**
   - Load all data at startup, not per request
   - Use in-memory caches only

2. **Don't hardcode medication data**
   - Use JSON mock files for easy updates
   - Create extension mechanism for future database integration

3. **Don't skip red flag combinations**
   - Red flags often require multiple signs (fever + neck stiffness + headache)
   - Don't just match individual keywords

4. **Don't forget Australian context**
   - PBS format is specific to Australia
   - MBS is specific to Medicare (Australian)
   - Interaction database should reference TGA
   - Error messages use Australian spelling (colour, organisation)

### Testing Strategy

1. **Unit Tests First**
   - Test each validator method independently
   - Use fixtures for mock data

2. **Integration Tests**
   - Test validators together (prescription + interaction + allergy)
   - Test batch operations

3. **Performance Tests**
   - Benchmark each validator
   - Ensure total <1 second
   - Profile memory usage

4. **Edge Case Tests**
   - Empty strings, null values
   - Boundary values (quantity 999, repeats 5)
   - Invalid formats vs. valid-looking invalid data

---

## Progress Tracking

### Milestone 1: PBS Validator (3 hours)
- [ ] Create PBSValidator class
- [ ] Implement: code validation, quantity limits, repeats max
- [ ] Implement: drug interactions (≥10 critical)
- [ ] Implement: allergy conflict checking
- [ ] Load PBS mock database
- [ ] Write 40+ tests, ≥70% coverage

### Milestone 2: MBS Validator (2.5 hours)
- [ ] Create MBSValidator class
- [ ] Implement: item number validation
- [ ] Implement: frequency limits, fasting requirements
- [ ] Implement: specimen type validation
- [ ] Load MBS mock database
- [ ] Write 35+ tests, ≥70% coverage

### Milestone 3: Clinical Safety (2.5 hours)
- [ ] Create ClinicalSafetyValidator class
- [ ] Implement: ≥10 red flags (RED/ORANGE/YELLOW)
- [ ] Implement: SOAP completeness, assessment quality, plan safety
- [ ] Write 45+ tests, ≥70% coverage
- [ ] Document each red flag with clinical reasoning

### Milestone 4: Orchestration & Testing (2 hours)
- [ ] Create PrescriptionValidator orchestrator
- [ ] Create PathologyValidator orchestrator
- [ ] Create ValidationResult dataclass
- [ ] Write integration tests
- [ ] Performance benchmarking
- [ ] Achieve ≥70% overall coverage
- [ ] Document all validators

---

## Files to Create/Modify

### Create
```
/backend/src/validators/
  ├── __init__.py
  ├── validation_result.py
  ├── pbs_validator.py
  ├── mbs_validator.py
  ├── clinical_safety_validator.py
  ├── prescription_validator.py
  ├── pathology_validator.py
  └── mock_databases/
      ├── pbs_medications.json
      ├── mbs_tests.json
      └── drug_interactions.json

/backend/tests/validators/
  ├── conftest.py
  ├── test_pbs_validator.py
  ├── test_mbs_validator.py
  ├── test_clinical_safety_validator.py
  ├── test_prescription_validator.py
  └── test_pathology_validator.py
```

### Modify
```
/backend/requirements.txt
  - Verify pytest installed
  - Verify pytest-cov installed

/backend/src/main.py
  - Import validators for initialization
  - Call load_mock_databases() at startup
```

---

**Status**: ⏳ Ready for Agent Delegation
**Next Task**: TASK_2.3_AI_Validation.md (depends on TASK_2.2 completion)
**Review Checklist**: PM validates ≥70% coverage and <1 second performance before moving to TASK_2.3
