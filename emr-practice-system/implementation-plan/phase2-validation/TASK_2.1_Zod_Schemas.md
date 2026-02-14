# TASK 2.1: Client-Side Validation - Zod Schemas (Layer 1)

**Phase**: Phase 2 - Validation Architecture
**Estimated Hours**: 6 hours
**Dependencies**: Phase 1 Complete (Frontend & Components), Zod ^3.22.4 installed, TypeScript 5.3+
**Agent Type**: `frontend-typescript-expert`
**Status**: ⏳ Not Started

---

## Overview

Implement comprehensive client-side validation layer using Zod schemas for real-time, instant feedback (<50ms). This layer provides the first line of defense against invalid data, catching format errors, missing required fields, and data type violations before submission to backend. Covers SOAP notes, prescriptions, pathology orders, and laboratory test orders with Australian terminology enforcement.

---

## Deliverables

### New Schema Files to Create

#### 1. `/emr-frontend/src/schemas/soap-note.schema.ts` (180+ lines)
- **soapNoteSchema**: Validates complete SOAP note structure
  - Subjective section: min 50 chars, max 2000 chars
  - Objective section: min 50 chars, max 2000 chars
  - Assessment section: min 30 chars, max 1500 chars
  - Plan section: min 30 chars, max 1500 chars
  - All sections required for submission
  - Timezone-aware timestamp validation
  - Episode ID validation (UUID format)

- **subjectiveSchema**: Validates subjective section
  - Chief complaint: 5-200 chars, starts with capital letter
  - HPI: 50-2000 chars, narrative format
  - Past medical history: min 1 item or "Nil significant"
  - Current medications array: name, dose format validation
  - Allergies array: allergen name, reaction, severity (mild/moderate/severe)
  - Social history fields (occupation, smoking, alcohol, drugs)

- **objectiveSchema**: Validates objective section
  - Vitals object: BP (systolic/diastolic format), HR, RR, Temp, O2Sat, Weight, Height
  - Physical examination: 6 required systems (cardiovascular, respiratory, abdominal, neurological, musculoskeletal, skin)
  - Each system: min 10 chars description
  - Lab results array: test name, value, unit, reference range

- **assessmentSchema**: Validates assessment section
  - Primary diagnosis: ICD-10 code format validation (A00-Z99.X)
  - Differential diagnoses: min 1, max 5
  - Clinical reasoning: 20-1000 chars
  - Risk stratification: low/medium/high

- **planSchema**: Validates management plan section
  - Investigations array: test name, MBS item number (5 digits)
  - Prescriptions array: medication, dose, frequency, repeats
  - Referrals array: specialty, urgency (routine/urgent/emergency)
  - Follow-up: timeframe in days, return to work status
  - Safety-net advice: patient education points

#### 2. `/emr-frontend/src/schemas/prescription.schema.ts` (160+ lines)
- **prescriptionSchema**: Validates single prescription
  - Medication name: 2-100 chars, alphanumeric + spaces only
  - PBS code: Format \d{4}[A-Z] (e.g., "1234A"), must match Australian PBS format
  - Dose: Format /^\d+(\.\d+)?\s*(mg|g|mcg|mL|units|%)$/ (e.g., "500mg", "2.5mL")
  - Dose unit: enum [mg, g, mcg, mL, units, %, meq, mmol]
  - Frequency: enum [daily, BD, TDS, QID, PRN, weekly, monthly] (case-insensitive)
  - Route: enum [PO, IV, IM, SC, PR, topical, inhaled, transdermal, sublingual]
  - Quantity: 1-999, warn if >100
  - Repeats: 0-5 maximum (PBS rule enforcement)
  - Indication: 5-500 chars, required field
  - Prescriber name: 5-100 chars, required
  - Date issued: ISO 8601 format, not future-dated
  - Authority required: boolean flag with authority code if true

- **prescriptionArraySchema**: Validates multiple prescriptions
  - Array of prescriptionSchema
  - Duplicate check: No identical medication+dose+frequency combinations
  - Interaction check: Warfarin + Aspirin flags as warning
  - Max 20 prescriptions per session

- **australianTerminologySchema**: Enforces Australian medical terminology
  - REJECT: acetaminophen, paracetamol ACCEPT
  - REJECT: morphine sulphate, ACCEPT morphine
  - REJECT: adrenaline, ACCEPT epinephrine or adrenaline (both allowed)
  - REJECT: sulfamethoxazole, ACCEPT: trimethoprim-sulfamethoxazole
  - Case-insensitive matching with error messages

#### 3. `/emr-frontend/src/schemas/pathology-order.schema.ts` (140+ lines)
- **pathologyOrderSchema**: Validates pathology order
  - Test name: 3-100 chars, alphanumeric + hyphens
  - MBS item number: exactly 5 digits (00001-99999 range)
  - Patient MRN: 5-12 alphanumeric chars
  - Specimen type: enum [blood, urine, CSF, saliva, tissue, swab, stool]
  - Collection method: enum [venipuncture, midstream, clean-catch, swab, biopsy]
  - Fasting required: boolean (UEC/lipids require fasting note)
  - Special collection instructions: max 200 chars
  - Urgency: enum [routine, urgent, emergency]
  - Indication: 5-500 chars, required
  - Date ordered: ISO 8601, not future-dated
  - Requesting clinician: 5-100 chars
  - Collection date range: If future ordered, must collect within 7 days

- **pathologyPanelSchema**: Common test panels
  - FBC (Full Blood Count): MBS 66589, no fasting required
  - UEC (Urea Electrolytes Creatinine): MBS 66589, fasting preferred
  - LFT (Liver Function Tests): MBS 66589, fasting preferred
  - Lipid Panel: MBS 66589, fasting required (flag if not)
  - Coagulation Screen: MBS 66589, special handling required
  - Thyroid Function: MBS 66589, no fasting
  - Glucose: MBS 66589, fasting status variable

- **pathologyArraySchema**: Multiple orders
  - Array of pathologyOrderSchema
  - Max 30 tests per session
  - Duplicate check: Same MBS item + patient not repeated

#### 4. `/emr-frontend/src/schemas/laboratory-tests.schema.ts` (120+ lines)
- **laboratoryTestSchema**: Individual test result validation
  - Test code: 3-10 alphanumeric chars
  - Test name: 5-100 chars
  - Result value: number or string (result format varies)
  - Unit: 1-20 chars (mg/dL, mmol/L, etc.)
  - Reference range: object {lower: number, upper: number}
  - Status: enum [normal, abnormal, critical, pending]
  - Collection date: ISO 8601, must be recent (<90 days)
  - Analysis date: ISO 8601, after collection date
  - Performed by: laboratory name or code

- **criticalValueSchema**: Flags critical lab values
  - Hemoglobin <7 g/dL or >20 g/dL
  - Potassium <2.5 or >6.5 mmol/L
  - Glucose <2.5 or >25 mmol/L
  - Troponin elevated with chest pain
  - INR >5 on warfarin

#### 5. `/emr-frontend/src/schemas/composite.schema.ts` (80+ lines)
- **sessionDataSchema**: Validates entire session data
  - Episode: soapNoteSchema
  - Prescriptions: prescriptionArraySchema
  - Pathology: pathologyArraySchema
  - Lab tests: array of laboratoryTestSchema
  - Session metadata: date, duration, user ID, patient ID

- **validationErrorSchema**: Standardized error format
  - Field path: dot notation (e.g., "subjective.chiefComplaint")
  - Error type: enum [required, format, range, logic, safety]
  - Message: user-friendly message
  - Severity: enum [error, warning, info]

### Utility Files to Create

#### 6. `/emr-frontend/src/utils/schema-validators.ts` (100+ lines)
- `validateSOAPNote(data: unknown): ValidationResult<SOAPNote>`
  - Batch validate all 4 sections
  - Return structured errors with field paths
  - Parse and report type coercion opportunities

- `validatePrescription(data: unknown): ValidationResult<Prescription>`
  - Single prescription validation
  - Cross-check against medication database
  - Return warnings for non-standard dosages

- `validatePathologyOrder(data: unknown): ValidationResult<PathologyOrder>`
  - Validate MBS item exists in database
  - Check specimen type appropriate for test
  - Warn if fasting not marked for fasting-required tests

- `validateSessionData(data: unknown): ValidationResult<SessionData>`
  - Validate entire session
  - Check for required components before submission
  - Return summary of all validation errors

- `sanitizeAustralianTerminology(text: string): {corrected: string, changed: boolean}`
  - Replace non-Australian terms with Australian equivalents
  - Suggest corrections to user
  - Return summary of changes made

#### 7. `/emr-frontend/src/utils/validation-formatting.ts` (60+ lines)
- `formatValidationError(error: ZodError): FormattedError[]`
  - Convert Zod errors to user-friendly messages
  - Group errors by field
  - Sort by severity

- `getErrorColor(severity: ErrorSeverity): string`
  - Map severity to Tailwind color classes

- `getErrorIcon(errorType: string): React.ReactNode`
  - Map error types to appropriate icons

#### 8. `/emr-frontend/src/types/validation.types.ts` (80+ lines)
```typescript
type ValidationResult<T> = {
  success: boolean;
  data?: T;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  parseTime: number; // milliseconds
};

type ValidationError = {
  field: string; // e.g., "subjective.chiefComplaint"
  message: string;
  type: 'required' | 'format' | 'range' | 'logic' | 'safety';
  severity: 'error' | 'warning' | 'info';
  suggestedValue?: string;
};

type ValidationWarning = {
  field: string;
  message: string;
  suggestedAction?: string;
};
```

### Configuration Files

#### 9. `/emr-frontend/src/config/validation.config.ts` (50+ lines)
- Export all schema instances
- Validation timeout: 50ms max
- Character limits
- Enum definitions

#### 10. `/emr-frontend/src/__tests__/schemas/*.test.ts` (500+ lines total)
- **soap-note.schema.test.ts**: 80+ test cases
  - Valid complete SOAP note
  - Each section minimum length violations
  - Character limit violations
  - Missing required fields
  - Invalid enum values
  - Invalid dates/UUIDs
  - Each test <2ms execution

- **prescription.schema.test.ts**: 100+ test cases
  - Valid prescriptions (10+ variants)
  - PBS code format violations (5+ variants)
  - Dose format violations
  - Quantity range violations
  - Repeat violations (>5)
  - Invalid routes/frequencies
  - Allergy matching tests
  - Australian terminology tests (20+ drug names)
  - Duplicate detection
  - Each test <2ms execution

- **pathology-order.schema.test.ts**: 60+ test cases
  - Valid orders (5+ variants)
  - MBS item number format violations
  - Specimen type validation
  - Fasting requirement checks
  - Collection date validation
  - Panel definitions
  - Each test <2ms execution

- **laboratory-tests.schema.test.ts**: 40+ test cases
  - Valid result entries
  - Critical value detection (hemoglobin, potassium, glucose, troponin)
  - Reference range validation
  - Date ordering validation

- **composite.schema.test.ts**: 30+ test cases
  - Complete valid session data
  - Session data with multiple errors
  - Error batching and reporting

---

## Detailed Requirements

### Requirement 1: <50ms Validation Response Time

**Specification:**
All schema validations must complete in <50ms, measured from input to validation result. This ensures real-time feedback as user types.

**Implementation Strategy:**
- Use Zod's `.parse()` method (not `.parseAsync()`)
- Synchronous-only validators, no async operations
- Cache compiled schemas in module exports
- Profile with performance markers in each validator
- Return validation results immediately

**Acceptance Criteria:**
- [ ] All 100+ test cases pass in <2ms per test (total <200ms for entire suite)
- [ ] Performance benchmarks show <50ms validation for complex SOAP notes
- [ ] No async operations in validation path
- [ ] Validation time logged and reported in development mode

### Requirement 2: Australian Terminology Enforcement

**Specification:**
Enforce Australian medical terminology per AMC Clinical Examination standards. Reject non-Australian terms with corrections offered.

**Drug Name Examples:**
- ✅ paracetamol → ❌ acetaminophen
- ✅ adrenaline OR epinephrine → ❌ neither (both allowed)
- ✅ salbutamol → ❌ albuterol
- ✅ methotrexate → ❌ methotrexate (acceptable)
- ✅ Co-amoxiclav → ❌ Augmentin (brand not generic)
- ✅ trimethoprim-sulfamethoxazole → ❌ sulfamethoxazole-trimethoprim

**Implementation:**
- Database of 500+ drug name corrections
- Case-insensitive matching
- Suggest correction in validation error
- Allow override with "use non-standard term" checkbox

**Acceptance Criteria:**
- [ ] 100+ Australian drug names correctly validated
- [ ] Non-Australian terms rejected with suggestion
- [ ] Terminology validation <5ms overhead
- [ ] Documentation of all accepted/rejected terms

### Requirement 3: PBS Code Format Validation

**Specification:**
PBS codes must match format \d{4}[A-Z], e.g., "1234A". Australia's Pharmaceutical Benefits Scheme uses this format.

**Valid Examples:**
- 0001A, 0123B, 9999Z
- **Invalid**: 123A (only 3 digits), 12345A (5 digits), 1234a (lowercase), 1234 (no letter)

**Reference Database:**
- Cross-check against sample PBS dataset with 4,000+ medications
- Flag if PBS code not found (warning, not error)
- Warn if code expired or requires authority

**Acceptance Criteria:**
- [ ] All valid PBS codes pass
- [ ] All invalid PBS codes rejected with clear message
- [ ] Regex tested against 50+ examples
- [ ] Sample dataset integration tested

### Requirement 4: MBS Item Number Validation

**Specification:**
MBS item numbers must be exactly 5 digits (00001-99999). Medicare Benefits Schedule item numbers follow this format.

**Valid Examples:**
- 00001, 10234, 99999
- **Invalid**: 1234 (4 digits), 100000 (6 digits), 1234A (non-numeric)

**Reference Integration:**
- Sample dataset of 100+ common MBS items
- Checksum validation if available
- Warn if item rarely used

**Acceptance Criteria:**
- [ ] All valid 5-digit numbers pass
- [ ] All invalid formats rejected
- [ ] Sample dataset has 100+ items
- [ ] Validation <1ms for single item

### Requirement 5: Comprehensive Test Coverage

**Specification:**
Minimum 100+ test cases covering all validation scenarios. Each test executes in <2ms.

**Test Categories:**
1. **Valid Data Tests (15 tests)**
   - Complete valid SOAP notes (5 variants)
   - Complete valid prescriptions (5 variants)
   - Complete valid pathology orders (5 variants)

2. **Format Violation Tests (25 tests)**
   - PBS codes: 5 variants of invalid format
   - MBS items: 5 variants of invalid format
   - Doses: 5 variants of invalid format
   - Dates/UUIDs: 5 variants of invalid format
   - Routes/frequencies: 5 variants of invalid format

3. **Range Violation Tests (20 tests)**
   - Character limits: too short (5 tests), too long (5 tests)
   - Quantity ranges: out of bounds (5 tests)
   - Repeats >5: exceeds limit (5 tests)

4. **Required Field Tests (15 tests)**
   - Missing each required field in SOAP sections
   - Missing required prescription fields
   - Missing required pathology fields

5. **Logic/Safety Tests (15 tests)**
   - Allergy conflicts with prescribed medication
   - Drug interactions (Warfarin + Aspirin)
   - Non-Australian terminology
   - Future-dated prescriptions
   - Collection date after analysis date

6. **Batch Processing Tests (10 tests)**
   - Multiple prescriptions in single session
   - Duplicate detection
   - Composite schema validation
   - Error aggregation and reporting

7. **Performance Tests (5 tests)**
   - Validate large SOAP notes (2000 char fields)
   - Validate session with 20 prescriptions
   - Validate session with 30 pathology tests
   - Benchmark suite execution time

**Acceptance Criteria:**
- [ ] 100+ tests written and passing
- [ ] 95%+ code coverage for schema files
- [ ] All tests execute <2ms per test
- [ ] Performance benchmarks documented
- [ ] Tests organized in logical groups with descriptive names

---

## Acceptance Criteria

### Functionality
- [ ] All 5 schema files (soap-note, prescription, pathology, laboratory, composite) created and exported
- [ ] soapNoteSchema validates all 4 sections with correct min/max lengths
- [ ] prescriptionSchema validates PBS codes and enforces Australian terminology
- [ ] pathologyOrderSchema validates MBS items (5 digits)
- [ ] australianTerminologySchema rejects non-Australian terms with suggestions
- [ ] All schemas compile without TypeScript errors
- [ ] Composite schema validates complete session data

### Performance
- [ ] All validations complete in <50ms
- [ ] Test suite runs in <200ms (100 tests, avg 2ms per test)
- [ ] No async operations in validation path
- [ ] Memory usage <10MB for schema compilation

### Testing
- [ ] 100+ test cases implemented
- [ ] Coverage ≥95% for all schema files
- [ ] All edge cases tested (empty strings, null values, boundary values)
- [ ] Performance tests pass (<2ms per test)
- [ ] Australian terminology tests (20+ drugs)

### Code Quality
- [ ] Zero TypeScript errors (`npm run type-check`)
- [ ] All code follows project style guide
- [ ] Comprehensive JSDoc comments on all exported functions
- [ ] README documentation for each schema
- [ ] Error messages are user-friendly and actionable

### Integration
- [ ] Schemas can be imported and used in React components
- [ ] ValidationResult type fully specified and exported
- [ ] Error formatting utilities available for UI display
- [ ] Composable with larger validation architecture (Layers 2 & 3)

---

## Testing Requirements

### Unit Tests
```typescript
// Example test structure
describe('soapNoteSchema', () => {
  it('should validate complete valid SOAP note', () => {
    const validNote = {
      subjective: { chiefComplaint: 'Chest pain', hpi: '...' },
      objective: { vitals: {...}, systems: [...] },
      assessment: { diagnosis: 'J45.9', reasoning: '...' },
      plan: { investigations: [], prescriptions: [], referrals: [] }
    };
    const result = validateSOAPNote(validNote);
    expect(result.success).toBe(true);
  });

  it('should reject chief complaint <5 chars', () => {
    const invalid = { subjective: { chiefComplaint: 'Pain' } };
    const result = validateSOAPNote(invalid);
    expect(result.success).toBe(false);
    expect(result.errors[0].field).toBe('subjective.chiefComplaint');
  });
});
```

### Integration Tests
- Validate complete session data (all 4 components)
- Test composition of schemas
- Verify error batching and reporting

### Performance Tests
```typescript
describe('validation performance', () => {
  it('should validate SOAP note in <50ms', () => {
    const start = performance.now();
    validateSOAPNote(largeValidNote);
    const duration = performance.now() - start;
    expect(duration).toBeLessThan(50);
  });
});
```

### Type Safety Tests
```typescript
// Ensure TypeScript catches misuse
const result = validateSOAPNote({...});
if (result.success) {
  const note: SOAPNote = result.data; // Should compile
  console.log(note.subjective.chiefComplaint); // OK
}
```

---

## Reference PRD Sections

### Backend API PRD
**Section**: Layer 1: Client-Side Validation (Zod)
**Link**: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md`

### Validation Rules
**Link**: `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md`
**Sections**:
- Layer 1: Client-Side Validation (Zod)
- Australian Terminology Enforcement
- PBS/MBS Format Rules

---

## Agent OS Delegation Prompt

```markdown
## TASK: Implement Client-Side Validation Layer (Zod Schemas)

### Context
You are implementing Layer 1 of a 3-layer validation architecture for an EMR practice system. This layer must:
1. Validate SOAP notes, prescriptions, pathology orders, and lab tests
2. Enforce Australian medical terminology (AMC Clinical Examination standards)
3. Complete all validations in <50ms
4. Provide 100+ test cases with 95%+ code coverage
5. Follow the project constraints in PROJECT_CONSTRAINTS.md

### Pre-Implementation Checklist
- [ ] Read PROJECT_CONSTRAINTS.md (esp. sections on medical accuracy and Australian compliance)
- [ ] Review `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md`
- [ ] Review Phase 1 component structure in `/emr-frontend/src/components/cerner/`
- [ ] Study Zod patterns in existing codebase (if any)

### Deliverables

1. **Schema Files (5 files)**
   - `/emr-frontend/src/schemas/soap-note.schema.ts`: 180+ lines
     - Validate subjective (min 50 chars), objective (min 50 chars), assessment (min 30 chars), plan (min 30 chars)
     - Include medical history, medications, allergies arrays
     - All fields required for final submission

   - `/emr-frontend/src/schemas/prescription.schema.ts`: 160+ lines
     - PBS code format: \d{4}[A-Z] (e.g., "1234A")
     - Dose format: /^\d+(\.\d+)?\s*(mg|g|mcg|mL|units)$/
     - Quantity: 1-999, repeats: 0-5 max
     - Indication: min 5 chars
     - Australian terminology enforcement

   - `/emr-frontend/src/schemas/pathology-order.schema.ts`: 140+ lines
     - MBS item: exactly 5 digits (00001-99999)
     - Specimen types: blood, urine, CSF, saliva, tissue, swab, stool
     - Fasting requirements for lipids/UEC
     - Urgency: routine/urgent/emergency

   - `/emr-frontend/src/schemas/laboratory-tests.schema.ts`: 120+ lines
     - Test results: code, name, value, unit, reference range
     - Critical value detection (hemoglobin, potassium, glucose, troponin)
     - Status: normal/abnormal/critical/pending

   - `/emr-frontend/src/schemas/composite.schema.ts`: 80+ lines
     - Validates entire session (SOAP + prescriptions + pathology + labs)

2. **Utility Files (3 files)**
   - `/emr-frontend/src/utils/schema-validators.ts`: 100+ lines
     - Exports: validateSOAPNote(), validatePrescription(), validatePathologyOrder(), validateSessionData()
     - Each returns ValidationResult<T> with success, data, errors, warnings, parseTime
     - All operations <50ms

   - `/emr-frontend/src/utils/validation-formatting.ts`: 60+ lines
     - formatValidationError(): Convert Zod errors to user-friendly format
     - getErrorColor(), getErrorIcon() for UI display

   - `/emr-frontend/src/types/validation.types.ts`: 80+ lines
     - ValidationResult<T>, ValidationError, ValidationWarning types
     - ErrorSeverity enum

3. **Config & Tests (2 files + test directory)**
   - `/emr-frontend/src/config/validation.config.ts`: Export all schemas, constants
   - `/emr-frontend/src/__tests__/schemas/`: 500+ lines of tests
     - soap-note.schema.test.ts (80 tests)
     - prescription.schema.test.ts (100 tests including 20+ Australian terminology tests)
     - pathology-order.schema.test.ts (60 tests)
     - laboratory-tests.schema.test.ts (40 tests)
     - composite.schema.test.ts (30 tests)

### Critical Constraints

1. **Performance**: ALL validations <50ms, test suite <200ms total
   - Use only synchronous validation (no async)
   - No I/O in validation path
   - Test each case: <2ms per test

2. **Australian Compliance**:
   - REJECT non-Australian terms with suggestions (paracetamol not acetaminophen)
   - 100+ Australian drug names validated
   - MBS item numbers (5 digits), PBS codes (\d{4}[A-Z])
   - Use AMC Clinical Examination standards, NOT ICRP

3. **Testing Requirements**:
   - 100+ test cases minimum
   - 95%+ code coverage
   - Performance tests included
   - All tests <2ms per test
   - Edge cases: empty strings, null values, boundary values

4. **Type Safety**:
   - 0 TypeScript errors (`npm run type-check`)
   - Full inference for ValidationResult<T>
   - Proper use of Zod's type system

### Australian Terminology Examples to Implement

Drug Names (enforce these):
- paracetamol ✅ / acetaminophen ❌
- adrenaline ✅ (or epinephrine) / neither ❌
- salbutamol ✅ / albuterol ❌
- methotrexate ✅ / methotrexate ✅ (same in both)
- Co-amoxiclav ✅ / Augmentin (brand) ❌
- trimethoprim-sulfamethoxazole ✅

Units & Formats:
- mL not cc
- mmol/L not mEq/L for potassium
- g/dL not g/100mL for hemoglobin

### Validation Checklist (Agent Must Complete Before Returning)

- [ ] All 5 schema files created with correct structure
- [ ] SOAP note schema validates 4 sections with min/max lengths
- [ ] Prescription schema enforces PBS code format (\d{4}[A-Z])
- [ ] Pathology schema validates MBS (5 digits exactly)
- [ ] Composite schema validates complete session
- [ ] 100+ test cases written (at least 20 for Australian terminology)
- [ ] All tests pass: npm test -- --coverage
- [ ] Coverage ≥95%: npm test -- --coverage
- [ ] TypeScript clean: npm run type-check (0 errors)
- [ ] Performance: All validations <50ms, test suite <200ms
- [ ] No async operations in validation path
- [ ] Error messages are user-friendly and actionable
- [ ] Schemas importable in React components
- [ ] ValidationResult type properly typed and exported
- [ ] All exported functions documented with JSDoc

### Success Criteria (PM Will Validate)
- 0 TypeScript errors
- 100+ tests passing
- ≥95% coverage
- <50ms validation time
- Proper Australian terminology enforcement
- Ready for Layer 2 (Python rule validators) to consume these types

### File Structure to Verify
```
emr-frontend/src/
├── schemas/
│   ├── soap-note.schema.ts
│   ├── prescription.schema.ts
│   ├── pathology-order.schema.ts
│   ├── laboratory-tests.schema.ts
│   └── composite.schema.ts
├── utils/
│   ├── schema-validators.ts
│   ├── validation-formatting.ts
│   └── validation.types.ts (or in types/)
├── types/
│   └── validation.types.ts
├── config/
│   └── validation.config.ts
├── constants/
│   └── australian-terminology.ts (if separate)
└── __tests__/
    └── schemas/
        ├── soap-note.schema.test.ts
        ├── prescription.schema.test.ts
        ├── pathology-order.schema.test.ts
        ├── laboratory-tests.schema.test.ts
        └── composite.schema.test.ts
```

### Next Steps After Completion
- Layer 2 (Python validators) will consume these types
- Layer 3 (Claude AI) will validate clinical reasoning
- Unified API endpoint will orchestrate all layers

### Questions Before Starting?
Contact PM with clarifications on:
- Specific Australian terminology requirements
- PBS/MBS code format variations
- Performance budget allocation across layers
```

---

## Implementation Notes

### Architecture Decisions

1. **Synchronous-Only Validation**
   - Client-side must be instant (no API calls)
   - Server-side rule validation happens in Layer 2
   - AI validation happens in Layer 3

2. **Error Message Strategy**
   - Show field-level errors in UI
   - Suggest corrections for Australian terminology
   - Batch multiple errors for submission
   - Use severity levels (error vs. warning)

3. **Type Export Strategy**
   - Export both Zod schemas and TypeScript types
   - `type SOAPNote = z.infer<typeof soapNoteSchema>`
   - Makes frontend components strongly typed

4. **Testing Organization**
   - One test file per schema
   - Group tests by category (valid, format, range, logic, safety)
   - Performance tests in separate describe block
   - Mock data in `__fixtures__` directory if reused

### Common Pitfalls to Avoid

1. **Don't use async validation**
   - No API calls to check PBS codes (do in Layer 2)
   - No database lookups (do in backend)
   - Keep client-side instant

2. **Don't hardcode medication lists**
   - Use sample data for development
   - Real list comes from backend database
   - Let Layer 2 validate against real PBS

3. **Don't skip Australian terminology**
   - Project explicitly requires AMC standards
   - Not ICRP standards (mentioned in constraints)
   - Document all enforced terms in README

4. **Don't ignore TypeScript strictness**
   - `strict: true` in tsconfig.json
   - No `any` types in validation code
   - Full type inference for ValidationResult<T>

### Performance Optimization Tips

1. **Schema Compilation**
   - Compile schemas once at module load
   - Export compiled instances, not factories
   ```typescript
   // GOOD
   export const soapNoteSchema = z.object({...});

   // BAD
   export const getSoapNoteSchema = () => z.object({...});
   ```

2. **Regex Optimization**
   - Pre-compile regexes as schema constants
   - Use simpler patterns where possible (PBS code doesn't need complex regex)

3. **Test Performance**
   - Use `performance.mark()` and `performance.measure()` API
   - Profile in real test environment
   - Set baseline expectations early

---

## Progress Tracking

### Milestone 1: Schema Foundation (2 hours)
- [ ] Create base schema structure
- [ ] Implement SOAP note schema
- [ ] Implement prescription schema

### Milestone 2: Pathology & Laboratory (1.5 hours)
- [ ] Implement pathology order schema
- [ ] Implement laboratory test schema
- [ ] Implement composite schema

### Milestone 3: Australian Terminology (1 hour)
- [ ] Create terminology enforcement schema
- [ ] Define 100+ drug name corrections
- [ ] Add validation tests for terminology

### Milestone 4: Testing & Optimization (1.5 hours)
- [ ] Write 100+ test cases
- [ ] Achieve 95%+ code coverage
- [ ] Optimize to <50ms validation time
- [ ] Document all test cases

---

## Files to Create/Modify

### Create
```
/emr-frontend/src/schemas/
  ├── soap-note.schema.ts
  ├── prescription.schema.ts
  ├── pathology-order.schema.ts
  ├── laboratory-tests.schema.ts
  └── composite.schema.ts

/emr-frontend/src/utils/
  ├── schema-validators.ts
  ├── validation-formatting.ts

/emr-frontend/src/types/
  └── validation.types.ts

/emr-frontend/src/config/
  └── validation.config.ts

/emr-frontend/src/__tests__/schemas/
  ├── soap-note.schema.test.ts
  ├── prescription.schema.test.ts
  ├── pathology-order.schema.test.ts
  ├── laboratory-tests.schema.test.ts
  └── composite.schema.test.ts

/emr-frontend/src/constants/
  └── australian-terminology.ts (optional, if large)
```

### Modify
```
/emr-frontend/tsconfig.json
  - Ensure strict: true if not set

/emr-frontend/package.json
  - Verify Zod ^3.22.4 installed
  - Verify TypeScript 5.3+ installed
```

---

**Status**: ⏳ Ready for Agent Delegation
**Next Task**: TASK_2.2_PBS_MBS_Validators.md (depends on TASK_2.1 completion)
**Review Checklist**: PM validates before moving to TASK_2.2
