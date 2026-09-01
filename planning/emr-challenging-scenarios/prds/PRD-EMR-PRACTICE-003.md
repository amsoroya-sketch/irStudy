# PRD-EMR-PRACTICE-003: EMR Frontend — Scenario Brief + Validation Results Page

**PRD ID**: PRD-EMR-PRACTICE-003
**Project**: irStudy Medical Education Platform (EMR + AI OSCE)
**Project Location**: /home/dev/Development/irStudy
**Working Directory**: /home/dev/Development/irStudy
**Technology Stack**: React 19 + TypeScript + Vite + MUI v7 + TanStack Query (Vitest + Playwright)
**Repository**: git@github.com-sketch:amsoroya-sketch/irStudy.git
**Status**: Ready for Implementation
**Created**: 2026-08-26
**Standards**: T-RALPH V2.6
**Prescription**: low
**Estimated Effort**: 5-6 hours
**Depends on**: PRD-EMR-PRACTICE-001 (real validation result shape from the backend)

---

## Project Context (CRITICAL for Ralph Execution)

**IMPORTANT**: This PRD is for the **irStudy** project. (The project `.claude/CLAUDE.md` mislabels the
frontend as "Flutter Desktop"; the ACTUAL frontend is **React 19 + TypeScript + Vite + MUI** — build
against that.)

**Project Constraints File**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
**Project CLAUDE.md File**: `/home/dev/Development/irStudy/.claude/CLAUDE.md`

**Technology Stack**:
- **Frontend**: React 19, TypeScript ~5.9, Vite 7, MUI v7, TanStack Query v5, react-router-dom v7
- **Testing**: Vitest + React Testing Library (unit/component), Playwright (e2e)

**Ralph Execution Command**:
```bash
cd /home/dev/Development/ralph-dashboard
./scripts/ralph_loop.sh --calls 40 --prompt /home/dev/Development/irStudy/planning/emr-challenging-scenarios/prds/PRD-EMR-PRACTICE-003.md
```

---

## 0 - DISCOVERY

**Ponytail Principle**: Both results-display components already exist but are orphaned; the results
page just needs building + routing. The scenario data is already fetched, just not rendered.

### 0.1 Existing Code Search (evidence — verified 2026-08-26)

```bash
# Orphaned display components (built, never imported by a page)
ls frontend/src/components/emr/validation/
# → ValidationStatusBanner.tsx (polls GET /emr/validation/:id, shows overall_score + AHPRA),
#   AMCRubricVisualization.tsx (5-category 0-10 bars)
grep -rn "ValidationStatusBanner\|AMCRubricVisualization" frontend/src/pages frontend/src/App.tsx
# → 0 matches (no page uses them)

# Submit already navigates to a route that does NOT exist
grep -rn "navigate('/emr/validation" frontend/src/pages/emr
# → EpicEMRPage.tsx / CernerEMRPage.tsx navigate('/emr/validation/:sessionId')
grep -n "emr/validation" frontend/src/App.tsx
# → 0 matches (route missing — submit dead-ends)

# The result type already models everything we render
grep -n "interface ValidationResult\|missing_elements\|dangerous_medications" frontend/src/types/emr.ts

# Scenario data fetched but not rendered
grep -n "presenting_complaint" frontend/src/components/emr/epic/EpicPatientBanner.tsx frontend/src/pages/emr/EpicEMRPage.tsx
# → present in MockPatient type / fetched on session.patient, NOT rendered as a task/brief
```

### 0.2 Discovery Results (reuse targets)

| Component | Location | Reuse decision |
|---|---|---|
| ValidationStatusBanner | `frontend/src/components/emr/validation/ValidationStatusBanner.tsx` | COMPOSE into results page |
| AMCRubricVisualization | `frontend/src/components/emr/validation/AMCRubricVisualization.tsx` | COMPOSE into results page |
| ValidationResult type | `frontend/src/types/emr.ts` | REUSE (has pass/missing/strengths) |
| Epic/Cerner pages | `frontend/src/pages/emr/{EpicEMRPage,CernerEMRPage}.tsx` | ADD scenario brief panel |
| Router | `frontend/src/App.tsx` | ADD `/emr/validation/:sessionId` route |
| axios instance | `frontend/src/utils/axiosInstance.ts` | REUSE for the results fetch |

### 0.3 Gap Analysis
- No `/emr/validation` route + no results page → submit dead-ends.
- Display components orphaned.
- No scenario/task brief shown (`presenting_complaint` + `validation_criteria.task` never rendered).
- `sessionId` vs `validation_id` param mismatch between submit-navigate and `ValidationStatusBanner`.

### 0.5 Reference Implementations
None external — compose in-repo components.

---

## T - TESTS (Write These FIRST)

### Test Inventory
- Component (Vitest): 7 · file `frontend/src/pages/emr/__tests__/EMRValidationPage.test.tsx`
  + `frontend/src/components/emr/__tests__/ScenarioBrief.test.tsx`
- E2E (Playwright): 1 · file `frontend/tests/emr-validation.spec.ts`

### TDD Workflow (MANDATORY)
1. **RED**: write all 8 tests → confirm they FAIL (page/component/route absent).
2. **GREEN**: implement minimal code → confirm PASS.
3. **REFACTOR**: clean up → tests still PASS.
Workflow is **RED → GREEN → REFACTOR**. Write NO implementation before the tests exist and fail.

#### Test 1: EMRValidationPage renders PASS state (score + PASS)
#### Test 2: EMRValidationPage renders FAIL state
#### Test 3: lists critical errors committed
#### Test 4: lists missing elements
#### Test 5: renders rubric bars from amc_rubric_scores
#### Test 6: shows strengths and areas for improvement
#### Test 7: ScenarioBrief renders presenting complaint + task
#### Test 8: E2E — nitrates-in-STEMI submission → results page shows FAIL

### Tests (representative full code)

```tsx
// FILE: frontend/src/pages/emr/__tests__/EMRValidationPage.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { EMRValidationPage } from '../EMRValidationPage';

const wrap = (result: any) => {
  vi.spyOn(global, 'fetch').mockResolvedValue({ ok: true, json: async () => result } as any);
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/emr/validation/sess-1']}>
        <Routes><Route path="/emr/validation/:sessionId" element={<EMRValidationPage />} /></Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

const PASS = { status: 'completed', overall_score: 12, pass_fail: true,
  amc_rubric_scores: [{ category: 'documentation', score: 8, feedback: 'good' }],
  missing_elements: [], critical_errors_committed: [], strengths: ['structured'],
  areas_for_improvement: ['more detail'] };
const FAIL = { ...PASS, overall_score: 6, pass_fail: false,
  missing_elements: ['aortic dissection considered'],
  critical_errors_committed: ['nitrates given in RV infarct'] };

it('Test 1: renders PASS state', async () => {
  wrap(PASS);
  await waitFor(() => expect(screen.getByText(/pass/i)).toBeInTheDocument());
  expect(screen.getByText(/12/)).toBeInTheDocument();
});
it('Test 2: renders FAIL state', async () => {
  wrap(FAIL);
  await waitFor(() => expect(screen.getByText(/fail/i)).toBeInTheDocument());
});
it('Test 3: lists critical errors committed', async () => {
  wrap(FAIL);
  await waitFor(() => expect(screen.getByText(/nitrates given in RV infarct/i)).toBeInTheDocument());
});
it('Test 4: lists missing elements', async () => {
  wrap(FAIL);
  await waitFor(() => expect(screen.getByText(/aortic dissection considered/i)).toBeInTheDocument());
});
it('Test 5: renders rubric bars from amc_rubric_scores', async () => {
  wrap(PASS);
  await waitFor(() => expect(screen.getByText(/documentation/i)).toBeInTheDocument());
});
it('Test 6: shows strengths and areas for improvement', async () => {
  wrap(PASS);
  await waitFor(() => expect(screen.getByText(/more detail/i)).toBeInTheDocument());
});
```

```tsx
// FILE: frontend/src/components/emr/__tests__/ScenarioBrief.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ScenarioBrief } from '../ScenarioBrief';

it('Test 7: renders presenting complaint and task', () => {
  render(<ScenarioBrief presentingComplaint="Central chest pain 40 min"
                        task="Document assessment and initial management." />);
  expect(screen.getByText(/central chest pain/i)).toBeInTheDocument();
  expect(screen.getByText(/document assessment/i)).toBeInTheDocument();
});
```

```ts
// FILE: frontend/tests/emr-validation.spec.ts  (Playwright — seeded stack, real data)
import { test, expect } from '@playwright/test';

test('E2E: nitrates-in-STEMI submission -> results page shows FAIL', async ({ page }) => {
  await page.goto('/login'); // seeded user
  // ... auth helper ...
  await page.goto('/emr/start');
  await page.getByRole('button', { name: /start new emr session/i }).click();
  await page.getByRole('heading', { name: /epic/i }).click();
  // scenario brief visible
  await expect(page.getByText(/document/i)).toBeVisible();
  // document a deliberately failing note (gives nitrates)
  await page.getByRole('tab', { name: /plan/i }).click();
  await page.getByRole('textbox').fill('Give GTN nitrates. Aspirin. Troponin.');
  await page.getByRole('button', { name: /submit for review/i }).click();
  // results page
  await expect(page).toHaveURL(/\/emr\/validation\//);
  await expect(page.getByText(/fail/i)).toBeVisible();
});
```

### Test Execution
```bash
cd frontend
npx vitest run src/pages/emr src/components/emr
npx playwright test tests/emr-validation.spec.ts   # against seeded stack
```

---

## R - REQUEST
As a student, after I submit my EMR documentation I want to **see my result** — PASS/FAIL, my score,
which required details I missed, and any critical error I made — instead of hitting a dead route. And
at the start I want to **see the scenario and my task**, not just demographics.

---

## A - ARCHITECTURE
- **`frontend/src/components/emr/ScenarioBrief.tsx`** — MUI card: presenting complaint + task
  (+ difficulty/specialty chips). Rendered at the top of `EpicEMRPage`/`CernerEMRPage` body
  (beside the existing conversion Alert, ~lines 173-188) from `session.patient.presenting_complaint`
  and `session.patient.validation_criteria.task`.
- **`frontend/src/pages/emr/EMRValidationPage.tsx`** — fetches the session/validation result via
  `axiosInstance` (resolve the `sessionId`→`validation_id` correctly), composes `ValidationStatusBanner`
  + `AMCRubricVisualization`, and renders `pass_fail`, `missing_elements`,
  `critical_errors_committed`, `strengths`, `areas_for_improvement` from `ValidationResult`.
- **Route**: register `/emr/validation/:sessionId` in `frontend/src/App.tsx` behind `ProtectedRoute`.
- **Param fix**: submit navigates with `sessionId`; either make the page resolve the session→validation
  id, or update `ValidationStatusBanner` to accept a `sessionId`. Pick one and keep it consistent.

---

## L - LOOP

### Loop Execution Strategy
**CRITICAL**: 3-phase sequential TDD (RED → GREEN → REFACTOR each phase). No phase advances with TS
errors / failing tests.

**Recovery Protocol**: if a phase is blocked, fix it in the CURRENT phase; never advance with
blockers; record the blocker + resolution in the H section.

**Dependency chain**:
```
Phase 1 (ScenarioBrief component + wire into Epic/Cerner pages)
    ↓ provides: student sees scenario + task
Phase 2 (EMRValidationPage composing orphaned validation components)
    ↓ provides: results rendering from ValidationResult
Phase 3 (route + param fix + e2e)
    ↓ provides: submit -> results page, no dead-end
COMPLETE (7 component tests + 1 e2e passing)
```

### Phase 1: ScenarioBrief (prescription low)
- GOAL: brief panel renders presenting complaint + task; wired into both EMR pages.
- CONSTRAINTS: MUI + TS strict, no `any`; reuse existing page layout.
- RUBRIC: Test 7 passes; `npx tsc -b` clean.

### Phase 2: EMRValidationPage (prescription low)
- GOAL: compose the two orphaned components + render pass/fail, missing, critical errors, strengths.
- CONSTRAINTS: reuse `ValidationResult` type + both display components (don't rebuild); TanStack Query for fetch.
- RUBRIC: Tests 1-6 pass.

### Phase 3: Route + param + e2e (prescription low)
- GOAL: `/emr/validation/:sessionId` registered; submit reaches results; e2e FAIL path green.
- CONSTRAINTS: fix the sessionId/validation_id mismatch consistently.
- RUBRIC: e2e test passes on the seeded stack.

---

## P - PLAN
1. Tests (RED): `EMRValidationPage.test.tsx`, `ScenarioBrief.test.tsx`, `emr-validation.spec.ts`.
2. `frontend/src/components/emr/ScenarioBrief.tsx` + wire into `EpicEMRPage.tsx`/`CernerEMRPage.tsx`.
3. `frontend/src/pages/emr/EMRValidationPage.tsx`.
4. `frontend/src/App.tsx` — add route; fix param mismatch.

---

## UI Coverage

| Screen (route) | Loads w/ data | Fields | Links / nav | API(s) | Spec |
| --- | --- | --- | --- | --- | --- |
| `/emr/epic/:sessionId` (brief panel) | real MockPatient | n/a (read-only brief) | Submit → `/emr/validation/:sessionId` | `GET /emr/sessions/:id` | `frontend/src/components/emr/__tests__/ScenarioBrief.test.tsx` + `emr-validation.spec.ts` |
| `/emr/validation/:sessionId` | real validation result | n/a (read-only results) | back to dashboard | `GET /emr/sessions/:id` / `/emr/validation/:id` | `frontend/src/pages/emr/__tests__/EMRValidationPage.test.tsx` + `emr-validation.spec.ts` |

---

## H - HANDOFF

### Agent constraints
**CRITICAL — read FIRST**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md` (React/TS patterns,
no `any`, testing). Then this PRD's T section + UI Coverage. Then the two orphaned validation
components and the Epic/Cerner pages. NOTE the frontend is React (not Flutter). Agent:
**react-frontend-developer**.

### Test Results Summary
```bash
# [TO BE FILLED BY RALPH AFTER EXECUTION] — vitest + playwright (npm test / e2e)
cd frontend && npx vitest run src/pages/emr src/components/emr
cd frontend && npx playwright test tests/emr-validation.spec.ts
```

### TDD Compliance Verification
- [ ] Component + e2e tests written first, confirmed FAILING — [TO BE FILLED BY RALPH]
- [ ] All passing after implementation — [TO BE FILLED BY RALPH]

### Success Criteria
- [ ] Student sees the scenario + task at the top of the EMR editor.
- [ ] Submit navigates to a working `/emr/validation/:sessionId` results page (no dead-end).
- [ ] Results show PASS/FAIL, score, missing elements, critical errors, strengths.
- [ ] No `any` types; `npx tsc -b` clean.

### Deliverables Checklist
- [ ] `frontend/src/components/emr/ScenarioBrief.tsx` + wired into Epic/Cerner pages
- [ ] `frontend/src/pages/emr/EMRValidationPage.tsx`
- [ ] `/emr/validation/:sessionId` route in `App.tsx` (param mismatch fixed)
- [ ] Vitest specs + `frontend/tests/emr-validation.spec.ts` (Playwright)

### Quality Gates

**Frontend build & tests (scoped to this PRD's surface):**
- [ ] `cd frontend && npx tsc -b` → 0 errors
- [ ] `cd frontend && npx vitest run src/pages/emr src/components/emr/validation src/components/emr/__tests__` → passing
- [ ] `cd frontend && npx playwright test tests/emr-validation.spec.ts --list` → success

**Functional e2e (container/CI tier — seeded stack, real data):**
- [ ] `cd frontend && npx playwright test tests/emr-validation.spec.ts` → exit code 0

**Security (passes only when no secret is found):**
- [ ] `! grep -rEn "sk-ant-|api_key\s*=\s*['\"]" frontend/src/pages/emr frontend/src/components/emr` → exit code 0

**Commit — final gate:**
- [ ] `git log -1 --pretty=%s | grep -q 'PRD-EMR-PRACTICE-003'` → exit code 0

### Commit as the final gate
After every Quality Gate passes:
`git add -A && git commit -m "feat(emr): PRD-EMR-PRACTICE-003 — scenario brief + validation results page"`.
Never commit `.env`, generated reports, or scratch files.

---

## Permissions (Ralph Autonomous Execution)

<!-- RALPH-PERMISSIONS:BEGIN -->
allow:
  - Bash(cd frontend && npx vitest*:*)
  - Bash(cd frontend && npx tsc*:*)
  - Bash(cd frontend && npx playwright*:*)
  - Bash(npx vitest:*)
  - Bash(npx playwright:*)
add-dir:
  - /home/dev/Development/irStudy
<!-- RALPH-PERMISSIONS:END -->
