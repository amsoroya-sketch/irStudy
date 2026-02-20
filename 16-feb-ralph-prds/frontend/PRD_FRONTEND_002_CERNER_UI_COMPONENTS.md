# PRD_FRONTEND_002: Cerner EMR UI Components

**PRD ID**: PRD_FRONTEND_002
**Title**: Cerner EMR User Interface Components
**Category**: Frontend - UI Components
**Priority**: P1-High
**Owner**: Frontend Engineer (Flutter Desktop Expert)
**Estimated Effort**: 10-14 hours
**Dependencies**: PRD_BACKEND_001 (database), PRD_BACKEND_002 (Session API), PRD_FRONTEND_001 (Epic UI patterns)
**Blocks**: PRD_FRONTEND_003 (Dashboard Integration)

**Created**: 2026-02-16
**Status**: Ready for Implementation

---

## R - REQUEST (What and Why)

### User Story

**AS A** medical student practicing EMR documentation
**I WANT TO** use a realistic Cerner-style EMR interface with dark theme and professional UI
**SO THAT** I can practice with both major Australian hospital EMR systems (Epic and Cerner) and adapt to different interface paradigms

### Business Context

**Current State**:
- Epic EMR components complete (PRD_FRONTEND_001)
- No Cerner EMR components exist
- Many Australian hospitals use Cerner (alongside Epic)
- Students need exposure to both systems for AMC Clinical Examination

**Problem**:
- Students only exposed to one EMR system (Epic)
- Cerner has different UX paradigms (dark theme, tabbed workflow, different terminology)
- Real hospitals use both systems - students must be adaptable
- Cerner components not available in project

**Desired State**:
- Complete Cerner UI component library (dark theme, blue accents)
- Same auto-save and API integration as Epic (code reuse)
- Cerner-specific UX patterns (PowerChart navigation, tabbed interface)
- Students can practice with both Epic and Cerner EMR systems

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Component Creation** | 100% Cerner components built | All 6 components complete |
| **Code Reuse** | ≥60% from Epic components | Share hooks, context, API logic |
| **API Integration** | Auto-save success rate >99% | Same as Epic (reuse hooks) |
| **Performance** | Auto-save <200ms | Same as Epic |
| **Accessibility** | WCAG 2.2 AA compliance | Lighthouse score ≥90 |
| **Visual Fidelity** | Cerner design match ≥95% | Designer review + user testing |
| **Test Coverage** | ≥70% component coverage | Jest + React Testing Library |

### Business Value

- **Dual System Exposure**: Prepares students for both major Australian hospital EMR systems
- **Code Efficiency**: Reuse Epic's API integration, hooks, and state management
- **Realistic Training**: Authentic Cerner UI builds muscle memory for clinical rotations
- **Flexibility**: Students can choose preferred EMR system for practice

---

## A - ARCHITECTURE (How It Will Be Built)

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   Cerner EMR UI Architecture                     │
└─────────────────────────────────────────────────────────────────┘

LAYERS:
  │
  ├─► PRESENTATION LAYER (Material-UI Components - Dark Theme)
  │   ├─ CernerAppBar (top nav, dark blue, patient context)
  │   ├─ CernerSidebar (left nav: Chart, Orders, Results, Notes)
  │   ├─ CernerPatientBanner (demographics, compact design)
  │   ├─ CernerSOAPEditor (PowerChart tabbed interface)
  │   ├─ CernerPrescriptionPanel (medication ordering)
  │   └─ CernerPathologyPanel (pathology test ordering)
  │
  ├─► STATE MANAGEMENT LAYER (Shared with Epic)
  │   ├─ EMRSessionContext (REUSED from PRD_FRONTEND_001)
  │   ├─ SOAPDraftContext (REUSED)
  │   ├─ PrescriptionContext (REUSED)
  │   └─ ValidationContext (REUSED)
  │
  ├─► API INTEGRATION LAYER (Shared with Epic)
  │   ├─ useEMRSession (REUSED from PRD_FRONTEND_001)
  │   ├─ useAutoSave (REUSED)
  │   ├─ useSubmitSession (REUSED)
  │   └─ useValidation (REUSED)
  │
  └─► BACKEND LAYER (Same API)
      ├─ POST /api/v1/emr/sessions/start
      ├─ PUT /api/v1/emr/sessions/{id}
      └─ POST /api/v1/emr/sessions/{id}/submit

DESIGN TOKENS (Cerner Theme - Dark):
- Primary: #0066CC (blue)
- Secondary: #003D7A (dark blue)
- Background: #1E1E1E (dark gray)
- Paper: #2D2D2D (lighter gray)
- Text: #FFFFFF (white)
- Text Secondary: #B0B0B0 (light gray)
- Font: Roboto (400, 500, 700)
- Border Radius: 8px (more rounded than Epic)
- Spacing: 8px base unit (MUI default)

THEME SWITCHING (Fix #2):
- **SHARED with PRD_FRONTEND_001**: ThemeProvider (see `frontend/src/context/ThemeContext.tsx`)
- Theme automatically changes based on active session's emr_system field
- Cerner sessions → cernerTheme (dark theme applied)
- Epic sessions → epicTheme (light theme applied)
- Both themes defined in same file for consistency
```

### Component Architecture Comparison

```
Epic (Light Theme)          Cerner (Dark Theme)
┌──────────────────┐        ┌──────────────────┐
│ Beige AppBar     │        │ Dark Blue AppBar │
├──────────────────┤        ├──────────────────┤
│                  │        │                  │
│ Light Background │        │ Dark Background  │
│ Minimal Rounded  │        │ More Rounded     │
│ Roboto Font      │        │ Roboto Font      │
│                  │        │                  │
└──────────────────┘        └──────────────────┘

SHARED:
- State management (EMRSessionContext)
- API hooks (useAutoSave, useSubmitSession)
- Business logic (validation, auto-save timing)

DIFFERENT:
- Visual design (colors, spacing)
- Component structure (Cerner uses more tabs)
- Terminology (Cerner: "PowerChart", Epic: "Chart Review")
```

### Cerner-Specific UX Patterns

```typescript
// Cerner PowerChart Navigation
// More tab-heavy than Epic (every section is a tab)

<CernerPowerChart>
  <MainTabs>
    <Tab label="Chart Review" />
    <Tab label="Orders" />
    <Tab label="Results" />
    <Tab label="Notes" />      {/* Cerner-specific */}
    <Tab label="Schedule" />   {/* Cerner-specific */}
  </MainTabs>

  <TabPanel value="Notes">
    <SubTabs>
      <Tab label="Progress Notes" />
      <Tab label="SOAP Notes" />
      <Tab label="Consult Notes" />
    </SubTabs>
  </TabPanel>
</CernerPowerChart>

// Epic uses sidebar navigation instead of nested tabs
```

### Material-UI Theme Configuration

```typescript
// File: frontend/src/theme/cernerTheme.ts

import { createTheme } from '@mui/material/styles';

export const cernerTheme = createTheme({
  palette: {
    mode: 'dark',           // KEY DIFFERENCE: Dark mode
    primary: {
      main: '#0066CC',      // Cerner blue
      light: '#3384D6',
      dark: '#004C99',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#003D7A',      // Dark blue accent
      light: '#005BA8',
      dark: '#002952',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#1E1E1E',   // Dark gray
      paper: '#2D2D2D',     // Lighter gray for cards
    },
    text: {
      primary: '#FFFFFF',   // White text
      secondary: '#B0B0B0', // Light gray text
    },
    error: {
      main: '#F44336',      // Brighter red for dark background
    },
    warning: {
      main: '#FF9800',      // Brighter orange
    },
    success: {
      main: '#4CAF50',      // Brighter green
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h4: {
      fontWeight: 500,
      fontSize: '1.75rem',
      color: '#FFFFFF',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1.25rem',
      color: '#FFFFFF',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
      color: '#FFFFFF',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.43,
      color: '#B0B0B0',
    },
  },
  shape: {
    borderRadius: 8,        // More rounded than Epic (8px vs 4px)
  },
  spacing: 8,
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#003D7A',  // Dark blue
          color: '#FFFFFF',
          boxShadow: '0px 2px 8px rgba(0,0,0,0.5)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
        },
        containedPrimary: {
          '&:hover': {
            backgroundColor: '#004C99',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            backgroundColor: '#2D2D2D',
            '& fieldset': {
              borderColor: '#4D4D4D',
            },
            '&:hover fieldset': {
              borderColor: '#0066CC',
            },
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#2D2D2D',
          backgroundImage: 'none',  // Remove MUI dark mode gradient
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
        standardError: {
          backgroundColor: '#3D1F1F',  // Dark red background
          color: '#FFCCCC',
        },
        standardWarning: {
          backgroundColor: '#3D2F1F',  // Dark orange background
          color: '#FFE0B2',
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          borderBottom: '2px solid #4D4D4D',
        },
        indicator: {
          backgroundColor: '#0066CC',
          height: 3,
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          color: '#B0B0B0',
          '&.Mui-selected': {
            color: '#FFFFFF',
          },
        },
      },
    },
  },
});
```

### Component Implementation (Key Differences from Epic)

```typescript
// Component 1: CernerAppBar
// Dark blue theme, more compact than Epic
interface CernerAppBarProps {
  patient: MockPatient;
  session: EMRSession;
  onSave: () => void;
  onSubmit: () => void;
  onExit: () => void;
  autoSaveStatus: 'idle' | 'saving' | 'saved' | 'error';
}

<CernerAppBar>
  <Logo>
    <PowerChartIcon /> {/* Cerner logo/icon */}
    PowerChart
  </Logo>
  <PatientContext sx={{ fontSize: '0.875rem' }}>  {/* Smaller than Epic */}
    {patient.full_name} | {patient.mrn} | {patient.age_years}y
  </PatientContext>
  <Actions>
    <Chip  {/* Cerner uses Chips for status */}
      label={autoSaveStatus}
      color={autoSaveStatus === 'saved' ? 'success' : 'default'}
      size="small"
    />
    <IconButton onClick={onSave}><SaveIcon /></IconButton>
    <Button onClick={onSubmit} variant="contained">Submit</Button>
    <IconButton onClick={onExit}><ExitIcon /></IconButton>
  </Actions>
</CernerAppBar>

// Component 2: CernerSidebar
// Vertical tabs instead of list (Cerner pattern)
interface CernerSidebarProps {
  activeSection: 'chart' | 'orders' | 'results' | 'notes';
  onSectionChange: (section: string) => void;
}

<CernerSidebar>
  <Tabs orientation="vertical" value={activeSection} onChange={onSectionChange}>
    <Tab label="Chart Review" icon={<ChartIcon />} value="chart" />
    <Tab label="Orders" icon={<OrdersIcon />} value="orders" />
    <Tab label="Results" icon={<ResultsIcon />} value="results" />
    <Tab label="Notes" icon={<NotesIcon />} value="notes" />
  </Tabs>
</CernerSidebar>

// Component 3: CernerPatientBanner
// More compact than Epic, dark theme
interface CernerPatientBannerProps {
  patient: MockPatient;
  compact?: boolean;
}

<CernerPatientBanner patient={patient}>
  <Grid container spacing={1}>  {/* Tighter spacing than Epic */}
    <Grid item xs={12} md={6}>
      <Typography variant="body2">
        {patient.full_name} | {patient.gender} | {patient.age_years}y | DOB: {patient.date_of_birth}
      </Typography>
    </Grid>
    <Grid item xs={12} md={3}>
      {patient.allergies.length > 0 ? (
        <Chip label={`Allergies: ${patient.allergies.join(', ')}`} color="error" size="small" />
      ) : (
        <Chip label="NKDA" color="default" size="small" />
      )}
    </Grid>
    <Grid item xs={12} md={3}>
      <Typography variant="body2">
        BP {vital_signs.bp} | HR {vital_signs.hr} | SpO2 {vital_signs.spo2}%
      </Typography>
    </Grid>
  </Grid>
</CernerPatientBanner>

// Component 4: CernerSOAPEditor
// PowerChart nested tabs (Cerner pattern)
interface CernerSOAPEditorProps {
  draft: SOAPNoteDraft;
  onChange: (field: keyof SOAPNoteDraft, value: string) => void;
  validationFeedback?: ValidationResult;
}

<CernerSOAPEditor>
  {/* Main tab for Notes section */}
  <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
    <Typography variant="h6" gutterBottom>
      SOAP Note
    </Typography>

    {/* Sub-tabs for SOAP sections */}
    <Tabs value={activeTab} onChange={setActiveTab}>
      <Tab label="S - Subjective" />
      <Tab label="O - Objective" />
      <Tab label="A - Assessment" />
      <Tab label="P - Plan" />
    </Tabs>

    <TabPanel value="subjective">
      <TextField
        multiline
        rows={10}
        fullWidth
        label="Subjective (Patient's Story)"
        placeholder="Chief complaint, HPI, ROS..."
        value={draft.subjective}
        onChange={(e) => onChange('subjective', e.target.value)}
        variant="outlined"
        sx={{
          '& .MuiInputBase-root': {
            color: '#FFFFFF',  // White text on dark background
          },
        }}
      />
      <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="caption" color="text.secondary">
          {wordCount(draft.subjective)} words
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {draft.subjective.length} characters
        </Typography>
      </Box>
    </TabPanel>

    {/* Similar panels for Objective, Assessment, Plan */}
  </Paper>
</CernerSOAPEditor>

// Component 5: CernerPrescriptionPanel
// Similar to Epic but dark theme styling
<CernerPrescriptionPanel>
  <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
    <Typography variant="h6" gutterBottom>
      Medications
    </Typography>

    <List>
      {prescriptions.map((rx, index) => (
        <ListItem
          key={index}
          sx={{
            bgcolor: '#3D3D3D',  // Slightly lighter than paper
            borderRadius: 2,
            mb: 1,
          }}
        >
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Autocomplete
                options={pbsMedications}
                getOptionLabel={(option) => `${option.name} (${option.pbs_code})`}
                renderInput={(params) => (
                  <TextField {...params} label="Medication" variant="outlined" size="small" />
                )}
                onChange={(e, value) => onChange(index, {...rx, medication: value})}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField label="Dose" size="small" value={rx.dose} onChange={...} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField label="Frequency" size="small" value={rx.frequency} onChange={...} />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField label="Duration" size="small" value={rx.duration} onChange={...} />
            </Grid>
            <Grid item xs={12} md={1}>
              <IconButton onClick={() => onRemove(index)} color="error">
                <DeleteIcon />
              </IconButton>
            </Grid>

            {/* Allergy warning */}
            {patientAllergies.some(a => rx.medication?.name.includes(a)) && (
              <Grid item xs={12}>
                <Alert severity="error">
                  ⚠️ ALLERGY WARNING: Patient allergic to {rx.medication.name}
                </Alert>
              </Grid>
            )}
          </Grid>
        </ListItem>
      ))}
    </List>

    <Button onClick={onAdd} startIcon={<AddIcon />} variant="contained" sx={{ mt: 2 }}>
      Add Medication
    </Button>
  </Paper>
</CernerPrescriptionPanel>

// Component 6: CernerPathologyPanel
// Similar to Epic but dark theme
<CernerPathologyPanel>
  <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
    <Typography variant="h6" gutterBottom>
      Pathology Orders
    </Typography>

    {/* Similar structure to CernerPrescriptionPanel */}
  </Paper>
</CernerPathologyPanel>
```

### Code Reuse Strategy

```typescript
// Shared hooks (100% reused from PRD_FRONTEND_001)
import { useEMRSession, useAutoSave, useSubmitSession } from '@/hooks/useEMRSession';
import { useAutoSaveEffect } from '@/hooks/useEMRSession';

// Shared context (100% reused)
import { EMRSessionProvider, useEMRSessionContext } from '@/context/EMRSessionContext';

// Shared types (100% reused)
import { SOAPNoteDraft, PrescriptionDraft, PathologyOrderDraft } from '@/types/emr';

// Only new code: Cerner-specific components
// frontend/src/components/emr/cerner/
//   - CernerAppBar.tsx (new, dark theme)
//   - CernerSidebar.tsx (new, vertical tabs)
//   - CernerPatientBanner.tsx (new, compact design)
//   - CernerSOAPEditor.tsx (new, PowerChart styling)
//   - CernerPrescriptionPanel.tsx (new, dark theme)
//   - CernerPathologyPanel.tsx (new, dark theme)

// Shared utilities (100% reused)
import { calculateWordCount, formatVitalSigns } from '@/utils/emr';
```

### Accessibility (Same Requirements as Epic)

```typescript
// WCAG 2.2 AA Compliance (same as PRD_FRONTEND_001)

// 1. Dark Mode Contrast Requirements
// Text on dark background must meet 7:1 ratio (AAA level for dark themes)
// White (#FFFFFF) on dark gray (#1E1E1E): 17.1:1 ✅
// Light gray (#B0B0B0) on dark gray (#1E1E1E): 9.8:1 ✅
// Blue (#0066CC) on dark gray (#1E1E1E): 6.2:1 ✅

// 2. Keyboard Navigation (identical to Epic)
<CernerSOAPEditor
  onKeyDown={(e) => {
    if (e.ctrlKey && e.key === 's') { e.preventDefault(); onSave(); }
    if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); onSubmit(); }
    if (e.key === 'Tab' && e.ctrlKey) { e.preventDefault(); setActiveTab((prev) => (prev + 1) % 4); }
  }}
/>

// 3. ARIA Labels (identical to Epic)
<TextField
  aria-label="Subjective section - Patient's story"
  aria-describedby="subjective-helper-text"
  aria-invalid={hasErrors}
  aria-required={true}
/>

// 4. Focus Management (identical to Epic)
// 5. Screen Reader Announcements (identical to Epic)
```

---

## L - LOOP (Iterative Development Plan)

### Development Phases

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Phase 1   │────►│   Phase 2   │────►│   Phase 3   │
│  Foundation │     │     Core    │     │    Polish   │
│   (3-4h)    │     │    (4-5h)   │     │    (3-4h)   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │
      ▼                    ▼                    ▼
 Theme + Basic       SOAP Editor +        Testing +
 Components          Panels              Accessibility
 (Reuse Epic hooks)  (Dark theme)        (WCAG AA)
```

### Phase 1: Foundation (3-4 hours)

**Goal**: Create Cerner theme and basic components (reuse Epic's state management)

**Tasks**:
1. Create Cerner Material-UI theme (`cernerTheme.ts`)
   - Dark mode palette (blue primary, dark background)
   - Typography overrides
   - Component style overrides (dark theme variants)

2. Create CernerAppBar component
   - Dark blue AppBar
   - Compact patient context (smaller than Epic)
   - Auto-save status as Chip (Cerner pattern)

3. Create CernerSidebar component
   - Vertical tabs (Cerner PowerChart pattern)
   - Icon + label for each section

4. Create CernerPatientBanner component
   - Compact grid layout (tighter spacing than Epic)
   - Chips for allergies (Cerner pattern)
   - Dark theme styling

**Validation Gate**:
- [ ] Theme applied successfully (dark background, blue accents)
- [ ] All 3 components render correctly
- [ ] Cerner visual design matches reference (95% fidelity)
- [ ] Dark mode contrast meets WCAG AAA (7:1 ratio)
- [ ] No console errors or TypeScript warnings

**Deliverables**:
- `frontend/src/theme/cernerTheme.ts` (120 lines)
- `frontend/src/components/emr/cerner/CernerAppBar.tsx` (140 lines)
- `frontend/src/components/emr/cerner/CernerSidebar.tsx` (100 lines)
- `frontend/src/components/emr/cerner/CernerPatientBanner.tsx` (150 lines)

---

### Phase 2: Core Functionality (4-5 hours)

**Goal**: Implement SOAP editor and prescription/pathology panels with dark theme

**Tasks**:
1. Create CernerSOAPEditor component
   - PowerChart nested tabs (main "Notes" tab → SOAP sub-tabs)
   - Dark theme TextField styling
   - Character/word counter
   - Validation feedback display

2. Create CernerPrescriptionPanel component
   - Dark theme Paper + List
   - PBS medication autocomplete (reuse Epic's data)
   - Allergy warnings (dark theme Alert)

3. Create CernerPathologyPanel component
   - Dark theme styling
   - MBS test autocomplete (reuse Epic's data)
   - Clinical indication field

4. Integrate with shared API hooks
   - Import useEMRSession, useAutoSave from Epic
   - Import EMRSessionContext from Epic
   - No new API integration code needed (100% reuse)

5. Create CernerPowerChartPage layout
   - Combine all Cerner components
   - Grid layout with dark theme
   - Responsive breakpoints

**Validation Gate**:
- [ ] SOAP editor functional (can type, switch tabs)
- [ ] Prescription/pathology panels functional
- [ ] Auto-save working (reusing Epic's hooks)
- [ ] Dark theme consistent across all components
- [ ] Performance: Auto-save <200ms (same as Epic)

**Deliverables**:
- `frontend/src/components/emr/cerner/CernerSOAPEditor.tsx` (280 lines)
- `frontend/src/components/emr/cerner/CernerPrescriptionPanel.tsx` (240 lines)
- `frontend/src/components/emr/cerner/CernerPathologyPanel.tsx` (190 lines)
- `frontend/src/pages/CernerPowerChartPage.tsx` (160 lines)

---

### Phase 3: Polish and Accessibility (3-4 hours)

**Goal**: WCAG 2.2 AA compliance, testing, production readiness

**Tasks**:
1. Dark mode contrast validation
   - Verify all text meets 7:1 ratio (AAA for dark themes)
   - Use Lighthouse + manual color picker testing
   - Fix any contrast issues

2. Implement keyboard navigation (same as Epic)
   - Reuse keyboard shortcut logic from Epic
   - Ctrl+S, Ctrl+Enter, Ctrl+Tab

3. Add ARIA labels (same as Epic)
   - All form fields have aria-label
   - Live regions for auto-save status

4. Write component tests
   - Jest + React Testing Library
   - Test dark theme rendering
   - Test user interactions
   - Reuse Epic's test patterns (change component imports only)

5. Performance optimization
   - Debounce SOAP editor onChange (same as Epic)
   - Memoize calculations
   - Lazy load autocomplete options

6. Documentation
   - Component prop documentation
   - Cerner-specific UX patterns guide
   - README for Cerner component library

**Validation Gate**:
- [ ] Lighthouse accessibility score ≥90
- [ ] Dark mode contrast meets WCAG AAA (7:1 ratio)
- [ ] Keyboard shortcuts working
- [ ] Component tests pass (≥70% coverage)
- [ ] No linting errors

**Deliverables**:
- `frontend/src/components/emr/cerner/__tests__/` (6 test files, ~500 lines)
- `frontend/src/components/emr/cerner/README.md` (120 lines)
- Updated accessibility compliance report

---

## P - PLAN (Detailed Task Breakdown)

### Phase 1 Tasks (Foundation)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **1.1** | Create `cernerTheme.ts` with dark mode theme | 1h | Frontend Engineer | None |
| **1.2** | Create CernerAppBar component | 1h | Frontend Engineer | Task 1.1 |
| **1.3** | Create CernerSidebar component (vertical tabs) | 0.75h | Frontend Engineer | Task 1.1 |
| **1.4** | Create CernerPatientBanner component | 1h | Frontend Engineer | Task 1.1 |
| **1.5** | Visual review: Compare against Cerner reference | 0.25h | Frontend Engineer | Tasks 1.2-1.4 |

**Phase 1 Total**: 4 hours

---

### Phase 2 Tasks (Core Functionality)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **2.1** | Create CernerSOAPEditor component (PowerChart tabs) | 1.5h | Frontend Engineer | Phase 1 |
| **2.2** | Add dark theme TextField styling | 0.5h | Frontend Engineer | Task 2.1 |
| **2.3** | Create CernerPrescriptionPanel component | 1.5h | Frontend Engineer | Phase 1 |
| **2.4** | Create CernerPathologyPanel component | 1h | Frontend Engineer | Phase 1 |
| **2.5** | Create CernerPowerChartPage layout | 1h | Frontend Engineer | Tasks 2.1-2.4 |
| **2.6** | Integrate with Epic's EMRSessionContext | 0.5h | Frontend Engineer | PRD_FRONTEND_001 |
| **2.7** | Test auto-save functionality | 0.5h | Frontend Engineer | Task 2.6 |

**Phase 2 Total**: 6.5 hours

---

### Phase 3 Tasks (Polish and Accessibility)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **3.1** | Dark mode contrast validation (Lighthouse + manual) | 0.75h | Frontend Engineer | Phase 2 |
| **3.2** | Implement keyboard shortcuts (reuse Epic logic) | 0.5h | Frontend Engineer | Phase 2 |
| **3.3** | Add ARIA labels (reuse Epic patterns) | 0.75h | Frontend Engineer | Phase 2 |
| **3.4** | Write component tests (6 components) | 2.5h | Frontend Engineer | Phase 2 |
| **3.5** | Run Lighthouse accessibility audit | 0.5h | Frontend Engineer | All above |
| **3.6** | Performance optimization (debounce, memoization) | 0.75h | Frontend Engineer | Phase 2 |
| **3.7** | Write documentation (README + JSDoc) | 0.75h | Frontend Engineer | All above |

**Phase 3 Total**: 6.5 hours

---

### Total Effort Summary

| Phase | Tasks | Effort | Key Deliverable |
|-------|-------|--------|-----------------|
| **Phase 1** | Foundation | 4h | Theme + 3 basic components |
| **Phase 2** | Core | 6.5h | SOAP editor + panels (dark theme) |
| **Phase 3** | Polish | 6.5h | WCAG compliance + tests |
| **TOTAL** | - | **17h** | Production-ready Cerner UI |

**Note**: Original estimate was 10-14 hours. Revised to 17 hours after detailed task breakdown. However, 60% code reuse from Epic (hooks, context, API logic) significantly reduces effort compared to Epic's 28 hours.

---

## H - HANDOFF (Acceptance Criteria and Delivery)

### Acceptance Criteria

#### Functional Requirements

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **F1** | Component creation | All 6 Cerner components created | Code review |
| **F2** | Cerner visual design | 95% match to Cerner reference | Designer review |
| **F3** | Dark theme | Consistent dark background, blue accents | Visual inspection |
| **F4** | Code reuse | ≥60% code reuse from Epic (hooks, context) | Code analysis |
| **F5** | Auto-save functionality | Auto-save works (reusing Epic hooks) | Manual testing |
| **F6** | SOAP editor | PowerChart nested tabs functional | Manual testing |
| **F7** | Prescription panel | PBS autocomplete works (reuse Epic data) | Manual testing |
| **F8** | Pathology panel | MBS autocomplete works | Manual testing |
| **F9** | Allergy warnings | Dark theme alerts display correctly | Test with mock patient |
| **F10** | Session state | Draft data persists (reusing Epic context) | Refresh test |

#### Quality Requirements

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **Q1** | Test coverage | ≥70% component coverage | Jest coverage report |
| **Q2** | Test pass rate | 100% (zero-tolerance) | `npm test` |
| **Q3** | Type safety | 0 TypeScript errors | `npx tsc --noEmit` |
| **Q4** | Linting | 0 ESLint errors | `npm run lint` |

#### Performance Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| **P1** | Auto-save latency | <200ms (same as Epic) | Chrome DevTools |
| **P2** | Initial page load | <1 second (LCP) | Lighthouse |
| **P3** | Dark theme rendering | No FOUC (flash of unstyled content) | Visual inspection |

#### Accessibility Requirements (WCAG 2.2 AA)

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **A1** | Lighthouse score | ≥90 accessibility score | Lighthouse audit |
| **A2** | Dark mode contrast | 7:1 ratio for normal text (AAA) | Lighthouse + manual |
| **A3** | Keyboard navigation | All functions accessible via keyboard | Manual testing |
| **A4** | Screen reader | NVDA/JAWS compatible | Manual testing |
| **A5** | ARIA labels | All form fields labeled | axe-core scan |

---

### Testing Requirements

#### Unit Tests (Reuse Epic Test Patterns)

```typescript
// File: frontend/src/components/emr/cerner/__tests__/CernerSOAPEditor.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { cernerTheme } from '@/theme/cernerTheme';
import { CernerSOAPEditor } from '../CernerSOAPEditor';

// Wrap component in Cerner theme for dark mode testing
const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={cernerTheme}>
      {component}
    </ThemeProvider>
  );
};

describe('CernerSOAPEditor', () => {
  it('renders all 4 SOAP tabs', () => {
    renderWithTheme(<CernerSOAPEditor draft={{}} onChange={jest.fn()} />);

    expect(screen.getByText('S - Subjective')).toBeInTheDocument();
    expect(screen.getByText('O - Objective')).toBeInTheDocument();
    expect(screen.getByText('A - Assessment')).toBeInTheDocument();
    expect(screen.getByText('P - Plan')).toBeInTheDocument();
  });

  it('applies dark theme styles', () => {
    const { container } = renderWithTheme(<CernerSOAPEditor draft={{}} onChange={jest.fn()} />);

    const paper = container.querySelector('.MuiPaper-root');
    const styles = window.getComputedStyle(paper!);

    expect(styles.backgroundColor).toBe('rgb(45, 45, 45)');  // #2D2D2D
  });

  it('updates character count on typing (same logic as Epic)', async () => {
    const onChange = jest.fn();
    renderWithTheme(<CernerSOAPEditor draft={{ subjective: '' }} onChange={onChange} />);

    const textarea = screen.getByLabelText(/subjective/i);
    fireEvent.change(textarea, { target: { value: 'Chief complaint' } });

    await screen.findByText(/15 characters/);
  });

  // ... (similar tests to Epic, verifying dark theme rendering)
});

// File: frontend/src/components/emr/cerner/__tests__/CernerPrescriptionPanel.test.tsx

describe('CernerPrescriptionPanel', () => {
  it('shows allergy warning with dark theme alert', () => {
    const prescriptions = [
      { medication: { name: 'Penicillin', pbs_code: '1234A' } },
    ];
    const patientAllergies = ['Penicillin'];

    renderWithTheme(
      <CernerPrescriptionPanel
        prescriptions={prescriptions}
        onAdd={jest.fn()}
        onRemove={jest.fn()}
        patientAllergies={patientAllergies}
      />
    );

    const alert = screen.getByText(/ALLERGY WARNING/);
    expect(alert).toBeInTheDocument();

    // Verify dark theme alert styling
    const alertContainer = alert.closest('.MuiAlert-root');
    const styles = window.getComputedStyle(alertContainer!);
    expect(styles.backgroundColor).toBe('rgb(61, 31, 31)');  // Dark red
  });
});
```

#### Integration Tests (Reuse Epic's API Integration Tests)

```typescript
// File: frontend/src/__tests__/CernerSession.integration.test.tsx

import { renderWithProviders } from '../test-utils';
import { CernerPowerChartPage } from '../pages/CernerPowerChartPage';

describe('Cerner Session Integration', () => {
  it('reuses Epic auto-save hooks', async () => {
    jest.useFakeTimers();
    let saveCount = 0;

    server.use(
      rest.put('/api/v1/emr/sessions/:id', (req, res, ctx) => {
        saveCount++;
        return res(ctx.json({ success: true }));
      })
    );

    renderWithProviders(<CernerPowerChartPage sessionId="123" />);

    // Type in SOAP note
    const textarea = await screen.findByLabelText(/subjective/i);
    fireEvent.change(textarea, { target: { value: 'Test note' } });

    // Fast-forward 30 seconds
    jest.advanceTimersByTime(30000);

    await waitFor(() => {
      expect(saveCount).toBe(1);  // Same behavior as Epic
    });

    jest.useRealTimers();
  });
});
```

#### Dark Mode Contrast Tests

```typescript
// File: frontend/src/theme/__tests__/cernerTheme.test.ts

import { cernerTheme } from '../cernerTheme';

describe('Cerner Theme Contrast', () => {
  it('meets WCAG AAA contrast ratio for dark mode (7:1)', () => {
    // White text on dark background
    const textColor = cernerTheme.palette.text.primary;  // #FFFFFF
    const backgroundColor = cernerTheme.palette.background.default;  // #1E1E1E

    const contrast = calculateContrastRatio(textColor, backgroundColor);

    expect(contrast).toBeGreaterThanOrEqual(7);  // WCAG AAA
  });

  it('primary blue meets WCAG AA contrast on dark background', () => {
    const blueColor = cernerTheme.palette.primary.main;  // #0066CC
    const backgroundColor = cernerTheme.palette.background.default;  // #1E1E1E

    const contrast = calculateContrastRatio(blueColor, backgroundColor);

    expect(contrast).toBeGreaterThanOrEqual(4.5);  // WCAG AA
  });
});
```

---

### Documentation Deliverables

#### 1. Cerner Component README

**File**: `frontend/src/components/emr/cerner/README.md`

```markdown
# Cerner PowerChart Components

Material-UI dark theme components for Cerner-style EMR interface.

## Key Differences from Epic

| Feature | Epic | Cerner |
|---------|------|--------|
| **Theme** | Light (beige/tan) | Dark (blue/gray) |
| **Navigation** | Sidebar (List) | Vertical Tabs |
| **Patient Banner** | Spacious | Compact |
| **Status Display** | Text + Icon | Chips |
| **Border Radius** | 4px | 8px |
| **Contrast** | WCAG AA (4.5:1) | WCAG AAA (7:1) |

## Code Reuse from Epic

This implementation reuses 60%+ code from PRD_FRONTEND_001:

**100% Reused**:
- State management (`EMRSessionContext`)
- API hooks (`useEMRSession`, `useAutoSave`, `useSubmitSession`)
- Auto-save logic
- Types (`SOAPNoteDraft`, `PrescriptionDraft`, etc.)
- Utilities (`calculateWordCount`, `formatVitalSigns`)

**New Code**:
- Cerner-specific components (dark theme styling)
- `cernerTheme.ts` (dark mode palette)

## Components

### CernerAppBar

Dark blue top navigation with compact patient context.

**Props**: Same as `EpicAppBar`

**Example**:
```tsx
<ThemeProvider theme={cernerTheme}>
  <CernerAppBar
    patient={patient}
    session={session}
    onSave={handleSave}
    onSubmit={handleSubmit}
    onExit={handleExit}
    autoSaveStatus={saveStatus}
  />
</ThemeProvider>
```

### CernerSOAPEditor

PowerChart nested tabs for SOAP note documentation.

**Props**: Same as `EpicSOAPEditor`

**Keyboard Shortcuts**: Same as Epic (Ctrl+S, Ctrl+Enter, Ctrl+Tab)

## Theme Usage

```tsx
import { cernerTheme } from './theme/cernerTheme';
import { ThemeProvider } from '@mui/material/styles';

<ThemeProvider theme={cernerTheme}>
  <CernerPowerChartPage sessionId="123" />
</ThemeProvider>
```

## Accessibility

WCAG 2.2 AAA compliant for dark mode:
- 7:1 contrast ratio (white on dark gray)
- Keyboard navigation
- Screen reader support
- ARIA labels

## Testing

```bash
npm test -- cerner
```
```

#### 2. Cerner UX Patterns Guide

**File**: `frontend/docs/CERNER_UX_PATTERNS.md`

```markdown
# Cerner PowerChart UX Patterns

## Navigation Philosophy

Cerner uses **nested tabs** instead of sidebars:

- Main sections are tabs (Chart, Orders, Results, Notes)
- Sub-sections are nested tabs (e.g., Notes → SOAP Notes)
- Epic uses sidebar navigation for main sections

## Status Indicators

Cerner uses **Chips** for status:
- Allergies: Red chip with medication name
- Auto-save: Green chip ("Saved") or gray chip ("Saving")
- Epic uses Alerts and text labels

## Color Philosophy

- **Dark theme**: Reduces eye strain for long EMR sessions
- **Blue accents**: Cerner brand color (#0066CC)
- **Compact layout**: More information density than Epic

## Typography

- Smaller font sizes than Epic (more compact)
- Same Roboto font family
- White text on dark background (WCAG AAA)

## When to Use Cerner vs Epic

**Use Cerner** if:
- Student prefers dark theme
- Student's hospital uses Cerner (e.g., some NSW Health facilities)
- Practicing compact, information-dense documentation

**Use Epic** if:
- Student prefers light theme
- Student's hospital uses Epic (e.g., some major Australian hospitals)
- Practicing spacious, detailed documentation
```

---

### Deployment Checklist

**Pre-Deployment**:
- [ ] All component tests pass (≥70% coverage)
- [ ] Lighthouse accessibility score ≥90
- [ ] Dark mode contrast validated (7:1 ratio)
- [ ] TypeScript compiles with 0 errors
- [ ] ESLint passes with 0 errors
- [ ] Visual review approved (Cerner design match ≥95%)
- [ ] Code review approved (Frontend Lead)

**Deployment Steps**:
1. [ ] Merge PR to `main` branch
2. [ ] Deploy to staging
3. [ ] Smoke test (start session, type SOAP note, auto-save works)
4. [ ] Dark theme visual check (no FOUC, contrast correct)
5. [ ] Performance test (auto-save <200ms)
6. [ ] Deploy to production
7. [ ] Monitor error logs
8. [ ] Update IMPLEMENTATION_STATUS.md

**Post-Deployment**:
- [ ] Monitor auto-save success rate (target >99%)
- [ ] Monitor dark theme rendering (no visual bugs)
- [ ] Collect user feedback (student preferences: Epic vs Cerner)

---

### Success Validation

**Definition of Done**:

✅ **Functional**:
- All 6 Cerner components created
- Dark theme consistent (blue accents, dark background)
- Auto-save working (reusing Epic hooks)
- SOAP editor, prescription panel, pathology panel functional

✅ **Code Reuse**:
- ≥60% code reuse from Epic (hooks, context, types)
- EMRSessionContext shared between Epic and Cerner

✅ **Quality**:
- Test coverage ≥70%
- Test pass rate 100%
- 0 TypeScript errors
- 0 ESLint errors

✅ **Performance**:
- Auto-save <200ms (same as Epic)
- Initial page load <1s

✅ **Accessibility**:
- Lighthouse score ≥90
- WCAG AAA contrast (7:1 for dark mode)
- Keyboard navigation working
- Screen reader compatible

✅ **Design**:
- Cerner visual design match ≥95%
- Dark blue/gray color scheme accurate
- PowerChart nested tabs implemented

**Acceptance Sign-Off**:
- [ ] Frontend Engineer: Code complete, tests passing
- [ ] PM Coordinator: Requirements met
- [ ] Designer: Visual design approved
- [ ] QA: Accessibility testing passed

---

## Related PRDs

**Depends On**:
- PRD_BACKEND_001: EMR Database Migration
- PRD_BACKEND_002: EMR Session API
- PRD_FRONTEND_001: Epic UI Migration (reuses hooks, context, types)

**Blocks**:
- PRD_FRONTEND_003: EMR Dashboard Integration (needs both Epic and Cerner components)

**Integrates With**:
- PRD_FRONTEND_001: Shares state management and API integration
- PRD_FRONTEND_004: EMR Validation Display

---

**End of PRD_FRONTEND_002**

**Next Steps**: After this PRD is approved, move to PRD_FRONTEND_003 (EMR Dashboard Integration).

**Total Frontend PRDs**: 2 of 4 complete (50%)
**Total Project PRDs**: 6 of 14 complete (43%)
