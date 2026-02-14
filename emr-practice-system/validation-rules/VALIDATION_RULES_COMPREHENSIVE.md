# Comprehensive Validation Rules - EMR Practice System

**Version**: 1.0
**Date**: 2026-02-02
**Purpose**: Complete validation specifications for SOAP notes, prescriptions, pathology orders, and clinical documentation in EMR practice system

---

## Table of Contents

1. [Overview](#overview)
2. [Three-Layer Validation Architecture](#three-layer-validation-architecture)
3. [Layer 1: Client-Side Validation (Zod)](#layer-1-client-side-validation-zod)
4. [Layer 2: Rule-Based Validation (Python)](#layer-2-rule-based-validation-python)
5. [Layer 3: AI-Powered Clinical Validation (Claude)](#layer-3-ai-powered-clinical-validation-claude)
6. [Australian Medical Compliance Rules](#australian-medical-compliance-rules)
7. [Clinical Red Flags](#clinical-red-flags)
8. [Validation Response Format](#validation-response-format)

---

## Overview

The EMR practice system uses a progressive three-layer validation approach:

| Layer | Technology | Response Time | Purpose | Feedback Type |
|-------|-----------|---------------|---------|---------------|
| Layer 1 | Zod (TypeScript) | Instant (<50ms) | Data structure, required fields, format | Red underlines, inline errors |
| Layer 2 | Python Rules Engine | Fast (<1 second) | Business logic, Australian compliance, safety checks | Yellow warnings, suggestions |
| Layer 3 | Claude AI | Deep (3-5 seconds) | Clinical reasoning, completeness, quality | Green insights, educational feedback |

**Progressive Disclosure**: Each layer builds on the previous one, providing increasingly sophisticated feedback.

---

## Three-Layer Validation Architecture

```
User Input
    ↓
┌─────────────────────────────────────────┐
│  Layer 1: Client-Side (Zod)            │
│  • Instant validation (<50ms)          │
│  • Required fields, data types         │
│  • Format validation (dates, dosages)  │
└─────────────────────────────────────────┘
    ↓ (if Layer 1 passes)
┌─────────────────────────────────────────┐
│  Layer 2: Rule-Based (Python)          │
│  • Fast validation (<1 second)         │
│  • PBS/MBS compliance                  │
│  • Drug interactions, contraindications│
│  • Clinical safety rules               │
└─────────────────────────────────────────┘
    ↓ (if Layer 2 passes)
┌─────────────────────────────────────────┐
│  Layer 3: AI-Powered (Claude)          │
│  • Deep validation (3-5 seconds)       │
│  • Clinical reasoning assessment       │
│  • Documentation completeness          │
│  • Educational feedback                │
└─────────────────────────────────────────┘
    ↓
Final Validation Result
```

---

## Layer 1: Client-Side Validation (Zod)

### 1.1 SOAP Note Schema

```typescript
import { z } from 'zod';

// Subjective Section Schema
const subjectiveSchema = z.object({
  chiefComplaint: z.string()
    .min(5, "Chief complaint must be at least 5 characters")
    .max(200, "Chief complaint must be less than 200 characters")
    .regex(/^[A-Z]/, "Chief complaint should start with a capital letter"),

  hpi: z.string()
    .min(50, "History of Present Illness should be at least 50 characters")
    .max(2000, "HPI should be less than 2000 characters"),

  pastMedicalHistory: z.array(z.string())
    .min(1, "At least one past medical history item required (or 'Nil significant')"),

  medications: z.array(z.object({
    name: z.string().min(2, "Medication name required"),
    dose: z.string().regex(/^\d+(\.\d+)?\s*(mg|g|mcg|mL|units)$/, "Invalid dose format (e.g., '500mg')"),
    frequency: z.string().regex(/^(daily|BD|TDS|QID|PRN|weekly)$/i, "Invalid frequency"),
    route: z.string().regex(/^(PO|IV|IM|SC|PR|topical|inhaled)$/i, "Invalid route")
  })),

  allergies: z.array(z.object({
    allergen: z.string().min(2, "Allergen name required"),
    reaction: z.string().min(3, "Reaction description required"),
    severity: z.enum(['mild', 'moderate', 'severe'])
  })).default([{ allergen: 'NKDA', reaction: 'None', severity: 'mild' }]),

  socialHistory: z.object({
    smoking: z.enum(['never', 'ex-smoker', 'current']),
    smokingPackYears: z.number().min(0).max(150).optional(),
    alcohol: z.enum(['none', 'social', 'moderate', 'heavy']),
    alcoholUnitsPerWeek: z.number().min(0).max(200).optional(),
    occupation: z.string().optional()
  }),

  familyHistory: z.array(z.string())
    .min(1, "At least one family history item required (or 'Non-contributory')")
});

// Objective Section Schema
const objectiveSchema = z.object({
  vitalSigns: z.object({
    temperature: z.number()
      .min(35, "Temperature too low")
      .max(42, "Temperature too high"),

    heartRate: z.number()
      .min(30, "Heart rate too low")
      .max(220, "Heart rate too high"),

    bloodPressure: z.object({
      systolic: z.number().min(60).max(250),
      diastolic: z.number().min(40).max(150)
    }).refine(
      (bp) => bp.systolic > bp.diastolic,
      "Systolic must be greater than diastolic"
    ),

    respiratoryRate: z.number()
      .min(8, "Respiratory rate too low")
      .max(60, "Respiratory rate too high"),

    oxygenSaturation: z.number()
      .min(50, "O2 saturation too low")
      .max(100, "O2 saturation cannot exceed 100%"),

    weight: z.number().min(2).max(300).optional(),
    height: z.number().min(30).max(250).optional(),
    bmi: z.number().min(10).max(70).optional()
  }),

  generalAppearance: z.string()
    .min(20, "General appearance should be at least 20 characters"),

  systemsExamination: z.object({
    cardiovascular: z.string().min(10, "Cardiovascular exam too brief"),
    respiratory: z.string().min(10, "Respiratory exam too brief"),
    abdominal: z.string().min(10, "Abdominal exam too brief"),
    neurological: z.string().optional(),
    musculoskeletal: z.string().optional(),
    skin: z.string().optional()
  })
});

// Assessment Section Schema
const assessmentSchema = z.object({
  workingDiagnosis: z.string()
    .min(5, "Working diagnosis required")
    .max(200, "Working diagnosis too long"),

  differentialDiagnoses: z.array(z.string())
    .min(2, "At least 2 differential diagnoses required")
    .max(5, "Maximum 5 differential diagnoses"),

  clinicalReasoning: z.string()
    .min(100, "Clinical reasoning should be at least 100 characters")
    .max(1500, "Clinical reasoning too long"),

  redFlags: z.array(z.string())
    .default([])
});

// Plan Section Schema
const planSchema = z.object({
  investigations: z.array(z.object({
    type: z.enum(['pathology', 'imaging', 'other']),
    test: z.string().min(3, "Test name required"),
    mbsItemNumber: z.string().regex(/^\d{5}$/, "MBS item number must be 5 digits").optional(),
    indication: z.string().min(10, "Indication required"),
    urgency: z.enum(['routine', 'urgent', 'emergency'])
  })).min(1, "At least one investigation required"),

  management: z.array(z.object({
    category: z.enum(['medication', 'procedure', 'referral', 'education', 'lifestyle']),
    description: z.string().min(10, "Management description required"),
    timeframe: z.string().optional()
  })).min(1, "At least one management item required"),

  followUp: z.object({
    timing: z.string().min(5, "Follow-up timing required (e.g., '2 weeks')"),
    reviewItems: z.array(z.string()).min(1, "At least one review item required"),
    redFlagsToAdvise: z.array(z.string()).optional()
  }),

  safetyNetting: z.string()
    .min(50, "Safety netting advice should be at least 50 characters")
});

// Complete SOAP Note Schema
export const soapNoteSchema = z.object({
  sessionId: z.string().uuid(),
  patientId: z.string().uuid(),
  subjective: subjectiveSchema,
  objective: objectiveSchema,
  assessment: assessmentSchema,
  plan: planSchema,
  timestamp: z.date(),
  authorId: z.string().uuid()
});

export type SOAPNote = z.infer<typeof soapNoteSchema>;
```

### 1.2 Prescription Schema

```typescript
// PBS Medication Schema
const pbsMedicationSchema = z.object({
  pbsCode: z.string()
    .regex(/^\d{4}[A-Z]$/, "PBS code must be 4 digits + letter (e.g., '1234A')"),

  medicationName: z.string()
    .min(2, "Medication name required")
    .refine(
      (name) => !name.toLowerCase().includes('acetaminophen'),
      "Use Australian terminology: 'paracetamol' not 'acetaminophen'"
    ),

  strength: z.string()
    .regex(/^\d+(\.\d+)?\s*(mg|g|mcg|mL|units)$/, "Invalid strength format"),

  form: z.enum([
    'tablet', 'capsule', 'liquid', 'cream', 'ointment',
    'injection', 'inhaler', 'patch', 'suppository'
  ]),

  quantity: z.number()
    .min(1, "Quantity must be at least 1")
    .max(200, "Quantity exceeds typical prescription limit"),

  repeats: z.number()
    .min(0, "Repeats cannot be negative")
    .max(5, "PBS maximum 5 repeats for most medications"),

  dosage: z.object({
    amount: z.string().regex(/^\d+(\.\d+)?(-\d+(\.\d+)?)?$/, "Invalid dosage amount"),
    frequency: z.string().regex(/^(daily|BD|TDS|QID|PRN|weekly|fortnightly)$/i),
    route: z.enum(['PO', 'IV', 'IM', 'SC', 'PR', 'topical', 'inhaled', 'sublingual']),
    duration: z.string().optional()
  }),

  indication: z.string()
    .min(10, "Indication for medication required (PBS requirement)"),

  authorityRequired: z.boolean()
    .default(false),

  authorityCode: z.string()
    .optional()
    .refine(
      (code, ctx) => {
        const authorityRequired = ctx.parent.authorityRequired;
        if (authorityRequired && !code) return false;
        return true;
      },
      "Authority code required for restricted PBS medications"
    )
});

export const prescriptionSchema = z.object({
  sessionId: z.string().uuid(),
  patientId: z.string().uuid(),
  medications: z.array(pbsMedicationSchema)
    .min(1, "At least one medication required"),
  prescriberNumber: z.string()
    .regex(/^\d{7}$/, "Prescriber number must be 7 digits (AHPRA format)"),
  timestamp: z.date(),

  // Drug interaction checking flags
  interactionCheckPassed: z.boolean().optional(),
  allergyCheckPassed: z.boolean().optional()
});

export type Prescription = z.infer<typeof prescriptionSchema>;
```

### 1.3 Pathology Order Schema

```typescript
const pathologyTestSchema = z.object({
  testName: z.string().min(3, "Test name required"),

  mbsItemNumber: z.string()
    .regex(/^\d{5}$/, "MBS item number must be 5 digits"),

  category: z.enum([
    'haematology', 'biochemistry', 'microbiology',
    'immunology', 'pathology', 'other'
  ]),

  specimenType: z.enum([
    'blood', 'urine', 'stool', 'sputum',
    'swab', 'tissue', 'csf', 'other'
  ]),

  urgency: z.enum(['routine', 'urgent', 'emergency']),

  indication: z.string()
    .min(20, "Clinical indication required (MBS requirement)"),

  fastingRequired: z.boolean().default(false)
});

export const pathologyOrderSchema = z.object({
  sessionId: z.string().uuid(),
  patientId: z.string().uuid(),
  tests: z.array(pathologyTestSchema)
    .min(1, "At least one test required")
    .max(20, "Maximum 20 tests per order"),

  providerNumber: z.string()
    .regex(/^\d{7}[A-Z]{2}$/, "Provider number must be 7 digits + 2 letters"),

  timestamp: z.date(),

  // Clinical context
  clinicalNotes: z.string()
    .min(30, "Clinical notes should be at least 30 characters"),

  collectionInstructions: z.string().optional()
});

export type PathologyOrder = z.infer<typeof pathologyOrderSchema>;
```

---

## Layer 2: Rule-Based Validation (Python)

### 2.1 PBS Medication Validation Engine

```python
# backend/src/validation/pbs_validator.py

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import date

@dataclass
class PBSMedication:
    pbs_code: str
    name: str
    strength: str
    max_quantity: int
    max_repeats: int
    authority_required: bool
    restrictions: List[str]
    contraindications: List[str]
    interactions: List[str]
    pregnancy_category: str  # A, B1, B2, B3, C, D, X
    breastfeeding_safe: bool

class PBSDatabase:
    """Mock PBS database - in production, connect to actual PBS API"""

    MEDICATIONS = {
        "1234A": PBSMedication(
            pbs_code="1234A",
            name="Paracetamol",
            strength="500mg",
            max_quantity=100,
            max_repeats=5,
            authority_required=False,
            restrictions=[],
            contraindications=["severe hepatic impairment"],
            interactions=["warfarin"],
            pregnancy_category="A",
            breastfeeding_safe=True
        ),
        "5678B": PBSMedication(
            pbs_code="5678B",
            name="Amoxicillin",
            strength="500mg",
            max_quantity=30,
            max_repeats=0,
            authority_required=False,
            restrictions=["acute infection only"],
            contraindications=["penicillin allergy"],
            interactions=["methotrexate", "oral contraceptives"],
            pregnancy_category="A",
            breastfeeding_safe=True
        ),
        "9012C": PBSMedication(
            pbs_code="9012C",
            name="Metformin",
            strength="500mg",
            max_quantity=200,
            max_repeats=5,
            authority_required=False,
            restrictions=["Type 2 diabetes only"],
            contraindications=["renal impairment (eGFR <30)", "metabolic acidosis"],
            interactions=["contrast media", "alcohol"],
            pregnancy_category="C",
            breastfeeding_safe=False
        )
        # In production: Load from PBS database (4,000+ medications)
    }

    @classmethod
    def get_medication(cls, pbs_code: str) -> Optional[PBSMedication]:
        return cls.MEDICATIONS.get(pbs_code)

@dataclass
class ValidationError:
    severity: str  # 'error', 'warning', 'info'
    category: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None

class PBSValidator:
    """Rule-based PBS medication validator"""

    def __init__(self):
        self.errors: List[ValidationError] = []

    def validate_prescription(
        self,
        medications: List[Dict],
        patient_allergies: List[Dict],
        patient_conditions: List[str],
        patient_medications: List[Dict],
        patient_age: int,
        patient_pregnant: bool = False,
        patient_breastfeeding: bool = False
    ) -> List[ValidationError]:
        """Comprehensive prescription validation"""

        self.errors = []

        for med in medications:
            # 1. Validate PBS code exists
            pbs_med = PBSDatabase.get_medication(med['pbs_code'])
            if not pbs_med:
                self.errors.append(ValidationError(
                    severity='error',
                    category='pbs_compliance',
                    message=f"Invalid PBS code: {med['pbs_code']}",
                    field='pbs_code',
                    suggestion="Check PBS online at pbs.gov.au"
                ))
                continue

            # 2. Check quantity limits
            if med['quantity'] > pbs_med.max_quantity:
                self.errors.append(ValidationError(
                    severity='warning',
                    category='pbs_compliance',
                    message=f"Quantity ({med['quantity']}) exceeds PBS maximum ({pbs_med.max_quantity})",
                    field='quantity',
                    suggestion=f"Reduce to {pbs_med.max_quantity} or provide clinical justification"
                ))

            # 3. Check repeats limit
            if med['repeats'] > pbs_med.max_repeats:
                self.errors.append(ValidationError(
                    severity='error',
                    category='pbs_compliance',
                    message=f"Repeats ({med['repeats']}) exceed PBS maximum ({pbs_med.max_repeats})",
                    field='repeats',
                    suggestion=f"Maximum {pbs_med.max_repeats} repeats for {pbs_med.name}"
                ))

            # 4. Check authority requirement
            if pbs_med.authority_required and not med.get('authority_code'):
                self.errors.append(ValidationError(
                    severity='error',
                    category='pbs_compliance',
                    message=f"{pbs_med.name} requires PBS authority",
                    field='authority_code',
                    suggestion="Obtain authority approval before prescribing"
                ))

            # 5. Check allergy contraindications
            for allergy in patient_allergies:
                allergen = allergy['allergen'].lower()
                if any(contraind.lower() in allergen for contraind in pbs_med.contraindications):
                    self.errors.append(ValidationError(
                        severity='error',
                        category='safety',
                        message=f"CONTRAINDICATED: Patient allergic to {allergen}",
                        field='medication',
                        suggestion=f"Consider alternative to {pbs_med.name}"
                    ))

            # 6. Check drug-drug interactions
            for existing_med in patient_medications:
                existing_name = existing_med['name'].lower()
                if any(interaction.lower() in existing_name for interaction in pbs_med.interactions):
                    self.errors.append(ValidationError(
                        severity='warning',
                        category='drug_interaction',
                        message=f"Potential interaction: {pbs_med.name} with {existing_med['name']}",
                        field='medication',
                        suggestion="Review interaction severity and consider alternatives"
                    ))

            # 7. Check pregnancy category
            if patient_pregnant:
                if pbs_med.pregnancy_category in ['D', 'X']:
                    self.errors.append(ValidationError(
                        severity='error',
                        category='safety',
                        message=f"CONTRAINDICATED in pregnancy (Category {pbs_med.pregnancy_category})",
                        field='medication',
                        suggestion=f"Do not prescribe {pbs_med.name} to pregnant patients"
                    ))
                elif pbs_med.pregnancy_category in ['C', 'B3']:
                    self.errors.append(ValidationError(
                        severity='warning',
                        category='safety',
                        message=f"Use with caution in pregnancy (Category {pbs_med.pregnancy_category})",
                        field='medication',
                        suggestion="Discuss risks/benefits with patient"
                    ))

            # 8. Check breastfeeding safety
            if patient_breastfeeding and not pbs_med.breastfeeding_safe:
                self.errors.append(ValidationError(
                    severity='warning',
                    category='safety',
                    message=f"{pbs_med.name} may not be safe during breastfeeding",
                    field='medication',
                    suggestion="Consult AMH or MotherSafe (1800 647 848)"
                ))

            # 9. Check age-appropriate dosing
            if patient_age < 18:
                self.errors.append(ValidationError(
                    severity='info',
                    category='safety',
                    message=f"Paediatric dosing required for {pbs_med.name}",
                    field='dosage',
                    suggestion="Verify dose using AMH Children's Dosing Companion"
                ))
            elif patient_age > 65:
                self.errors.append(ValidationError(
                    severity='info',
                    category='safety',
                    message=f"Elderly patient - consider dose adjustment for {pbs_med.name}",
                    field='dosage',
                    suggestion="Check renal function and consider reduced dose"
                ))

        return self.errors
```

### 2.2 MBS Pathology Validation Engine

```python
# backend/src/validation/mbs_validator.py

from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class MBSItem:
    item_number: str
    description: str
    category: str
    requires_indication: bool
    requires_fasting: bool
    frequency_limit: Optional[str]  # e.g., "once per 12 months"
    cost: float  # Schedule fee

class MBSDatabase:
    """Mock MBS database - in production, connect to actual MBS API"""

    ITEMS = {
        "65070": MBSItem(
            item_number="65070",
            description="Full Blood Count (FBC)",
            category="haematology",
            requires_indication=True,
            requires_fasting=False,
            frequency_limit=None,
            cost=16.90
        ),
        "66512": MBSItem(
            item_number="66512",
            description="Lipid Studies",
            category="biochemistry",
            requires_indication=True,
            requires_fasting=True,
            frequency_limit="once per 12 months",
            cost=19.40
        ),
        "66551": MBSItem(
            item_number="66551",
            description="HbA1c",
            category="biochemistry",
            requires_indication=True,
            requires_fasting=False,
            frequency_limit="once per 3 months for diabetes monitoring",
            cost=16.80
        )
        # In production: Load from MBS database
    }

    @classmethod
    def get_item(cls, item_number: str) -> Optional[MBSItem]:
        return cls.ITEMS.get(item_number)

class MBSValidator:
    """Rule-based MBS pathology validator"""

    def __init__(self):
        self.errors: List[ValidationError] = []

    def validate_pathology_order(
        self,
        tests: List[Dict],
        indication: str,
        patient_recent_tests: List[Dict]
    ) -> List[ValidationError]:
        """Comprehensive pathology order validation"""

        self.errors = []

        # 1. Check indication provided (MBS requirement)
        if not indication or len(indication) < 20:
            self.errors.append(ValidationError(
                severity='error',
                category='mbs_compliance',
                message="Clinical indication required (MBS requirement)",
                field='indication',
                suggestion="Provide detailed clinical indication for tests"
            ))

        for test in tests:
            # 2. Validate MBS item number
            mbs_item = MBSDatabase.get_item(test['mbs_item_number'])
            if not mbs_item:
                self.errors.append(ValidationError(
                    severity='error',
                    category='mbs_compliance',
                    message=f"Invalid MBS item number: {test['mbs_item_number']}",
                    field='mbs_item_number',
                    suggestion="Check MBS online at mbsonline.gov.au"
                ))
                continue

            # 3. Check fasting requirement
            if mbs_item.requires_fasting and not test.get('fasting_required'):
                self.errors.append(ValidationError(
                    severity='warning',
                    category='test_requirements',
                    message=f"{mbs_item.description} requires fasting",
                    field='fasting_required',
                    suggestion="Advise patient to fast 10-12 hours before test"
                ))

            # 4. Check frequency limits
            if mbs_item.frequency_limit:
                # Check recent tests
                for recent_test in patient_recent_tests:
                    if recent_test['mbs_item_number'] == mbs_item.item_number:
                        self.errors.append(ValidationError(
                            severity='warning',
                            category='mbs_compliance',
                            message=f"{mbs_item.description} frequency limit: {mbs_item.frequency_limit}",
                            field='test',
                            suggestion="Provide clinical justification for repeat test"
                        ))

            # 5. Validate indication matches test
            indication_lower = indication.lower()
            if mbs_item.category == 'haematology' and 'blood' not in indication_lower:
                self.errors.append(ValidationError(
                    severity='info',
                    category='clinical_reasoning',
                    message=f"Indication unclear for {mbs_item.description}",
                    field='indication',
                    suggestion="Clarify why haematology test is indicated"
                ))

        return self.errors
```

### 2.3 SOAP Note Clinical Safety Rules

```python
# backend/src/validation/clinical_safety_validator.py

from typing import List, Dict
import re

class ClinicalSafetyValidator:
    """Rule-based clinical safety checks for SOAP notes"""

    RED_FLAG_PATTERNS = {
        'chest_pain': [
            r'\b(chest pain|chest discomfort|angina|crushing pain)\b',
            r'\b(radiating pain|jaw pain|arm pain)\b',
            r'\b(diaphoresis|sweating profusely)\b'
        ],
        'stroke': [
            r'\b(facial droop|weakness|numbness)\b',
            r'\b(slurred speech|dysarthria|aphasia)\b',
            r'\b(sudden headache|worst headache)\b',
            r'\b(loss of vision|diplopia|visual loss)\b'
        ],
        'sepsis': [
            r'\b(fever|temperature >38|rigors)\b',
            r'\b(tachycardia|HR >100)\b',
            r'\b(hypotension|BP <90)\b',
            r'\b(confusion|altered mental state)\b'
        ],
        'anaphylaxis': [
            r'\b(difficulty breathing|stridor|wheezing)\b',
            r'\b(facial swelling|angioedema)\b',
            r'\b(urticaria|rash|itch)\b',
            r'\b(recent allergen exposure)\b'
        ],
        'suicide_risk': [
            r'\b(suicidal|self harm|wants to die)\b',
            r'\b(hopeless|no point living)\b',
            r'\b(suicide plan|suicide method)\b'
        ]
    }

    def __init__(self):
        self.errors: List[ValidationError] = []

    def validate_soap_note(self, soap_note: Dict) -> List[ValidationError]:
        """Comprehensive SOAP note safety validation"""

        self.errors = []

        # 1. Check for red flag patterns
        self._check_red_flags(soap_note)

        # 2. Validate vital signs
        self._validate_vital_signs(soap_note['objective']['vital_signs'])

        # 3. Check differential diagnoses completeness
        self._check_differentials(soap_note['assessment'])

        # 4. Validate follow-up plan
        self._validate_follow_up(soap_note['plan'])

        # 5. Check safety netting
        self._check_safety_netting(soap_note['plan'])

        return self.errors

    def _check_red_flags(self, soap_note: Dict):
        """Detect clinical red flags in documentation"""

        combined_text = ' '.join([
            soap_note['subjective']['chief_complaint'],
            soap_note['subjective']['hpi'],
            soap_note['objective']['general_appearance']
        ]).lower()

        for flag_category, patterns in self.RED_FLAG_PATTERNS.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    matches.append(pattern)

            if matches:
                severity = 'error' if flag_category in ['chest_pain', 'stroke', 'anaphylaxis', 'suicide_risk'] else 'warning'

                self.errors.append(ValidationError(
                    severity=severity,
                    category='red_flag',
                    message=f"RED FLAG DETECTED: {flag_category.replace('_', ' ').title()}",
                    field='assessment',
                    suggestion=self._get_red_flag_action(flag_category)
                ))

    def _get_red_flag_action(self, flag_category: str) -> str:
        """Get appropriate action for red flag"""

        actions = {
            'chest_pain': "Consider ACS protocol: ECG, troponin, aspirin 300mg, GTN, urgent cardiology review",
            'stroke': "Activate CODE STROKE: CT brain, BP control, consider thrombolysis within 4.5 hours",
            'sepsis': "Initiate sepsis protocol: blood cultures, IV antibiotics within 1 hour, fluid resuscitation",
            'anaphylaxis': "Anaphylaxis protocol: IM adrenaline 0.5mg, remove allergen, IV fluids, antihistamine",
            'suicide_risk': "Psychiatric emergency: Risk assessment, ensure patient safety, urgent mental health review"
        }

        return actions.get(flag_category, "Urgent clinical review required")

    def _validate_vital_signs(self, vital_signs: Dict):
        """Check for abnormal vital signs"""

        # Temperature
        temp = vital_signs['temperature']
        if temp < 36.0:
            self.errors.append(ValidationError(
                severity='warning',
                category='vital_signs',
                message=f"Hypothermia detected: Temperature {temp}°C",
                field='temperature',
                suggestion="Consider warming measures, check for sepsis or hypothyroidism"
            ))
        elif temp > 38.0:
            self.errors.append(ValidationError(
                severity='warning',
                category='vital_signs',
                message=f"Fever detected: Temperature {temp}°C",
                field='temperature',
                suggestion="Investigate infection source, consider blood cultures if >38.5°C"
            ))

        # Heart Rate
        hr = vital_signs['heart_rate']
        if hr < 50:
            self.errors.append(ValidationError(
                severity='warning',
                category='vital_signs',
                message=f"Bradycardia: Heart rate {hr} bpm",
                field='heart_rate',
                suggestion="Check medications (beta-blockers, digoxin), ECG, consider causes"
            ))
        elif hr > 100:
            self.errors.append(ValidationError(
                severity='warning',
                category='vital_signs',
                message=f"Tachycardia: Heart rate {hr} bpm",
                field='heart_rate',
                suggestion="Investigate causes: pain, anxiety, sepsis, PE, cardiac arrhythmia"
            ))

        # Blood Pressure
        bp_systolic = vital_signs['blood_pressure']['systolic']
        bp_diastolic = vital_signs['blood_pressure']['diastolic']

        if bp_systolic < 90:
            self.errors.append(ValidationError(
                severity='error',
                category='vital_signs',
                message=f"Hypotension: BP {bp_systolic}/{bp_diastolic} mmHg",
                field='blood_pressure',
                suggestion="Urgent assessment: IV access, fluid resuscitation, investigate cause (sepsis, bleeding, cardiac)"
            ))
        elif bp_systolic > 180 or bp_diastolic > 110:
            self.errors.append(ValidationError(
                severity='warning',
                category='vital_signs',
                message=f"Hypertensive urgency: BP {bp_systolic}/{bp_diastolic} mmHg",
                field='blood_pressure',
                suggestion="Assess for end-organ damage, consider antihypertensive treatment"
            ))

        # Oxygen Saturation
        spo2 = vital_signs['oxygen_saturation']
        if spo2 < 90:
            self.errors.append(ValidationError(
                severity='error',
                category='vital_signs',
                message=f"Critical hypoxia: SpO2 {spo2}%",
                field='oxygen_saturation',
                suggestion="Urgent: Oxygen therapy, ABG, CXR, investigate respiratory/cardiac cause"
            ))
        elif spo2 < 94:
            self.errors.append(ValidationError(
                severity='warning',
                category='vital_signs',
                message=f"Mild hypoxia: SpO2 {spo2}%",
                field='oxygen_saturation',
                suggestion="Consider oxygen therapy, assess respiratory status"
            ))

    def _check_differentials(self, assessment: Dict):
        """Validate differential diagnoses completeness"""

        if len(assessment['differential_diagnoses']) < 2:
            self.errors.append(ValidationError(
                severity='warning',
                category='clinical_reasoning',
                message="Insufficient differential diagnoses",
                field='differential_diagnoses',
                suggestion="Include at least 2-3 differential diagnoses with clinical reasoning"
            ))

        if len(assessment['clinical_reasoning']) < 100:
            self.errors.append(ValidationError(
                severity='warning',
                category='clinical_reasoning',
                message="Clinical reasoning too brief",
                field='clinical_reasoning',
                suggestion="Explain reasoning for working diagnosis and key differentials"
            ))

    def _validate_follow_up(self, plan: Dict):
        """Ensure appropriate follow-up planned"""

        if not plan.get('follow_up'):
            self.errors.append(ValidationError(
                severity='error',
                category='management',
                message="No follow-up plan specified",
                field='follow_up',
                suggestion="Specify follow-up timing and review items"
            ))

    def _check_safety_netting(self, plan: Dict):
        """Ensure safety netting advice provided"""

        safety_netting = plan.get('safety_netting', '')
        if len(safety_netting) < 50:
            self.errors.append(ValidationError(
                severity='warning',
                category='safety',
                message="Insufficient safety netting advice",
                field='safety_netting',
                suggestion="Provide clear red flag symptoms and when to seek urgent care"
            ))
```

---

## Layer 3: AI-Powered Clinical Validation (Claude)

### 3.1 SOAP Note Deep Validation

```python
# backend/src/validation/ai_validator.py

from anthropic import Anthropic
from typing import Dict, List
import json

class AIValidator:
    """AI-powered clinical validation using Claude 3.5 Sonnet"""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    async def validate_soap_note(self, soap_note: Dict, patient_context: Dict) -> Dict:
        """
        Deep clinical validation of SOAP note

        Returns:
        {
            "overall_score": 0-100,
            "strengths": ["..."],
            "improvements": ["..."],
            "educational_feedback": "...",
            "clinical_reasoning_quality": "excellent|good|adequate|needs_improvement",
            "documentation_completeness": 0-100
        }
        """

        prompt = self._build_soap_validation_prompt(soap_note, patient_context)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.3,  # Lower temperature for consistent evaluation
            system=self._get_system_prompt(),
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return json.loads(response.content[0].text)

    def _get_system_prompt(self) -> str:
        """System prompt for AI validator"""

        return """You are an Australian medical educator and senior clinician with expertise in:
        - Clinical documentation assessment
        - Australian medical terminology and practices
        - PBS/MBS compliance
        - AMC Clinical Examination standards
        - eTG (Therapeutic Guidelines) recommendations

        Your role is to provide educational feedback on clinical documentation created by medical students preparing for ICRP (Intern Clinical Readiness Program).

        Assessment Criteria:
        1. **Clinical Reasoning** (30 points)
           - Logical progression from history to diagnosis
           - Appropriate differential diagnoses
           - Evidence-based reasoning

        2. **Documentation Completeness** (25 points)
           - All required sections present
           - Adequate detail in each section
           - No critical omissions

        3. **Australian Medical Compliance** (20 points)
           - Correct Australian terminology (paracetamol, paediatric, etc.)
           - PBS/MBS item numbers where applicable
           - Alignment with eTG recommendations

        4. **Patient Safety** (15 points)
           - Red flags identified and addressed
           - Appropriate safety netting
           - Risk mitigation strategies

        5. **Professional Communication** (10 points)
           - Clear, concise language
           - Appropriate medical terminology
           - Structured format

        Provide constructive, educational feedback that helps students improve their clinical documentation skills.

        Return your assessment as JSON in this exact format:
        {
            "overall_score": 0-100,
            "category_scores": {
                "clinical_reasoning": 0-30,
                "documentation_completeness": 0-25,
                "australian_compliance": 0-20,
                "patient_safety": 0-15,
                "professional_communication": 0-10
            },
            "strengths": ["strength 1", "strength 2", "strength 3"],
            "improvements": [
                {
                    "category": "clinical_reasoning|documentation|compliance|safety|communication",
                    "issue": "specific issue identified",
                    "suggestion": "how to improve",
                    "example": "example of good practice"
                }
            ],
            "educational_feedback": "2-3 paragraphs of constructive feedback",
            "clinical_reasoning_quality": "excellent|good|adequate|needs_improvement",
            "critical_errors": ["any critical safety or clinical errors"],
            "commendations": ["specific things done well"]
        }"""

    def _build_soap_validation_prompt(self, soap_note: Dict, patient_context: Dict) -> str:
        """Build comprehensive validation prompt"""

        return f"""Please validate this SOAP note for a medical student's EMR practice session.

**Patient Context:**
- Age: {patient_context['age']} years
- Sex: {patient_context['sex']}
- Presenting Complaint: {patient_context['presenting_complaint']}
- Practice Scenario: {patient_context['scenario_description']}

**Student's SOAP Note:**

### SUBJECTIVE
**Chief Complaint:** {soap_note['subjective']['chief_complaint']}

**History of Present Illness:**
{soap_note['subjective']['hpi']}

**Past Medical History:**
{', '.join(soap_note['subjective']['past_medical_history'])}

**Current Medications:**
{self._format_medications(soap_note['subjective']['medications'])}

**Allergies:**
{self._format_allergies(soap_note['subjective']['allergies'])}

**Social History:**
- Smoking: {soap_note['subjective']['social_history']['smoking']}
- Alcohol: {soap_note['subjective']['social_history']['alcohol']}
- Occupation: {soap_note['subjective']['social_history'].get('occupation', 'Not specified')}

**Family History:**
{', '.join(soap_note['subjective']['family_history'])}

### OBJECTIVE
**Vital Signs:**
- Temperature: {soap_note['objective']['vital_signs']['temperature']}°C
- Heart Rate: {soap_note['objective']['vital_signs']['heart_rate']} bpm
- Blood Pressure: {soap_note['objective']['vital_signs']['blood_pressure']['systolic']}/{soap_note['objective']['vital_signs']['blood_pressure']['diastolic']} mmHg
- Respiratory Rate: {soap_note['objective']['vital_signs']['respiratory_rate']}/min
- SpO2: {soap_note['objective']['vital_signs']['oxygen_saturation']}%

**General Appearance:**
{soap_note['objective']['general_appearance']}

**Systems Examination:**
{self._format_examination(soap_note['objective']['systems_examination'])}

### ASSESSMENT
**Working Diagnosis:** {soap_note['assessment']['working_diagnosis']}

**Differential Diagnoses:**
{self._format_list(soap_note['assessment']['differential_diagnoses'])}

**Clinical Reasoning:**
{soap_note['assessment']['clinical_reasoning']}

### PLAN
**Investigations:**
{self._format_investigations(soap_note['plan']['investigations'])}

**Management:**
{self._format_management(soap_note['plan']['management'])}

**Follow-up:**
- Timing: {soap_note['plan']['follow_up']['timing']}
- Review Items: {', '.join(soap_note['plan']['follow_up']['review_items'])}

**Safety Netting:**
{soap_note['plan']['safety_netting']}

---

Please provide comprehensive educational feedback on this SOAP note, focusing on clinical reasoning, documentation quality, and Australian medical practice standards."""

    def _format_medications(self, medications: List[Dict]) -> str:
        if not medications:
            return "None"
        return '\n'.join([
            f"- {med['name']} {med['dose']} {med['frequency']} {med['route']}"
            for med in medications
        ])

    def _format_allergies(self, allergies: List[Dict]) -> str:
        if not allergies or allergies[0]['allergen'] == 'NKDA':
            return "No known drug allergies"
        return '\n'.join([
            f"- {allergy['allergen']}: {allergy['reaction']} ({allergy['severity']})"
            for allergy in allergies
        ])

    def _format_examination(self, systems: Dict) -> str:
        return '\n'.join([
            f"- **{system.title()}:** {findings}"
            for system, findings in systems.items()
            if findings
        ])

    def _format_list(self, items: List[str]) -> str:
        return '\n'.join([f"{i+1}. {item}" for i, item in enumerate(items)])

    def _format_investigations(self, investigations: List[Dict]) -> str:
        return '\n'.join([
            f"- {inv['test']} ({inv['type']}) - {inv['urgency']} - MBS: {inv.get('mbs_item_number', 'N/A')}\n  Indication: {inv['indication']}"
            for inv in investigations
        ])

    def _format_management(self, management: List[Dict]) -> str:
        return '\n'.join([
            f"- [{mgmt['category']}] {mgmt['description']}"
            for mgmt in management
        ])
```

### 3.2 Prescription Deep Validation

```python
async def validate_prescription_ai(self, prescription: Dict, patient_context: Dict) -> Dict:
    """
    Deep validation of prescription

    Returns:
    {
        "safety_score": 0-100,
        "appropriateness_score": 0-100,
        "concerns": ["..."],
        "recommendations": ["..."],
        "educational_notes": "..."
    }
    """

    prompt = f"""Please validate this prescription for educational purposes.

**Patient Context:**
- Age: {patient_context['age']} years
- Weight: {patient_context['weight']} kg
- Allergies: {', '.join([a['allergen'] for a in patient_context['allergies']])}
- Current Medications: {', '.join([m['name'] for m in patient_context['current_medications']])}
- Conditions: {', '.join(patient_context['conditions'])}
- Pregnant: {patient_context.get('pregnant', False)}
- Breastfeeding: {patient_context.get('breastfeeding', False)}
- Renal Function: eGFR {patient_context.get('egfr', 'unknown')}

**Prescription:**
{self._format_prescription(prescription)}

Please assess:
1. **Medication Appropriateness** (40 points)
   - Correct medication choice for indication
   - Appropriate for patient's age, weight, comorbidities
   - Evidence-based selection (eTG compliance)

2. **Dosing Accuracy** (30 points)
   - Correct dose for indication
   - Appropriate frequency and duration
   - Dose adjustments for renal/hepatic impairment

3. **Safety Profile** (30 points)
   - No contraindications
   - Drug interactions managed
   - Allergy checks performed
   - Pregnancy/breastfeeding considerations

Return JSON assessment with safety_score, appropriateness_score, concerns, recommendations, and educational_notes."""

    response = self.client.messages.create(
        model=self.model,
        max_tokens=3000,
        temperature=0.3,
        system=self._get_prescription_validator_prompt(),
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)

def _get_prescription_validator_prompt(self) -> str:
    return """You are an Australian clinical pharmacist and medical educator specializing in:
    - Medication safety and appropriateness
    - PBS compliance and restrictions
    - Australian therapeutic guidelines (eTG)
    - Drug interactions and contraindications
    - Prescribing for special populations (paediatric, geriatric, pregnancy)

    Provide educational feedback to help medical students become safe prescribers.
    Focus on Australian prescribing practices and PBS requirements.

    Return your assessment as JSON in this format:
    {
        "safety_score": 0-100,
        "appropriateness_score": 0-100,
        "pbs_compliance_score": 0-100,
        "concerns": [
            {
                "severity": "critical|major|minor",
                "category": "dosing|interaction|contraindication|pbs_compliance",
                "issue": "specific concern",
                "recommendation": "what to do instead"
            }
        ],
        "recommendations": ["positive suggestions for improvement"],
        "educational_notes": "2-3 paragraphs explaining prescribing principles",
        "etg_alignment": "yes|partial|no",
        "etg_recommendations": "relevant eTG guidance if applicable"
    }"""
```

---

## Australian Medical Compliance Rules

### Terminology Requirements

| ❌ American Term | ✅ Australian Term | Context |
|-----------------|-------------------|---------|
| Acetaminophen | Paracetamol | Analgesic medication |
| Tylenol | Panadol | Brand name paracetamol |
| Pediatric | Paediatric | Children's medicine |
| Anesthesia | Anaesthesia | Surgical context |
| Edema | Oedema | Fluid retention |
| Hematology | Haematology | Blood specialty |
| Cesarean | Caesarean | C-section delivery |
| Liter | Litre | Volume measurement |
| Color | Colour | British spelling |
| Program | Programme | British spelling (medical context) |

### PBS Compliance Requirements

1. **PBS Code Format**: `\d{4}[A-Z]` (e.g., "1234A")
2. **Authority Items**: Require prior approval via phone or online
3. **Quantity Limits**: Must not exceed PBS maximum quantity
4. **Repeat Limits**: Maximum 5 repeats for most medications
5. **Indication Required**: Clinical indication must be documented
6. **Safety Net**: Track patient contributions for PBS safety net threshold

### MBS Compliance Requirements

1. **Item Number Format**: 5 digits (e.g., "65070")
2. **Clinical Indication**: Must be documented for all pathology
3. **Frequency Limits**: Some tests limited (e.g., lipids once per 12 months)
4. **Provider Number**: 7 digits + 2 letters (e.g., "1234567AB")
5. **Bulk Billing**: Document if bulk billed or private fee charged

---

## Clinical Red Flags

### Emergency Red Flags (Immediate Action Required)

| Category | Red Flags | Action |
|----------|-----------|--------|
| **Cardiac** | Chest pain + diaphoresis + radiation to jaw/arm | ACS protocol: ECG, troponin, aspirin 300mg, urgent cardiology |
| **Neurological** | Sudden weakness + facial droop + speech difficulty | CODE STROKE: CT brain, BP control, consider thrombolysis |
| **Respiratory** | SpO2 <90% + respiratory distress + confusion | Emergency oxygen, ABG, CXR, ICU review |
| **Sepsis** | Fever + hypotension + altered mental state + tachycardia | Sepsis protocol: blood cultures, IV antibiotics <1 hour |
| **Anaphylaxis** | Difficulty breathing + facial swelling + urticaria after allergen exposure | IM adrenaline 0.5mg, IV fluids, antihistamine, remove allergen |
| **Psychiatric** | Suicidal ideation + plan + means + hopelessness | Psychiatric emergency: ensure safety, urgent MH review |

### Warning Red Flags (Urgent Review Required)

| Category | Red Flags | Action |
|----------|-----------|--------|
| **Abdominal** | Severe abdominal pain + rigidity + rebound tenderness | Surgical review: ?perforation, ?ruptured AAA |
| **Obstetric** | Vaginal bleeding + abdominal pain in pregnancy | Urgent obstetric review: ?ectopic, ?miscarriage, ?placental abruption |
| **Paediatric** | Non-blanching rash + fever + lethargy | Meningococcal protocol: blood cultures, IV ceftriaxone |
| **Trauma** | Head injury + loss of consciousness + vomiting | CT brain, neurosurgical review if indicated |

---

## Validation Response Format

### Unified Validation Response Structure

```typescript
interface ValidationResponse {
  // Overall validation result
  passed: boolean;  // true if no critical errors

  // Three-layer validation results
  layers: {
    layer1: {
      status: 'passed' | 'failed' | 'skipped';
      duration_ms: number;
      errors: ValidationError[];
    };
    layer2: {
      status: 'passed' | 'failed' | 'skipped';
      duration_ms: number;
      errors: ValidationError[];
    };
    layer3: {
      status: 'passed' | 'failed' | 'skipped';
      duration_ms: number;
      ai_result: AIValidationResult;
    };
  };

  // Aggregated feedback
  errors: ValidationError[];       // Severity: 'error'
  warnings: ValidationError[];     // Severity: 'warning'
  info: ValidationError[];         // Severity: 'info'

  // Educational feedback
  educational_feedback: string;
  strengths: string[];
  improvements: Improvement[];

  // Scores
  overall_score: number;  // 0-100
  category_scores: {
    clinical_reasoning?: number;
    documentation_completeness?: number;
    australian_compliance?: number;
    patient_safety?: number;
    professional_communication?: number;
  };

  // Metadata
  validation_timestamp: string;
  total_duration_ms: number;
}

interface ValidationError {
  severity: 'error' | 'warning' | 'info';
  category: string;  // e.g., 'pbs_compliance', 'red_flag', 'safety'
  message: string;
  field?: string;
  suggestion?: string;
  line_number?: number;  // For text editor highlighting
}

interface Improvement {
  category: string;
  issue: string;
  suggestion: string;
  example?: string;
}

interface AIValidationResult {
  overall_score: number;
  category_scores: Record<string, number>;
  strengths: string[];
  improvements: Improvement[];
  educational_feedback: string;
  clinical_reasoning_quality: 'excellent' | 'good' | 'adequate' | 'needs_improvement';
  critical_errors: string[];
  commendations: string[];
}
```

### Example Validation Response

```json
{
  "passed": false,
  "layers": {
    "layer1": {
      "status": "failed",
      "duration_ms": 12,
      "errors": [
        {
          "severity": "error",
          "category": "required_field",
          "message": "Chief complaint must be at least 5 characters",
          "field": "subjective.chief_complaint"
        }
      ]
    },
    "layer2": {
      "status": "passed",
      "duration_ms": 847,
      "errors": [
        {
          "severity": "warning",
          "category": "pbs_compliance",
          "message": "Quantity (120) exceeds PBS maximum (100)",
          "field": "medications[0].quantity",
          "suggestion": "Reduce to 100 or provide clinical justification"
        },
        {
          "severity": "warning",
          "category": "drug_interaction",
          "message": "Potential interaction: Metformin with contrast media",
          "field": "medications[0]",
          "suggestion": "Withhold metformin 48 hours before contrast study"
        }
      ]
    },
    "layer3": {
      "status": "passed",
      "duration_ms": 4235,
      "ai_result": {
        "overall_score": 78,
        "category_scores": {
          "clinical_reasoning": 24,
          "documentation_completeness": 19,
          "australian_compliance": 18,
          "patient_safety": 12,
          "professional_communication": 5
        },
        "strengths": [
          "Comprehensive history taking with all relevant systems reviewed",
          "Appropriate differential diagnoses considered",
          "Good use of Australian medical terminology (paracetamol, paediatric)"
        ],
        "improvements": [
          {
            "category": "clinical_reasoning",
            "issue": "Differential diagnoses listed but not prioritized by likelihood",
            "suggestion": "Rank differential diagnoses from most to least likely based on clinical features",
            "example": "1. Community-acquired pneumonia (most likely based on fever, productive cough, CXR findings) 2. Bronchitis (less likely due to CXR consolidation) 3. PE (low probability, no risk factors)"
          },
          {
            "category": "documentation",
            "issue": "Safety netting advice generic and non-specific",
            "suggestion": "Provide specific red flag symptoms for this clinical scenario",
            "example": "Return immediately if: increased shortness of breath, chest pain, coughing up blood, confusion, or unable to keep down fluids"
          }
        ],
        "educational_feedback": "This is a solid SOAP note demonstrating good clinical reasoning and comprehensive documentation. Your history taking was thorough and you correctly identified the key clinical features. The differential diagnoses are appropriate, though you could strengthen your clinical reasoning by explicitly ranking them by probability and explaining your thought process.\n\nYour management plan is evidence-based and follows eTG recommendations for community-acquired pneumonia. Good use of PBS-compliant antibiotics with correct dosing. Consider adding specific parameters for clinical improvement (e.g., 'review in 48 hours, expect fever to resolve in 2-3 days, CXR improvement in 4-6 weeks').\n\nOverall, this demonstrates good readiness for internship. Focus on strengthening your safety netting advice and making your clinical reasoning more explicit to build strong defensive documentation habits.",
        "clinical_reasoning_quality": "good",
        "critical_errors": [],
        "commendations": [
          "Excellent vital signs documentation with all parameters recorded",
          "Appropriate follow-up plan with clear timeframe",
          "Good PBS compliance with correct medication codes"
        ]
      }
    }
  },
  "errors": [
    {
      "severity": "error",
      "category": "required_field",
      "message": "Chief complaint must be at least 5 characters",
      "field": "subjective.chief_complaint"
    }
  ],
  "warnings": [
    {
      "severity": "warning",
      "category": "pbs_compliance",
      "message": "Quantity (120) exceeds PBS maximum (100)",
      "field": "medications[0].quantity",
      "suggestion": "Reduce to 100 or provide clinical justification"
    },
    {
      "severity": "warning",
      "category": "drug_interaction",
      "message": "Potential interaction: Metformin with contrast media",
      "field": "medications[0]",
      "suggestion": "Withhold metformin 48 hours before contrast study"
    }
  ],
  "info": [],
  "educational_feedback": "[Same as layer3.ai_result.educational_feedback]",
  "strengths": [
    "Comprehensive history taking with all relevant systems reviewed",
    "Appropriate differential diagnoses considered",
    "Good use of Australian medical terminology"
  ],
  "improvements": [
    {
      "category": "clinical_reasoning",
      "issue": "Differential diagnoses not prioritized by likelihood",
      "suggestion": "Rank differentials from most to least likely based on clinical features"
    }
  ],
  "overall_score": 78,
  "category_scores": {
    "clinical_reasoning": 24,
    "documentation_completeness": 19,
    "australian_compliance": 18,
    "patient_safety": 12,
    "professional_communication": 5
  },
  "validation_timestamp": "2026-02-02T14:35:22Z",
  "total_duration_ms": 5094
}
```

---

## Implementation Checklist

### Layer 1 (Client-Side Zod)
- [ ] Implement all Zod schemas (SOAP, Prescription, Pathology)
- [ ] Integrate with React Hook Form
- [ ] Display inline validation errors with red underlines
- [ ] Test all field validations
- [ ] Handle optional vs required fields correctly

### Layer 2 (Rule-Based Python)
- [ ] Implement PBS validator with mock database
- [ ] Implement MBS validator with mock database
- [ ] Implement clinical safety validator
- [ ] Connect to actual PBS/MBS APIs (production)
- [ ] Test all validation rules
- [ ] Handle edge cases (multiple medications, drug interactions)

### Layer 3 (AI-Powered Claude)
- [ ] Implement AI validator client
- [ ] Create comprehensive system prompts
- [ ] Test prompt quality with sample SOAP notes
- [ ] Implement prompt caching for efficiency
- [ ] Handle API errors gracefully
- [ ] Test educational feedback quality

### Integration
- [ ] Create unified validation API endpoint
- [ ] Implement progressive validation flow
- [ ] Add validation result caching
- [ ] Create validation history tracking
- [ ] Implement real-time feedback display in UI
- [ ] Test end-to-end validation flow

---

**Document Version**: 1.0
**Last Updated**: 2026-02-02
**Next Review**: After RALPH agent implementation

