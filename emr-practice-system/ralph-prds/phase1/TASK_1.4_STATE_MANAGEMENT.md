# TASK 1.4: State Management (Zustand Stores)

**Task ID**: TASK_1.4
**Phase**: Phase 1 - Frontend Foundation
**Estimated Time**: 4 hours
**Prerequisites**: TASK_1.1 (Project Setup)
**Dependencies**: Zustand 4.4.7, TypeScript

---

## Overview

Create Zustand stores for global state management across the EMR practice system. These stores will handle session state, user preferences, form data, and validation results.

**Reference**: See `/home/dev/Development/irStudy/emr-practice-system/design-specs/MASTER_EMR_PRD.md` section on State Management.

---

## Stores to Create

### 1. Session Store (1.5 hours)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/stores/sessionStore.ts`

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface Patient {
  id: string;
  firstName: string;
  lastName: string;
  mrn: string;
  dob: string;
  age: number;
  gender: 'M' | 'F' | 'Other';
  allergies: string[];
  alerts: string[];
}

interface EMRSession {
  id: string;
  userId: string;
  patientId: string;
  linkedOsceId?: string;
  emrType: 'cerner' | 'epic';
  status: 'active' | 'paused' | 'completed' | 'abandoned';
  startedAt: string; // ISO datetime
  expiresAt: string; // ISO datetime
  completedAt?: string;
}

interface SessionState {
  // Current session
  currentSession: EMRSession | null;
  currentPatient: Patient | null;

  // Session management
  startSession: (session: EMRSession, patient: Patient) => void;
  endSession: (score?: number) => void;
  pauseSession: () => void;
  resumeSession: () => void;

  // Session data
  elapsedTime: number;
  updateElapsedTime: (seconds: number) => void;

  // Typing metrics
  typingMetrics: {
    totalKeystrokes: number;
    backspaceCount: number;
    wordsPerMinute: number;
    accuracyRate: number;
  };
  updateTypingMetrics: (metrics: Partial<SessionState['typingMetrics']>) => void;

  // Clear state
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        currentSession: null,
        currentPatient: null,
        elapsedTime: 0,
        typingMetrics: {
          totalKeystrokes: 0,
          backspaceCount: 0,
          wordsPerMinute: 0,
          accuracyRate: 100,
        },

        // Start a new session
        startSession: (session, patient) => {
          set({
            currentSession: { ...session, status: 'active' },
            currentPatient: patient,
            elapsedTime: 0,
            typingMetrics: {
              totalKeystrokes: 0,
              backspaceCount: 0,
              wordsPerMinute: 0,
              accuracyRate: 100,
            },
          });
        },

        // End session
        endSession: (score) => {
          const session = get().currentSession;
          if (!session) return;

          set({
            currentSession: {
              ...session,
              status: 'completed',
              completedAt: new Date().toISOString(),
            },
          });

          // Optionally submit to backend
          // submitSessionResults(session, score);
        },

        // Pause session
        pauseSession: () => {
          const session = get().currentSession;
          if (!session) return;

          set({
            currentSession: {
              ...session,
              status: 'paused',
            },
          });
        },

        // Resume session
        resumeSession: () => {
          const session = get().currentSession;
          if (!session) return;

          set({
            currentSession: {
              ...session,
              status: 'active',
            },
          });
        },

        // Update elapsed time
        updateElapsedTime: (seconds) => {
          set({ elapsedTime: seconds });
        },

        // Update typing metrics
        updateTypingMetrics: (metrics) => {
          set((state) => ({
            typingMetrics: {
              ...state.typingMetrics,
              ...metrics,
            },
          }));
        },

        // Clear all session data
        clearSession: () => {
          set({
            currentSession: null,
            currentPatient: null,
            elapsedTime: 0,
            typingMetrics: {
              totalKeystrokes: 0,
              backspaceCount: 0,
              wordsPerMinute: 0,
              accuracyRate: 100,
            },
          });
        },
      }),
      {
        name: 'emr-session-storage',
        partialize: (state) => ({
          currentSession: state.currentSession,
          currentPatient: state.currentPatient,
          elapsedTime: state.elapsedTime,
        }),
      }
    ),
    { name: 'SessionStore' }
  )
);
```

---

### 2. Form State Store (1.5 hours)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/stores/formStore.ts`

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface SOAPNote {
  subjective: {
    chiefComplaint: string;
    hpi: string;
    reviewOfSystems: Record<string, string>;
  };
  objective: {
    vitalSigns: {
      temperature: number;
      heartRate: number;
      bloodPressureSystolic: number;
      bloodPressureDiastolic: number;
      respiratoryRate: number;
      oxygenSaturation: number;
    };
    physicalExam: Record<string, string>;
  };
  assessment: string;
  plan: string;
}

interface Prescription {
  medication: string;
  dose: string;
  frequency: string;
  duration: string;
  route: string;
  indication: string;
  pbsCode?: string;
  isPbsEligible: boolean;
}

interface PathologyOrder {
  testName: string;
  category: string;
  urgency: 'routine' | 'urgent' | 'stat';
  clinicalIndication: string;
  mbsCode?: string;
}

interface FormState {
  // SOAP Note data
  soapNote: SOAPNote | null;
  updateSOAPNote: (section: keyof SOAPNote, data: any) => void;
  clearSOAPNote: () => void;

  // Prescriptions
  prescriptions: Prescription[];
  addPrescription: (prescription: Prescription) => void;
  removePrescription: (index: number) => void;
  updatePrescription: (index: number, prescription: Prescription) => void;
  clearPrescriptions: () => void;

  // Pathology Orders
  pathologyOrders: PathologyOrder[];
  addPathologyOrder: (order: PathologyOrder) => void;
  removePathologyOrder: (index: number) => void;
  updatePathologyOrder: (index: number, order: PathologyOrder) => void;
  clearPathologyOrders: () => void;

  // Auto-save tracking
  lastSaved: string | null;
  isDirty: boolean;
  markDirty: () => void;
  markClean: () => void;

  // Clear all form data
  clearAllForms: () => void;
}

const initialSOAPNote: SOAPNote = {
  subjective: {
    chiefComplaint: '',
    hpi: '',
    reviewOfSystems: {},
  },
  objective: {
    vitalSigns: {
      temperature: 37.0,
      heartRate: 75,
      bloodPressureSystolic: 120,
      bloodPressureDiastolic: 80,
      respiratoryRate: 16,
      oxygenSaturation: 98,
    },
    physicalExam: {},
  },
  assessment: '',
  plan: '',
};

export const useFormStore = create<FormState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        soapNote: null,
        prescriptions: [],
        pathologyOrders: [],
        lastSaved: null,
        isDirty: false,

        // Update SOAP Note section
        updateSOAPNote: (section, data) => {
          set((state) => ({
            soapNote: {
              ...(state.soapNote || initialSOAPNote),
              [section]: {
                ...(state.soapNote?.[section] || {}),
                ...data,
              },
            },
            isDirty: true,
          }));
        },

        // Clear SOAP Note
        clearSOAPNote: () => {
          set({ soapNote: null, isDirty: false });
        },

        // Prescriptions
        addPrescription: (prescription) => {
          set((state) => ({
            prescriptions: [...state.prescriptions, prescription],
            isDirty: true,
          }));
        },

        removePrescription: (index) => {
          set((state) => ({
            prescriptions: state.prescriptions.filter((_, i) => i !== index),
            isDirty: true,
          }));
        },

        updatePrescription: (index, prescription) => {
          set((state) => ({
            prescriptions: state.prescriptions.map((p, i) =>
              i === index ? prescription : p
            ),
            isDirty: true,
          }));
        },

        clearPrescriptions: () => {
          set({ prescriptions: [], isDirty: false });
        },

        // Pathology Orders
        addPathologyOrder: (order) => {
          set((state) => ({
            pathologyOrders: [...state.pathologyOrders, order],
            isDirty: true,
          }));
        },

        removePathologyOrder: (index) => {
          set((state) => ({
            pathologyOrders: state.pathologyOrders.filter((_, i) => i !== index),
            isDirty: true,
          }));
        },

        updatePathologyOrder: (index, order) => {
          set((state) => ({
            pathologyOrders: state.pathologyOrders.map((o, i) =>
              i === index ? order : o
            ),
            isDirty: true,
          }));
        },

        clearPathologyOrders: () => {
          set({ pathologyOrders: [], isDirty: false });
        },

        // Auto-save tracking
        markDirty: () => {
          set({ isDirty: true });
        },

        markClean: () => {
          set({
            isDirty: false,
            lastSaved: new Date().toISOString(),
          });
        },

        // Clear all forms
        clearAllForms: () => {
          set({
            soapNote: null,
            prescriptions: [],
            pathologyOrders: [],
            lastSaved: null,
            isDirty: false,
          });
        },
      }),
      {
        name: 'emr-form-storage',
        partialize: (state) => ({
          soapNote: state.soapNote,
          prescriptions: state.prescriptions,
          pathologyOrders: state.pathologyOrders,
          lastSaved: state.lastSaved,
        }),
      }
    ),
    { name: 'FormStore' }
  )
);
```

---

### 3. Validation Store (1 hour)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/stores/validationStore.ts`

```typescript
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface ValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
  source: 'client' | 'python' | 'ai';
}

interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  suggestions: string[];
  score?: number;
  aiAnalysis?: {
    clinicalAccuracy: number;
    documentationQuality: number;
    completeness: number;
    feedback: string;
  };
}

interface ValidationState {
  // Current validation results
  soapValidation: ValidationResult | null;
  prescriptionValidation: Record<number, ValidationResult>;
  pathologyValidation: Record<number, ValidationResult>;

  // Validation status
  isValidating: boolean;
  lastValidated: string | null;

  // Set validation results
  setSOAPValidation: (result: ValidationResult) => void;
  setPrescriptionValidation: (index: number, result: ValidationResult) => void;
  setPathologyValidation: (index: number, result: ValidationResult) => void;

  // Clear validation
  clearSOAPValidation: () => void;
  clearPrescriptionValidation: (index: number) => void;
  clearPathologyValidation: (index: number) => void;
  clearAllValidation: () => void;

  // Validation state
  setValidating: (validating: boolean) => void;

  // Get all errors
  getAllErrors: () => ValidationError[];
  hasErrors: () => boolean;
}

export const useValidationStore = create<ValidationState>()(
  devtools(
    (set, get) => ({
      // Initial state
      soapValidation: null,
      prescriptionValidation: {},
      pathologyValidation: {},
      isValidating: false,
      lastValidated: null,

      // Set SOAP validation
      setSOAPValidation: (result) => {
        set({
          soapValidation: result,
          lastValidated: new Date().toISOString(),
          isValidating: false,
        });
      },

      // Set prescription validation
      setPrescriptionValidation: (index, result) => {
        set((state) => ({
          prescriptionValidation: {
            ...state.prescriptionValidation,
            [index]: result,
          },
          lastValidated: new Date().toISOString(),
        }));
      },

      // Set pathology validation
      setPathologyValidation: (index, result) => {
        set((state) => ({
          pathologyValidation: {
            ...state.pathologyValidation,
            [index]: result,
          },
          lastValidated: new Date().toISOString(),
        }));
      },

      // Clear validations
      clearSOAPValidation: () => {
        set({ soapValidation: null });
      },

      clearPrescriptionValidation: (index) => {
        set((state) => {
          const { [index]: _, ...rest } = state.prescriptionValidation;
          return { prescriptionValidation: rest };
        });
      },

      clearPathologyValidation: (index) => {
        set((state) => {
          const { [index]: _, ...rest } = state.pathologyValidation;
          return { pathologyValidation: rest };
        });
      },

      clearAllValidation: () => {
        set({
          soapValidation: null,
          prescriptionValidation: {},
          pathologyValidation: {},
          lastValidated: null,
        });
      },

      // Set validating state
      setValidating: (validating) => {
        set({ isValidating: validating });
      },

      // Get all errors from all sources
      getAllErrors: () => {
        const state = get();
        const errors: ValidationError[] = [];

        // SOAP errors
        if (state.soapValidation) {
          errors.push(...state.soapValidation.errors);
        }

        // Prescription errors
        Object.values(state.prescriptionValidation).forEach((validation) => {
          errors.push(...validation.errors);
        });

        // Pathology errors
        Object.values(state.pathologyValidation).forEach((validation) => {
          errors.push(...validation.errors);
        });

        return errors;
      },

      // Check if any errors exist
      hasErrors: () => {
        return get().getAllErrors().length > 0;
      },
    }),
    { name: 'ValidationStore' }
  )
);
```

---

## Usage Examples

### Session Store Example

```typescript
import { useSessionStore } from '@stores/sessionStore';

function SessionComponent() {
  const {
    currentSession,
    currentPatient,
    startSession,
    endSession,
    elapsedTime,
    updateElapsedTime,
  } = useSessionStore();

  // Start a new session
  const handleStartSession = () => {
    startSession(
      {
        id: 'session-123',
        userId: 'user-456',
        patientId: 'patient-789',
        emrType: 'cerner',
        status: 'active',
        startedAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 15 * 60 * 1000).toISOString(), // 15 min
      },
      {
        id: 'patient-789',
        firstName: 'John',
        lastName: 'Smith',
        mrn: '12345678',
        dob: '1980-05-15',
        age: 44,
        gender: 'M',
        allergies: ['Penicillin'],
        alerts: [],
      }
    );
  };

  // Timer effect
  useEffect(() => {
    if (currentSession?.status === 'active') {
      const interval = setInterval(() => {
        updateElapsedTime(elapsedTime + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [currentSession, elapsedTime]);

  return <div>{/* Session UI */}</div>;
}
```

### Form Store Example

```typescript
import { useFormStore } from '@stores/formStore';

function SOAPEditor() {
  const { soapNote, updateSOAPNote, isDirty, markClean } = useFormStore();

  const handleSaveHPI = (hpi: string) => {
    updateSOAPNote('subjective', {
      hpi,
    });
  };

  const handleAutoSave = async () => {
    // Save to backend
    await api.saveSOAPNote(soapNote);
    markClean();
  };

  return <div>{/* SOAP Editor UI */}</div>;
}
```

### Validation Store Example

```typescript
import { useValidationStore } from '@stores/validationStore';

function ValidationPanel() {
  const {
    soapValidation,
    setSOAPValidation,
    isValidating,
    setValidating,
    getAllErrors,
  } = useValidationStore();

  const handleValidate = async () => {
    setValidating(true);

    // Call validation APIs
    const result = await api.validateSOAP(soapNote);

    setSOAPValidation(result);
  };

  const allErrors = getAllErrors();

  return (
    <div>
      {allErrors.map((error, idx) => (
        <div key={idx}>{error.message}</div>
      ))}
    </div>
  );
}
```

---

## Validation Checklist

Before marking this task complete, verify:

- [ ] All 3 stores created and exported correctly
- [ ] TypeScript types are properly defined
- [ ] Zustand devtools enabled in development
- [ ] Session store persists to localStorage
- [ ] Form store persists to localStorage
- [ ] Validation store does NOT persist (runtime only)
- [ ] Store actions work correctly:
  - [ ] Session start/end/pause/resume
  - [ ] SOAP note updates by section
  - [ ] Prescription add/remove/update
  - [ ] Pathology order add/remove/update
  - [ ] Validation results set/clear
- [ ] Store selectors work correctly
- [ ] No TypeScript errors
- [ ] Import paths use aliases (@stores/*)
- [ ] Zustand middleware (persist, devtools) configured properly

---

## Time Breakdown

- Session Store: 1.5 hours
- Form State Store: 1.5 hours
- Validation Store: 1 hour
- **Total**: 4 hours

---

## Next Steps

After completing this task:
1. Proceed to **TASK_1.5_CUSTOM_HOOKS.md** (Custom React hooks)
2. Then move to **Phase 2** (Validation layer)

---

**Last Updated**: 2026-02-03
**Status**: Ready for Implementation
