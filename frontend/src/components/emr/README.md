# EMR Practice System Frontend Components

## Overview

This directory contains React + TypeScript + Material-UI v7 components for the EMR Practice System. The system supports two EMR interfaces: **Epic** (light theme) and **Cerner PowerChart** (dark theme).

## Component Structure

```
emr/
├── epic/                    # Epic EMR components (light theme)
│   ├── EpicAppBar.tsx       # Top navigation with patient context
│   ├── EpicSidebar.tsx      # Left navigation (Chart, Orders, Results)
│   ├── EpicPatientBanner.tsx # Patient demographics, allergies, vitals
│   ├── EpicSOAPEditor.tsx   # 4-tab SOAP note editor
│   ├── EpicPrescriptionPanel.tsx # Australian PBS medication ordering
│   ├── EpicPathologyPanel.tsx # Australian MBS pathology ordering
│   └── index.ts             # Barrel export
├── cerner/                  # Cerner PowerChart components (dark theme)
│   ├── CernerAppBar.tsx     # Dark-themed AppBar
│   ├── CernerSidebar.tsx    # Dark-themed Sidebar
│   ├── CernerPatientBanner.tsx # Dark-themed Patient Banner
│   ├── CernerSOAPEditor.tsx # Reuses Epic editor (theme-agnostic)
│   ├── CernerPrescriptionPanel.tsx # Reuses Epic panel
│   ├── CernerPathologyPanel.tsx # Reuses Epic panel
│   └── index.ts             # Barrel export
└── validation/              # Validation feedback components
    ├── ValidationStatusBanner.tsx # Real-time validation polling
    ├── AMCRubricVisualization.tsx # AMC rubric score bars
    └── index.ts             # Barrel export
```

## Themes

### Epic Theme (`/themes/epicTheme.ts`)
- **Primary:** Beige/tan (#D4C5A9) - Epic signature color
- **Secondary:** Brown (#8B7355) - Warm accent
- **Background:** Off-white (#FAFAF8) - Reduces eye strain
- **Mode:** Light
- **Border Radius:** 4px (minimal, clinical appearance)

### Cerner Theme (`/themes/cernerTheme.ts`)
- **Primary:** Blue (#0066CC) - Cerner signature color
- **Secondary:** Light blue (#00A3E0) - Accent
- **Background:** Dark gray (#1E1E1E) - Reduces eye strain
- **Mode:** Dark
- **Border Radius:** 8px (modern, friendly appearance)

## Usage Examples

### Epic EMR Session Page

```typescript
import React, { useState } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { epicTheme } from '../../themes/epicTheme';
import {
  EpicAppBar,
  EpicSidebar,
  EpicPatientBanner,
  EpicSOAPEditor,
  EpicPrescriptionPanel,
  EpicPathologyPanel,
} from '../../components/emr/epic';
import { useAutoSave } from '../../hooks/useAutoSave';

const EpicEMRPage = () => {
  const [draft, setDraft] = useState<SOAPNoteDraft>({
    subjective: '',
    objective: '',
    assessment: '',
    plan: '',
    prescriptions: [],
    pathology_orders: [],
    imaging_orders: [],
  });

  const [activeSection, setActiveSection] = useState<'chart' | 'orders' | 'results'>('chart');

  // Auto-save hook (debounced 5 seconds)
  const { saveStatus } = useAutoSave({
    sessionId: 'session-uuid',
    debounceMs: 5000,
    maxWaitMs: 30000,
  });

  const handleSOAPChange = (field: keyof SOAPNoteDraft, value: string) => {
    setDraft({ ...draft, [field]: value });
    // Auto-save triggered automatically
  };

  return (
    <ThemeProvider theme={epicTheme}>
      <EpicAppBar
        patient={mockPatient}
        onSave={handleManualSave}
        onSubmit={handleSubmit}
        onExit={handleExit}
        autoSaveStatus={saveStatus}
      />

      <Box display="flex">
        <EpicSidebar
          activeSection={activeSection}
          onSectionChange={setActiveSection}
        />

        <Box flex={1} p={3}>
          <EpicPatientBanner patient={mockPatient} />

          {activeSection === 'chart' && (
            <EpicSOAPEditor
              sessionId="session-uuid"
              draft={draft}
              onChange={handleSOAPChange}
            />
          )}

          {activeSection === 'orders' && (
            <>
              <EpicPrescriptionPanel
                prescriptions={draft.prescriptions}
                onChange={(prescriptions) =>
                  setDraft({ ...draft, prescriptions })
                }
              />
              <EpicPathologyPanel
                pathologyOrders={draft.pathology_orders}
                onChange={(pathology_orders) =>
                  setDraft({ ...draft, pathology_orders })
                }
              />
            </>
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
};
```

### Cerner PowerChart Session Page

```typescript
import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { cernerTheme } from '../../themes/cernerTheme';
import {
  CernerAppBar,
  CernerSidebar,
  CernerPatientBanner,
  CernerSOAPEditor,
} from '../../components/emr/cerner';

const CernerEMRPage = () => {
  // Same logic as Epic, just different components
  return (
    <ThemeProvider theme={cernerTheme}>
      <CernerAppBar {...props} />
      {/* Rest of layout identical to Epic */}
    </ThemeProvider>
  );
};
```

### Validation Display

```typescript
import React from 'react';
import {
  ValidationStatusBanner,
  AMCRubricVisualization,
} from '../../components/emr/validation';

const EMRValidationPage = ({ validationId }) => {
  const [validationResult, setValidationResult] = useState(null);

  return (
    <Box>
      <ValidationStatusBanner
        validationId={validationId}
        onComplete={(result) => setValidationResult(result)}
      />

      {validationResult && (
        <AMCRubricVisualization scores={validationResult.amc_rubric_scores} />
      )}
    </Box>
  );
};
```

## Key Features

### 1. Auto-Save Integration
- Uses `useAutoSave` hook (already exists in `/hooks/useAutoSave.ts`)
- Debounced by 5 seconds (prevents API spam)
- Force save after 30 seconds even if user still typing
- Visual status indicator in AppBar

### 2. Australian Medical Standards
- **PBS medications:** Paracetamol (NOT acetaminophen), Salbutamol (NOT albuterol)
- **MBS pathology:** Australian test names and item codes
- **AHPRA compliance:** Documentation standards validation

### 3. Accessibility (WCAG 2.2 AA)
- Keyboard navigation for all components
- ARIA labels for screen readers
- Focus management
- Color contrast ratios >4.5:1
- Status announcements with `aria-live`

### 4. Performance
- Component lazy loading support
- Optimized re-renders with React.memo where appropriate
- Debounced auto-save (<200ms p95 target)
- Material-UI sx prop for zero-runtime CSS

### 5. Code Reuse
- Cerner components reuse 60% of Epic logic
- SOAPEditor, PrescriptionPanel, PathologyPanel are theme-agnostic
- Only AppBar, Sidebar, PatientBanner are theme-specific

## API Integration

All components integrate with backend APIs from PRD_BACKEND_002:

- `POST /api/v1/emr/sessions/start` - Start new session
- `PUT /api/v1/emr/sessions/{id}` - Auto-save session data
- `POST /api/v1/emr/sessions/{id}/submit` - Submit for validation
- `GET /api/v1/emr/validation/{id}` - Poll validation status

## Type Definitions

See `/types/emr.ts` for complete type definitions:
- `EMRSession` - Session model
- `SOAPNoteDraft` - SOAP note structure
- `PrescriptionDraft` - PBS medication
- `PathologyOrderDraft` - MBS pathology test
- `ValidationResult` - AMC rubric scores

## Testing

Unit tests for components should be added:

```bash
# Run tests
npm test src/components/emr

# Coverage
npm run test:coverage
```

## Implementation Status

- ✅ Epic UI components (6 components + theme)
- ✅ Cerner UI components (6 components + theme)
- ✅ Validation display components (2 components)
- ✅ Type definitions (emr.ts)
- ✅ Theme configurations (epicTheme.ts, cernerTheme.ts)
- ⏳ Dashboard EMR metrics integration (Phase 4)
- ⏳ Routing and page integration (Phase 6)

## Next Steps

1. **Dashboard Integration** - Add EMR metrics to dashboard
2. **Routing** - Create `/emr/epic` and `/emr/cerner` routes
3. **API Mocking** - Add MSW handlers for development
4. **Unit Tests** - Add React Testing Library tests
5. **E2E Tests** - Add Playwright tests for full EMR workflow

## Australian Medical Terminology Reference

| ❌ American | ✅ Australian |
|------------|--------------|
| Acetaminophen | Paracetamol |
| Albuterol | Salbutamol |
| Epinephrine | Adrenaline |
| Tylenol | Panadol |
| ER | ED (Emergency Department) |

## Resources

- [AMC Clinical Examination Standards](https://www.amc.org.au/)
- [PBS (Pharmaceutical Benefits Scheme)](https://www.pbs.gov.au/)
- [MBS (Medicare Benefits Schedule)](https://www.mbsonline.gov.au/)
- [Material-UI v7 Docs](https://mui.com/)
- [React 19 Docs](https://react.dev/)
