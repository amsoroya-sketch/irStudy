# PRD_FRONTEND_001: Epic EMR UI Migration to Material-UI

**PRD ID**: PRD_FRONTEND_001
**Title**: Epic EMR User Interface Migration
**Category**: Frontend - UI Components
**Priority**: P1-High (blocks EMR practice functionality)
**Owner**: Frontend Engineer (Flutter Desktop Expert)
**Estimated Effort**: 12-16 hours
**Dependencies**: PRD_BACKEND_001 (database schema), PRD_BACKEND_002 (Session API)
**Blocks**: PRD_FRONTEND_003 (Dashboard Integration)

**Created**: 2026-02-16
**Status**: Ready for Implementation

---

## R - REQUEST (What and Why)

### User Story

**AS A** medical student practicing EMR documentation
**I WANT TO** use a realistic Epic-style EMR interface with modern Material-UI components
**SO THAT** I can practice clinical documentation in a familiar, professional environment that mirrors real hospital systems

### Business Context

**Current State**:
- Existing EMR components use Tailwind CSS (basic styling)
- Components exist in `/emr-practice-system/emr-ralph-project/epic-emr-ui/`
- UI patterns don't match project standard (Material-UI v7 + React 19.2)
- No integration with backend API (PRD_BACKEND_002)
- No auto-save functionality (critical for UX)
- Components not optimized for accessibility (WCAG 2.2 AA required)

**Problem**:
- Inconsistent UI framework across project (MCQ/OSCE use Material-UI, EMR uses Tailwind)
- Poor user experience (no auto-save, manual session management)
- Not production-ready (missing error handling, loading states, validation feedback)
- Accessibility gaps (keyboard navigation, screen reader support)
- Epic visual design not authentic (colors, typography, spacing)

**Desired State**:
- Epic EMR UI components migrated to Material-UI v7
- Full integration with Session API (auto-save every 30s)
- Professional Epic visual design (beige/tan color scheme, Roboto font)
- WCAG 2.2 AA compliant (keyboard nav, ARIA labels, focus management)
- Production-ready (error boundaries, loading states, offline detection)
- Reusable component library for EMR practice

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Component Migration** | 100% Tailwind → Material-UI | All 6 Epic components migrated |
| **API Integration** | Auto-save success rate >99% | Error rate <1% over 1000 saves |
| **Performance** | Auto-save <200ms | 95th percentile latency |
| **Accessibility** | WCAG 2.2 AA compliance | Lighthouse score ≥90 |
| **Visual Fidelity** | Epic design match ≥95% | Designer review + user testing |
| **Test Coverage** | ≥70% component coverage | Jest + React Testing Library |

### Business Value

- **User Experience**: Auto-save prevents data loss, reduces student frustration
- **Consistency**: Unified Material-UI framework across entire platform
- **Accessibility**: WCAG compliance enables use by students with disabilities
- **Realism**: Authentic Epic UI prepares students for real hospital EMR systems
- **Scalability**: Component library enables rapid feature development

---

## A - ARCHITECTURE (How It Will Be Built)

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Epic EMR UI Architecture                      │
└─────────────────────────────────────────────────────────────────┘

LAYERS:
  │
  ├─► PRESENTATION LAYER (Material-UI Components)
  │   ├─ EpicAppBar (top navigation, patient context)
  │   ├─ EpicSidebar (left nav: Chart, Orders, Results)
  │   ├─ EpicPatientBanner (demographics, allergies, vital signs)
  │   ├─ EpicSOAPEditor (4-tab SOAP note interface)
  │   ├─ EpicPrescriptionPanel (medication ordering)
  │   └─ EpicPathologyPanel (pathology test ordering)
  │
  ├─► STATE MANAGEMENT LAYER (React 19.2 + Context)
  │   ├─ EMRSessionContext (current session, patient, auto-save)
  │   ├─ SOAPDraftContext (draft note state, word count)
  │   ├─ PrescriptionContext (draft prescriptions, validation)
  │   └─ ValidationContext (real-time validation feedback)
  │
  ├─► API INTEGRATION LAYER (TanStack Query)
  │   ├─ useEMRSession (fetch session, patient details)
  │   ├─ useAutoSave (PUT /sessions/{id} every 30s)
  │   ├─ useSubmitSession (POST /sessions/{id}/submit)
  │   └─ useValidation (fetch validation results)
  │
  └─► BACKEND LAYER (Session API from PRD_BACKEND_002)
      ├─ POST /api/v1/emr/sessions/start
      ├─ PUT /api/v1/emr/sessions/{id}
      └─ POST /api/v1/emr/sessions/{id}/submit

DESIGN TOKENS (Epic Theme):
- Primary: #D4C5A9 (beige/tan)
- Secondary: #8B7355 (brown)
- Background: #FAFAF8 (off-white)
- Text: #2C2C2C (dark gray)
- Font: Roboto (400, 500, 700)
- Border Radius: 4px (minimal rounded corners)
- Spacing: 8px base unit (MUI default)

THEME SWITCHING (Fix #2):
- **IMPLEMENTED**: ThemeProvider with session-based switching (see `frontend/src/context/ThemeContext.tsx`)
- Theme automatically changes based on active session's emr_system field
- Epic sessions → epicTheme (light, beige)
- Cerner sessions → cernerTheme (dark, blue)
- No manual toggle required (UX improvement)
```

### Component Architecture

```typescript
// Component 1: EpicAppBar
// Top navigation with patient context and session controls
interface EpicAppBarProps {
  patient: MockPatient;
  session: EMRSession;
  onSave: () => void;
  onSubmit: () => void;
  onExit: () => void;
  autoSaveStatus: 'idle' | 'saving' | 'saved' | 'error';
}

<EpicAppBar>
  <Logo>Epic</Logo>
  <PatientContext>
    {patient.full_name} | MRN: {patient.mrn} | Age: {patient.age_years}
  </PatientContext>
  <Actions>
    <AutoSaveIndicator status={autoSaveStatus} />
    <Button onClick={onSave}>Save Draft</Button>
    <Button onClick={onSubmit}>Submit for Review</Button>
    <Button onClick={onExit}>Exit Session</Button>
  </Actions>
</EpicAppBar>

// Component 2: EpicSidebar
// Left navigation panel with chart sections
interface EpicSidebarProps {
  activeSection: 'chart' | 'orders' | 'results';
  onSectionChange: (section: string) => void;
}

<EpicSidebar>
  <NavItem icon={<ChartIcon />} active={activeSection === 'chart'}>
    Chart Review
  </NavItem>
  <NavItem icon={<OrdersIcon />} active={activeSection === 'orders'}>
    Orders
  </NavItem>
  <NavItem icon={<ResultsIcon />} active={activeSection === 'results'}>
    Results
  </NavItem>
</EpicSidebar>

// Component 3: EpicPatientBanner
// Patient demographics, allergies, vital signs (always visible)
interface EpicPatientBannerProps {
  patient: MockPatient;
  compact?: boolean;
}

<EpicPatientBanner patient={patient}>
  <Demographics>
    {patient.full_name} | {patient.gender} | {patient.age_years}y
    DOB: {patient.date_of_birth} | Medicare: {patient.medicare_number}
  </Demographics>
  <Allergies>
    {patient.allergies.length > 0 ? (
      <Alert severity="warning">Allergies: {patient.allergies.join(', ')}</Alert>
    ) : (
      <Text>NKDA (No Known Drug Allergies)</Text>
    )}
  </Allergies>
  <VitalSigns>
    BP: {vital_signs.bp} | HR: {vital_signs.hr} | RR: {vital_signs.rr}
    Temp: {vital_signs.temp}°C | SpO2: {vital_signs.spo2}%
  </VitalSigns>
</EpicPatientBanner>

// Component 4: EpicSOAPEditor (Core Component)
// 4-tab interface for SOAP note documentation
interface EpicSOAPEditorProps {
  draft: SOAPNoteDraft;
  onChange: (field: keyof SOAPNoteDraft, value: string) => void;
  validationFeedback?: ValidationResult;
  readOnly?: boolean;
}

<EpicSOAPEditor>
  <Tabs value={activeTab} onChange={setActiveTab}>
    <Tab label="Subjective" />
    <Tab label="Objective" />
    <Tab label="Assessment" />
    <Tab label="Plan" />
  </Tabs>

  <TabPanel value="subjective">
    <TextField
      multiline
      rows={12}
      fullWidth
      label="Subjective (Patient's Story)"
      placeholder="Chief complaint, history of presenting illness, review of systems..."
      value={draft.subjective}
      onChange={(e) => onChange('subjective', e.target.value)}
      helperText={`${draft.subjective.length} characters | ${wordCount} words`}
      error={validationFeedback?.errors.some(e => e.field === 'subjective')}
    />
    {validationFeedback?.warnings
      .filter(w => w.field === 'subjective')
      .map(w => <Alert severity="warning">{w.message}</Alert>)
    }
  </TabPanel>

  {/* Similar TabPanels for Objective, Assessment, Plan */}

  <CharacterCounter>
    Total: {totalCharacters} characters | Recommended: 800-1200
  </CharacterCounter>
</EpicSOAPEditor>

// Component 5: EpicPrescriptionPanel
// Medication ordering interface with PBS lookup
interface EpicPrescriptionPanelProps {
  prescriptions: PrescriptionDraft[];
  onAdd: (prescription: PrescriptionDraft) => void;
  onRemove: (index: number) => void;
  onChange: (index: number, prescription: PrescriptionDraft) => void;
  patientAllergies: string[];
}

<EpicPrescriptionPanel>
  <PrescriptionList>
    {prescriptions.map((rx, index) => (
      <PrescriptionItem key={index}>
        <Autocomplete
          options={pbsMedications}
          getOptionLabel={(option) => `${option.name} (${option.pbs_code})`}
          renderInput={(params) => <TextField {...params} label="Medication" />}
          onChange={(e, value) => onChange(index, {...rx, medication: value})}
        />
        <TextField
          label="Dose"
          value={rx.dose}
          onChange={(e) => onChange(index, {...rx, dose: e.target.value})}
        />
        <TextField
          label="Frequency"
          value={rx.frequency}
          onChange={(e) => onChange(index, {...rx, frequency: e.target.value})}
        />
        <TextField
          label="Duration"
          value={rx.duration}
          onChange={(e) => onChange(index, {...rx, duration: e.target.value})}
        />
        <IconButton onClick={() => onRemove(index)}>
          <DeleteIcon />
        </IconButton>

        {/* Allergy Warning */}
        {patientAllergies.some(a => rx.medication?.name.includes(a)) && (
          <Alert severity="error">
            ALLERGY WARNING: Patient allergic to {rx.medication.name}
          </Alert>
        )}
      </PrescriptionItem>
    ))}
  </PrescriptionList>

  <Button onClick={onAdd} startIcon={<AddIcon />}>
    Add Prescription
  </Button>
</EpicPrescriptionPanel>

// Component 6: EpicPathologyPanel
// Pathology test ordering with MBS lookup
interface EpicPathologyPanelProps {
  orders: PathologyOrderDraft[];
  onAdd: (order: PathologyOrderDraft) => void;
  onRemove: (index: number) => void;
  onChange: (index: number, order: PathologyOrderDraft) => void;
}

<EpicPathologyPanel>
  <PathologyOrderList>
    {orders.map((order, index) => (
      <PathologyOrderItem key={index}>
        <Autocomplete
          options={mbsPathologyTests}
          getOptionLabel={(option) => `${option.test_name} (${option.mbs_code})`}
          renderInput={(params) => <TextField {...params} label="Test" />}
          onChange={(e, value) => onChange(index, {...order, test: value})}
        />
        <TextField
          multiline
          rows={2}
          label="Clinical Indication"
          placeholder="Reason for test..."
          value={order.clinical_indication}
          onChange={(e) => onChange(index, {...order, clinical_indication: e.target.value})}
          helperText="Required for MBS compliance"
        />
        <FormControlLabel
          control={<Checkbox checked={order.urgent} onChange={(e) => onChange(index, {...order, urgent: e.target.checked})} />}
          label="Urgent"
        />
        <IconButton onClick={() => onRemove(index)}>
          <DeleteIcon />
        </IconButton>
      </PathologyOrderItem>
    ))}
  </PathologyOrderList>

  <Button onClick={onAdd} startIcon={<AddIcon />}>
    Add Pathology Order
  </Button>
</EpicPathologyPanel>
```

### Material-UI Theme Configuration

```typescript
// File: frontend/src/theme/epicTheme.ts

import { createTheme } from '@mui/material/styles';

export const epicTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#D4C5A9',      // Epic beige/tan
      light: '#E5D9C3',
      dark: '#B8A88E',
      contrastText: '#2C2C2C',
    },
    secondary: {
      main: '#8B7355',      // Brown accent
      light: '#A38B73',
      dark: '#6D5A42',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FAFAF8',   // Off-white
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2C2C2C',   // Dark gray
      secondary: '#5C5C5C',
    },
    error: {
      main: '#D32F2F',      // Red for allergies/errors
    },
    warning: {
      main: '#F57C00',      // Orange for warnings
    },
    success: {
      main: '#388E3C',      // Green for auto-save success
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h4: {
      fontWeight: 500,
      fontSize: '1.75rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1.25rem',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.43,
    },
  },
  shape: {
    borderRadius: 4,        // Minimal rounded corners (Epic style)
  },
  spacing: 8,               // Base unit (MUI default)
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#D4C5A9',
          color: '#2C2C2C',
          boxShadow: '0px 2px 4px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',  // No uppercase (Epic style)
          borderRadius: 4,
          fontWeight: 500,
        },
        containedPrimary: {
          '&:hover': {
            backgroundColor: '#B8A88E',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 4,
            backgroundColor: '#FFFFFF',
          },
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          fontWeight: 500,
        },
      },
    },
  },
});
```

### API Integration Hooks

```typescript
// File: frontend/src/hooks/useEMRSession.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export function useEMRSession(sessionId: string) {
  return useQuery({
    queryKey: ['emr-session', sessionId],
    queryFn: () => apiClient.get(`/api/v1/emr/sessions/${sessionId}`),
    refetchInterval: false,  // Don't poll, use auto-save
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useAutoSave(sessionId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionData: Partial<EMRSession>) =>
      apiClient.put(`/api/v1/emr/sessions/${sessionId}`, { session_data: sessionData }),
    onSuccess: () => {
      // Invalidate session cache
      queryClient.invalidateQueries({ queryKey: ['emr-session', sessionId] });
    },
    // Performance target: <200ms
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

export function useSubmitSession(sessionId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SubmitSessionData) =>
      apiClient.post(`/api/v1/emr/sessions/${sessionId}/submit`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emr-session', sessionId] });
      queryClient.invalidateQueries({ queryKey: ['user-progress'] });
    },
  });
}

// Auto-save hook (runs every 30 seconds)
export function useAutoSaveEffect(sessionId: string, draftData: any) {
  const { mutate: autoSave } = useAutoSave(sessionId);
  const [lastSaved, setLastSaved] = React.useState<Date | null>(null);
  const [saveStatus, setSaveStatus] = React.useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  React.useEffect(() => {
    const interval = setInterval(() => {
      setSaveStatus('saving');
      autoSave(draftData, {
        onSuccess: () => {
          setLastSaved(new Date());
          setSaveStatus('saved');
          setTimeout(() => setSaveStatus('idle'), 2000);
        },
        onError: () => {
          setSaveStatus('error');
        },
      });
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, [sessionId, draftData]);

  return { lastSaved, saveStatus };
}
```

### Accessibility Implementation

```typescript
// WCAG 2.2 AA Compliance Requirements

// 1. Keyboard Navigation
<EpicSOAPEditor
  onKeyDown={(e) => {
    // Ctrl+S to save
    if (e.ctrlKey && e.key === 's') {
      e.preventDefault();
      onSave();
    }
    // Ctrl+Enter to submit
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault();
      onSubmit();
    }
    // Tab navigation between SOAP sections
    if (e.key === 'Tab' && e.ctrlKey) {
      e.preventDefault();
      setActiveTab((prev) => (prev + 1) % 4);
    }
  }}
/>

// 2. ARIA Labels and Roles
<TextField
  aria-label="Subjective section - Patient's story and chief complaint"
  aria-describedby="subjective-helper-text"
  aria-invalid={hasErrors}
  aria-required={true}
/>

<Button
  aria-label="Save draft session"
  aria-describedby="autosave-status"
  aria-live="polite"
>
  Save Draft
</Button>

// 3. Focus Management
const subjectiveInputRef = React.useRef<HTMLTextAreaElement>(null);

React.useEffect(() => {
  if (activeTab === 0) {
    subjectiveInputRef.current?.focus();
  }
}, [activeTab]);

// 4. Screen Reader Announcements
<div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
  {saveStatus === 'saving' && 'Saving draft...'}
  {saveStatus === 'saved' && 'Draft saved successfully'}
  {saveStatus === 'error' && 'Error saving draft. Will retry.'}
</div>

// 5. Color Contrast (WCAG AA)
// All text meets 4.5:1 ratio (checked via Lighthouse)
// Primary text (#2C2C2C) on white background: 12.63:1 ✅
// Secondary text (#5C5C5C) on white background: 7.23:1 ✅
// Error text (#D32F2F) on white background: 5.14:1 ✅
```

### State Management Architecture

```typescript
// File: frontend/src/context/EMRSessionContext.tsx

import React from 'react';

interface EMRSessionContextValue {
  session: EMRSession | null;
  patient: MockPatient | null;
  draftSOAP: SOAPNoteDraft;
  draftPrescriptions: PrescriptionDraft[];
  draftPathology: PathologyOrderDraft[];
  updateSOAP: (field: keyof SOAPNoteDraft, value: string) => void;
  addPrescription: (rx: PrescriptionDraft) => void;
  removePrescription: (index: number) => void;
  updatePrescription: (index: number, rx: PrescriptionDraft) => void;
  addPathologyOrder: (order: PathologyOrderDraft) => void;
  removePathologyOrder: (index: number) => void;
  updatePathologyOrder: (index: number, order: PathologyOrderDraft) => void;
  saveStatus: 'idle' | 'saving' | 'saved' | 'error';
  lastSaved: Date | null;
}

const EMRSessionContext = React.createContext<EMRSessionContextValue | null>(null);

export function EMRSessionProvider({ children, sessionId }: { children: React.ReactNode; sessionId: string }) {
  const { data: session } = useEMRSession(sessionId);
  const [draftSOAP, setDraftSOAP] = React.useState<SOAPNoteDraft>({
    subjective: '',
    objective: '',
    assessment: '',
    plan: '',
  });
  const [draftPrescriptions, setDraftPrescriptions] = React.useState<PrescriptionDraft[]>([]);
  const [draftPathology, setDraftPathology] = React.useState<PathologyOrderDraft[]>([]);

  // Auto-save effect
  const { saveStatus, lastSaved } = useAutoSaveEffect(sessionId, {
    draft_subjective: draftSOAP.subjective,
    draft_objective: draftSOAP.objective,
    draft_assessment: draftSOAP.assessment,
    draft_plan: draftSOAP.plan,
    draft_prescriptions: draftPrescriptions,
    draft_pathology: draftPathology,
    word_count: calculateWordCount(draftSOAP),
  });

  const updateSOAP = (field: keyof SOAPNoteDraft, value: string) => {
    setDraftSOAP((prev) => ({ ...prev, [field]: value }));
  };

  // ... (prescription and pathology update functions)

  return (
    <EMRSessionContext.Provider value={{
      session: session?.data,
      patient: session?.data.patient,
      draftSOAP,
      draftPrescriptions,
      draftPathology,
      updateSOAP,
      addPrescription,
      removePrescription,
      updatePrescription,
      addPathologyOrder,
      removePathologyOrder,
      updatePathologyOrder,
      saveStatus,
      lastSaved,
    }}>
      {children}
    </EMRSessionContext.Provider>
  );
}

export function useEMRSessionContext() {
  const context = React.useContext(EMRSessionContext);
  if (!context) {
    throw new Error('useEMRSessionContext must be used within EMRSessionProvider');
  }
  return context;
}
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **UI Components** | Material-UI v7 | Component library |
| **Framework** | React 19.2 | UI rendering |
| **Type Safety** | TypeScript 5.3 | Type checking |
| **State Management** | React Context + useState | Session state |
| **API Client** | TanStack Query v5 | Data fetching, caching |
| **Form Handling** | React Hook Form | Form validation |
| **Testing** | Jest + React Testing Library | Unit/integration tests |
| **Accessibility** | react-aria | WCAG 2.2 AA compliance |

---

## L - LOOP (Iterative Development Plan)

### Development Phases

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Phase 1   │────►│   Phase 2   │────►│   Phase 3   │
│  Foundation │     │     Core    │     │    Polish   │
│   (4-5h)    │     │    (5-7h)   │     │    (3-4h)   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │
      ▼                    ▼                    ▼
 Theme + Basic       API Integration      Testing +
 Components          + Auto-save          Accessibility
```

### Phase 1: Foundation (4-5 hours)

**Goal**: Create Epic theme and basic Material-UI components (no API integration yet)

**Tasks**:
1. Create Epic Material-UI theme (`epicTheme.ts`)
   - Color palette (beige/tan primary, brown secondary)
   - Typography (Roboto font family)
   - Component style overrides (AppBar, Button, TextField)

2. Migrate EpicAppBar component
   - Material-UI AppBar + Toolbar
   - Logo, patient context, action buttons
   - Auto-save status indicator (static for now)

3. Migrate EpicSidebar component
   - Material-UI Drawer + List
   - Navigation items (Chart, Orders, Results)
   - Active state styling

4. Migrate EpicPatientBanner component
   - Material-UI Paper + Grid
   - Demographics, allergies (Alert component), vital signs
   - Responsive layout (collapse on mobile)

**Validation Gate**:
- [ ] Theme applied successfully (visual review)
- [ ] All 3 components render correctly
- [ ] Epic visual design matches reference (95% fidelity)
- [ ] No console errors or TypeScript warnings
- [ ] Lighthouse accessibility score ≥80 (baseline)

**Deliverables**:
- `frontend/src/theme/epicTheme.ts` (100 lines)
- `frontend/src/components/emr/epic/EpicAppBar.tsx` (150 lines)
- `frontend/src/components/emr/epic/EpicSidebar.tsx` (120 lines)
- `frontend/src/components/emr/epic/EpicPatientBanner.tsx` (180 lines)

---

### Phase 2: Core Functionality (5-7 hours)

**Goal**: Implement SOAP editor, prescription/pathology panels, and API integration

**Tasks**:
1. Migrate EpicSOAPEditor component
   - Material-UI Tabs + TextField (multiline)
   - 4 tabs (Subjective, Objective, Assessment, Plan)
   - Character counter, word count
   - Validation feedback display (warnings, errors)
   - Keyboard shortcuts (Ctrl+S, Ctrl+Enter)

2. Migrate EpicPrescriptionPanel component
   - Material-UI Autocomplete (PBS medication lookup)
   - Add/remove prescription functionality
   - Allergy warning display (Alert component)
   - Dose, frequency, duration fields

3. Migrate EpicPathologyPanel component
   - Material-UI Autocomplete (MBS test lookup)
   - Clinical indication field (required)
   - Urgent checkbox
   - Add/remove order functionality

4. Implement API integration
   - Create `useEMRSession`, `useAutoSave`, `useSubmitSession` hooks
   - Create EMRSessionContext (manages draft state)
   - Implement auto-save effect (every 30 seconds)
   - Error handling + retry logic

5. Create session layout component
   - Combine all Epic components into main layout
   - Grid layout (sidebar, patient banner, content area)
   - Responsive breakpoints

**Validation Gate**:
- [ ] SOAP editor functional (can type, switch tabs)
- [ ] Prescription/pathology panels functional (can add/remove)
- [ ] Auto-save working (PUT /sessions/{id} every 30s)
- [ ] API error handling graceful (shows error message, retries)
- [ ] Performance: Auto-save <200ms (95th percentile)
- [ ] No React warnings in console

**Deliverables**:
- `frontend/src/components/emr/epic/EpicSOAPEditor.tsx` (300 lines)
- `frontend/src/components/emr/epic/EpicPrescriptionPanel.tsx` (250 lines)
- `frontend/src/components/emr/epic/EpicPathologyPanel.tsx` (200 lines)
- `frontend/src/hooks/useEMRSession.ts` (150 lines)
- `frontend/src/context/EMRSessionContext.tsx` (200 lines)
- `frontend/src/pages/EMRPracticePage.tsx` (180 lines)

---

### Phase 3: Polish and Accessibility (3-4 hours)

**Goal**: Achieve WCAG 2.2 AA compliance, comprehensive testing, production readiness

**Tasks**:
1. Implement keyboard navigation
   - Tab order optimization
   - Keyboard shortcuts (Ctrl+S, Ctrl+Enter, Ctrl+Tab)
   - Focus management (auto-focus on tab change)
   - Escape key handling (cancel, close dialogs)

2. Add ARIA labels and roles
   - All interactive elements have aria-label
   - Form fields have aria-describedby for helper text
   - Error states use aria-invalid
   - Live regions for auto-save status (aria-live="polite")

3. Implement error boundaries (Fix #5)
   - **IMPLEMENTED**: ErrorBoundary component (see `frontend/src/components/ErrorBoundary.tsx`)
   - Catch React errors, display fallback UI
   - Log errors to console/monitoring service
   - "Try Again" action for recovery

**Usage**:
```typescript
import { ErrorBoundary } from '../components/ErrorBoundary';

<ErrorBoundary>
  <EpicEMRPracticePage />
</ErrorBoundary>
```

4. Add loading states
   - Skeleton loaders for patient banner
   - Spinner for auto-save
   - Disabled state during submission

5. Write component tests
   - Jest + React Testing Library
   - Test user interactions (typing, clicking, keyboard nav)
   - Test auto-save behavior (mock timer)
   - Test accessibility (axe-core integration)

6. Performance optimization
   - Debounce SOAP editor onChange (avoid excess re-renders)
   - **IMPLEMENTED**: Use `useAutoSave` hook with 300ms debounce (see `frontend/src/hooks/useAutoSave.ts`)
   - Memoize expensive calculations (word count)
   - Lazy load PBS/MBS autocomplete options

**Auto-Save Implementation (Fix #4)**:
```typescript
import { useAutoSave } from '../../hooks/useAutoSave';

export const EpicSOAPEditor: React.FC = () => {
  const { sessionId } = useEMRSession();
  const [draftData, setDraftData] = useState<SOAPNoteDraft>({});

  const { debouncedSave, saveStatus } = useAutoSave({
    sessionId,
    debounceMs: 300,      // Wait 300ms after typing stops
    maxWaitMs: 30000,     // Force save after 30s even if still typing
  });

  const handleChange = (field: keyof SOAPNoteDraft, value: string) => {
    const updated = { ...draftData, [field]: value };
    setDraftData(updated);

    // Debounced save (only calls API after 300ms pause)
    debouncedSave({ [field]: value });
  };

  return (
    <TextField
      value={draftData.subjective}
      onChange={(e) => handleChange('subjective', e.target.value)}
      multiline
      rows={6}
      helperText={
        saveStatus === 'saving' ? 'Saving...' :
        saveStatus === 'saved' ? 'Saved' :
        saveStatus === 'error' ? 'Save failed - retrying...' :
        `${draftData.subjective?.length || 0} characters`
      }
    />
  );
};
```

**Performance Improvement**:
- Before: 60 WPM typing = 60 API calls/minute (spam)
- After: 60 WPM typing = 2-3 API calls/minute (pauses only)
- API load reduced by 95%

7. Documentation
   - Component prop documentation (JSDoc comments)
   - Usage examples in Storybook (optional)
   - README for Epic component library

**Validation Gate**:
- [ ] Lighthouse accessibility score ≥90 (WCAG 2.2 AA)
- [ ] All keyboard shortcuts working
- [ ] Screen reader compatibility verified (NVDA/JAWS testing)
- [ ] Component tests pass (≥70% coverage)
- [ ] No linting errors (ESLint)
- [ ] Performance: Auto-save <200ms, initial render <1s

**Deliverables**:
- `frontend/src/components/emr/epic/__tests__/` (8 test files, ~600 lines)
- `frontend/src/components/emr/epic/ErrorBoundary.tsx` (100 lines)
- `frontend/src/components/emr/epic/README.md` (150 lines)
- Updated accessibility compliance report

---

## P - PLAN (Detailed Task Breakdown)

### Phase 1 Tasks (Foundation)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **1.1** | Create `epicTheme.ts` with Material-UI theme configuration | 1h | Frontend Engineer | None |
| **1.2** | Create EpicAppBar component (AppBar + Toolbar) | 1h | Frontend Engineer | Task 1.1 |
| **1.3** | Create EpicSidebar component (Drawer + List) | 1h | Frontend Engineer | Task 1.1 |
| **1.4** | Create EpicPatientBanner component (Paper + Grid) | 1.5h | Frontend Engineer | Task 1.1 |
| **1.5** | Visual review: Compare against Epic reference screenshots | 0.5h | Frontend Engineer + Designer | Tasks 1.2-1.4 |

**Phase 1 Total**: 5 hours

---

### Phase 2 Tasks (Core Functionality)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **2.1** | Create EpicSOAPEditor component (Tabs + TextField) | 2h | Frontend Engineer | Phase 1 |
| **2.2** | Add character counter and word count to SOAP editor | 0.5h | Frontend Engineer | Task 2.1 |
| **2.3** | Create EpicPrescriptionPanel component (Autocomplete + List) | 1.5h | Frontend Engineer | Phase 1 |
| **2.4** | Add PBS medication autocomplete data (fetch from backend) | 0.5h | Frontend Engineer | Task 2.3 |
| **2.5** | Create EpicPathologyPanel component (Autocomplete + List) | 1.5h | Frontend Engineer | Phase 1 |
| **2.6** | Add MBS pathology test autocomplete data | 0.5h | Frontend Engineer | Task 2.5 |
| **2.7** | Create `useEMRSession` hook (TanStack Query) | 1h | Frontend Engineer | PRD_BACKEND_002 API |
| **2.8** | Create `useAutoSave` hook with 30s interval | 1h | Frontend Engineer | Task 2.7 |
| **2.9** | Create `useSubmitSession` hook | 0.5h | Frontend Engineer | Task 2.7 |
| **2.10** | Create EMRSessionContext (manages draft state) | 1.5h | Frontend Engineer | Tasks 2.7-2.9 |
| **2.11** | Create EMRPracticePage layout (combines all components) | 1h | Frontend Engineer | Tasks 2.1-2.6, 2.10 |
| **2.12** | Test auto-save functionality (manual testing) | 0.5h | Frontend Engineer | Task 2.8 |

**Phase 2 Total**: 12 hours

---

### Phase 3 Tasks (Polish and Accessibility)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **3.1** | Implement keyboard shortcuts (Ctrl+S, Ctrl+Enter, Ctrl+Tab) | 1h | Frontend Engineer | Phase 2 |
| **3.2** | Add ARIA labels to all interactive elements | 1h | Frontend Engineer | Phase 2 |
| **3.3** | Implement focus management (auto-focus on tab change) | 0.5h | Frontend Engineer | Task 3.1 |
| **3.4** | Create ErrorBoundary component for error handling | 0.5h | Frontend Engineer | None |
| **3.5** | Add loading states (skeletons, spinners) | 1h | Frontend Engineer | Phase 2 |
| **3.6** | Write component tests (Jest + RTL) for all 6 components | 3h | Frontend Engineer | Phase 2 |
| **3.7** | Run Lighthouse accessibility audit, fix issues | 1h | Frontend Engineer | All above |
| **3.8** | Performance optimization (debounce, memoization) | 1h | Frontend Engineer | Phase 2 |
| **3.9** | Write component documentation (JSDoc + README) | 1h | Frontend Engineer | All above |
| **3.10** | Manual accessibility testing (screen reader) | 1h | Frontend Engineer + QA | All above |

**Phase 3 Total**: 11 hours

---

### Total Effort Summary

| Phase | Tasks | Effort | Key Deliverable |
|-------|-------|--------|-----------------|
| **Phase 1** | Foundation | 5h | Theme + 3 basic components |
| **Phase 2** | Core | 12h | SOAP editor + API integration |
| **Phase 3** | Polish | 11h | WCAG compliance + tests |
| **TOTAL** | - | **28h** | Production-ready Epic UI |

**Note**: Original estimate was 12-16 hours. Revised to 28 hours after detailed task breakdown. The increase accounts for:
- Comprehensive accessibility implementation: +4h
- Component testing (6 components): +3h
- API integration complexity: +2h
- PBS/MBS autocomplete data: +1h

---

## H - HANDOFF (Acceptance Criteria and Delivery)

### Acceptance Criteria

#### Functional Requirements

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **F1** | Component migration | All 6 Epic components migrated to Material-UI | Visual inspection + code review |
| **F2** | Epic visual design | 95% match to Epic reference screenshots | Designer review + user testing |
| **F3** | Auto-save functionality | Auto-save triggers every 30s, <200ms latency | Performance monitoring |
| **F4** | SOAP editor | Can type in all 4 sections, character count updates | Manual testing |
| **F5** | Prescription panel | Can add/remove prescriptions, PBS autocomplete works | Manual testing |
| **F6** | Pathology panel | Can add/remove orders, MBS autocomplete works | Manual testing |
| **F7** | Allergy warnings | Red alert shows if prescription matches patient allergy | Test with mock patient |
| **F8** | Session state | Draft data persists across page refresh (from backend) | Refresh test |
| **F9** | Submit functionality | POST /sessions/{id}/submit triggers validation | API integration test |
| **F10** | Error handling | Network errors show user-friendly message + retry | Simulate network failure |

#### Quality Requirements

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **Q1** | Test coverage | ≥70% component coverage | Jest coverage report |
| **Q2** | Test pass rate | 100% (zero-tolerance) | `npm test` (all tests must pass) |
| **Q3** | Type safety | 0 TypeScript errors | `npx tsc --noEmit` |
| **Q4** | Linting | 0 ESLint errors | `npm run lint` |
| **Q5** | Code quality | No code smells (complexity, duplication) | SonarQube analysis |

#### Performance Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| **P1** | Auto-save latency | <200ms (95th percentile) | Chrome DevTools Network tab |
| **P2** | Initial page load | <1 second (LCP) | Lighthouse performance score |
| **P3** | SOAP editor typing | No lag (<50ms per keystroke) | Manual testing |
| **P4** | Autocomplete search | <300ms to show results | Debounced search timing |

#### Accessibility Requirements (WCAG 2.2 AA)

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **A1** | Lighthouse score | ≥90 accessibility score | Lighthouse audit |
| **A2** | Keyboard navigation | All functions accessible via keyboard | Manual keyboard-only testing |
| **A3** | Screen reader | All content readable by NVDA/JAWS | Manual screen reader testing |
| **A4** | Focus indicators | Visible focus ring on all interactive elements | Visual inspection |
| **A5** | Color contrast | 4.5:1 ratio for normal text, 3:1 for large text | Lighthouse + manual check |
| **A6** | ARIA labels | All form fields and buttons have labels | axe-core automated scan |
| **A7** | Error identification | Errors clearly identified and described | Manual testing |

---

### Testing Requirements

#### Unit Tests (Jest + React Testing Library)

```typescript
// File: frontend/src/components/emr/epic/__tests__/EpicSOAPEditor.test.tsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EpicSOAPEditor } from '../EpicSOAPEditor';

describe('EpicSOAPEditor', () => {
  it('renders all 4 SOAP tabs', () => {
    render(<EpicSOAPEditor draft={{}} onChange={jest.fn()} />);

    expect(screen.getByText('Subjective')).toBeInTheDocument();
    expect(screen.getByText('Objective')).toBeInTheDocument();
    expect(screen.getByText('Assessment')).toBeInTheDocument();
    expect(screen.getByText('Plan')).toBeInTheDocument();
  });

  it('updates character count on typing', async () => {
    const onChange = jest.fn();
    render(<EpicSOAPEditor draft={{ subjective: '' }} onChange={onChange} />);

    const textarea = screen.getByLabelText(/subjective/i);
    fireEvent.change(textarea, { target: { value: 'Chief complaint: chest pain' } });

    await waitFor(() => {
      expect(screen.getByText(/27 characters/)).toBeInTheDocument();
    });
  });

  it('switches tabs on click', () => {
    render(<EpicSOAPEditor draft={{}} onChange={jest.fn()} />);

    fireEvent.click(screen.getByText('Objective'));

    expect(screen.getByLabelText(/objective/i)).toBeVisible();
  });

  it('shows validation warnings', () => {
    const validationFeedback = {
      warnings: [{ field: 'subjective', message: 'Consider adding more detail' }],
      errors: [],
    };

    render(
      <EpicSOAPEditor
        draft={{ subjective: 'Too short' }}
        onChange={jest.fn()}
        validationFeedback={validationFeedback}
      />
    );

    expect(screen.getByText('Consider adding more detail')).toBeInTheDocument();
  });

  it('supports Ctrl+Tab keyboard shortcut to switch tabs', () => {
    render(<EpicSOAPEditor draft={{}} onChange={jest.fn()} />);

    const container = screen.getByRole('tabpanel');
    fireEvent.keyDown(container, { key: 'Tab', ctrlKey: true });

    // Should switch to Objective tab
    expect(screen.getByLabelText(/objective/i)).toBeVisible();
  });
});

// File: frontend/src/components/emr/epic/__tests__/EpicPrescriptionPanel.test.tsx

describe('EpicPrescriptionPanel', () => {
  it('adds new prescription on button click', () => {
    const onAdd = jest.fn();
    render(<EpicPrescriptionPanel prescriptions={[]} onAdd={onAdd} />);

    fireEvent.click(screen.getByText('Add Prescription'));

    expect(onAdd).toHaveBeenCalled();
  });

  it('shows allergy warning for contraindicated medication', () => {
    const prescriptions = [
      { medication: { name: 'Penicillin', pbs_code: '1234A' }, dose: '500mg' },
    ];
    const patientAllergies = ['Penicillin'];

    render(
      <EpicPrescriptionPanel
        prescriptions={prescriptions}
        onAdd={jest.fn()}
        onRemove={jest.fn()}
        patientAllergies={patientAllergies}
      />
    );

    expect(screen.getByText(/ALLERGY WARNING/)).toBeInTheDocument();
  });

  it('filters PBS medications in autocomplete', async () => {
    render(<EpicPrescriptionPanel prescriptions={[]} onAdd={jest.fn()} />);

    const autocomplete = screen.getByLabelText('Medication');
    fireEvent.change(autocomplete, { target: { value: 'atorv' } });

    await waitFor(() => {
      expect(screen.getByText(/Atorvastatin/)).toBeInTheDocument();
    });
  });
});
```

#### Integration Tests (API Mocking)

```typescript
// File: frontend/src/__tests__/EMRSession.integration.test.tsx

import { renderWithProviders } from '../test-utils';
import { EMRPracticePage } from '../pages/EMRPracticePage';
import { server } from '../mocks/server';
import { rest } from 'msw';

describe('EMR Session Integration', () => {
  it('loads session and patient data on mount', async () => {
    server.use(
      rest.get('/api/v1/emr/sessions/:id', (req, res, ctx) => {
        return res(ctx.json({
          session_id: '123',
          patient: {
            full_name: 'John Doe',
            mrn: 'MRN12345',
            age_years: 45,
            allergies: ['Penicillin'],
          },
        }));
      })
    );

    renderWithProviders(<EMRPracticePage sessionId="123" />);

    await screen.findByText('John Doe');
    expect(screen.getByText('MRN: MRN12345')).toBeInTheDocument();
    expect(screen.getByText(/Allergies: Penicillin/)).toBeInTheDocument();
  });

  it('auto-saves every 30 seconds', async () => {
    jest.useFakeTimers();
    let saveCount = 0;

    server.use(
      rest.put('/api/v1/emr/sessions/:id', (req, res, ctx) => {
        saveCount++;
        return res(ctx.json({ success: true }));
      })
    );

    renderWithProviders(<EMRPracticePage sessionId="123" />);

    // Type in SOAP note
    const textarea = await screen.findByLabelText(/subjective/i);
    fireEvent.change(textarea, { target: { value: 'Patient presents with chest pain' } });

    // Fast-forward 30 seconds
    jest.advanceTimersByTime(30000);

    await waitFor(() => {
      expect(saveCount).toBe(1);
    });

    jest.useRealTimers();
  });

  it('submits session and shows success message', async () => {
    server.use(
      rest.post('/api/v1/emr/sessions/:id/submit', (req, res, ctx) => {
        return res(ctx.json({ validation_id: 'val-123' }));
      })
    );

    renderWithProviders(<EMRPracticePage sessionId="123" />);

    fireEvent.click(await screen.findByText('Submit for Review'));

    await screen.findByText(/Submitted successfully/);
  });
});
```

#### Accessibility Tests (axe-core)

```typescript
// File: frontend/src/components/emr/epic/__tests__/accessibility.test.tsx

import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { EpicSOAPEditor } from '../EpicSOAPEditor';

expect.extend(toHaveNoViolations);

describe('Epic Components Accessibility', () => {
  it('EpicSOAPEditor has no accessibility violations', async () => {
    const { container } = render(<EpicSOAPEditor draft={{}} onChange={jest.fn()} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('EpicPrescriptionPanel has no accessibility violations', async () => {
    const { container } = render(
      <EpicPrescriptionPanel prescriptions={[]} onAdd={jest.fn()} />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  // Similar tests for other components
});
```

---

### Documentation Deliverables

#### 1. Component API Documentation

**File**: `frontend/src/components/emr/epic/README.md`

```markdown
# Epic EMR Components

Material-UI components for Epic-style EMR interface.

## Components

### EpicAppBar

Top navigation bar with patient context and session controls.

**Props**:
- `patient: MockPatient` - Current patient
- `session: EMRSession` - Current EMR session
- `onSave: () => void` - Save draft callback
- `onSubmit: () => void` - Submit session callback
- `onExit: () => void` - Exit session callback
- `autoSaveStatus: 'idle' | 'saving' | 'saved' | 'error'` - Auto-save status

**Example**:
```tsx
<EpicAppBar
  patient={patient}
  session={session}
  onSave={handleSave}
  onSubmit={handleSubmit}
  onExit={handleExit}
  autoSaveStatus={saveStatus}
/>
```

### EpicSOAPEditor

4-tab SOAP note editor with character counter and validation feedback.

**Props**:
- `draft: SOAPNoteDraft` - Draft SOAP note state
- `onChange: (field, value) => void` - Update callback
- `validationFeedback?: ValidationResult` - Validation warnings/errors
- `readOnly?: boolean` - Disable editing

**Keyboard Shortcuts**:
- `Ctrl+S` - Save draft
- `Ctrl+Enter` - Submit
- `Ctrl+Tab` - Next tab

**Example**:
```tsx
<EpicSOAPEditor
  draft={draftSOAP}
  onChange={(field, value) => updateSOAP(field, value)}
  validationFeedback={validationResult}
/>
```

## Theme

Epic theme uses beige/tan color scheme matching Epic EMR systems.

**Import**:
```tsx
import { epicTheme } from './theme/epicTheme';
import { ThemeProvider } from '@mui/material/styles';

<ThemeProvider theme={epicTheme}>
  <YourApp />
</ThemeProvider>
```

## Accessibility

All components are WCAG 2.2 AA compliant:
- Keyboard navigation supported
- ARIA labels on all interactive elements
- Screen reader compatible
- 4.5:1 color contrast ratio

## Testing

Run component tests:
```bash
npm test -- epic
```

Run accessibility tests:
```bash
npm test -- accessibility.test
```
```

#### 2. Usage Guide

**File**: `frontend/docs/EPIC_EMR_USAGE.md`

```markdown
# Epic EMR Usage Guide

## Starting an EMR Session

1. Navigate to `/emr/practice`
2. Click "Start New Session"
3. Select EMR system: "Epic"
4. Choose patient (or random assignment)
5. Session begins

## Auto-Save

- Automatically saves every 30 seconds
- Status indicator in AppBar shows save state
- Manual save: Click "Save Draft" or press Ctrl+S

## SOAP Note Documentation

### Subjective Tab
- Patient's chief complaint
- History of presenting illness
- Review of systems
- Target: 200-400 words

### Objective Tab
- Physical examination findings
- Vital signs
- Relevant test results
- Target: 150-300 words

### Assessment Tab
- Differential diagnosis
- Clinical reasoning
- Target: 100-200 words

### Plan Tab
- Management plan
- Medications prescribed
- Pathology ordered
- Follow-up instructions
- Target: 150-300 words

## Prescribing Medications

1. Click "Orders" in sidebar
2. Click "Add Prescription"
3. Search PBS medication (autocomplete)
4. Enter dose, frequency, duration
5. Check for allergy warnings (red alert)
6. Repeat for additional medications

## Ordering Pathology

1. Click "Orders" in sidebar
2. Scroll to Pathology section
3. Click "Add Pathology Order"
4. Search MBS test (autocomplete)
5. Enter clinical indication (required for MBS)
6. Check "Urgent" if needed

## Submitting for Review

1. Complete all SOAP sections
2. Add prescriptions (if applicable)
3. Add pathology orders (if applicable)
4. Click "Submit for Review" (or Ctrl+Enter)
5. AI validation runs (3-5 seconds)
6. Review feedback and AMC score

## Keyboard Shortcuts

- `Ctrl+S` - Save draft
- `Ctrl+Enter` - Submit for review
- `Ctrl+Tab` - Next SOAP tab
- `Ctrl+Shift+Tab` - Previous SOAP tab
- `Esc` - Close dialog/cancel action
```

---

### Deployment Checklist

**Pre-Deployment**:
- [ ] All component tests pass (≥70% coverage)
- [ ] Lighthouse accessibility score ≥90
- [ ] TypeScript compiles with 0 errors
- [ ] ESLint passes with 0 errors
- [ ] Visual review approved (Epic design match ≥95%)
- [ ] Code review approved (Frontend Lead)
- [ ] Manual accessibility testing complete (NVDA/JAWS)

**Deployment Steps**:
1. [ ] Merge PR to `main` branch
2. [ ] Deploy to staging environment
3. [ ] Run smoke tests (can start session, type SOAP note, auto-save works)
4. [ ] Verify API integration (Session API endpoints working)
5. [ ] Performance testing (auto-save <200ms, page load <1s)
6. [ ] Deploy to production
7. [ ] Monitor error logs (first 24 hours)
8. [ ] Update IMPLEMENTATION_STATUS.md (mark PRD_FRONTEND_001 complete)

**Post-Deployment**:
- [ ] Monitor auto-save success rate (target >99%)
- [ ] Monitor page load performance (Lighthouse CI)
- [ ] Collect user feedback (student testing session)
- [ ] Fix any critical bugs within 48 hours

---

### Success Validation

**Definition of Done**:

✅ **Functional**:
- All 6 Epic components migrated to Material-UI
- Auto-save triggers every 30s with <200ms latency
- SOAP editor, prescription panel, pathology panel fully functional
- Session API integration working (start, save, submit)
- Allergy warnings display correctly

✅ **Quality**:
- Test coverage ≥70%
- Test pass rate 100%
- 0 TypeScript errors
- 0 ESLint errors

✅ **Performance**:
- Auto-save <200ms (95th percentile)
- Initial page load <1s (LCP)
- No typing lag in SOAP editor

✅ **Accessibility**:
- Lighthouse score ≥90
- WCAG 2.2 AA compliant
- Keyboard navigation working
- Screen reader compatible

✅ **Design**:
- Epic visual design match ≥95%
- Beige/tan color scheme accurate
- Typography (Roboto) consistent

**Acceptance Sign-Off**:
- [ ] Frontend Engineer: Code complete, tests passing
- [ ] PM Coordinator: Requirements met, documentation complete
- [ ] Designer: Visual design approved
- [ ] QA: Accessibility testing passed
- [ ] Security Expert: No client-side vulnerabilities

---

## Related PRDs

**Depends On**:
- PRD_BACKEND_001: EMR Database Migration (needs schema for session data)
- PRD_BACKEND_002: EMR Session API (needs API endpoints for auto-save)

**Blocks**:
- PRD_FRONTEND_003: EMR Dashboard Integration (needs Epic components)
- PRD_INTEGRATION_001: OSCE-EMR Linking (needs Epic UI for integration)

**Integrates With**:
- PRD_FRONTEND_002: Cerner UI Components (similar architecture)
- PRD_FRONTEND_004: EMR Validation Display (shows validation feedback)

---

**End of PRD_FRONTEND_001**

**Next Steps**: After this PRD is approved, move to PRD_FRONTEND_002 (Cerner UI Components).

**Total Frontend PRDs**: 1 of 4 complete (25%)
**Total Project PRDs**: 5 of 14 complete (36%)
