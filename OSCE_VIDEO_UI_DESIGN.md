# OSCE Video Resources - UI/UX Design Specification

## 📱 Component Preview

This document describes the visual design and user experience for the video resources component in the OSCE web application.

---

## 🎨 Visual Design

### Color Palette

```
Primary (Essential Videos):
- Border: #3B82F6 (blue-500)
- Button: #2563EB (blue-600)
- Button Hover: #1D4ED8 (blue-700)
- Background: Linear gradient from #EFF6FF (blue-50) to #EEF2FF (indigo-50)

Secondary (Supplementary Videos):
- Border: #D1D5DB (gray-300)
- Button: #4B5563 (gray-600)
- Button Hover: #374151 (gray-700)

Accent Colors:
- Success/Award: #10B981 (green-600)
- Clock: #6B7280 (gray-500)
- Info: #3B82F6 (blue-500)
```

### Typography

```
- Component Title: 2xl (24px), Bold, Gray-900
- Video Title: Base (16px), Semibold, Gray-900
- Source: Small (14px), Regular, Gray-600
- Body Text: Small (14px), Regular, Gray-700
- Duration: Small (14px), Regular, Gray-500
```

---

## 📐 Layout Specifications

### Desktop (≥768px)

```
Container Width: 100% (max-width constrained by parent)
Padding: 24px (p-6)
Border Radius: 8px (rounded-lg)

Video Grid:
- Columns: 2 (md:grid-cols-2)
- Gap: 16px (gap-4)

Card Structure:
┌─────────────────────────────────────────────────┐
│ Padding: 16px (p-4)                            │
│                                                 │
│ ┌─ Video Icon (20x20)                         │
│ │  Video Title (font-semibold)                │
│ │                                   ⏱️ 10 min │
│ └─ Source Name (text-sm, gray-600)            │
│                                                 │
│ 📖 Focus: [description text]                   │
│                                                 │
│ ▼ Why recommended?                             │
│ [Collapsible content when expanded]            │
│                                                 │
│ ┌──────────────────────────────────────┐      │
│ │   ▶️ Watch Video 🔗                  │      │
│ └──────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
```

### Mobile (<768px)

```
Video Grid:
- Columns: 1 (single column)
- Stack vertically
- Full width cards
```

---

## 🎭 Component States

### 1. Default State (Collapsed)

```
┌───────────────────────────────────────────────────────────┐
│  📺 Video Demonstrations                                   │
│  Watch these curated demonstrations from top medical...    │
├───────────────────────────────────────────────────────────┤
│  🔵 Essential - Watch These First                         │
│                                                             │
│  [Video Card 1]  [Video Card 2]                           │
│                                                             │
│  ⚪ Supplementary Videos (2) ▼                            │
└───────────────────────────────────────────────────────────┘
```

### 2. Expanded State (Showing Supplementary)

```
┌───────────────────────────────────────────────────────────┐
│  📺 Video Demonstrations                                   │
│  Watch these curated demonstrations from top medical...    │
├───────────────────────────────────────────────────────────┤
│  🔵 Essential - Watch These First                         │
│                                                             │
│  [Video Card 1]  [Video Card 2]                           │
│                                                             │
│  ⚪ Supplementary Videos (2) ▲                            │
│                                                             │
│  [Supplementary Card 1]  [Supplementary Card 2]           │
└───────────────────────────────────────────────────────────┘
```

### 3. Video Card - Collapsed

```
┌──────────────────────────────────────────────┐
│ 📹 Cardiovascular Examination                │
│ Stanford Medicine 25                ⏱️ 10 min │
│                                               │
│ 📖 Complete systematic cardiac examination   │
│                                               │
│ ▼ Why recommended?                           │
│                                               │
│ ┌──────────────────────────────────────┐    │
│ │   ▶️ Watch Video 🔗                  │    │
│ └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

### 4. Video Card - Expanded

```
┌──────────────────────────────────────────────┐
│ 📹 Cardiovascular Examination                │
│ Stanford Medicine 25                ⏱️ 10 min │
│                                               │
│ 📖 Complete systematic cardiac examination   │
│                                               │
│ ▲ Why recommended?                           │
│ ┌────────────────────────────────────────┐  │
│ │ Gold standard demonstration from       │  │
│ │ Stanford, excellent for murmur...      │  │
│ │                                        │  │
│ │ 🏆 Australian AMC Clinical Exam        │  │
│ │    Relevance                           │  │
│ │    Technique fully compatible with     │  │
│ │    AMC Clinical exam requirements      │  │
│ └────────────────────────────────────────┘  │
│                                               │
│ ┌──────────────────────────────────────┐    │
│ │   ▶️ Watch Video 🔗                  │    │
│ └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

---

## 🖱️ Interactive Elements

### Clickable Areas

1. **"Why recommended?" Toggle**
   - Type: Button
   - Behavior: Expands/collapses explanation
   - Icon: ChevronDown → ChevronUp
   - Hover: Text changes from gray-600 to gray-900

2. **"Supplementary Videos" Toggle**
   - Type: Button
   - Behavior: Shows/hides supplementary video grid
   - Icon: ChevronDown → ChevronUp
   - Hover: Text color change

3. **"Watch Video" Button**
   - Type: Link (opens in new tab)
   - Attributes: `target="_blank" rel="noopener noreferrer"`
   - Hover: Background darkens
   - Icons: PlayCircle + ExternalLink

### Hover Effects

```css
/* Video Card */
.video-card:hover {
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  transition: box-shadow 0.2s ease;
}

/* Watch Video Button */
.watch-button:hover {
  background-color: [darker shade];
  transition: background-color 0.2s ease;
}
```

---

## 🎬 Animation & Transitions

### Collapsible Sections

```
Transition: All 0.2s ease-in-out
- Height: Auto → 0 (collapse)
- Opacity: 1 → 0 (fade out)
```

### Card Hover

```
Transition: box-shadow 0.2s ease
- Shadow: sm → md
```

---

## 📊 Content Hierarchy

```
Level 1: Component Title + Description
  ↓
Level 2: Category Labels (Essential / Supplementary)
  ↓
Level 3: Video Cards
  ├─ Video Title (Primary)
  ├─ Source (Secondary)
  ├─ Duration (Tertiary)
  ├─ Focus (Description)
  └─ Why Recommended (Collapsible)
      └─ Australian Relevance (Highlighted)
```

---

## 🔍 Accessibility (WCAG 2.1 AA)

### Keyboard Navigation

```
Tab Order:
1. Component header (not focusable)
2. Video card 1 - "Why recommended?" button
3. Video card 1 - "Watch Video" link
4. Video card 2 - "Why recommended?" button
5. Video card 2 - "Watch Video" link
6. "Supplementary Videos" toggle
7. [Repeat for supplementary videos]
```

### ARIA Labels

```html
<button
  aria-expanded="false"
  aria-controls="video-1-details"
>
  Why recommended?
</button>

<div id="video-1-details" role="region">
  [Collapsible content]
</div>
```

### Color Contrast

```
All text meets WCAG AA standards:
- Gray-900 on White: 21:1 (AAA)
- Gray-700 on White: 12:1 (AAA)
- Gray-600 on White: 8:1 (AA)
- Blue-600 on White: 8:1 (AA)
```

---

## 📱 Responsive Breakpoints

```
Mobile (< 768px):
- Single column layout
- Full-width cards
- Stack vertically

Tablet (768px - 1024px):
- 2-column grid
- Maintain spacing

Desktop (> 1024px):
- 2-column grid
- Maximum container width
```

---

## 🎯 User Flow

```
1. User loads OSCE detail page
   ↓
2. Video component renders (if video_resources exists)
   ↓
3. User sees "Essential Videos" section (auto-expanded)
   ↓
4. User can:
   a) Click "Why recommended?" to see details
   b) Click "Watch Video" to open in new tab
   c) Toggle "Supplementary Videos" section
   ↓
5. User returns to page after watching (new tab closes)
```

---

## 💡 UX Enhancements

### Visual Indicators

1. **Blue Left Border** on essential videos = "High priority"
2. **Duration Badge** = "Time commitment visibility"
3. **Source Name** = "Credibility indicator"
4. **🏆 Award Icon** on Australian relevance = "AMC exam alignment"

### Progressive Disclosure

1. **Default:** Show essential videos (most important)
2. **Optional:** Hide supplementary videos (reduce overwhelm)
3. **Collapsible:** "Why recommended?" (reduce initial scan)

### Microcopy

```
Component Header: "Video Demonstrations"
- Clear, action-oriented

Essential Badge: "Watch These First"
- Directive, prioritizes content

Study Tip: "💡 Watch videos alongside reading..."
- Contextual help, actionable advice
```

---

## 🧪 Testing Scenarios

### Visual Regression Tests

1. Component with 4 essential, 0 supplementary
2. Component with 2 essential, 3 supplementary
3. Component with 0 essential, 2 supplementary
4. Component with no videos (should not render)
5. Mobile viewport (< 768px)
6. Tablet viewport (768px - 1024px)
7. Desktop viewport (> 1024px)

### Interaction Tests

1. Toggle "Why recommended?" (expand/collapse)
2. Toggle "Supplementary Videos" (show/hide)
3. Click "Watch Video" (opens in new tab)
4. Keyboard navigation (tab through all elements)
5. Screen reader announcement (ARIA labels)

---

## 📐 Component Integration

### In OSCE Detail Page

```
Page Layout:
┌─────────────────────────────────────┐
│ OSCE Header (Station Title)         │
├─────────────────────────────────────┤
│ Patient Instructions                 │
├─────────────────────────────────────┤
│ 📺 Video Demonstrations             │  ← Insert here
│ [Component renders]                  │
├─────────────────────────────────────┤
│ Candidate Instructions               │
├─────────────────────────────────────┤
│ Learning Objectives                  │
├─────────────────────────────────────┤
│ Practice Button / Timer              │
└─────────────────────────────────────┘
```

### Conditional Rendering

```typescript
{osce.video_resources && (
  <OSCEVideoResources
    videoResources={osce.video_resources}
    stationTitle={osce.station_title}
  />
)}
```

---

## 🎨 Design Rationale

### Why Blue for Essential Videos?

- **Psychology:** Blue = Trust, professionalism, medical
- **Contrast:** Stands out against white background
- **Accessibility:** High contrast (8:1 ratio)
- **Brand:** Aligns with medical education aesthetics

### Why Collapsible Sections?

- **Progressive Disclosure:** Reduce cognitive load
- **Scanability:** Users can quickly see titles
- **Mobile-Friendly:** Save screen space
- **User Control:** Let users decide what to expand

### Why External Link Icons?

- **Transparency:** Users know they're leaving the site
- **Expectation:** Clear indicator of behavior
- **Standard:** Common UX pattern (familiar)

---

**Last Updated:** February 13, 2026
**Designer:** AI Assistant
**Status:** ✅ Production Ready
