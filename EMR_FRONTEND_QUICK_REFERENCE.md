# EMR Frontend Quick Reference

## Files Created (21 total)

### Themes (2 files)
- `/frontend/src/themes/epicTheme.ts` (170 lines) - Light theme, beige
- `/frontend/src/themes/cernerTheme.ts` (180 lines) - Dark theme, blue

### Epic Components (7 files)
- `/frontend/src/components/emr/epic/EpicAppBar.tsx` (178 lines)
- `/frontend/src/components/emr/epic/EpicSidebar.tsx` (112 lines)
- `/frontend/src/components/emr/epic/EpicPatientBanner.tsx` (145 lines)
- `/frontend/src/components/emr/epic/EpicSOAPEditor.tsx` (178 lines)
- `/frontend/src/components/emr/epic/EpicPrescriptionPanel.tsx` (230 lines)
- `/frontend/src/components/emr/epic/EpicPathologyPanel.tsx` (220 lines)
- `/frontend/src/components/emr/epic/index.ts` (10 lines)

### Cerner Components (7 files)
- `/frontend/src/components/emr/cerner/CernerAppBar.tsx` (165 lines)
- `/frontend/src/components/emr/cerner/CernerSidebar.tsx` (105 lines)
- `/frontend/src/components/emr/cerner/CernerPatientBanner.tsx` (130 lines)
- `/frontend/src/components/emr/cerner/CernerSOAPEditor.tsx` (3 lines - reuses Epic)
- `/frontend/src/components/emr/cerner/CernerPrescriptionPanel.tsx` (3 lines - reuses Epic)
- `/frontend/src/components/emr/cerner/CernerPathologyPanel.tsx` (3 lines - reuses Epic)
- `/frontend/src/components/emr/cerner/index.ts` (10 lines)

### Validation Components (3 files)
- `/frontend/src/components/emr/validation/ValidationStatusBanner.tsx` (116 lines)
- `/frontend/src/components/emr/validation/AMCRubricVisualization.tsx` (180 lines)
- `/frontend/src/components/emr/validation/index.ts` (5 lines)

### Dashboard Components (2 files)
- `/frontend/src/components/dashboard/EMRMetricsGrid.tsx` (95 lines)
- `/frontend/src/components/dashboard/RecentEMRSessionsList.tsx` (165 lines)

### Types (1 file)
- `/frontend/src/types/emr.ts` (220 lines)

### Documentation (1 file)
- `/frontend/src/components/emr/README.md` (350 lines)

---

## Import Examples

### Epic Components
```typescript
import { epicTheme } from '@/themes/epicTheme';
import {
  EpicAppBar,
  EpicSidebar,
  EpicPatientBanner,
  EpicSOAPEditor,
  EpicPrescriptionPanel,
  EpicPathologyPanel,
} from '@/components/emr/epic';
```

### Cerner Components
```typescript
import { cernerTheme } from '@/themes/cernerTheme';
import {
  CernerAppBar,
  CernerSidebar,
  CernerPatientBanner,
  CernerSOAPEditor,
  CernerPrescriptionPanel,
  CernerPathologyPanel,
} from '@/components/emr/cerner';
```

### Validation Components
```typescript
import {
  ValidationStatusBanner,
  AMCRubricVisualization,
} from '@/components/emr/validation';
```

### Dashboard Components
```typescript
import { EMRMetricsGrid } from '@/components/dashboard/EMRMetricsGrid';
import { RecentEMRSessionsList } from '@/components/dashboard/RecentEMRSessionsList';
```

### Types
```typescript
import {
  EMRSession,
  SOAPNoteDraft,
  PrescriptionDraft,
  PathologyOrderDraft,
  ValidationResult,
  AMCRubricScore,
  EMRDashboardMetrics,
} from '@/types/emr';
```

### Existing Hooks
```typescript
import { useAutoSave } from '@/hooks/useAutoSave'; // Already exists!
```

---

## Component Props Quick Reference

### EpicAppBar / CernerAppBar
```typescript
<EpicAppBar
  patient={mockPatient}
  onSave={() => {}}
  onSubmit={() => {}}
  onExit={() => {}}
  autoSaveStatus="saved" // 'idle' | 'saving' | 'saved' | 'error'
  isSubmitting={false}
/>
```

### EpicSidebar / CernerSidebar
```typescript
<EpicSidebar
  activeSection="chart" // 'chart' | 'orders' | 'results'
  onSectionChange={(section) => setActiveSection(section)}
  open={true}
/>
```

### EpicPatientBanner / CernerPatientBanner
```typescript
<EpicPatientBanner
  patient={mockPatient}
  compact={false}
/>
```

### EpicSOAPEditor / CernerSOAPEditor
```typescript
<EpicSOAPEditor
  sessionId="uuid"
  draft={soapDraft}
  onChange={(field, value) => setDraft({ ...draft, [field]: value })}
  validationFeedback={['Missing red flags', 'Add differential']}
  readonly={false}
/>
```

### EpicPrescriptionPanel / CernerPrescriptionPanel
```typescript
<EpicPrescriptionPanel
  prescriptions={draft.prescriptions}
  onChange={(prescriptions) => setDraft({ ...draft, prescriptions })}
  readonly={false}
/>
```

### EpicPathologyPanel / CernerPathologyPanel
```typescript
<EpicPathologyPanel
  pathologyOrders={draft.pathology_orders}
  onChange={(pathology_orders) => setDraft({ ...draft, pathology_orders })}
  readonly={false}
/>
```

### ValidationStatusBanner
```typescript
<ValidationStatusBanner
  validationId="uuid"
  onComplete={(result) => setValidationResult(result)}
/>
```

### AMCRubricVisualization
```typescript
<AMCRubricVisualization
  scores={validationResult.amc_rubric_scores}
/>
```

### EMRMetricsGrid
```typescript
<EMRMetricsGrid
  metrics={dashboardMetrics}
  isLoading={isLoading}
  error={error}
/>
```

### RecentEMRSessionsList
```typescript
<RecentEMRSessionsList
  sessions={recentSessions}
  isLoading={isLoading}
  error={error}
/>
```

---

## Auto-Save Hook Usage

```typescript
import { useAutoSave } from '@/hooks/useAutoSave';

const { saveStatus, debouncedSave } = useAutoSave({
  sessionId: 'uuid',
  debounceMs: 5000,     // 5 second debounce
  maxWaitMs: 30000,     // Force save after 30s
  onSaveSuccess: () => console.log('Saved!'),
  onSaveError: (error) => console.error(error),
});

// Trigger save on change (debounced automatically)
const handleChange = (field: string, value: string) => {
  setDraft({ ...draft, [field]: value });
  debouncedSave({ [field]: value });
};

// Display status in AppBar
<EpicAppBar autoSaveStatus={saveStatus} />
```

---

## Theme Usage

```typescript
import { ThemeProvider } from '@mui/material/styles';
import { epicTheme } from '@/themes/epicTheme';
import { cernerTheme } from '@/themes/cernerTheme';

// Epic session
<ThemeProvider theme={epicTheme}>
  <EpicAppBar {...props} />
</ThemeProvider>

// Cerner session
<ThemeProvider theme={cernerTheme}>
  <CernerAppBar {...props} />
</ThemeProvider>
```

---

## Australian Medical Terminology

| ❌ American | ✅ Australian |
|------------|--------------|
| Acetaminophen | Paracetamol |
| Albuterol | Salbutamol |
| Epinephrine | Adrenaline |
| Tylenol | Panadol |
| ER | ED (Emergency Department) |

---

## Common PBS Medications (Built-in)

1. Paracetamol 500mg tablets
2. Ibuprofen 200mg/400mg tablets
3. Salbutamol 100mcg inhaler
4. Amoxicillin 500mg capsules
5. Cefalexin 500mg capsules
6. Atorvastatin 20mg tablets
7. Metformin 500mg tablets
8. Ramipril 5mg tablets
9. Omeprazole 20mg capsules
10. Aspirin 100mg tablets
11. Amlodipine 5mg tablets

---

## Common MBS Pathology Tests (Built-in)

1. Full Blood Count (FBC)
2. Urea and Electrolytes (UEC)
3. Liver Function Tests (LFTs)
4. C-Reactive Protein (CRP)
5. Erythrocyte Sedimentation Rate (ESR)
6. Thyroid Function Tests (TFTs)
7. Lipid Panel
8. HbA1c
9. Fasting Blood Glucose
10. Coagulation Studies (INR, APTT)
11. Blood Cultures
12. Urinalysis
13. Urine Microscopy & Culture
14. Troponin
15. D-Dimer
16. Vitamin B12 & Folate
17. Iron Studies

---

## API Endpoints (Backend Integration)

```typescript
// Session Management
POST   /api/v1/emr/sessions/start        // Start new session
GET    /api/v1/emr/sessions/:id          // Get session
PUT    /api/v1/emr/sessions/:id          // Auto-save session
POST   /api/v1/emr/sessions/:id/submit   // Submit for validation

// Validation
GET    /api/v1/emr/validation/:id        // Get validation status (polling)

// Dashboard
GET    /api/v1/emr/dashboard/metrics     // Get EMR metrics
GET    /api/v1/emr/dashboard/sessions    // Get recent sessions
```

---

## Validation Commands

```bash
# Type check (from /frontend)
npx tsc --noEmit

# Lint
npm run lint

# Build
npm run build

# Dev server
npm run dev
# Visit: http://localhost:5173
```

---

## Status Summary

✅ Epic UI (6 components + theme) - COMPLETE
✅ Cerner UI (6 components + theme) - COMPLETE
✅ Validation display (2 components) - COMPLETE
✅ Types (emr.ts) - COMPLETE
✅ Auto-save hook - ALREADY EXISTS (reused)
⏳ Dashboard integration (2 components created, needs integration) - 50%
⏳ Routing (/emr/epic, /emr/cerner) - PENDING

**Overall: 75% Complete**
