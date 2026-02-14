# TASK 2.1: Zod Validation Schemas

**Task ID**: TASK_2.1
**Phase**: Phase 2 - Validation Layer
**Estimated Time**: 6 hours
**Prerequisites**: TASK_1.1 (Project Setup)
**Dependencies**: Zod 3.22.4, TypeScript

---

## Overview

Create comprehensive Zod validation schemas for all EMR data structures. These schemas provide **Layer 1 validation** (client-side, <50ms) with Australian clinical standards.

**Reference**: See `/home/dev/Development/irStudy/emr-practice-system/design-specs/MASTER_EMR_PRD.md` section on Validation Architecture.

---

## Schemas to Create

### 1. SOAP Note Schemas (2 hours)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/schemas/soapNoteSchema.ts`

```typescript
import { z } from 'zod';

// Vital Signs Schema
export const vitalSignsSchema = z.object({
  temperature: z
    .number()
    .min(35, 'Temperature too low (hypothermia)')
    .max(42, 'Temperature too high'),
  heartRate: z
    .number()
    .int()
    .min(40, 'Heart rate too low')
    .max(200, 'Heart rate too high'),
  bloodPressureSystolic: z
    .number()
    .int()
    .min(60, 'Systolic BP too low')
    .max(250, 'Systolic BP too high'),
  bloodPressureDiastolic: z
    .number()
    .int()
    .min(40, 'Diastolic BP too low')
    .max(150, 'Diastolic BP too high'),
  respiratoryRate: z
    .number()
    .int()
    .min(8, 'Respiratory rate too low')
    .max(40, 'Respiratory rate too high'),
  oxygenSaturation: z
    .number()
    .int()
    .min(70, 'Oxygen saturation critically low')
    .max(100, 'Oxygen saturation cannot exceed 100%'),
  weight: z.number().positive().optional(),
  height: z.number().positive().optional(),
  bmi: z.number().positive().optional(),
  painScore: z.number().int().min(0).max(10).optional(),
});

// Review of Systems Schema
export const reviewOfSystemsSchema = z.object({
  constitutional: z.string().max(500).optional(),
  cardiovascular: z.string().max(500).optional(),
  respiratory: z.string().max(500).optional(),
  gastrointestinal: z.string().max(500).optional(),
  genitourinary: z.string().max(500).optional(),
  musculoskeletal: z.string().max(500).optional(),
  neurological: z.string().max(500).optional(),
  psychiatric: z.string().max(500).optional(),
  skin: z.string().max(500).optional(),
  endocrine: z.string().max(500).optional(),
  hematologic: z.string().max(500).optional(),
  immunologic: z.string().max(500).optional(),
});

// Subjective Section Schema
export const subjectiveSchema = z.object({
  chiefComplaint: z
    .string()
    .min(5, 'Chief complaint must be at least 5 characters')
    .max(200, 'Chief complaint too long'),
  hpi: z
    .string()
    .min(50, 'HPI must be at least 50 characters for adequate documentation')
    .max(5000, 'HPI too long'),
  pastMedicalHistory: z.string().max(2000).optional(),
  medications: z.string().max(2000).optional(),
  allergies: z.string().max(500).optional(),
  socialHistory: z.string().max(1000).optional(),
  familyHistory: z.string().max(1000).optional(),
  reviewOfSystems: reviewOfSystemsSchema.optional(),
});

// Objective Section Schema
export const objectiveSchema = z.object({
  vitalSigns: vitalSignsSchema,
  generalAppearance: z
    .string()
    .min(10, 'General appearance must be documented')
    .max(500),
  cardiovascularExam: z.string().max(1000).optional(),
  respiratoryExam: z.string().max(1000).optional(),
  abdominalExam: z.string().max(1000).optional(),
  neurologicalExam: z.string().max(1000).optional(),
  musculoskeletalExam: z.string().max(1000).optional(),
  skinExam: z.string().max(500).optional(),
  otherFindings: z.string().max(1000).optional(),
});

// Assessment Schema
export const assessmentSchema = z.object({
  primaryDiagnosis: z
    .string()
    .min(3, 'Primary diagnosis required')
    .max(200),
  differentialDiagnoses: z
    .array(z.string().max(200))
    .max(5)
    .optional(),
  clinicalReasoning: z
    .string()
    .min(30, 'Clinical reasoning must be documented')
    .max(2000),
  icdCodes: z
    .array(
      z.object({
        code: z.string(),
        description: z.string(),
      })
    )
    .optional(),
});

// Plan Schema
export const planSchema = z.object({
  investigations: z.string().max(2000).optional(),
  medications: z.string().max(2000).optional(),
  procedures: z.string().max(1000).optional(),
  referrals: z.string().max(1000).optional(),
  patientEducation: z.string().max(1000).optional(),
  followUp: z
    .string()
    .min(10, 'Follow-up plan required')
    .max(500),
  safetynetting: z.string().max(500).optional(),
});

// Complete SOAP Note Schema
export const soapNoteSchema = z.object({
  subjective: subjectiveSchema,
  objective: objectiveSchema,
  assessment: assessmentSchema,
  plan: planSchema,
  metadata: z.object({
    sessionId: z.string().uuid(),
    emrType: z.enum(['cerner', 'epic']),
    startTime: z.string().datetime(),
    completionTime: z.string().datetime().optional(),
    clinician: z.string(),
  }),
});

// Export type
export type SOAPNote = z.infer<typeof soapNoteSchema>;
export type VitalSigns = z.infer<typeof vitalSignsSchema>;
export type Subjective = z.infer<typeof subjectiveSchema>;
export type Objective = z.infer<typeof objectiveSchema>;
export type Assessment = z.infer<typeof assessmentSchema>;
export type Plan = z.infer<typeof planSchema>;
```

---

### 2. Prescription Schema (2 hours)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/schemas/prescriptionSchema.ts`

```typescript
import { z } from 'zod';

// Australian PBS-compliant prescription schema
export const prescriptionSchema = z
  .object({
    // Medication details
    medication: z
      .string()
      .min(3, 'Medication name required')
      .max(200),
    genericName: z.string().optional(),
    brandName: z.string().optional(),

    // Dosing
    dose: z
      .string()
      .min(1, 'Dose required')
      .max(50)
      .regex(
        /^\d+(\.\d+)?\s*(mg|g|mcg|mL|units|IU)$/i,
        'Dose must include amount and unit (e.g., "50 mg", "10 mL")'
      ),
    frequency: z
      .string()
      .min(1, 'Frequency required')
      .max(100),
    route: z.enum(
      [
        'oral',
        'IV',
        'IM',
        'SC',
        'topical',
        'inhaled',
        'rectal',
        'sublingual',
        'transdermal',
        'intranasal',
        'other',
      ],
      {
        errorMap: () => ({ message: 'Invalid route of administration' }),
      }
    ),
    duration: z
      .string()
      .min(1, 'Duration required')
      .max(50)
      .regex(
        /^\d+\s*(day|days|week|weeks|month|months)$/i,
        'Duration must include number and unit (e.g., "7 days", "2 weeks")'
      ),

    // Quantity and repeats
    quantity: z
      .number()
      .int()
      .positive('Quantity must be positive')
      .max(1000, 'Quantity exceeds maximum'),
    repeats: z
      .number()
      .int()
      .min(0, 'Repeats cannot be negative')
      .max(5, 'Maximum 5 repeats allowed on PBS'),

    // Clinical information
    indication: z
      .string()
      .min(5, 'Indication required for safe prescribing')
      .max(500),
    specialInstructions: z.string().max(500).optional(),

    // PBS information
    pbsCode: z.string().optional(),
    isPbsEligible: z.boolean().default(false),
    authorityRequired: z.boolean().default(false),
    authorityNumber: z.string().optional(),
    streamlinedCode: z.string().optional(),

    // Safety checks
    isPrn: z.boolean().default(false),
    maxDailyDose: z.string().optional(),

    // Metadata
    prescribedBy: z.string(),
    prescribedDate: z.string().datetime(),
    prescriberNumber: z
      .string()
      .regex(/^\d{7}[A-Z]?$/, 'Invalid Australian prescriber number')
      .optional(),
  })
  .refine(
    (data) => {
      // If authority required, authority number must be provided
      if (data.authorityRequired && !data.authorityNumber) {
        return false;
      }
      return true;
    },
    {
      message: 'Authority number required when authority is needed',
      path: ['authorityNumber'],
    }
  )
  .refine(
    (data) => {
      // If PBS eligible, PBS code should be provided
      if (data.isPbsEligible && !data.pbsCode && !data.streamlinedCode) {
        return false;
      }
      return true;
    },
    {
      message: 'PBS code or streamlined code required for PBS prescriptions',
      path: ['pbsCode'],
    }
  );

// Prescription batch (for multiple medications)
export const prescriptionBatchSchema = z.object({
  prescriptions: z
    .array(prescriptionSchema)
    .min(1, 'At least one prescription required')
    .max(10, 'Maximum 10 prescriptions per batch'),
  sessionId: z.string().uuid(),
  patientId: z.string().uuid(),
});

// Export types
export type Prescription = z.infer<typeof prescriptionSchema>;
export type PrescriptionBatch = z.infer<typeof prescriptionBatchSchema>;

// Common validation helpers
export const validateDrugInteractions = (
  prescriptions: Prescription[]
): boolean => {
  // This would call backend API for drug interaction checking
  return true;
};

export const validatePBSRestrictions = (
  prescription: Prescription
): boolean => {
  // This would call backend API for PBS restriction checking
  return true;
};
```

---

### 3. Pathology Order Schema (1.5 hours)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/schemas/pathologySchema.ts`

```typescript
import { z } from 'zod';

// Australian MBS-compliant pathology order schema
export const pathologyOrderSchema = z
  .object({
    // Test information
    testName: z
      .string()
      .min(3, 'Test name required')
      .max(200),
    testCategory: z.enum([
      'biochemistry',
      'haematology',
      'microbiology',
      'immunology',
      'cytology',
      'histopathology',
      'molecular',
      'other',
    ]),
    testCode: z.string().optional(),

    // Clinical information
    clinicalIndication: z
      .string()
      .min(10, 'Clinical indication required for pathology requests')
      .max(500),
    relevantHistory: z.string().max(1000).optional(),
    currentMedications: z.string().max(500).optional(),

    // Urgency
    urgency: z.enum(['routine', 'urgent', 'stat'], {
      errorMap: () => ({ message: 'Invalid urgency level' }),
    }),
    clinicalNotes: z.string().max(500).optional(),

    // Specimen details
    specimenType: z
      .string()
      .min(2, 'Specimen type required')
      .max(100),
    collectionDate: z.string().datetime().optional(),
    collectionSite: z.string().max(100).optional(),

    // MBS information
    mbsCode: z.string().optional(),
    isMbsEligible: z.boolean().default(false),
    bulkBilled: z.boolean().default(false),

    // Requesting clinician
    requestedBy: z.string(),
    requestedDate: z.string().datetime(),
    providerNumber: z
      .string()
      .regex(/^\d{6,8}[A-Z]{0,2}$/, 'Invalid Australian provider number')
      .optional(),
    copyTo: z.array(z.string()).optional(),

    // Flags
    fasting: z.boolean().default(false),
    pregnant: z.boolean().optional(),
    infectious: z.boolean().default(false),
  })
  .refine(
    (data) => {
      // Stat orders must have clinical notes
      if (data.urgency === 'stat' && !data.clinicalNotes) {
        return false;
      }
      return true;
    },
    {
      message: 'Clinical notes required for stat orders',
      path: ['clinicalNotes'],
    }
  )
  .refine(
    (data) => {
      // MBS eligible orders should have MBS code
      if (data.isMbsEligible && !data.mbsCode) {
        return false;
      }
      return true;
    },
    {
      message: 'MBS code required for MBS eligible tests',
      path: ['mbsCode'],
    }
  );

// Pathology batch (for multiple tests)
export const pathologyBatchSchema = z.object({
  orders: z
    .array(pathologyOrderSchema)
    .min(1, 'At least one test required')
    .max(20, 'Maximum 20 tests per batch'),
  sessionId: z.string().uuid(),
  patientId: z.string().uuid(),
  priority: z.enum(['routine', 'urgent', 'stat']),
});

// Common pathology test panels
export const commonPanels = {
  fbc: [
    'Full Blood Count',
    'White Cell Count',
    'Haemoglobin',
    'Platelets',
    'Differential',
  ],
  uec: [
    'Sodium',
    'Potassium',
    'Chloride',
    'Bicarbonate',
    'Urea',
    'Creatinine',
    'eGFR',
  ],
  lft: ['ALT', 'AST', 'ALP', 'GGT', 'Bilirubin', 'Albumin', 'Total Protein'],
  lipids: [
    'Total Cholesterol',
    'HDL',
    'LDL',
    'Triglycerides',
    'Cholesterol Ratio',
  ],
  tft: ['TSH', 'Free T4', 'Free T3'],
  coags: ['PT', 'INR', 'APTT'],
};

// Export types
export type PathologyOrder = z.infer<typeof pathologyOrderSchema>;
export type PathologyBatch = z.infer<typeof pathologyBatchSchema>;
```

---

### 4. Session Schema (0.5 hours)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/schemas/sessionSchema.ts`

```typescript
import { z } from 'zod';

export const sessionSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  patientId: z.string().uuid(),
  linkedOsceId: z.string().uuid().optional(),
  emrType: z.enum(['cerner', 'epic']),
  status: z.enum(['active', 'paused', 'completed', 'abandoned']),
  startedAt: z.string().datetime(),
  expiresAt: z.string().datetime(),
  completedAt: z.string().datetime().optional(),
  timeLimit: z.number().int().positive().default(15 * 60), // 15 minutes in seconds
  overallScore: z.number().int().min(0).max(100).optional(),
});

export const sessionMetricsSchema = z.object({
  sessionId: z.string().uuid(),
  typingMetrics: z.object({
    totalKeystrokes: z.number().int().min(0),
    backspaceCount: z.number().int().min(0),
    wordsPerMinute: z.number().min(0),
    accuracyRate: z.number().min(0).max(100),
  }),
  documentationMetrics: z.object({
    soapNoteCompleteness: z.number().min(0).max(100),
    prescriptionCount: z.number().int().min(0),
    pathologyOrderCount: z.number().int().min(0),
    timeToFirstEntry: z.number().int().min(0), // seconds
    totalActiveTime: z.number().int().min(0), // seconds
  }),
  validationMetrics: z.object({
    clientValidationErrors: z.number().int().min(0),
    pythonValidationErrors: z.number().int().min(0),
    aiValidationScore: z.number().min(0).max(100).optional(),
  }),
});

export type Session = z.infer<typeof sessionSchema>;
export type SessionMetrics = z.infer<typeof sessionMetricsSchema>;
```

---

## Schema Validation Utilities

**File**: `/home/dev/Development/irStudy/emr-frontend/src/schemas/validationUtils.ts`

```typescript
import { z } from 'zod';

/**
 * Validate data against schema and return formatted errors
 */
export function validateSchema<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; errors: Array<{ field: string; message: string }> } {
  const result = schema.safeParse(data);

  if (result.success) {
    return { success: true, data: result.data };
  }

  const errors = result.error.errors.map((err) => ({
    field: err.path.join('.'),
    message: err.message,
  }));

  return { success: false, errors };
}

/**
 * Validate partial data (for auto-save validation)
 */
export function validatePartial<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { isValid: boolean; errors: Array<{ field: string; message: string }> } {
  const partialSchema = schema.partial();
  const result = partialSchema.safeParse(data);

  if (result.success) {
    return { isValid: true, errors: [] };
  }

  const errors = result.error.errors.map((err) => ({
    field: err.path.join('.'),
    message: err.message,
  }));

  return { isValid: false, errors };
}

/**
 * Get field-specific error
 */
export function getFieldError(
  errors: Array<{ field: string; message: string }>,
  fieldPath: string
): string | undefined {
  return errors.find((err) => err.field === fieldPath)?.message;
}
```

---

## Validation Checklist

Before marking this task complete, verify:

- [ ] All schemas created and exported correctly
- [ ] TypeScript types properly inferred from schemas
- [ ] SOAP Note Schema:
  - [ ] Vital signs validation (ranges)
  - [ ] Review of systems (optional fields)
  - [ ] Chief complaint (min 5 chars)
  - [ ] HPI (min 50 chars)
  - [ ] Assessment (min 30 chars)
  - [ ] Plan (min 50 chars)
- [ ] Prescription Schema:
  - [ ] Dose format validation (regex)
  - [ ] Duration format validation (regex)
  - [ ] PBS compliance (authority, codes)
  - [ ] Route enum validation
  - [ ] Prescriber number format
- [ ] Pathology Schema:
  - [ ] Clinical indication required
  - [ ] Urgency levels
  - [ ] MBS compliance
  - [ ] Provider number format
  - [ ] Stat order rules
- [ ] Session Schema:
  - [ ] UUID validation
  - [ ] Datetime validation
  - [ ] Status enum
- [ ] Validation utilities work correctly
- [ ] No TypeScript errors
- [ ] Import paths use aliases (@schemas/*)

---

## Time Breakdown

- SOAP Note Schemas: 2 hours
- Prescription Schema: 2 hours
- Pathology Order Schema: 1.5 hours
- Session Schema: 0.5 hours
- **Total**: 6 hours

---

## Next Steps

After completing this task:
1. Proceed to **TASK_2.2_PYTHON_VALIDATORS.md** (Python rule-based validation)
2. Then **TASK_2.3_AI_VALIDATION.md** (Claude AI validation)

---

**Last Updated**: 2026-02-03
**Status**: Ready for Implementation
