# PRD: React Frontend for AI OSCE Simulation

**PRD ID**: PRD_AI_OSCE_005_FRONTEND_IMPLEMENTATION
**Category**: Frontend (React)
**Priority**: P0-Critical (DEPENDS on PRD_001, PRD_002, PRD_003, PRD_004)
**Estimated Effort**: 24-28 hours
**Dependencies**: PRD_AI_OSCE_001 (Database), PRD_AI_OSCE_002 (AI Integration), PRD_AI_OSCE_003 (WebSocket)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story

**As a** medical student
**I want** a responsive React UI to browse AI patient personas, chat with an AI patient for 8 minutes with real-time timer, view my conversation transcript, and see detailed AMC-based scoring feedback
**So that** I can practice clinical communication skills with realistic simulations, receive instant feedback, and track my progress toward the AMC Clinical Examination

**As a** educator/administrator
**I want** analytics and reporting features to monitor student performance across personas and identify common clinical gaps
**So that** I can adjust curriculum content and provide targeted intervention

### Business Context

The AI OSCE Frontend must provide an intuitive, accessible interface for medical students to:

1. **Persona Discovery** (Browse, Filter, Select)
   - Browse 360 AI patient personas organized by specialty
   - Filter by difficulty level (Foundation/Intermediate/Advanced)
   - View patient demographics, presenting complaint, and estimated duration
   - Select a persona to start practice session

2. **8-Minute OSCE Session** (Real-time Chat Interface)
   - Chat interface with live WebSocket messaging
   - Server-side countdown timer with 1-minute warning
   - Patient emotional state indicators (visual, color-coded)
   - Student message input validation
   - Auto-scroll conversation history
   - Session auto-finalizes at 8:00 (hard stop)

3. **Results Display** (Scoring & Feedback)
   - AMC 15-mark rubric breakdown (Communication, Clinical Reasoning, Information Gathering, Management, Professionalism)
   - Pass/Fail status with reference range
   - Strengths and areas for improvement
   - Overall clinical feedback
   - Transcript viewer with annotated emotions

4. **Transcript Viewer** (Post-Session Review)
   - Full conversation history with timestamps
   - Patient emotional state at each message
   - Student action classification (communication, info gathering, management)
   - Export transcript as PDF

5. **Mock Exam Orchestration** (Phase 2)
   - 16 sequential stations (personas)
   - 8 minutes per station, 2.5 hours total
   - Station progression UI
   - Cumulative scoring across all stations
   - Session pause/resume capability

**Business Value**:
- Self-directed learning at scale (no human examiner required)
- Immediate, consistent AI feedback
- Progress tracking integrated with existing LMS
- Reduced examination anxiety through unlimited practice
- Cost-effective ($0.04-0.07 per session vs. $50+ human OSCE)

### Success Metrics

- **User Experience**: <2 second chat latency perceived (p95), smooth real-time updates
- **Accessibility**: WCAG 2.2 AA (keyboard navigation, screen reader compatible, 4.5:1 contrast)
- **Performance**: Page load <2s (first contentful paint), chat scroll smooth (60fps)
- **Mobile Responsive**: Functional on 320px (mobile) to 1920px (desktop)
- **Reliability**: 99%+ WebSocket connection uptime, zero message loss
- **User Adoption**: 90%+ of students attempt ≥1 persona in first month

### Scope

**In Scope**:
- Persona listing & filtering UI (specialty, difficulty, search)
- Persona detail view (demographics, chief complaint, est. duration)
- Session start/initialization (create osce_attempt via API)
- WebSocket integration with real-time chat messaging
- 8-minute timer with 1-minute warning alert
- Patient emotional state visualization (icons, color palette)
- Message history display with auto-scroll
- Results page with AMC rubric breakdown and feedback
- Transcript viewer with emotional state annotations
- PDF export for transcript
- Student dashboard (practice history, performance stats)
- Error handling & recovery UI (reconnect prompts, timeout messages)
- Responsive layout (mobile, tablet, desktop)
- WCAG 2.2 AA accessibility compliance

**Out of Scope** (Future Iterations, PRD_006):
- Mock exam mode orchestration (16 stations, 2.5 hours) - Phase 2
- Educator analytics dashboard - Phase 2
- Voice/video streaming - Phase 3
- Social features (peer comparison, study groups) - Phase 3
- Mobile native app (iOS/Android) - Phase 3

---

## A - ARCHITECTURE (How)

### Technical Approach

Implement React 18 frontend using Material-UI v5 components, TanStack Query for API data fetching and caching, Zustand for session state management, and native WebSocket API with automatic reconnection. Use TypeScript for type safety and Jest/React Testing Library for component testing.

**Key Design Decisions**:
1. **Material-UI v5**: Provides production-grade accessible components (buttons, forms, dialogs, etc.)
2. **TanStack Query**: Handles REST API caching, refetching, and mutations (persona list, scores, etc.)
3. **Zustand**: Lightweight state for WebSocket session context (attempt_id, timer, messages, user)
4. **Native WebSocket API**: No additional library, simple connection management
5. **Responsive Design**: Mobile-first CSS, CSS Grid for layout flexibility
6. **Real-time Updates**: WebSocket for chat + TanStack Query polling for background scoring
7. **Error Boundaries**: React Error Boundary for crash protection
8. **Lazy Loading**: Code-splitting for routes (persona list, session, results) to optimize bundle

### System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        REACT FRONTEND                            │
│  (Component Tree, State Management, API Integration)             │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                    ROUTING & LAYOUTS                             │
│  - LandingPage                                                   │
│  - PersonaBrowsePage (filter, search, pagination)               │
│  - PersonaDetailPage (demographics, preview)                    │
│  - SessionPage (WebSocket chat, timer, patient info)            │
│  - ResultsPage (scores, feedback, transcript)                   │
│  - DashboardPage (practice history, stats)                      │
│  - ErrorBoundary (fallback UI)                                  │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│               SHARED COMPONENTS & HOOKS                          │
│  - TimerDisplay (countdown, warning alerts)                     │
│  - ChatMessage (student vs. patient styling)                    │
│  - EmotionalStateIndicator (icon, color, tooltip)              │
│  - MessageInput (text area, submit, validation)                │
│  - RubricBreakdown (score cards, visual progress)              │
│  - useWebSocket (connection management, auto-reconnect)        │
│  - useSessionState (Zustand store)                             │
│  - useOsceApi (TanStack Query hooks)                           │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                STATE MANAGEMENT (Zustand)                        │
│  - sessionStore:                                                 │
│    - attemptId, userId, personaId                               │
│    - messages (array), emotionalState, empathyPoints           │
│    - timer (elapsed, remaining, warningShown)                  │
│    - sessionState (active, warning, ended)                     │
│  - Actions: setMessage, setEmotionalState, updateTimer, etc.   │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│              API LAYER (TanStack Query)                          │
│  - usePersonasQuery (GET /api/v1/osce-personas)                │
│  - usePersonaDetailQuery (GET /api/v1/osce-personas/{id})      │
│  - useStartSessionMutation (POST /api/v1/osce-sessions)        │
│  - useSessionTranscriptQuery (GET /api/v1/osce-sessions/{id}) │
│  - useScoresQuery (GET /api/v1/osce-sessions/{id}/scores)     │
│  - Automatic caching, refetch on window focus, stale time=60s  │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│              WEBSOCKET LAYER                                     │
│  - wss://api.example.com/ws/osce/{attempt_id}?token=...        │
│  - Message Types: student_message, patient_message,            │
│    timer_update, timer_warning, session_ended, scoring_complete│
│  - Exponential backoff reconnection (1s, 2s, 4s, 8s, max 32s) │
│  - Auto-reconnect on network error                             │
│  - Message queue if offline (resume on reconnect)              │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│              BACKEND APIS (FastAPI)                              │
│  - GET /api/v1/osce-personas?specialty=...&difficulty=...      │
│  - GET /api/v1/osce-personas/{id}                              │
│  - POST /api/v1/osce-sessions (create, get JWT token)         │
│  - GET /api/v1/osce-sessions/{id}                             │
│  - GET /api/v1/osce-sessions/{id}/transcript                  │
│  - GET /api/v1/osce-sessions/{id}/scores                      │
│  - WebSocket: wss://api.example.com/ws/osce/{id}             │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│              BACKEND SERVICES & STORAGE                          │
│  - PostgreSQL: personas, attempts, scores, user_progress       │
│  - Redis: active session state, messages, emotional state      │
│  - AI Services: AI Patient (chat), AI Examiner (scoring)      │
└──────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
frontend/src/
├── pages/
│   ├── LandingPage.tsx
│   ├── PersonaBrowsePage.tsx
│   ├── PersonaDetailPage.tsx
│   ├── SessionPage.tsx
│   ├── ResultsPage.tsx
│   ├── DashboardPage.tsx
│   └── NotFoundPage.tsx
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── MainLayout.tsx
│   ├── persona/
│   │   ├── PersonaCard.tsx
│   │   ├── PersonaFilter.tsx
│   │   └── PersonaDetailCard.tsx
│   ├── session/
│   │   ├── ChatMessage.tsx
│   │   ├── ChatWindow.tsx
│   │   ├── MessageInput.tsx
│   │   ├── TimerDisplay.tsx
│   │   ├── EmotionalStateIndicator.tsx
│   │   └── SessionHeader.tsx
│   ├── results/
│   │   ├── RubricBreakdown.tsx
│   │   ├── ScoreCard.tsx
│   │   ├── FeedbackSection.tsx
│   │   └── TranscriptViewer.tsx
│   ├── common/
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorAlert.tsx
│   │   ├── ConfirmDialog.tsx
│   │   └── Tooltip.tsx
│   └── accessibility/
│       ├── SkipToMain.tsx
│       └── LiveRegion.tsx
├── hooks/
│   ├── useWebSocket.ts
│   ├── useSessionState.ts
│   ├── useOsceApi.ts
│   ├── useTimer.ts
│   └── useLocalStorage.ts
├── stores/
│   ├── sessionStore.ts (Zustand)
│   ├── authStore.ts
│   └── preferencesStore.ts
├── api/
│   ├── client.ts (Axios instance, JWT interceptor)
│   ├── osce.ts (API functions for OSCE endpoints)
│   ├── auth.ts (Authentication endpoints)
│   └── types.ts (API response DTOs)
├── types/
│   ├── index.ts (Global TypeScript types)
│   ├── api.ts (API DTOs)
│   ├── session.ts (Session state types)
│   └── ui.ts (UI component props)
├── utils/
│   ├── formatters.ts (time, numbers, scores)
│   ├── validators.ts (message length, etc.)
│   ├── pdf-export.ts (transcript PDF generation)
│   └── accessibility.ts (ARIA utilities)
├── styles/
│   ├── theme.ts (Material-UI theme, colors)
│   ├── globals.css (base styles)
│   └── animations.css (transitions, timers)
├── App.tsx (Root component, router setup)
├── index.tsx (Entry point)
└── env.ts (Environment config)

frontend/tests/
├── components/
│   ├── SessionPage.test.tsx
│   ├── PersonaBrowsePage.test.tsx
│   ├── ResultsPage.test.tsx
│   ├── ChatMessage.test.tsx
│   └── TimerDisplay.test.tsx
├── hooks/
│   ├── useWebSocket.test.ts
│   ├── useSessionState.test.ts
│   └── useOsceApi.test.ts
├── api/
│   ├── osce.test.ts
│   └── client.test.ts
└── utils/
    ├── formatters.test.ts
    ├── validators.test.ts
    └── pdf-export.test.ts
```

### Component Hierarchy (Session Page - Core Feature)

```
SessionPage (Main container, WebSocket connection)
├── SessionHeader (Patient name, specialty, difficulty)
│   └── EmotionalStateIndicator (patient state: ANXIOUS_GUARDED, CAUTIOUSLY_OPEN, etc.)
├── MainGridContainer
│   ├── ChatWindow (left, 60% width on desktop)
│   │   ├── ChatMessage[] (student & patient messages)
│   │   │   ├── ChatMessage (speaker, text, timestamp)
│   │   │   └── EmotionalStateChange (animated badge)
│   │   └── MessageInput (text area, submit button)
│   └── SessionInfoPanel (right, 40% width on desktop)
│       ├── TimerDisplay (countdown, warning alert)
│       │   └── WarningBadge ("1 MINUTE REMAINING" at 7:00)
│       ├── PatientInfoCard (demographics, complaint, symptoms)
│       └── SessionStats (message count, empathy points, ...)
└── BottomBar (Exit session, pause, help buttons)

(Mobile: Stack vertically, hide right panel until toggle)
```

### Data Flow: Starting a Session

```
Step 1: User selects persona from browse page
   ↓
Step 2: Frontend calls POST /api/v1/osce-sessions
   Request: {persona_id, difficulty_override?}
   ↓
Step 3: Backend creates osce_attempt record, returns:
   {
     attempt_id: "uuid-123",
     websocket_url: "wss://api.example.com/ws/osce/uuid-123",
     session_token: "eyJ..."
   }
   ↓
Step 4: Frontend navigates to SessionPage with attempt_id
   ↓
Step 5: Frontend opens WebSocket connection
   ws = new WebSocket("wss://.../ws/osce/uuid-123?token=eyJ...")
   ↓
Step 6: Backend authenticates token, loads session, sends opening statement
   WebSocket SEND: {
     type: "patient_message",
     speaker: "patient",
     message: "Doctor, I've been having...",
     emotional_state: "ANXIOUS_GUARDED"
   }
   ↓
Step 7: Frontend receives, stores in Zustand store, displays in ChatWindow
   ↓
Step 8: Timer starts counting down
   WebSocket sends timer_update every 1 second
   ↓
Step 9: User types, clicks "Send Message" button
   Frontend: ws.send({type: "student_message", message: "..."})
   ↓
Step 10: Backend processes, AI Patient responds
   WebSocket SEND: {
     type: "patient_message",
     message: "Well, it started...",
     emotional_state: "CAUTIOUSLY_OPEN"
   }
   ↓
Step 11: Frontend receives, updates ChatWindow, auto-scrolls
   ↓
(Repeat steps 9-11 until 8:00)
   ↓
Step 12: At 7:00: WebSocket sends timer_warning
   Frontend: Highlights timer in red, shows "1 MINUTE REMAINING"
   ↓
Step 13: At 8:00: WebSocket sends session_ended + scoring_complete
   Frontend: Disables message input, navigates to ResultsPage
   ↓
Step 14: ResultsPage displays scores, feedback, transcript
```

### Accessibility Architecture (WCAG 2.2 AA)

1. **Keyboard Navigation** (TAB through UI elements)
   - Focus management: Auto-focus chat input after session starts
   - Skip link: "Skip to main content" visible on page load
   - Dialog traps: Escape to close, focus returns

2. **Screen Reader Support**
   - Semantic HTML: `<main>`, `<nav>`, `<section>` for landmarks
   - ARIA labels: `aria-label="Send message"` on button
   - Live regions: `aria-live="polite"` for timer updates, chat messages
   - Role descriptions: `role="log"` for chat history

3. **Visual Contrast** (4.5:1 minimum)
   - Black text (#000000) on white bg (#FFFFFF): 21:1
   - Timer warning (red #D32F2F) on white: 5.25:1
   - Focus indicators: 2px solid blue outline

4. **Color Independence**
   - Emotional states: Color + icon (not color alone)
   - Pass/Fail: Green/Red + checkmark/X icon
   - Alerts: Color + text + icon

5. **Responsive Text**
   - Minimum font size: 14px (12px only for secondary info)
   - Line height: 1.5x minimum
   - Letter spacing: 0.12em on headings

---

## L - LOOP (Iterative Development)

### Phase 1: Persona Discovery & Session Setup (30% of effort, 7-8 hours)
**Goal**: Implement persona browsing, filtering, and session initialization

**Tasks**:
1. Create API client & TanStack Query hooks - 1 hour
2. Implement persona listing page with filters - 1.5 hours
3. Build persona detail page - 1 hour
4. Add session start flow (API call, get JWT) - 1 hour
5. Create session state management (Zustand) - 1 hour
6. Implement basic error handling & loading states - 0.5 hours

**Validation Gate**:
- [ ] Persona list loads and displays with filters (specialty, difficulty)
- [ ] Search filters personas by name/complaint
- [ ] Pagination works (20 personas per page)
- [ ] Detail page shows demographics, chief complaint, estimated duration
- [ ] Start session button calls API, receives attempt_id + token
- [ ] SessionPage navigates with attempt_id in URL
- [ ] API errors display user-friendly messages
- [ ] Loading states show spinners

---

### Phase 2: Real-Time Chat & Timer (40% of effort, 10-12 hours)
**Goal**: WebSocket integration with chat messaging and 8-minute countdown timer

**Tasks**:
1. Implement useWebSocket hook (connection, auth, reconnection) - 2 hours
2. Create ChatWindow component with message display - 1.5 hours
3. Build MessageInput component with validation - 1 hour
4. Implement TimerDisplay with countdown and warnings - 1.5 hours
5. Add EmotionalStateIndicator visualization - 1 hour
6. Create SessionHeader with patient info - 0.5 hours
7. Implement message history auto-scroll - 0.5 hours
8. Add connection recovery UI (reconnect prompts) - 1 hour

**Validation Gate**:
- [ ] WebSocket connects with JWT token
- [ ] Opening patient message displays on connect
- [ ] User message input validates (not empty, <5000 chars)
- [ ] Send button submits message via WebSocket
- [ ] Patient responses appear in chat in real-time
- [ ] Timer counts down (8:00 → 0:00)
- [ ] Timer updates every 1 second (±0.5s)
- [ ] 1-minute warning displays at 7:00 (red highlight)
- [ ] Chat auto-scrolls to latest message
- [ ] Emotional state icon changes when patient state changes
- [ ] Message input disabled after session ends
- [ ] Network disconnect triggers reconnect prompt
- [ ] Reconnect within 30s resumes session
- [ ] Chat latency <2 seconds perceived (p95)

---

### Phase 3: Results Display & Accessibility (25% of effort, 6-7 hours)
**Goal**: Score display, transcript viewer, and WCAG 2.2 AA compliance

**Tasks**:
1. Create results page layout & AMC rubric breakdown - 1.5 hours
2. Build score cards with visual progress bars - 1 hour
3. Implement transcript viewer with annotations - 1.5 hours
4. Add PDF export for transcript - 1 hour
5. Accessibility audit & fixes (WCAG 2.2 AA) - 1.5 hours

**Validation Gate**:
- [ ] Results page displays AMC 15-mark rubric breakdown
- [ ] Score cards show: score, max score, feedback
- [ ] Pass/Fail status clearly indicated
- [ ] Transcript displays full conversation with timestamps
- [ ] Emotional state annotations shown at each message
- [ ] PDF export contains transcript + scores
- [ ] WCAG 2.2 AA: Keyboard navigation (TAB works)
- [ ] WCAG 2.2 AA: Screen reader accessible (ARIA labels)
- [ ] WCAG 2.2 AA: Color contrast ≥4.5:1
- [ ] WCAG 2.2 AA: Focus indicators visible
- [ ] Mobile responsive: Works on 320px to 1920px

---

### Phase 4: Testing & Performance Optimization (5% of effort, 1-2 hours)
**Goal**: Unit & component tests, performance tuning, launch readiness

**Tasks**:
1. Write unit tests for hooks & utilities - 1 hour
2. Write component tests (main UI) - 0.5 hours
3. Performance profiling & optimization (lazy load, code split) - 0.5 hours

**Validation Gate**:
- [ ] Jest test coverage ≥80%
- [ ] All tests pass (100%)
- [ ] Page load time <2s (first contentful paint)
- [ ] Chat scroll smooth (60fps)
- [ ] Bundle size <300KB (gzipped)
- [ ] Lighthouse score ≥90 (performance)
- [ ] No console errors or warnings

---

## P - PLAN (Detailed Implementation)

### Phase 1 Tasks

**Task 1.1**: Create API Client & TanStack Query Hooks
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/api/client.ts`, `frontend/src/api/osce.ts`, `frontend/src/hooks/useOsceApi.ts`
- **Dependencies**: Backend PRD_001 (endpoints must be deployed)
- **Acceptance Criteria**:
  - [ ] Axios instance with JWT interceptor (`frontend/src/api/client.ts`)
  - [ ] Auth token stored in localStorage/sessionStorage
  - [ ] Auto-add `Authorization: Bearer {token}` header to requests
  - [ ] API functions for all endpoints: usePersonasQuery, usePersonaDetailQuery, useStartSessionMutation, useScoresQuery
  - [ ] TanStack Query configured: staleTime=60s, cacheTime=300s
  - [ ] Error handling: Retry on 5xx, user-friendly messages on 4xx
  - [ ] Test: Mock API calls, verify headers, error handling

**Task 1.2**: Implement Persona Listing Page with Filters
- **Effort**: 1.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/pages/PersonaBrowsePage.tsx`, `frontend/src/components/persona/PersonaFilter.tsx`
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Page displays grid of 20 persona cards per page
  - [ ] Filter by specialty dropdown (Cardiology, Respiratory, Neurology, etc.)
  - [ ] Filter by difficulty toggle (Foundation, Intermediate, Advanced)
  - [ ] Search by persona name or chief complaint
  - [ ] Pagination controls (Previous/Next, page counter)
  - [ ] Persona cards show: name, age, chief complaint, specialty, difficulty, estimated duration
  - [ ] Cards are clickable (navigate to detail page)
  - [ ] Loading state shows spinner
  - [ ] Error state shows retry button
  - [ ] Responsive: Single column on mobile, 2 columns on tablet, 3+ on desktop

**Task 1.3**: Build Persona Detail Page
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/pages/PersonaDetailPage.tsx`, `frontend/src/components/persona/PersonaDetailCard.tsx`
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] URL param: `PersonaDetailPage?id={persona_id}`
  - [ ] Display: Name, age, gender, occupation, cultural background
  - [ ] Display: Chief complaint, opening statement, key symptoms
  - [ ] Display: Medical history highlights, red flags, estimated difficulty
  - [ ] "Start Practice" button at top and bottom
  - [ ] "Back to Browse" button
  - [ ] Responsive layout (single column mobile, multi-column desktop)
  - [ ] Loading state while fetching details
  - [ ] 404 page if persona not found

**Task 1.4**: Add Session Start Flow
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/api/osce.ts` (useStartSessionMutation)
- **Dependencies**: Tasks 1.2-1.3, Backend PRD_001 (POST /api/v1/osce-sessions)
- **Acceptance Criteria**:
  - [ ] "Start Practice" button calls POST /api/v1/osce-sessions
  - [ ] Request body: {persona_id}
  - [ ] Response: {attempt_id, websocket_url, session_token}
  - [ ] Store session_token in sessionStorage (expires at 8:00)
  - [ ] Navigate to SessionPage with attempt_id in URL
  - [ ] Show loading spinner during API call
  - [ ] Handle errors: Network, 404 (persona not found), 401 (unauthorized)
  - [ ] Test: Mock API response, verify navigation

**Task 1.5**: Create Session State Management
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/stores/sessionStore.ts` (Zustand), `frontend/src/hooks/useSessionState.ts`
- **Dependencies**: Task 1.4
- **Acceptance Criteria**:
  - [ ] Zustand store with state:
    - attemptId, userId, personaId
    - messages: {speaker, text, timestamp, emotional_state}[]
    - emotionalState: "ANXIOUS_GUARDED" | "CAUTIOUSLY_OPEN" | etc.
    - empathyPoints: number
    - timer: {elapsed, remaining, started_at}
    - sessionState: "active" | "warning_1min" | "ended"
  - [ ] Actions: setAttemptId, addMessage, setEmotionalState, updateTimer, setSessionEnded
  - [ ] Persist to localStorage (recover on page refresh)
  - [ ] useSessionState hook exports store + actions
  - [ ] Test: Verify state updates, localStorage persistence

**Task 1.6**: Implement Basic Error Handling & Loading States
- **Effort**: 0.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/common/ErrorAlert.tsx`, `frontend/src/components/common/LoadingSpinner.tsx`
- **Dependencies**: Tasks 1.1-1.5
- **Acceptance Criteria**:
  - [ ] ErrorAlert component: icon, message, retry button
  - [ ] LoadingSpinner component: Material-UI CircularProgress
  - [ ] API error boundaries: Catch and display errors
  - [ ] User-friendly messages (no technical stack traces)
  - [ ] Retry button for failed API calls
  - [ ] Test: Verify error display, retry functionality

---

### Phase 2 Tasks

**Task 2.1**: Implement useWebSocket Hook
- **Effort**: 2 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/hooks/useWebSocket.ts`
- **Dependencies**: Task 1.4 (have session_token)
- **Acceptance Criteria**:
  - [ ] Hook manages WebSocket lifecycle
  - [ ] URL: `wss://api.example.com/ws/osce/{attempt_id}?token={session_token}`
  - [ ] Auto-connect on mount, auto-disconnect on unmount
  - [ ] Expose methods: send(message), connect(), disconnect()
  - [ ] Expose state: isConnected, isConnecting, isReconnecting, lastError
  - [ ] Exponential backoff on disconnect (1s, 2s, 4s, 8s, max 32s)
  - [ ] Max 10 reconnection attempts, then give up
  - [ ] Message queue while offline (retry on reconnect)
  - [ ] Error handling: Network down, 4xx auth, 5xx server
  - [ ] Test: Mock WebSocket, verify connection flow, reconnection logic

**Task 2.2**: Create ChatWindow Component
- **Effort**: 1.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/session/ChatWindow.tsx`, `frontend/src/components/session/ChatMessage.tsx`
- **Dependencies**: Tasks 1.5, 2.1
- **Acceptance Criteria**:
  - [ ] Display list of ChatMessage components (student and patient)
  - [ ] ChatMessage shows: speaker, text, timestamp (HH:MM format)
  - [ ] Student messages: Light gray bg, right-aligned
  - [ ] Patient messages: Blue bg, left-aligned
  - [ ] Timestamp on hover (tooltip)
  - [ ] Emotional state badge on patient messages (colored icon)
  - [ ] Auto-scroll to latest message on new message
  - [ ] Scrollable container if messages exceed viewport
  - [ ] MessageInput component below (see Task 2.3)
  - [ ] Test: Verify message display, auto-scroll, styling

**Task 2.3**: Build MessageInput Component
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/session/MessageInput.tsx`
- **Dependencies**: Tasks 1.5, 2.1
- **Acceptance Criteria**:
  - [ ] Text area input field (Material-UI TextField multiline)
  - [ ] "Send" button (Material-UI Button variant="contained")
  - [ ] Validate: Message not empty, length <5000 chars
  - [ ] Show validation error if message invalid
  - [ ] Disabled after session ends (sessionState === "ended")
  - [ ] Disabled while WebSocket disconnected (visual indicator)
  - [ ] Send on: Button click OR Shift+Enter (standard form shortcut)
  - [ ] Clear input after successful send
  - [ ] On send: Emit to WebSocket, update Zustand store
  - [ ] Accessible: ARIA label, keyboard focus visible
  - [ ] Test: Verify validation, send logic, accessibility

**Task 2.4**: Implement TimerDisplay Component
- **Effort**: 1.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/session/TimerDisplay.tsx`, `frontend/src/hooks/useTimer.ts`
- **Dependencies**: Tasks 1.5, 2.1
- **Acceptance Criteria**:
  - [ ] Display countdown timer (M:SS format: 8:00 → 7:59 → ... → 0:00)
  - [ ] useTimer hook: Updates every 1 second
  - [ ] Sync with server: Listen for WebSocket timer_update messages
  - [ ] Normal state (0:00 - 6:59): Black text, large font (36px)
  - [ ] Warning state (7:00 - 7:59): Red text (#D32F2F), pulsing animation
  - [ ] Warning badge: "1 MINUTE REMAINING" text in red box
  - [ ] Ended state (8:00+): Show "Session Ended"
  - [ ] Audio alert at 7:00 (optional, can be disabled)
  - [ ] Accuracy: ±0.5 seconds (don't rely on client-side time)
  - [ ] Test: Mock timer updates, verify display, warning state

**Task 2.5**: Add EmotionalStateIndicator Component
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/session/EmotionalStateIndicator.tsx`
- **Dependencies**: Tasks 1.5, 2.2
- **Acceptance Criteria**:
  - [ ] Display emotional state icon + label
  - [ ] States: ANXIOUS_GUARDED (😟 red), CAUTIOUSLY_OPEN (😐 orange), TRUSTING (😊 green), WITHDRAWN (😕 gray), UPSET (😞 red)
  - [ ] Color accessibility: Icon + label (not color alone)
  - [ ] Size: 24x24px icon (inline), 32x32px (header)
  - [ ] Tooltip on hover: Full state name + description
  - [ ] Animated transition when state changes (fade + scale)
  - [ ] Accessible: `role="status"`, `aria-live="polite"` when changes
  - [ ] Test: Verify icon display, transitions, accessibility

**Task 2.6**: Create SessionHeader Component
- **Effort**: 0.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/session/SessionHeader.tsx`
- **Dependencies**: Tasks 1.5, 2.5
- **Acceptance Criteria**:
  - [ ] Display patient name, age, chief complaint
  - [ ] Display specialty badge (Cardiology, etc.)
  - [ ] Display emotional state indicator
  - [ ] "Exit Session" button (with confirmation)
  - [ ] Responsive: Stack vertically on mobile, horizontal on desktop
  - [ ] Test: Verify display, exit button functionality

**Task 2.7**: Implement Message History Auto-Scroll
- **Effort**: 0.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/session/ChatWindow.tsx` (useEffect hook)
- **Dependencies**: Task 2.2
- **Acceptance Criteria**:
  - [ ] ChatWindow scrolls to bottom on new message
  - [ ] useRef to div.scrollable container
  - [ ] useEffect triggers on messages array change
  - [ ] Smooth scroll animation (CSS transition)
  - [ ] Don't scroll if user manually scrolled up (preserve context)
  - [ ] Detect: scrollTop + scrollHeight - clientHeight > threshold (e.g., 50px)
  - [ ] Test: Verify auto-scroll, manual scroll detection

**Task 2.8**: Add Connection Recovery UI
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/session/ConnectionStatus.tsx`
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] Display connection status icon (green: connected, yellow: reconnecting, red: disconnected)
  - [ ] Toast notification: "Connection lost. Reconnecting..." on disconnect
  - [ ] Toast notification: "Connection restored." on reconnect
  - [ ] Manual "Reconnect" button if auto-reconnect fails
  - [ ] Disable message input while disconnected (visual feedback)
  - [ ] Auto-dismiss toast after 5s
  - [ ] Accessible: ARIA live region for status updates
  - [ ] Test: Mock disconnect/reconnect, verify UI updates

---

### Phase 3 Tasks

**Task 3.1**: Create Results Page Layout & Rubric Breakdown
- **Effort**: 1.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/pages/ResultsPage.tsx`, `frontend/src/components/results/RubricBreakdown.tsx`
- **Dependencies**: Backend PRD_003 (scoring_complete message), Task 2.4
- **Acceptance Criteria**:
  - [ ] ResultsPage displays on WebSocket session_ended message
  - [ ] RubricBreakdown shows: Communication, Clinical Reasoning, Info Gathering, Management, Professionalism
  - [ ] Each rubric: Score (0-max), max score, percentage
  - [ ] Total score at top: bold, large font
  - [ ] Pass/Fail status: Green checkmark (PASS) or red X (FAIL)
  - [ ] Reference range: "Passing: ≥10/15" (displayed below total)
  - [ ] Responsive: Stack vertically on mobile, grid on desktop
  - [ ] Test: Verify rubric display, score formatting

**Task 3.2**: Build Score Cards with Visual Progress Bars
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/results/ScoreCard.tsx`
- **Dependencies**: Task 3.1
- **Acceptance Criteria**:
  - [ ] ScoreCard component: Category name, score, max, percentage bar
  - [ ] Progress bar: Green if score ≥80%, yellow if 60-79%, red if <60%
  - [ ] Bar width: (score / max) * 100%
  - [ ] Score text: "3/3 (100%)"
  - [ ] Hover tooltip: Category description
  - [ ] Accessible: aria-valuenow, aria-valuemax, role="progressbar"
  - [ ] Test: Verify score display, progress bar colors, accessibility

**Task 3.3**: Implement Transcript Viewer
- **Effort**: 1.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/results/TranscriptViewer.tsx`
- **Dependencies**: Task 2.2 (ChatMessage component reuse)
- **Acceptance Criteria**:
  - [ ] Full conversation history with timestamps
  - [ ] Emotional state badge on patient messages
  - [ ] Student action labels on student messages (e.g., "Info Gathering")
  - [ ] Expandable sections: Conversation, Actions Summary, Emotional Timeline
  - [ ] Scrollable container (500px max height)
  - [ ] "Print" button for printing transcript
  - [ ] "Export as PDF" button (see Task 3.4)
  - [ ] Test: Verify transcript display, expandable sections

**Task 3.4**: Add PDF Export for Transcript
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/utils/pdf-export.ts`, integrate into ResultsPage
- **Dependencies**: Task 3.3, install jsPDF or pdfkit library
- **Acceptance Criteria**:
  - [ ] "Download Transcript PDF" button
  - [ ] PDF content: Title, metadata (date, persona, duration)
  - [ ] PDF content: Full conversation (messages + timestamps)
  - [ ] PDF content: Scores and rubric breakdown
  - [ ] PDF content: Feedback and areas for improvement
  - [ ] Filename: `OSCE_Transcript_{attempt_id}_{date}.pdf`
  - [ ] Layout: Readable on A4 page (portrait)
  - [ ] Test: Generate PDF, verify content, file size <2MB

**Task 3.5**: Accessibility Audit & WCAG 2.2 AA Fixes
- **Effort**: 1.5 hours
- **Owner**: Frontend Engineer / QA
- **Deliverable**: Fixes to all components for WCAG 2.2 AA compliance
- **Dependencies**: Tasks 2.1-2.8, 3.1-3.4
- **Acceptance Criteria**:
  - [ ] **Keyboard Navigation**: Tab through all interactive elements, Escape closes dialogs
  - [ ] **Focus Management**: Visible focus indicators (2px solid #2196F3), focus order logical
  - [ ] **Screen Reader**: Semantic HTML, ARIA labels on images/icons, live regions for updates
  - [ ] **Color Contrast**: 4.5:1 minimum on all text (use contrast checker)
  - [ ] **Icons**: Color + label/icon (not color alone for meaning)
  - [ ] **Responsive Text**: 14px minimum, 1.5x line height
  - [ ] **Skip Link**: "Skip to main content" visible on focus
  - [ ] **Form Labels**: Explicit `<label>` tags, `aria-label` on buttons
  - [ ] **Error Messages**: Associated with form field, `aria-invalid="true"` on input
  - [ ] **Lighthouse Audit**: Score ≥90, 0 accessibility issues
  - [ ] Run axe DevTools, fix all violations
  - [ ] Test with screen reader (NVDA/JAWS): Verify navigation, messaging

---

### Phase 4 Tasks

**Task 4.1**: Write Unit Tests for Hooks & Utilities
- **Effort**: 1 hour
- **Owner**: Frontend Engineer / QA
- **Deliverable**: `frontend/tests/hooks/*.test.ts`, `frontend/tests/utils/*.test.ts`
- **Dependencies**: Tasks 2.1, 3.4
- **Test Cases**:
  - [ ] useWebSocket: Connection, disconnect, reconnection logic
  - [ ] useTimer: Timer tick, state transitions
  - [ ] useSessionState: State updates, localStorage persistence
  - [ ] formatters.ts: Time formatting (8:00 → "8 minutes"), score % calculation
  - [ ] validators.ts: Message length validation, empty check
  - [ ] pdf-export.ts: PDF generation, content verification
  - [ ] Coverage ≥80%
  - [ ] All tests pass (100%)

**Task 4.2**: Write Component Tests (Main UI)
- **Effort**: 0.5 hours
- **Owner**: Frontend Engineer / QA
- **Deliverable**: `frontend/tests/components/*.test.tsx`
- **Dependencies**: Tasks 2.2-2.8, 3.1-3.4
- **Test Cases**:
  - [ ] SessionPage: Renders chat, timer, patient info
  - [ ] ChatWindow: Displays messages, auto-scrolls
  - [ ] TimerDisplay: Countdown, warning state, accuracy
  - [ ] MessageInput: Validation, send on button/Enter
  - [ ] ResultsPage: Rubric display, score calculations
  - [ ] PersonaBrowsePage: Filter, pagination, search
  - [ ] Coverage ≥80%

**Task 4.3**: Performance Profiling & Optimization
- **Effort**: 0.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: Optimized bundle, lazy-loaded routes
- **Dependencies**: All tasks
- **Optimizations**:
  - [ ] Code splitting: Lazy load routes (React.lazy + Suspense)
  - [ ] Bundle size: <300KB gzipped (check with `npm run build`)
  - [ ] Image optimization: Compress with ImageOptim or similar
  - [ ] Memoization: React.memo on ChatMessage, ScoreCard (prevent re-renders)
  - [ ] useMemo/useCallback: Optimize expensive calculations, event handlers
  - [ ] Lighthouse audit: Performance score ≥90
  - [ ] Chat scroll: 60fps (check DevTools Performance tab)
  - [ ] Page load: <2s first contentful paint (Lighthouse)

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements

**Persona Discovery**:
- [ ] Persona list loads with pagination (20 per page)
- [ ] Filters work: Specialty, difficulty, search
- [ ] Persona detail page displays demographics and chief complaint
- [ ] "Start Practice" button works on detail page

**Chat & Timer**:
- [ ] WebSocket connects with session token
- [ ] Opening patient message displays on connect
- [ ] Message input validates (not empty, <5000 chars)
- [ ] Send button submits message and clears input
- [ ] Patient responses appear in real-time
- [ ] Timer counts down accurately (±0.5 seconds)
- [ ] 1-minute warning displays at 7:00
- [ ] Session auto-finalizes at 8:00 (input disabled)
- [ ] Emotional state indicator updates when patient state changes
- [ ] Chat auto-scrolls to latest message
- [ ] Timestamp shows on each message (HH:MM)

**Results & Scoring**:
- [ ] Results page displays on session end
- [ ] AMC rubric breakdown shows all 5 categories
- [ ] Total score and pass/fail status displayed
- [ ] Score cards show percentage progress bars
- [ ] Transcript viewer displays full conversation
- [ ] PDF export generates valid PDF file

**Connection & Recovery**:
- [ ] Network disconnect shows error message
- [ ] Auto-reconnect attempts within 30s
- [ ] Manual reconnect button if auto-reconnect fails
- [ ] Session recovers after reconnect (no message loss)
- [ ] Connection status indicator visible

**Dashboard & History**:
- [ ] Dashboard page lists practice history
- [ ] Each entry shows: Date, persona name, duration, score
- [ ] Clickable to view results

#### Accessibility Requirements (WCAG 2.2 AA)
- [ ] **Keyboard Navigation**: Tab through all elements, Escape closes dialogs
- [ ] **Focus Management**: Visible focus indicators (2px outline)
- [ ] **Screen Reader**: Semantic HTML, ARIA labels, live regions work
- [ ] **Color Contrast**: All text ≥4.5:1 (verified with contrast checker)
- [ ] **Icons**: Always paired with text/label
- [ ] **Mobile Responsive**: Functions on 320px - 1920px width
- [ ] **Skip Link**: "Skip to main content" works
- [ ] **Form Accessibility**: Labels linked, errors associated, ARIA validation

#### Quality Requirements
- [ ] **Test Coverage**: ≥80% (unit + component)
- [ ] **Test Pass Rate**: 100% (zero tolerance for failures)
- [ ] **Linting**: `npm run lint` → 0 errors, 0 warnings
- [ ] **Type Safety**: `npm run typecheck` → 0 errors
- [ ] **No Console Errors**: Zero errors/warnings in browser console

#### Performance Requirements
- [ ] **Page Load**: <2 seconds first contentful paint (Lighthouse)
- [ ] **Bundle Size**: <300KB gzipped (Check via `npm run build`)
- [ ] **Chat Scroll**: Smooth 60fps (DevTools Performance)
- [ ] **Chat Latency**: <2 seconds perceived (p95) message-to-response
- [ ] **Lighthouse Score**: ≥90 (Performance, Accessibility, Best Practices)

#### Security Requirements
- [ ] **JWT Authentication**: Token required for WebSocket
- [ ] **Session Token**: Expires after 8 minutes
- [ ] **HTTPS**: All connections encrypted (wss://)
- [ ] **Input Sanitization**: Messages sanitized before display (no XSS)
- [ ] **Error Messages**: No sensitive data exposed (no error stack traces to user)

---

### Documentation Deliverables

#### Frontend Developer Guide (`frontend/docs/FRONTEND_ARCHITECTURE.md`)
- Component hierarchy and data flow
- API client setup and TanStack Query patterns
- WebSocket integration and reconnection logic
- Zustand store organization
- Testing setup and conventions
- Accessibility checklist
- Performance optimization tips

#### Component Library (`frontend/docs/COMPONENT_LIBRARY.md`)
- All reusable components with props, usage examples
- Design system: Colors, typography, spacing
- Accessibility requirements for each component

#### API Integration Guide (`frontend/docs/API_INTEGRATION.md`)
- All REST endpoints with request/response examples
- WebSocket message protocol
- Error handling patterns
- JWT token management

---

### Testing Requirements

#### Unit Tests
```typescript
// frontend/tests/hooks/useWebSocket.test.ts
describe('useWebSocket', () => {
  it('should connect on mount', async () => {
    // Mock WebSocket, verify connection called
  });

  it('should reconnect with exponential backoff', async () => {
    // Verify retry delays: 1s, 2s, 4s, 8s, etc.
  });

  it('should queue messages while offline', async () => {
    // Disconnect, send message, verify queued
    // Reconnect, verify message sent
  });
});

// frontend/tests/utils/formatters.test.ts
describe('formatters', () => {
  it('should format timer (480 → "8:00")', () => {
    expect(formatTimer(480)).toBe('8:00');
  });

  it('should format percentage (7/15 → "47%")', () => {
    expect(formatPercentage(7, 15)).toBe('47%');
  });
});
```

#### Component Tests
```typescript
// frontend/tests/components/SessionPage.test.tsx
describe('SessionPage', () => {
  it('should display chat window and timer', () => {
    // Render with mock WebSocket
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByText(/8:00/)).toBeInTheDocument();
  });

  it('should send message on button click', async () => {
    // User types, clicks Send
    // Verify WebSocket.send called
  });

  it('should show 1-minute warning at 7:00', async () => {
    // Mock timer update to 420s
    // Verify warning badge displayed
  });
});
```

#### Integration Tests (E2E)
```typescript
// frontend/tests/e2e/session.test.ts
describe('Full Session Flow (E2E)', () => {
  it('should complete 8-minute session', async () => {
    // 1. Login
    // 2. Browse personas, select one
    // 3. Click "Start Practice"
    // 4. Send 3 messages, receive responses
    // 5. Wait until 8:00, verify session ends
    // 6. Verify results page displays scores
    // 7. Verify PDF export works
  });
});
```

---

### Success Validation

**This PRD is considered COMPLETE when**:

1. ✅ Persona browsing and filtering functional
2. ✅ Session initialization working (API call, get JWT)
3. ✅ WebSocket connects and authenticates
4. ✅ Chat messaging real-time and responsive (<2s)
5. ✅ Timer counts down accurately (±0.5s)
6. ✅ 1-minute warning displays at 7:00
7. ✅ Session auto-finalizes at 8:00
8. ✅ Results page displays AMC rubric breakdown
9. ✅ Transcript viewer functional with PDF export
10. ✅ Connection recovery working (reconnect on disconnect)
11. ✅ WCAG 2.2 AA accessibility compliance verified
12. ✅ Test coverage ≥80%, all tests pass
13. ✅ Page load <2s, Lighthouse ≥90
14. ✅ Zero console errors/warnings
15. ✅ Documentation complete (architecture, API, components)

---

### Launch Readiness Checklist

**Pre-Launch (Dev)**:
- [ ] Local development environment setup documented
- [ ] All dependencies installed (npm install)
- [ ] Environment variables (.env.example provided)
- [ ] npm run dev starts dev server
- [ ] npm run build creates optimized production bundle

**Pre-Launch (QA)**:
- [ ] Manual testing checklist completed (all user flows)
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Mobile device testing (iPhone, Android)
- [ ] Screen reader testing (NVDA/JAWS)
- [ ] Load testing: Concurrent users simulate peak usage
- [ ] WebSocket load test: 100+ concurrent sessions

**Pre-Launch (DevOps)**:
- [ ] CI/CD pipeline configured (GitHub Actions)
- [ ] Automated tests run on PR/push
- [ ] Build artifact uploaded to CDN
- [ ] Environment variables secured (no secrets in code)
- [ ] Monitoring alerts configured (error rate, latency)
- [ ] Rollback plan documented

**Pre-Launch (Security)**:
- [ ] HTTPS/WSS only (no HTTP/WS)
- [ ] JWT token validation on every request
- [ ] CORS headers configured correctly
- [ ] Rate limiting on API endpoints
- [ ] Input sanitization (prevent XSS)
- [ ] SQL injection prevention (use parameterized queries)

---

## Dependencies Matrix

| Task | Depends On | Enables |
|------|-----------|---------|
| 1.1 | Backend PRD_001 | 1.2, 1.3, 1.4 |
| 1.2 | 1.1 | 1.3 |
| 1.3 | 1.2 | 1.4 |
| 1.4 | 1.3, Backend PRD_001 | 1.5, 2.1 |
| 1.5 | 1.4 | 2.1-2.8 |
| 1.6 | 1.1-1.5 | All |
| 2.1 | 1.4, 1.5 | 2.2-2.8 |
| 2.2 | 1.5, 2.1 | 3.1-3.4 |
| 2.3 | 1.5, 2.1 | 2.8 |
| 2.4 | 1.5, 2.1 | 3.1 |
| 2.5 | 1.5, 2.2 | 2.8 |
| 2.6 | 1.5, 2.5 | 3.2 |
| 2.7 | 2.2 | 2.8 |
| 2.8 | 2.1 | 3.5 |
| 3.1 | Backend PRD_003, 2.4 | 3.2 |
| 3.2 | 3.1 | 3.5 |
| 3.3 | 2.2 | 3.4 |
| 3.4 | 3.3 | 4.3 |
| 3.5 | 2.1-2.8, 3.1-3.4 | 4.1-4.3 |
| 4.1 | 2.1, 3.4 | Launch |
| 4.2 | 2.2-2.8, 3.1-3.4 | Launch |
| 4.3 | All tasks | Launch |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| WebSocket latency >2s | Medium | High | Implement connection pooling, optimize AI service |
| Browser WebSocket incompatibility | Low | Medium | Test on major browsers (Chrome, Firefox, Safari, Edge) |
| Accessibility compliance gaps | Medium | Medium | Conduct WCAG audit early (Task 3.5), use automated tools |
| Performance regression (slow scroll) | Medium | Medium | Profile with DevTools, lazy load messages, memoize |
| Session timeout/recovery issues | Medium | High | Thorough testing of disconnect/reconnect scenarios |
| Mobile responsiveness problems | Low | Low | Design mobile-first, test on real devices |
| PDF export file size >2MB | Low | Low | Optimize by excluding large data, compress images |
| JWT token expiry during session | Low | Medium | Refresh token before expiry, handle 401 gracefully |

---

## Resource Allocation

- **Frontend Engineer**: 20-24 hours (Tasks 1.1-4.3)
- **QA/Testing**: 4-6 hours (Task 4.1-4.2, accessibility audit)
- **Designer** (optional): 2-3 hours (component design review, accessibility review)
- **DevOps**: 1-2 hours (CI/CD setup, environment config)

**Total**: 24-28 hours (3.5-4 days for one engineer)

---

**Document Status**: Complete
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Version**: 1.0
**File Size**: ~48 KB
**Target Readers**: Frontend Engineers, QA, Product Managers, Designers

---

## Related Documents

- **Depends On**: PRD_AI_OSCE_001_DATABASE_AND_APIS, PRD_AI_OSCE_002_AI_INTEGRATION, PRD_AI_OSCE_003_WEBSOCKET_INFRASTRUCTURE
- **Enables**: PRD_AI_OSCE_006_MOCK_EXAM_ORCHESTRATION, Analytics Dashboard (Phase 2)
- **Architecture Ref**: AI_OSCE_SIMULATION_INTEGRATION_ARCHITECTURE.md (Section 1-2)
- **WebSocket Protocol**: PRD_AI_OSCE_003_WEBSOCKET_INFRASTRUCTURE.md (Message Types section)
