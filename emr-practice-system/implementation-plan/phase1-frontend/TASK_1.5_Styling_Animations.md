# TASK 1.5: Styling & Animations

**Phase**: Phase 1 - Frontend Completion
**Estimated Hours**: 6 hours
**Dependencies**: TASK 1.1-1.4 complete (all components and hooks), Tailwind CSS, Framer Motion installed
**Agent Type**: `frontend-react-expert`
**Status**: ⏳ Not Started

---

## Overview

Implement comprehensive styling and animation system for the EMR practice system. This task covers creating a dual-theme system (Cerner dark blue + Epic purple), implementing Framer Motion animations for smooth transitions, establishing responsive breakpoints for mobile/tablet/desktop, and ensuring WCAG 2.1 AA accessibility compliance. The goal is pixel-perfect styling that matches real hospital EMR interfaces while maintaining performance and accessibility standards.

---

## Deliverables

### Styling Files to Create

- `/emr-frontend/src/styles/globals.css` (200+ lines)
  - Global styles and CSS resets
  - CSS custom properties (variables) for both themes
  - Typography system definitions
  - Base component styles

- `/emr-frontend/src/styles/themes/cerner.css` (250+ lines)
  - Cerner-specific CSS variables and overrides
  - Dark sidebar styling (#2c3e50)
  - Blue accent colors (#3498db)
  - Module-specific color variables

- `/emr-frontend/src/styles/themes/epic.css` (250+ lines)
  - Epic-specific CSS variables and overrides
  - Purple accent colors (#8b5cf6)
  - Light background (#f5f3ff)
  - Icon bar styling

- `/emr-frontend/src/styles/animations.css` (180+ lines)
  - Reusable animation keyframes
  - Fade, slide, scale animations
  - Transitions for all interactive elements

- `/emr-frontend/src/styles/responsive.css` (150+ lines)
  - Responsive breakpoints (mobile, tablet, desktop)
  - Mobile-first approach
  - Responsive typography scaling

### Animation Components to Create

- `/emr-frontend/src/components/animations/FadeInUp.tsx` (40 lines)
  - Reusable fade + slide up animation wrapper

- `/emr-frontend/src/components/animations/ScaleIn.tsx` (40 lines)
  - Reusable scale animation wrapper

- `/emr-frontend/src/components/animations/SlideInLeft.tsx` (40 lines)
  - Slide from left animation

- `/emr-frontend/src/components/animations/AnimatedCard.tsx` (60 lines)
  - Card component with hover animation

### Configuration Files

- `/emr-frontend/tailwind.config.js` (150+ lines)
  - Tailwind configuration with custom theme
  - Extended colors for Cerner/Epic
  - Custom animation definitions
  - Responsive breakpoints

- `/emr-frontend/src/styles/tailwind-overrides.css` (100+ lines)
  - Tailwind utility overrides
  - Custom utility classes
  - Theme-specific utilities

---

## Detailed Requirements

### Requirement 1: Global Styles & CSS Variables

**File: globals.css (200+ lines)**

```css
/* CSS Custom Properties - Shared */
:root {
  /* Spacing System */
  --spacing-xs: 0.25rem;    /* 4px */
  --spacing-sm: 0.5rem;     /* 8px */
  --spacing-md: 1rem;       /* 16px */
  --spacing-lg: 1.5rem;     /* 24px */
  --spacing-xl: 2rem;       /* 32px */
  --spacing-2xl: 3rem;      /* 48px */

  /* Border Radius */
  --radius-sm: 0.375rem;    /* 6px */
  --radius-md: 0.5rem;      /* 8px */
  --radius-lg: 0.75rem;     /* 12px */
  --radius-full: 9999px;

  /* Font System */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'Roboto Mono', 'Courier New', monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;       /* 12px */
  --text-sm: 0.875rem;      /* 14px */
  --text-base: 1rem;        /* 16px */
  --text-lg: 1.125rem;      /* 18px */
  --text-xl: 1.25rem;       /* 20px */
  --text-2xl: 1.5rem;       /* 24px */
  --text-3xl: 1.875rem;     /* 30px */

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Z-Index Scale */
  --z-dropdown: 1000;
  --z-modal: 2000;
  --z-popover: 3000;
  --z-tooltip: 4000;

  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}

/* Theme Selection */
:root[data-theme="cerner"] {
  @import url('./themes/cerner.css');
}

:root[data-theme="epic"] {
  @import url('./themes/epic.css');
}

/* Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--text-primary);
  background-color: var(--bg-light);
  transition: background-color var(--transition-base), color var(--transition-base);
}

/* Typography */
h1 { font-size: var(--text-3xl); font-weight: 700; line-height: var(--leading-tight); }
h2 { font-size: var(--text-2xl); font-weight: 600; line-height: var(--leading-tight); }
h3 { font-size: var(--text-xl); font-weight: 600; line-height: var(--leading-normal); }
h4 { font-size: var(--text-lg); font-weight: 600; line-height: var(--leading-normal); }
h5 { font-size: var(--text-base); font-weight: 600; line-height: var(--leading-normal); }
h6 { font-size: var(--text-sm); font-weight: 600; line-height: var(--leading-normal); }

p { margin-bottom: var(--spacing-md); }
strong { font-weight: 600; }
em { font-style: italic; }

/* Form Elements */
input, textarea, select, button {
  font-family: inherit;
  font-size: inherit;
}

input, textarea, select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background-color: var(--bg-white);
  color: var(--text-primary);
  transition: border-color var(--transition-base);
}

input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-alpha-10);
}

button {
  cursor: pointer;
  transition: all var(--transition-base);
  border-radius: var(--radius-md);
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-light);
}

::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--border-dark);
}
```

**Features:**
- Complete CSS variable system for theming
- Consistent spacing scale (4px base unit)
- Comprehensive typography hierarchy
- Z-index scale for layering
- Transition and animation timing
- Shadow system for depth
- Base element styling
- Form element styling
- Custom scrollbar styling

**Acceptance Criteria:**
- [ ] All CSS variables defined
- [ ] Base element styles applied globally
- [ ] Typography hierarchy complete
- [ ] No hardcoded colors (use CSS variables)
- [ ] Form elements styled consistently
- [ ] Scrollbars styled (webkit and Firefox)
- [ ] Variables work for both themes

---

### Requirement 2: Cerner Theme (cerner.css)

**File: themes/cerner.css (250+ lines)**

**Color Palette:**
```css
:root[data-theme="cerner"] {
  /* Primary Colors */
  --primary: #3498db;                    /* Blue */
  --primary-hover: #2980b9;
  --primary-active: #21618c;
  --primary-alpha-10: rgba(52, 152, 219, 0.1);
  --primary-alpha-20: rgba(52, 152, 219, 0.2);

  /* Background Colors */
  --bg-dark: #2c3e50;                    /* Sidebar */
  --bg-darker: #1a252f;                  /* Sidebar header */
  --bg-light: #ecf0f1;                   /* Content area */
  --bg-white: #ffffff;                   /* Cards, modals */

  /* Text Colors */
  --text-primary: #2c3e50;
  --text-secondary: #7f8c8d;
  --text-light: #bdc3c7;
  --text-inverse: #ffffff;               /* Text on dark bg */

  /* Semantic Colors */
  --success: #27ae60;
  --warning: #f39c12;
  --error: #e74c3c;
  --info: #3498db;
  --critical: #c0392b;

  /* Module Colors */
  --module-dashboard: #3498db;
  --module-patient: #27ae60;
  --module-soap: #9b59b6;
  --module-meds: #e67e22;
  --module-orders: #e74c3c;
  --module-vitals: #16a085;
  --module-alerts: #f39c12;

  /* Border & Shadow */
  --border: #bdc3c7;
  --border-light: #ecf0f1;
  --border-dark: #95a5a6;
  --shadow-color: rgba(0, 0, 0, 0.1);
}
```

**Sidebar Styling:**
```css
.cerner-sidebar {
  background-color: var(--bg-dark);
  color: var(--text-inverse);
  width: 256px;
  box-shadow: 2px 0 8px var(--shadow-color);
}

.cerner-sidebar-header {
  background-color: var(--bg-darker);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: var(--spacing-md);
}

.cerner-nav-item {
  color: var(--text-light);
  transition: all var(--transition-base);
  padding: var(--spacing-sm) var(--spacing-md);
}

.cerner-nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--text-inverse);
}

.cerner-nav-item.active {
  background-color: rgba(52, 152, 219, 0.2);
  color: var(--primary);
  border-left: 4px solid var(--primary);
}
```

**Component-Specific Styling:**
```css
/* Patient Banner */
.cerner-patient-banner {
  background-color: var(--bg-dark);
  color: var(--text-inverse);
  padding: var(--spacing-md) var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-md);
}

.cerner-patient-info {
  flex: 1;
}

.cerner-patient-name {
  font-size: var(--text-xl);
  font-weight: 700;
  margin-bottom: var(--spacing-xs);
}

.cerner-allergy-alert {
  background-color: #c0392b;
  color: white;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  font-weight: 600;
  display: inline-block;
}

/* Form Elements */
.cerner-input {
  background-color: var(--bg-white);
  border: 1px solid var(--border);
  color: var(--text-primary);
}

.cerner-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-alpha-10);
}

.cerner-button-primary {
  background-color: var(--primary);
  color: white;
  padding: var(--spacing-sm) var(--spacing-lg);
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
}

.cerner-button-primary:hover {
  background-color: var(--primary-hover);
}

.cerner-button-primary:active {
  background-color: var(--primary-active);
}
```

**Acceptance Criteria:**
- [ ] All Cerner colors applied correctly
- [ ] Sidebar dark background (#2c3e50)
- [ ] Blue primary accent (#3498db)
- [ ] Module colors defined
- [ ] Semantic colors (success, warning, error)
- [ ] Text colors contrast ≥4.5:1 (WCAG AA)
- [ ] Hover/active states defined
- [ ] Shadow system applied

---

### Requirement 3: Epic Theme (epic.css)

**File: themes/epic.css (250+ lines)**

**Color Palette:**
```css
:root[data-theme="epic"] {
  /* Primary Colors */
  --primary: #8b5cf6;                    /* Purple */
  --primary-hover: #7c3aed;
  --primary-active: #6d28d9;
  --primary-alpha-10: rgba(139, 92, 246, 0.1);
  --primary-alpha-20: rgba(139, 92, 246, 0.2);

  /* Background Colors */
  --bg-dark: #581c87;                    /* Dark purple (icon bar) */
  --bg-darker: #3b0764;
  --bg-light: #f5f3ff;                   /* Light purple (content) */
  --bg-white: #ffffff;

  /* Text Colors */
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-light: #9ca3af;
  --text-inverse: #ffffff;

  /* Semantic Colors */
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;
  --critical: #dc2626;

  /* Icon Bar */
  --icon-bar-bg: #1f2937;
  --icon-inactive: #9ca3af;
  --icon-active: #8b5cf6;

  /* Border & Shadow */
  --border: #d1d5db;
  --border-light: #e5e7eb;
  --border-dark: #bfdbfe;
  --shadow-color: rgba(139, 92, 246, 0.1);
}
```

**Icon Bar Styling:**
```css
.epic-icon-bar {
  width: 72px;
  background-color: var(--icon-bar-bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-md) 0;
  box-shadow: 2px 0 8px var(--shadow-color);
}

.epic-icon-button {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: none;
  border: none;
  cursor: pointer;
  transition: all var(--transition-base);
  color: var(--icon-inactive);
  margin: var(--spacing-xs) 0;
}

.epic-icon-button:hover {
  background-color: rgba(139, 92, 246, 0.1);
  color: var(--icon-active);
}

.epic-icon-button.active {
  background-color: var(--primary-alpha-20);
  color: var(--icon-active);
}
```

**Workspace Panel Styling:**
```css
.epic-workspace {
  display: flex;
  height: calc(100vh - 60px);
  gap: var(--spacing-md);
}

.epic-workspace-left {
  width: 40%;
  min-width: 300px;
  background-color: var(--bg-light);
  padding: var(--spacing-lg);
  overflow-y: auto;
  box-shadow: var(--shadow-sm);
}

.epic-workspace-resize-handle {
  width: 4px;
  background-color: var(--border-light);
  cursor: col-resize;
  transition: background-color var(--transition-base);
}

.epic-workspace-resize-handle:hover {
  background-color: var(--primary);
}

.epic-workspace-right {
  flex: 1;
  min-width: 500px;
  background-color: var(--bg-white);
  padding: var(--spacing-lg);
  overflow-y: auto;
  box-shadow: var(--shadow-sm);
}
```

**Acceptance Criteria:**
- [ ] All Epic colors applied correctly
- [ ] Purple primary accent (#8b5cf6)
- [ ] Light background (#f5f3ff)
- [ ] Icon bar dark background (#1f2937)
- [ ] Text colors contrast ≥4.5:1
- [ ] Hover/active states defined
- [ ] Workspace panel styling complete
- [ ] Shadow system applied

---

### Requirement 4: Animations (animations.css)

**File: animations.css (180+ lines)**

```css
/* Fade Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeOutDown {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(10px);
  }
}

/* Slide Animations */
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Scale Animations */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes scaleOut {
  from {
    opacity: 1;
    transform: scale(1);
  }
  to {
    opacity: 0;
    transform: scale(0.95);
  }
}

/* Pulse Animation */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Bounce Animation */
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

/* Loading Spinner */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Utility Classes */
.animate-fade-in {
  animation: fadeIn var(--transition-base);
}

.animate-fade-in-up {
  animation: fadeInUp var(--transition-base);
}

.animate-slide-in-left {
  animation: slideInLeft var(--transition-slow);
}

.animate-scale-in {
  animation: scaleIn var(--transition-base);
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-spin {
  animation: spin 1s linear infinite;
}
```

**Acceptance Criteria:**
- [ ] All animation keyframes defined
- [ ] Smooth 60fps animations
- [ ] Animations use CSS custom properties for timing
- [ ] Utility classes for common animations
- [ ] No jank or stuttering
- [ ] Respects prefers-reduced-motion
- [ ] Timing aligns with --transition-* variables

---

### Requirement 5: Responsive Design

**File: responsive.css (150+ lines)**

```css
/* Mobile First Breakpoints */
/* Mobile: 320px - 640px */
@media (max-width: 639px) {
  .cerner-sidebar {
    width: 100%;
    height: auto;
    position: relative;
  }

  .sidebar-nav {
    display: flex;
    overflow-x: auto;
    padding: var(--spacing-sm);
  }

  .cerner-nav-item {
    flex-shrink: 0;
    width: 100%;
  }

  .epic-workspace {
    flex-direction: column;
  }

  .epic-workspace-left,
  .epic-workspace-right {
    width: 100%;
    min-width: 0;
  }

  .epic-icon-bar {
    width: 100%;
    height: 72px;
    flex-direction: row;
  }

  /* Typography */
  h1 { font-size: var(--text-2xl); }
  h2 { font-size: var(--text-xl); }
  h3 { font-size: var(--text-lg); }
}

/* Tablet: 640px - 1024px */
@media (min-width: 640px) and (max-width: 1023px) {
  .cerner-sidebar {
    width: 220px;
  }

  .epic-workspace-left {
    width: 35%;
  }

  .epic-workspace-right {
    min-width: 400px;
  }

  /* Adjust spacing */
  .cerner-sidebar-nav {
    padding: var(--spacing-sm) 0;
  }
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
  .cerner-sidebar {
    width: 256px;
  }

  .epic-workspace-left {
    width: 40%;
  }

  .epic-workspace-right {
    min-width: 500px;
  }
}

/* Large Desktop: 1440px+ */
@media (min-width: 1440px) {
  .cerner-sidebar {
    width: 280px;
  }

  /* Increased max-width for content areas */
  .epic-workspace-left {
    max-width: 600px;
  }
}

/* Landscape Mode */
@media (orientation: landscape) and (max-height: 500px) {
  .cerner-sidebar {
    height: 100vh;
    overflow-y: auto;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Dark Mode (Optional) */
@media (prefers-color-scheme: dark) {
  /* Adjust colors for dark mode if needed */
  /* Can keep current theme as "dark mode" default */
}

/* High Contrast Mode */
@media (prefers-contrast: more) {
  .cerner-nav-item {
    border: 1px solid var(--border);
  }

  .epic-icon-button {
    border: 2px solid currentColor;
  }
}

/* Touch Devices */
@media (hover: none) and (pointer: coarse) {
  button, a, input {
    min-height: 44px;  /* Touch target minimum */
    min-width: 44px;
  }

  .tooltip {
    display: none;  /* No hover on touch devices */
  }
}

/* Print Styles */
@media print {
  .cerner-sidebar,
  .epic-icon-bar,
  button {
    display: none;
  }

  body {
    background-color: white;
    color: black;
  }
}
```

**Acceptance Criteria:**
- [ ] Mobile layout responsive (320px+)
- [ ] Tablet layout optimized (640px+)
- [ ] Desktop layout full-featured (1024px+)
- [ ] Touch targets ≥44x44px on mobile
- [ ] No horizontal scrolling on mobile
- [ ] Respects prefers-reduced-motion
- [ ] Respects prefers-color-scheme
- [ ] Respects prefers-contrast
- [ ] Print styles functional

---

### Requirement 6: Tailwind Configuration

**File: tailwind.config.js (150+ lines)**

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cerner Colors
        'cerner-primary': '#3498db',
        'cerner-dark': '#2c3e50',
        'cerner-darker': '#1a252f',
        'cerner-light': '#ecf0f1',
        'cerner-success': '#27ae60',
        'cerner-warning': '#f39c12',
        'cerner-error': '#e74c3c',

        // Epic Colors
        'epic-primary': '#8b5cf6',
        'epic-dark': '#581c87',
        'epic-light': '#f5f3ff',
        'epic-success': '#10b981',
        'epic-warning': '#f59e0b',
        'epic-error': '#ef4444',
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'fade-in-up': 'fadeInUp 0.3s ease-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      spacing: {
        'xs': '0.25rem',
        'sm': '0.5rem',
        'md': '1rem',
        'lg': '1.5rem',
        'xl': '2rem',
        '2xl': '3rem',
      },
      borderRadius: {
        'sm': '0.375rem',
        'md': '0.5rem',
        'lg': '0.75rem',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1)',
      },
    },
  },
  plugins: [],
};
```

**Acceptance Criteria:**
- [ ] All custom colors defined
- [ ] Custom animations included
- [ ] Extended spacing system
- [ ] Custom border radius
- [ ] Shadow system configured
- [ ] Responsive breakpoints set
- [ ] No Tailwind conflicts with custom CSS

---

### Requirement 7: Framer Motion Animation Components

**Components to Create:**

#### FadeInUp.tsx (40 lines)
```typescript
interface FadeInUpProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
}

export const FadeInUp: React.FC<FadeInUpProps> = ({
  children,
  delay = 0,
  duration = 0.3
}) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: 10 }}
    transition={{ delay, duration }}
  >
    {children}
  </motion.div>
);
```

#### ScaleIn.tsx (40 lines)
```typescript
interface ScaleInProps {
  children: React.ReactNode;
  delay?: number;
}

export const ScaleIn: React.FC<ScaleInProps> = ({
  children,
  delay = 0
}) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, duration: 0.2 }}
  >
    {children}
  </motion.div>
);
```

#### AnimatedCard.tsx (60 lines)
```typescript
interface AnimatedCardProps {
  children: React.ReactNode;
  hoverable?: boolean;
  onClick?: () => void;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  hoverable = true,
  onClick
}) => (
  <motion.div
    whileHover={hoverable ? { y: -4, boxShadow: '0 10px 15px rgb(0 0 0 / 0.1)' } : {}}
    whileTap={hoverable ? { scale: 0.98 } : {}}
    onClick={onClick}
    className="rounded-lg bg-white p-4 shadow-md transition-all"
  >
    {children}
  </motion.div>
);
```

**Acceptance Criteria:**
- [ ] All animation components created
- [ ] Framer Motion properly installed
- [ ] Animations smooth (60fps)
- [ ] No jank or stuttering
- [ ] Respects prefers-reduced-motion

---

## Acceptance Criteria (Overall Task)

### Styling Quality
- [ ] No hardcoded colors (all use CSS variables)
- [ ] Consistent spacing scale (4px base)
- [ ] Typography hierarchy complete
- [ ] No inline styles (Tailwind + CSS modules only)
- [ ] DRY principle applied throughout

### Theme System
- [ ] Cerner theme (#2c3e50, #3498db) applied correctly
- [ ] Epic theme (#8b5cf6, #f5f3ff) applied correctly
- [ ] Theme switching works (data-theme attribute)
- [ ] All components adapt to theme

### Animations
- [ ] All animations smooth (60fps)
- [ ] No jank or layout thrashing
- [ ] Framer Motion animations integrated
- [ ] CSS keyframe animations defined
- [ ] Respects prefers-reduced-motion

### Responsive Design
- [ ] Mobile (320px+) - responsive layout
- [ ] Tablet (640px+) - optimized spacing
- [ ] Desktop (1024px+) - full features
- [ ] No horizontal scrolling on mobile
- [ ] Touch targets ≥44x44px

### Accessibility (WCAG 2.1 AA)
- [ ] Text contrast ≥4.5:1 (normal text)
- [ ] Text contrast ≥3:1 (large text)
- [ ] Focus indicators visible
- [ ] Color not only way to convey info
- [ ] Respects prefers-reduced-motion
- [ ] Respects prefers-contrast
- [ ] High contrast mode tested

### Performance
- [ ] No layout shift (CLS < 0.1)
- [ ] Animations don't block user input
- [ ] CSS file size optimized
- [ ] No unused CSS (Tailwind purging)
- [ ] Page renders in <3 seconds

### Testing
- [ ] Visual regression tests (if configured)
- [ ] Responsive design tested on multiple devices
- [ ] Theme switching tested
- [ ] Animations tested in Chrome/Firefox/Safari
- [ ] Accessibility tested with screen reader
- [ ] High contrast mode tested
- [ ] Reduced motion tested

---

## Testing Requirements

### Manual Testing Checklist

- [ ] **Cerner Theme**:
  - [ ] Sidebar displays with dark blue background
  - [ ] Text readable (white on dark)
  - [ ] Active navigation item highlighted
  - [ ] Hover states visible

- [ ] **Epic Theme**:
  - [ ] Icon bar displays with correct colors
  - [ ] Purple accents applied
  - [ ] Light background renders correctly
  - [ ] Icons visible in icon bar

- [ ] **Animations**:
  - [ ] Fade-in animations on page load
  - [ ] Slide animations on navigation
  - [ ] Scale animations on hover
  - [ ] No jank during animations

- [ ] **Responsive**:
  - [ ] Mobile layout: sidebar horizontal or hidden
  - [ ] Tablet layout: optimized spacing
  - [ ] Desktop layout: full features visible
  - [ ] Touch targets large enough on mobile

- [ ] **Accessibility**:
  - [ ] Text contrast sufficient (use aXe DevTools)
  - [ ] Focus indicators visible (Tab key)
  - [ ] Colors not only conveying info (use ColorBlind Chrome extension)
  - [ ] Keyboard navigation works
  - [ ] Screen reader can read content

---

## Reference PRD Sections

- **Styling Specification**: Complete document
  - Location: `/home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md`

- **Color Palettes**: Section 2
  - Cerner: Lines 56-97
  - Epic: Lines 101-133

- **Typography System**: Section 2
  - Lines 136-208

- **Component Styling**: Section 3
  - Cerner: Lines 214-300
  - Epic: Extensive specs

---

## Agent OS Delegation Prompt

```
Agent Task: Implement EMR Styling & Animations

CRITICAL - Read constraints FIRST:
1. Read /home/dev/Development/irStudy/constraints/README.md
2. Read /home/dev/Development/irStudy/CLAUDE.md
3. Search for existing styling patterns in /home/dev/Development/irStudy/frontend/src/styles/
4. Reference PRD: /home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md

CONTEXT:
- Styling system for dual-theme EMR (Cerner + Epic)
- Tailwind CSS + custom CSS + Framer Motion
- Mobile-first responsive design
- WCAG 2.1 AA accessibility compliance
- Zero tolerance for hardcoded colors
- 60fps animations required

DELIVERABLES:
1. globals.css (200+ lines) - CSS variables, base styles
2. cerner.css (250+ lines) - Cerner color palette & styling
3. epic.css (250+ lines) - Epic color palette & styling
4. animations.css (180+ lines) - All animation keyframes
5. responsive.css (150+ lines) - Responsive breakpoints
6. tailwind.config.js (150+ lines) - Tailwind configuration
7. FadeInUp.tsx, ScaleIn.tsx, SlideInLeft.tsx, AnimatedCard.tsx (animation components)

CRITICAL REQUIREMENTS:
1. CSS Variables - MANDATORY:
   - No hardcoded colors anywhere
   - All colors use CSS custom properties
   - Variables defined in globals.css
   - Theme-specific overrides in cerner.css / epic.css
   - Example: --primary, --bg-dark, --text-primary, etc.

2. Cerner Theme (#2c3e50, #3498db):
   - Sidebar: dark background
   - Primary: blue (#3498db)
   - Module colors: distinct colors for each module
   - Text on dark: white/light gray

3. Epic Theme (#8b5cf6, #f5f3ff):
   - Icon bar: dark background
   - Primary: purple (#8b5cf6)
   - Light background: #f5f3ff
   - Modern, clean aesthetic

4. Animations (Framer Motion + CSS):
   - Fade, slide, scale animations
   - Smooth 60fps (no jank)
   - Debounce heavy animations
   - Respect prefers-reduced-motion

5. Responsive Breakpoints:
   - Mobile: 320px - 639px
   - Tablet: 640px - 1023px
   - Desktop: 1024px+
   - Large: 1440px+
   - Mobile-first approach

6. Accessibility (WCAG 2.1 AA):
   - Text contrast ≥4.5:1
   - Focus indicators visible
   - Respects prefers-reduced-motion
   - Respects prefers-contrast
   - Touch targets ≥44x44px

VALIDATION CHECKLIST (self-validate before returning):
- [ ] Read constraints README and CLAUDE.md
- [ ] Searched for existing styling patterns
- [ ] All CSS variable files created
- [ ] No hardcoded colors (grep for #[0-9a-f]{6})
- [ ] Cerner theme colors correct
- [ ] Epic theme colors correct
- [ ] Animations smooth (60fps, no jank)
- [ ] Responsive breakpoints correct
- [ ] Text contrast tested (≥4.5:1 for normal)
- [ ] Focus indicators visible
- [ ] prefers-reduced-motion respected
- [ ] prefers-contrast respected
- [ ] Touch targets ≥44x44px on mobile
- [ ] Tailwind config complete
- [ ] No CSS conflicts
- [ ] No unused CSS
- [ ] Browser compatibility tested (Chrome, Firefox, Safari)
- [ ] Mobile tested on actual device or simulator
- [ ] Tablet tested on actual device or simulator
- [ ] High contrast mode tested
- [ ] Dark mode preference tested
- [ ] Print styles tested

ACCEPTANCE CRITERIA (COMPLETE when all pass):
- [ ] No hardcoded colors (all use CSS variables)
- [ ] Consistent spacing scale (4px base)
- [ ] Typography hierarchy complete
- [ ] Cerner theme working correctly
- [ ] Epic theme working correctly
- [ ] Theme switching functional
- [ ] All animations smooth (60fps)
- [ ] Animations respect prefers-reduced-motion
- [ ] Responsive design works (mobile/tablet/desktop)
- [ ] Touch targets ≥44x44px
- [ ] No horizontal scrolling on mobile
- [ ] Text contrast WCAG AA (≥4.5:1)
- [ ] Focus indicators visible
- [ ] High contrast mode working
- [ ] Print styles functional
- [ ] CSS file size optimized
- [ ] No layout shift (CLS < 0.1)
- [ ] Page renders <3 seconds
- [ ] All browsers supported (Chrome, Firefox, Safari, Edge)
- [ ] No console errors or warnings

Return JSON summary:
{
  "status": "COMPLETE",
  "files_created": [...],
  "themes_implemented": ["cerner", "epic"],
  "animations_count": "X",
  "responsive_breakpoints": 4,
  "accessibility_tests_passed": true,
  "performance_metrics": {
    "css_size_kb": X,
    "animation_fps": 60,
    "cls_score": X
  },
  "notes": "..."
}
```

---

## Implementation Notes

### CSS Variable Naming Convention

```
--[component]-[property]-[state]
--primary          (main brand color)
--primary-hover    (hover state)
--primary-alpha-10 (10% opacity)

--bg-dark          (dark background)
--bg-light         (light background)
--bg-white         (white)

--text-primary     (main text)
--text-secondary   (secondary text)
--text-inverse     (on dark backgrounds)
```

### Theme Switching

```typescript
// In App.tsx or ThemeProvider
useEffect(() => {
  const theme = localStorage.getItem('theme') || 'cerner';
  document.documentElement.setAttribute('data-theme', theme);
}, []);

// In component
<button onClick={() => {
  const newTheme = theme === 'cerner' ? 'epic' : 'cerner';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
}}>
  Switch Theme
</button>
```

### Animation Performance

Use CSS transforms and opacity (GPU-accelerated):
```css
/* Good - GPU accelerated */
transform: translateX(10px);
opacity: 0.5;

/* Bad - CPU intensive */
left: 10px;
color: rgba(0,0,0,0.5); /* position change, not opacity */
```

### Accessibility Testing Tools

- **aXe DevTools**: Chrome extension for contrast checking
- **ColorBlind Simulator**: Chrome extension
- **Screen Reader**: NVDA (Windows) or VoiceOver (Mac)
- **Keyboard Navigation**: Tab through entire interface

---

## Progress Tracking

- **Status**: ⏳ Not Started
- **Start Date**: [Fill when started]
- **End Date**: [Fill when completed]
- **Actual Hours**: [Fill when completed]
- **Blockers**: [Document any blockers encountered]
- **Notes**: [Any important notes during implementation]

### Checkpoint 1: Base Styling (Est. 2 hours)
- [ ] globals.css created with CSS variables
- [ ] Base element styles applied
- [ ] Typography system defined
- [ ] Z-index scale defined

### Checkpoint 2: Theme System (Est. 2 hours)
- [ ] cerner.css created with all colors
- [ ] epic.css created with all colors
- [ ] Theme switching tested
- [ ] All components adapted to themes

### Checkpoint 3: Animations & Responsive (Est. 1.5 hours)
- [ ] animations.css created with all keyframes
- [ ] responsive.css created with breakpoints
- [ ] Framer Motion components created
- [ ] Responsive design tested

### Checkpoint 4: Accessibility & Testing (Est. 0.5 hours)
- [ ] Contrast testing completed
- [ ] Keyboard navigation tested
- [ ] Screen reader tested
- [ ] Reduced motion tested
- [ ] All browsers tested

---

**Previous Task**: TASK 1.4 - Custom Hooks
**Next Task**: Phase 2 - Validation & Backend Integration
