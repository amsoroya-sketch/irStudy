# EMR Practice System - Complete Styling & Functionality Specification

**Document:** UI/UX Styling and Interactive Functionality
**Version:** 1.0
**Date:** 2026-02-02
**Purpose:** Complete specifications for visual design, CSS styling, animations, and interactive behaviors

---

## Table of Contents
1. [Design System Overview](#design-system-overview)
2. [Color Palette & Typography](#color-palette--typography)
3. [Component Styling Specifications](#component-styling-specifications)
4. [Interactive Behaviors](#interactive-behaviors)
5. [Animations & Transitions](#animations--transitions)
6. [Responsive Design](#responsive-design)
7. [Accessibility](#accessibility)
8. [State Management & Data Flow](#state-management--data-flow)

---

## 1. Design System Overview

### Design Philosophy
- **Medical Authenticity:** Match real Cerner/Epic interfaces 95%+
- **Clarity:** Clear hierarchy, readable text, obvious actions
- **Efficiency:** Minimize clicks, keyboard shortcuts, auto-save
- **Feedback:** Instant visual feedback for all actions
- **Safety:** Color coding for critical information (allergies red, warnings yellow)

### CSS Framework
```bash
# Technology Stack
- Tailwind CSS 3.4+ (utility-first styling)
- CSS Modules (component-scoped styles)
- Framer Motion (animations)
- Lucide React (icons)

# File Structure
src/
├── styles/
│   ├── globals.css           # Global styles, CSS variables
│   ├── tailwind.config.js    # Tailwind configuration
│   └── themes/
│       ├── cerner.css        # Cerner-specific overrides
│       └── epic.css          # Epic-specific overrides
```

---

## 2. Color Palette & Typography

### Cerner PowerChart Color Palette

```css
/* CSS Variables - Cerner Theme */
:root[data-theme="cerner"] {
  /* Primary Colors */
  --cerner-primary: #3498db;        /* Blue - primary actions */
  --cerner-primary-hover: #2980b9;
  --cerner-primary-active: #21618c;

  /* Background Colors */
  --cerner-bg-dark: #2c3e50;        /* Sidebar background */
  --cerner-bg-darker: #1a252f;      /* Sidebar header/footer */
  --cerner-bg-light: #ecf0f1;       /* Content background */
  --cerner-bg-white: #ffffff;       /* Cards, modals */

  /* Text Colors */
  --cerner-text-primary: #2c3e50;   /* Main text */
  --cerner-text-secondary: #7f8c8d; /* Secondary text */
  --cerner-text-light: #bdc3c7;     /* Disabled text */
  --cerner-text-inverse: #ffffff;   /* Text on dark bg */

  /* Semantic Colors */
  --cerner-success: #27ae60;        /* Success states */
  --cerner-warning: #f39c12;        /* Warnings */
  --cerner-error: #e74c3c;          /* Errors */
  --cerner-info: #3498db;           /* Info messages */
  --cerner-critical: #c0392b;       /* Critical alerts */

  /* Module Colors (for navigation items) */
  --cerner-dashboard: #3498db;      /* Blue */
  --cerner-patient: #27ae60;        /* Green */
  --cerner-soap: #9b59b6;           /* Purple */
  --cerner-meds: #e67e22;           /* Orange */
  --cerner-orders: #e74c3c;         /* Red */
  --cerner-vitals: #16a085;         /* Teal */
  --cerner-alerts: #f39c12;         /* Yellow */

  /* Border & Shadow */
  --cerner-border: #bdc3c7;
  --cerner-border-light: #ecf0f1;
  --cerner-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  --cerner-shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.15);
}
```

### Epic EHR Color Palette

```css
/* CSS Variables - Epic Theme */
:root[data-theme="epic"] {
  /* Primary Colors */
  --epic-primary: #8b5cf6;          /* Purple - primary actions */
  --epic-primary-hover: #7c3aed;
  --epic-primary-active: #6d28d9;

  /* Background Colors */
  --epic-bg-dark: #581c87;          /* Sidebar background */
  --epic-bg-darker: #3b0764;        /* Darker purple */
  --epic-bg-light: #f5f3ff;         /* Content background */
  --epic-bg-white: #ffffff;

  /* Text Colors */
  --epic-text-primary: #1f2937;
  --epic-text-secondary: #6b7280;
  --epic-text-light: #9ca3af;
  --epic-text-inverse: #ffffff;

  /* Semantic Colors */
  --epic-success: #10b981;
  --epic-warning: #f59e0b;
  --epic-error: #ef4444;
  --epic-info: #3b82f6;
  --epic-critical: #dc2626;

  /* Border & Shadow */
  --epic-border: #d1d5db;
  --epic-border-light: #e5e7eb;
  --epic-shadow: 0 2px 8px rgba(139, 92, 246, 0.1);
  --epic-shadow-lg: 0 4px 16px rgba(139, 92, 246, 0.15);
}
```

### Typography System

```css
/* Typography Hierarchy */
:root {
  /* Font Families */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'Roboto Mono', 'Courier New', monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;      /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;      /* 24px */
  --text-3xl: 1.875rem;    /* 30px */

  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Letter Spacing */
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
}

/* Typography Classes */
.heading-1 {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
}

.heading-2 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
}

.heading-3 {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-normal);
}

.body-text {
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  line-height: var(--leading-normal);
}

.body-text-small {
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  line-height: var(--leading-normal);
}

.medical-note {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}
```

---

## 3. Component Styling Specifications

### 3.1 Cerner Sidebar (Fixed Navigation)

```css
/* Cerner Sidebar Component */
.cerner-sidebar {
  /* Layout */
  width: 256px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;

  /* Styling */
  background: var(--cerner-bg-dark);
  color: var(--cerner-text-inverse);

  /* Display */
  display: flex;
  flex-direction: column;

  /* Shadow */
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.2);
}

.cerner-sidebar-header {
  /* Layout */
  padding: 1rem;

  /* Styling */
  background: var(--cerner-bg-darker);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.cerner-sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cerner-logo-icon {
  width: 32px;
  height: 32px;
  background: var(--cerner-primary);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-bold);
  font-size: var(--text-lg);
}

.cerner-sidebar-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--cerner-text-inverse);
}

.cerner-sidebar-subtitle {
  font-size: var(--text-xs);
  color: var(--cerner-text-light);
  margin-top: 2px;
}

/* Navigation Items */
.cerner-sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.cerner-nav-item {
  /* Layout */
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;

  /* Styling */
  cursor: pointer;
  border-left: 4px solid transparent;
  transition: all 0.2s ease;

  /* Typography */
  font-size: var(--text-sm);
  color: var(--cerner-text-light);
  text-decoration: none;
}

.cerner-nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--cerner-text-inverse);
}

.cerner-nav-item.active {
  background: rgba(255, 255, 255, 0.1);
  border-left-color: var(--cerner-primary);
  color: var(--cerner-text-inverse);
  font-weight: var(--font-medium);
}

.cerner-nav-item-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.cerner-nav-item.active .cerner-nav-item-icon {
  /* Module-specific colors when active */
  color: var(--cerner-dashboard); /* Dynamic based on module */
}

/* Sidebar Footer */
.cerner-sidebar-footer {
  /* Layout */
  padding: 1rem;

  /* Styling */
  background: var(--cerner-bg-darker);
  border-top: 1px solid rgba(255, 255, 255, 0.1);

  /* Typography */
  font-size: var(--text-xs);
  color: var(--cerner-text-light);
}

.cerner-session-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.cerner-session-id {
  font-family: var(--font-mono);
  color: var(--cerner-text-inverse);
}
```

### 3.2 Patient Banner (Top Bar)

```css
/* Patient Banner Component */
.patient-banner {
  /* Layout */
  position: sticky;
  top: 0;
  z-index: 900;
  padding: 0.75rem 1.5rem;

  /* Styling */
  background: var(--cerner-bg-light);
  border-bottom: 3px solid var(--cerner-primary);

  /* Shadow */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.patient-demographics {
  /* Layout */
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;

  /* Typography */
  font-size: var(--text-sm);
  color: var(--cerner-text-primary);
}

.patient-name {
  /* Typography */
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--cerner-text-primary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.patient-gender,
.patient-age {
  font-weight: var(--font-medium);
}

.patient-divider {
  color: var(--cerner-text-secondary);
  font-weight: var(--font-normal);
}

.patient-mrn,
.patient-dob {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

/* Allergy Alert */
.patient-allergies {
  /* Layout */
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;

  /* Styling */
  background: linear-gradient(to right, #fee, #fff);
  border: 2px solid var(--cerner-error);
  border-radius: 6px;

  /* Typography */
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--cerner-critical);
}

.patient-allergies-icon {
  width: 20px;
  height: 20px;
  color: var(--cerner-error);
  animation: pulse-warning 2s ease-in-out infinite;
}

@keyframes pulse-warning {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.1);
  }
}

.patient-allergies-label {
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.patient-allergies-list {
  font-weight: var(--font-normal);
}
```

### 3.3 SOAP Note Editor

```css
/* Progress Note Editor Container */
.progress-note-editor {
  /* Layout */
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;

  /* Styling */
  background: var(--cerner-bg-white);
  border-radius: 8px;
  box-shadow: var(--cerner-shadow-lg);
}

/* Editor Header */
.editor-header {
  /* Layout */
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;

  /* Styling */
  border-bottom: 2px solid var(--cerner-border-light);
}

.editor-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--cerner-text-primary);
  margin-bottom: 0.25rem;
}

.editor-subtitle {
  font-size: var(--text-sm);
  color: var(--cerner-text-secondary);
}

/* Typing Metrics Badge */
.typing-metrics-badge {
  /* Layout */
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;

  /* Styling */
  background: linear-gradient(135deg, var(--cerner-primary), var(--cerner-primary-hover));
  border-radius: 20px;
  color: white;

  /* Typography */
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.typing-wpm {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  font-family: var(--font-mono);
}

/* SOAP Section Container */
.soap-section {
  /* Layout */
  margin-bottom: 2rem;
}

.section-label {
  /* Layout */
  display: block;
  margin-bottom: 0.5rem;

  /* Typography */
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--cerner-text-primary);
}

.section-hint {
  /* Typography */
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  color: var(--cerner-text-secondary);
  margin-left: 0.5rem;
}

/* SOAP Textarea */
.soap-textarea {
  /* Layout */
  width: 100%;
  padding: 1rem;
  min-height: 120px;

  /* Styling */
  background: #fafafa;
  border: 2px solid var(--cerner-border);
  border-radius: 6px;
  resize: vertical;

  /* Typography */
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  color: var(--cerner-text-primary);

  /* Transition */
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.soap-textarea:focus {
  outline: none;
  border-color: var(--cerner-primary);
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
  background: white;
}

.soap-textarea.error {
  border-color: var(--cerner-error);
  background: #fff5f5;
}

.soap-textarea.error:focus {
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

/* Section Metadata */
.section-meta {
  /* Layout */
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-top: 0.5rem;
  gap: 1rem;
}

.text-info {
  /* Layout */
  display: flex;
  align-items: start;
  gap: 0.5rem;
  flex: 1;

  /* Styling */
  padding: 0.5rem;
  background: #e8f4fd;
  border-left: 3px solid var(--cerner-info);
  border-radius: 4px;

  /* Typography */
  font-size: var(--text-xs);
  color: #2c5f77;
}

.text-info-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  margin-top: 2px;
}

.char-count {
  /* Typography */
  font-size: var(--text-xs);
  color: var(--cerner-text-secondary);
  font-family: var(--font-mono);
  white-space: nowrap;
}

.char-count .text-red-600 {
  color: var(--cerner-error);
  font-weight: var(--font-semibold);
}

.char-count .text-green-600 {
  color: var(--cerner-success);
}

/* Error Message */
.error-message {
  /* Layout */
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;

  /* Styling */
  background: #fff5f5;
  border: 1px solid var(--cerner-error);
  border-radius: 4px;

  /* Typography */
  font-size: var(--text-sm);
  color: var(--cerner-error);
  font-weight: var(--font-medium);
}

/* Editor Actions (Bottom Buttons) */
.editor-actions {
  /* Layout */
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;

  /* Styling */
  border-top: 2px solid var(--cerner-border-light);
}

/* Button Styles */
.btn-secondary {
  /* Layout */
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;

  /* Styling */
  background: #f8f9fa;
  border: 2px solid var(--cerner-border);
  border-radius: 6px;
  cursor: pointer;

  /* Typography */
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--cerner-text-primary);

  /* Transition */
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #e9ecef;
  border-color: var(--cerner-text-secondary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-secondary:active {
  transform: translateY(0);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-primary {
  /* Layout */
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 2rem;

  /* Styling */
  background: linear-gradient(135deg, var(--cerner-primary), var(--cerner-primary-hover));
  border: none;
  border-radius: 6px;
  cursor: pointer;

  /* Typography */
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: white;

  /* Shadow & Transition */
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
  transition: all 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(52, 152, 219, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
```

### 3.4 Validation Feedback Panel

```css
/* Validation Panel (slides in from right) */
.validation-panel {
  /* Layout */
  position: fixed;
  right: 0;
  top: 0;
  width: 480px;
  height: 100vh;
  padding: 2rem;
  overflow-y: auto;

  /* Styling */
  background: white;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.2);
  z-index: 1100;

  /* Animation */
  animation: slide-in-right 0.3s ease-out;
}

@keyframes slide-in-right {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Overall Score Display */
.overall-score-container {
  /* Layout */
  text-align: center;
  padding: 2rem;
  margin-bottom: 2rem;

  /* Styling */
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  border: 2px solid var(--cerner-border-light);
}

.overall-score-value {
  font-size: 4rem;
  font-weight: var(--font-bold);
  font-family: var(--font-mono);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.overall-score-value.excellent {
  color: var(--cerner-success);
}

.overall-score-value.good {
  color: #27ae60;
}

.overall-score-value.satisfactory {
  color: var(--cerner-warning);
}

.overall-score-value.needs-improvement {
  color: #e67e22;
}

.overall-score-value.unsatisfactory {
  color: var(--cerner-error);
}

/* Progress Bar */
.progress-bar-container {
  /* Layout */
  width: 100%;
  height: 12px;
  margin: 1rem 0;

  /* Styling */
  background: #e9ecef;
  border-radius: 6px;
  overflow: hidden;
}

.progress-bar-fill {
  /* Layout */
  height: 100%;

  /* Styling */
  background: linear-gradient(90deg, var(--cerner-primary), var(--cerner-primary-hover));
  border-radius: 6px;

  /* Animation */
  transition: width 0.6s ease-out;
}

/* Criteria Breakdown */
.criteria-section {
  margin-bottom: 1.5rem;
}

.criteria-item {
  /* Layout */
  padding: 1rem;
  margin-bottom: 1rem;

  /* Styling */
  background: #f8f9fa;
  border-left: 4px solid var(--cerner-primary);
  border-radius: 6px;
}

.criteria-header {
  /* Layout */
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.criteria-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--cerner-text-primary);
}

.criteria-score {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  font-family: var(--font-mono);
}

.criteria-feedback {
  font-size: var(--text-sm);
  color: var(--cerner-text-secondary);
  line-height: var(--leading-normal);
  margin-top: 0.5rem;
}

/* Strengths Section */
.strengths-section {
  /* Layout */
  margin-bottom: 2rem;
  padding: 1.5rem;

  /* Styling */
  background: #f0fdf4;
  border: 2px solid var(--cerner-success);
  border-radius: 8px;
}

.section-title {
  /* Layout */
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;

  /* Typography */
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--cerner-text-primary);
}

.strengths-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.strength-item {
  /* Layout */
  display: flex;
  align-items: start;
  gap: 0.75rem;
  margin-bottom: 0.75rem;

  /* Typography */
  font-size: var(--text-sm);
  color: #166534;
}

.strength-checkmark {
  /* Layout */
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;

  /* Styling */
  color: var(--cerner-success);
}

/* Improvements Section */
.improvements-section {
  /* Layout */
  margin-bottom: 2rem;
  padding: 1.5rem;

  /* Styling */
  background: #fff7ed;
  border: 2px solid var(--cerner-warning);
  border-radius: 8px;
}

.improvement-item {
  /* Layout */
  display: flex;
  align-items: start;
  gap: 0.75rem;
  margin-bottom: 0.75rem;

  /* Typography */
  font-size: var(--text-sm);
  color: #9a3412;
}

.improvement-bullet {
  /* Layout */
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;

  /* Styling */
  color: var(--cerner-warning);
}

/* Suggestion Cards */
.suggestion-card {
  /* Layout */
  padding: 1rem;
  margin-bottom: 1rem;

  /* Styling */
  background: white;
  border: 2px solid #dbeafe;
  border-left-width: 4px;
  border-left-color: var(--cerner-info);
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.suggestion-issue {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--cerner-text-primary);
  margin-bottom: 0.5rem;
}

.suggestion-text {
  font-size: var(--text-sm);
  color: var(--cerner-text-secondary);
  margin-bottom: 0.75rem;
}

.suggestion-example {
  /* Layout */
  padding: 0.75rem;

  /* Styling */
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 4px;

  /* Typography */
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: #374151;
}

.suggestion-example-label {
  font-size: var(--text-xs);
  color: var(--cerner-text-secondary);
  margin-bottom: 0.25rem;
}

/* Priority Badges */
.priority-badge {
  /* Layout */
  display: inline-block;
  padding: 0.25rem 0.75rem;
  margin-bottom: 0.5rem;

  /* Styling */
  border-radius: 12px;

  /* Typography */
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.priority-high {
  background: #fee2e2;
  color: #991b1b;
}

.priority-medium {
  background: #fed7aa;
  color: #9a3412;
}

.priority-low {
  background: #dbeafe;
  color: #1e40af;
}

/* Australian Compliance Badges */
.compliance-badges {
  /* Layout */
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.compliance-badge {
  /* Layout */
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;

  /* Styling */
  border-radius: 20px;

  /* Typography */
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.compliance-badge.passed {
  background: #dcfce7;
  color: #166534;
  border: 1px solid var(--cerner-success);
}

.compliance-badge.failed {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid var(--cerner-error);
}

.compliance-badge-icon {
  width: 16px;
  height: 16px;
}

/* Action Buttons in Panel */
.panel-actions {
  /* Layout */
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid var(--cerner-border-light);
}

.btn-revise {
  flex: 1;
  justify-content: center;
}

.btn-accept {
  flex: 1;
  justify-content: center;
}
```

---

## 4. Interactive Behaviors

### 4.1 Auto-Save Functionality

```typescript
// Auto-save implementation
import { useEffect, useRef } from 'react';
import { debounce } from 'lodash';

export const useAutoSave = (
  data: any,
  saveFunction: (data: any) => Promise<void>,
  delay: number = 30000 // 30 seconds
) => {
  const lastSavedRef = useRef<string>('');

  // Debounced save function
  const debouncedSave = useRef(
    debounce(async (currentData: any) => {
      const dataString = JSON.stringify(currentData);

      // Only save if data has changed
      if (dataString !== lastSavedRef.current) {
        try {
          await saveFunction(currentData);
          lastSavedRef.current = dataString;

          // Show save indicator
          showToast('Draft saved', 'success');
        } catch (error) {
          console.error('Auto-save failed:', error);
          showToast('Auto-save failed', 'error');
        }
      }
    }, delay)
  ).current;

  // Trigger save when data changes
  useEffect(() => {
    if (data) {
      debouncedSave(data);
    }
  }, [data]);

  // Save before unmount
  useEffect(() => {
    return () => {
      debouncedSave.flush();
    };
  }, []);
};

// Usage in SOAP Note Editor
const ProgressNoteEditor = () => {
  const { watch, getValues } = useForm();
  const currentData = watch();

  useAutoSave(currentData, async (data) => {
    await api.saveDraft(sessionId, data);
  }, 30000);

  return (/* ... */);
};
```

### 4.2 Real-Time Typing Metrics

```typescript
// Typing metrics tracker
export const useTypingMetrics = () => {
  const [metrics, setMetrics] = useState({
    startTime: Date.now(),
    keystrokes: 0,
    characters: 0,
    words: 0,
    wpm: 0,
    accuracy: 100
  });

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    setMetrics(prev => {
      const newKeystrokes = prev.keystrokes + 1;
      const elapsedMinutes = (Date.now() - prev.startTime) / 60000;

      // Calculate WPM (average 5 characters per word)
      const wpm = Math.round((newKeystrokes / 5) / elapsedMinutes);

      return {
        ...prev,
        keystrokes: newKeystrokes,
        wpm: isNaN(wpm) || !isFinite(wpm) ? 0 : wpm
      };
    });
  }, []);

  const updateWordCount = useCallback((text: string) => {
    const words = text.split(/\s+/).filter(Boolean).length;
    const characters = text.length;

    setMetrics(prev => ({
      ...prev,
      words,
      characters
    }));
  }, []);

  const reset = useCallback(() => {
    setMetrics({
      startTime: Date.now(),
      keystrokes: 0,
      characters: 0,
      words: 0,
      wpm: 0,
      accuracy: 100
    });
  }, []);

  return {
    metrics,
    handleKeyPress,
    updateWordCount,
    reset
  };
};
```

### 4.3 PBS Medication Search (Debounced)

```typescript
// Debounced search for PBS medications
export const usePBSSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<PBSMedication[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Debounced search function
  const debouncedSearch = useRef(
    debounce(async (searchQuery: string) => {
      if (searchQuery.length < 2) {
        setResults([]);
        return;
      }

      setIsSearching(true);

      try {
        const response = await api.searchPBS(searchQuery);
        setResults(response.data);
      } catch (error) {
        console.error('PBS search failed:', error);
        showToast('Search failed', 'error');
      } finally {
        setIsSearching(false);
      }
    }, 300) // 300ms delay
  ).current;

  // Handle search input change
  const handleSearch = (value: string) => {
    setQuery(value);
    debouncedSearch(value);
  };

  // Clear search
  const clearSearch = () => {
    setQuery('');
    setResults([]);
  };

  return {
    query,
    results,
    isSearching,
    handleSearch,
    clearSearch
  };
};
```

### 4.4 Form Validation (Real-Time)

```typescript
// Real-time form validation with Zod
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';

const ProgressNoteEditor = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid, isDirty },
    watch,
    trigger
  } = useForm<SOAPNoteFormData>({
    resolver: zodResolver(soapNoteSchema),
    mode: 'onChange', // Validate on every change
    reValidateMode: 'onChange'
  });

  // Watch specific fields for live validation
  const subjective = watch('subjective');

  // Trigger validation when user stops typing
  const handleBlur = async (field: keyof SOAPNoteFormData) => {
    await trigger(field);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <textarea
        {...register('subjective')}
        onBlur={() => handleBlur('subjective')}
        className={errors.subjective ? 'error' : ''}
      />

      {errors.subjective && (
        <p className="error-message">
          {errors.subjective.message}
        </p>
      )}
    </form>
  );
};
```

### 4.5 Keyboard Shortcuts

```typescript
// Keyboard shortcuts for efficiency
export const useKeyboardShortcuts = (handlers: Record<string, () => void>) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + S: Save draft
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handlers.saveDraft?.();
      }

      // Ctrl/Cmd + Enter: Submit
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handlers.submit?.();
      }

      // Escape: Cancel/Close
      if (e.key === 'Escape') {
        handlers.cancel?.();
      }

      // Ctrl/Cmd + /: Show keyboard shortcuts help
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        handlers.showHelp?.();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handlers]);
};

// Usage
const ProgressNoteEditor = () => {
  useKeyboardShortcuts({
    saveDraft: handleSaveDraft,
    submit: handleSubmit(onSubmit),
    cancel: () => router.back(),
    showHelp: () => setShowShortcutsModal(true)
  });

  return (/* ... */);
};
```

---

## 5. Animations & Transitions

### 5.1 Framer Motion Variants

```typescript
// Animation variants for Framer Motion
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 }
};

export const slideInRight = {
  initial: { x: '100%', opacity: 0 },
  animate: { x: 0, opacity: 1 },
  exit: { x: '100%', opacity: 0 },
  transition: { type: 'spring', damping: 25, stiffness: 200 }
};

export const scaleUp = {
  initial: { scale: 0.9, opacity: 0 },
  animate: { scale: 1, opacity: 1 },
  exit: { scale: 0.9, opacity: 0 },
  transition: { duration: 0.2 }
};

// Progress bar animation
export const progressBarFill = {
  initial: { width: 0 },
  animate: (score: number) => ({
    width: `${score}%`,
    transition: {
      duration: 0.8,
      ease: 'easeOut'
    }
  })
};

// Validation panel entrance
export const validationPanelVariants = {
  hidden: {
    x: '100%',
    opacity: 0
  },
  visible: {
    x: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      damping: 20,
      stiffness: 150
    }
  },
  exit: {
    x: '100%',
    opacity: 0,
    transition: {
      duration: 0.2
    }
  }
};

// Usage
import { motion, AnimatePresence } from 'framer-motion';

const ValidationPanel = ({ isOpen, onClose }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          variants={validationPanelVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          className="validation-panel"
        >
          {/* Panel content */}
        </motion.div>
      )}
    </AnimatePresence>
  );
};
```

### 5.2 Loading States

```css
/* Loading Spinner */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--cerner-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Skeleton Loader */
@keyframes skeleton-loading {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}

.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 0px,
    #e0e0e0 40px,
    #f0f0f0 80px
  );
  background-size: 200px 100%;
  animation: skeleton-loading 1.4s ease-in-out infinite;
  border-radius: 4px;
}

.skeleton-text {
  height: 16px;
  margin-bottom: 8px;
}

.skeleton-title {
  height: 24px;
  width: 60%;
  margin-bottom: 12px;
}
```

---

## 6. Responsive Design

### Breakpoints

```css
:root {
  --breakpoint-sm: 640px;   /* Mobile landscape */
  --breakpoint-md: 768px;   /* Tablet */
  --breakpoint-lg: 1024px;  /* Laptop */
  --breakpoint-xl: 1280px;  /* Desktop */
  --breakpoint-2xl: 1536px; /* Large desktop */
}

/* Mobile-first responsive utilities */
@media (max-width: 1024px) {
  .cerner-sidebar {
    /* On tablet/mobile, sidebar becomes drawer */
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .cerner-sidebar.open {
    transform: translateX(0);
  }

  .soap-textarea {
    font-size: 16px; /* Prevent zoom on iOS */
  }

  .validation-panel {
    width: 100%; /* Full width on mobile */
  }
}

@media (max-width: 768px) {
  .patient-demographics {
    flex-direction: column;
    align-items: flex-start;
  }

  .editor-header {
    flex-direction: column;
    gap: 1rem;
  }

  .editor-actions {
    flex-direction: column;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
```

---

## 7. Accessibility (WCAG 2.1 AA)

```css
/* Focus visible styles */
*:focus-visible {
  outline: 3px solid var(--cerner-primary);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Skip to main content link */
.skip-to-main {
  position: absolute;
  left: -9999px;
  z-index: 999;
  padding: 1rem;
  background: var(--cerner-primary);
  color: white;
  text-decoration: none;
}

.skip-to-main:focus {
  left: 50%;
  transform: translateX(-50%);
  top: 1rem;
}

/* Screen reader only text */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  :root {
    --cerner-border: #000;
    --cerner-text-secondary: #000;
  }

  .btn-primary,
  .btn-secondary {
    border: 2px solid currentColor;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 8. State Management & Data Flow

### 8.1 State Architecture

```typescript
// Zustand store for EMR session state
import create from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface EMRSessionState {
  // Current session data
  sessionId: string | null;
  patient: Patient | null;
  emrType: 'cerner' | 'epic';

  // SOAP note in progress
  soapNote: Partial<SOAPNote>;

  // Prescriptions in progress
  prescriptions: Prescription[];

  // Validation results
  validationResult: ValidationResult | null;

  // UI state
  isSaving: boolean;
  isSubmitting: boolean;
  showValidationPanel: boolean;

  // Actions
  startSession: (patient: Patient, emrType: 'cerner' | 'epic') => void;
  updateSOAPNote: (field: keyof SOAPNote, value: string) => void;
  addPrescription: (rx: Prescription) => void;
  removePrescription: (id: string) => void;
  submitForValidation: () => Promise<void>;
  saveDraft: () => Promise<void>;
  endSession: () => void;
}

export const useEMRSession = create<EMRSessionState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        sessionId: null,
        patient: null,
        emrType: 'cerner',
        soapNote: {},
        prescriptions: [],
        validationResult: null,
        isSaving: false,
        isSubmitting: false,
        showValidationPanel: false,

        // Actions
        startSession: (patient, emrType) => {
          const sessionId = `session_${Date.now()}`;
          set({
            sessionId,
            patient,
            emrType,
            soapNote: {},
            prescriptions: [],
            validationResult: null
          });
        },

        updateSOAPNote: (field, value) => {
          set(state => ({
            soapNote: {
              ...state.soapNote,
              [field]: value
            }
          }));
        },

        addPrescription: (rx) => {
          set(state => ({
            prescriptions: [...state.prescriptions, rx]
          }));
        },

        removePrescription: (id) => {
          set(state => ({
            prescriptions: state.prescriptions.filter(rx => rx.id !== id)
          }));
        },

        submitForValidation: async () => {
          const { sessionId, patient, soapNote } = get();

          set({ isSubmitting: true });

          try {
            const response = await api.validateSOAPNote(sessionId, soapNote, patient);

            set({
              validationResult: response.data,
              showValidationPanel: true,
              isSubmitting: false
            });
          } catch (error) {
            console.error('Validation failed:', error);
            set({ isSubmitting: false });
            showToast('Validation failed', 'error');
          }
        },

        saveDraft: async () => {
          const { sessionId, soapNote, prescriptions } = get();

          set({ isSaving: true });

          try {
            await api.saveDraft(sessionId, {
              soapNote,
              prescriptions
            });

            set({ isSaving: false });
            showToast('Draft saved', 'success');
          } catch (error) {
            console.error('Save failed:', error);
            set({ isSaving: false });
            showToast('Save failed', 'error');
          }
        },

        endSession: () => {
          set({
            sessionId: null,
            patient: null,
            soapNote: {},
            prescriptions: [],
            validationResult: null,
            showValidationPanel: false
          });
        }
      }),
      {
        name: 'emr-session-storage',
        partialize: (state) => ({
          // Only persist these fields
          sessionId: state.sessionId,
          patient: state.patient,
          soapNote: state.soapNote,
          prescriptions: state.prescriptions
        })
      }
    )
  )
);
```

### 8.2 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interaction Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  Cerner Sidebar  │  Patient Banner  │  SOAP Editor  │  Meds Form│
└────────┬──────────────────┬─────────────────┬──────────────┬────┘
         │                  │                 │              │
         │                  │                 │              │
         ▼                  ▼                 ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      State Management (Zustand)                  │
├─────────────────────────────────────────────────────────────────┤
│  sessionState  │  patientData  │  soapNoteState  │  rxListState│
└────────┬──────────────────┬─────────────────┬──────────────┬────┘
         │                  │                 │              │
         │                  │                 │              │
         ▼                  ▼                 ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Service Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  GET /patient  │  POST /sessions  │  POST /validate  │ POST /rx│
└────────┬──────────────────┬─────────────────┬──────────────┬────┘
         │                  │                 │              │
         │                  │                 │              │
         ▼                  ▼                 ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│  Patient DB  │  Session DB  │  Rule Engine  │  AI Validator   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary

This comprehensive specification provides:

✅ **Complete CSS styling** for all components (Cerner sidebar, patient banner, SOAP editor, validation panel)

✅ **Interactive behaviors** (auto-save, typing metrics, debounced search, keyboard shortcuts)

✅ **Animations & transitions** (Framer Motion variants, loading states, skeleton loaders)

✅ **Responsive design** (mobile-first, tablet/desktop breakpoints)

✅ **Accessibility** (WCAG 2.1 AA compliant, focus styles, screen reader support)

✅ **State management architecture** (Zustand store, data flow diagram)

✅ **Visual design system** (color palettes, typography, spacing)

**Next Steps:**
1. Review and approve this specification
2. Create React component implementations
3. Set up RALPH agents for implementation
4. Begin frontend development sprint

**Estimated Implementation Time:** 80-120 hours (4-6 weeks)
