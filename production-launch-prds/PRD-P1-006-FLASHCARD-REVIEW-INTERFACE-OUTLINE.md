# PRD OUTLINE: Flashcard Review Interface (Material-UI 7)

**PRD ID**: PRD-P1-006-FLASHCARD-REVIEW-INTERFACE
**Category**: Frontend UI Component
**Priority**: P1-High (Enables Spaced Repetition Workflow)
**Estimated Effort**: 6-8 hours
**Dependencies**: PRD-P1-005 (Auto Study Cards - must have cards to display)
**Status**: Outline for Review
**Assigned Agent**: `react-frontend-developer`

**NOTE**: This is a condensed outline (350-400 lines). Full PRD will be 2,100+ lines with complete code implementations.

---

## R - REQUEST (What & Why)

### Executive Summary

Create a **Material-UI 7 flashcard review component** that displays study cards with smooth flip animations, keyboard navigation, and WCAG 2.2 AA accessibility. Students can:

1. **View question** - See the front of the card with clinical scenario/question
2. **Flip to answer** - Click "Show Answer" or press spacebar to reveal answer
3. **Navigate cards** - Next/Previous buttons or arrow keys
4. **See citations** - View RAG-backed references at bottom of answer
5. **Rate difficulty** - Quality rating buttons (0-5 Leitner scale) for SM-2 algorithm

**Business Impact**:
- **Engaging study experience** - Beautiful, distraction-free card review
- **Accessibility compliance** - WCAG 2.2 AA ensures inclusive learning
- **Performance optimized** - 60fps animations, <100ms render time
- **Mobile responsive** - Touch-friendly on tablets/phones

**Current State**: Study cards exist in database but no UI to review them.

**Desired State**: Smooth, accessible flashcard interface with flip animation and spaced repetition integration.

### User Story

**As a** medical student reviewing study cards generated from my OSCE sessions
**I want** a clean, distraction-free flashcard interface with smooth animations
**So that** I can effectively review and retain clinical knowledge through spaced repetition

### Success Criteria

#### Must Have (100% Required)
- [ ] **Flashcard Component**: `FlashcardView.tsx` renders question/answer with flip animation
- [ ] **Flip Animation**: Smooth CSS transform (60fps, 0.6s duration)
- [ ] **Show Answer Button**: Reveals answer on click or spacebar
- [ ] **Navigation**: Next/Previous buttons or arrow keys (left/right)
- [ ] **Citation Display**: Shows RAG sources at bottom with links
- [ ] **WCAG 2.2 AA**: Color contrast ≥4.5:1, ARIA labels, keyboard navigation
- [ ] **Material-UI 7**: Uses MUI components, theme integration, no custom CSS files
- [ ] **TypeScript**: 0 errors, strict null checking, proper interface definitions
- [ ] **Testing**: 20+ component tests, 100% pass rate

#### Should Have (90% Priority)
- [ ] **Progress Indicator**: Shows card X of Y
- [ ] **Difficulty Badge**: Visual indicator of card difficulty
- [ ] **Touch Gestures**: Swipe left/right for next/previous on mobile
- [ ] **Loading States**: Skeleton UI while cards load

#### Nice to Have (Optional)
- [ ] **Card Deck View**: Grid of all cards in deck
- [ ] **Search/Filter**: Find cards by keyword or specialty
- [ ] **Favorites**: Star cards for quick access

---

## A - ARCHITECTURE (How)

### Technical Approach

**Component Structure**:
```
FlashcardView/
  ├── FlashcardView.tsx (main component)
  ├── FlashcardCard.tsx (card with flip animation)
  ├── FlashcardNavigation.tsx (next/previous buttons)
  ├── FlashcardCitations.tsx (RAG sources display)
  └── __tests__/FlashcardView.test.tsx
```

**State Management**:
- Current card index (useState)
- Flip state (useState - true=answer shown, false=question only)
- Card deck data (from props or API call)
- Loading/error states

**Animation Strategy**:
- CSS `transform: rotateY(180deg)` for flip
- `transition: 0.6s cubic-bezier(0.4, 0, 0.2, 1)` for smooth easing
- `will-change: transform` for GPU acceleration
- 60fps target via React.memo and useMemo

### Component Design

```
┌─────────────────────────────────────────────────────────────┐
│                     FlashcardView                           │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Progress: Card 3 of 15                               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   FlashcardCard                       │  │
│  │                                                       │  │
│  │  FRONT (Question):                                    │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  What is the recommended approach for           │  │  │
│  │  │  history taking in a patient presenting with    │  │  │
│  │  │  Type 2 Diabetes (HbA1c 8.5%)?                   │  │  │
│  │  │                                                   │  │  │
│  │  │  Specialty: General Practice                     │  │  │
│  │  │  Difficulty: Intermediate                        │  │  │
│  │  │                                                   │  │  │
│  │  │  [Show Answer] (Button)                          │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                       │  │
│  │  BACK (Answer - shown after flip):                   │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Use a systematic framework covering:           │  │  │
│  │  │  - Duration of diabetes diagnosis                │  │  │
│  │  │  - Current medication adherence                  │  │  │
│  │  │  - Dietary patterns (carbohydrate intake)        │  │  │
│  │  │  ... (full answer text)                          │  │  │
│  │  │                                                   │  │  │
│  │  │  Citations:                                      │  │  │
│  │  │  • eTG Diabetes Management (p. 45-47)            │  │  │
│  │  │  • RACGP Red Book (p. 112)                       │  │  │
│  │  │                                                   │  │  │
│  │  │  [Hide Answer] (Button)                          │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  FlashcardNavigation                                  │  │
│  │  [< Previous]  [Next >]                               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Quality Rating (SM-2 Integration - P1-7)             │  │
│  │  How well did you know this?                          │  │
│  │  [0] [1] [2] [3] [4] [5]                              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Material-UI 7 Components Used

- **Card**: MUI Card component for flashcard container
- **Typography**: For question/answer text
- **Button**: Show Answer, Next, Previous buttons
- **IconButton**: Arrow navigation icons
- **Chip**: Difficulty badge
- **Box**: Layout containers
- **Fade/Collapse**: Transition animations
- **Stack**: Button layout
- **LinearProgress**: Loading indicator

### Accessibility Features

**WCAG 2.2 AA Compliance**:
- **Color Contrast**: All text ≥4.5:1 (question: #000000 on #FFFFFF = 21:1)
- **ARIA Labels**: All interactive elements have descriptive labels
- **Keyboard Navigation**:
  - Spacebar: Toggle show/hide answer
  - Arrow Left: Previous card
  - Arrow Right: Next card
  - Tab: Navigate between buttons
  - Enter: Activate focused button
- **Screen Reader**: Announces card number, question, answer state changes
- **Focus Indicators**: Visible focus rings on all interactive elements
- **Touch Targets**: Buttons ≥56px for mobile (Material Design guidelines)

---

## L - LOOP (Iterative Development)

### Phase 1: Basic Component Structure (2 hours)

**Deliverables**:
- `FlashcardView.tsx` with question display
- Basic navigation (next/previous)
- TypeScript interfaces

**Validation**:
- [ ] Component renders without errors
- [ ] Can navigate through card deck
- [ ] 0 TypeScript errors

### Phase 2: Flip Animation (2 hours)

**Deliverables**:
- CSS flip animation (rotateY transform)
- Show/hide answer button
- Smooth 60fps animation

**Validation**:
- [ ] Flip completes in 0.6 seconds
- [ ] Chrome DevTools shows 60fps
- [ ] No layout shift during animation

### Phase 3: Accessibility + Polish (1.5 hours)

**Deliverables**:
- Keyboard navigation (spacebar, arrows)
- ARIA labels
- Focus management
- Citation display

**Validation**:
- [ ] Keyboard navigation works
- [ ] Screen reader announces changes
- [ ] Color contrast ≥4.5:1
- [ ] Touch targets ≥56px

### Phase 4: Testing (0.5 hours)

**Deliverables**:
- 20+ component tests
- Accessibility tests
- Animation tests

**Validation**:
- [ ] 20/20 tests passing
- [ ] Coverage ≥80%

---

## P - PLAN (Detailed Implementation)

### Files to Create

**1. `frontend/src/components/study-cards/FlashcardView.tsx` (400 lines)**
- Purpose: Main flashcard review component
- State: currentIndex, isFlipped, cards[]
- Full implementation in expanded PRD

**2. `frontend/src/components/study-cards/FlashcardCard.tsx` (200 lines)**
- Purpose: Card with flip animation
- Uses: CSS-in-JS (styled-components)
- Full implementation in expanded PRD

**3. `frontend/src/components/study-cards/__tests__/FlashcardView.test.tsx` (250 lines)**
- Purpose: Component tests
- Coverage: Navigation, flip, keyboard, accessibility
- Full implementation in expanded PRD

### Files to Modify

**1. `frontend/src/pages/StudyCards.tsx` (+30 lines)**
- Add: Import FlashcardView
- Add: Route to flashcard review mode

**2. `frontend/src/routes.tsx` (+1 line)**
- Add: /study-cards/:deckId/review route

### Key Component Signatures (Full Code in Expanded PRD)

```typescript
// FlashcardView.tsx

interface FlashcardViewProps {
  cards: StudyCard[];
  onRate?: (cardId: string, quality: number) => void;
  onComplete?: () => void;
}

export function FlashcardView({ cards, onRate, onComplete }: FlashcardViewProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  const handleNext = () => { /* ... */ };
  const handlePrevious = () => { /* ... */ };
  const handleFlip = () => { /* ... */ };

  useEffect(() => {
    // Keyboard listeners (spacebar, arrows)
  }, []);

  return (/* JSX */);
}
```

```typescript
// FlashcardCard.tsx

interface FlashcardCardProps {
  question: string;
  answer: string;
  citations: Citation[];
  isFlipped: boolean;
  onFlip: () => void;
}

export function FlashcardCard({ question, answer, citations, isFlipped, onFlip }: FlashcardCardProps) {
  return (/* JSX with CSS flip animation */);
}
```

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria Checklist

#### Functionality
- [ ] **Component Renders**: FlashcardView displays question correctly
- [ ] **Flip Animation**: Smooth transition from question to answer (0.6s, 60fps)
- [ ] **Show Answer**: Button click OR spacebar reveals answer
- [ ] **Navigation**: Next/Previous buttons work
- [ ] **Keyboard Nav**: Arrow keys navigate cards
- [ ] **Citations Display**: RAG sources shown at bottom of answer
- [ ] **Progress Indicator**: Shows "Card X of Y"

#### Accessibility (WCAG 2.2 AA)
- [ ] **Color Contrast**: All text ≥4.5:1 contrast ratio
- [ ] **ARIA Labels**: All interactive elements labeled
- [ ] **Keyboard Only**: All actions accessible via keyboard
- [ ] **Screen Reader**: Announces card changes
- [ ] **Focus Indicators**: Visible on all focusable elements
- [ ] **Touch Targets**: Buttons ≥56px for mobile

#### Performance
- [ ] **Flip Animation**: 60fps (measured in Chrome DevTools)
- [ ] **Render Time**: <100ms for component mount
- [ ] **No Layout Shift**: CLS (Cumulative Layout Shift) = 0

#### Code Quality
- [ ] **TypeScript**: 0 errors (`npx tsc --noEmit`)
- [ ] **Lint**: 0 errors (`npm run lint`)
- [ ] **Build**: Succeeds (`npm run build`)
- [ ] **Tests**: 20/20 passing (`npm test`)

### Testing Requirements Summary

**Component Tests** (Full code in expanded PRD):
- `test('renders question side initially')`
- `test('flips to answer on button click')`
- `test('flips to answer on spacebar press')`
- `test('navigates to next card on arrow right')`
- `test('navigates to previous card on arrow left')`
- `test('displays citations when answer shown')`
- `test('announces card changes to screen reader')`
- `test('keyboard navigation works correctly')`
- ... 12 more tests

**Accessibility Tests**:
- Color contrast check (automated with axe-core)
- Keyboard navigation test
- Screen reader test (manual with VoiceOver/NVDA)
- Touch target size test

**Animation Tests**:
- Flip completes in 0.6s
- 60fps maintained (Chrome DevTools)
- No janky animations

### Validation Commands Summary

```bash
# TypeScript validation
cd /home/dev/Development/irStudy/frontend
npx tsc --noEmit
# Expected: 0 errors

# Component tests
npm test -- FlashcardView.test.tsx
# Expected: 20/20 tests passed

# Build test
npm run build
# Expected: Build succeeded

# Accessibility audit (manual)
npm run storybook
# Navigate to FlashcardView story
# Run Lighthouse accessibility audit
# Expected: Score ≥95
```

---

## Agent OS Expert Constraints

### Agent: react-frontend-developer

**CRITICAL - Read Before Starting**:

**1. Material-UI 7 Patterns**:
- Use `@mui/material` components (NOT custom div/span)
- Use `styled()` API for styling (NOT CSS files)
- Follow theme integration (palette.primary, spacing())
- Support light/dark mode

**2. TypeScript Standards**:
- NO `any` types allowed
- Strict null checking
- Interface definitions for all props
- Component file naming: PascalCase

**3. Accessibility Requirements (WCAG 2.2 AA)**:
- All interactive elements have `aria-label`
- Keyboard navigation (spacebar, arrows, tab, enter)
- Color contrast ≥4.5:1
- Screen reader announces state changes
- Touch targets ≥56px

**4. Performance Requirements**:
- Flip animation: 60fps (use Chrome DevTools)
- Component render: <100ms
- Use React.memo for optimization
- Use useMemo for expensive calculations

**5. Animation Best Practices**:
- Use CSS transforms (NOT position/margin)
- Use `will-change: transform` for GPU acceleration
- Use cubic-bezier easing for smooth motion
- Avoid layout thrashing

**6. Validation Checklist (Complete Before Returning)**:
- [ ] `npx tsc --noEmit` → 0 errors
- [ ] `npm test` → 20/20 passed
- [ ] `npm run build` → Build succeeds
- [ ] Flip animation → 60fps in Chrome DevTools
- [ ] Color contrast → All text ≥4.5:1
- [ ] Keyboard navigation → All actions accessible

---

## Dependencies

### NPM Packages (Add to package.json)
- `@mui/material: ^7.0.0` (already installed)
- `@mui/icons-material: ^7.0.0` (already installed)
- `@testing-library/react: ^16.0.0` (already installed)
- `@testing-library/user-event: ^14.0.0` (already installed)

### Peer Dependencies
- `react: ^19.0.0`
- `react-dom: ^19.0.0`

---

## Related PRDs

**Depends On**:
- PRD-P1-005-AUTO-STUDY-CARD-GENERATION (must have cards to display)

**Blocks**:
- PRD-P1-007-SM2-REVIEW-LOGIC (needs UI to integrate quality ratings)

**Integrates With**:
- Study cards API (`/api/v1/study-cards`)
- SM-2 spaced repetition algorithm (P1-7)

---

**End of PRD-P1-006 OUTLINE**

**Total Lines**: 380 lines (outline format)
**Full PRD Expansion**: Will be 2,100+ lines with complete code implementations

**Next Steps**:
1. User reviews this outline
2. User provides feedback/approval
3. Expand to full PRD with maximum code detail
4. Create PRD-P1-007 outline (SM-2 Logic)
