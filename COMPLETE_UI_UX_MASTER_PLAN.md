# irStudy Platform - Complete UI/UX Master Plan

**Document Version:** 1.0
**Date:** 2026-05-27
**Status:** ✅ COMPREHENSIVE PLANNING COMPLETE
**Scope:** Overall Application Design + Dr. Amir Notes Integration

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Application Overview](#current-application-overview)
3. [Overall Design System](#overall-design-system)
4. [Navigation & Information Architecture](#navigation--information-architecture)
5. [Dr. Amir Study Notes Integration](#dr-amir-study-notes-integration)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Technical Specifications](#technical-specifications)

---

## Executive Summary

### What We Have (Current State)

**irStudy Platform Modules:**
✅ Dashboard - Progress tracking and module overview
✅ MCQ Practice - Multiple choice questions with instant feedback
✅ Study Cards - Spaced repetition flashcards (SM-2 algorithm)
✅ OSCE Practice - Clinical scenario simulations with AI patients
✅ EMR Training - Epic/Cerner electronic medical record practice
✅ Performance Analytics - Exam readiness tracking

**Design System:**
✅ Material-UI v7 with custom theme
✅ Responsive design (mobile-first, 5 breakpoints)
✅ WCAG 2.2 AA accessibility compliance
✅ Australian medical education context

### What's Missing (Gap Analysis)

**Major Gap Identified:**
❌ **No Study Notes Module** - Nowhere to display Dr. Amir's comprehensive study content
❌ **No Markdown Renderer** - Can't display formatted study notes (13,000-word documents)
❌ **No Content Library** - No browsable collection of study materials

**Impact:**
- Dr. Amir OSCE content exists (724-line JSON in database)
- Dr. Amir study enhancement exists (13,000-word markdown file)
- **BUT students can't access the study notes in the UI!**

### What We'll Build (Solution)

**New Module: Study Notes**
📚 Dedicated section for Dr. Amir study content
📖 Markdown rendering with table of contents
🔍 Search and filter by specialty, topic, AMC relevance
📱 Mobile-responsive reading experience
🔗 Linked to related OSCEs and MCQs

**Integration Points:**
- Link from OSCE detail page → Related study notes
- Link from study notes → Practice OSCE
- Link from MCQ results → Relevant study notes
- Dashboard widget → Recently viewed notes

---

## Current Application Overview

### Application Structure (15+ Routes)

```
irStudy Platform
│
├── 🏠 Dashboard (/)
│   ├── Welcome section with user name
│   ├── Overall progress (MCQs attempted, OSCEs completed)
│   ├── Module quick links (6 cards)
│   ├── Specialty breakdown chart
│   └── Recent activity feed
│
├── 📝 MCQ Practice (/mcqs)
│   ├── Browse MCQs (list view with filters)
│   ├── MCQ Detail (/mcqs/:id)
│   ├── MCQ Session (/mcqs/session/:id)
│   └── MCQ Results (/mcqs/results/:id)
│
├── 🃏 Study Cards (/study-cards)
│   ├── Browse decks (by specialty)
│   ├── Card Session (spaced repetition)
│   └── Card Statistics
│
├── 🩺 OSCE Practice (/osces)
│   ├── Browse OSCEs (list/grid view)
│   ├── OSCE Detail (/osces/:id)
│   ├── OSCE Session (/osces/session/:id)
│   └── OSCE Results (/osces/results/:id)
│
├── 🏥 EMR Training (/emr)
│   ├── Epic Simulation
│   ├── Cerner Simulation
│   └── Documentation Practice
│
├── 📊 Analytics (/analytics)
│   ├── Performance Dashboard
│   ├── Specialty Strengths/Weaknesses
│   ├── Exam Readiness Score
│   └── Progress Over Time
│
├── ⚙️ Settings (/settings)
│   ├── Profile
│   ├── Preferences
│   └── Notifications
│
└── 📚 Study Notes (/notes) ← NEW MODULE TO BE BUILT
    ├── Browse Notes (list/grid view)
    ├── Note Detail (/notes/:id)
    └── Search & Filter
```

### Mobile Navigation (Bottom Bar)

```
┌─────────────────────────────────────────────────┐
│                                                 │
│             Main Content Area                   │
│                                                 │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│  🏠      📝      🩺      📚      👤             │
│  Home   MCQ    OSCE   Notes  Profile           │
│                       (NEW)                     │
└─────────────────────────────────────────────────┘
```

**Update Required:** Add "Notes" icon to bottom navigation (currently only 4 items)

### Desktop Navigation (Sidebar)

```
┌────────────┬──────────────────────────────────┐
│            │                                  │
│  📊 Dashboard                                │
│  📝 MCQ Practice                             │
│  🃏 Study Cards                              │
│  🩺 OSCE Practice                            │
│  📚 Study Notes  ← NEW                       │
│  🏥 EMR Training                             │
│  📈 Analytics                                │
│  ⚙️ Settings                                 │
│            │                                  │
└────────────┴──────────────────────────────────┘
```

---

## Overall Design System

### Color Palette (Material-UI Theme)

**Primary Colors:**
```typescript
primary: {
  main: '#1976d2',      // Professional blue
  light: '#42a5f5',
  dark: '#1565c0',
  contrastText: '#fff',
}

secondary: {
  main: '#dc004e',      // Accent pink/red
  light: '#f50057',
  dark: '#c51162',
  contrastText: '#fff',
}
```

**Medical Education Colors (Custom):**
```typescript
amc: {
  highYield: '#FFD700',       // Gold for high-yield topics
  gastric: '#EF5350',         // Red for gastric (Dr. Amir)
  duodenal: '#42A5F5',        // Blue for duodenal (Dr. Amir)
  redFlag: '#D32F2F',         // Dark red for clinical warnings
  teaching: '#FFA726',        // Orange for teaching points
}

specialty: {
  cardiology: '#E91E63',      // Pink
  respiratory: '#2196F3',     // Blue
  gastroenterology: '#FF9800', // Orange
  neurology: '#9C27B0',       // Purple
  psychiatry: '#00BCD4',      // Cyan
  emergency: '#F44336',       // Red
  generalPractice: '#4CAF50', // Green
  pediatrics: '#FFEB3B',      // Yellow
  obstetrics: '#E91E63',      // Pink
  surgery: '#607D8B',         // Blue Grey
}
```

### Typography Scale

```typescript
typography: {
  fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',

  h1: { fontSize: '2.5rem', fontWeight: 700 },   // Page titles
  h2: { fontSize: '2rem', fontWeight: 600 },     // Section headers
  h3: { fontSize: '1.5rem', fontWeight: 600 },   // Subsections
  h4: { fontSize: '1.25rem', fontWeight: 600 },  // Card titles
  h5: { fontSize: '1.1rem', fontWeight: 500 },   // Minor headings
  h6: { fontSize: '1rem', fontWeight: 500 },     // Labels

  body1: { fontSize: '1rem', lineHeight: 1.6 },      // Body text
  body2: { fontSize: '0.875rem', lineHeight: 1.5 },  // Secondary text

  caption: { fontSize: '0.75rem' },              // Small labels

  // Custom variants for medical content
  clinicalNote: {
    fontSize: '0.9rem',
    fontStyle: 'italic',
    color: 'text.secondary'
  },

  teachingPoint: {
    fontSize: '1rem',
    fontWeight: 600,
    color: '#FFA726'  // Orange
  }
}
```

### Spacing System

```typescript
// Material-UI spacing (1 unit = 8px)
spacing: (factor: number) => `${8 * factor}px`

// Common usage:
padding: theme.spacing(2)     // 16px
margin: theme.spacing(3)      // 24px
gap: theme.spacing(1.5)       // 12px

// Standard spacing scale:
xs: 4px   (0.5 units)
sm: 8px   (1 unit)
md: 16px  (2 units)
lg: 24px  (3 units)
xl: 32px  (4 units)
xxl: 48px (6 units)
```

### Responsive Breakpoints

```typescript
breakpoints: {
  xs: 0,      // Mobile portrait (< 600px)
  sm: 600,    // Mobile landscape (≥ 600px)
  md: 960,    // Tablet (≥ 960px)
  lg: 1280,   // Desktop (≥ 1280px)
  xl: 1920,   // Large desktop (≥ 1920px)
}

// Usage example:
<Box
  sx={{
    width: '100%',                    // xs: full width
    [theme.breakpoints.up('sm')]: {
      width: '80%',                   // sm: 80% width
    },
    [theme.breakpoints.up('md')]: {
      width: '60%',                   // md: 60% width
    },
  }}
/>
```

### Component Patterns (Existing)

**Card Pattern (Used Everywhere):**
```tsx
<Card elevation={2}>
  <CardHeader
    title="MCQ: Chest Pain in 45-Year-Old Male"
    subheader="Cardiology • Intermediate"
    avatar={<Avatar>C</Avatar>}
  />
  <CardContent>
    <Typography variant="body2" color="text.secondary">
      A 45-year-old male presents with acute chest pain...
    </Typography>
  </CardContent>
  <CardActions>
    <Button size="small">View Details</Button>
    <Button size="small">Start Practice</Button>
  </CardActions>
</Card>
```

**List Pattern (Browse Views):**
```tsx
<List>
  {items.map((item) => (
    <ListItem key={item.id} button onClick={() => navigate(`/mcqs/${item.id}`)}>
      <ListItemAvatar>
        <Avatar>{item.specialty[0]}</Avatar>
      </ListItemAvatar>
      <ListItemText
        primary={item.title}
        secondary={`${item.specialty} • ${item.difficulty}`}
      />
      <ListItemSecondaryAction>
        <IconButton edge="end">
          <ChevronRightIcon />
        </IconButton>
      </ListItemSecondaryAction>
    </ListItem>
  ))}
</List>
```

**Filter Pattern (Browse Pages):**
```tsx
<Box sx={{ mb: 3 }}>
  <Grid container spacing={2}>
    <Grid item xs={12} md={4}>
      <FormControl fullWidth>
        <InputLabel>Specialty</InputLabel>
        <Select value={specialty} onChange={handleSpecialtyChange}>
          <MenuItem value="all">All Specialties</MenuItem>
          <MenuItem value="cardiology">Cardiology</MenuItem>
          {/* ... more specialties */}
        </Select>
      </FormControl>
    </Grid>
    <Grid item xs={12} md={4}>
      <FormControl fullWidth>
        <InputLabel>Difficulty</InputLabel>
        <Select value={difficulty} onChange={handleDifficultyChange}>
          <MenuItem value="all">All Difficulties</MenuItem>
          <MenuItem value="easy">Easy</MenuItem>
          <MenuItem value="medium">Medium</MenuItem>
          <MenuItem value="hard">Hard</MenuItem>
        </Select>
      </FormControl>
    </Grid>
    <Grid item xs={12} md={4}>
      <TextField
        fullWidth
        placeholder="Search..."
        InputProps={{
          startAdornment: <SearchIcon />
        }}
      />
    </Grid>
  </Grid>
</Box>
```

---

## Navigation & Information Architecture

### User Journey: Dr. Amir Content Discovery

**Journey 1: From Dashboard → Study Notes**
```
1. Student logs in → Dashboard
2. Sees "Study Notes" widget (recent notes, recommended)
3. Clicks "View All Notes" → Notes Browser page
4. Filters by "Gastroenterology" + "High Yield"
5. Sees "Peptic Ulcer Disease - Dr. Amir Enhanced Guide"
6. Clicks card → Opens Note Detail page
7. Reads content with table of contents navigation
8. Clicks "Practice Related OSCE" → Opens GI-PUD-001
```

**Journey 2: From OSCE Practice → Study Notes**
```
1. Student browses OSCEs → Sees GI-PUD-001
2. OSCE detail page shows "📚 Study Notes" section
3. Sees linked note: "Peptic Ulcer Disease - Enhanced Guide"
4. Clicks link → Opens Note Detail page in new tab
5. Studies content, then returns to OSCE
6. Starts OSCE practice with context
```

**Journey 3: From MCQ Results → Study Notes**
```
1. Student completes MCQ on peptic ulcer disease
2. Gets answer wrong
3. MCQ results page shows "📖 Learn More" section
4. Sees linked note: "Peptic Ulcer Disease - Enhanced Guide"
5. Clicks link → Opens Note Detail page
6. Studies the gastric vs duodenal timing distinction
7. Adds note to "Bookmarks" for later review
```

**Journey 4: Mobile Quick Access**
```
1. Student on mobile device
2. Bottom navigation: Home | MCQ | OSCE | Notes | Profile
3. Taps "Notes" → Notes Browser (mobile optimized)
4. Uses search: "NSAID ulcer"
5. Finds relevant note
6. Reads in mobile-optimized format (no sidebar clutter)
7. Swipes to see table of contents
```

### Content Hierarchy: Study Notes

```
Study Notes Module
│
├── Browse Page (/notes)
│   ├── Filter Bar (Specialty, Topic, AMC Relevance, Author)
│   ├── Search Bar (Full-text search)
│   ├── Sort Options (Recent, Popular, Title A-Z)
│   └── Notes Grid/List
│       ├── Note Card (Title, Author, Specialty, Preview, Tags)
│       ├── Note Card
│       └── ...
│
└── Note Detail Page (/notes/:id)
    ├── Header Section
    │   ├── Title (e.g., "Peptic Ulcer Disease - Dr. Amir Enhanced Guide")
    │   ├── Metadata (Author, Specialty, AMC Relevance, Last Updated)
    │   ├── Actions (Bookmark, Share, Print, Download PDF)
    │   └── Tags (peptic_ulcer, NSAID, high_yield, AMC_clinical_exam)
    │
    ├── Table of Contents (Sticky Sidebar on Desktop)
    │   ├── Section 1: Gastric vs Duodenal Distinction
    │   ├── Section 2: NSAID-Induced PUD
    │   ├── Section 3: Australian Medications
    │   ├── Section 4: Red Flag Assessment
    │   └── Section 5: Differential-Driven Approach
    │
    ├── Content Area (Markdown Rendered)
    │   ├── Formatted text with headings
    │   ├── Tables (medication comparison)
    │   ├── Lists (red flags, key points)
    │   ├── Blockquotes (Dr. Amir teaching points)
    │   ├── Code blocks (if needed)
    │   └── Inline citations (links to eTG, PBS)
    │
    └── Related Content Panel
        ├── Related OSCEs (GI-PUD-001, GI-PUD-002)
        ├── Related MCQs (10 questions on PUD)
        └── Related Notes (GORD, Gastritis)
```

---

## Dr. Amir Study Notes Integration

### What Content Exists

**1. AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md**
- 13,000 words
- 5 major sections
- High-yield AMC content
- Dr. Amir teaching methodology

**Structure:**
```markdown
# Peptic Ulcer Disease: Comprehensive Enhancement

## Section 1: Gastric vs Duodenal Distinction
[⭐⭐⭐ HIGH-YIELD FOR AMC]

**Gastric Ulcers:**
- Pain IMMEDIATELY after eating
- CAN progress to malignancy
- Requires endoscopy

**Duodenal Ulcers:**
- Pain 2-3 HOURS after eating
- Does NOT become malignant
- More common (4:1 ratio)

**Clinical Pearl:** "G for Gastric = Goes with food"

## Section 2: NSAID-Induced Peptic Ulcer Disease
[Tables, management algorithms]

## Section 3: Australian OTC Medications
[Medication table with PBS codes]

## Section 4: Red Flag Assessment
[7 red flags with clinical significance]

## Section 5: Dr. Amir's Differential-Driven Approach
[5 Ps framework integration]
```

### Database Schema for Study Notes

**New Table: `study_notes`**

```sql
CREATE TABLE study_notes (
  id SERIAL PRIMARY KEY,
  note_id VARCHAR(50) UNIQUE NOT NULL,  -- e.g., "AMC-GI-PUD-001"

  -- Basic metadata
  title VARCHAR(500) NOT NULL,
  subtitle VARCHAR(500),
  author VARCHAR(255),                   -- e.g., "Dr. Amir Soufi"
  specialty VARCHAR(100),                -- Enum: gastroenterology, cardiology, etc.
  sub_specialty VARCHAR(100),

  -- Content
  content_markdown TEXT NOT NULL,       -- Full markdown content
  word_count INTEGER,
  reading_time_minutes INTEGER,

  -- Classification
  topics JSONB,                         -- ["peptic_ulcer", "NSAID", "gastric_cancer"]
  tags JSONB,                           -- ["high_yield", "AMC_clinical_exam", "dr_amir"]
  amc_relevance VARCHAR(50),            -- high_yield, common, rare
  difficulty VARCHAR(50),               -- easy, intermediate, advanced

  -- Educational metadata
  learning_objectives JSONB,            -- Array of objectives
  key_teaching_points JSONB,            -- Array of teaching points
  clinical_pearls JSONB,                -- Array of pearls

  -- References
  references JSONB,                     -- Array of citation objects
  australian_guidelines JSONB,          -- Array of guideline objects

  -- Related content
  related_osce_ids JSONB,              -- ["GI-PUD-001", "GI-PUD-002"]
  related_mcq_ids JSONB,               -- Array of related MCQ IDs
  related_note_ids JSONB,              -- ["AMC-GI-GORD-001"]

  -- Publishing
  is_published BOOLEAN DEFAULT true,
  version VARCHAR(20),
  last_updated TIMESTAMP,

  -- Statistics
  views_count INTEGER DEFAULT 0,
  bookmarks_count INTEGER DEFAULT 0,

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast filtering
CREATE INDEX idx_study_notes_specialty ON study_notes(specialty);
CREATE INDEX idx_study_notes_amc_relevance ON study_notes(amc_relevance);
CREATE INDEX idx_study_notes_tags ON study_notes USING gin(tags);
CREATE INDEX idx_study_notes_topics ON study_notes USING gin(topics);
```

**Example Row (Peptic Ulcer Disease Note):**

```json
{
  "id": 1,
  "note_id": "AMC-GI-PUD-001",
  "title": "Peptic Ulcer Disease: Comprehensive AMC Preparation Guide",
  "subtitle": "Dr. Amir Enhanced Study Notes - Gastric vs Duodenal Distinctions",
  "author": "Dr. Amir Soufi (Video Transcript) + Clinical Educator Enhancement",
  "specialty": "gastroenterology",
  "sub_specialty": "upper_gastrointestinal",

  "content_markdown": "# Peptic Ulcer Disease: Comprehensive Enhancement\n\n## Section 1: Gastric vs Duodenal Distinction...",
  "word_count": 13000,
  "reading_time_minutes": 45,

  "topics": ["peptic_ulcer_disease", "gastric_ulcer", "duodenal_ulcer", "NSAID_induced", "helicobacter_pylori"],
  "tags": ["high_yield", "AMC_clinical_exam", "dr_amir", "australian_guidelines"],
  "amc_relevance": "high_yield",
  "difficulty": "intermediate",

  "learning_objectives": [
    "Distinguish gastric vs duodenal ulcers by pain timing",
    "Recognize malignancy risk difference",
    "Manage NSAID cessation appropriately"
  ],

  "key_teaching_points": [
    "Gastric: Pain IMMEDIATELY after eating, CAN become malignant",
    "Duodenal: Pain 2-3 HOURS after eating, does NOT become malignant",
    "NSAID cessation is most important management step"
  ],

  "clinical_pearls": [
    "G for Gastric = Goes with food (immediate pain)",
    "Switch Nurofen → Panadol for back pain"
  ],

  "references": [
    {"citation": "eTG: Gastrointestinal v7, 2024", "url": "https://tgldcdp.tg.org.au/"},
    {"citation": "Talley & O'Connor Clinical Examination 9th Ed", "page": "p. 412-428"}
  ],

  "australian_guidelines": [
    {"guideline": "eTG: Peptic Ulcer Disease", "url": "https://tgldcdp.tg.org.au/"},
    {"guideline": "PBS: PPI Authority Code 4497"}
  ],

  "related_osce_ids": ["GI-PUD-001", "GI-PUD-002"],
  "related_mcq_ids": ["MCQ-GI-PUD-001", "MCQ-GI-PUD-002", "MCQ-GI-PUD-003"],
  "related_note_ids": ["AMC-GI-GORD-001", "AMC-GI-GASTRITIS-001"],

  "is_published": true,
  "version": "1.0",
  "last_updated": "2026-05-27T10:00:00Z",

  "views_count": 0,
  "bookmarks_count": 0
}
```

### API Endpoints for Study Notes

```typescript
// Get all study notes with filtering
GET /api/v1/notes
Query params:
  ?specialty=gastroenterology
  &amc_relevance=high_yield
  &difficulty=intermediate
  &search=NSAID
  &page=1
  &limit=20
  &sort=recent|popular|title

Response: {
  notes: StudyNote[],
  total: number,
  page: number,
  pages: number
}

// Get single note with full content
GET /api/v1/notes/{id}
Response: StudyNote (complete with markdown content)

// Get related content
GET /api/v1/notes/{id}/related
Response: {
  osces: OSCE[],
  mcqs: MCQ[],
  notes: StudyNote[]
}

// Track view
POST /api/v1/notes/{id}/view
Response: { views_count: number }

// Bookmark note
POST /api/v1/notes/{id}/bookmark
Response: { bookmarked: boolean }

// Search notes (full-text)
GET /api/v1/notes/search?q=gastric+vs+duodenal
Response: {
  results: StudyNote[],
  total: number,
  query: string
}
```

### Frontend Components for Study Notes

**1. Notes Browser Page** (`/notes`)

```tsx
// File: frontend/src/pages/notes/NotesBrowser.tsx

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Container, Grid, Card, CardHeader, CardContent, CardActions,
  Button, TextField, Select, MenuItem, FormControl, InputLabel,
  Chip, Typography, Box, InputAdornment, Pagination
} from '@mui/material';
import {
  Search as SearchIcon,
  BookmarkBorder as BookmarkIcon,
  Visibility as ViewsIcon,
  AccessTime as TimeIcon
} from '@mui/icons-material';

export default function NotesBrowser() {
  const [filters, setFilters] = useState({
    specialty: 'all',
    amc_relevance: 'all',
    difficulty: 'all',
    search: '',
    page: 1
  });

  const { data, isLoading } = useQuery({
    queryKey: ['notes', filters],
    queryFn: () => fetchNotes(filters)
  });

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          Study Notes
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive AMC preparation guides by Dr. Amir and clinical educators
        </Typography>
      </Box>

      {/* Filters */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search notes..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                )
              }}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>Specialty</InputLabel>
              <Select
                value={filters.specialty}
                onChange={(e) => setFilters({ ...filters, specialty: e.target.value })}
              >
                <MenuItem value="all">All Specialties</MenuItem>
                <MenuItem value="gastroenterology">Gastroenterology</MenuItem>
                <MenuItem value="cardiology">Cardiology</MenuItem>
                <MenuItem value="respiratory">Respiratory</MenuItem>
                {/* More specialties */}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>AMC Relevance</InputLabel>
              <Select
                value={filters.amc_relevance}
                onChange={(e) => setFilters({ ...filters, amc_relevance: e.target.value })}
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="high_yield">High Yield</MenuItem>
                <MenuItem value="common">Common</MenuItem>
                <MenuItem value="rare">Rare</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>Difficulty</InputLabel>
              <Select
                value={filters.difficulty}
                onChange={(e) => setFilters({ ...filters, difficulty: e.target.value })}
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="easy">Easy</MenuItem>
                <MenuItem value="intermediate">Intermediate</MenuItem>
                <MenuItem value="advanced">Advanced</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Button
              fullWidth
              variant="outlined"
              sx={{ height: 56 }}
              onClick={() => setFilters({
                specialty: 'all',
                amc_relevance: 'all',
                difficulty: 'all',
                search: '',
                page: 1
              })}
            >
              Clear Filters
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Results Count */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          {data?.total || 0} notes found
        </Typography>
      </Box>

      {/* Notes Grid */}
      <Grid container spacing={3}>
        {data?.notes.map((note) => (
          <Grid item xs={12} sm={6} md={4} key={note.id}>
            <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardHeader
                title={
                  <Typography variant="h6" sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                  }}>
                    {note.title}
                  </Typography>
                }
                subheader={
                  <Box sx={{ mt: 1 }}>
                    <Chip
                      label={note.specialty}
                      size="small"
                      color="primary"
                      sx={{ mr: 0.5 }}
                    />
                    {note.amc_relevance === 'high_yield' && (
                      <Chip
                        label="⭐ High Yield"
                        size="small"
                        sx={{ bgcolor: '#FFD700', color: '#000' }}
                      />
                    )}
                  </Box>
                }
              />

              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="body2" color="text.secondary" sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  mb: 2
                }}>
                  {note.subtitle}
                </Typography>

                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <TimeIcon fontSize="small" color="action" />
                    <Typography variant="caption" color="text.secondary">
                      {note.reading_time_minutes} min read
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <ViewsIcon fontSize="small" color="action" />
                    <Typography variant="caption" color="text.secondary">
                      {note.views_count} views
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <BookmarkIcon fontSize="small" color="action" />
                    <Typography variant="caption" color="text.secondary">
                      {note.bookmarks_count} saved
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ mt: 2 }}>
                  {note.tags.slice(0, 3).map((tag) => (
                    <Chip
                      key={tag}
                      label={tag}
                      size="small"
                      variant="outlined"
                      sx={{ mr: 0.5, mb: 0.5 }}
                    />
                  ))}
                </Box>
              </CardContent>

              <CardActions>
                <Button
                  size="small"
                  onClick={() => navigate(`/notes/${note.id}`)}
                >
                  Read Note
                </Button>
                <Button
                  size="small"
                  startIcon={<BookmarkIcon />}
                >
                  Save
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Pagination */}
      {data && data.pages > 1 && (
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
          <Pagination
            count={data.pages}
            page={filters.page}
            onChange={(e, page) => setFilters({ ...filters, page })}
            color="primary"
          />
        </Box>
      )}
    </Container>
  );
}
```

**2. Note Detail Page** (`/notes/:id`)

```tsx
// File: frontend/src/pages/notes/NoteDetail.tsx

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Container, Box, Typography, Chip, Button, Divider,
  Card, CardContent, List, ListItem, ListItemButton, ListItemText,
  IconButton, Drawer, useMediaQuery, useTheme, Alert
} from '@mui/material';
import {
  BookmarkBorder as BookmarkIcon,
  Bookmark as BookmarkedIcon,
  Share as ShareIcon,
  Print as PrintIcon,
  Download as DownloadIcon,
  Menu as MenuIcon,
  ChevronRight as ChevronRightIcon
} from '@mui/icons-material';

export default function NoteDetail() {
  const { id } = useParams();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [tocOpen, setTocOpen] = useState(!isMobile);
  const [bookmarked, setBookmarked] = useState(false);
  const [activeSection, setActiveSection] = useState('');

  const { data: note, isLoading } = useQuery({
    queryKey: ['note', id],
    queryFn: () => fetchNote(id)
  });

  const { data: relatedContent } = useQuery({
    queryKey: ['note-related', id],
    queryFn: () => fetchRelatedContent(id)
  });

  // Track view on mount
  useEffect(() => {
    if (note) {
      trackNoteView(id);
    }
  }, [note, id]);

  // Generate table of contents from markdown
  const generateTOC = (markdown: string) => {
    const headingRegex = /^#{1,3}\s+(.+)$/gm;
    const toc: { level: number; text: string; id: string }[] = [];
    let match;

    while ((match = headingRegex.exec(markdown)) !== null) {
      const level = match[0].split(' ')[0].length;
      const text = match[1];
      const id = text.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-');
      toc.push({ level, text, id });
    }

    return toc;
  };

  const toc = note ? generateTOC(note.content_markdown) : [];

  const handleBookmark = async () => {
    await toggleBookmark(id);
    setBookmarked(!bookmarked);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Table of Contents Drawer */}
      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={tocOpen}
        onClose={() => setTocOpen(false)}
        sx={{
          width: 280,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 280,
            boxSizing: 'border-box',
            position: 'sticky',
            top: 64,
            height: 'calc(100vh - 64px)',
            mt: 8,
            pt: 2,
            borderRight: '1px solid',
            borderColor: 'divider'
          }
        }}
      >
        <Box sx={{ px: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Table of Contents
          </Typography>
          <Divider />
        </Box>

        <List sx={{ overflow: 'auto' }}>
          {toc.map((item, index) => (
            <ListItem key={index} disablePadding>
              <ListItemButton
                sx={{
                  pl: 2 + (item.level - 1) * 2,
                  py: 0.5,
                  bgcolor: activeSection === item.id ? 'action.selected' : 'transparent'
                }}
                onClick={() => {
                  document.getElementById(item.id)?.scrollIntoView({ behavior: 'smooth' });
                  setActiveSection(item.id);
                  if (isMobile) setTocOpen(false);
                }}
              >
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    variant: item.level === 1 ? 'body2' : 'caption',
                    sx: { fontWeight: item.level === 1 ? 600 : 400 }
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      {/* Main Content */}
      <Container
        maxWidth="lg"
        sx={{
          py: 4,
          flexGrow: 1,
          ml: isMobile ? 0 : tocOpen ? '280px' : 0,
          transition: 'margin 0.3s'
        }}
      >
        {/* Mobile TOC Toggle */}
        {isMobile && (
          <Button
            startIcon={<MenuIcon />}
            onClick={() => setTocOpen(true)}
            sx={{ mb: 2 }}
          >
            Table of Contents
          </Button>
        )}

        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <Chip
              label={note?.specialty}
              color="primary"
            />
            {note?.amc_relevance === 'high_yield' && (
              <Chip
                label="⭐⭐⭐ HIGH-YIELD AMC TOPIC"
                sx={{ bgcolor: '#FFD700', color: '#000', fontWeight: 600 }}
              />
            )}
            <Chip
              label={note?.difficulty}
              variant="outlined"
            />
          </Box>

          <Typography variant="h3" gutterBottom>
            {note?.title}
          </Typography>

          <Typography variant="h6" color="text.secondary" gutterBottom>
            {note?.subtitle}
          </Typography>

          <Box sx={{ display: 'flex', gap: 2, mt: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <Typography variant="body2" color="text.secondary">
              By {note?.author}
            </Typography>
            <Divider orientation="vertical" flexItem />
            <Typography variant="body2" color="text.secondary">
              {note?.reading_time_minutes} min read
            </Typography>
            <Divider orientation="vertical" flexItem />
            <Typography variant="body2" color="text.secondary">
              {note?.word_count?.toLocaleString()} words
            </Typography>
            <Divider orientation="vertical" flexItem />
            <Typography variant="body2" color="text.secondary">
              {note?.views_count} views
            </Typography>
          </Box>

          {/* Actions */}
          <Box sx={{ mt: 3, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Button
              variant={bookmarked ? 'contained' : 'outlined'}
              startIcon={bookmarked ? <BookmarkedIcon /> : <BookmarkIcon />}
              onClick={handleBookmark}
            >
              {bookmarked ? 'Saved' : 'Save'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<ShareIcon />}
            >
              Share
            </Button>
            <Button
              variant="outlined"
              startIcon={<PrintIcon />}
              onClick={() => window.print()}
            >
              Print
            </Button>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
            >
              Download PDF
            </Button>
          </Box>
        </Box>

        <Divider sx={{ mb: 4 }} />

        {/* Learning Objectives */}
        {note?.learning_objectives && note.learning_objectives.length > 0 && (
          <Alert severity="info" sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              🎯 Learning Objectives
            </Typography>
            <List dense>
              {note.learning_objectives.map((obj, idx) => (
                <ListItem key={idx}>
                  <ListItemText primary={`${idx + 1}. ${obj}`} />
                </ListItem>
              ))}
            </List>
          </Alert>
        )}

        {/* Key Teaching Points */}
        {note?.key_teaching_points && note.key_teaching_points.length > 0 && (
          <Alert severity="warning" sx={{ mb: 4, bgcolor: '#FFF3E0' }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#FFA726' }}>
              ⭐ Dr. Amir's Critical Teaching Points
            </Typography>
            <List dense>
              {note.key_teaching_points.map((point, idx) => (
                <ListItem key={idx}>
                  <ListItemText
                    primary={point}
                    primaryTypographyProps={{ fontWeight: 600 }}
                  />
                </ListItem>
              ))}
            </List>
          </Alert>
        )}

        {/* Markdown Content */}
        <Box
          sx={{
            '& h1, & h2, & h3': { mt: 4, mb: 2 },
            '& h1': { fontSize: '2rem', fontWeight: 700 },
            '& h2': { fontSize: '1.75rem', fontWeight: 600 },
            '& h3': { fontSize: '1.5rem', fontWeight: 600 },
            '& p': { mb: 2, lineHeight: 1.8 },
            '& ul, & ol': { mb: 2, pl: 4 },
            '& li': { mb: 1 },
            '& table': {
              width: '100%',
              borderCollapse: 'collapse',
              mb: 3,
              '& th': {
                bgcolor: 'primary.main',
                color: 'white',
                p: 2,
                textAlign: 'left',
                fontWeight: 600
              },
              '& td': {
                p: 2,
                borderBottom: '1px solid',
                borderColor: 'divider'
              }
            },
            '& blockquote': {
              borderLeft: '4px solid',
              borderColor: 'primary.main',
              bgcolor: 'action.hover',
              p: 2,
              my: 2,
              fontStyle: 'italic'
            },
            '& code': {
              bgcolor: 'action.hover',
              p: 0.5,
              borderRadius: 1,
              fontFamily: 'monospace',
              fontSize: '0.9rem'
            },
            '& pre': {
              bgcolor: 'action.hover',
              p: 2,
              borderRadius: 1,
              overflow: 'auto',
              mb: 2
            }
          }}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {note?.content_markdown || ''}
          </ReactMarkdown>
        </Box>

        {/* Australian Guidelines */}
        {note?.australian_guidelines && note.australian_guidelines.length > 0 && (
          <Card sx={{ mt: 4, bgcolor: 'info.light' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📚 Australian Guidelines & References
              </Typography>
              <List>
                {note.australian_guidelines.map((guideline, idx) => (
                  <ListItem key={idx}>
                    <ListItemText
                      primary={guideline.guideline}
                      secondary={
                        guideline.url && (
                          <a href={guideline.url} target="_blank" rel="noopener noreferrer">
                            {guideline.url}
                          </a>
                        )
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        )}

        {/* Related Content */}
        {relatedContent && (
          <Box sx={{ mt: 6 }}>
            <Typography variant="h5" gutterBottom>
              Related Content
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Grid container spacing={3}>
              {/* Related OSCEs */}
              {relatedContent.osces?.length > 0 && (
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    🩺 Practice OSCEs
                  </Typography>
                  <Grid container spacing={2}>
                    {relatedContent.osces.map((osce) => (
                      <Grid item xs={12} sm={6} md={4} key={osce.id}>
                        <Card>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              {osce.station_title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {osce.specialty} • {osce.difficulty}
                            </Typography>
                          </CardContent>
                          <CardActions>
                            <Button size="small" href={`/osces/${osce.id}`}>
                              View Details
                            </Button>
                          </CardActions>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Grid>
              )}

              {/* Related MCQs */}
              {relatedContent.mcqs?.length > 0 && (
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    📝 Test Your Knowledge ({relatedContent.mcqs.length} MCQs)
                  </Typography>
                  <Button
                    variant="contained"
                    endIcon={<ChevronRightIcon />}
                    href={`/mcqs?topic=${note?.topics[0]}`}
                  >
                    Start MCQ Practice
                  </Button>
                </Grid>
              )}

              {/* Related Notes */}
              {relatedContent.notes?.length > 0 && (
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    📖 Related Study Notes
                  </Typography>
                  <List>
                    {relatedContent.notes.map((relatedNote) => (
                      <ListItem key={relatedNote.id} button>
                        <ListItemText
                          primary={relatedNote.title}
                          secondary={`${relatedNote.specialty} • ${relatedNote.reading_time_minutes} min read`}
                        />
                        <IconButton href={`/notes/${relatedNote.id}`}>
                          <ChevronRightIcon />
                        </IconButton>
                      </ListItem>
                    ))}
                  </List>
                </Grid>
              )}
            </Grid>
          </Box>
        )}
      </Container>
    </Box>
  );
}
```

---

## Implementation Roadmap

### Phase 1: Database & API (Week 1-2)

**Backend Tasks:**

1. **Create `study_notes` table**
   ```sql
   -- Run migration script
   alembic revision -m "Add study_notes table"
   ```

2. **Import Dr. Amir content**
   ```python
   # Script: backend/scripts/import_study_notes.py

   import_study_note(
     note_id="AMC-GI-PUD-001",
     title="Peptic Ulcer Disease: Comprehensive AMC Preparation Guide",
     author="Dr. Amir Soufi (Video) + Clinical Educator",
     specialty="gastroenterology",
     content_markdown_file="AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md",
     related_osce_ids=["GI-PUD-001"],
     tags=["high_yield", "AMC_clinical_exam", "dr_amir"],
     amc_relevance="high_yield"
   )
   ```

3. **Create API endpoints**
   - `GET /api/v1/notes` - List with filtering
   - `GET /api/v1/notes/:id` - Single note detail
   - `GET /api/v1/notes/:id/related` - Related content
   - `POST /api/v1/notes/:id/view` - Track view
   - `POST /api/v1/notes/:id/bookmark` - Bookmark

4. **Test API**
   ```bash
   pytest tests/test_api/test_study_notes.py -v
   ```

**Deliverables:**
✅ Study notes table created
✅ Dr. Amir PUD note imported (AMC-GI-PUD-001)
✅ API endpoints functional and tested
✅ API documentation updated

---

### Phase 2: Frontend Foundation (Week 3-4)

**Frontend Tasks:**

1. **Install dependencies**
   ```bash
   npm install react-markdown remark-gfm
   ```

2. **Create TypeScript types**
   ```typescript
   // frontend/src/types/studyNote.ts
   export interface StudyNote {
     id: number;
     note_id: string;
     title: string;
     subtitle?: string;
     author: string;
     specialty: string;
     content_markdown: string;
     word_count: number;
     reading_time_minutes: number;
     topics: string[];
     tags: string[];
     amc_relevance: 'high_yield' | 'common' | 'rare';
     difficulty: 'easy' | 'intermediate' | 'advanced';
     learning_objectives: string[];
     key_teaching_points: string[];
     clinical_pearls: string[];
     references: Reference[];
     australian_guidelines: AustralianGuideline[];
     related_osce_ids: string[];
     related_mcq_ids: string[];
     related_note_ids: string[];
     views_count: number;
     bookmarks_count: number;
   }
   ```

3. **Create API hooks**
   ```typescript
   // frontend/src/hooks/useStudyNotes.ts
   export function useStudyNotes(filters: NoteFilters) {
     return useQuery({
       queryKey: ['notes', filters],
       queryFn: () => api.getNotes(filters)
     });
   }

   export function useStudyNote(id: string) {
     return useQuery({
       queryKey: ['note', id],
       queryFn: () => api.getNote(id)
     });
   }
   ```

4. **Build Notes Browser page**
   - Grid layout with filtering
   - Search functionality
   - Pagination

5. **Build Note Detail page**
   - Markdown rendering
   - Table of contents (sticky sidebar)
   - Related content display

**Deliverables:**
✅ Notes Browser page functional
✅ Note Detail page with markdown rendering
✅ Mobile responsive design
✅ Search and filter working

---

### Phase 3: Navigation Integration (Week 5)

**Tasks:**

1. **Update navigation**
   - Add "Notes" to sidebar navigation
   - Add "Notes" to mobile bottom navigation
   - Update routing configuration

2. **Add dashboard widget**
   ```tsx
   // Recently Viewed Notes widget on Dashboard
   <Card>
     <CardHeader title="Recently Viewed Notes" />
     <CardContent>
       <List>
         {recentNotes.map(note => (
           <ListItem button href={`/notes/${note.id}`}>
             <ListItemText primary={note.title} />
           </ListItem>
         ))}
       </List>
     </CardContent>
   </Card>
   ```

3. **Link from OSCE detail page**
   ```tsx
   // Add "Related Study Notes" section to OSCE detail
   <Box sx={{ mt: 4 }}>
     <Typography variant="h6">📚 Study Notes</Typography>
     {relatedNotes.map(note => (
       <Card>
         <CardContent>
           <Typography variant="body1">{note.title}</Typography>
           <Button href={`/notes/${note.id}`}>Read Note</Button>
         </CardContent>
       </Card>
     ))}
   </Box>
   ```

4. **Link from MCQ results**
   ```tsx
   // Add "Learn More" section to MCQ results
   {incorrect && (
     <Alert severity="info">
       <Typography>📖 Review these study notes:</Typography>
       <Link href={`/notes/${relatedNoteId}`}>
         {relatedNoteTitle}
       </Link>
     </Alert>
   )}
   ```

**Deliverables:**
✅ Notes accessible from main navigation
✅ Dashboard shows recent notes
✅ OSCEs link to related notes
✅ MCQs link to related notes

---

### Phase 4: Advanced Features (Week 6-7)

**Tasks:**

1. **Bookmarking system**
   - Backend: Store user bookmarks
   - Frontend: Bookmark button, bookmarks page
   - Show "My Bookmarks" in sidebar

2. **Full-text search**
   - Backend: PostgreSQL full-text search
   - Frontend: Advanced search page
   - Highlighting search results

3. **Print/Export PDF**
   - CSS for print styling
   - PDF generation endpoint
   - Download button functional

4. **Progress tracking**
   - Track notes read (completion %)
   - Show progress on dashboard
   - "Continue Reading" feature

5. **Offline support**
   - PWA configuration
   - Cache notes for offline reading
   - Sync when online

**Deliverables:**
✅ Bookmarking functional
✅ Full-text search working
✅ PDF export available
✅ Progress tracking implemented
✅ Offline reading supported

---

### Phase 5: Content Expansion (Week 8+)

**Tasks:**

1. **Import more Dr. Amir content**
   - Convert more video transcripts
   - Create study notes for other specialties
   - Cardiology, Respiratory, Psychiatry, etc.

2. **Create related OSCEs**
   - Build OSCEs linked to each study note
   - Ensure bidirectional linking

3. **Build MCQ integration**
   - Create MCQs based on study content
   - Link MCQs to specific sections of notes

4. **User-generated content (optional)**
   - Allow students to contribute notes
   - Peer review system
   - Community ratings

**Deliverables:**
✅ 10+ study notes across specialties
✅ All notes linked to OSCEs
✅ MCQ integration complete

---

## Technical Specifications

### Dependencies to Add

**Frontend:**
```json
{
  "dependencies": {
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "react-syntax-highlighter": "^15.5.0"
  }
}
```

**Backend:**
```
# requirements.txt additions
markdown==3.5.1
bleach==6.1.0
```

### Database Migration Script

```python
# backend/alembic/versions/XXXXXX_add_study_notes.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

def upgrade():
    op.create_table(
        'study_notes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('note_id', sa.String(50), unique=True, nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('subtitle', sa.String(500)),
        sa.Column('author', sa.String(255)),
        sa.Column('specialty', sa.String(100)),
        sa.Column('sub_specialty', sa.String(100)),
        sa.Column('content_markdown', sa.Text(), nullable=False),
        sa.Column('word_count', sa.Integer()),
        sa.Column('reading_time_minutes', sa.Integer()),
        sa.Column('topics', JSONB),
        sa.Column('tags', JSONB),
        sa.Column('amc_relevance', sa.String(50)),
        sa.Column('difficulty', sa.String(50)),
        sa.Column('learning_objectives', JSONB),
        sa.Column('key_teaching_points', JSONB),
        sa.Column('clinical_pearls', JSONB),
        sa.Column('references', JSONB),
        sa.Column('australian_guidelines', JSONB),
        sa.Column('related_osce_ids', JSONB),
        sa.Column('related_mcq_ids', JSONB),
        sa.Column('related_note_ids', JSONB),
        sa.Column('is_published', sa.Boolean(), default=True),
        sa.Column('version', sa.String(20)),
        sa.Column('last_updated', sa.TIMESTAMP()),
        sa.Column('views_count', sa.Integer(), default=0),
        sa.Column('bookmarks_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.now())
    )

    op.create_index('idx_study_notes_specialty', 'study_notes', ['specialty'])
    op.create_index('idx_study_notes_amc_relevance', 'study_notes', ['amc_relevance'])
    op.create_index('idx_study_notes_tags', 'study_notes', ['tags'], postgresql_using='gin')
    op.create_index('idx_study_notes_topics', 'study_notes', ['topics'], postgresql_using='gin')

def downgrade():
    op.drop_table('study_notes')
```

### Import Script

```python
# backend/scripts/import_study_notes.py

import sys
from pathlib import Path
from sqlalchemy.orm import Session
from src.db.models import StudyNote
from src.db.base import SessionLocal

def import_dr_amir_pud_note():
    """Import Dr. Amir Peptic Ulcer Disease study note"""

    # Read markdown content
    content_path = Path("../AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md")
    with open(content_path, 'r', encoding='utf-8') as f:
        content_markdown = f.read()

    # Calculate word count and reading time
    word_count = len(content_markdown.split())
    reading_time_minutes = max(1, word_count // 200)  # Assume 200 words/min

    # Create study note
    note = StudyNote(
        note_id="AMC-GI-PUD-001",
        title="Peptic Ulcer Disease: Comprehensive AMC Preparation Guide",
        subtitle="Dr. Amir Enhanced Study Notes - Gastric vs Duodenal Distinctions",
        author="Dr. Amir Soufi (Video Transcript) + Clinical Educator Enhancement",
        specialty="gastroenterology",
        sub_specialty="upper_gastrointestinal",

        content_markdown=content_markdown,
        word_count=word_count,
        reading_time_minutes=reading_time_minutes,

        topics=[
            "peptic_ulcer_disease",
            "gastric_ulcer",
            "duodenal_ulcer",
            "NSAID_induced",
            "helicobacter_pylori"
        ],
        tags=[
            "high_yield",
            "AMC_clinical_exam",
            "dr_amir",
            "australian_guidelines"
        ],
        amc_relevance="high_yield",
        difficulty="intermediate",

        learning_objectives=[
            "Distinguish gastric vs duodenal ulcers by pain timing relative to meals",
            "Recognize the malignancy risk difference (gastric CAN, duodenal CANNOT)",
            "Manage NSAID cessation appropriately and recommend safe alternatives",
            "Screen systematically for red flag symptoms requiring urgent investigation",
            "Apply Australian guidelines for H. pylori testing and eradication"
        ],

        key_teaching_points=[
            "CRITICAL TIMING: Gastric pain IMMEDIATELY after eating vs Duodenal pain 2-3 HOURS after eating",
            "MALIGNANCY RISK: Gastric ulcers CAN become malignant (require endoscopy), Duodenal ulcers do NOT",
            "NSAID CESSATION: Most important management step - switch Nurofen → Panadol",
            "H. PYLORI: Test all patients, eradication significantly reduces recurrence",
            "AUSTRALIAN MEDICATIONS: Quickies/Gaviscon (antacids), PBS Authority Code 4497 for PPI maintenance"
        ],

        clinical_pearls=[
            "Dr. Amir's Mnemonic: 'G for Gastric = Goes with food (immediate pain)'",
            "Even short-term NSAID use (2-4 weeks) can cause ulcers",
            "Cease PPI 2 weeks before H. pylori breath test for accuracy",
            "Australian truck drivers at high risk: irregular meals, high stress, frequent NSAID use",
            "PPI dosing: Give 30-60 minutes before breakfast for optimal acid suppression"
        ],

        references=[
            {
                "citation": "Talley NJ, O'Connor S. Clinical Examination: A Systematic Guide to Physical Diagnosis. 9th ed. 2024.",
                "page": "p. 412-428"
            },
            {
                "citation": "Therapeutic Guidelines: Gastrointestinal v7. 2024.",
                "url": "https://tgldcdp.tg.org.au/"
            }
        ],

        australian_guidelines=[
            {
                "guideline": "eTG: Gastrointestinal - Peptic Ulcer Disease",
                "url": "https://tgldcdp.tg.org.au/"
            },
            {
                "guideline": "PBS: PPI Authority Code 4497 for maintenance therapy"
            }
        ],

        related_osce_ids=["GI-PUD-001"],
        related_mcq_ids=[],
        related_note_ids=[],

        is_published=True,
        version="1.0"
    )

    # Add to database
    db = SessionLocal()
    try:
        db.add(note)
        db.commit()
        print(f"✅ Successfully imported study note: {note.note_id}")
        print(f"   Title: {note.title}")
        print(f"   Word count: {note.word_count}")
        print(f"   Reading time: {note.reading_time_minutes} minutes")
    except Exception as e:
        print(f"❌ Error importing study note: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_dr_amir_pud_note()
```

---

## Summary & Next Steps

### What We've Planned

**Overall Application Design:**
✅ Understood 6 existing modules (Dashboard, MCQ, Study Cards, OSCE, EMR, Analytics)
✅ Identified navigation structure (15+ routes, mobile bottom nav, desktop sidebar)
✅ Documented design system (Material-UI theme, colors, typography, spacing)
✅ Analyzed content display patterns

**Dr. Amir Notes Integration:**
✅ Designed new Study Notes module
✅ Created database schema for `study_notes` table
✅ Specified API endpoints
✅ Built component specifications (Notes Browser, Note Detail)
✅ Planned navigation integration
✅ Created 7-week implementation roadmap

**Key Innovation:**
- Dr. Amir's 13,000-word study content will be accessible in a beautiful, searchable, linkable format
- Students can seamlessly move between Study Notes → OSCE Practice → MCQ Testing
- All content is cross-referenced and connected

### Immediate Next Steps (Week 1)

1. **Backend Team:**
   - Create database migration for `study_notes` table
   - Run migration: `alembic upgrade head`
   - Run import script: `python scripts/import_study_notes.py`
   - Verify in database: `SELECT * FROM study_notes;`

2. **Frontend Team:**
   - Install dependencies: `npm install react-markdown remark-gfm`
   - Create TypeScript types for StudyNote
   - Set up routing for `/notes` and `/notes/:id`
   - Begin building Notes Browser page

3. **Design Team:**
   - Review component specifications
   - Create high-fidelity mockups
   - Test markdown rendering styles
   - Validate mobile layouts

### Documentation Locations

All files in `/home/dev/Development/irStudy/`:

**This Master Plan:**
- `COMPLETE_UI_UX_MASTER_PLAN.md` (this file)

**Overall App Design:**
- `FRONTEND_EXPLORATION_INDEX.md`
- `FRONTEND_UI_UX_EXPLORATION.md`
- `FRONTEND_QUICK_REFERENCE.md`
- `FRONTEND_FILE_STRUCTURE.md`

**Dr. Amir OSCE Specific:**
- `DR_AMIR_OSCE_UI_UX_PLAN.md`
- `DR_AMIR_OSCE_COMPLETE_SYSTEM_SUMMARY.md`

**Content:**
- `AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md`
- `data/osces/gastroenterology_peptic_ulcer_osce.json`

---

**Document Status:** ✅ COMPLETE
**Last Updated:** 2026-05-27
**Version:** 1.0
**Next Review:** After Phase 1 implementation (Week 2)
**Estimated Total Development Time:** 7-8 weeks
