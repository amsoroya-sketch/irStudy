# Frontend TASK_006: Quiz Interface Implementation

## Goal
Implement TASK_006 Quiz Interface components for the irStudy platform following TDD approach.

## What to Build

### Component 1: OSCEPracticePlaceholder
Create `frontend/src/components/osce/OSCEPracticePlaceholder.tsx`
- Display "AI OSCE Practice Coming Soon" alert
- Show disabled "Connect to AI Patient" button with tooltip
- Display static OSCE scenario preview
- Explain backend not ready (AI Patient/Examiner agents not implemented)

### Component 2: AMCRubricDisplay
Create `frontend/src/components/osce/AMCRubricDisplay.tsx`
- Display AMC 15-mark rubric with 5 domains:
  * Communication Skills (0-3 marks)
  * Clinical Reasoning (0-4 marks)
  * Information Gathering (0-3 marks)
  * Management Plan (0-3 marks)
  * Professionalism & Ethics (0-2 marks)
- Show behavioral anchors for each mark level
- Calculate total score out of 15
- Indicate pass threshold (≥10 = pass)

### Component 3: Enhance MCQPracticeInterface
Modify existing `frontend/src/components/mcq/MCQPracticeInterface.tsx`
- Add keyboard shortcuts:
  * Keys 1-5: Select answers A-E
  * Arrow Up/Down: Navigate options
  * Enter: Submit answer
  * N: Next question (after submission)
- Add timer warning states:
  * Yellow warning at <30 seconds
  * Red pulsing warning at <10 seconds
  * Screen reader announcements via aria-live

## Requirements
- Write tests FIRST (TDD approach)
- Use Material-UI v6 components
- WCAG 2.2 AA accessibility (ARIA labels, keyboard nav)
- 0 TypeScript errors
- 80%+ test coverage

## Reference
Full PRD: `frontend-features-15-feb/ralph-prds/PRD_TASK_006_QUIZ_INTERFACE.md`

## DO NOT stop until all 3 components are fully implemented and tested.
