# TASK 1.1: Complete Cerner Components

**Phase**: Phase 1 - Frontend Completion
**Estimated Hours**: 12 hours
**Dependencies**: Frontend environment setup, React 18 + TypeScript configured, Tailwind CSS installed
**Agent Type**: `frontend-react-expert`
**Status**: ⏳ Not Started

---

## Overview

Complete implementation of all Cerner PowerChart UI components with full functionality. This task focuses on creating the dark-themed Cerner interface with 7 core modules (Dashboard, Patient Chart, Progress Notes, Medications, Orders, Vitals, Alerts). Includes enhanced MedicationOrderEntry with PBS search and dosage calculator, PathologyOrderForm with MBS validation, and refinement of existing sidebar/header components.

---

## Deliverables

### New Components to Create

- `/emr-frontend/src/components/cerner/MedicationOrderEntry.tsx` (350+ lines)
  - PBS medication search functionality
  - Dose calculator with age/weight adjustments
  - Quantity and repeats validation
  - Drug interaction warnings
  - Indication field with character counter

- `/emr-frontend/src/components/cerner/PathologyOrderForm.tsx` (280+ lines)
  - MBS item number lookup
  - Common test panel buttons (FBC, UEC, LFT, etc.)
  - Indication requirement validation
  - Urgency selection (Routine/Urgent/Emergency)
  - Auto-population of patient demographics

- `/emr-frontend/src/components/cerner/DashboardModule.tsx` (250+ lines)
  - Key metrics cards (sessions completed, avg score, typing speed)
  - Quick access buttons for modules
  - Recent sessions list
  - Performance charts

- `/emr-frontend/src/components/cerner/PatientChartModule.tsx` (300+ lines)
  - Tabbed interface (Demographics, History, Vitals, Allergies, Medications)
  - Patient summary card
  - Edit functionality for demographics
  - Allergy alert display (red background)

- `/emr-frontend/src/components/cerner/ProgressNoteModule.tsx` (280+ lines)
  - SOAP note editor with 4 sections
  - Character count for each section
  - Auto-save indicator
  - Validation feedback (min 50 chars per section)

### Enhancements to Existing Components

- `/emr-frontend/src/components/cerner/CernerSidebar.tsx` - Refinement
  - Add module color indicators
  - Implement active state styling
  - Add keyboard navigation support
  - Tooltip on hover

- `/emr-frontend/src/components/cerner/CernerHeader.tsx` - Refinement
  - Add patient info display
  - Session timer
  - Quick action buttons (Save, Submit, Help)

- `/emr-frontend/src/components/cerner/PatientBanner.tsx` - Refinement
  - Display allergies with red alert background
  - Show critical info flags
  - Add patient MRN and age

- `/emr-frontend/src/components/cerner/SOAPNoteEditor.tsx` - Enhancement
  - Implement real-time validation display
  - Add auto-save every 30 seconds
  - Character counter for each section
  - Typing metrics display

### Utility & Constants

- `/emr-frontend/src/constants/cerner-modules.ts` (50 lines)
  - Module definitions with colors and icons
  - Navigation structure

- `/emr-frontend/src/constants/pbs-sample-data.ts` (100 lines)
  - Sample PBS medication list for search
  - Dose ranges for common medications
  - Allergy categories

- `/emr-frontend/src/constants/mbs-sample-data.ts` (80 lines)
  - Common MBS item numbers
  - Test panel definitions

---

## Detailed Requirements

### Requirement 1: MedicationOrderEntry Component

**Specification:**

```typescript
interface MedicationOrderEntryProps {
  patientAge: number;
  patientWeight: number;
  patientAllergies: string[];
  currentMedications: string[];
  onSubmit: (prescription: Prescription) => void;
}

interface Prescription {
  medication: string;
  dose: string;
  unit: string;
  frequency: string;
  quantity: number;
  repeats: number;
  indication: string;
  pbs_item?: string;
  requires_authority?: boolean;
}
```

**Features:**

- **PBS Search**: Debounced search (300ms) against 4,000+ Australian medications
  - Show search results dropdown with medication name, strength, PBS status
  - Highlight if PBS-listed or requires streamlined authority
  - Click to select, populate dose field

- **Dosage Calculator**:
  - Input: medication name, patient age, weight
  - Output: recommended dose range with units
  - Support age-based and weight-based calculations
  - Show renal/hepatic adjustment warnings if indicated

- **Validation**:
  - Quantity: 1-999 (max 100 without warning)
  - Repeats: 0-5 (max 5 repeats per PBS rules)
  - Indication: Minimum 5 characters required
  - Allergy check: Cross-reference against patient allergies

- **Visual Feedback**:
  - Green checkmark for valid fields
  - Red border + error message for invalid
  - Yellow warning triangle for cautions (quantity >100, etc.)
  - Blue info box for drug interactions

**Acceptance Criteria:**
- [ ] PBS search returns results within 500ms
- [ ] Dosage calculator shows appropriate ranges for common medications
- [ ] Validation prevents submission of invalid prescriptions
- [ ] Quantity/repeats validation enforces PBS rules
- [ ] Allergy warnings display prominently (red background)
- [ ] Form can be cleared and reset without page reload

---

### Requirement 2: PathologyOrderForm Component

**Specification:**

```typescript
interface PathologyOrderFormProps {
  patientDemographics: {
    age: number;
    gender: 'M' | 'F';
    mbs_number?: string;
  };
  onSubmit: (order: PathologyOrder) => void;
}

interface PathologyOrder {
  test_type: string;
  mbs_item: string;
  indication: string;
  urgency: 'Routine' | 'Urgent' | 'Emergency';
  special_requirements?: string;
}
```

**Features:**

- **Test Panel Buttons**: Quick buttons for common panels
  - Full Blood Count (FBC)
  - Urea, Electrolytes, Creatinine (UEC/U&E)
  - Liver Function Tests (LFT)
  - Coagulation Screen
  - Blood Glucose
  - Lipid Profile
  - Bone Profile
  - Click to auto-populate indication field template

- **MBS Lookup**:
  - Field to enter or search MBS item number
  - Display item description and fee
  - Show rebate amount
  - Validate MBS item is current

- **Indication Field**:
  - Required field (validation error if empty)
  - Suggest common indications as dropdown
  - Character counter (max 500 characters)

- **Urgency Selection**:
  - Radio buttons or dropdown: Routine / Urgent / Emergency
  - Default to "Routine"
  - Show clinical rationale field for Urgent/Emergency

**Acceptance Criteria:**
- [ ] All common test panels have pre-configured buttons
- [ ] MBS item validation prevents invalid items
- [ ] Indication field is required and validated
- [ ] Urgency selection is mandatory
- [ ] Form prevents submission without all required fields
- [ ] Form resets properly when "Clear" button clicked

---

### Requirement 3: Enhanced CernerSidebar Component

**Current State**: Basic sidebar with module list
**Enhancement Needed**:

- **Module Color Indicators**: Each module has distinct color
  - Dashboard: Blue (#3498db)
  - Patient Chart: Green (#27ae60)
  - Progress Notes: Purple (#9b59b6)
  - Medications: Orange (#e67e22)
  - Orders: Red (#e74c3c)
  - Vitals: Teal (#16a085)
  - Alerts: Yellow (#f39c12)

- **Active State Styling**:
  - Left border (4px) filled with module color
  - Background highlight (#34495e)
  - Bold text

- **Keyboard Navigation**:
  - Arrow keys to move between modules
  - Enter to activate module
  - Tab to focus

- **Tooltips**:
  - Show on hover delay 500ms
  - Display module name and keyboard shortcut

- **Icons**:
  - Use Lucide icons matching module function
  - Size 20px
  - Color changes on hover/active

**Acceptance Criteria:**
- [ ] Sidebar renders with all 7 modules visible
- [ ] Active module highlighted correctly
- [ ] Keyboard navigation works smoothly
- [ ] Tooltips appear on hover (500ms delay)
- [ ] Icons scale and color appropriately
- [ ] Sidebar scrolls if content overflows

---

### Requirement 4: Enhanced PatientBanner Component

**Current State**: Minimal patient header
**Enhancement Needed**:

- **Critical Information Display**:
  - Patient Name (large, bold)
  - Age and Gender
  - MRN (Medical Record Number)
  - Date of Birth

- **Allergy Alert System**:
  - If allergies present: RED background (#e74c3c)
  - Display: "ALLERGIES: Penicillin, Aspirin"
  - Font-weight: bold
  - Icon: AlertTriangle (Lucide)

- **Critical Flags**:
  - Display any critical patient flags
  - Example: "NKDA" (No Known Drug Allergies) in green
  - Example: "DNR" (Do Not Resuscitate) in red

- **Status Indicators**:
  - Current location (Ward, ED, ICU, etc.)
  - Current status (Active, Discharged, Archived)

**Styling**:
- Use Cerner color scheme (#2c3e50 background)
- White text on dark background
- Clear visual hierarchy
- Red sections for critical information

**Acceptance Criteria:**
- [ ] Patient name displays prominently
- [ ] Allergy section displays with red background when allergies present
- [ ] MRN and age displayed clearly
- [ ] Critical flags highlighted appropriately
- [ ] Component responsive on smaller screens
- [ ] No console warnings or errors

---

### Requirement 5: Enhanced SOAPNoteEditor Component

**Current State**: Basic text input fields
**Enhancement Needed**:

- **Real-Time Validation Display**:
  - Below each section, show character count
  - Display validation status: ✓ (green) or ✗ (red)
  - Show minimum character requirement (e.g., "50/50 characters")
  - Validation feedback text in tooltip on hover

- **Auto-Save Functionality**:
  - Debounce 30 seconds after last keystroke
  - Display "Saving..." indicator while saving
  - Show "Saved at HH:MM" message when complete
  - Cancel auto-save on component unmount

- **Character Counters**:
  - Below Subjective field: "150/2000"
  - Below Objective field: "120/2000"
  - Below Assessment field: "85/1000"
  - Below Plan field: "95/1500"
  - Red text if exceeding limit

- **Typing Metrics Display**:
  - Small card showing:
    - Words per minute (WPM)
    - Characters typed
    - Time elapsed
    - Accuracy percentage (if applicable)

**Acceptance Criteria:**
- [ ] Auto-save triggers after 30 seconds of inactivity
- [ ] Character counters display and update in real-time
- [ ] Validation status shows correctly (green checkmark = valid)
- [ ] Auto-save can be cancelled on unmount
- [ ] Typing metrics display without affecting performance
- [ ] Form content persists after browser refresh

---

## Acceptance Criteria

### Component Quality
- [ ] All components render without console errors or warnings
- [ ] TypeScript compilation produces 0 errors
- [ ] Props properly typed with interfaces
- [ ] PropTypes or TypeScript interfaces document all props

### Functionality
- [ ] MedicationOrderEntry: PBS search works, dosage calculator shows correct ranges
- [ ] PathologyOrderForm: Test panels populate correctly, validation prevents invalid submissions
- [ ] CernerSidebar: Active state styling works, keyboard navigation functions
- [ ] PatientBanner: Allergies display with red background, critical flags highlighted
- [ ] SOAPNoteEditor: Auto-save triggers every 30s, character counters display

### Styling & Theming
- [ ] All components use Cerner color scheme (#2c3e50, #3498db)
- [ ] Responsive design: works on 1024px and larger screens
- [ ] Tailwind classes used consistently
- [ ] No inline styles except for dynamic theming
- [ ] Dark theme applied consistently

### Validation & Safety
- [ ] Patient allergies prevent prescription of allergenic medications
- [ ] PBS rules enforced (max 5 repeats, valid items only)
- [ ] MBS items validated before form submission
- [ ] SOAP note minimum character requirements enforced
- [ ] Indication field required for prescriptions/orders

### Testing
- [ ] Unit tests written for all components (>80% coverage)
- [ ] Test cases cover happy path and error scenarios
- [ ] Test cases cover validation edge cases
- [ ] All tests pass with 0 failures
- [ ] Integration tests verify component interaction

### Performance
- [ ] PBS search debounced at 300ms (no excessive API calls)
- [ ] Auto-save debounced at 30 seconds
- [ ] Components render within 16ms frame budget
- [ ] No memory leaks on component unmount
- [ ] Smooth animations (60fps)

---

## Testing Requirements

### Unit Tests

#### MedicationOrderEntry.test.tsx
```typescript
// Test PBS search functionality
test('PBS search returns results within 500ms', () => { });
test('PBS search handles no results gracefully', () => { });

// Test dosage calculator
test('Dosage calculator shows weight-based dose range', () => { });
test('Dosage calculator shows age-based adjustment', () => { });

// Test validation
test('Form prevents submission with invalid dose', () => { });
test('Allergy check prevents prescription of allergenic drug', () => { });
test('Repeats validation enforces max 5 repeats', () => { });
test('Indication field required for PBS compliance', () => { });

// Test form submission
test('Form submits with all required fields', () => { });
test('Form clears when clear button clicked', () => { });
```

#### PathologyOrderForm.test.tsx
```typescript
// Test panel buttons
test('FBC button pre-populates indication field', () => { });
test('UEC button pre-populates with standard indication', () => { });

// Test validation
test('MBS item validation prevents invalid items', () => { });
test('Indication field required', () => { });
test('Urgency selection mandatory', () => { });

// Test form submission
test('Form prevents submission without indication', () => { });
test('Form submits successfully with all fields', () => { });
```

#### CernerSidebar.test.tsx
```typescript
// Test rendering
test('All 7 modules render with correct colors', () => { });
test('Active module highlighted correctly', () => { });

// Test interaction
test('Clicking module calls onNavigate', () => { });
test('Keyboard arrow keys navigate between modules', () => { });
test('Keyboard Enter activates module', () => { });

// Test styling
test('Active module shows correct border color', () => { });
test('Icons render with correct size and color', () => { });
```

### Integration Tests

#### EMR Session Integration
- [ ] Components work together in full EMR session
- [ ] Data flows correctly between components
- [ ] Sidebar navigation updates main content
- [ ] Patient banner updates when patient changes
- [ ] Validation feedback appears in feedback panel

---

## Reference PRD Sections

- **Master EMR PRD**: Section 1 (Simulated EMR Environments - Cerner)
  - Location: `/home/dev/Development/irStudy/emr-practice-system/prd/00_MASTER_EMR_PRD.md`
  - Sections: Lines 42-46 (Cerner features), Lines 154-159 (Frontend components)

- **Styling & Functionality PRD**: Sections 2.1 (Cerner color palette), 3.1 (Cerner sidebar)
  - Location: `/home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md`
  - Sections: Lines 56-97 (Colors), Lines 214-300 (Sidebar styling)

- **Validation Rules**: Section 6 (SOAP Note Validation Rules), Section 7 (Prescription Rules)
  - Location: `/home/dev/Development/irStudy/emr-practice-system/prd/00_MASTER_EMR_PRD.md`
  - Sections: Lines 710-855 (Rule examples)

---

## Agent OS Delegation Prompt

```
Agent Task: Complete Cerner PowerChart UI Components

CRITICAL - Read constraints FIRST:
1. Read /home/dev/Development/irStudy/constraints/README.md completely
2. Read /home/dev/Development/irStudy/CLAUDE.md (project-specific requirements)
3. Search for existing React patterns in /home/dev/Development/irStudy/frontend/src/components/
4. Reference PRD: /home/dev/Development/irStudy/emr-practice-system/prd/00_MASTER_EMR_PRD.md (lines 42-46, 154-159)
5. Reference styling: /home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md (lines 56-97, 214-300)

CONTEXT:
- This is part of EMR practice system for Australian medical students (ICRP preparation)
- Must follow Australian medical terminology: paracetamol (not acetaminophen), salbutamol (not albuterol)
- TypeScript + React 18 + Tailwind CSS stack
- Cerner theme: Dark background (#2c3e50), blue primary (#3498db)
- PBS compliance critical: max 5 repeats, indication required, allergy checking
- Zero tolerance for TypeScript compilation errors

DELIVERABLES:
1. MedicationOrderEntry.tsx (350+ lines) - PBS search, dosage calculator, validation
2. PathologyOrderForm.tsx (280+ lines) - MBS lookup, test panels, urgency selection
3. DashboardModule.tsx (250+ lines) - Metrics cards, quick access, charts
4. PatientChartModule.tsx (300+ lines) - Tabbed interface, patient summary
5. ProgressNoteModule.tsx (280+ lines) - SOAP editor, validation feedback
6. Enhanced CernerSidebar.tsx - Module colors, active state, keyboard nav
7. Enhanced CernerHeader.tsx - Patient info, session timer, quick actions
8. Enhanced PatientBanner.tsx - Allergies (red), critical flags, MRN
9. Enhanced SOAPNoteEditor.tsx - Auto-save (30s), char counters, validation display
10. Constants: cerner-modules.ts, pbs-sample-data.ts, mbs-sample-data.ts

CRITICAL REQUIREMENTS:
1. Authentication & Security:
   - NEVER hardcode patient data
   - Validate all user inputs before API calls
   - Use environment variables for sensitive data

2. Australian Medical Compliance:
   - Use Australian medication names (paracetamol, not acetaminophen)
   - PBS rules enforced (max 5 repeats, listed items only)
   - MBS item validation
   - NKDA vs allergy clarity

3. Validation Rules:
   - MedicationOrderEntry: Max 5 repeats, indication required, allergy check
   - PathologyOrderForm: MBS item validation, indication required
   - SOAPNoteEditor: Min 50 chars subjective/objective, 30 chars assessment/plan

4. Performance:
   - PBS search debounced 300ms
   - Auto-save debounced 30 seconds
   - Components render <16ms
   - No memory leaks on unmount

5. Testing:
   - Unit tests for all components (80%+ coverage)
   - Happy path + error scenarios
   - Edge case validation testing
   - All tests must pass 100%

VALIDATION CHECKLIST (self-validate before returning):
- [ ] Read constraints README and CLAUDE.md
- [ ] Searched for existing React patterns in frontend/src
- [ ] 0 TypeScript errors (ran `npm run type-check`)
- [ ] All tests pass with 100% success rate (ran `npm run test`)
- [ ] No console warnings or errors (checked in browser console)
- [ ] PBS search debounced correctly (300ms)
- [ ] Auto-save debounced correctly (30s)
- [ ] Allergy validation prevents prescription of allergenic drugs
- [ ] Max 5 repeats enforced in MedicationOrderEntry
- [ ] MBS item validation enforces valid items only
- [ ] Character counters display correctly and update in real-time
- [ ] Active state styling works in CernerSidebar
- [ ] Keyboard navigation functions in sidebar
- [ ] Red background for allergies in PatientBanner
- [ ] Components render without console errors
- [ ] Styling uses Cerner color scheme correctly
- [ ] All components responsive (1024px+)
- [ ] PropTypes or TypeScript interfaces document all props
- [ ] Memory cleanup on component unmount verified

ACCEPTANCE CRITERIA (task is only COMPLETE when all pass):
- [ ] All components render without console errors or warnings
- [ ] TypeScript compilation produces 0 errors
- [ ] All unit tests pass (80%+ coverage)
- [ ] MedicationOrderEntry: PBS search works, dosage calculator accurate
- [ ] PathologyOrderForm: Test panels work, validation prevents invalid submissions
- [ ] CernerSidebar: Active state, keyboard nav, tooltips function
- [ ] PatientBanner: Allergies display red, critical flags highlighted
- [ ] SOAPNoteEditor: Auto-save 30s, char counters display, validation shows
- [ ] All components use Cerner color scheme (#2c3e50, #3498db)
- [ ] Responsive design works (1024px+)
- [ ] PBS rules enforced (max 5 repeats, indication required, allergy check)
- [ ] MBS items validated
- [ ] Performance metrics met (search 300ms, auto-save 30s, render 16ms)

Return JSON summary when complete:
{
  "status": "COMPLETE",
  "components_created": [...],
  "test_results": "X/X passing",
  "typescript_errors": 0,
  "console_errors": 0,
  "notes": "..."
}
```

---

## Implementation Notes

### Key Architecture Decisions

1. **Component Composition**: Each module (Dashboard, Patient Chart, Progress Notes, etc.) is a standalone component. CernerSidebar controls navigation between them.

2. **Data Flow**:
   - Patient data flows from parent (EMR session) to all child components
   - Validation results flow from child to parent via callbacks
   - Auto-save persists to localStorage and backend via debounced API call

3. **Validation Strategy**:
   - Layer 1 (Client): Real-time validation (character count, required fields)
   - Layer 2 (Rules): PBS/MBS rules, allergy checking
   - Layer 3 (AI): Backend Claude validation for clinical accuracy

4. **Color System**:
   - Use CSS variables (--cerner-primary, --cerner-bg-dark, etc.)
   - Theme-switching: add `data-theme="cerner"` to root element
   - All colors defined in `/src/styles/cerner.css`

### PBS & MBS Data

For MVP, use sample data files (not API calls):
- **pbs-sample-data.ts**: ~400 common medications with dose ranges
- **mbs-sample-data.ts**: ~50 common pathology items with item numbers

Real PBS/MBS APIs can be integrated later.

### Typing Strategy

Use strict TypeScript:
```typescript
interface Prescription {
  medication: string;
  dose: string;
  unit: 'mg' | 'mL' | 'g' | 'mcg' | 'IU';
  frequency: string;
  quantity: number;
  repeats: number; // max 5
  indication: string; // min 5 chars
  pbs_item?: string;
  requires_authority?: boolean;
}
```

### Common Pitfalls to Avoid

1. **Don't** hardcode patient data - always pass via props
2. **Don't** make API calls on every keystroke - use debouncing
3. **Don't** use inline CSS - use Tailwind or CSS modules
4. **Don't** forget to cleanup subscriptions/timers on unmount
5. **Don't** validate only on submit - validate in real-time
6. **Don't** ignore accessibility - use semantic HTML, ARIA labels

### Browser DevTools Tips

- Check React DevTools: verify props flow correctly
- Check Performance tab: ensure render times <16ms
- Check Network tab: verify debounced API calls (30s auto-save = ~1 call per 30s)
- Check Console: should be completely clean, no errors/warnings

---

## Progress Tracking

- **Status**: ⏳ Not Started
- **Start Date**: [Fill when started]
- **End Date**: [Fill when completed]
- **Actual Hours**: [Fill when completed]
- **Blockers**: [Document any blockers encountered]
- **Notes**: [Any important notes during implementation]

### Checkpoint 1: Components Created (Est. 4 hours)
- [ ] MedicationOrderEntry.tsx created with basic structure
- [ ] PathologyOrderForm.tsx created with basic structure
- [ ] Module components created (Dashboard, PatientChart, ProgressNote)
- [ ] All TypeScript interfaces defined

### Checkpoint 2: Functionality Implemented (Est. 6 hours)
- [ ] PBS search functional (300ms debounce)
- [ ] Dosage calculator working
- [ ] PathologyOrderForm validation working
- [ ] CernerSidebar keyboard navigation working
- [ ] SOAPNoteEditor auto-save working (30s debounce)

### Checkpoint 3: Tests & Validation (Est. 2 hours)
- [ ] All unit tests written and passing
- [ ] No TypeScript errors
- [ ] No console errors/warnings
- [ ] Manual testing complete (all features work as expected)
- [ ] Performance metrics verified

---

**Previous Task**: Frontend environment setup
**Next Task**: TASK 1.2 - Complete Epic Components
