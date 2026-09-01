# irStudy Frontend: File Structure & Component Map

## Directory Organization

```
/home/dev/Development/irStudy/frontend/src/
├── App.tsx                          # Main app component with routing
├── main.tsx                         # React entry point
├── App.css                          # Global styles (minimal)
├── index.css                        # Global styles
│
├── api/                             # API integration layer
│   ├── client.ts                    # Axios instance
│   ├── dashboard.ts                 # Dashboard API endpoints
│   ├── mcqs.ts                      # MCQ API endpoints
│   ├── osce.ts                      # OSCE API endpoints
│   ├── studyCards.ts                # Study cards API
│   ├── personas.ts                  # Persona API (MCQ content)
│   ├── mockExams.ts                 # Mock exam API
│   ├── integration.ts               # OSCE-to-EMR converter API
│   └── permissions.ts               # RBAC permissions API
│
├── components/                      # Reusable components (organized by feature)
│   ├── citations/
│   │   └── CitationPanel.tsx        # Citation display component
│   ├── common/
│   │   └── ImageLightbox.tsx        # Image modal viewer
│   ├── dashboard/                   # Dashboard-specific components
│   │   ├── OverallProgressCard.tsx  # Top-level metrics card
│   │   ├── ModuleStatsGrid.tsx      # 4-module statistics
│   │   ├── SpecialtyBreakdownChart.tsx
│   │   ├── RecentActivityFeed.tsx
│   │   ├── RecommendationsPanel.tsx
│   │   ├── ExamReadinessGauge.tsx
│   │   ├── PerformanceChart.tsx
│   │   ├── WeakAreasPanel.tsx
│   │   ├── SpecialtyBreakdown.tsx
│   │   └── __tests__/              # Component tests
│   ├── emr/                         # EMR-specific components
│   │   ├── EpicEMRDisplay.tsx
│   │   ├── CernerEMRDisplay.tsx
│   │   └── EMRValidationDisplay.tsx
│   ├── integration/                 # Cross-module integration
│   │   └── OSCEToEMRModal.tsx       # OSCE-to-EMR converter UI
│   ├── layout/
│   │   ├── MobileBottomNav.tsx      # Mobile navigation (fixed bottom)
│   │   └── MobileBottomNav.test.tsx
│   ├── mcq/                         # MCQ-specific components
│   │   ├── MCQPracticeInterface.tsx # Main MCQ UI
│   │   ├── MCQTimer.tsx             # Question timer
│   │   └── __tests__/
│   ├── osce/                        # OSCE-specific components
│   │   ├── OSCEScenarioCard.tsx
│   │   ├── AMCRubricDisplay.tsx     # AMC scoring rubric
│   │   └── __tests__/
│   ├── study-cards/                 # Flashcard components
│   │   ├── FlashcardReview.tsx      # Main review interface
│   │   ├── FlashcardCard.tsx        # Individual card display
│   │   ├── CitationsList.tsx        # Citation list for cards
│   │   ├── QualityRating.tsx        # SM-2 quality buttons
│   │   ├── NavigationControls.tsx   # Next/prev controls
│   │   ├── LoadingStates.tsx
│   │   └── __tests__/
│   ├── ErrorBoundary.tsx            # Global error boundary
│   ├── ProtectedRoute.tsx           # Auth-protected route wrapper
│   └── PermissionGuard.tsx          # RBAC-based component visibility
│
├── context/                         # React Context (global state)
│   ├── AuthContext.tsx              # Authentication context
│   └── ThemeContext.tsx             # Theme selection context
│
├── hooks/                           # Custom React hooks
│   ├── useAuth.ts                   # Auth context hook
│   ├── useMCQs.ts                   # MCQ listing hook
│   ├── useMCQ.ts                    # Single MCQ hook
│   ├── useOSCEs.ts                  # OSCE listing hook
│   ├── useStudyCards.ts             # Study cards hook
│   ├── useDashboard.ts              # Dashboard data hook
│   ├── useEMRDashboardData.ts       # EMR metrics hook
│   ├── useUserProgress.ts           # User progress hook
│   ├── useAutoSave.ts               # Auto-save functionality
│   ├── useResponsive.ts             # Responsive breakpoint hook
│   ├── usePermissions.ts            # RBAC permissions hook
│   ├── useSM2Algorithm.ts           # SM-2 spaced repetition hook
│   ├── useWebSocket.ts              # WebSocket connection hook
│   └── __tests__/
│
├── pages/                           # Page components (routes)
│   ├── Dashboard.tsx                # Main dashboard (legacy)
│   ├── UnifiedDashboardPage.tsx     # Unified dashboard (current)
│   ├── MCQBrowser.tsx               # MCQ list/search page
│   ├── MCQAttempt.tsx               # Single MCQ page
│   ├── OSCEPractice.tsx             # OSCE practice page
│   ├── OSCESession.tsx              # Active OSCE session page
│   ├── PerformanceDashboard.tsx     # Analytics page
│   ├── Login.tsx                    # Login page
│   ├── Register.tsx                 # Registration page
│   ├── emr/
│   │   ├── StartEMRSessionPage.tsx
│   │   ├── EMRSelectSystemPage.tsx
│   │   ├── EpicEMRPage.tsx
│   │   └── CernerEMRPage.tsx
│   ├── osce/
│   │   ├── MockExamStart.tsx
│   │   ├── MockExamStation.tsx
│   │   └── MockExamResults.tsx
│   └── __tests__/
│
├── providers/
│   └── QueryProvider.tsx            # React Query setup
│
├── theme/                           # Design system / theme
│   └── theme.ts                     # MUI custom theme (colors, typography, spacing, breakpoints)
│
├── themes/                          # Alternative themes (EMR-specific)
│   ├── epicTheme.ts                 # Epic EMR theme
│   └── cernerTheme.ts               # Cerner EMR theme
│
├── types/                           # TypeScript type definitions
│   ├── api.ts                       # Generic API types
│   ├── auth.ts                      # Auth types
│   ├── citation.ts                  # Citation types
│   ├── dashboard.ts                 # Dashboard response types
│   ├── emr.ts                       # EMR types
│   ├── mcq.ts                       # MCQ types (50+ lines)
│   ├── osce.ts                      # OSCE types
│   └── study-cards.ts               # Study card types
│
├── utils/                           # Utility functions
│   ├── axiosInstance.ts             # Axios configuration
│   ├── citationParser.ts            # Parse citations into structured data
│   ├── validation.ts                # Input validation utilities
│   ├── examReadiness.ts             # Exam readiness calculations
│   └── examReadiness.test.ts        # Exam readiness tests
│
├── test/
│   └── setup.ts                     # Vitest configuration
│
├── routes.tsx                       # Route definitions with lazy loading
│
└── auth-index.ts                    # Auth utilities (legacy?)
```

---

## Component Dependency Map

```
App.tsx (Root)
├── ThemeProvider (MUI)
├── CssBaseline
├── QueryClientProvider (React Query)
└── BrowserRouter
    └── AuthProvider
        └── Suspense (with LoadingFallback)
            └── Routes
                ├── Login
                ├── Register
                └── ProtectedRoute
                    ├── UnifiedDashboard
                    │   ├── OverallProgressCard
                    │   ├── ModuleStatsGrid
                    │   ├── SpecialtyBreakdownChart
                    │   ├── RecentActivityFeed
                    │   └── RecommendationsPanel
                    ├── MCQBrowser
                    │   └── MCQCard[] (pagination)
                    ├── MCQAttempt
                    │   └── MCQPracticeInterface
                    │       ├── MCQTimer
                    │       ├── ImageLightbox (if image)
                    │       └── CitationPanel
                    ├── FlashcardReview
                    │   ├── FlashcardCard
                    │   ├── CitationsList
                    │   ├── QualityRating
                    │   └── NavigationControls
                    ├── OSCEPractice
                    ├── OSCESession
                    │   └── AMCRubricDisplay
                    ├── PerformanceDashboard
                    ├── StartEMRSessionPage
                    ├── EMRSelectSystemPage
                    ├── EpicEMRPage
                    ├── CernerEMRPage
                    ├── MockExamStart
                    ├── MockExamStation
                    └── MockExamResults
            └── MobileBottomNav (shown only on mobile <768px)
```

---

## Data Flow Patterns

### MCQ Practice Flow
```
MCQBrowser (page)
  └── useQuery('mcqs', filters) → API
      └── MCQCard[] displayed
          └── Click "Attempt"
              └── MCQAttempt (page)
                  └── useQuery('mcq', id) → API
                      └── MCQPracticeInterface (component)
                          ├── Display question + options
                          ├── Timer countdown
                          └── Submit answer
                              └── useMutation (submitAnswer) → API
                                  └── Show result + explanation + citation
```

### Study Cards Flow
```
FlashcardReview (page)
  └── useStudyCards() → API
      └── Get cards due for review
          └── FlashcardCard[] carousel
              ├── Display question
              ├── Toggle answer visibility
              └── Submit quality rating (1-5)
                  └── useMutation (reviewCard) → API
                      └── Calculate SM-2 params
                          └── Move to next card
```

### Dashboard Flow
```
UnifiedDashboardPage (page)
  ├── useDashboardOverview() → API
  │   └── DashboardOverviewResponse
  │       ├── overall_progress
  │       ├── modules (mcq, osce, emr, mock_exam)
  │       ├── specialty_breakdown[]
  │       ├── recent_activity[]
  │       └── recommendations[]
  │
  ├── useEMRDashboardData() → API (parallel)
  │   └── EMR metrics + recent sessions
  │
  └── Components rendered:
      ├── OverallProgressCard
      ├── ModuleStatsGrid (4 modules)
      ├── SpecialtyBreakdownChart
      ├── RecentActivityFeed
      ├── RecommendationsPanel
      └── ExamReadinessGauge
```

---

## State Management Pattern

### Global State (Context)
- **AuthContext**: User info, token, permissions
- **ThemeContext**: Current theme selection

### Query State (React Query)
- Caching with 5-minute default stale time
- Automatic refetch on focus
- Parallel queries for dashboard
- Query invalidation on mutations

### Local Component State (useState)
- Form inputs (filters, search)
- UI state (showAnswer, currentCardIndex, page)
- Modal state (isOpen, selectedItem)

### Custom Hooks
- `useMCQ()` - Fetch single MCQ
- `useStudyCards()` - Fetch study cards due
- `useDashboard()` - Fetch dashboard data
- `usePermissions()` - Get user permissions
- `useResponsive()` - Current breakpoint

---

## TypeScript Type System

### Entry Point
```typescript
// User authenticated
type User = {
  id: number;
  email: string;
  name: string;
  role: 'student' | 'instructor' | 'admin';
  permissions: string[];
}

// MCQ structure
interface MCQPublic {
  id: number;
  question_text: string;
  options: { A: string; B: string; C: string; D: string; E?: string };
  specialty: MedicalSpecialty;
  difficulty: DifficultyLevel;
  image_url?: string;
}

// Study card structure
interface StudyCard {
  id: number;
  question: string;
  answer: string;
  citations: StudyCardCitation[];
  tags: string[];
  sm2_params: SM2Params;
}

// Dashboard response
interface DashboardOverviewResponse {
  overall_progress: OverallProgress;
  modules: { mcq: ModuleStats; osce: ModuleStats; emr: ModuleStats; mock_exam: ModuleStats };
  specialty_breakdown: SpecialtyBreakdown[];
  recent_activity: RecentActivity[];
  recommendations: Recommendation[];
}
```

---

## Performance Optimizations

### Code Splitting
- ✓ Routes lazy-loaded with `React.lazy()`
- ✓ Dynamic imports: `import('./pages/Dashboard')`
- ✓ Suspense fallback with `LoadingFallback`

### Caching
- ✓ React Query with 5-minute default stale time
- ✓ Automatic cache invalidation on mutations
- ✓ Parallel queries for dashboard

### Responsive Images
- ✓ ImageLightbox component for modal display
- ✓ Image URL from API (backend handles CDN)
- ✓ Captions for accessibility

### Bundle Size
- MUI (Material-UI): Tree-shakable
- React Query: 30KB gzipped
- Recharts: ~40KB gzipped
- No heavy markdown libraries (yet)

---

## Testing Structure

### Unit Tests
- Component tests in `__tests__/` subdirectories
- `vitest` as test runner
- `@testing-library/react` for component testing

### Example Test Locations
- `/src/components/dashboard/__tests__/ModuleStatsGrid.test.tsx`
- `/src/components/mcq/MCQPracticeInterface.test.tsx`
- `/src/hooks/__tests__/useResponsive.test.tsx`
- `/src/utils/examReadiness.test.ts`

### Test Coverage Target
- ≥70% code coverage (irStudy requirement)
- Unit tests for hooks, utils, components
- Integration tests for user flows
- E2E tests via Playwright (if configured)

---

## Build Configuration

### Vite Configuration
- Entry: `index.html`
- Output: `dist/` directory
- TypeScript: `tsc -b` for type checking
- Linting: ESLint with TypeScript support

### Build Commands
```bash
npm run dev        # Development server
npm run build      # Production build (tsc + vite build)
npm run preview    # Preview production build
npm run lint       # ESLint check
npm test           # Run Vitest
npm test:watch     # Watch mode
npm test:ui        # Vitest UI dashboard
```

---

## Key Dependencies

### UI Framework
- `react` v19.2.0
- `react-dom` v19.2.0
- `@mui/material` v7.3.7 (component library)
- `@mui/icons-material` v7.3.8 (icons)
- `@emotion/react`, `@emotion/styled` (MUI dependency)

### Data & State
- `@tanstack/react-query` v5.90.20 (API caching)
- `axios` v1.13.4 (HTTP client)

### Routing
- `react-router-dom` v7.13.0

### Charts & Visualization
- `recharts` v2.15.4
- `@mui/x-charts` v7.29.1

### Utilities
- `react-swipeable` v7.0.2 (mobile gestures)
- `lucide-react` v0.577.0 (alternative icons)
- `workbox-window` v7.4.0 (PWA support)
- `vite-plugin-pwa` v1.2.0 (PWA configuration)

### Development
- `typescript` v5.9.3
- `vitest` v4.0.18 (unit tests)
- `@testing-library/react` v16.3.2
- `eslint` v9.39.2
- `prettier` v3.8.1

---

## Next Steps for Dr. Amir Notes

1. **Create types** in `/src/types/notes.ts`
   ```typescript
   interface StudyNote {
     id: string;
     title: string;
     content: string;        // Markdown
     category: string;
     tags: string[];
     author: string;         // "Dr. Amir"
     created_at: string;
     updated_at: string;
   }
   ```

2. **Create API hook** in `/src/hooks/useStudyNotes.ts`

3. **Create components**:
   - `/src/components/notes/NotesBrowser.tsx` (list + filters)
   - `/src/components/notes/NotesViewer.tsx` (full display)
   - `/src/components/notes/NotesCard.tsx` (preview card)
   - `/src/components/notes/TableOfContents.tsx` (TOC)

4. **Install markdown renderer**:
   ```bash
   npm install react-markdown
   ```

5. **Add routes** in `/src/routes.tsx`:
   ```typescript
   export const NotesBrowser = lazy(() => import('./pages/NotesBrowser'));
   export const NotesViewer = lazy(() => import('./pages/NotesViewer'));
   ```

6. **Add routes** in `/src/App.tsx`:
   ```typescript
   <Route path="/notes" element={<NotesBrowser />} />
   <Route path="/notes/:id" element={<NotesViewer />} />
   ```

7. **Update mobile nav** in `/src/components/layout/MobileBottomNav.tsx`
   (Add "Notes" link)

---

**Location**: `/home/dev/Development/irStudy/backend/FRONTEND_FILE_STRUCTURE.md`
**Last Updated**: 2026-05-27
**Status**: Complete
