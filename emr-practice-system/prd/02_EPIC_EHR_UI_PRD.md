# Epic EHR UI Product Requirements Document

**Version**: 1.0
**Date**: 2026-02-02
**Product**: EMR Practice System - Epic EHR Simulation
**Target Users**: Medical students preparing for ICRP in Australian hospitals

---

## Table of Contents

1. [Epic EHR Overview](#epic-ehr-overview)
2. [Visual Design System](#visual-design-system)
3. [Core Components](#core-components)
4. [Navigation & Workflows](#navigation--workflows)
5. [Implementation Specifications](#implementation-specifications)
6. [Differences from Cerner](#differences-from-cerner)

---

## Epic EHR Overview

### What is Epic?

Epic is one of the two major EMR systems used in Australian hospitals (alongside Cerner PowerChart). Epic is known for:
- **Purple branding** and modern, clean interface
- **Icon-based navigation** with activity tabs
- **Integrated workflow** (notes, orders, results in one view)
- **Customizable workspace** with panels

### Epic in Australian Hospitals

Epic is used in major Australian hospitals including:
- Royal Melbourne Hospital
- Alfred Health
- Monash Health
- Queensland Health facilities
- Various private hospitals

### Key Differences from Cerner

| Feature | Cerner PowerChart | Epic EHR |
|---------|-------------------|----------|
| **Color Scheme** | Dark blue/grey (#2c3e50) | Purple/white (#8b5cf6) |
| **Navigation** | Left sidebar | Top tabs + left icon bar |
| **Layout** | Sidebar + main content | Icon bar + workspace panels |
| **Branding** | Professional dark | Modern purple |
| **Workflow** | Tab-based sections | Activity-based workspace |

---

## Visual Design System

### Color Palette

```css
/* Epic Theme Color Variables */
:root[data-theme="epic"] {
  /* Primary Purple */
  --epic-primary: #8b5cf6;          /* Epic purple */
  --epic-primary-dark: #7c3aed;     /* Darker purple for hover */
  --epic-primary-light: #a78bfa;    /* Lighter purple for accents */

  /* Background Colors */
  --epic-bg-white: #ffffff;         /* Main background */
  --epic-bg-light: #f9fafb;         /* Secondary background */
  --epic-bg-grey: #f3f4f6;          /* Panel backgrounds */

  /* Text Colors */
  --epic-text-primary: #111827;     /* Main text */
  --epic-text-secondary: #6b7280;   /* Secondary text */
  --epic-text-muted: #9ca3af;       /* Muted text */

  /* Border Colors */
  --epic-border: #e5e7eb;           /* Standard borders */
  --epic-border-dark: #d1d5db;      /* Emphasized borders */

  /* Status Colors */
  --epic-success: #10b981;          /* Success states */
  --epic-warning: #f59e0b;          /* Warnings */
  --epic-error: #ef4444;            /* Errors */
  --epic-info: #3b82f6;             /* Info messages */

  /* Icon Bar */
  --epic-icon-bar: #1f2937;         /* Left icon bar background */
  --epic-icon-inactive: #9ca3af;    /* Inactive icon color */
  --epic-icon-active: #8b5cf6;      /* Active icon color */
}
```

### Typography

```css
/* Epic Typography System */
.epic-font-family {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.epic-heading-xl {
  font-size: 1.875rem;  /* 30px */
  font-weight: 700;
  line-height: 1.2;
  color: var(--epic-text-primary);
}

.epic-heading-lg {
  font-size: 1.5rem;    /* 24px */
  font-weight: 600;
  line-height: 1.3;
  color: var(--epic-text-primary);
}

.epic-heading-md {
  font-size: 1.25rem;   /* 20px */
  font-weight: 600;
  line-height: 1.4;
  color: var(--epic-text-primary);
}

.epic-body-lg {
  font-size: 1rem;      /* 16px */
  font-weight: 400;
  line-height: 1.5;
  color: var(--epic-text-primary);
}

.epic-body-md {
  font-size: 0.875rem;  /* 14px */
  font-weight: 400;
  line-height: 1.5;
  color: var(--epic-text-secondary);
}

.epic-body-sm {
  font-size: 0.75rem;   /* 12px */
  font-weight: 400;
  line-height: 1.5;
  color: var(--epic-text-muted);
}
```

---

## Core Components

### 1. Epic Icon Bar (Left Navigation)

**Visual Mockup:**
```
┌─────┐
│  E  │  Epic logo
├─────┤
│ 📋 │  Patient Chart (active)
├─────┤
│ 📝 │  Notes
├─────┤
│ 💊 │  Medications
├─────┤
│ 🧪 │  Results
├─────┤
│ 📊 │  Orders
├─────┤
│ 📅 │  Schedule
├─────┤
│ ⚙️  │  Settings
└─────┘
```

**Component Specification:**

```typescript
import React from 'react';
import {
  ClipboardList, FileText, Pill, FlaskConical,
  ClipboardCheck, Calendar, Settings, Home
} from 'lucide-react';

interface EpicIconBarProps {
  activeView: string;
  onNavigate: (view: string) => void;
  sessionId: string;
}

const iconBarItems = [
  {
    id: 'dashboard',
    icon: Home,
    label: 'Dashboard',
    view: '/epic',
    color: 'text-purple-600'
  },
  {
    id: 'chart',
    icon: ClipboardList,
    label: 'Patient Chart',
    view: '/epic/chart',
    color: 'text-purple-600'
  },
  {
    id: 'notes',
    icon: FileText,
    label: 'Notes',
    view: '/epic/notes',
    color: 'text-blue-600'
  },
  {
    id: 'medications',
    icon: Pill,
    label: 'Medications',
    view: '/epic/medications',
    color: 'text-green-600'
  },
  {
    id: 'results',
    icon: FlaskConical,
    label: 'Results',
    view: '/epic/results',
    color: 'text-orange-600'
  },
  {
    id: 'orders',
    icon: ClipboardCheck,
    label: 'Orders',
    view: '/epic/orders',
    color: 'text-red-600'
  },
  {
    id: 'schedule',
    icon: Calendar,
    label: 'Schedule',
    view: '/epic/schedule',
    color: 'text-indigo-600'
  }
];

export const EpicIconBar: React.FC<EpicIconBarProps> = ({
  activeView,
  onNavigate,
  sessionId
}) => {
  return (
    <div className="epic-icon-bar">
      {/* Epic Logo */}
      <div className="epic-logo">
        <span className="text-2xl font-bold text-purple-600">E</span>
      </div>

      {/* Navigation Icons */}
      <div className="epic-nav-icons">
        {iconBarItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.view;

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.view)}
              className={`epic-icon-button ${isActive ? 'active' : ''}`}
              title={item.label}
              aria-label={item.label}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon
                className={`w-6 h-6 ${isActive ? item.color : 'text-gray-400'}`}
              />
              {isActive && (
                <span className="epic-icon-label">{item.label}</span>
              )}
            </button>
          );
        })}
      </div>

      {/* Settings at Bottom */}
      <div className="epic-icon-settings">
        <button
          onClick={() => onNavigate('/epic/settings')}
          className="epic-icon-button"
          title="Settings"
          aria-label="Settings"
        >
          <Settings className="w-6 h-6 text-gray-400" />
        </button>
      </div>
    </div>
  );
};
```

**CSS Styling:**

```css
/* Epic Icon Bar */
.epic-icon-bar {
  width: 72px;
  height: 100vh;
  background-color: var(--epic-icon-bar);
  display: flex;
  flex-direction: column;
  align-items: center;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}

.epic-logo {
  width: 100%;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background-color: #ffffff;
}

.epic-nav-icons {
  flex: 1;
  width: 100%;
  padding: 16px 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.epic-icon-button {
  width: 56px;
  height: 56px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.epic-icon-button:hover {
  background-color: rgba(139, 92, 246, 0.1);
}

.epic-icon-button.active {
  background-color: rgba(139, 92, 246, 0.15);
}

.epic-icon-button.active::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 32px;
  background-color: var(--epic-primary);
  border-radius: 0 2px 2px 0;
}

.epic-icon-label {
  font-size: 10px;
  margin-top: 4px;
  color: var(--epic-primary);
  font-weight: 600;
}

.epic-icon-settings {
  width: 100%;
  padding: 16px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
```

### 2. Epic Patient Banner

**Visual Mockup:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  👤 Sarah Johnson, 45F                    MRN: 12345678    DOB: 15/03/1979  │
│  ⚠️  ALLERGIES: Penicillin (Anaphylaxis), Sulfa drugs (Rash)                │
│  📋 Active Problems: Type 2 Diabetes, Hypertension, Asthma                   │
│  💊 Current Meds: 6 medications     📍 Location: Ward 3B, Bed 12             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Component Specification:**

```typescript
import React from 'react';
import { User, AlertTriangle, ClipboardList, Pill, MapPin } from 'lucide-react';

interface EpicPatientBannerProps {
  patient: {
    id: string;
    name: string;
    age: number;
    sex: 'M' | 'F' | 'Other';
    mrn: string;
    dob: string;
    allergies: Array<{
      allergen: string;
      reaction: string;
      severity: 'mild' | 'moderate' | 'severe';
    }>;
    activeProblems: string[];
    currentMedications: number;
    location: string;
  };
}

export const EpicPatientBanner: React.FC<EpicPatientBannerProps> = ({ patient }) => {
  const hasAllergies = patient.allergies.length > 0 && patient.allergies[0].allergen !== 'NKDA';
  const severeAllergies = patient.allergies.filter(a => a.severity === 'severe');

  return (
    <div className="epic-patient-banner">
      {/* Main Patient Info */}
      <div className="epic-banner-main">
        <User className="w-6 h-6 text-gray-600" />
        <div className="epic-patient-name">
          <span className="font-bold text-lg">{patient.name}</span>
          <span className="text-gray-600 ml-2">{patient.age}{patient.sex}</span>
        </div>
        <div className="epic-patient-identifiers">
          <span className="epic-badge">MRN: {patient.mrn}</span>
          <span className="epic-badge">DOB: {patient.dob}</span>
        </div>
      </div>

      {/* Allergy Alert */}
      {hasAllergies && (
        <div className={`epic-allergy-alert ${severeAllergies.length > 0 ? 'severe' : ''}`}>
          <AlertTriangle className="w-5 h-5" />
          <span className="font-semibold">ALLERGIES:</span>
          <span>
            {patient.allergies.map(a => `${a.allergen} (${a.reaction})`).join(', ')}
          </span>
        </div>
      )}

      {/* Clinical Summary */}
      <div className="epic-banner-summary">
        <div className="epic-summary-item">
          <ClipboardList className="w-4 h-4 text-gray-500" />
          <span className="text-sm">
            <strong>Active Problems:</strong> {patient.activeProblems.join(', ')}
          </span>
        </div>
        <div className="epic-summary-item">
          <Pill className="w-4 h-4 text-gray-500" />
          <span className="text-sm">
            <strong>Current Meds:</strong> {patient.currentMedications} medications
          </span>
        </div>
        <div className="epic-summary-item">
          <MapPin className="w-4 h-4 text-gray-500" />
          <span className="text-sm">
            <strong>Location:</strong> {patient.location}
          </span>
        </div>
      </div>
    </div>
  );
};
```

**CSS Styling:**

```css
/* Epic Patient Banner */
.epic-patient-banner {
  background: linear-gradient(to bottom, #ffffff, #f9fafb);
  border-bottom: 3px solid var(--epic-primary);
  padding: 16px 24px;
  margin-left: 72px; /* Account for icon bar */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.epic-banner-main {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.epic-patient-name {
  display: flex;
  align-items: center;
  flex: 1;
}

.epic-patient-identifiers {
  display: flex;
  gap: 12px;
}

.epic-badge {
  background-color: var(--epic-bg-grey);
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--epic-text-secondary);
}

.epic-allergy-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #fef3c7;
  border: 2px solid #f59e0b;
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
  font-size: 0.875rem;
  color: #92400e;
}

.epic-allergy-alert.severe {
  background-color: #fee2e2;
  border-color: #ef4444;
  color: #991b1b;
}

.epic-allergy-alert svg {
  flex-shrink: 0;
}

.epic-banner-summary {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.epic-summary-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--epic-text-secondary);
}
```

### 3. Epic Workspace Panel Layout

**Visual Mockup:**
```
┌─────┬──────────────────────────────────────────────────────────────┐
│  E  │  [Chart] [Notes] [Meds] [Results] [Orders] [In Basket]      │
│     ├──────────────────────────────────────────────────────────────┤
│ 📋 │  ┌────────────────────┐  ┌────────────────────────────────┐  │
│     │  │  Note Composer     │  │  Clinical Summary              │  │
│ 📝 │  │                    │  │                                │  │
│     │  │  [SOAP Template ▼] │  │  Recent Vitals:                │  │
│ 💊 │  │                    │  │  BP: 128/82, HR: 76            │  │
│     │  │  Chief Complaint:  │  │                                │  │
│ 🧪 │  │  [text area]       │  │  Recent Labs:                  │  │
│     │  │                    │  │  HbA1c: 6.8% (2 weeks ago)     │  │
│ 📊 │  │  HPI:              │  │                                │  │
│     │  │  [text area]       │  │  Active Orders:                │  │
│ 📅 │  │                    │  │  • Metformin 500mg BD          │  │
│     │  └────────────────────┘  │  • FBC (pending)               │  │
│ ⚙️  │                          └────────────────────────────────┘  │
└─────┴──────────────────────────────────────────────────────────────┘
```

**Component Specification:**

```typescript
import React, { useState } from 'react';
import { FileText, Activity, Pill, FlaskConical, ClipboardCheck, Inbox } from 'lucide-react';

interface EpicWorkspacePanelProps {
  sessionId: string;
  patientId: string;
}

const workspaceTabs = [
  { id: 'chart', label: 'Chart', icon: FileText },
  { id: 'notes', label: 'Notes', icon: FileText },
  { id: 'meds', label: 'Medications', icon: Pill },
  { id: 'results', label: 'Results', icon: FlaskConical },
  { id: 'orders', label: 'Orders', icon: ClipboardCheck },
  { id: 'inbox', label: 'In Basket', icon: Inbox }
];

export const EpicWorkspacePanel: React.FC<EpicWorkspacePanelProps> = ({
  sessionId,
  patientId
}) => {
  const [activeTab, setActiveTab] = useState('notes');
  const [leftPanelWidth, setLeftPanelWidth] = useState(60); // percentage

  return (
    <div className="epic-workspace">
      {/* Tab Bar */}
      <div className="epic-tab-bar">
        {workspaceTabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`epic-tab ${activeTab === tab.id ? 'active' : ''}`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Panel Layout */}
      <div className="epic-panel-layout">
        {/* Left Panel: Main Content */}
        <div className="epic-panel-left" style={{ width: `${leftPanelWidth}%` }}>
          {activeTab === 'notes' && <EpicNoteComposer sessionId={sessionId} />}
          {activeTab === 'meds' && <EpicMedicationPanel patientId={patientId} />}
          {activeTab === 'orders' && <EpicOrderPanel patientId={patientId} />}
        </div>

        {/* Resize Handle */}
        <div
          className="epic-panel-resize"
          onMouseDown={(e) => handleResizeStart(e, setLeftPanelWidth)}
        />

        {/* Right Panel: Clinical Summary */}
        <div className="epic-panel-right" style={{ width: `${100 - leftPanelWidth}%` }}>
          <EpicClinicalSummary patientId={patientId} />
        </div>
      </div>
    </div>
  );
};

// Resize handler
const handleResizeStart = (
  e: React.MouseEvent,
  setWidth: (width: number) => void
) => {
  e.preventDefault();

  const startX = e.clientX;
  const startWidth = parseInt(
    getComputedStyle(e.currentTarget.previousElementSibling as Element).width
  );

  const handleMouseMove = (moveEvent: MouseEvent) => {
    const dx = moveEvent.clientX - startX;
    const containerWidth = window.innerWidth - 72; // Subtract icon bar
    const newWidth = ((startWidth + dx) / containerWidth) * 100;

    // Constrain between 40% and 70%
    const constrainedWidth = Math.min(Math.max(newWidth, 40), 70);
    setWidth(constrainedWidth);
  };

  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);
};
```

**CSS Styling:**

```css
/* Epic Workspace */
.epic-workspace {
  margin-left: 72px; /* Account for icon bar */
  height: calc(100vh - 120px); /* Subtract patient banner */
  display: flex;
  flex-direction: column;
  background-color: var(--epic-bg-light);
}

.epic-tab-bar {
  display: flex;
  background-color: #ffffff;
  border-bottom: 2px solid var(--epic-border);
  padding: 0 16px;
  gap: 4px;
}

.epic-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  color: var(--epic-text-secondary);
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.epic-tab:hover {
  background-color: var(--epic-bg-light);
  color: var(--epic-text-primary);
}

.epic-tab.active {
  color: var(--epic-primary);
  border-bottom-color: var(--epic-primary);
  background-color: var(--epic-bg-light);
}

.epic-panel-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.epic-panel-left {
  background-color: #ffffff;
  overflow-y: auto;
  padding: 24px;
  border-right: 1px solid var(--epic-border);
}

.epic-panel-resize {
  width: 6px;
  background-color: var(--epic-border);
  cursor: col-resize;
  transition: background-color 0.2s ease;
}

.epic-panel-resize:hover {
  background-color: var(--epic-primary);
}

.epic-panel-right {
  background-color: var(--epic-bg-grey);
  overflow-y: auto;
  padding: 24px;
}
```

### 4. Epic Note Composer

**Component Specification:**

```typescript
import React, { useState } from 'react';
import { FileText, Save, Clock, CheckCircle } from 'lucide-react';

interface EpicNoteComposerProps {
  sessionId: string;
}

const noteTemplates = [
  { id: 'soap', label: 'SOAP Note', sections: ['Subjective', 'Objective', 'Assessment', 'Plan'] },
  { id: 'progress', label: 'Progress Note', sections: ['Interval History', 'Exam', 'Data', 'Assessment', 'Plan'] },
  { id: 'admission', label: 'Admission Note', sections: ['CC', 'HPI', 'PMHx', 'Medications', 'Allergies', 'SocHx', 'FamHx', 'ROS', 'PE', 'Labs', 'Assessment', 'Plan'] },
  { id: 'discharge', label: 'Discharge Summary', sections: ['Admission Date', 'Discharge Date', 'Diagnoses', 'Hospital Course', 'Discharge Medications', 'Follow-up'] }
];

export const EpicNoteComposer: React.FC<EpicNoteComposerProps> = ({ sessionId }) => {
  const [selectedTemplate, setSelectedTemplate] = useState('soap');
  const [autoSaveStatus, setAutoSaveStatus] = useState<'saved' | 'saving' | 'unsaved'>('saved');
  const [noteContent, setNoteContent] = useState<Record<string, string>>({});

  const currentTemplate = noteTemplates.find(t => t.id === selectedTemplate);

  return (
    <div className="epic-note-composer">
      {/* Header */}
      <div className="epic-composer-header">
        <FileText className="w-5 h-5 text-purple-600" />
        <h2 className="text-xl font-semibold">Note Composer</h2>

        {/* Auto-save Status */}
        <div className="epic-autosave-status ml-auto">
          {autoSaveStatus === 'saved' && (
            <>
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-sm text-gray-600">Saved</span>
            </>
          )}
          {autoSaveStatus === 'saving' && (
            <>
              <Clock className="w-4 h-4 text-blue-600 animate-spin" />
              <span className="text-sm text-gray-600">Saving...</span>
            </>
          )}
        </div>
      </div>

      {/* Template Selector */}
      <div className="epic-template-selector">
        <label className="text-sm font-medium text-gray-700">Note Template:</label>
        <select
          value={selectedTemplate}
          onChange={(e) => setSelectedTemplate(e.target.value)}
          className="epic-select"
        >
          {noteTemplates.map((template) => (
            <option key={template.id} value={template.id}>
              {template.label}
            </option>
          ))}
        </select>
      </div>

      {/* Note Sections */}
      <div className="epic-note-sections">
        {currentTemplate?.sections.map((section) => (
          <div key={section} className="epic-note-section">
            <label className="epic-section-label">{section}</label>
            <textarea
              value={noteContent[section] || ''}
              onChange={(e) => setNoteContent({ ...noteContent, [section]: e.target.value })}
              placeholder={`Enter ${section.toLowerCase()}...`}
              className="epic-textarea"
              rows={6}
            />
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="epic-composer-actions">
        <button className="epic-btn-secondary">
          Save Draft
        </button>
        <button className="epic-btn-primary">
          <Save className="w-4 h-4" />
          Sign & Submit
        </button>
      </div>
    </div>
  );
};
```

**CSS Styling:**

```css
/* Epic Note Composer */
.epic-note-composer {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 900px;
}

.epic-composer-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--epic-border);
}

.epic-autosave-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.epic-template-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.epic-select {
  padding: 10px 14px;
  border: 2px solid var(--epic-border);
  border-radius: 8px;
  font-size: 0.875rem;
  background-color: #ffffff;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.epic-select:focus {
  outline: none;
  border-color: var(--epic-primary);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.epic-note-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.epic-note-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.epic-section-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--epic-text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.epic-textarea {
  padding: 12px 14px;
  border: 2px solid var(--epic-border);
  border-radius: 8px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  resize: vertical;
  transition: border-color 0.2s ease;
}

.epic-textarea:focus {
  outline: none;
  border-color: var(--epic-primary);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.epic-composer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 2px solid var(--epic-border);
}

.epic-btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background-color: var(--epic-primary);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.epic-btn-primary:hover {
  background-color: var(--epic-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(139, 92, 246, 0.2);
}

.epic-btn-secondary {
  padding: 12px 24px;
  background-color: #ffffff;
  color: var(--epic-text-primary);
  border: 2px solid var(--epic-border);
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.epic-btn-secondary:hover {
  border-color: var(--epic-primary);
  color: var(--epic-primary);
}
```

### 5. Epic Medication Order Panel

**Component Specification:**

```typescript
import React, { useState } from 'react';
import { Pill, Search, Plus, AlertTriangle } from 'lucide-react';

interface EpicMedicationPanelProps {
  patientId: string;
}

export const EpicMedicationPanel: React.FC<EpicMedicationPanelProps> = ({ patientId }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMed, setSelectedMed] = useState<any>(null);

  return (
    <div className="epic-medication-panel">
      {/* Header */}
      <div className="epic-panel-header">
        <Pill className="w-5 h-5 text-purple-600" />
        <h2 className="text-xl font-semibold">Medication Orders</h2>
        <button className="epic-btn-primary ml-auto">
          <Plus className="w-4 h-4" />
          New Order
        </button>
      </div>

      {/* PBS Search */}
      <div className="epic-search-section">
        <label className="text-sm font-medium text-gray-700">Search PBS Medications:</label>
        <div className="epic-search-input-wrapper">
          <Search className="w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by medication name or PBS code..."
            className="epic-search-input"
          />
        </div>
      </div>

      {/* Medication Form */}
      {selectedMed && (
        <div className="epic-med-form">
          <h3 className="font-semibold text-lg mb-4">{selectedMed.name}</h3>

          <div className="epic-form-grid">
            <div className="epic-form-field">
              <label>Strength</label>
              <select className="epic-select">
                <option>500mg</option>
                <option>1000mg</option>
              </select>
            </div>

            <div className="epic-form-field">
              <label>Route</label>
              <select className="epic-select">
                <option>PO (Oral)</option>
                <option>IV (Intravenous)</option>
                <option>IM (Intramuscular)</option>
              </select>
            </div>

            <div className="epic-form-field">
              <label>Frequency</label>
              <select className="epic-select">
                <option>BD (Twice daily)</option>
                <option>TDS (Three times daily)</option>
                <option>QID (Four times daily)</option>
              </select>
            </div>

            <div className="epic-form-field">
              <label>Quantity</label>
              <input type="number" className="epic-input" placeholder="60" />
            </div>

            <div className="epic-form-field">
              <label>Repeats</label>
              <input type="number" className="epic-input" max="5" placeholder="5" />
            </div>
          </div>

          <div className="epic-form-field-full">
            <label>Clinical Indication (PBS Requirement)</label>
            <textarea
              className="epic-textarea"
              rows={3}
              placeholder="Enter clinical indication for prescribing this medication..."
            />
          </div>

          {/* PBS Authority Alert */}
          <div className="epic-alert-warning">
            <AlertTriangle className="w-5 h-5" />
            <div>
              <strong>PBS Authority Required</strong>
              <p>This medication requires PBS authority approval before prescribing.</p>
            </div>
          </div>

          <div className="epic-form-actions">
            <button className="epic-btn-secondary">Cancel</button>
            <button className="epic-btn-primary">Add to Orders</button>
          </div>
        </div>
      )}
    </div>
  );
};
```

**CSS Styling:**

```css
/* Epic Medication Panel */
.epic-medication-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.epic-panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--epic-border);
}

.epic-search-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.epic-search-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border: 2px solid var(--epic-border);
  border-radius: 8px;
  background-color: #ffffff;
  transition: border-color 0.2s ease;
}

.epic-search-input-wrapper:focus-within {
  border-color: var(--epic-primary);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.epic-search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.875rem;
}

.epic-med-form {
  background-color: var(--epic-bg-light);
  padding: 20px;
  border-radius: 12px;
  border: 2px solid var(--epic-border);
}

.epic-form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.epic-form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.epic-form-field label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--epic-text-primary);
}

.epic-form-field-full {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.epic-input {
  padding: 10px 14px;
  border: 2px solid var(--epic-border);
  border-radius: 8px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.epic-input:focus {
  outline: none;
  border-color: var(--epic-primary);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.epic-alert-warning {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background-color: #fef3c7;
  border: 2px solid #f59e0b;
  border-radius: 8px;
  margin-bottom: 16px;
}

.epic-alert-warning svg {
  flex-shrink: 0;
  color: #f59e0b;
}

.epic-alert-warning strong {
  display: block;
  font-weight: 600;
  color: #92400e;
  margin-bottom: 4px;
}

.epic-alert-warning p {
  font-size: 0.875rem;
  color: #92400e;
}

.epic-form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
```

---

## Navigation & Workflows

### Epic Workflow Patterns

1. **Chart Review Workflow**
   ```
   Icon Bar (Chart) → Patient Banner → Tab Bar (Chart)
   → Left Panel (Patient Summary) + Right Panel (Recent Results)
   ```

2. **Note Writing Workflow**
   ```
   Icon Bar (Notes) → Patient Banner → Tab Bar (Notes)
   → Left Panel (Note Composer) + Right Panel (Clinical Summary)
   ```

3. **Medication Ordering Workflow**
   ```
   Icon Bar (Medications) → Patient Banner → Tab Bar (Meds)
   → Search PBS → Select Medication → Fill Order Form
   → Validation → Add to Orders
   ```

4. **Results Review Workflow**
   ```
   Icon Bar (Results) → Patient Banner → Tab Bar (Results)
   → Left Panel (Lab Results Timeline) + Right Panel (Trending Graphs)
   ```

---

## Differences from Cerner

### Visual Design

| Aspect | Cerner | Epic |
|--------|--------|------|
| **Primary Color** | Blue (#3498db) | Purple (#8b5cf6) |
| **Background** | Dark (#2c3e50) | Light (#ffffff) |
| **Navigation** | Sidebar | Icon bar + tabs |
| **Layout** | Single panel | Resizable dual panels |
| **Typography** | Sans-serif | Inter font |

### Interaction Patterns

| Feature | Cerner | Epic |
|---------|--------|------|
| **Navigation** | Click sidebar items | Click icons, then tabs |
| **Note Writing** | Full-screen editor | Split panel with clinical summary |
| **Search** | Top search bar | Context-specific search in each panel |
| **Actions** | Bottom action bar | Context-specific buttons |
| **Validation** | Right panel | Inline + summary panel |

### User Experience Focus

**Cerner**: Traditional hospital system feel
- Professional, clinical
- Information-dense
- Tab-based workflow

**Epic**: Modern, streamlined experience
- Consumer-friendly design
- Visual hierarchy with panels
- Activity-based workflow

---

## Implementation Specifications

### Component Hierarchy

```
<EpicEHRApp>
  ├── <EpicIconBar />
  ├── <EpicPatientBanner />
  └── <EpicWorkspace>
      ├── <EpicTabBar />
      └── <EpicPanelLayout>
          ├── <EpicLeftPanel>
          │   ├── <EpicNoteComposer />      (if tab='notes')
          │   ├── <EpicMedicationPanel />   (if tab='meds')
          │   └── <EpicOrderPanel />        (if tab='orders')
          ├── <EpicResizeHandle />
          └── <EpicRightPanel>
              └── <EpicClinicalSummary />
```

### State Management (Zustand)

```typescript
interface EpicEHRState {
  // Navigation
  activeView: string;
  activeTab: string;

  // Layout
  leftPanelWidth: number;

  // Session
  sessionId: string | null;
  patient: Patient | null;

  // Content
  currentNote: Partial<Note>;
  currentOrders: Order[];

  // Actions
  setActiveView: (view: string) => void;
  setActiveTab: (tab: string) => void;
  setLeftPanelWidth: (width: number) => void;
  updateNote: (section: string, content: string) => void;
  addOrder: (order: Order) => void;
}
```

### Responsive Breakpoints

```css
/* Epic Responsive Design */
@media (max-width: 1440px) {
  .epic-panel-layout {
    /* Stack panels vertically on smaller screens */
    flex-direction: column;
  }

  .epic-panel-left,
  .epic-panel-right {
    width: 100% !important;
  }
}

@media (max-width: 1024px) {
  .epic-icon-bar {
    width: 60px;
  }

  .epic-icon-label {
    display: none;
  }
}

@media (max-width: 768px) {
  .epic-tab-bar {
    overflow-x: auto;
  }

  .epic-form-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## Implementation Checklist

### Epic UI Components
- [ ] EpicIconBar with icon navigation
- [ ] EpicPatientBanner with allergy alerts
- [ ] EpicWorkspacePanel with tab bar
- [ ] EpicNoteComposer with templates
- [ ] EpicMedicationPanel with PBS search
- [ ] EpicOrderPanel for pathology
- [ ] EpicClinicalSummary sidebar
- [ ] EpicResizeHandle for panels

### Styling & Theming
- [ ] Epic purple color palette
- [ ] Inter font typography
- [ ] Light theme backgrounds
- [ ] Purple accent colors
- [ ] Smooth transitions and animations
- [ ] Responsive breakpoints

### Interactions
- [ ] Icon bar navigation
- [ ] Tab switching
- [ ] Panel resizing
- [ ] Note template selection
- [ ] PBS medication search
- [ ] Form validation
- [ ] Auto-save functionality

### Integration
- [ ] Share state with Cerner theme toggle
- [ ] Unified validation system
- [ ] Consistent session management
- [ ] Shared patient data
- [ ] Common authentication

---

**Document Version**: 1.0
**Last Updated**: 2026-02-02
**Status**: ✅ Ready for Implementation
**Estimated Implementation Time**: 35-40 hours

