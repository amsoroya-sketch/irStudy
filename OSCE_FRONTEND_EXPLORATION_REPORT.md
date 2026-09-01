# irStudy Frontend OSCE Implementation Exploration

**Date:** 2026-05-27  
**Focus:** Current OSCE display implementation and UI patterns

---

## 1. EXISTING OSCE COMPONENTS

### Location: `/home/dev/Development/irStudy/frontend/src/components/osce/`

**Components Found:**

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `AMCRubricDisplay.tsx` | Display AMC 15-mark rubric with scoring breakdown | 326 | Production |
| `WebSocketChat.tsx` | Real-time AI patient chat interface | 400+ | Production |
| `SessionTimer.tsx` | Countdown timer for OSCE sessions | TBD | Production |
| `SessionControls.tsx` | Pause/Resume/End session buttons | TBD | Production |
| `EmotionalStateIndicator.tsx` | Show patient emotional state during chat | 200+ | Production |
| `OSCEPracticePlaceholder.tsx` | UI placeholder for OSCE practice | TBD | Production |
| `index.ts` | Barrel export file | - | Supporting |

**Test Coverage:**
- `AMCRubricDisplay.test.tsx` - Unit tests for rubric display
- `OSCEPracticePlaceholder.test.tsx` - Tests for placeholder
- `__tests__/` directory contains additional tests

---

## 2. EXISTING OSCE PAGES

### Location: `/home/dev/Development/irStudy/frontend/src/pages/`

**OSCE-Related Pages:**

| File | Purpose | Status |
|------|---------|--------|
| `OSCEPractice.tsx` | Patient persona selector & OSCE browser | Production |
| `OSCESession.tsx` | Active OSCE session interface | Production |
| `osce/MockExamStart.tsx` | Mock exam initialization | Production |
| `osce/MockExamStation.tsx` | Individual mock exam station | Production |
| `osce/MockExamResults.tsx` | Mock exam results display | Production |

**Key Page Features:**

### OSCEPractice.tsx (477 lines)
- **Purpose:** Patient persona selection and preview
- **Features:**
  - Specialty filter (Cardiology, Emergency, General Practice, Pediatrics, Respiratory)
  - Difficulty filter (Foundation, Intermediate, Advanced)
  - Patient details card showing demographics, clinical info, chief complaint
  - Learning objectives and key differentials
  - AMC competencies display
  - "Start Session" button to begin OSCE

### OSCESession.tsx (560 lines)
- **Purpose:** Active OSCE session with WebSocket chat
- **Features:**
  - Patient name and specialty badges
  - Session timer (countdown)
  - WebSocket chat interface for patient interaction
  - Pause/Resume/End session controls
  - Score dialog showing overall score and breakdown
  - OSCE-to-EMR conversion modal
  - Patient info card (chief complaint, AMC blueprint area)

### MockExamStation.tsx (100+ lines)
- **Purpose:** Individual station in mock exam
- **Features:**
  - Station timer (8-minute countdown)
  - Progress indicator across stations
  - Auto-advance to next station
  - Persona selection for current station

---

## 3. DATA MODELS & TYPES

### Location: `/home/dev/Development/irStudy/frontend/src/types/osce.ts`

**Key Interfaces:**

```typescript
// AMC 15-Mark Rubric
interface AMCRubricDomain {
  name: string;                      // e.g., "Communication Skills"
  maxMarks: number;                  // 0-4
  description: string;
  behavioralAnchors: Record<number, string>; // Mark level descriptions
}

interface AMCRubricScore {
  communicationSkills: number;       // 0-3
  clinicalReasoning: number;         // 0-4
  informationGathering: number;      // 0-3
  managementPlan: number;            // 0-3
  professionalismEthics: number;     // 0-2
  totalScore: number;                // 0-15
  passed: boolean;                   // >= 10 marks
}

// OSCE Scenario
interface OSCEScenario {
  id: string;
  title: string;
  description: string;
  specialty: string;
  difficulty: 'easy' | 'medium' | 'hard';
  timeLimitMinutes: number;          // Usually 8
  patientPresentation: string;
  learningObjectives: string[];
}

// OSCE Session
interface OSCESession {
  id: string;
  scenario: OSCEScenario;
  status: 'not_started' | 'in_progress' | 'completed' | 'abandoned';
  startedAt?: Date;
  completedAt?: Date;
  rubricScore?: AMCRubricScore;
}
```

### Location: `/home/dev/Development/irStudy/frontend/src/api/osce.ts`

**API Types:**

```typescript
interface OSCEAttempt {
  attempt_id: string;
  user_id: string;
  persona_id: string;
  started_at: string;
  completed_at: string | null;
  score: number | null;              // 0-100
  status: 'in_progress' | 'completed' | 'abandoned';
  transcript: Array<{
    speaker: 'student' | 'patient';
    message: string;
    timestamp: string;
  }>;
  persona?: PersonaDetail;
}
```

### Location: `/home/dev/Development/irStudy/frontend/src/api/personas.ts`

**Patient Persona Types:**

```typescript
interface PersonaListItem {
  persona_id: string;
  persona_code: string;              // e.g., "cardiology_001_stemi_male_65"
  name: string;
  age: number;
  gender: string;
  specialty: string;
  chief_complaint: string;
  difficulty_level: string;          // "foundation" | "intermediate" | "advanced"
  estimated_pass_rate: number | null;
  amc_blueprint_area: string;
}

interface PersonaDetail extends PersonaListItem {
  occupation: string | null;
  cultural_background: string | null;
  preferred_language: string;
  opening_statement: string;
  symptoms: Record<string, any>;     // Progressive disclosure
  medical_history: Record<string, any>;
  emotional_profile: Record<string, any>;
  rag_query_hints: string[];
  key_differentials: string[];
  critical_actions: string[];        // Must-do items
  amc_competencies: string[];
}
```

---

## 4. CURRENT UI DESIGN PATTERNS

### Design System: Material-UI 7.3.7

**Theme Configuration:**
- Custom breakpoints: xs(320px), sm(768px), md(1024px), lg(1280px), xl(1920px)
- Primary color: #1976d2 (blue)
- Secondary color: #dc004e (magenta)
- Success: #4caf50, Warning: #ff9800, Error: #f44336, Info: #2196f3
- Responsive typography (scales on mobile)
- Border radius: 8px (buttons), 12px (cards)
- 8px base spacing unit

**Component Library:**
- `@mui/material` - UI components
- `@mui/icons-material` - Icons
- `@mui/x-charts` - Charts (for dashboards)
- `recharts` - Additional charting
- Emotion/styled-components for custom styling

### Layout Patterns Found

**Card-Based Layout:**
```
┌─────────────────────────────────┐
│ Header / Title                  │
├─────────────────────────────────┤
│ Content (key-value pairs)       │
└─────────────────────────────────┘
```

**Grid Layout:**
- 12-column grid system
- Responsive: xs(12), sm(6), md(4), lg(3), xl(2)
- Spacing(2, 3) between elements

**Patient Details Pattern (from OSCEPractice.tsx):**
```
┌─── Demographics Card ────────┐  ┌─── Clinical Info Card ────────┐
│ Name:                        │  │ Specialty: Cardiology          │
│ Age/Gender: 65 years, Male   │  │ Difficulty: Advanced           │
│ Occupation: Retired Manager  │  │ Pass Rate: 45%                 │
│ Cultural Background:         │  │ AMC Blueprint: CV Conditions   │
└──────────────────────────────┘  └────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│ Chief Complaint Card                                            │
│ "Patient presenting with symptoms consistent with STEMI..."   │
└─────────────────────────────────────────────────────────────────┘
┌────────── Differentials ─────────┐  ┌─── Competencies ──────────┐
│ • MI (Inferior)                  │  │ • History Taking           │
│ • MI (Anterior)                  │  │ • Physical Examination     │
│ • Unstable Angina                │  │ • Clinical Reasoning       │
└──────────────────────────────────┘  └────────────────────────────┘
```

**Session Display Pattern (from OSCESession.tsx):**
```
┌─────── Header ────────────────────────────────────────────┐
│ OSCE Session: John Brown [Cardiology] [Advanced] [65M]    │
└───────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Chief Complaint: Chest pain  │  AMC Area: CV Conditions    │
└─────────────────────────────────────────────────────────────┘
    ┌──── Timer ────┐          ┌─────── Controls ──────┐
    │ 06:32 remain  │          │ [Pause] [End]         │
    └───────────────┘          └───────────────────────┘
┌──────────────────────────────── Chat Interface ──────────────┐
│ Patient: "Hello, I've been having chest pain..."             │
│ Student: "When did the pain start?"                          │
│ Patient: "About 2 hours ago while I was..."                  │
└───────────────────────────────────────────────────────────────┘
```

**Scoring/Results Pattern (from AMCRubricDisplay.tsx):**
```
┌──────── Overall Score ────────┐
│ Communication Skills    3/3 ██░│
│ Clinical Reasoning      2/4 ██░│
│ Information Gathering   3/3 ███│
│ Management Plan         2/3 ██░│
│ Professionalism & Ethics 1/2 ░░│
│ ──────────────────────────────│
│ TOTAL: 11/15           ✓ PASS  │
└───────────────────────────────┘
```

---

## 5. API INTEGRATION

### OSCE Endpoints (`src/api/osce.ts`)

```typescript
// Session Management
createOSCESession(personaId: string) → OSCEAttempt
getOSCESession(attemptId: string) → OSCEAttempt
getOSCESessions(userId?: string) → OSCEAttempt[]
pauseOSCESession(attemptId: string) → void
resumeOSCESession(attemptId: string) → void
endOSCESession(attemptId: string) → OSCEAttempt
```

### Persona Endpoints (`src/api/personas.ts`)

```typescript
// Persona Listing & Details
getPersonas(params?: PersonaListParams) → PersonaListItem[]
getPersonaDetail(personaId: string) → PersonaDetail
```

### State Management

**React Query:**
- Query keys: `['personas']`, `['persona-detail', id]`, `['osce-session', id]`
- Stale times: personas (2min), details (5min), sessions (30sec)
- Mutations: `createOSCESession`, session controls

**No Redux/Context for OSCE data** - React Query handles caching

---

## 6. CURRENT GAPS & LIMITATIONS

### 1. **Minimal Score Breakdown**
- Current: Shows overall percentage score only
- Missing: Detailed AMC 15-mark rubric breakdown
- Missing: Behavioral anchors and feedback

### 2. **Limited Clinical Context Display**
- Current: Chief complaint and basic demographics
- Missing: Red flags and warning signs
- Missing: Learning objectives display
- Missing: Critical actions checklist
- Missing: Expected investigations

### 3. **No Evidence-Based References**
- Current: No citation display during session
- Missing: Linked Australian medical guidelines
- Missing: RAG system integration for references
- Missing: Source document links

### 4. **Basic Feedback**
- Current: No post-session feedback
- Missing: Performance vs benchmarks
- Missing: Personalized recommendations
- Missing: Strength/weakness analysis

### 5. **Limited Marking Criteria**
- Current: Only shows final scores
- Missing: Marking rubric during session
- Missing: Real-time performance tracking
- Missing: Mark allocation display

### 6. **No Learning Path Integration**
- Current: Standalone session view
- Missing: Connection to learning objectives
- Missing: Competency mapping
- Missing: Progress tracking

### 7. **Minimal Patient Context**
- Current: Basics (age, gender, specialty)
- Missing: Medical history details
- Missing: Medication list
- Missing: Symptom progression
- Missing: Emotional state tracking

---

## 7. FILE INVENTORY

### Component Files
```
/frontend/src/components/osce/
├── AMCRubricDisplay.tsx          (326 lines) - Rubric scoring display
├── AMCRubricDisplay.test.tsx     - Unit tests
├── WebSocketChat.tsx             (400+ lines) - Chat interface
├── SessionTimer.tsx              - Countdown timer
├── SessionControls.tsx           - Pause/Resume/End buttons
├── EmotionalStateIndicator.tsx   (200+ lines) - Patient emotion display
├── OSCEPracticePlaceholder.tsx   - UI placeholder
├── OSCEPracticePlaceholder.test.tsx
├── index.ts                      - Exports
└── __tests__/                    - Test directory
```

### Page Files
```
/frontend/src/pages/
├── OSCEPractice.tsx              (477 lines) - Persona browser
├── OSCESession.tsx               (560 lines) - Active session
└── osce/
    ├── MockExamStart.tsx         - Exam start page
    ├── MockExamStation.tsx       (100+ lines) - Station view
    └── MockExamResults.tsx       - Results display
```

### Type Files
```
/frontend/src/types/
└── osce.ts                       (98 lines) - OSCE interfaces

/frontend/src/api/
├── osce.ts                       (160 lines) - OSCE endpoints
└── personas.ts                   (100+ lines) - Persona endpoints
```

### Support Files
```
/frontend/src/
├── routes.tsx                    - Route configuration
├── theme/theme.ts               (287 lines) - Material-UI theme
├── components/osce/index.ts      - Component exports
└── package.json                  - Dependencies (MUI 7.3.7, React 19.2.0, React Query 5.90.20)
```

---

## 8. ROUTING CONFIGURATION

From `routes.tsx`:

```typescript
// OSCE pages (lazy loaded for code splitting)
export const OSCEPractice = lazy(() => import('./pages/OSCEPractice'));
export const OSCESession = lazy(() => import('./pages/OSCESession'));

// Mock Exam pages
export const MockExamStart = lazy(() => import('./pages/osce/MockExamStart'));
export const MockExamStation = lazy(() => import('./pages/osce/MockExamStation'));
export const MockExamResults = lazy(() => import('./pages/osce/MockExamResults'));
```

**Expected Routes:**
- `/osce-practice` - Persona browser
- `/osce/session/:attemptId` - Active session
- `/osce/mock-exam/start` - Mock exam intro
- `/osce/mock-exam/:stationId` - Individual station
- `/osce/mock-exam/results` - Results page

---

## 9. KEY DESIGN SYSTEM FINDINGS

### Typography Scale
- h1-h4: Display headings (scalable)
- h5-h6: Section headings
- body1: Default text
- body2: Secondary text
- caption/overline: Small labels

### Color Semantics
- **Primary (Blue #1976d2):** Main actions, important info
- **Secondary (Magenta #dc004e):** Alternative actions
- **Success (Green #4caf50):** Pass, completion, positive
- **Warning (Orange #ff9800):** Caution, limited time
- **Error (Red #f44336):** Fail, critical issues
- **Info (Light Blue #2196f3):** Informational messages

### Responsive Breakpoints
- **xs (320px):** Mobile phones
- **sm (768px):** Tablets
- **md (1024px):** Small desktop
- **lg (1280px):** Large desktop
- **xl (1920px):** Ultra-wide

### Spacing Convention
- **Base unit:** 8px
- **Common gaps:** 1 (8px), 2 (16px), 3 (24px)
- **Card padding:** 16px (desktop), 12px (mobile)

---

## 10. ACCESSIBILITY COMPLIANCE

**WCAG 2.2 AA Standards Implemented:**

✅ Semantic HTML (role, aria-label attributes)  
✅ Color not used alone (text labels with icons)  
✅ Screen reader support (aria-labels on timers, controls)  
✅ Keyboard navigation (form controls, buttons)  
✅ High contrast colors (minimum 4.5:1 ratio)  
✅ Touch target size (minimum 44px on mobile)  
✅ Focus indicators on interactive elements  
✅ Responsive font sizes (no fixed pixels < 16px)  

---

## 11. TECHNOLOGY STACK SUMMARY

| Category | Technology | Version |
|----------|-----------|---------|
| **Framework** | React | 19.2.0 |
| **Router** | React Router DOM | 7.13.0 |
| **UI Library** | Material-UI | 7.3.7 |
| **Icons** | MUI Icons | 7.3.8 |
| **State** | React Query | 5.90.20 |
| **HTTP** | Axios | 1.13.4 |
| **Charts** | Recharts, MUI X-Charts | Latest |
| **Styling** | Emotion (styled-components) | 11.14.0+ |
| **Build** | Vite | 7.2.4 |
| **Language** | TypeScript | 5.9.3 |
| **Testing** | Vitest, @testing-library/react | 6.9.1+ |

---

## 12. RECOMMENDATIONS FOR DR. AMIR OSCE DISPLAY

Based on this exploration, here's what needs to be added:

### Priority 1: Enhanced Rubric Display
- [ ] Expand AMCRubricDisplay to show detailed marking criteria
- [ ] Add behavioral anchors for reference during session
- [ ] Display expected outcomes for each domain

### Priority 2: Clinical Context Panel
- [ ] Red flags display (pre-session and during)
- [ ] Learning objectives sidebar
- [ ] Critical actions checklist
- [ ] Expected investigations list

### Priority 3: Evidence Integration
- [ ] Citation panel for Australian medical guidelines
- [ ] RAG system integration for real-time references
- [ ] Source document links
- [ ] Differential diagnosis explanations

### Priority 4: Patient Context
- [ ] Expanded demographics card
- [ ] Medical history timeline
- [ ] Medication/allergy display
- [ ] Symptom progression tracker

### Priority 5: Post-Session Analysis
- [ ] Detailed performance breakdown
- [ ] Benchmark comparison
- [ ] Personalized feedback
- [ ] Recommendation engine

### Priority 6: Progress Tracking
- [ ] Unified competency dashboard
- [ ] Learning path integration
- [ ] Strength/weakness analysis
- [ ] Goal setting interface

---

## 13. NEXT STEPS

1. **Extend Type Definitions** - Add fields for marking criteria, red flags, learning objectives
2. **Create New Components:**
   - `OSCEMarkingCriteria.tsx` - Show detailed rubric
   - `ClinicalContextPanel.tsx` - Red flags, learning objectives
   - `CitationPanel.tsx` - Evidence display
   - `PatientHistoryPanel.tsx` - Full medical context
   - `PerformanceFeedback.tsx` - Post-session analysis
3. **Update OSCESession.tsx** - Integrate new components into session layout
4. **Update API Types** - Extend PersonaDetail with full clinical data
5. **Create Tests** - Unit tests for all new components

