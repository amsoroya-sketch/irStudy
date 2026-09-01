# irStudy Frontend: Quick Reference Guide

## Design System at a Glance

### Color Palette
```
Primary:     #1976d2 (Blue) - Main actions, links
Secondary:   #dc004e (Pink) - Highlights, secondary actions
Success:     #4caf50 (Green) - Correct, positive feedback
Error:       #f44336 (Red) - Incorrect, errors, warnings
Warning:     #ff9800 (Orange) - Caution, important notices
Info:        #2196f3 (Light Blue) - Information, hints
Background: #f5f5f5 (Light Gray)
Paper:       #ffffff (White)
```

### Typography
- **Font**: Roboto
- **Headings**: h1 (2.5rem) → h6 (1rem), responsive scaling on mobile
- **Body**: body1 (1rem) → body2 (0.875rem)
- **Responsive**: Uses `responsiveFontSizes()` for automatic scaling

### Spacing
- **Base Unit**: 8px
- **Common**: 8px, 16px, 24px, 32px
- **Border Radius**: 8px (default), 12px (cards)

### Breakpoints
```
xs: 320px   | sm: 768px  | md: 1024px | lg: 1280px | xl: 1920px
Mobile      | Tablet     | Desktop    | Large      | XL Desktop
```

---

## Navigation Routes

### Public
- `/login` - Login page
- `/register` - Register page

### Protected (Authenticated)
| Module | Routes |
|--------|--------|
| **Dashboard** | `/dashboard`, `/performance` |
| **MCQ** | `/mcqs`, `/mcqs/:id/attempt` |
| **Study Cards** | `/study-cards` |
| **OSCE** | `/osce-practice`, `/osce/session/:attemptId`, `/osce/mock-exam/*` |
| **EMR** | `/emr/start`, `/emr/select/:id`, `/emr/epic/:id`, `/emr/cerner/:id` |

### Mobile Navigation (Bottom Bar - <768px)
1. Home → `/dashboard`
2. Practice → `/mcqs`
3. Study → `/study-cards`
4. Progress → `/performance`
5. Profile → `/profile`

---

## Key Components

### Dashboard (`UnifiedDashboardPage.tsx`)
- OverallProgressCard: Top-level metrics
- ModuleStatsGrid: MCQ, OSCE, EMR, Mock Exam stats
- SpecialtyBreakdownChart: Performance by specialty
- RecentActivityFeed: Timeline of activities
- RecommendationsPanel: Personalized recommendations

### MCQ Browser (`MCQBrowser.tsx`)
- Filters: Search, Category, Difficulty, Tags
- Card Grid: Question preview, difficulty, tags, attempt button
- Pagination: Navigate through results

### Study Cards (`FlashcardReview.tsx`)
- Large card display: Question/Answer toggle
- Quality ratings: Again, Hard, Good, Easy (SM-2)
- Citations: Australian source references
- Navigation: Next card button

### MCQ Attempt (`MCQAttempt.tsx`)
- Timer: Countdown for question
- Question + 5 options: Radio buttons for selection
- Instant feedback: Explanation + Citation (after submit)
- Learning points: Key takeaways

---

## Content Display Patterns

### Plain Text
- Question, Answer, Explanation
- Learning Points (array of strings)
- Tags (array of strings)

### Rich Content (Needed for Dr. Amir Notes)
- **Currently Supported**: Plain text, citations, images
- **Missing**: Markdown rendering, code blocks, formatted lists

### Citation Display
- **Component**: CitationPanel.tsx
- **Sources**: eTG, PBS, AMH, AHPRA, RACGP, NSW Health
- **Includes**: Page numbers, sections, URLs, RAG verification badges

### Images
- **Component**: ImageLightbox.tsx
- **Features**: Zoom, swipe-to-close, modal display

---

## Design Patterns (Copy These!)

### Card Pattern
```tsx
<Card>
  <CardContent>
    <Typography variant="h5">{title}</Typography>
    <Typography variant="body2">{content}</Typography>
  </CardContent>
  <CardActions>
    <Button>Action</Button>
  </CardActions>
</Card>
```

### Grid Layout (Mobile-First)
```tsx
<Grid container spacing={3}>
  <Grid item xs={12} md={6}>Left</Grid>
  <Grid item xs={12} md={6}>Right</Grid>
</Grid>
```

### Difficulty Chips
```tsx
<Chip
  label="Easy"
  color="success"  // easy
  // OR color="warning" for medium
  // OR color="error" for hard
/>
```

### Form Input
```tsx
<TextField
  label="Search MCQs"
  value={search}
  onChange={(e) => setSearch(e.target.value)}
  fullWidth
  variant="outlined"
/>
```

### Loading State
```tsx
{isLoading && <CircularProgress />}
{error && <Alert severity="error">{error}</Alert>}
{data && <Box>...</Box>}
```

---

## For Dr. Amir Notes Integration

### Proposed Structure
```
/notes                     - Notes browser (list + filters)
/notes/:id                 - Individual note viewer
```

### Components to Create
1. **NotesCard** - Preview card (title, excerpt, author badge)
2. **NotesViewer** - Full note display (markdown support needed)
3. **NotesBrowser** - Search, filter, pagination
4. **TableOfContents** - Auto-generated from headings

### Required Library
```bash
npm install react-markdown
```

### Data Type
```typescript
interface StudyNote {
  id: string;
  title: string;
  content: string;        // Markdown
  category: string;       // e.g., "Cardiology"
  tags: string[];         // e.g., ["ECG", "Arrhythmia"]
  author: string;         // "Dr. Amir"
  created_at: string;     // ISO 8601
  updated_at: string;     // ISO 8601
  citations?: string[];   // Reference sources
}
```

### Layout Template (Copy This!)
```tsx
<Container maxWidth="lg">
  {/* Header */}
  <Box display="flex" justifyContent="space-between" mb={3}>
    <Typography variant="h4">Study Notes</Typography>
    <TextField placeholder="Search..." />
  </Box>

  {/* Filter Bar */}
  <Stack direction="row" spacing={2} mb={3}>
    <Select label="Category" />
    <Select label="Specialty" />
  </Stack>

  {/* Notes Grid */}
  <Grid container spacing={3}>
    {notes.map((note) => (
      <Grid item xs={12} md={6} lg={4} key={note.id}>
        <NotesCard note={note} />
      </Grid>
    ))}
  </Grid>

  {/* Pagination */}
  <Box display="flex" justifyContent="center" mt={4}>
    <Pagination count={pages} page={page} onChange={handlePageChange} />
  </Box>
</Container>
```

---

## Accessibility Requirements

### WCAG 2.2 AA Compliance
- Minimum touch target: 44px × 44px (mobile)
- Color contrast: ≥4.5:1 for text
- Heading hierarchy: h1 → h6 (no skipping)
- ARIA labels on all interactive elements
- Keyboard navigation support
- Screen reader friendly

### Implemented in irStudy
✓ Responsive design (mobile-first)
✓ Semantic HTML (<main>, <section>, <article>)
✓ ARIA labels on buttons/icons
✓ Touch target sizing (44px minimum)
✓ Color contrast (checked in theme)
✓ Font size: 16px on mobile (prevents iOS zoom)

---

## File Locations (Quick Lookup)

| What | Where |
|------|-------|
| Theme colors, spacing | `/src/theme/theme.ts` |
| Routes | `/src/routes.tsx` |
| Main App | `/src/App.tsx` |
| Mobile nav | `/src/components/layout/MobileBottomNav.tsx` |
| Dashboard | `/src/pages/UnifiedDashboardPage.tsx` |
| MCQ Browser | `/src/pages/MCQBrowser.tsx` |
| MCQ Attempt | `/src/pages/MCQAttempt.tsx` |
| Study Cards | `/src/components/study-cards/FlashcardReview.tsx` |
| Citations | `/src/components/citations/CitationPanel.tsx` |
| Citation parser | `/src/utils/citationParser.ts` |
| Type definitions | `/src/types/` |
| API hooks | `/src/hooks/` |
| Dashboard components | `/src/components/dashboard/` |

---

## Common Tasks

### Add a New Route
1. Create component in `/pages/` or `/components/`
2. Add lazy load in `/routes.tsx`
3. Add route in `/App.tsx` (inside `<Routes>`)
4. Update mobile nav in `/components/layout/MobileBottomNav.tsx` (if applicable)

### Add a New Component
1. Create in `/src/components/` (organize by feature)
2. Use MUI components (Box, Card, Typography, etc.)
3. Follow spacing: `sx={{ mb: 3, mt: 2 }}` (uses 8px base)
4. Add ARIA labels and role attributes
5. Test responsive breakpoints (mobile-first)

### Display Rich Content (Markdown)
1. Install: `npm install react-markdown`
2. Import: `import ReactMarkdown from 'react-markdown'`
3. Use: `<ReactMarkdown>{markdownString}</ReactMarkdown>`
4. Customize rendering with component overrides

### Create a List/Grid
1. Use `Grid container` + `Grid item` (responsive)
2. Or use `List` + `ListItem` + `ListItemText` (semantic)
3. Responsive: `xs={12} md={6} lg={4}` (mobile: full, desktop: split)

---

## Performance Tips

- ✓ Routes are lazy-loaded (code splitting)
- ✓ React Query caching (5 minute default)
- ✓ Responsive images (lightbox component)
- ✓ Minimal re-renders (proper useState structure)

---

**Last Updated**: 2026-05-27
**Location**: `/home/dev/Development/irStudy/backend/FRONTEND_QUICK_REFERENCE.md`
