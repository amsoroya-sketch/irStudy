# irStudy Frontend Exploration: Complete Documentation Index

## Overview

This documentation package provides a comprehensive exploration of the irStudy frontend application's UI/UX design, navigation structure, and component architecture. The exploration is designed to support the integration of Dr. Amir study notes into the platform.

**Status**: Complete (May 27, 2026)
**Framework**: React 19 + TypeScript + Material-UI v7 + Vite
**Target Platform**: Mobile-first responsive web application

---

## Documentation Files

### 1. FRONTEND_UI_UX_EXPLORATION.md (17 KB)
**Comprehensive technical exploration of the entire frontend application**

**Covers**:
- Overall application architecture and structure
- Complete design system (colors, typography, spacing, breakpoints)
- Full navigation structure (15+ routes)
- Page layout patterns for all major modules
- Existing content display components and patterns
- Design patterns used across the application
- Gaps in the current design system
- Information architecture overview
- Specific recommendations for Dr. Amir notes integration
- Summary of application structure at a glance

**Best For**: Understanding the big picture, getting familiar with the design philosophy, planning integration approach

**Key Sections**:
- Section 2: Design System (Colors, Typography, Spacing, Breakpoints)
- Section 3: Navigation Routes (Public/Protected, Mobile Navigation)
- Section 4: Page Layout Patterns (Dashboard, MCQ, Study Cards)
- Section 5: Content Display Components (Citations, Study Cards, MCQs, Images)
- Section 9: Recommendations for Dr. Amir Notes Integration
- Section 11: Next Steps for Implementation

---

### 2. FRONTEND_QUICK_REFERENCE.md (8.1 KB)
**Quick lookup guide with code snippets and design patterns**

**Covers**:
- Design system at a glance (colors, typography, spacing, breakpoints)
- Navigation routes quick lookup table
- Key components overview
- Content display patterns
- Design patterns with code examples (cards, grids, chips, forms, loading states)
- Dr. Amir notes integration proposal
- Accessibility requirements checklist
- File location quick lookup table
- Common tasks and how-tos
- Performance tips

**Best For**: Quick reference while coding, copy-paste code snippets, finding file locations, common tasks

**Key Sections**:
- "Design Patterns (Copy These!)" with code examples
- "Dr. Amir Notes Integration" with data type and layout template
- "File Locations (Quick Lookup)" table
- "Common Tasks" section

---

### 3. FRONTEND_FILE_STRUCTURE.md (17 KB)
**Complete file tree and component dependency mapping**

**Covers**:
- Full directory organization of `/src/`
- 60+ file locations with descriptions
- Component dependency tree (root → all routes)
- Data flow patterns for major user flows
- State management patterns (Context, React Query, useState)
- TypeScript type system overview
- Performance optimizations implemented
- Testing structure and locations
- Build configuration and commands
- Key dependencies with versions
- Next steps for Dr. Amir notes integration (with code)

**Best For**: Understanding file organization, finding specific components, tracing data flow, planning new components

**Key Sections**:
- "Directory Organization" with full tree
- "Component Dependency Map" showing React tree hierarchy
- "Data Flow Patterns" for MCQ, Study Cards, Dashboard
- "State Management Pattern" explanation
- "TypeScript Type System" examples
- "Next Steps for Dr. Amir Notes" with implementation guide

---

## Quick Start: Finding What You Need

### I want to understand the overall UI/UX design
→ Read **FRONTEND_UI_UX_EXPLORATION.md** (Sections 1-6)

### I want to integrate Dr. Amir notes
→ Read **FRONTEND_UI_UX_EXPLORATION.md** (Section 9) + **FRONTEND_QUICK_REFERENCE.md** (Section "Dr. Amir Notes Integration")

### I want to find where a specific component is
→ Use **FRONTEND_FILE_STRUCTURE.md** (Section "Directory Organization" or "Quick Lookup" table)

### I want to understand the design system
→ Read **FRONTEND_QUICK_REFERENCE.md** (Top section: "Design System at a Glance") or **FRONTEND_UI_UX_EXPLORATION.md** (Section 2)

### I need code snippets for common patterns
→ Use **FRONTEND_QUICK_REFERENCE.md** (Section "Design Patterns (Copy These!)")

### I want to understand how data flows in the app
→ Read **FRONTEND_FILE_STRUCTURE.md** (Section "Data Flow Patterns")

### I want to understand navigation routes
→ Use **FRONTEND_QUICK_REFERENCE.md** ("Navigation Routes" table) or **FRONTEND_UI_UX_EXPLORATION.md** (Section 3)

### I want to know what components exist
→ Read **FRONTEND_FILE_STRUCTURE.md** (Section "Component Dependency Map" or "Directory Organization")

---

## Key Findings Summary

### Design System
- **Colors**: Primary (#1976d2 blue), Secondary (#dc004e pink)
- **Typography**: Roboto, responsive scaling, 6 heading levels
- **Spacing**: 8px base unit
- **Breakpoints**: 5 responsive breakpoints (xs/sm/md/lg/xl)
- **Current State**: Comprehensive Material-UI v7 theme with mobile-first design

### Navigation
- **Mobile**: Bottom navigation bar (5 items)
- **Desktop**: Sidebar navigation (not fully explored)
- **Routes**: 15+ pages, all lazy-loaded for performance
- **Architecture**: Client-side routing with React Router

### Content Display
- **Plain text**: Questions, answers, explanations, learning points
- **Rich content**: NOT currently supported (no markdown renderer)
- **Citations**: Australian medical sources (eTG, PBS, AMH, etc.)
- **Images**: Lightbox modal with zoom
- **Lists**: Tags, learning points, recommendations

### Major Modules
1. Dashboard (overall progress)
2. MCQ Practice (browse, attempt, review)
3. Study Cards (spaced repetition flashcards)
4. OSCE Practice (scenario-based training)
5. EMR Training (Epic/Cerner simulations)
6. Performance Analytics (exam readiness tracking)

### Gaps for Dr. Amir Notes
- No markdown renderer (required for rich text)
- No notes viewer component (needs to be created)
- No notes browser/search UI (needs to be created)
- Notes routes not yet defined

---

## Integration Checklist for Dr. Amir Notes

### Phase 1: Foundation
- [ ] Create TypeScript types (`/src/types/notes.ts`)
- [ ] Install markdown renderer: `npm install react-markdown`
- [ ] Create API hooks (`/src/hooks/useStudyNotes.ts`)

### Phase 2: Components
- [ ] Create `NotesBrowser` component (list + filters)
- [ ] Create `NotesViewer` component (full display with markdown)
- [ ] Create `NotesCard` component (preview card)
- [ ] Create `TableOfContents` component (for long notes)

### Phase 3: Integration
- [ ] Add routes in `/src/routes.tsx` (lazy load)
- [ ] Add routes in `/src/App.tsx` (add protected routes)
- [ ] Update mobile nav in `/src/components/layout/MobileBottomNav.tsx`
- [ ] Connect to backend API endpoints

### Phase 4: Testing
- [ ] Unit tests for components
- [ ] Integration tests for user flows
- [ ] E2E tests via Playwright
- [ ] Achieve ≥70% code coverage

### Phase 5: Polish
- [ ] Design system compliance (colors, spacing, typography)
- [ ] Accessibility audit (WCAG 2.2 AA)
- [ ] Mobile responsiveness testing
- [ ] Performance optimization

---

## Design Patterns to Follow

### Card Pattern (Most Common)
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

### Responsive Grid
```tsx
<Grid container spacing={3}>
  <Grid item xs={12} md={6}>{/* Mobile: full, Desktop: half */}</Grid>
  <Grid item xs={12} md={6}>{/* Mobile: full, Desktop: half */}</Grid>
</Grid>
```

### Loading State
```tsx
{isLoading && <CircularProgress />}
{error && <Alert severity="error">{error}</Alert>}
{data && <Box>{/* Content */}</Box>}
```

### Form Input
```tsx
<TextField
  label="Search"
  value={value}
  onChange={(e) => setValue(e.target.value)}
  fullWidth
  variant="outlined"
/>
```

---

## Important Files to Modify for Notes Integration

| File | Purpose | Modification |
|------|---------|--------------|
| `/src/routes.tsx` | Route definitions | Add lazy-loaded Notes routes |
| `/src/App.tsx` | Main app routing | Add `/notes/*` protected routes |
| `/src/components/layout/MobileBottomNav.tsx` | Mobile navigation | Add "Notes" link (becomes 6 items) |
| `/src/theme/theme.ts` | Design system | (No changes needed) |
| `/src/types/` | Type definitions | Add `notes.ts` with StudyNote interface |
| `/src/hooks/` | API hooks | Add `useStudyNotes.ts` |
| `/src/components/` | Components | Add `notes/` directory with 4 components |

---

## Dependencies to Install

```bash
# Required
npm install react-markdown

# Optional (for syntax highlighting in code blocks)
npm install highlight.js
npm install react-syntax-highlighter

# Optional (for table of contents auto-generation)
npm install remark-toc
npm install remark-slug
```

---

## Frontend Technology Stack

**Framework**: React 19.2.0
**Styling**: Material-UI v7.3.7 + Emotion CSS-in-JS
**State Management**: React Context + React Query v5
**Routing**: React Router DOM v7.13.0
**API Client**: Axios v1.13.4
**Charts**: Recharts v2.15.4 + MUI X Charts v7.29.1
**Build Tool**: Vite v7.2.4
**Testing**: Vitest v4.0.18 + Testing Library
**Language**: TypeScript 5.9.3
**Code Quality**: ESLint + Prettier

---

## Performance Notes

- Routes are lazy-loaded (code splitting for ~15 pages)
- React Query caches API responses (5 minutes default)
- Responsive images use lightbox component
- Material-UI is tree-shakable (only used components bundled)
- No heavy dependencies (markdown renderer ~8KB gzipped)

---

## Accessibility Compliance

The irStudy frontend implements WCAG 2.2 AA standards:
- Responsive design (mobile-first, 5 breakpoints)
- Semantic HTML with proper heading hierarchy
- ARIA labels on all interactive elements
- Touch targets ≥44px on mobile
- Color contrast ≥4.5:1 for text
- Keyboard navigation support
- Screen reader friendly

---

## Next Steps

1. **Start here**: Read `FRONTEND_UI_UX_EXPLORATION.md` Section 9 for integration recommendations
2. **Planning**: Review integration checklist above
3. **Development**: Reference `FRONTEND_QUICK_REFERENCE.md` while coding
4. **Implementation**: Follow file structure in `FRONTEND_FILE_STRUCTURE.md` Section "Next Steps"
5. **Testing**: Ensure ≥70% code coverage and WCAG 2.2 AA compliance

---

## Document Statistics

| Document | Lines | Size | Purpose |
|----------|-------|------|---------|
| FRONTEND_UI_UX_EXPLORATION.md | 569 | 17 KB | Complete technical exploration |
| FRONTEND_QUICK_REFERENCE.md | 308 | 8.1 KB | Quick lookup and code snippets |
| FRONTEND_FILE_STRUCTURE.md | 472 | 17 KB | File organization and dependencies |
| **Total** | **1,349** | **42.1 KB** | Complete documentation package |

---

## How to Use These Documents

### For First-Time Readers
1. Start with `FRONTEND_QUICK_REFERENCE.md` (5-10 minutes)
2. Move to `FRONTEND_UI_UX_EXPLORATION.md` (20-30 minutes)
3. Reference `FRONTEND_FILE_STRUCTURE.md` as needed (lookup)

### For Implementation
1. Keep `FRONTEND_QUICK_REFERENCE.md` open (for code snippets)
2. Use `FRONTEND_FILE_STRUCTURE.md` (for file locations)
3. Refer to `FRONTEND_UI_UX_EXPLORATION.md` (for design decisions)

### For Integration Planning
1. Read `FRONTEND_UI_UX_EXPLORATION.md` Section 9
2. Review integration checklist (above)
3. Follow implementation guide in `FRONTEND_FILE_STRUCTURE.md` "Next Steps"

---

## Related Documentation

- **Backend Documentation**: `/home/dev/Development/irStudy/backend/` (API specs, database schema)
- **Project Constraints**: `/home/dev/Development/irStudy/.claude/CLAUDE.md` (cross-system requirements)
- **Frontend README**: `/home/dev/Development/irStudy/frontend/README.md` (dev setup)

---

**Created**: May 27, 2026
**Last Updated**: May 28, 2026
**Location**: `/home/dev/Development/irStudy/backend/FRONTEND_EXPLORATION_INDEX.md`
**Status**: Ready for use
