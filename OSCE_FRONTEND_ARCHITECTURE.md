# irStudy OSCE Frontend Architecture Overview

## Current Component Hierarchy

```
App (routes.tsx)
├── OSCEPractice (pages/OSCEPractice.tsx)
│   └── Persona Selection & Preview
│       ├── Filters (Specialty, Difficulty)
│       ├── Persona List
│       └── PersonaDetail Card
│           ├── Demographics Card
│           ├── Clinical Info Card
│           ├── Chief Complaint Card
│           ├── Differentials Card
│           └── AMC Competencies Card
│
├── OSCESession (pages/OSCESession.tsx)
│   ├── Header Section
│   │   ├── Patient Name + Badges
│   │   └── Patient Info Card
│   ├── Session Timer (SessionTimer.tsx)
│   ├── Session Controls (SessionControls.tsx)
│   │   ├── Pause Button
│   │   ├── Resume Button
│   │   └── End Button (with confirmation)
│   ├── WebSocketChat (WebSocketChat.tsx)
│   │   ├── Message List
│   │   ├── Emotional State (EmotionalStateIndicator.tsx)
│   │   └── Message Input
│   ├── Score Dialog
│   │   └── AMCRubricDisplay.tsx
│   └── OSCE-to-EMR Modal
│
├── MockExamStart (pages/osce/MockExamStart.tsx)
│   └── Exam initialization & station count
│
├── MockExamStation (pages/osce/MockExamStation.tsx)
│   ├── Station Header (e.g., "Station 1 of 9")
│   ├── Session Timer (countdown)
│   ├── WebSocketChat
│   └── Auto-advance on time-up
│
└── MockExamResults (pages/osce/MockExamResults.tsx)
    └── Overall score breakdown

```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Query Cache                           │
│  - ['personas']: PersonaListItem[]                              │
│  - ['persona-detail', id]: PersonaDetail                        │
│  - ['osce-session', id]: OSCEAttempt                            │
└──────────────────┬──────────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
   ┌─────────┐          ┌──────────────┐
   │ useQuery│          │ useMutation  │
   │ (GET)   │          │ (POST/PUT)   │
   └────┬────┘          └──────┬───────┘
        │                      │
        ├─ getPersonas()       ├─ createOSCESession()
        ├─ getPersonaDetail()  ├─ pauseOSCESession()
        ├─ getOSCESession()    ├─ resumeOSCESession()
        └─ getOSCESessions()   └─ endOSCESession()
        │                      │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Axios Instance     │
        │  (API Client)        │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Backend API         │
        │  /api/v1/*           │
        └──────────────────────┘
```

---

## Current Page Layouts

### OSCEPractice Page Layout

```
┌─────────────────────────────────────────────────┐
│  Header: "OSCE Practice - Patient Personas"     │
│  Subtitle: "Select a patient to begin..."       │
└─────────────────────────────────────────────────┘

┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Specialty Filter │ │ Difficulty Filter│ │ Patient Selector │
└──────────────────┘ └──────────────────┘ └──────────────────┘

┌───────────────────────────────────────────────────────────────┐
│ SELECTED PATIENT DETAIL (if persona is selected)              │
├───────────────────────────────────────────────────────────────┤
│
│  ┌─────────────────┐    ┌─────────────────┐
│  │ Demographics    │    │ Clinical Info   │
│  │ - Name          │    │ - Specialty     │
│  │ - Age/Gender    │    │ - Difficulty    │
│  │ - Occupation    │    │ - Pass Rate     │
│  └─────────────────┘    └─────────────────┘
│
│  ┌───────────────────────────────────────┐
│  │ Chief Complaint                       │
│  │ "Patient presenting with..."          │
│  └───────────────────────────────────────┘
│
│  ┌──────────────────────┐ ┌──────────────────────┐
│  │ Key Differentials    │ │ AMC Competencies     │
│  │ - MI (Inferior)      │ │ - History Taking     │
│  │ - MI (Anterior)      │ │ - Exam Skills        │
│  └──────────────────────┘ └──────────────────────┘
│
│                    ┌────────────────────┐
│                    │ [START SESSION]    │
│                    └────────────────────┘
└───────────────────────────────────────────────────────────────┘
```

### OSCESession Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Header: "OSCE Session: John Brown"                              │
│ Badges: [Cardiology] [Advanced] [65 years, Male]               │
│ Back Button                                                     │
├─────────────────────────────────────────────────────────────────┤
│ Chief Complaint: Chest pain  │  AMC Area: Cardiovascular       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐              ┌──────────────────┐
│  Timer: 06:32    │              │ [Pause] [End]    │
│  Remaining       │              │                  │
└──────────────────┘              └──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      CHAT INTERFACE                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Patient [Neutral]: "Hello, I've been having chest pain"  │  │
│  │ Student: "When did it start?"                            │  │
│  │ Patient [Concerned]: "About 2 hours ago..."              │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ [Your message here...                            ]  [SEND]   │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

[Score Dialog - appears on session end]
┌─────────────────────────────────────────────────────────────────┐
│ OSCE Session Complete                                           │
│ Overall Score: 72%                                              │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│ │ Communication│  │ Clinical     │  │ Professionalism
│ │ 78%          │  │ Reasoning    │  │ 65%          │           │
│ └──────────────┘  │ 68%          │  └──────────────┘           │
│                   └──────────────┘                               │
│ [Convert to EMR Practice]  [Back to OSCE Practice]              │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Response Examples

### GET /patient-personas
```json
[
  {
    "persona_id": "550e8400-e29b-41d4-a716-446655440000",
    "persona_code": "cardiology_001_stemi_male_65",
    "name": "John Brown",
    "age": 65,
    "gender": "male",
    "specialty": "Cardiology",
    "chief_complaint": "Patient presenting with symptoms consistent with STEMI",
    "difficulty_level": "advanced",
    "estimated_pass_rate": 0.45,
    "amc_blueprint_area": "Cardiovascular Conditions"
  }
]
```

### GET /patient-personas/:id
```json
{
  "persona_id": "550e8400-e29b-41d4-a716-446655440000",
  "persona_code": "cardiology_001_stemi_male_65",
  "name": "John Brown",
  "age": 65,
  "gender": "male",
  "specialty": "Cardiology",
  "chief_complaint": "Patient presenting with symptoms consistent with STEMI",
  "difficulty_level": "advanced",
  "estimated_pass_rate": 0.45,
  "amc_blueprint_area": "Cardiovascular Conditions",
  "occupation": "Retired Accountant",
  "cultural_background": "Anglo-Saxon",
  "preferred_language": "English",
  "opening_statement": "Doctor, I've been having severe chest pain for the past 2 hours...",
  "symptoms": {
    "immediate": ["chest pain", "shortness of breath", "anxiety"],
    "on_questioning": ["diaphoresis", "radiation to left arm"]
  },
  "medical_history": {
    "past_medical": ["hypertension", "hyperlipidemia"],
    "medications": ["atenolol", "atorvastatin"],
    "allergies": ["penicillin"]
  },
  "emotional_profile": {
    "initial_state": "anxious",
    "escalation_triggers": ["no diagnosis", "dismissive communication"],
    "calming_factors": ["clear explanations", "empathy"]
  },
  "rag_query_hints": ["STEMI", "chest pain", "MI diagnosis", "ECG"],
  "key_differentials": ["STEMI", "NSTEMI", "Unstable Angina", "Aortic Dissection"],
  "critical_actions": ["Get ECG within 10 minutes", "Establish IV access", "Consider aspirin"],
  "amc_competencies": ["History Taking", "Physical Examination", "Clinical Reasoning", "Communication"]
}
```

### POST /osce-sessions
```json
{
  "attempt_id": "650e8400-e29b-41d4-a716-446655440111",
  "user_id": "750e8400-e29b-41d4-a716-446655440222",
  "persona_id": "550e8400-e29b-41d4-a716-446655440000",
  "started_at": "2026-05-27T10:30:00Z",
  "completed_at": null,
  "score": null,
  "status": "in_progress",
  "transcript": [],
  "persona": { ... }
}
```

---

## Component Props & Interfaces

### AMCRubricDisplay Props
```typescript
interface AMCRubricDisplayProps {
  score: AMCRubricScore;        // Scoring breakdown
  showBehavioralAnchors?: boolean; // Show mark level descriptions
  showProgressBars?: boolean;   // Show visual progress bars
}
```

### WebSocketChat Props
```typescript
interface WebSocketChatProps {
  attemptId: string;            // OSCE attempt ID
  token: string;                // JWT for WebSocket auth
  patientName?: string;         // For display
  onSessionEnd?: (score: SessionScore) => void;
}
```

### SessionControls Props
```typescript
interface SessionControlsProps {
  sessionStatus: 'active' | 'paused' | 'ended';
  onPause: () => Promise<void>;
  onResume: () => Promise<void>;
  onEnd: () => Promise<void>;
  disabled?: boolean;
}
```

---

## TypeScript Type System

### Core Types (osce.ts)
```
AMCRubricDomain
├── name: string
├── maxMarks: number
├── description: string
└── behavioralAnchors: Record<number, string>

AMCRubricScore
├── communicationSkills: number
├── clinicalReasoning: number
├── informationGathering: number
├── managementPlan: number
├── professionalismEthics: number
├── totalScore: number
└── passed: boolean

OSCEScenario
├── id: string
├── title: string
├── description: string
├── specialty: string
├── difficulty: 'easy' | 'medium' | 'hard'
├── timeLimitMinutes: number
├── patientPresentation: string
└── learningObjectives: string[]

OSCESession
├── id: string
├── scenario: OSCEScenario
├── status: OSCESessionStatus
├── startedAt?: Date
├── completedAt?: Date
└── rubricScore?: AMCRubricScore

OSCESessionStatus = 'not_started' | 'in_progress' | 'completed' | 'abandoned'
```

### API Types (osce.ts / personas.ts)
```
OSCEAttempt
├── attempt_id: string (UUID)
├── user_id: string (UUID)
├── persona_id: string (UUID)
├── started_at: string (ISO)
├── completed_at: string | null
├── score: number | null
├── status: 'in_progress' | 'completed' | 'abandoned'
├── transcript: Array<ChatMessage>
└── persona?: PersonaDetail

PersonaListItem
├── persona_id: string
├── persona_code: string
├── name: string
├── age: number
├── gender: string
├── specialty: string
├── chief_complaint: string
├── difficulty_level: string
├── estimated_pass_rate: number | null
└── amc_blueprint_area: string

PersonaDetail extends PersonaListItem
├── occupation: string | null
├── cultural_background: string | null
├── preferred_language: string
├── opening_statement: string
├── symptoms: Record<string, any>
├── medical_history: Record<string, any>
├── emotional_profile: Record<string, any>
├── rag_query_hints: string[]
├── key_differentials: string[]
├── critical_actions: string[]
└── amc_competencies: string[]
```

---

## Styling Architecture

### Theme System (theme/theme.ts)
```
Material-UI Theme (v7.3.7)
├── Palette
│   ├── Primary: #1976d2
│   ├── Secondary: #dc004e
│   ├── Success: #4caf50
│   ├── Warning: #ff9800
│   ├── Error: #f44336
│   └── Info: #2196f3
├── Breakpoints
│   ├── xs: 320px
│   ├── sm: 768px
│   ├── md: 1024px
│   ├── lg: 1280px
│   └── xl: 1920px
├── Typography
│   ├── h1-h4: Display headings
│   ├── h5-h6: Section headings
│   ├── body1-body2: Content text
│   └── caption/overline: Labels
└── Components
    ├── MuiButton: Custom styling
    ├── MuiCard: Responsive shadows
    ├── MuiTextField: Touch-friendly
    └── MuiDialog: Full-screen on mobile

Styled Components (Emotion/styled)
├── ChatContainer: Flex layout, scrollable
├── MessageList: Message history
├── ControlsContainer: Button layout
└── Custom styled variants
```

---

## State Management Pattern

### React Query Setup
```typescript
// Query Keys
queryKey: ['personas', specialty, difficulty]
queryKey: ['persona-detail', personaId]
queryKey: ['osce-session', attemptId]

// Stale Times
staleTime: 2 * 60 * 1000  // Personas (2 min)
staleTime: 5 * 60 * 1000  // Details (5 min)
staleTime: 30 * 1000      // Sessions (30 sec)

// Mutations
createOSCESession: POST /osce-sessions
pauseOSCESession: PUT /osce-sessions/:id/pause
resumeOSCESession: PUT /osce-sessions/:id/resume
endOSCESession: POST /osce-sessions/:id/end
```

### Local Component State
```
OSCEPractice
├── filters: { specialty?, difficulty?, skip, limit }
└── selectedPersonaId: string

OSCESession
├── sessionScore: SessionScore | null
├── showScoreDialog: boolean
├── showConversionModal: boolean
├── pausedAt: string | undefined
└── manualStatus: 'active' | 'paused' | 'ended' | null

WebSocketChat
├── messages: ChatMessage[]
├── inputValue: string
├── isLoading: boolean
└── connectionStatus: 'connecting' | 'connected' | 'error'

SessionControls
└── endDialogOpen: boolean
```

---

## Performance Optimizations

### Code Splitting
```typescript
// routes.tsx uses lazy() for page components
export const OSCEPractice = lazy(() => import('./pages/OSCEPractice'));
export const OSCESession = lazy(() => import('./pages/OSCESession'));

// Suspense boundary handles loading
<Suspense fallback={<CircularProgress />}>
  <Outlet />
</Suspense>
```

### Memoization
```
useMemo: Session state derivation
useCallback: Event handlers (pause, resume, end)
React.memo: Component props memoization
```

### Query Optimization
```
Stale times prevent unnecessary refetches
Enabled flag prevents queries when dependencies missing
Pagination: limit 100, skip offset
```

---

## Error Handling

### Query Error States
```
personasError → Alert "Failed to load personas"
detailError → Alert "Failed to load patient details"
sessionError → Alert "Failed to load session"
```

### Mutation Error States
```
createSession error → Alert "Failed to start session"
pauseSession error → Log error, throw for caller
resumeSession error → Log error, throw for caller
endSession error → Navigate back to practice
```

---

## Next Steps for Dr. Amir OSCE Enhancement

### Phase 1: Type System Extension
1. Add `OSCEMarkingCriteria` interface
2. Add `ClinicalRedFlags` interface
3. Add `LearningObjective` interface
4. Extend `PersonaDetail` with these fields
5. Update API response types

### Phase 2: New Components
1. `OSCEMarkingCriteria.tsx` - Detailed rubric reference
2. `ClinicalContextPanel.tsx` - Red flags + objectives
3. `CitationPanel.tsx` - Evidence references
4. `PatientHistoryPanel.tsx` - Medical context
5. `PerformanceFeedback.tsx` - Post-session analysis

### Phase 3: Layout Integration
1. Update `OSCESession.tsx` layout:
   ```
   ┌─ Header ─────────────────────────────┐
   │ [Chat] │ [Marking Criteria] │ [Context]│
   │        │                    │          │
   │        │                    │ Red Flags│
   │        │                    │ Learning │
   │        │                    │ Objectives
   └────────────────────────────────────────┘
   ```

### Phase 4: API Integration
1. Extend `/patient-personas/:id` response
2. Add `/osce-sessions/:id/feedback` endpoint
3. Add RAG citation integration

### Phase 5: Testing
1. Unit tests for new components
2. Integration tests for layout
3. E2E tests for OSCE flow
