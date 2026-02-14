# irStudy Medical Education Platform
## Comprehensive UI Design System & Templates

**Version:** 1.0  
**Date:** 2026-02-06  
**Platforms:** Web, Mobile (iOS/Android), Tablet, Desktop  

---

## 📐 PART 1: DESIGN SYSTEM FOUNDATION

### 1.1 Design Philosophy

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DESIGN PRINCIPLES                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1. CLINICAL PRECISION                                                          │
│     • Clean, organized layouts that mirror medical professionalism              │
│     • Clear hierarchy reducing cognitive load during study sessions             │
│     • Trustworthy visual language (authoritative but approachable)              │
│                                                                                 │
│  2. FOCUSED LEARNING                                                            │
│     • Minimize distractions (no unnecessary animations/ads)                     │
│     • Content-first design with generous whitespace                             │
│     • Progressive disclosure (show details on demand)                           │
│                                                                                 │
│  3. ACCESSIBLE & INCLUSIVE                                                      │
│     • WCAG 2.1 AA compliance minimum                                            │
│     • Support for color blindness, screen readers, keyboard navigation          │
│     • Responsive across all device sizes                                        │
│                                                                                 │
│  4. EFFICIENT INTERACTION                                                       │
│     • Reduce clicks to common actions                                           │
│     • Keyboard shortcuts for power users                                        │
│     • Consistent patterns across all modules                                    │
│                                                                                 │
│  5. MOTIVATING PROGRESS                                                         │
│     • Celebratory micro-interactions for achievements                           │
│     • Clear progress visualization                                              │
│     • Gamification elements that enhance (not distract from) learning           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Color System

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         COLOR PALETTE                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  PRIMARY COLORS (Medical Trust)                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Primary Blue        Primary Dark       Primary Light                   │   │
│  │  ██████ #2563EB      ██████ #1D4ED8     ██████ #DBEAFE                  │   │
│  │  Usage: CTAs, Links  Usage: Hover       Usage: Backgrounds              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  SECONDARY COLORS (Medical Context)                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Teal                Emerald            Indigo                          │   │
│  │  ██████ #14B8A6      ██████ #10B981     ██████ #6366F1                  │   │
│  │  Usage: Success      Usage: Correct     Usage: Premium                  │   │
│  │                                                                         │   │
│  │  Amber               Rose               Violet                          │   │
│  │  ██████ #F59E0B      ██████ #F43F5E     ██████ #8B5CF6                  │   │
│  │  Usage: Warning      Usage: Error       Usage: Ultimate                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  NEUTRAL COLORS (Interface Foundation)                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Gray 900    Gray 700    Gray 500    Gray 300    Gray 100    White      │   │
│  │  ████ #111827 ████ #374151 ████ #6B7280 ████ #D1D5DB ████ #F3F4F6 ████  │   │
│  │  Text/Headings Body Text Borders Backgrounds Page Bg Cards              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  SEMANTIC COLORS (Status & Feedback)                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Status          Background    Foreground    Border                      │   │
│  │  ──────────────────────────────────────────────────────────              │   │
│  │  Success         #DCFCE7       #166534       #86EFAC                     │   │
│  │  Error           #FEE2E2       #991B1B       #FCA5A5                     │   │
│  │  Warning         #FEF3C7       #92400E       #FCD34D                     │   │
│  │  Info            #DBEAFE       #1E40AF       #93C5FD                     │   │
│  │  Correct Answer  #D1FAE5       #065F46       #34D399                     │   │
│  │  Wrong Answer    #FEE2E2       #991B1B       #FCA5A5                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  THEME-SPECIFIC COLORS                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  EMR Cerner Theme        EMR Epic Theme                                 │   │
│  │  ─────────────────────────────────────────                              │   │
│  │  Background: #1E293B     Background: #F8FAFC                           │   │
│  │  Primary: #3B82F6        Primary: #8B5CF6                               │   │
│  │  Secondary: #10B981      Secondary: #EC4899                             │   │
│  │  Text: #F1F5F9           Text: #1E293B                                  │   │
│  │  Border: #334155         Border: #E2E8F0                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  DARK MODE COLORS                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Background: #0F172A         Background Elevated: #1E293B               │   │
│  │  Text Primary: #F8FAFC       Text Secondary: #94A3B8                    │   │
│  │  Border: #334155             Overlay: rgba(0,0,0,0.7)                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Typography System

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         TYPOGRAPHY SCALE                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  FONT FAMILY: Inter (Primary), JetBrains Mono (Code/Monospace)                  │
│  Fallback: system-ui, -apple-system, sans-serif                                 │
│                                                                                 │
│  TYPE SCALE (Desktop - Base 16px):                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Style         Size      Weight    Line Height    Letter Spacing        │   │
│  │  ─────────────────────────────────────────────────────────────────     │   │
│  │  H1 (Hero)     48px      700       1.1          -0.02em                 │   │
│  │  H2            36px      700       1.2          -0.01em                 │   │
│  │  H3            30px      600       1.3          0                       │   │
│  │  H4            24px      600       1.4          0                       │   │
│  │  H5            20px      600       1.4          0                       │   │
│  │  H6            18px      600       1.4          0                       │   │
│  │  Body Large    18px      400       1.6          0                       │   │
│  │  Body          16px      400       1.6          0                       │   │
│  │  Body Small    14px      400       1.5          0                       │   │
│  │  Caption       12px      500       1.4          0.01em                  │   │
│  │  Overline      12px      600       1.4          0.05em (uppercase)      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  RESPONSIVE TYPE SCALE:                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Style         Desktop    Tablet      Mobile                            │   │
│  │  ──────────────────────────────────────────────────────────             │   │
│  │  H1 (Hero)     48px       40px        32px                              │   │
│  │  H2            36px       32px        28px                              │   │
│  │  H3            30px       26px        24px                              │   │
│  │  H4            24px       22px        20px                              │   │
│  │  Body          16px       16px        16px (minimum)                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  TYPOGRAPHY PATTERNS:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Element               Style              Example                         │   │
│  │  ─────────────────────────────────────────────────────────────────     │   │
│  │  Page Title            H2, Gray 900       "Cardiology Study"            │   │
│  │  Section Title         H4, Primary        "Arrhythmias"                 │   │
│  │  Card Title            H6, Gray 900       "Atrial Fibrillation"         │   │
│  │  Question Text         Body Large,        "A 65-year-old man..."        │   │
│  │                        Gray 900                                         │   │
│  │  Answer Option         Body, Gray 700     "A. Immediate cardioversion"  │   │
│  │  Explanation           Body, Gray 700     "The correct answer is..."    │   │
│  │  Label/Caption         Caption, Gray 500  "Question 5 of 20"            │   │
│  │  Button Text           Body Small,        "Submit Answer"               │   │
│  │                        weight 600                                       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 Spacing System

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SPACING SCALE                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  BASE UNIT: 4px                                                                 │
│                                                                                 │
│  SCALE:                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Token      Value    Usage                                              │   │
│  │  ─────────────────────────────────────────────────────────────────────  │   │
│  │  space-0    0px      No space                                           │   │
│  │  space-1    4px      Tightest (icon padding)                            │   │
│  │  space-2    8px      Tight (inline elements)                            │   │
│  │  space-3    12px     Compact (form labels)                              │   │
│  │  space-4    16px     Default (component padding)                        │   │
│  │  space-5    20px     Relaxed (card padding)                             │   │
│  │  space-6    24px     Comfortable (section gaps)                         │   │
│  │  space-8    32px     Large (page sections)                              │   │
│  │  space-10   40px     XL (major sections)                                │   │
│  │  space-12   48px     2XL (page padding)                                 │   │
│  │  space-16   64px     3XL (hero sections)                                │   │
│  │  space-20   80px     4XL (major page divisions)                         │   │
│  │  space-24   96px     5XL (section breaks)                               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  LAYOUT SPACING:                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Context                         Spacing                                │   │
│  │  ─────────────────────────────────────────────────────────────────     │   │
│  │  Page padding (desktop)          48px (space-12)                        │   │
│  │  Page padding (tablet)           32px (space-8)                         │   │
│  │  Page padding (mobile)           16px (space-4)                         │   │
│  │  Between sections                64px (space-16)                        │   │
│  │  Between cards                   24px (space-6)                         │   │
│  │  Card internal padding           24px (space-6)                         │   │
│  │  Form field gap                  20px (space-5)                         │   │
│  │  Button group gap                12px (space-3)                         │   │
│  │  Icon + text gap                 8px (space-2)                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  GRID SYSTEM:                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Container max-width: 1280px (xl), 1024px (lg), 768px (md)              │   │
│  │  Gutter: 24px (desktop), 16px (mobile)                                  │   │
│  │  Columns: 12 (desktop), 8 (tablet), 4 (mobile)                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.5 Component Library - Core Components

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         COMPONENT LIBRARY                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  =============================================================================  │
│  BUTTONS                                                                        │
│  =============================================================================  │
│                                                                                 │
│  PRIMARY BUTTON                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Default State:              Hover State:              Active State:    │   │
│  │  ┌──────────────┐            ┌──────────────┐          ┌──────────────┐ │   │
│  │  │  Primary     │            │  Primary     │          │  Primary     │ │   │
│  │  │  Action      │            │  Action      │          │  Action      │ │   │
│  │  └──────────────┘            └──────────────┘          └──────────────┘ │   │
│  │  BG: #2563EB                 BG: #1D4ED8               BG: #1E40AF      │   │
│  │  Text: White                 Text: White               Text: White      │   │
│  │  Border: none                Border: none              Border: none     │   │
│  │  Shadow: shadow-md           Shadow: shadow-lg         Shadow: inset    │   │
│  │  Padding: 12px 24px                                                    │   │
│  │  Border Radius: 8px (rounded-lg)                                       │   │
│  │  Font: 14px, weight 600                                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  BUTTON VARIANTS:                                                               │
│  ┌────────────────┬────────────────┬────────────────┬────────────────┐         │
│  │    Primary     │   Secondary    │     Ghost      │     Danger     │         │
│  ├────────────────┼────────────────┼────────────────┼────────────────┤         │
│  │  ████ Primary  │  Secondary     │   Ghost        │    Delete      │         │
│  │  BG: Blue 600  │  BG: White     │   BG: Transp.  │    BG: Red 600 │         │
│  │  Text: White   │  Border: Gray  │   Text: Blue   │    Text: White │         │
│  │                │  Text: Gray    │                │                │         │
│  └────────────────┴────────────────┴────────────────┴────────────────┘         │
│                                                                                 │
│  BUTTON SIZES:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Small:        Medium (Default):       Large:                           │   │
│  │  ┌────┐        ┌────────┐              ┌────────────┐                   │   │
│  │  │Save│        │ Action │              │  Continue  │                   │   │
│  │  └────┘        └────────┘              └────────────┘                   │   │
│  │  Padding:      Padding:                Padding:                         │   │
│  │  8px 16px      12px 24px               16px 32px                        │   │
│  │  Font: 12px    Font: 14px              Font: 16px                       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  BUTTON WITH ICON:                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐ │   │
│  │  │  ⬇️ Download       │  │  Next →            │  │  ← Back            │ │   │
│  │  └────────────────────┘  └────────────────────┘  └────────────────────┘ │   │
│  │  Icon: 16px, left        Icon: 16px, right       Icon: 16px, left       │   │
│  │  Gap: 8px                Gap: 8px                Gap: 8px               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  LOADING STATE:                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ┌────────────────┐                                                     │   │
│  │  │  ⏳ Loading...  │  Spinner: 16px, animated                             │   │
│  │  └────────────────┘  Text: "Loading..." or action verb                    │   │
│  │                      Disabled: true, opacity: 0.7                        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  =============================================================================  │
│  CARDS                                                                          │
│  =============================================================================  │
│                                                                                 │
│  STANDARD CARD                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                                                                 │   │   │
│  │  │  Card Title                                          [Icon]   │   │   │
│  │  │  Card content goes here. This is the body text that             │   │   │
│  │  │  describes the card's purpose and content.                      │   │   │
│  │  │                                                                 │   │   │
│  │  │  ┌──────────────┐ ┌──────────────┐                              │   │   │
│  │  │  │  Action 1    │ │  Action 2    │                              │   │   │
│  │  │  └──────────────┘ └──────────────┘                              │   │   │
│  │  │                                                                 │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                         │   │
│  │  Background: White                                                      │   │
│  │  Border: 1px solid Gray 200 (#E5E7EB)                                   │   │
│  │  Border Radius: 12px (rounded-xl)                                       │   │
│  │  Shadow: shadow-sm (0 1px 2px rgba(0,0,0,0.05))                         │   │
│  │  Padding: 24px (space-6)                                                │   │
│  │  Hover Shadow: shadow-md                                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  CARD VARIANTS:                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  ELEVATED CARD (Featured)        OUTLINED CARD (Selectable)             │   │
│  │  ┌─────────────────────────┐     ┌─────────────────────────┐            │   │
│  │  │                         │     │                         │            │   │
│  │  │  Featured Content       │     │  Selectable Item        │            │   │
│  │  │                         │     │                         │            │   │
│  │  └─────────────────────────┘     └─────────────────────────┘            │   │
│  │  Shadow: shadow-lg               Border: 2px solid (selected: Primary)  │   │
│  │                                                                         │   │
│  │  HOVER CARD (Interactive)      COLLAPSED CARD (Accordion)               │   │
│  │  ┌─────────────────────────┐     ┌─────────────────────────┐            │   │
│  │  │                         │     │  Title              [▼] │            │   │
│  │  │  Interactive Element    │     └─────────────────────────┘            │   │
│  │  │  (hover to expand)      │                                          │   │
│  │  └─────────────────────────┘                                          │   │
│  │  Transform: translateY(-2px) on hover                                 │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  QUESTION CARD (MCQ Specific)                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  QUESTION 5 OF 30                              [Flag] [Bookmark]│   │   │
│  │  │  ─────────────────────────────────────────────────────────────  │   │   │
│  │  │                                                                 │   │   │
│  │  │  A 65-year-old man presents with crushing chest pain...         │   │   │
│  │  │                                                                 │   │   │
│  │  │  What is the most appropriate initial management?               │   │   │
│  │  │                                                                 │   │   │
│  │  │  ○ A. Immediate electrical cardioversion                        │   │   │
│  │  │  ○ B. Rate control with metoprolol                              │   │   │
│  │  │  ○ C. Anticoagulation assessment (CHA2DS2-VASc)                 │   │   │
│  │  │  ○ D. Rhythm control with amiodarone                            │   │   │
│  │  │                                                                 │   │   │
│  │  │  [Show Hint]  [Submit Answer]                                   │   │   │
│  │  │                                                                 │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                         │   │
│  │  Question Text: Body Large, Gray 900                                    │   │
│  │  Options: Body, Gray 700, with radio buttons                            │   │
│  │  Selected Option: Border Primary, BG Blue 50                            │   │
│  │  Correct Answer: Border Green, BG Green 50                              │   │
│  │  Wrong Answer: Border Red, BG Red 50                                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  =============================================================================  │
│  FORM ELEMENTS                                                                  │
│  =============================================================================  │
│                                                                                 │
│  TEXT INPUT                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  Label                                                                  │   │
│  │  ┌────────────────────────────────────────┐                             │   │
│  │  │  Placeholder text...                   │                             │   │
│  │  └────────────────────────────────────────┘                             │   │
│  │  Helper text or error message                                           │   │
│  │                                                                         │   │
│  │  Height: 44px (minimum touch target)                                    │   │
│  │  Padding: 12px 16px                                                     │   │
│  │  Border: 1px solid Gray 300                                             │   │
│  │  Border Radius: 8px                                                     │   │
│  │  Focus: Border Primary, Ring 2px Primary Light                          │   │
│  │  Error: Border Red 500, Text Red 600                                    │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  SELECT DROPDOWN                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ┌────────────────────────────────────────┐                             │   │
│  │  │  Select option...               [▼]    │                             │   │
│  │  └────────────────────────────────────────┘                             │   │
│  │       ↓                                                                 │   │
│  │  ┌────────────────────────────────────────┐                             │   │
│  │  │  ┌──────────────────────────────────┐  │                             │   │
│  │  │  │  ● Option 1                      │  │                             │   │
│  │  │  │  ○ Option 2                      │  │                             │   │
│  │  │  │  ○ Option 3                      │  │                             │   │
│  │  │  └──────────────────────────────────┘  │                             │   │
│  │  └────────────────────────────────────────┘                             │   │
│  │                                                                         │   │
│  │  Dropdown: Max height 240px, scrollable                                 │   │
│  │  Selected: BG Primary Light, Text Primary                               │   │
│  │  Hover: BG Gray 50                                                      │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  CHECKBOX & RADIO                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  Checkbox (Multi-select):          Radio (Single select):               │   │
│  │  ☑️ Option 1                        ● Option 1 (selected)                │   │
│  │  ☐ Option 2                         ○ Option 2                          │   │
│  │  ☑️ Option 3                         ○ Option 3                          │   │
│  │                                                                         │   │
│  │  Size: 20px × 20px                                                      │   │
│  │  Checked: BG Primary, White checkmark/dot                               │   │
│  │  Unchecked: Border Gray 400, BG White                                   │   │
│  │  Gap between options: 12px                                              │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  =============================================================================  │
│  NAVIGATION COMPONENTS                                                          │
│  =============================================================================  │
│                                                                                 │
│  TOP NAVIGATION BAR                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  [LOGO]   🔍 Search...    [Study ▼] [Practice ▼] [Lab ▼]  🔔 👤 │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                         │   │
│  │  Height: 64px                                                           │   │
│  │  Background: White                                                      │   │
│  │  Border Bottom: 1px solid Gray 200                                      │   │
│  │  Logo: Height 32px                                                      │   │
│  │  Search: Width 320px, BG Gray 100, Border radius full                   │   │
│  │  Nav Items: Font 14px, weight 500, gap 8px                              │   │
│  │  Icons: 20px, Color Gray 600                                            │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  LEFT SIDEBAR NAVIGATION                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Width: 280px (expanded), 72px (collapsed)                              │   │
│  │  Background: White                                                      │   │
│  │  Border Right: 1px solid Gray 200                                       │   │
│  │                                                                         │   │
│  │  SECTION HEADER                                                         │   │
│  │  ┌────────────────────────────────────────┐                             │   │
│  │  │  📚 STUDY HUB                          │                             │   │
│  │  └────────────────────────────────────────┘                             │   │
│  │  Font: 12px, uppercase, weight 600, Gray 500                            │   │
│  │  Padding: 16px 20px 8px                                                 │   │
│  │                                                                         │   │
│  │  NAV ITEM                                                               │   │
│  │  ┌────────────────────────────────────────┐                             │   │
│  │  │  📝  MCQs                        [▶]   │                             │   │
│  │  └────────────────────────────────────────┘                             │   │
│  │  Height: 40px                                                           │   │
│  │  Padding: 0 16px                                                        │   │
│  │  Font: 14px, weight 500                                                 │   │
│  │  Icon: 20px, margin-right 12px                                          │   │
│  │  Hover: BG Gray 50                                                      │   │
│  │  Active: BG Primary Light, Text Primary, Left border 3px Primary        │   │
│  │                                                                         │   │
│  │  SUBMENU (Expanded)                                                     │   │
│  │  ┌────────────────────────────────────────┐                             │   │
│  │  │  ┌──────────────────────────────────┐  │                             │   │
│  │  │  │  By Specialty                    │  │                             │   │
│  │  │  │  By System                       │  │                             │   │
│  │  │  │  By Topic                    ✓   │  │ ← Active sub-item         │   │
│  │  │  └──────────────────────────────────┘  │                             │   │
│  │  └────────────────────────────────────────┘                             │   │
│  │  Indent: 32px                                                           │   │
│  │  Font: 14px, weight 400                                                 │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  BOTTOM NAVIGATION (Mobile)                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────────┬─────────┬─────────┬─────────┬─────────┐                   │   │
│  │  │   🏠    │   📚    │   🎯    │   📊    │   👤    │                   │   │
│  │  │  Home   │  Study  │ Practice│ Progress│ Profile │                   │   │
│  │  └─────────┴─────────┴─────────┴─────────┴─────────┘                   │   │
│  │                                                                         │   │
│  │  Height: 64px + safe area inset                                         │   │
│  │  Background: White                                                      │   │
│  │  Border Top: 1px solid Gray 200                                         │   │
│  │  Icons: 24px                                                            │   │
│  │  Labels: 12px                                                           │   │
│  │  Active: Icon Primary, Label Primary                                    │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  =============================================================================  │
│  FEEDBACK COMPONENTS                                                            │
│  =============================================================================  │
│                                                                                 │
│  ALERT / BANNER                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  Success Banner:                                                        │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  ✅  Your answer was correct!  [View Explanation]  [×]          │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │  BG: Green 50, Border: Green 200, Text: Green 800                       │   │
│  │                                                                         │   │
│  │  Error Banner:                                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  ⚠️  Session expired. Please log in again.        [Log In] [×] │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │  BG: Red 50, Border: Red 200, Text: Red 800                             │   │
│  │                                                                         │   │
│  │  Info Banner:                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  ℹ️  New features available! Check out AI Patient Simulator. [→]│   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │  BG: Blue 50, Border: Blue 200, Text: Blue 800                          │   │
│  │                                                                         │   │
│  │  Padding: 12px 16px, Border Radius: 8px, Margin: 16px 0                 │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  TOOLTIP                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    ┌─────────────────────┐                              │   │
│  │  Hover over →     │  Tooltip text here  │                              │   │
│  │  this icon   →   (?) └─────────────────────┘                              │   │
│  │                                                                         │   │
│  │  BG: Gray 900, Text: White, Font: 12px                                  │   │
│  │  Padding: 8px 12px, Border Radius: 6px                                  │   │
│  │  Arrow: 6px triangle pointing to trigger                                │   │
│  │  Animation: Fade in 150ms, slight Y translation                         │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  MODAL / DIALOG                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  ┌───────────────────────────────────────────────────────────────┐     │   │
│  │  │  Modal Title                                      [×]         │     │   │
│  │  │  ─────────────────────────────────────────────────────────    │     │   │
│  │  │                                                               │     │   │
│  │  │  Modal content goes here. Can include forms,                  │     │   │
│  │  │  confirmation messages, or complex interactions.              │     │   │
│  │  │                                                               │     │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                           │     │   │
│  │  │  │   Cancel     │  │   Confirm    │                           │     │   │
│  │  │  └──────────────┘  └──────────────┘                           │     │   │
│  │  │                                                               │     │   │
│  │  └───────────────────────────────────────────────────────────────┘     │   │
│  │                              ↑                                          │   │
│  │  Overlay: rgba(0,0,0,0.5)  ──┘                                          │   │
│  │                                                                         │   │
│  │  Modal: BG White, Border Radius: 12px, Shadow: shadow-2xl               │   │
│  │  Width: 480px (default), 640px (large), Full screen (mobile)            │   │
│  │  Padding: 24px                                                          │   │
│  │  Animation: Scale from 0.95 + fade in 200ms                             │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  PROGRESS INDICATORS                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  Linear Progress Bar:                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  Study Progress (75%)                                           │   │   │
│  │  │  [████████████████████░░░░░░░░░░]                               │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │  Height: 8px, BG: Gray 200, Fill: Primary                             │   │
│  │  Border Radius: full                                                    │   │
│  │                                                                         │   │
│  │  Circular Progress (Score):                                             │   │
│  │       ┌─────────┐                                                       │   │
│  │      /    85%    \     Size: 80px                                      │   │
│  │     │   ██████   │    Stroke: 8px                                      │   │
│  │      \   ██████  /     Color: Green (pass), Amber (border), Red (fail) │   │
│  │       └─────────┘                                                       │   │
│  │                                                                         │   │
│  │  Step Progress:                                                         │   │
│  │  ●──────●──────◌──────◌                                                 │   │
│  │  Step1   Step2   Step3   Step4                                          │   │
│  │  Complete: ● Primary, Active: ● Primary with ring, Future: ◌ Gray      │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
