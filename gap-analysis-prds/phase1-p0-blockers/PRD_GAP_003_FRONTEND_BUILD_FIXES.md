# PRD_GAP_003: Frontend Build Fixes (TypeScript Errors)

**Priority**: P0 - CRITICAL BLOCKER
**Estimated Effort**: 1 hour
**Dependencies**: None
**Owner**: flutter-desktop-expert

---

## 1. REQUEST (What & Why)

### Problem Statement
Production build **FAILS** with 19 TypeScript errors, blocking deployment.

### Current Errors
```
ERROR in src/hooks/useAutoSave.ts:40:31
Cannot find module '../api/axiosInstance' or its corresponding type declarations.

ERROR in src/components/OSCEVideoResources.tsx:18:23
Cannot find module 'lucide-react' or its corresponding type declarations.

ERROR in src/components/osce/AMCRubricDisplay.tsx:209:15
Property 'item' does not exist on type 'GridProps'. Did you mean 'size'?

+ 16 more errors (unused variables, type mismatches)
```

---

## 2. IMPLEMENTATION TASKS

### Task 1: Fix Import Path (5 minutes)
**File**: `frontend/src/hooks/useAutoSave.ts:40`
```typescript
// BEFORE:
import { axiosInstance } from '../api/axiosInstance';

// AFTER:
import { axiosInstance } from '../utils/axiosInstance';
```

### Task 2: Install Missing Packages (2 minutes)
```bash
cd /home/dev/Development/irStudy/frontend
npm install lucide-react @types/node
```

### Task 3: Fix Material-UI v7 API (15 minutes)
**File**: `frontend/src/components/osce/AMCRubricDisplay.tsx`
```tsx
// BEFORE (MUI v6 API):
import { Grid } from '@mui/material';
<Grid container spacing={2}>
  <Grid item xs={6}>  // ❌ 'item' prop removed in v7

// AFTER (MUI v7 API):
import { Grid2 } from '@mui/material';
<Grid2 container spacing={2}>
  <Grid2 size={6}>  // ✅ Use 'size' prop in v7
```

### Task 4: Remove Unused Variables (30 minutes)
Fix 9 warnings in:
- `src/pages/PerformanceDashboard.tsx`
- `src/components/dashboard/WeakAreasPanel.tsx`
- `src/context/ThemeContext.tsx`

### Task 5: Verify Build (5 minutes)
```bash
npm run build
# Expected: ✓ built in 2.5s
```

---

## 3. ACCEPTANCE CRITERIA
- [x] `npm run build` succeeds with 0 errors
- [x] 0 TypeScript errors
- [x] ≤5 warnings (not blockers)
- [x] Production bundle generated in `dist/`

---

**END OF PRD_GAP_003**
