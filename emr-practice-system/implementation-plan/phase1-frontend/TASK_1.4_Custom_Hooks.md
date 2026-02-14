# TASK 1.4: Custom Hooks

**Phase**: Phase 1 - Frontend Completion
**Estimated Hours**: 4 hours
**Dependencies**: TASK 1.3 (State Management) complete, React 18, TypeScript
**Agent Type**: `frontend-react-expert`
**Status**: ⏳ Not Started

---

## Overview

Implement 4 custom React hooks that provide specialized functionality for the EMR practice system: `useAutoSave` (debounced auto-saving with cancellation), `useTypingMetrics` (WPM calculation and typing stats), `usePBSSearch` (medication search with debounce), and `useValidation` (progressive 3-layer validation). These hooks encapsulate complex logic and are used across both Cerner and Epic components.

---

## Deliverables

### Custom Hooks to Create

- `/emr-frontend/src/hooks/useAutoSave.ts` (120+ lines)
  - Debounced auto-save with 30s configurable delay
  - Cancel on component unmount
  - Track saving state
  - Handle errors

- `/emr-frontend/src/hooks/useTypingMetrics.ts` (140+ lines)
  - Calculate words per minute (WPM)
  - Track characters typed
  - Calculate accuracy percentage
  - Handle session timing

- `/emr-frontend/src/hooks/usePBSSearch.ts` (160+ lines)
  - Debounced medication search (300ms)
  - Search against 4000+ medications
  - Format results with PBS info
  - Handle loading/error states

- `/emr-frontend/src/hooks/useValidation.ts` (200+ lines)
  - Three-layer validation (L1→L2→L3)
  - Layer 1: Client-side (instant)
  - Layer 2: Rules engine (2-3 seconds)
  - Layer 3: AI validation (5-8 seconds)
  - Progressive feedback display

### Supporting Files

- `/emr-frontend/src/utils/typing-metrics.utils.ts` (100+ lines)
  - WPM calculation algorithms
  - Accuracy calculation
  - Session timing utilities

- `/emr-frontend/src/utils/validation-rules.utils.ts` (150+ lines)
  - SOAP note validation rules
  - Prescription validation rules
  - Pathology validation rules
  - Australian terminology checker

---

## Detailed Requirements

### Requirement 1: useAutoSave Hook

**Specification:**

```typescript
interface useAutoSaveOptions {
  debounceMs?: number;  // default 30000 (30 seconds)
  onSave: () => Promise<void>;
  onError?: (error: Error) => void;
  enabled?: boolean;    // default true
}

interface useAutoSaveReturn {
  isSaving: boolean;
  lastSavedAt?: Date;
  saveError?: Error;
  forceSync: () => Promise<void>;
  cancel: () => void;
  resetError: () => void;
}

function useAutoSave(options: useAutoSaveOptions): useAutoSaveReturn
```

**Features:**

- **Debounced Saving**:
  - Waits 30 seconds after last trigger
  - Cancels pending save if new trigger arrives
  - Only saves if content changed

- **State Tracking**:
  - `isSaving`: true during API call
  - `lastSavedAt`: timestamp of last successful save
  - `saveError`: error from failed save attempts

- **Cleanup**:
  - Automatically cancel on component unmount
  - Handle pending saves gracefully

- **Manual Control**:
  - `forceSync()`: Save immediately
  - `cancel()`: Cancel pending save
  - `resetError()`: Clear error message

- **Error Handling**:
  - Catch API errors
  - Call `onError` callback
  - Don't crash on error

**Usage Example:**

```typescript
const { isSaving, lastSavedAt, forceSync } = useAutoSave({
  debounceMs: 30000,
  onSave: async () => {
    // Call API to save note
    await api.saveNote(noteContent);
  },
  onError: (error) => {
    console.error('Save failed:', error.message);
    showErrorToast('Failed to save');
  }
});

// In component:
useEffect(() => {
  // Auto-save on content change
  useAutoSave hook will debounce
}, [noteContent]);

return (
  <div>
    {isSaving && <div>Saving...</div>}
    {lastSavedAt && <div>Saved at {lastSavedAt.toLocaleTimeString()}</div>}
    <button onClick={forceSync}>Save Now</button>
  </div>
);
```

**Acceptance Criteria:**
- [ ] Auto-save debounces at 30 seconds
- [ ] Manual `forceSync()` saves immediately
- [ ] `isSaving` flag updates correctly
- [ ] `lastSavedAt` records timestamp
- [ ] Cleanup cancels pending saves on unmount
- [ ] Errors caught and handled gracefully
- [ ] Works with async `onSave` callback
- [ ] No memory leaks or infinite loops

---

### Requirement 2: useTypingMetrics Hook

**Specification:**

```typescript
interface useTypingMetricsOptions {
  enabled?: boolean;
  onMetricsChange?: (metrics: TypingMetrics) => void;
}

interface TypingMetrics {
  wordsPerMinute: number;
  charactersTyped: number;
  timeElapsed: number; // seconds
  accuracy: number; // 0-100 percentage
}

function useTypingMetrics(options?: useTypingMetricsOptions): TypingMetrics
```

**Features:**

- **WPM Calculation**:
  - Characters typed / 5 / minutes elapsed
  - Update every 5 seconds
  - Smooth calculation (no jumps)

- **Character Tracking**:
  - Count total characters typed (letters, numbers, spaces, punctuation)
  - Reset on new session
  - Track deletions separately

- **Session Timing**:
  - Start timer on first keystroke
  - Pause if idle >30 seconds
  - Resume on next keystroke

- **Accuracy Calculation**:
  - Compare typed text to expected text (if available)
  - Calculate percentage correct
  - Default 100% if no comparison text

- **Real-Time Updates**:
  - Update metrics every keystroke
  - Call `onMetricsChange` callback
  - Update store (useEMRSessionStore)

**Usage Example:**

```typescript
const [content, setContent] = useState('');
const metrics = useTypingMetrics({
  enabled: true,
  onMetricsChange: (metrics) => {
    // Update store or display
    useEMRSessionStore.setState({ typingMetrics: metrics });
  }
});

const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
  setContent(e.target.value);
  // Hook automatically updates metrics
};

return (
  <div>
    <textarea value={content} onChange={handleChange} />
    <div>
      WPM: {metrics.wordsPerMinute}
      Characters: {metrics.charactersTyped}
      Time: {metrics.timeElapsed}s
    </div>
  </div>
);
```

**Acceptance Criteria:**
- [ ] WPM calculated correctly
- [ ] Characters typed counted accurately
- [ ] Accuracy calculated (if comparison text provided)
- [ ] Metrics update in real-time
- [ ] Session timer works (starts/pauses/resumes)
- [ ] `onMetricsChange` callback fires on updates
- [ ] Metrics reset on new session
- [ ] No performance impact on typing (smooth input)
- [ ] Handles edge cases (empty text, very fast typing)

---

### Requirement 3: usePBSSearch Hook

**Specification:**

```typescript
interface usePBSSearchOptions {
  debounceMs?: number; // default 300
  minChars?: number;   // default 2
  maxResults?: number; // default 20
}

interface PBSMedication {
  id: string;
  name: string;
  strength: string;
  form: string;
  isListed: boolean;
  requiresAuthority: boolean;
  doseRange?: { min: string; max: string };
}

interface usePBSSearchReturn {
  results: PBSMedication[];
  isLoading: boolean;
  error?: string;
  search: (query: string) => Promise<void>;
  clear: () => void;
}

function usePBSSearch(options?: usePBSSearchOptions): usePBSSearchReturn
```

**Features:**

- **Debounced Search**:
  - 300ms debounce (prevent excessive searches)
  - Minimum 2 characters to search
  - Cancel previous search if new query arrives

- **Search Results**:
  - Return up to 20 results
  - Include medication name, strength, form
  - Flag PBS-listed status
  - Flag if requires streamlined authority

- **Loading State**:
  - `isLoading`: true while searching
  - Display loading indicator to user

- **Error Handling**:
  - Handle search errors gracefully
  - Display error message
  - Allow retry

- **Caching** (optional):
  - Cache recent searches (last 10 queries)
  - Return cached results instantly if available

**Usage Example:**

```typescript
const { results, isLoading, error, search, clear } = usePBSSearch({
  debounceMs: 300,
  maxResults: 20
});

const handleSearch = async (query: string) => {
  if (query.length < 2) {
    clear();
    return;
  }
  await search(query);
};

return (
  <div>
    <input
      type="text"
      placeholder="Search medications..."
      onChange={(e) => handleSearch(e.target.value)}
    />
    {isLoading && <div>Searching...</div>}
    {error && <div className="error">{error}</div>}
    <ul>
      {results.map((med) => (
        <li key={med.id}>
          {med.name} {med.strength}
          {med.requiresAuthority && <span className="badge">Auth Required</span>}
        </li>
      ))}
    </ul>
  </div>
);
```

**Acceptance Criteria:**
- [ ] Search debounces at 300ms
- [ ] Minimum 2 characters enforced
- [ ] Results return within 500ms
- [ ] Max 20 results returned
- [ ] PBS-listed flag displayed correctly
- [ ] Authority requirement flag shown
- [ ] Loading indicator displays during search
- [ ] Errors caught and displayed
- [ ] Clear function empties results
- [ ] No memory leaks from debounced calls
- [ ] Works with sample data (MVP) and API (future)

---

### Requirement 4: useValidation Hook

**Specification:**

```typescript
interface useValidationOptions {
  apiClient?: ValidationAPIClient;
  ragService?: RAGService;
}

interface ValidationLayer {
  layer: number; // 1, 2, or 3
  status: 'pending' | 'in_progress' | 'complete' | 'error';
  errors: ValidationError[];
  warnings: ValidationWarning[];
  info: ValidationInfo[];
}

interface useValidationReturn {
  // Current validation state
  validationLayers: ValidationLayer[];
  currentLayer: number;
  overallValidationStatus: 'invalid' | 'valid_with_warnings' | 'valid';

  // Actions
  validateLayer1: (noteData: SOAPNote) => void; // sync, instant
  validateLayer2: (noteData: SOAPNote) => Promise<void>; // rules engine, 2-3s
  validateLayer3: (noteData: SOAPNote, patientData: PatientData) => Promise<void>; // AI, 5-8s
  validateAll: (noteData: SOAPNote, patientData: PatientData) => Promise<void>;
  clearValidation: () => void;
}

function useValidation(options?: useValidationOptions): useValidationReturn
```

**Features:**

- **Layer 1: Client-Side Validation** (Instant)
  - Check SOAP note structure (all 4 sections present)
  - Check minimum character lengths (50, 50, 30, 30)
  - Check for required keywords (diagnosis, medication, investigation)
  - Display inline errors immediately

- **Layer 2: Rules Engine Validation** (2-3 seconds)
  - PBS rules for prescriptions (max 5 repeats, listed items)
  - MBS rules for pathology (valid item numbers)
  - Allergy checking against patient data
  - Drug interaction checking
  - Australian terminology checking

- **Layer 3: AI-Powered Validation** (5-8 seconds)
  - Send to Claude API for clinical review
  - Check clinical accuracy
  - Verify diagnosis matches presentation
  - Identify red flags
  - Provide detailed feedback

- **Progressive Display**:
  - Show Layer 1 errors immediately
  - Show Layer 2 errors after 2-3 seconds
  - Show Layer 3 feedback after 5-8 seconds
  - Each layer builds on previous feedback

**Usage Example:**

```typescript
const {
  validationLayers,
  currentLayer,
  overallValidationStatus,
  validateAll,
  clearValidation
} = useValidation({
  apiClient: validationAPIClient
});

const handleSubmit = async () => {
  await validateAll(soapNote, patientData);

  // validationLayers will progressively populate:
  // - Layer 1: instant (structure/character count)
  // - Layer 2: 2-3s (PBS/MBS/allergy/interaction)
  // - Layer 3: 5-8s (AI clinical review)
};

return (
  <div>
    {validationLayers.map((layer) => (
      <ValidationLayerDisplay key={layer.layer} layer={layer} />
    ))}
    {overallValidationStatus === 'invalid' && (
      <div className="error">Fix errors before submitting</div>
    )}
  </div>
);
```

**Acceptance Criteria:**
- [ ] Layer 1 validation instant (0ms, sync)
- [ ] Layer 2 validation completes in 2-3 seconds
- [ ] Layer 3 validation completes in 5-8 seconds
- [ ] Layer 1 checks structure and character counts
- [ ] Layer 2 checks PBS/MBS/allergy/interaction rules
- [ ] Layer 3 calls Claude API for clinical review
- [ ] Progressive display shows results as they arrive
- [ ] overallValidationStatus computed correctly
- [ ] Validation can be cleared/reset
- [ ] Errors and warnings tracked separately
- [ ] No console errors
- [ ] No API calls until validateLayer2/3 triggered

---

## Supporting Utilities

### typing-metrics.utils.ts

```typescript
// WPM Calculation
export function calculateWPM(
  charactersTyped: number,
  timeElapsedSeconds: number
): number {
  if (timeElapsedSeconds === 0) return 0;
  const words = charactersTyped / 5; // Standard: 5 chars = 1 word
  const minutes = timeElapsedSeconds / 60;
  return Math.round(words / minutes);
}

// Accuracy Calculation
export function calculateAccuracy(
  typedText: string,
  expectedText: string
): number {
  const minLength = Math.min(typedText.length, expectedText.length);
  let matches = 0;
  for (let i = 0; i < minLength; i++) {
    if (typedText[i] === expectedText[i]) matches++;
  }
  return Math.round((matches / expectedText.length) * 100);
}

// Session Timing
export function getSessionElapsedTime(startTime: Date): number {
  return Math.floor((Date.now() - startTime.getTime()) / 1000);
}
```

### validation-rules.utils.ts

```typescript
// SOAP Note Rules
export function validateSOAPStructure(note: SOAPNote): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!note.subjective || note.subjective.length < 50) {
    errors.push({
      field: 'subjective',
      message: 'Subjective must be at least 50 characters',
      severity: 'error'
    });
  }

  // ... more rules

  return errors;
}

// PBS Rules
export function validatePrescription(
  rx: Prescription,
  patientAllergies: string[]
): ValidationError[] {
  const errors: ValidationError[] = [];

  if (rx.repeats > 5) {
    errors.push({
      field: 'repeats',
      message: 'Maximum 5 repeats allowed per PBS rules',
      severity: 'error'
    });
  }

  // ... more rules

  return errors;
}

// Australian Terminology
export function checkAustralianTerminology(text: string): ValidationWarning[] {
  const warnings: ValidationWarning[] = [];

  const americanTerms: Record<string, string> = {
    'acetaminophen': 'paracetamol',
    'epinephrine': 'adrenaline',
    'albuterol': 'salbutamol'
  };

  for (const [american, australian] of Object.entries(americanTerms)) {
    if (text.toLowerCase().includes(american)) {
      warnings.push({
        field: 'terminology',
        message: `Use Australian term "${australian}" instead of "${american}"`,
        severity: 'warning'
      });
    }
  }

  return warnings;
}
```

---

## Acceptance Criteria

### Hook Implementation
- [ ] All 4 hooks created with complete TypeScript types
- [ ] All hooks properly typed with interfaces
- [ ] No `any` types
- [ ] Proper cleanup on unmount
- [ ] No memory leaks

### useAutoSave
- [ ] Debounces at 30 seconds (configurable)
- [ ] Manual `forceSync()` saves immediately
- [ ] `isSaving` flag updates correctly
- [ ] Errors handled gracefully
- [ ] Cleanup cancels pending saves

### useTypingMetrics
- [ ] WPM calculated correctly
- [ ] Characters tracked accurately
- [ ] Metrics update in real-time
- [ ] Accuracy calculated (if comparison text)
- [ ] Session timer works
- [ ] No performance impact on typing

### usePBSSearch
- [ ] Debounces at 300ms
- [ ] Minimum 2 characters enforced
- [ ] Returns up to 20 results
- [ ] PBS-listed flag displayed
- [ ] Loading/error states work
- [ ] Clear function works

### useValidation
- [ ] Layer 1 instant (0ms)
- [ ] Layer 2 within 2-3 seconds
- [ ] Layer 3 within 5-8 seconds
- [ ] Progressive display works
- [ ] All validation rules applied
- [ ] Errors/warnings tracked separately

### Testing
- [ ] Unit tests for all hooks (80%+ coverage)
- [ ] Test happy path and error scenarios
- [ ] All tests pass 100%
- [ ] No TypeScript errors
- [ ] No console errors/warnings

---

## Testing Requirements

### Unit Tests

#### useAutoSave.test.ts
```typescript
test('Auto-save debounces at 30 seconds', () => { });
test('forceSync saves immediately', () => { });
test('isSaving flag updates during save', () => { });
test('lastSavedAt records timestamp', () => { });
test('Errors handled gracefully', () => { });
test('Cleanup cancels pending saves', () => { });
```

#### useTypingMetrics.test.ts
```typescript
test('WPM calculated correctly', () => { });
test('Characters tracked accurately', () => { });
test('Metrics update in real-time', () => { });
test('Accuracy calculated (if comparison text)', () => { });
test('Session timer starts and stops', () => { });
```

#### usePBSSearch.test.ts
```typescript
test('Search debounces at 300ms', () => { });
test('Minimum 2 characters enforced', () => { });
test('Results return within 500ms', () => { });
test('Max 20 results returned', () => { });
test('PBS-listed flag displayed correctly', () => { });
test('Loading indicator displays', () => { });
test('Clear function empties results', () => { });
```

#### useValidation.test.ts
```typescript
test('Layer 1 validation is instant', () => { });
test('Layer 2 validation completes in 2-3 seconds', () => { });
test('Layer 3 validation completes in 5-8 seconds', () => { });
test('Progressive display shows results as they arrive', () => { });
test('Overall validation status computed correctly', () => { });
test('Validation can be cleared', () => { });
```

---

## Reference PRD Sections

- **Validation Architecture**: Section 3 (User Input Validation & Feedback System)
  - Location: `/home/dev/Development/irStudy/emr-practice-system/prd/00_MASTER_EMR_PRD.md`
  - Lines 370-565

- **Validation Rules Examples**: Section 6-7
  - Lines 710-930 (Detailed validation rule examples)

---

## Agent OS Delegation Prompt

```
Agent Task: Implement EMR Custom Hooks

CRITICAL - Read constraints FIRST:
1. Read /home/dev/Development/irStudy/constraints/README.md
2. Read /home/dev/Development/irStudy/CLAUDE.md
3. Search for existing hook patterns in /home/dev/Development/irStudy/frontend/src/hooks/
4. Reference PRD: /home/dev/Development/irStudy/emr-practice-system/prd/00_MASTER_EMR_PRD.md (lines 370-930)

CONTEXT:
- Custom hooks provide specialized functionality for EMR practice system
- useAutoSave: 30s debounce, cancellation on unmount
- useTypingMetrics: WPM, character count, accuracy
- usePBSSearch: 300ms debounce, medication search
- useValidation: 3-layer validation (instant/2-3s/5-8s)
- React 18 + TypeScript required
- Zero tolerance for type errors

DELIVERABLES:
1. useAutoSave.ts (120+ lines) - Debounced auto-save, cleanup
2. useTypingMetrics.ts (140+ lines) - WPM, chars, accuracy, timing
3. usePBSSearch.ts (160+ lines) - Medication search with debounce
4. useValidation.ts (200+ lines) - 3-layer progressive validation
5. typing-metrics.utils.ts (100+ lines) - WPM/accuracy calculations
6. validation-rules.utils.ts (150+ lines) - Validation rule functions

CRITICAL REQUIREMENTS:
1. useAutoSave (120+ lines):
   - Options: debounceMs (default 30000), onSave, onError, enabled
   - Return: isSaving, lastSavedAt, saveError, forceSync, cancel, resetError
   - Debounce at 30 seconds
   - Cancel pending save on unmount
   - Handle async onSave callback
   - Track error and provide error state

2. useTypingMetrics (140+ lines):
   - Calculate WPM: chars / 5 / minutes
   - Track characters typed
   - Calculate accuracy if comparison text provided
   - Session timing: start/pause/resume
   - Update metrics every keystroke
   - Callback: onMetricsChange

3. usePBSSearch (160+ lines):
   - Debounce: 300ms (configurable)
   - Minimum 2 characters
   - Return up to 20 results
   - Include PBS info: name, strength, form, isListed, requiresAuthority
   - Loading state during search
   - Error state if search fails
   - Clear function to empty results
   - Caching of recent searches (optional)

4. useValidation (200+ lines):
   - Layer 1 (Instant, sync):
     - Check SOAP structure (4 sections)
     - Check min character lengths (50/50/30/30)
     - Check required keywords
   - Layer 2 (2-3 seconds, rules):
     - PBS rules (max 5 repeats, listed items)
     - Allergy checking
     - Drug interactions
     - Australian terminology
   - Layer 3 (5-8 seconds, AI):
     - Call Claude API
     - Clinical accuracy review
     - Red flag detection
     - Detailed feedback
   - Progressive display: each layer builds on previous

5. Performance Requirements:
   - Auto-save debounce: 30 seconds
   - PBS search debounce: 300ms
   - Typing metrics: update every keystroke (no lag)
   - Validation Layer 1: <10ms
   - Validation Layer 2: 2-3 seconds
   - Validation Layer 3: 5-8 seconds
   - No memory leaks from listeners/timeouts

6. Australian Medical Compliance:
   - Terminology checking in validation
   - PBS/MBS rules enforced
   - Allergy safety critical
   - Drug interaction warnings

VALIDATION CHECKLIST (self-validate before returning):
- [ ] Read constraints README and CLAUDE.md
- [ ] Searched for existing hook patterns
- [ ] 0 TypeScript errors (npm run type-check)
- [ ] All tests pass 100% (npm run test)
- [ ] useAutoSave debounces at 30 seconds
- [ ] useAutoSave manual forceSync works
- [ ] useAutoSave cleanup cancels pending
- [ ] useTypingMetrics WPM calculation accurate
- [ ] useTypingMetrics accuracy calculated (if comparison text)
- [ ] useTypingMetrics no lag on typing
- [ ] usePBSSearch debounces at 300ms
- [ ] usePBSSearch returns max 20 results
- [ ] usePBSSearch shows PBS status
- [ ] usePBSSearch handles loading/error
- [ ] useValidation Layer 1 instant (<10ms)
- [ ] useValidation Layer 2 in 2-3 seconds
- [ ] useValidation Layer 3 in 5-8 seconds
- [ ] useValidation progressive display works
- [ ] All utility functions in place
- [ ] Validation rules cover PBS/allergy/interaction/terminology
- [ ] No memory leaks detected
- [ ] No console errors or warnings

ACCEPTANCE CRITERIA (COMPLETE when all pass):
- [ ] All 4 hooks created and properly typed
- [ ] All utility files created
- [ ] TypeScript: 0 errors
- [ ] All tests pass (80%+ coverage)
- [ ] useAutoSave: 30s debounce, cleanup, error handling
- [ ] useTypingMetrics: WPM accurate, real-time, no lag
- [ ] usePBSSearch: 300ms debounce, 20 results max, PBS info
- [ ] useValidation: 3-layer, progressive, all rules applied
- [ ] All hooks properly cleanup on unmount
- [ ] No memory leaks or performance issues
- [ ] All Australian medical rules enforced
- [ ] No console errors or warnings
- [ ] API-ready (can connect to real backend later)

Return JSON summary:
{
  "status": "COMPLETE",
  "hooks_created": ["useAutoSave", "useTypingMetrics", "usePBSSearch", "useValidation"],
  "utilities_created": ["typing-metrics.utils", "validation-rules.utils"],
  "test_results": "X/X passing",
  "typescript_errors": 0,
  "console_errors": 0,
  "performance_notes": "Auto-save 30s, PBS search 300ms, Validation L1: <10ms, L2: 2-3s, L3: 5-8s",
  "notes": "..."
}
```

---

## Implementation Notes

### Debouncing Strategy

Use a custom debounce function or `lodash.debounce`:

```typescript
import { debounce } from 'lodash';

const debouncedSearch = useCallback(
  debounce(async (query: string) => {
    // Perform search
  }, 300),
  []
);
```

### Cleanup Strategy

Always cleanup in `useEffect` return:

```typescript
useEffect(() => {
  // Setup listener
  const timer = setTimeout(() => { /* ... */ }, 30000);

  // Cleanup
  return () => clearTimeout(timer);
}, []);
```

### Layer Validation Pattern

```typescript
const validateAll = async (note, patient) => {
  // Layer 1: Instant (no await)
  const layer1Errors = validateSOAPStructure(note);
  setValidationLayers([{ layer: 1, errors: layer1Errors, status: 'complete' }]);

  // Layer 2: After 2-3 seconds
  setTimeout(async () => {
    const layer2Errors = await validateRules(note, patient);
    setValidationLayers(prev => [...prev, { layer: 2, errors: layer2Errors }]);
  }, 0); // Simulate network delay

  // Layer 3: After 5-8 seconds
  setTimeout(async () => {
    const layer3Result = await validateWithAI(note, patient);
    setValidationLayers(prev => [...prev, { layer: 3, ...layer3Result }]);
  }, 0);
};
```

---

## Progress Tracking

- **Status**: ⏳ Not Started
- **Start Date**: [Fill when started]
- **End Date**: [Fill when completed]
- **Actual Hours**: [Fill when completed]
- **Blockers**: [Document any blockers encountered]
- **Notes**: [Any important notes during implementation]

### Checkpoint 1: Utility Functions (Est. 1 hour)
- [ ] typing-metrics.utils.ts created with all calculations
- [ ] validation-rules.utils.ts created with all rule functions
- [ ] All utility functions tested

### Checkpoint 2: Hook Implementation (Est. 2 hours)
- [ ] useAutoSave.ts created with debounce and cleanup
- [ ] useTypingMetrics.ts created with real-time metrics
- [ ] usePBSSearch.ts created with debounce and caching
- [ ] useValidation.ts created with 3-layer validation

### Checkpoint 3: Testing & Polish (Est. 1 hour)
- [ ] All unit tests written and passing
- [ ] No TypeScript errors
- [ ] No console errors/warnings
- [ ] Performance verified
- [ ] Cleanup verified (no memory leaks)

---

**Previous Task**: TASK 1.3 - State Management
**Next Task**: TASK 1.5 - Styling & Animations
