# TASK 1.2: Complete Epic Components

**Phase**: Phase 1 - Frontend Completion
**Estimated Hours**: 8 hours
**Dependencies**: TASK 1.1 complete (Cerner components establish pattern), React 18 + TypeScript, Tailwind CSS
**Agent Type**: `frontend-react-expert`
**Status**: ⏳ Not Started

---

## Overview

Complete implementation of all Epic EHR UI components with purple theme branding and modern icon-based navigation. Epic is the second major EMR system used in Australian hospitals. This task focuses on creating the purple-themed interface with 7 core modules accessed via left icon bar (Storyboard, Patient Summary, Note Writer, Med Manager, Order Entry, Flowsheet, Settings). Includes EpicWorkspacePanel with resizable dual-panel layout, EpicMedicationPanel with PBS search, and EpicTemplateSelector for SOAP/Progress/Discharge templates.

---

## Deliverables

### New Components to Create

- `/emr-frontend/src/components/epic/EpicIconBar.tsx` (220+ lines)
  - Left vertical navigation bar with 8 icon buttons
  - Icon colors per module type
  - Active state highlighting
  - Tooltip labels on hover
  - Keyboard shortcut display

- `/emr-frontend/src/components/epic/EpicWorkspacePanel.tsx` (350+ lines)
  - Resizable dual-panel layout (left: patient info, right: note editor)
  - Vertical resize handle between panels (drag to adjust width)
  - Save/collapse functionality for left panel
  - Responsive: minimum panel widths (300px left, 500px right)
  - Smooth resize animation

- `/emr-frontend/src/components/epic/EpicMedicationPanel.tsx` (300+ lines)
  - Purple-themed medication management interface
  - PBS medication search (same as Cerner but purple theme)
  - Current medications list with edit/remove buttons
  - Allergy section (red background, purple text)
  - Drug interactions display
  - Add new medication button

- `/emr-frontend/src/components/epic/EpicTemplateSelector.tsx` (250+ lines)
  - SOAP Note template
  - Progress Note template
  - Discharge Summary template
  - Template preview before selection
  - Custom template creation option

- `/emr-frontend/src/components/epic/EpicStoryboard.tsx` (280+ lines)
  - Timeline view of patient events
  - Display problems, medications, orders, results
  - Color-coded by category
  - Timeline markers for dates
  - Filter by type (Problems/Meds/Orders/Results)

- `/emr-frontend/src/components/epic/EpicNoteWriter.tsx` (300+ lines)
  - Main note writing interface
  - Template selector integrated
  - SOAP note input with real-time validation
  - Character counters
  - Auto-save 30 seconds
  - Preview mode toggle

- `/emr-frontend/src/components/epic/EpicOrderEntry.tsx` (280+ lines)
  - Unified medication + pathology order entry
  - Tabbed interface (Medications, Pathology, Imaging)
  - Recent orders quick-access list
  - Order basket summary
  - Submit button

### Enhancements to Existing Components

- `/emr-frontend/src/components/epic/EpicHeader.tsx` - If needed
  - Patient banner with Epic styling (purple accents)
  - Session timer
  - Quick action buttons

- Epic-specific constants and utilities
  - Module definitions with Epic colors
  - Template definitions

### Utility & Constants

- `/emr-frontend/src/constants/epic-modules.ts` (60 lines)
  - Module definitions with Epic purple color scheme
  - Icon assignments
  - Keyboard shortcuts

- `/emr-frontend/src/constants/epic-templates.ts` (100 lines)
  - SOAP template with Epic formatting
  - Progress Note template
  - Discharge Summary template
  - Field validation rules per template

---

## Detailed Requirements

### Requirement 1: EpicIconBar Component

**Specification:**

```typescript
interface EpicIconBarProps {
  activeModule: string;
  onModuleSelect: (moduleId: string) => void;
  sessionId: string;
  userRole: 'student' | 'educator';
}

interface EpicModule {
  id: string;
  label: string;
  icon: React.ComponentType;
  color: string;
  shortcut: string; // e.g., "Alt+1"
}
```

**Features:**

- **Icon Bar Layout**:
  - 72px wide vertical bar on left side
  - Dark background (#1f2937)
  - 8 icon buttons (60px x 60px each)
  - Epic logo (purple "E") at top

- **Module Icons** (all from Lucide):
  - Storyboard (activity/timeline icon)
  - Patient Summary (clipboard)
  - Note Writer (document/pen icon)
  - Med Manager (pill icon)
  - Order Entry (clipboard with checkmark)
  - Flowsheet (grid/table icon)
  - Settings (gear icon)
  - Help (question mark) - bonus

- **Active State**:
  - Active icon: purple (#8b5cf6)
  - Inactive icon: gray (#9ca3af)
  - Background highlight on hover
  - Smooth 0.2s transition

- **Tooltips**:
  - Show on hover with 500ms delay
  - Display module name + keyboard shortcut
  - Position to right of icon
  - Dark background with white text

- **Keyboard Navigation**:
  - Alt+1: Storyboard
  - Alt+2: Patient Summary
  - Alt+3: Note Writer
  - Alt+4: Med Manager
  - Alt+5: Order Entry
  - Alt+6: Flowsheet
  - Alt+7: Settings
  - Arrow up/down: cycle through modules

**Styling** (Purple Theme):
- Use CSS variables: --epic-primary (#8b5cf6), --epic-icon-bar (#1f2937)
- Smooth hover effects
- No text labels (icon-only until hover)

**Acceptance Criteria:**
- [ ] 8 module buttons render with correct icons
- [ ] Active module highlighted in purple
- [ ] Tooltips appear on hover after 500ms delay
- [ ] Keyboard shortcuts work (Alt+1, Alt+2, etc.)
- [ ] Arrow keys cycle through modules
- [ ] Smooth transitions between states
- [ ] Responsive: maintains 72px width on all screen sizes

---

### Requirement 2: EpicWorkspacePanel Component

**Specification:**

```typescript
interface EpicWorkspacePanelProps {
  patientInfo: PatientData;
  noteContent: string;
  onNoteChange: (content: string) => void;
  onSave: () => void;
}

interface ResizeState {
  leftPanelWidth: number;  // pixels, min 300, max 60% of viewport
  isDragging: boolean;
}
```

**Features:**

- **Dual Panel Layout**:
  - Left panel: Patient info, allergies, current meds, recent orders
  - Right panel: Note editor (SOAP or template)
  - Vertical resize handle between panels
  - Min left panel: 300px
  - Min right panel: 500px
  - Default split: 40%/60%

- **Resize Handle**:
  - 4px wide, vertical bar
  - Cursor changes to `col-resize` on hover
  - Visual feedback: shows on hover as colored bar
  - Smooth drag animation

- **Left Panel Collapse**:
  - Collapse button (<<) to hide patient info
  - Saves space for wider note editor
  - Double-click handle to toggle collapse

- **Responsive Behavior**:
  - On screens <1400px: enforce max right panel width
  - On screens <1024px: stack panels vertically
  - Maintain usability on all sizes

- **Styling**:
  - Left panel background: #f5f3ff (light purple)
  - Right panel background: #ffffff (white)
  - Border between: #d1d5db (gray)
  - Resize handle: #8b5cf6 (purple) on hover

**Acceptance Criteria:**
- [ ] Two panels render side-by-side
- [ ] Resize handle drags smoothly between min/max widths
- [ ] Collapse button hides/shows left panel
- [ ] Double-click handle toggles collapse
- [ ] Panels maintain proper proportions
- [ ] Responsive stacking on small screens
- [ ] No jank during resize (smooth 60fps animation)
- [ ] Panel widths persist in localStorage (optional but nice)

---

### Requirement 3: EpicMedicationPanel Component

**Specification:**

```typescript
interface EpicMedicationPanelProps {
  patientAllergies: string[];
  currentMedications: Medication[];
  onAddMedication: (medication: Medication) => void;
  onRemoveMedication: (medicationId: string) => void;
}

interface Medication {
  id: string;
  name: string;
  dose: string;
  frequency: string;
  indication: string;
  startDate: string;
  endDate?: string;
}
```

**Features:**

- **Current Medications List**:
  - Display each medication with dose, frequency, start date
  - Action buttons: Edit, Stop, View History
  - Sort options: By start date, alphabetical, by indication
  - Search/filter by medication name

- **Allergies Section**:
  - Red background (#ef4444)
  - White text
  - Bold "ALLERGIES:" label
  - List all allergies comma-separated
  - Allergy type icon (e.g., warning triangle)

- **Add Medication Flow**:
  - Click "+ Add Medication" button
  - Opens modal with PBS search
  - Same search functionality as Cerner component
  - Can specify dose, frequency, indication
  - Save or cancel

- **Drug Interactions**:
  - If interactions detected, show warning banner
  - List each interaction with severity level
  - Color code: Red (major), Yellow (moderate), Blue (minor)
  - Show suggested action (e.g., "Monitor renal function")

- **Styling** (Purple Theme):
  - Use Epic color palette
  - Purple headings (#8b5cf6)
  - Light purple background (#f5f3ff)
  - White cards for each section
  - Consistent spacing (16px margins)

**Acceptance Criteria:**
- [ ] Current medications list displays with all details
- [ ] Allergies shown with red background
- [ ] Add medication button opens modal
- [ ] PBS search functional in modal
- [ ] Drug interactions detected and displayed
- [ ] All buttons (Edit, Stop, Add) functional
- [ ] No console errors or warnings
- [ ] Responsive on all screen sizes

---

### Requirement 4: EpicTemplateSelector Component

**Specification:**

```typescript
interface EpicTemplateSelectorProps {
  onSelectTemplate: (template: Template) => void;
  onCancel: () => void;
}

interface Template {
  id: string;
  name: string;
  description: string;
  fields: TemplateField[];
  preview: string;
}
```

**Features:**

- **Template Options**:
  - **SOAP Note**: Structured format with S/O/A/P sections
    - Description: "Subjective, Objective, Assessment, Plan - Standard clinical note format"
    - Fields: [subjective, objective, assessment, plan]

  - **Progress Note**: Focused update on patient progress
    - Description: "Brief update on current status and changes since last note"
    - Fields: [current_status, changes, assessment, next_steps]

  - **Discharge Summary**: Comprehensive discharge documentation
    - Description: "Complete summary of admission, treatment, and discharge instructions"
    - Fields: [admission_reason, hospital_course, medications, follow_up, instructions]

- **Visual Presentation**:
  - 3 template cards displayed side-by-side
  - Each card shows: Name, description, preview
  - Click to select, shows larger preview
  - "Use This Template" button appears on selection
  - "Cancel" button to go back

- **Template Preview**:
  - Shows field labels and example structure
  - Gray placeholder text in fields
  - Scrollable if preview is long
  - Shows character limits for each field

- **Custom Template Option**:
  - 4th card: "+ Create Custom Template"
  - Allows user to define custom field structure
  - Advanced feature - can be skip for MVP

**Styling**:
- Grid layout: 3 columns (2 columns on tablet, 1 on mobile)
- Card elevation on hover
- Purple accent color for selected template
- Clean, minimal design

**Acceptance Criteria:**
- [ ] 3 template cards render correctly
- [ ] Template preview shows correct fields
- [ ] Selection updates UI appropriately
- [ ] "Use This Template" button functional
- [ ] Cancel button returns to previous view
- [ ] Responsive grid layout
- [ ] No console errors

---

### Requirement 5: EpicNoteWriter Component

**Specification:**

```typescript
interface EpicNoteWriterProps {
  patientId: string;
  sessionId: string;
  selectedTemplate: Template;
  onSave: (note: NoteData) => void;
  onSubmitForValidation: (note: NoteData) => void;
}

interface NoteData {
  template_id: string;
  content: Record<string, string>; // key: field name, value: field content
  created_at: timestamp;
  updated_at: timestamp;
}
```

**Features:**

- **Note Editing**:
  - Display fields based on selected template
  - Each field has label and text area
  - Character counter below each field
  - Real-time validation feedback
  - Min character requirement validation

- **Auto-Save**:
  - Debounced 30 seconds
  - "Saving..." indicator while saving
  - "Saved at HH:MM" confirmation
  - Cancel on unmount

- **Preview Mode**:
  - Toggle between Edit and Preview
  - Preview shows formatted note
  - Read-only in preview mode
  - Edit button to return to editing

- **Typing Metrics** (optional):
  - Display WPM, character count, time elapsed
  - Small card in corner
  - Doesn't interfere with editing

- **Action Buttons**:
  - Save Draft (saves but doesn't submit)
  - Submit for Validation (sends for AI review)
  - Clear (reset form - confirm dialog)
  - Cancel (exit without saving - confirm if changes)

- **Styling** (Epic Purple Theme):
  - Light purple background (#f5f3ff)
  - White text areas
  - Purple headings and buttons
  - Consistent spacing and typography

**Acceptance Criteria:**
- [ ] All template fields render correctly
- [ ] Character counters display and update
- [ ] Real-time validation shows feedback
- [ ] Auto-save triggers every 30 seconds
- [ ] Preview mode displays formatted note
- [ ] Save and Submit buttons functional
- [ ] Typing metrics display (if included)
- [ ] No console errors
- [ ] Responsive on all screen sizes

---

### Requirement 6: EpicStoryboard Component

**Specification:**

```typescript
interface EpicStoryboardProps {
  patientEvents: PatientEvent[];
  filters: StoryboardFilter[];
}

interface PatientEvent {
  id: string;
  date: string;
  type: 'problem' | 'medication' | 'order' | 'result' | 'note';
  title: string;
  description: string;
  color: string;
}

interface StoryboardFilter {
  label: string;
  type: string;
  enabled: boolean;
}
```

**Features:**

- **Timeline View**:
  - Vertical timeline with date markers
  - Events shown as cards to right of timeline
  - Chronological order (newest first)
  - Color-coded by event type:
    - Problems: Red (#ef4444)
    - Medications: Green (#10b981)
    - Orders: Blue (#3b82f6)
    - Results: Orange (#f59e0b)
    - Notes: Purple (#8b5cf6)

- **Event Cards**:
  - Date/time in small text
  - Title (bold)
  - Brief description
  - Type icon
  - Click to expand with full details

- **Filter Options**:
  - Checkbox filters: Problems, Medications, Orders, Results
  - Toggle filters on/off
  - Timeline updates dynamically
  - Remember filter state in localStorage

- **Expandable Events**:
  - Click event card to expand
  - Show full details in modal or panel
  - Display related items (e.g., medication orders related to problem)

- **Search**:
  - Search box to filter events by title/description
  - Real-time search results
  - Highlight matching text

**Styling** (Purple Theme):
- Use Epic color palette
- Timeline line: light purple (#d1d5db)
- Events: color-coded with smooth animations
- Hover effects on cards
- Clean, professional timeline UI

**Acceptance Criteria:**
- [ ] Timeline renders with all events
- [ ] Events color-coded by type
- [ ] Filter buttons functional
- [ ] Search filters events in real-time
- [ ] Click event expands with details
- [ ] Responsive timeline on mobile (horizontal scroll or collapsed)
- [ ] No console errors

---

## Acceptance Criteria (Overall Task)

### Component Quality
- [ ] All components render without console errors or warnings
- [ ] TypeScript compilation produces 0 errors
- [ ] All props properly typed with interfaces
- [ ] No PropTypes issues

### Functionality
- [ ] EpicIconBar: Module selection, keyboard shortcuts, tooltips work
- [ ] EpicWorkspacePanel: Resizable panels, collapse functionality, responsive
- [ ] EpicMedicationPanel: Add/remove meds, allergy display, interactions show
- [ ] EpicTemplateSelector: Template selection, preview, Use Template button
- [ ] EpicNoteWriter: Auto-save (30s), char counters, validation display
- [ ] EpicStoryboard: Timeline events, filtering, search functional

### Styling & Theming
- [ ] All components use Epic color scheme (#8b5cf6, #f5f3ff, white)
- [ ] Consistent spacing and typography
- [ ] Responsive design: works 1024px and larger
- [ ] Purple theme applied throughout
- [ ] No inline styles (Tailwind classes only)

### Validation & Safety
- [ ] Patient allergies prevent prescription of allergenic medications
- [ ] PBS rules enforced (max 5 repeats, valid items)
- [ ] All user inputs validated before processing
- [ ] Character limits enforced

### Testing
- [ ] Unit tests written for all components (80%+ coverage)
- [ ] Test cases cover happy path and error scenarios
- [ ] All tests pass 100%
- [ ] No TypeScript errors
- [ ] No console errors/warnings

### Performance
- [ ] Workspace panel resize smooth (60fps)
- [ ] Auto-save debounced (30s)
- [ ] Component render <16ms
- [ ] No memory leaks on unmount
- [ ] Smooth animations and transitions

---

## Testing Requirements

### Unit Tests

#### EpicIconBar.test.tsx
```typescript
test('All 8 modules render with correct icons', () => { });
test('Active module highlighted in purple', () => { });
test('Clicking module calls onModuleSelect', () => { });
test('Keyboard shortcut Alt+1 selects first module', () => { });
test('Arrow keys cycle through modules', () => { });
test('Tooltips appear on hover after 500ms', () => { });
```

#### EpicWorkspacePanel.test.tsx
```typescript
test('Left and right panels render', () => { });
test('Resize handle drags to change panel widths', () => { });
test('Collapse button hides left panel', () => { });
test('Double-click handle toggles collapse', () => { });
test('Responsive stacking on screens <1024px', () => { });
test('Min panel widths enforced (300px left, 500px right)', () => { });
```

#### EpicMedicationPanel.test.tsx
```typescript
test('Current medications list displays correctly', () => { });
test('Allergies shown with red background', () => { });
test('Add Medication button opens modal', () => { });
test('PBS search works in modal', () => { });
test('Drug interactions detected and displayed', () => { });
test('Edit and Remove buttons functional', () => { });
```

#### EpicNoteWriter.test.tsx
```typescript
test('Template fields render correctly', () => { });
test('Character counters display and update', () => { });
test('Auto-save triggers every 30 seconds', () => { });
test('Preview mode displays formatted note', () => { });
test('Save button saves to localStorage', () => { });
test('Submit button triggers validation', () => { });
```

---

## Reference PRD Sections

- **Master EMR PRD**: Section 1.1 (Epic EHR Simulation)
  - Location: `/home/dev/Development/irStudy/emr-practice-system/prd/00_MASTER_EMR_PRD.md`
  - Sections: Lines 48-51 (Epic overview)

- **Epic UI PRD**: Complete document
  - Location: `/home/dev/Development/irStudy/emr-practice-system/prd/02_EPIC_EHR_UI_PRD.md`
  - Sections: All major sections on Epic components

- **Styling PRD**: Epic color palette and component styling
  - Location: `/home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md`
  - Sections: Lines 101-133 (Epic colors), Epic component specs

- **Differences from Cerner**:
  - Icon-based navigation vs. sidebar
  - Purple theme vs. dark blue
  - Modern vs. traditional UI

---

## Agent OS Delegation Prompt

```
Agent Task: Complete Epic EHR UI Components

CRITICAL - Read constraints FIRST:
1. Read /home/dev/Development/irStudy/constraints/README.md completely
2. Read /home/dev/Development/irStudy/CLAUDE.md (project-specific requirements)
3. Review completed TASK 1.1 (Cerner components) for pattern consistency
4. Search for existing React patterns in /home/dev/Development/irStudy/frontend/src/components/
5. Reference PRD: /home/dev/Development/irStudy/emr-practice-system/prd/02_EPIC_EHR_UI_PRD.md
6. Reference styling: /home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md

CONTEXT:
- This is part of EMR practice system for Australian medical students (ICRP preparation)
- Epic is modern purple-themed EMR (vs. Cerner dark blue)
- Icon-based navigation (vs. Cerner sidebar)
- Resizable workspace panels (key Epic feature)
- TypeScript + React 18 + Tailwind CSS stack
- Zero tolerance for TypeScript compilation errors
- Must match Epic UX patterns from real system

DELIVERABLES:
1. EpicIconBar.tsx (220+ lines) - Left navigation with 8 module icons
2. EpicWorkspacePanel.tsx (350+ lines) - Resizable dual-panel layout
3. EpicMedicationPanel.tsx (300+ lines) - Purple-themed med management
4. EpicTemplateSelector.tsx (250+ lines) - SOAP/Progress/Discharge templates
5. EpicStoryboard.tsx (280+ lines) - Timeline view of patient events
6. EpicNoteWriter.tsx (300+ lines) - Template-based note editor with auto-save
7. EpicOrderEntry.tsx (280+ lines) - Unified order entry (meds + pathology)
8. Constants: epic-modules.ts, epic-templates.ts

CRITICAL REQUIREMENTS:
1. Epic Color Theme - MANDATORY:
   - Primary: #8b5cf6 (purple)
   - Dark: #581c87
   - Light background: #f5f3ff
   - White: #ffffff
   - Text: #1f2937 (dark gray)
   - Accent success: #10b981 (green)

2. Icon-Based Navigation (NOT sidebar):
   - Left icon bar, 72px wide
   - 8 module icons (Storyboard, Patient Summary, Note Writer, Med Manager, Order Entry, Flowsheet, Settings)
   - Active state in purple
   - Tooltip labels on hover
   - Keyboard shortcuts (Alt+1, Alt+2, etc.)

3. Workspace Panel Resizing:
   - Smooth drag between panels (no jank)
   - Min widths enforced (300px left, 500px right)
   - Double-click to collapse
   - Responsive stacking on small screens
   - CRITICAL: 60fps animation, no layout thrashing

4. Template System:
   - SOAP template (S/O/A/P sections)
   - Progress Note template
   - Discharge Summary template
   - Each template has field validation rules
   - Preview before selection

5. Auto-Save & Validation:
   - 30-second debounce
   - Display "Saving..." and "Saved at HH:MM"
   - Cancel on unmount
   - Real-time character counters

6. Australian Medical Compliance:
   - Use Australian medication names
   - PBS rules: max 5 repeats
   - MBS item validation
   - Allergy checking with red background display

VALIDATION CHECKLIST (self-validate before returning):
- [ ] Read constraints README and CLAUDE.md
- [ ] Reviewed TASK 1.1 Cerner components for pattern consistency
- [ ] Searched for existing React patterns
- [ ] 0 TypeScript errors (npm run type-check)
- [ ] All tests pass 100% (npm run test)
- [ ] No console warnings/errors
- [ ] EpicIconBar renders with correct icons and purple theme
- [ ] Keyboard shortcuts work (Alt+1 through Alt+7)
- [ ] Workspace panel resize is smooth (60fps, no jank)
- [ ] Min panel widths enforced
- [ ] Collapse/expand functionality works
- [ ] Templates display correct fields
- [ ] Auto-save debounced at 30 seconds
- [ ] Character counters display and update in real-time
- [ ] Allergies displayed with red background
- [ ] Drug interactions detected and shown
- [ ] All components responsive (1024px+)
- [ ] Purple theme consistent throughout
- [ ] No memory leaks on unmount
- [ ] All button interactions functional

ACCEPTANCE CRITERIA (task COMPLETE when all pass):
- [ ] All components render without console errors
- [ ] TypeScript: 0 errors
- [ ] All unit tests pass (80%+ coverage)
- [ ] EpicIconBar: Modules selectable, keyboard shortcuts work, tooltips show
- [ ] EpicWorkspacePanel: Panels resize smoothly, collapse works, responsive
- [ ] EpicMedicationPanel: Meds display, allergies red, interactions shown
- [ ] EpicTemplateSelector: 3 templates display, preview works, selection functional
- [ ] EpicNoteWriter: Template fields render, auto-save (30s), char counters show
- [ ] EpicStoryboard: Timeline renders, filtering/search work
- [ ] All components use Epic purple theme correctly
- [ ] Responsive design (1024px+)
- [ ] Performance: Panel resize smooth (60fps), render <16ms, no jank
- [ ] All interaction tests pass (keyboard, click, drag)
- [ ] No console errors or warnings

Return JSON summary:
{
  "status": "COMPLETE",
  "components_created": [...],
  "test_results": "X/X passing",
  "typescript_errors": 0,
  "console_errors": 0,
  "performance_notes": "Workspace panel resize: Xfps, render time: Xms",
  "notes": "..."
}
```

---

## Implementation Notes

### Key Architecture Decisions

1. **Icon-Based vs. Sidebar Navigation**: Epic uses icon bar (72px) vs. Cerner's sidebar (256px). This is a deliberate architectural difference - icon bar saves space and allows wider content area.

2. **Resizable Workspace**: The dual-panel layout with drag resize is the defining Epic feature. Must be smooth and performant:
   - Use `onMouseMove` + `onMouseUp` for drag tracking
   - Update state in RAF (requestAnimationFrame) for 60fps
   - Debounce resize events to prevent layout thrashing

3. **Template System**: Unlike Cerner (free-form note), Epic uses templates. Templates define field structure and validation.

4. **Color Consistency**: Epic is exclusively purple (#8b5cf6 and variants). No other primary colors like Cerner's multi-color modules.

### Performance Optimization

For the workspace resize (most performance-critical):
```typescript
const handleMouseMove = useCallback((e: MouseEvent) => {
  if (!isDragging) return;

  requestAnimationFrame(() => {
    const newWidth = e.clientX - containerRef.current.offsetLeft;
    if (newWidth >= MIN_LEFT_WIDTH && newWidth <= MAX_LEFT_WIDTH) {
      setLeftPanelWidth(newWidth);
    }
  });
}, [isDragging]);
```

This ensures:
- No layout recalculation on every mousemove
- 60fps animation
- Smooth drag experience

### Template Field Validation

Each template defines field validation:
```typescript
const SOAP_TEMPLATE: Template = {
  id: 'soap',
  name: 'SOAP Note',
  fields: [
    { name: 'subjective', label: 'Subjective', min: 50, max: 2000 },
    { name: 'objective', label: 'Objective', min: 50, max: 2000 },
    { name: 'assessment', label: 'Assessment', min: 30, max: 1000 },
    { name: 'plan', label: 'Plan', min: 30, max: 1500 }
  ]
};
```

### Common Pitfalls to Avoid

1. **Workspace Panel Resize Jank**: Use RAF + debounce, not direct state updates
2. **Memory Leaks**: Always cleanup mouse listeners in useEffect
3. **Icon Bar Width**: Keep at 72px strictly (affects responsive breakpoints)
4. **Color Consistency**: Use CSS variables, not hardcoded colors
5. **Tooltip Delay**: Implement 500ms delay to avoid flickering
6. **Auto-Save Persistence**: Use localStorage + backend API, cancel on unmount

### Testing Resize Functionality

```typescript
test('Workspace panel resize is smooth', () => {
  render(<EpicWorkspacePanel />);
  const handle = screen.getByTestId('resize-handle');

  fireEvent.mouseDown(handle);
  fireEvent.mouseMove(document, { clientX: 600 });
  fireEvent.mouseUp(document);

  // Verify new width is within min/max bounds
  expect(leftPanel).toHaveStyle('width: 600px');
});
```

---

## Progress Tracking

- **Status**: ⏳ Not Started
- **Start Date**: [Fill when started]
- **End Date**: [Fill when completed]
- **Actual Hours**: [Fill when completed]
- **Blockers**: [Document any blockers encountered]
- **Notes**: [Any important notes during implementation]

### Checkpoint 1: Components Created (Est. 3 hours)
- [ ] EpicIconBar.tsx created with icon rendering
- [ ] EpicWorkspacePanel.tsx created with basic layout
- [ ] EpicMedicationPanel.tsx created with structure
- [ ] EpicTemplateSelector.tsx created with card layout
- [ ] All TypeScript interfaces defined

### Checkpoint 2: Functionality Implemented (Est. 4 hours)
- [ ] Icon bar keyboard shortcuts working
- [ ] Workspace panel resize smooth and performant
- [ ] Template selector displays previews
- [ ] Auto-save functional (30s debounce)
- [ ] Character counters display
- [ ] Allergy display with red background

### Checkpoint 3: Tests & Polish (Est. 1 hour)
- [ ] All unit tests written and passing
- [ ] No TypeScript errors
- [ ] No console errors/warnings
- [ ] Performance verified (60fps resize, <16ms render)
- [ ] All interactive features tested manually

---

**Previous Task**: TASK 1.1 - Complete Cerner Components
**Next Task**: TASK 1.3 - State Management
