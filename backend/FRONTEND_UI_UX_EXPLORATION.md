# irStudy Frontend Exploration Report
## UI/UX Design and Navigation Architecture

**Date**: May 27, 2026
**Project**: irStudy Platform (EMR + AI OSCE)
**Technology Stack**: React 19 + TypeScript + Material-UI (MUI) v7 + Vite

---

## 1. Overall Application Architecture

### Application Structure
The irStudy frontend is a responsive, mobile-first React application with lazy-loaded routes and code-splitting for performance optimization.

**Entry Point**: `/home/dev/Development/irStudy/frontend/src/main.tsx`
**Main App**: `/home/dev/Development/irStudy/frontend/src/App.tsx`

### Key Features
- Protected routes with RBAC (Role-Based Access Control)
- React Query for data fetching and caching
- Mobile-first responsive design
- Accessibility compliance (WCAG 2.2 AA)
- Multiple study modules: MCQ, OSCE, EMR, Mock Exams

---

## 2. Design System / Theme

### Theme Configuration
**Location**: `/home/dev/Development/irStudy/frontend/src/theme/theme.ts`

#### Color Palette
- **Primary**: #1976d2 (blue)
- **Secondary**: #dc004e (pink/red)
- **Success**: #4caf50 (green)
- **Error**: #f44336 (red)
- **Warning**: #ff9800 (orange)
- **Info**: #2196f3 (light blue)
- **Background**: #f5f5f5 (light gray)
- **Paper**: #ffffff (white)

#### Typography System
- **Font Family**: Roboto
- **Heading Sizes**: h1-h6 (2.5rem down to 1rem)
- **Body**: body1 (1rem), body2 (0.875rem)
- **Responsive**: Automatically scales on mobile using `responsiveFontSizes()`

#### Responsive Breakpoints
```
xs: 320px   (mobile small)
sm: 768px   (tablet)
md: 1024px  (desktop small)
lg: 1280px  (desktop large)
xl: 1920px  (desktop XL)
```

#### Component-Level Customizations
- **MuiButton**: Rounded (8px), no text-transform, responsive padding
- **MuiCard**: Rounded (12px), elevation adjusts for mobile
- **MuiIconButton**: 44px minimum touch target on mobile
- **MuiTextField**: 16px font on mobile (prevents iOS zoom)
- **MuiDialog**: Full-screen on mobile (<768px)
- **MuiAppBar/Toolbar**: Height 56px mobile, 64px desktop

#### Spacing Scale
- **Base Unit**: 8px
- **Border Radius**: 8px (default), 12px (cards)

---

## 3. Navigation Structure

### Main Routes
**Routes File**: `/home/dev/Development/irStudy/frontend/src/routes.tsx`

#### Public Routes
- `/login` - Login page
- `/register` - Registration page

#### Protected Routes (Authenticated Users)

**Dashboard & Main**
- `/dashboard` - Unified dashboard (PRD-MVP-002)
- `/performance` - Performance analytics dashboard

**MCQ Practice**
- `/mcqs` - MCQ browser (search, filter, pagination)
- `/mcqs/:id/attempt` - Single MCQ attempt with timer

**Study Cards**
- `/study-cards` - Flashcard review (spaced repetition)

**OSCE Practice**
- `/osce-practice` - OSCE practice module
- `/osce/session/:attemptId` - Active OSCE session
- `/osce/mock-exam/start` - Start mock exam
- `/osce/mock-exam/:examId/station/:stationNumber` - Mock exam station
- `/osce/mock-exam/:examId/results` - Mock exam results

**EMR Training**
- `/emr/start` - Start new EMR session
- `/emr/select/:sessionId` - Select EMR system (Epic/Cerner)
- `/emr/epic/:sessionId` - Epic EMR simulation
- `/emr/cerner/:sessionId` - Cerner EMR simulation

### Navigation Components

#### Mobile Navigation
**File**: `/home/dev/Development/irStudy/frontend/src/components/layout/MobileBottomNav.tsx`

Bottom navigation bar (shown only on mobile <768px):
- Home → `/dashboard`
- Practice → `/mcqs`
- Study → `/study-cards`
- Progress → `/performance`
- Profile → `/profile`

**Design**:
- Fixed bottom position with safe-area-inset for notched phones
- 56px height
- Touch targets: ≥44px (WCAG compliant)
- Active item indicated via `aria-current="page"`
- Icons: Home, Quiz, School, Dashboard, Person

#### Desktop Navigation
- Presumed sidebar/header navigation (not yet explored)
- Adaptive to available screen width

---

## 4. Page Layout Patterns

### Dashboard Pages
**Primary Dashboard**: `/home/dev/Development/irStudy/frontend/src/pages/UnifiedDashboardPage.tsx`

**Layout Structure**:
```
Container (maxWidth="lg")
├── Header (h1 "Dashboard" + Refresh button)
├── OverallProgressCard (top-level metrics)
├── ModuleStatsGrid (4 modules: MCQ, OSCE, EMR, Mock Exam)
├── Two-Column Grid (md=6 each, responsive)
│   ├── SpecialtyBreakdownChart (left)
│   └── RecentActivityFeed (right)
└── RecommendationsPanel (bottom)
```

**Key Dashboard Components**:
- `OverallProgressCard` - Total sessions, completion %, avg score, time spent
- `ModuleStatsGrid` - Stats for each module (attempts, sessions, average score)
- `SpecialtyBreakdownChart` - Performance by medical specialty
- `RecentActivityFeed` - Timeline of recent activities
- `RecommendationsPanel` - Personalized recommendations
- `ExamReadinessGauge` - Progress towards exam readiness

### MCQ Browser Pattern
**File**: `/home/dev/Development/irStudy/frontend/src/pages/MCQBrowser.tsx`

**Layout**:
```
Container
├── Filters (TextField search, Select for category/difficulty)
├── Results Grid
│   └── Card per MCQ
│       ├── Question preview
│       ├── Difficulty chip
│       ├── Tags
│       └── "Attempt" button
└── Pagination
```

### Study Cards Pattern
**File**: `/home/dev/Development/irStudy/frontend/src/components/study-cards/FlashcardReview.tsx`

**Layout**:
```
Container
├── Current Card (large display)
│   ├── Question
│   ├── [Show Answer button]
│   ├── Answer (revealed on click)
│   └── Citations
├── Quality Ratings (Again, Hard, Good, Easy)
└── Navigation (Next card)
```

---

## 5. Study Notes / Content Display Components

### Existing Content Display Patterns

#### Citation Panel
**File**: `/home/dev/Development/irStudy/frontend/src/components/citations/CitationPanel.tsx`

**Features**:
- Displays Australian medical guideline citations
- Supports sources: eTG, PBS, AMH, AHPRA, RACGP, NSW Health
- Shows: Page numbers, sections, URLs
- Copy-to-clipboard functionality
- RAG verification badges
- Source-specific icons

#### Citation Parser Utility
**File**: `/home/dev/Development/irStudy/frontend/src/utils/citationParser.ts`

**Capabilities**:
- Parses citation strings into structured data
- Extracts: source, title, page, section, URL
- Supports Australian medical sources
- Returns: `ParsedCitation` interface with `displayText`

#### Study Card Display
**File**: `/home/dev/Development/irStudy/frontend/src/components/study-cards/FlashcardCard.tsx`

**Displays**:
- Question (study_card.question)
- Answer with explanation (study_card.answer)
- Citations (study_card.citations[])
- Topic, subtopic, difficulty, tags
- SM-2 spaced repetition metadata

#### MCQ Content Display
**File**: `/home/dev/Development/irStudy/frontend/src/components/mcq/MCQPracticeInterface.tsx`

**Displays**:
- Question text (question_text)
- 5 MCQ options (A, B, C, D, E)
- Image (image_url) with lightbox (ImageLightbox component)
- Image caption
- Timer and progress
- Answer explanation (after submission)
- Citation (after submission)
- Learning points (after submission)

#### Image Lightbox
**File**: `/home/dev/Development/irStudy/frontend/src/components/common/ImageLightbox.tsx`

**Features**:
- Displays images in modal lightbox
- Zoom capability
- Swipe to close

### Content Types Supported
1. **Plain Text**: Question, Answer, Explanation, Learning points
2. **Structured Data**: Citations, tags, metadata
3. **Images**: MCQ images with captions
4. **Lists**: Learning points (array), tags (array)

### Data Structure for Content
From types files, content includes:

**Study Cards**:
- `question`: string
- `answer`: string (explanation with RAG content)
- `citations`: StudyCardCitation[] (source, page, section, Qdrant ID)
- `tags`: string[]
- `topic`, `subtopic`, `specialty`, `difficulty`

**MCQs**:
- `question_text`: string
- `options`: { A, B, C, D, E?: string }
- `image_url`: string | null
- `image_caption`: string | null
- `explanation`: string (after submission)
- `citation`: string (Australian source)
- `learning_points`: string[] | null

---

## 6. Existing Design Patterns

### Card Component Pattern
```tsx
<Card>
  <CardContent>
    {/* Content */}
  </CardContent>
  <CardActions>
    <Button>Action</Button>
  </CardActions>
</Card>
```

### Grid Layout Pattern
```tsx
<Grid container spacing={3}>
  <Grid item xs={12} md={6}>
    {/* Left column (mobile: full width) */}
  </Grid>
  <Grid item xs={12} md={6}>
    {/* Right column (mobile: full width) */}
  </Grid>
</Grid>
```

### Chip Usage Pattern
- Difficulty chips: `success` (easy), `warning` (medium), `error` (hard)
- Tag chips: Specialty/topic tags
- Metadata chips: Page numbers, sections

### Button Patterns
- Primary action: `variant="contained"` + `color="primary"`
- Secondary action: `variant="outlined"`
- Link-style: `variant="text"`
- Icon buttons: Always tooltips for accessibility

### Form Pattern
- TextField with label
- Select dropdown for filters
- Controlled components (useState for form state)
- Validation on change/submit

### List Pattern
- `List` + `ListItem` + `ListItemText` for structured lists
- Typography for unstructured lists

### Loading Pattern
- `CircularProgress` for loading states
- `Skeleton` for loading skeletons (placeholder animation)
- `Alert` for error messages

---

## 7. Gaps in Current Design System

### Missing Components
1. **Markdown Renderer**: No markdown-to-HTML rendering component
   - Limitation: Content is currently plain text only
   - Need: Support for formatted text (bold, italic, lists, code blocks)

2. **Content Viewer**: No dedicated study notes/document viewer
   - Flashcards show simple text
   - Could benefit from richer formatting

3. **Search/Filter Component**: Basic text search exists
   - No advanced search (boolean operators, exact phrases)
   - No tag-based filtering in some areas

4. **Progress Tracking Component**: Progress bars exist but no detailed breakdown
   - Could add topic-level progress visualization

5. **Sidebar Navigation**: Not visible in explored code
   - Only mobile bottom nav implemented
   - Desktop sidebar likely exists elsewhere

### Missing Documentation
- No centralized UI component library documentation
- No design tokens export
- No accessibility guidelines checklist
- No component usage examples

---

## 8. Information Architecture

### Primary Modules
1. **Dashboard** (Home)
   - Overall progress
   - Module statistics
   - Specialty breakdown
   - Recommendations
   - Recent activity

2. **MCQ Practice**
   - Browse/search MCQs
   - Filter by specialty, difficulty, tags
   - Attempt questions with timer
   - Instant feedback with citations

3. **Study Cards**
   - Spaced repetition review
   - Flash cards (question/answer)
   - Quality ratings (SM-2 algorithm)
   - Citation display

4. **OSCE Practice**
   - OSCE scenarios
   - Mock exam mode
   - Scoring and results
   - Specialties covered

5. **EMR Training**
   - Epic EMR simulation
   - Cerner EMR simulation
   - Patient record navigation
   - Validation scoring

6. **Performance Analytics**
   - Specialty breakdown charts
   - Weekly trends
   - Weak areas identification
   - Exam readiness gauge

---

## 9. Recommendations for Dr. Amir Notes Integration

### Proposed Navigation Location
**Primary Entry Point**: New tab in primary navigation (mobile + desktop)
- Mobile: Add "Notes" to MobileBottomNav (would become 6 items, consider drawer)
- Desktop: Add to sidebar menu
- Breadcrumb: Home > Notes > [Category] > [Note Title]

**Alternative Routes**:
- `/notes` - Notes browser/index
- `/notes/:id` - Individual note viewer
- `/notes?category=cardiology` - Filtered notes

### Proposed Layout Pattern
```
Container (maxWidth="lg")
├── Header: "Study Notes" + Search/Filter
├── Filter Sidebar or Top Bar
│   ├── Category dropdown
│   ├── Specialty filter
│   ├── Search box
│   └── Sort (recent, alphabetical, recommended)
└── Notes Grid or List
    ├── Note Card (preview mode)
    │   ├── Title
    │   ├── Category/Tags
    │   ├── Excerpt (first 2-3 lines)
    │   ├── Author badge (Dr. Amir)
    │   ├── Read time estimate
    │   └── "View Full" button
    └── Detail Page (full content with rich formatting)
        ├── Title + metadata (author, date, category)
        ├── Table of contents (for long notes)
        ├── Rich content (with markdown or HTML)
        ├── Citations/References section
        ├── Related study cards (internal linking)
        └── Navigation (prev/next note)
```

### Content Display Components Needed
1. **Notes Browser Component**
   - Card-based grid layout
   - Search and filter
   - Pagination
   - Favorite/bookmark functionality

2. **Notes Viewer Component**
   - Markdown/Rich text renderer
   - Table of contents (if >3000 words)
   - Citation display (existing CitationPanel can be reused)
   - Related content suggestions
   - Print/export options

3. **Note Card Component**
   - Title, excerpt, metadata
   - Category badge
   - Author badge (Dr. Amir)
   - Interaction: hover preview or tooltip

### Design System Alignment
- **Colors**: Use existing theme (primary for links, secondary for highlights)
- **Typography**: h2 for note titles, body1/body2 for content
- **Spacing**: Use theme.spacing (8px base unit)
- **Cards**: Follow existing Card pattern (12px border-radius)
- **Responsive**: Mobile-first (xs: single column, md+: 2-3 columns)

### Markdown Support
**Recommended Library**: react-markdown (lightweight, no heavy dependencies)

**Features to Support**:
- Headings (h1-h6)
- Bold, italic, strikethrough
- Lists (ordered, unordered, nested)
- Code blocks (with syntax highlighting via `highlight.js` or `prism`)
- Tables (if needed)
- Links (with rel="noopener noreferrer" for security)
- Blockquotes
- Inline code
- Images (with alt text)

**Note**: Material-UI's `Typography` component can be leveraged for semantic HTML.

### Rich Text Editor Integration (If Needed Later)
For Dr. Amir to create/edit notes:
- Recommended: Tiptap Editor (headless, TypeScript-first)
- Alternative: Draft.js (Facebook's editor framework)
- Simple alternative: Markdown editor (textarea + preview)

---

## 10. Summary: Application Structure at a Glance

```
irStudy Frontend
├── Design System (MUI v7 + Custom Theme)
│   ├── Colors: Primary (#1976d2), Secondary (#dc004e), Semantic (success/error/warning/info)
│   ├── Typography: Roboto, responsive sizing, 5 breakpoints
│   └── Spacing: 8px base unit, responsive padding/margin
│
├── Navigation
│   ├── Mobile: Bottom navigation (Home, Practice, Study, Progress)
│   ├── Desktop: Sidebar (presumed, not fully explored)
│   └── Routes: 15+ pages, lazy-loaded for performance
│
├── Core Modules
│   ├── Dashboard: Overview of all modules + recommendations
│   ├── MCQ Practice: Browse, attempt, review with citations
│   ├── Study Cards: Spaced repetition flashcards
│   ├── OSCE Practice: Scenario-based clinical training
│   ├── EMR Training: Epic/Cerner simulations
│   └── Performance: Analytics and exam readiness
│
├── Content Display Patterns
│   ├── Plain Text: Question, answer, explanation
│   ├── Citations: Australian sources (eTG, PBS, AMH, etc.)
│   ├── Images: Lightbox viewer
│   ├── Lists: Tags, learning points
│   └── Metadata: Difficulty, specialty, topic, etc.
│
└── Component Library (MUI-based)
    ├── Cards, Grids, Forms
    ├── Chips, Buttons, Typography
    ├── Dialogs, Modals, Alerts
    ├── Charts/Graphs (recharts, MUI X Charts)
    └── Icons (Material Icons)
```

---

## 11. Next Steps for Dr. Amir Notes Integration

1. **Create Types** (`/frontend/src/types/notes.ts`):
   ```typescript
   interface StudyNote {
     id: string;
     title: string;
     content: string; // Markdown
     category: string;
     tags: string[];
     author: string; // "Dr. Amir"
     created_at: string;
     updated_at: string;
     citations?: CitationSource[];
   }
   ```

2. **Create API Hooks** (`/frontend/src/hooks/useStudyNotes.ts`):
   - Fetch notes list with filters
   - Fetch single note detail
   - Search/filter notes

3. **Create Components**:
   - `NotesCard.tsx` - Card preview component
   - `NotesViewer.tsx` - Full note display with markdown
   - `NotesBrowser.tsx` - Search and filter interface
   - `NotesTable.tsx` - Table of contents for long notes

4. **Install Markdown Renderer**: `react-markdown` (if not already installed)

5. **Update Theme** (if needed): Add note-specific semantic colors

6. **Add Routes**:
   - `/notes` - Notes browser
   - `/notes/:id` - Individual note

7. **Update Navigation**: Add "Notes" to mobile bottom nav and desktop sidebar

8. **Testing**: Unit tests for components, E2E tests for note viewing

---

**Report Generated**: 2026-05-27
**Status**: Comprehensive frontend exploration complete
