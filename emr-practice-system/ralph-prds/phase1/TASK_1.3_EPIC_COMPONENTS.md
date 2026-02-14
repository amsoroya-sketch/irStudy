# TASK 1.3: Epic EHR Components

**Task ID**: TASK_1.3
**Phase**: Phase 1 - Frontend Foundation
**Estimated Time**: 12 hours
**Prerequisites**: TASK_1.1 (Project Setup)
**Dependencies**: React 18, TypeScript, Tailwind CSS, Framer Motion, React Hook Form, Zod

---

## Overview

Create Epic EHR UI components following Epic's design language (light theme, purple accents, clean interface). These components will provide the practice environment for Epic EHR documentation.

**Reference**: See `/home/dev/Development/irStudy/emr-practice-system/design-specs/EPIC_EHR_UI_PRD.md` for full design specifications.

---

## Components to Build

### 1. EpicSidebar Component (3 hours)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/components/epic/EpicSidebar.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import {
  ClipboardList,
  FileText,
  Pill,
  Activity,
  FlaskConical,
  Clock,
  Settings,
  ChevronRight,
  User
} from 'lucide-react';
import { motion } from 'framer-motion';

interface EpicSidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  sessionId?: string;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  badge?: number;
}

export const EpicSidebar: React.FC<EpicSidebarProps> = ({
  currentPath,
  onNavigate,
  sessionId
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['chart']));

  // Timer for session tracking
  useEffect(() => {
    if (!sessionId) return;

    const interval = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [sessionId]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const navigationItems: NavItem[] = [
    {
      id: 'notes',
      label: 'Notes',
      icon: <FileText size={20} />,
      path: '/epic/notes'
    },
    {
      id: 'orders',
      label: 'Orders',
      icon: <ClipboardList size={20} />,
      path: '/epic/orders',
      badge: 0
    },
    {
      id: 'medications',
      label: 'Medications',
      icon: <Pill size={20} />,
      path: '/epic/medications'
    },
    {
      id: 'results',
      label: 'Results',
      icon: <FlaskConical size={20} />,
      path: '/epic/results'
    },
    {
      id: 'flowsheet',
      label: 'Flowsheet',
      icon: <Activity size={20} />,
      path: '/epic/flowsheet'
    }
  ];

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  return (
    <div className="epic-sidebar">
      {/* Patient Context Bar */}
      <div className="epic-sidebar-patient">
        <div className="flex items-center gap-3">
          <div className="epic-patient-avatar">
            <User size={20} />
          </div>
          <div className="flex-1">
            <div className="epic-patient-name">Smith, John</div>
            <div className="epic-patient-mrn">MRN: 12345678</div>
          </div>
        </div>
      </div>

      {/* Session Timer */}
      {sessionId && (
        <div className="epic-timer">
          <Clock size={16} className="text-epic-primary" />
          <span className="epic-timer-text">{formatTime(elapsedTime)}</span>
        </div>
      )}

      {/* Navigation Sections */}
      <nav className="epic-nav">
        <div className="epic-nav-section">
          <button
            className="epic-nav-section-header"
            onClick={() => toggleSection('chart')}
          >
            <ChevronRight
              size={16}
              className={`epic-nav-chevron ${expandedSections.has('chart') ? 'expanded' : ''}`}
            />
            <span>Chart Review</span>
          </button>

          {expandedSections.has('chart') && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="epic-nav-items"
            >
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.path)}
                  className={`epic-nav-item ${
                    currentPath === item.path ? 'active' : ''
                  }`}
                >
                  <span className="epic-nav-icon">{item.icon}</span>
                  <span className="epic-nav-label">{item.label}</span>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span className="epic-nav-badge">{item.badge}</span>
                  )}
                </button>
              ))}
            </motion.div>
          )}
        </div>
      </nav>

      {/* Settings Button */}
      <div className="epic-sidebar-footer">
        <button className="epic-settings-btn">
          <Settings size={18} />
          <span>Settings</span>
        </button>
      </div>
    </div>
  );
};
```

**CSS** (add to `/home/dev/Development/irStudy/emr-frontend/src/index.css`):

```css
/* Epic Sidebar Styles */
.epic-sidebar {
  @apply w-64 bg-white border-r border-gray-200 flex flex-col h-screen;
}

.epic-sidebar-patient {
  @apply p-4 border-b border-gray-200 bg-gradient-to-r from-epic-bg-light to-white;
}

.epic-patient-avatar {
  @apply w-10 h-10 rounded-full bg-epic-primary/10 flex items-center justify-center text-epic-primary;
}

.epic-patient-name {
  @apply text-sm font-semibold text-gray-900;
}

.epic-patient-mrn {
  @apply text-xs text-gray-500;
}

.epic-timer {
  @apply flex items-center justify-center gap-2 py-3 px-4 bg-epic-bg-light border-b border-gray-200;
}

.epic-timer-text {
  @apply text-sm font-mono font-semibold text-gray-700;
}

.epic-nav {
  @apply flex-1 overflow-y-auto py-2;
}

.epic-nav-section {
  @apply mb-1;
}

.epic-nav-section-header {
  @apply w-full flex items-center gap-2 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors;
}

.epic-nav-chevron {
  @apply transition-transform duration-200;
}

.epic-nav-chevron.expanded {
  @apply rotate-90;
}

.epic-nav-items {
  @apply pl-4;
}

.epic-nav-item {
  @apply w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-epic-bg-light hover:text-epic-primary transition-all rounded-r-lg my-0.5;
}

.epic-nav-item.active {
  @apply bg-epic-primary/10 text-epic-primary font-semibold border-l-3 border-epic-primary;
}

.epic-nav-icon {
  @apply flex-shrink-0;
}

.epic-nav-label {
  @apply flex-1;
}

.epic-nav-badge {
  @apply bg-epic-primary text-white text-xs font-bold px-2 py-0.5 rounded-full min-w-[1.25rem] text-center;
}

.epic-sidebar-footer {
  @apply p-4 border-t border-gray-200;
}

.epic-settings-btn {
  @apply w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors;
}
```

---

### 2. EpicPatientBanner Component (3 hours)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/components/epic/EpicPatientBanner.tsx`

```typescript
import React from 'react';
import { AlertCircle, Calendar, MapPin, Phone } from 'lucide-react';
import { motion } from 'framer-motion';

interface PatientData {
  firstName: string;
  lastName: string;
  mrn: string;
  dob: string; // ISO date string
  age: number;
  gender: 'M' | 'F' | 'Other';
  allergies: string[];
  alerts: string[];
  contact: {
    phone?: string;
    address?: string;
  };
}

interface EpicPatientBannerProps {
  patient: PatientData;
  encounterType?: string;
  location?: string;
}

export const EpicPatientBanner: React.FC<EpicPatientBannerProps> = ({
  patient,
  encounterType = 'Outpatient Visit',
  location = 'General Medicine Clinic'
}) => {
  const calculateAge = (dob: string): string => {
    const birthDate = new Date(dob);
    const today = new Date();
    const years = today.getFullYear() - birthDate.getFullYear();
    const months = today.getMonth() - birthDate.getMonth();

    if (years < 2) {
      const totalMonths = years * 12 + months;
      return `${totalMonths} mo`;
    }
    return `${years} y`;
  };

  const formatDOB = (dob: string): string => {
    return new Date(dob).toLocaleDateString('en-AU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <div className="epic-patient-banner">
      {/* Main Patient Info */}
      <div className="epic-banner-main">
        <div className="epic-banner-name">
          {patient.lastName.toUpperCase()}, {patient.firstName}
        </div>
        <div className="epic-banner-demographics">
          <span className="epic-demo-item">
            <Calendar size={14} />
            {formatDOB(patient.dob)} ({calculateAge(patient.dob)})
          </span>
          <span className="epic-demo-divider">•</span>
          <span className="epic-demo-item">
            {patient.gender === 'M' ? 'Male' : patient.gender === 'F' ? 'Female' : 'Other'}
          </span>
          <span className="epic-demo-divider">•</span>
          <span className="epic-demo-item">MRN: {patient.mrn}</span>
        </div>
      </div>

      {/* Encounter Info */}
      <div className="epic-banner-encounter">
        <div className="epic-encounter-type">{encounterType}</div>
        <div className="epic-encounter-location">
          <MapPin size={14} />
          {location}
        </div>
      </div>

      {/* Alerts and Allergies */}
      {(patient.allergies.length > 0 || patient.alerts.length > 0) && (
        <div className="epic-banner-alerts">
          {patient.allergies.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="epic-alert epic-alert-allergy"
            >
              <AlertCircle size={16} />
              <span className="epic-alert-label">Allergies:</span>
              <span className="epic-alert-value">
                {patient.allergies.join(', ')}
              </span>
            </motion.div>
          )}

          {patient.alerts.map((alert, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="epic-alert epic-alert-warning"
            >
              <AlertCircle size={16} />
              <span className="epic-alert-value">{alert}</span>
            </motion.div>
          ))}
        </div>
      )}

      {/* Contact Info (Collapsible) */}
      {patient.contact.phone && (
        <div className="epic-banner-contact">
          <Phone size={14} />
          <span>{patient.contact.phone}</span>
        </div>
      )}
    </div>
  );
};
```

**CSS**:

```css
/* Epic Patient Banner Styles */
.epic-patient-banner {
  @apply bg-white border-b-2 border-epic-primary shadow-sm;
}

.epic-banner-main {
  @apply px-6 py-3 bg-gradient-to-r from-epic-bg-light to-white;
}

.epic-banner-name {
  @apply text-xl font-bold text-gray-900 mb-1;
}

.epic-banner-demographics {
  @apply flex items-center gap-2 text-sm text-gray-600;
}

.epic-demo-item {
  @apply flex items-center gap-1;
}

.epic-demo-divider {
  @apply text-gray-400;
}

.epic-banner-encounter {
  @apply px-6 py-2 bg-white flex items-center gap-4 border-b border-gray-200;
}

.epic-encounter-type {
  @apply text-sm font-semibold text-epic-primary;
}

.epic-encounter-location {
  @apply flex items-center gap-1 text-sm text-gray-600;
}

.epic-banner-alerts {
  @apply px-6 py-2 bg-amber-50 border-b border-amber-200 space-y-1;
}

.epic-alert {
  @apply flex items-center gap-2 text-sm;
}

.epic-alert-allergy {
  @apply text-red-700;
}

.epic-alert-warning {
  @apply text-amber-700;
}

.epic-alert-label {
  @apply font-semibold;
}

.epic-alert-value {
  @apply font-medium;
}

.epic-banner-contact {
  @apply px-6 py-2 bg-gray-50 flex items-center gap-2 text-sm text-gray-600;
}
```

---

### 3. EpicNoteEditor Component (6 hours)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/components/epic/EpicNoteEditor.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Save, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Zod Schema for Epic Note Validation
const epicNoteSchema = z.object({
  chiefComplaint: z.string().min(5, 'Chief complaint must be at least 5 characters'),
  hpi: z.string().min(50, 'HPI must be at least 50 characters'),
  reviewOfSystems: z.object({
    constitutional: z.string().optional(),
    cardiovascular: z.string().optional(),
    respiratory: z.string().optional(),
    gastrointestinal: z.string().optional(),
    genitourinary: z.string().optional(),
    musculoskeletal: z.string().optional(),
    neurological: z.string().optional(),
    psychiatric: z.string().optional(),
    skin: z.string().optional(),
    endocrine: z.string().optional(),
  }),
  physicalExam: z.object({
    general: z.string().min(10, 'General exam required'),
    vitals: z.object({
      temperature: z.number().min(35).max(42),
      heartRate: z.number().min(40).max(200),
      bloodPressureSystolic: z.number().min(60).max(250),
      bloodPressureDiastolic: z.number().min(40).max(150),
      respiratoryRate: z.number().min(8).max(40),
      oxygenSaturation: z.number().min(70).max(100),
    }),
    systemExams: z.string().min(20, 'Detailed physical exam required'),
  }),
  assessment: z.string().min(30, 'Assessment must be at least 30 characters'),
  plan: z.string().min(50, 'Plan must be at least 50 characters'),
});

type EpicNoteFormData = z.infer<typeof epicNoteSchema>;

interface EpicNoteEditorProps {
  sessionId: string;
  onSave?: (data: EpicNoteFormData) => Promise<void>;
  initialData?: Partial<EpicNoteFormData>;
  autoSaveInterval?: number; // seconds, default 30
}

type AutoSaveStatus = 'saved' | 'saving' | 'unsaved' | 'error';

export const EpicNoteEditor: React.FC<EpicNoteEditorProps> = ({
  sessionId,
  onSave,
  initialData,
  autoSaveInterval = 30
}) => {
  const [autoSaveStatus, setAutoSaveStatus] = useState<AutoSaveStatus>('saved');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [activeSection, setActiveSection] = useState<string>('hpi');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isDirty },
    reset
  } = useForm<EpicNoteFormData>({
    resolver: zodResolver(epicNoteSchema),
    defaultValues: initialData || {
      chiefComplaint: '',
      hpi: '',
      reviewOfSystems: {},
      physicalExam: {
        general: '',
        vitals: {
          temperature: 37.0,
          heartRate: 75,
          bloodPressureSystolic: 120,
          bloodPressureDiastolic: 80,
          respiratoryRate: 16,
          oxygenSaturation: 98,
        },
        systemExams: '',
      },
      assessment: '',
      plan: '',
    }
  });

  // Watch for changes to trigger auto-save
  const formData = watch();

  useEffect(() => {
    if (isDirty) {
      setAutoSaveStatus('unsaved');
    }
  }, [formData, isDirty]);

  // Auto-save functionality
  useEffect(() => {
    const autoSaveTimer = setInterval(async () => {
      if (autoSaveStatus === 'unsaved' && onSave) {
        setAutoSaveStatus('saving');
        try {
          await handleSubmit(async (data) => {
            await onSave(data);
            setAutoSaveStatus('saved');
            setLastSaved(new Date());
          })();
        } catch (error) {
          setAutoSaveStatus('error');
          console.error('Auto-save failed:', error);
        }
      }
    }, autoSaveInterval * 1000);

    return () => clearInterval(autoSaveTimer);
  }, [autoSaveStatus, autoSaveInterval, handleSubmit, onSave]);

  const manualSave = async () => {
    setAutoSaveStatus('saving');
    try {
      await handleSubmit(async (data) => {
        if (onSave) {
          await onSave(data);
        }
        setAutoSaveStatus('saved');
        setLastSaved(new Date());
      })();
    } catch (error) {
      setAutoSaveStatus('error');
    }
  };

  const sections = [
    { id: 'hpi', label: 'HPI' },
    { id: 'ros', label: 'Review of Systems' },
    { id: 'exam', label: 'Physical Exam' },
    { id: 'assessment', label: 'Assessment' },
    { id: 'plan', label: 'Plan' },
  ];

  return (
    <div className="epic-note-editor">
      {/* Note Header */}
      <div className="epic-note-header">
        <div className="epic-note-title">Progress Note</div>
        <div className="epic-note-actions">
          {/* Auto-save Status */}
          <div className="epic-autosave-status">
            <AnimatePresence mode="wait">
              {autoSaveStatus === 'saved' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-2 text-green-600"
                >
                  <CheckCircle size={16} />
                  <span className="text-sm">
                    Saved {lastSaved && `at ${lastSaved.toLocaleTimeString()}`}
                  </span>
                </motion.div>
              )}
              {autoSaveStatus === 'saving' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-2 text-blue-600"
                >
                  <Clock size={16} className="animate-spin" />
                  <span className="text-sm">Saving...</span>
                </motion.div>
              )}
              {autoSaveStatus === 'unsaved' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-2 text-amber-600"
                >
                  <AlertCircle size={16} />
                  <span className="text-sm">Unsaved changes</span>
                </motion.div>
              )}
              {autoSaveStatus === 'error' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-2 text-red-600"
                >
                  <AlertCircle size={16} />
                  <span className="text-sm">Save failed</span>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <button
            onClick={manualSave}
            className="epic-save-btn"
            disabled={autoSaveStatus === 'saving'}
          >
            <Save size={18} />
            <span>Save Note</span>
          </button>
        </div>
      </div>

      {/* Section Tabs */}
      <div className="epic-note-tabs">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`epic-tab ${activeSection === section.id ? 'active' : ''}`}
          >
            {section.label}
          </button>
        ))}
      </div>

      {/* Note Content */}
      <form className="epic-note-content">
        {/* Chief Complaint */}
        <div className="epic-form-group">
          <label className="epic-label">Chief Complaint</label>
          <input
            type="text"
            {...register('chiefComplaint')}
            className="epic-input"
            placeholder="Enter chief complaint..."
          />
          {errors.chiefComplaint && (
            <span className="epic-error">{errors.chiefComplaint.message}</span>
          )}
        </div>

        {/* HPI Section */}
        {activeSection === 'hpi' && (
          <div className="epic-form-group">
            <label className="epic-label">History of Present Illness</label>
            <textarea
              {...register('hpi')}
              className="epic-textarea"
              rows={8}
              placeholder="Document the history of present illness..."
            />
            {errors.hpi && (
              <span className="epic-error">{errors.hpi.message}</span>
            )}
          </div>
        )}

        {/* Review of Systems */}
        {activeSection === 'ros' && (
          <div className="epic-ros-grid">
            {Object.keys(epicNoteSchema.shape.reviewOfSystems.shape).map((system) => (
              <div key={system} className="epic-form-group">
                <label className="epic-label capitalize">{system}</label>
                <textarea
                  {...register(`reviewOfSystems.${system}` as any)}
                  className="epic-textarea-sm"
                  rows={3}
                  placeholder={`Document ${system} review...`}
                />
              </div>
            ))}
          </div>
        )}

        {/* Physical Exam */}
        {activeSection === 'exam' && (
          <>
            <div className="epic-vitals-grid">
              <div className="epic-form-group">
                <label className="epic-label">Temp (°C)</label>
                <input
                  type="number"
                  step="0.1"
                  {...register('physicalExam.vitals.temperature', { valueAsNumber: true })}
                  className="epic-input-sm"
                />
              </div>
              <div className="epic-form-group">
                <label className="epic-label">HR (bpm)</label>
                <input
                  type="number"
                  {...register('physicalExam.vitals.heartRate', { valueAsNumber: true })}
                  className="epic-input-sm"
                />
              </div>
              <div className="epic-form-group">
                <label className="epic-label">BP Sys (mmHg)</label>
                <input
                  type="number"
                  {...register('physicalExam.vitals.bloodPressureSystolic', { valueAsNumber: true })}
                  className="epic-input-sm"
                />
              </div>
              <div className="epic-form-group">
                <label className="epic-label">BP Dia (mmHg)</label>
                <input
                  type="number"
                  {...register('physicalExam.vitals.bloodPressureDiastolic', { valueAsNumber: true })}
                  className="epic-input-sm"
                />
              </div>
              <div className="epic-form-group">
                <label className="epic-label">RR (bpm)</label>
                <input
                  type="number"
                  {...register('physicalExam.vitals.respiratoryRate', { valueAsNumber: true })}
                  className="epic-input-sm"
                />
              </div>
              <div className="epic-form-group">
                <label className="epic-label">SpO₂ (%)</label>
                <input
                  type="number"
                  {...register('physicalExam.vitals.oxygenSaturation', { valueAsNumber: true })}
                  className="epic-input-sm"
                />
              </div>
            </div>

            <div className="epic-form-group">
              <label className="epic-label">General Appearance</label>
              <textarea
                {...register('physicalExam.general')}
                className="epic-textarea"
                rows={3}
                placeholder="Document general appearance..."
              />
              {errors.physicalExam?.general && (
                <span className="epic-error">{errors.physicalExam.general.message}</span>
              )}
            </div>

            <div className="epic-form-group">
              <label className="epic-label">Detailed System Examination</label>
              <textarea
                {...register('physicalExam.systemExams')}
                className="epic-textarea"
                rows={8}
                placeholder="Document detailed physical examination findings..."
              />
              {errors.physicalExam?.systemExams && (
                <span className="epic-error">{errors.physicalExam.systemExams.message}</span>
              )}
            </div>
          </>
        )}

        {/* Assessment */}
        {activeSection === 'assessment' && (
          <div className="epic-form-group">
            <label className="epic-label">Assessment</label>
            <textarea
              {...register('assessment')}
              className="epic-textarea"
              rows={8}
              placeholder="Document clinical assessment and differential diagnosis..."
            />
            {errors.assessment && (
              <span className="epic-error">{errors.assessment.message}</span>
            )}
          </div>
        )}

        {/* Plan */}
        {activeSection === 'plan' && (
          <div className="epic-form-group">
            <label className="epic-label">Plan</label>
            <textarea
              {...register('plan')}
              className="epic-textarea"
              rows={8}
              placeholder="Document management plan..."
            />
            {errors.plan && (
              <span className="epic-error">{errors.plan.message}</span>
            )}
          </div>
        )}
      </form>
    </div>
  );
};
```

**CSS**:

```css
/* Epic Note Editor Styles */
.epic-note-editor {
  @apply bg-white rounded-lg shadow-lg h-full flex flex-col;
}

.epic-note-header {
  @apply px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-epic-bg-light;
}

.epic-note-title {
  @apply text-xl font-bold text-gray-900;
}

.epic-note-actions {
  @apply flex items-center gap-4;
}

.epic-autosave-status {
  @apply min-w-[150px];
}

.epic-save-btn {
  @apply flex items-center gap-2 px-4 py-2 bg-epic-primary text-white rounded-lg hover:bg-epic-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.epic-note-tabs {
  @apply flex border-b border-gray-200 bg-gray-50 px-4;
}

.epic-tab {
  @apply px-4 py-3 text-sm font-medium text-gray-600 hover:text-epic-primary hover:bg-white transition-all border-b-2 border-transparent;
}

.epic-tab.active {
  @apply text-epic-primary bg-white border-epic-primary;
}

.epic-note-content {
  @apply flex-1 overflow-y-auto p-6 space-y-6;
}

.epic-form-group {
  @apply space-y-2;
}

.epic-label {
  @apply block text-sm font-semibold text-gray-700;
}

.epic-input {
  @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-epic-primary focus:border-transparent transition-all;
}

.epic-input-sm {
  @apply w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-epic-primary focus:border-transparent transition-all;
}

.epic-textarea {
  @apply w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-epic-primary focus:border-transparent transition-all resize-none;
}

.epic-textarea-sm {
  @apply w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-epic-primary focus:border-transparent transition-all resize-none;
}

.epic-error {
  @apply text-sm text-red-600 font-medium;
}

.epic-ros-grid {
  @apply grid grid-cols-2 gap-4;
}

.epic-vitals-grid {
  @apply grid grid-cols-3 gap-4 p-4 bg-epic-bg-light rounded-lg border border-gray-200;
}
```

---

## Testing

**Test Page**: `/home/dev/Development/irStudy/emr-frontend/src/pages/epic/EpicTest.tsx`

```typescript
import React from 'react';
import { EpicSidebar } from '@components/epic/EpicSidebar';
import { EpicPatientBanner } from '@components/epic/EpicPatientBanner';
import { EpicNoteEditor } from '@components/epic/EpicNoteEditor';

export const EpicTest: React.FC = () => {
  const mockPatient = {
    firstName: 'John',
    lastName: 'Smith',
    mrn: '12345678',
    dob: '1980-05-15',
    age: 44,
    gender: 'M' as const,
    allergies: ['Penicillin', 'Sulfa drugs'],
    alerts: ['Fall risk', 'DNR on file'],
    contact: {
      phone: '02 9876 5432',
      address: '123 Main St, Sydney NSW 2000'
    }
  };

  const handleSave = async (data: any) => {
    console.log('Saving note:', data);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
  };

  return (
    <div className="flex h-screen" data-theme="epic">
      <EpicSidebar
        currentPath="/epic/notes"
        onNavigate={(path) => console.log('Navigate to:', path)}
        sessionId="test-session-123"
      />
      <div className="flex-1 flex flex-col">
        <EpicPatientBanner patient={mockPatient} />
        <div className="flex-1 p-6 bg-gray-50">
          <EpicNoteEditor
            sessionId="test-session-123"
            onSave={handleSave}
            autoSaveInterval={10}
          />
        </div>
      </div>
    </div>
  );
};
```

---

## Validation Checklist

Before marking this task complete, verify:

- [ ] All 3 Epic components render without errors
- [ ] Epic theme colors applied correctly (purple accents, light background)
- [ ] EpicSidebar navigation works with active states
- [ ] Session timer counts up correctly
- [ ] EpicPatientBanner displays all patient data
- [ ] Allergies and alerts show with proper styling
- [ ] EpicNoteEditor tabs switch between sections
- [ ] Form validation works (Zod schema)
- [ ] Auto-save triggers every 30 seconds
- [ ] Manual save button works
- [ ] Auto-save status updates correctly
- [ ] Vital signs accept numeric input only
- [ ] All error messages display for invalid inputs
- [ ] Components are responsive
- [ ] TypeScript shows no errors
- [ ] CSS classes follow Epic design system

---

## Time Breakdown

- EpicSidebar: 3 hours
- EpicPatientBanner: 3 hours
- EpicNoteEditor: 6 hours
- **Total**: 12 hours

---

## Next Steps

After completing this task:
1. Proceed to **TASK_1.4_STATE_MANAGEMENT.md** (Zustand stores)
2. Then **TASK_1.5_CUSTOM_HOOKS.md** (Custom React hooks)

---

**Last Updated**: 2026-02-03
**Status**: Ready for Implementation
