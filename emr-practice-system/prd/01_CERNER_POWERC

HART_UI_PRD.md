# Cerner PowerChart UI Simulation - Detailed PRD

**Component:** Cerner PowerChart Interface
**Version:** 1.0
**Date:** 2026-02-02
**Dependencies:** Main EMR PRD

---

## Overview

Create pixel-perfect simulation of Cerner PowerChart interface used in Australian hospitals (Young District Hospital, Western NSW LHD, and similar facilities).

### Design Goals
1. **Authenticity:** 95%+ visual similarity to real Cerner PowerChart
2. **Usability:** Intuitive navigation for users unfamiliar with EMR
3. **Performance:** < 2s page load, smooth transitions
4. **Responsive:** Desktop-first (1920x1080), tablet support (1024x768)

---

## UI Components Specification

### 1. Cerner Sidebar (Primary Navigation)

#### Visual Design
```
┌─────────────────────┐
│ [C] PowerChart      │  ← Header (dark gray #2c3e50)
│  irStudy Simulation │
├─────────────────────┤
│ [🏠] Dashboard      │  ← Nav item (hover: #34495e)
│ [👤] Patient Chart  │
│ [📝] Progress Note  │  ← Active (blue border-left #3498db)
│ [💊] Medications    │
│ [🧪] Orders         │
│ [❤️] Vital Signs    │
│ [⚠️] Alerts         │
├─────────────────────┤
│ Session: SIM-12345  │  ← Footer (timestamp, session ID)
│ Time: 14:32         │
└─────────────────────┘
```

#### Technical Specs
```typescript
interface CernerSidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  sessionId: string;
}

const navItems = [
  {
    id: 'dashboard',
    path: '/cerner',
    icon: Home,
    label: 'Dashboard',
    color: 'text-blue-600'
  },
  {
    id: 'patient',
    path: '/cerner/patient',
    icon: User,
    label: 'Patient Chart',
    color: 'text-green-600'
  },
  {
    id: 'soap',
    path: '/cerner/soap',
    icon: FileText,
    label: 'Progress Note',
    color: 'text-purple-600'
  },
  {
    id: 'medications',
    path: '/cerner/medications',
    icon: Pill,
    label: 'Medications',
    color: 'text-orange-600'
  },
  {
    id: 'orders',
    path: '/cerner/orders',
    icon: FlaskConical,
    label: 'Orders',
    color: 'text-red-600'
  },
  {
    id: 'vitals',
    path: '/cerner/vitals',
    icon: Activity,
    label: 'Vital Signs',
    color: 'text-teal-600'
  },
  {
    id: 'alerts',
    path: '/cerner/alerts',
    icon: AlertCircle,
    label: 'Alerts',
    color: 'text-yellow-600'
  }
];
```

#### CSS Styling
```css
.cerner-sidebar {
  width: 256px;
  height: 100vh;
  background: #2c3e50;
  color: #ecf0f1;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.cerner-sidebar-header {
  padding: 1rem;
  background: #1a252f;
  border-bottom: 1px solid #34495e;
}

.cerner-nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background 0.2s;
  border-left: 4px solid transparent;
}

.cerner-nav-item:hover {
  background: #34495e;
}

.cerner-nav-item.active {
  background: #34495e;
  border-left-color: #3498db;
}

.cerner-sidebar-footer {
  margin-top: auto;
  padding: 1rem;
  background: #1a252f;
  border-top: 1px solid #34495e;
  font-size: 0.75rem;
  color: #95a5a6;
}
```

---

### 2. Patient Banner (Top Bar)

#### Visual Design
```
┌────────────────────────────────────────────────────────────────────────┐
│ SMITH, John (M, 67y)  |  MRN: 1234567  |  DOB: 15/03/1957  |  Ward: 2B│
│ ⚠️ ALLERGIES: Penicillin (Anaphylaxis), Shellfish (Rash)              │
└────────────────────────────────────────────────────────────────────────┘
```

#### Component Structure
```typescript
interface PatientBannerProps {
  patient: {
    firstName: string;
    lastName: string;
    gender: 'M' | 'F' | 'Other';
    age: number;
    mrn: string;
    dob: string;
    ward?: string;
    allergies: Allergy[];
  };
}

const PatientBanner: React.FC<PatientBannerProps> = ({ patient }) => {
  const hasAllergies = patient.allergies.length > 0;

  return (
    <div className="patient-banner">
      <div className="patient-demographics">
        <span className="patient-name">
          {patient.lastName.toUpperCase()}, {patient.firstName}
        </span>
        <span className="patient-gender">({patient.gender})</span>
        <span className="patient-age">{patient.age}y</span>
        <span className="divider">|</span>
        <span>MRN: {patient.mrn}</span>
        <span className="divider">|</span>
        <span>DOB: {format(patient.dob, 'dd/MM/yyyy')}</span>
        {patient.ward && (
          <>
            <span className="divider">|</span>
            <span>Ward: {patient.ward}</span>
          </>
        )}
      </div>

      {hasAllergies && (
        <div className="patient-allergies">
          <AlertTriangle className="text-red-600" size={16} />
          <span className="font-semibold">ALLERGIES:</span>
          {patient.allergies.map((allergy, index) => (
            <span key={index}>
              {allergy.allergen} ({allergy.reaction})
              {index < patient.allergies.length - 1 && ', '}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
```

#### CSS Styling
```css
.patient-banner {
  background: #ecf0f1;
  border-bottom: 3px solid #3498db;
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
}

.patient-demographics {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.patient-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: #2c3e50;
}

.patient-allergies {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #fee;
  border: 2px solid #e74c3c;
  border-radius: 4px;
  color: #c0392b;
  font-weight: 600;
}

.divider {
  color: #95a5a6;
  margin: 0 0.5rem;
}
```

---

### 3. Progress Note Editor (SOAP Format)

#### Visual Design
```
┌──────────────────────────────────────────────────────────────────┐
│ Progress Note - SOAP Format                          [Save Draft] │
│ Document patient encounter following SOAP structure   [Submit]    │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│ Subjective  (Patient's description, symptoms, history)            │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ [Type here...]                                                │ │
│ │                                                                │ │
│ │                                                                │ │
│ └──────────────────────────────────────────────────────────────┘ │
│ ℹ️ Include: Chief complaint, HPI, relevant PMHx                   │
│ Character count: 0/2000 | Word count: 0 | Min: 50 chars         │
│                                                                    │
│ Objective  (Clinical findings, vital signs, examination)          │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │                                                                │ │
│ └──────────────────────────────────────────────────────────────┘ │
│ ℹ️ Include: Vital signs, physical examination findings           │
│                                                                    │
│ Assessment  (Diagnosis, differential, problem list)               │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │                                                                │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ Plan  (Management, investigations, follow-up)                     │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │                                                                │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ [⬅️ Back]  [💾 Save Draft]  [🚀 Submit for AI Validation]       │
└──────────────────────────────────────────────────────────────────┘
```

#### Component Implementation
```typescript
interface ProgressNoteEditorProps {
  patientId: string;
  sessionId: string;
  initialData?: Partial<SOAPNote>;
  onSave: (note: SOAPNote) => Promise<void>;
  onSubmit: (note: SOAPNote) => Promise<ValidationResult>;
}

const ProgressNoteEditor: React.FC<ProgressNoteEditorProps> = ({
  patientId,
  sessionId,
  initialData,
  onSave,
  onSubmit
}) => {
  const [isSaving, setIsSaving] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [typingMetrics, setTypingMetrics] = useState({
    startTime: Date.now(),
    keystrokes: 0,
    wpm: 0
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    getValues
  } = useForm<SOAPNoteFormData>({
    resolver: zodResolver(soapNoteSchema),
    defaultValues: initialData || {
      subjective: '',
      objective: '',
      assessment: '',
      plan: ''
    }
  });

  // Auto-save every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      handleSaveDraft();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // Track typing metrics
  const handleKeyPress = (field: string) => {
    setTypingMetrics(prev => {
      const newKeystrokes = prev.keystrokes + 1;
      const elapsedMinutes = (Date.now() - prev.startTime) / 60000;
      const wpm = Math.round((newKeystrokes / 5) / elapsedMinutes);

      return {
        ...prev,
        keystrokes: newKeystrokes,
        wpm: isNaN(wpm) ? 0 : wpm
      };
    });
  };

  const handleSaveDraft = async () => {
    setIsSaving(true);
    const values = getValues();
    const note: SOAPNote = {
      id: `soap_${Date.now()}`,
      patientId,
      sessionId,
      createdAt: new Date().toISOString(),
      ...values
    };

    await onSave(note);
    setIsSaving(false);
  };

  const handleSubmitForValidation = async (data: SOAPNoteFormData) => {
    setIsSubmitting(true);
    const note: SOAPNote = {
      id: `soap_${Date.now()}`,
      patientId,
      sessionId,
      createdAt: new Date().toISOString(),
      ...data
    };

    const validationResult = await onSubmit(note);
    // Show validation panel
    setIsSubmitting(false);
  };

  const getCharCount = (field: keyof SOAPNoteFormData) => {
    const value = watch(field);
    return value?.length || 0;
  };

  const getWordCount = (field: keyof SOAPNoteFormData) => {
    const value = watch(field);
    return value?.split(/\s+/).filter(Boolean).length || 0;
  };

  return (
    <div className="progress-note-editor">
      {/* Header */}
      <div className="editor-header">
        <div>
          <h2 className="text-xl font-semibold">Progress Note - SOAP Format</h2>
          <p className="text-sm text-gray-600">
            Document patient encounter following SOAP structure
          </p>
        </div>
        <div className="flex items-center gap-2">
          <TypingMetricsBadge wpm={typingMetrics.wpm} />
          {isSaving && <span className="text-sm text-gray-500">Saving...</span>}
        </div>
      </div>

      <form onSubmit={handleSubmit(handleSubmitForValidation)} className="editor-form">
        {/* Subjective Section */}
        <div className="soap-section">
          <label className="section-label">
            Subjective
            <span className="section-hint">
              (Patient's description, symptoms, history)
            </span>
          </label>

          <textarea
            {...register('subjective')}
            onKeyPress={() => handleKeyPress('subjective')}
            rows={6}
            className={`soap-textarea ${errors.subjective ? 'error' : ''}`}
            placeholder="Example: Patient presents with 3-day history of productive cough with green sputum, fever (max 39°C), and shortness of breath on exertion. Reports night sweats. Denies chest pain. No recent travel. Non-smoker. PMHx: Type 2 diabetes (well-controlled on metformin). Allergies: Penicillin (rash)."
          />

          <div className="section-meta">
            <div className="text-info">
              <Info size={14} />
              <span>
                Include: Chief complaint, HPI (onset, duration, severity, aggravating/relieving factors),
                relevant PMHx, medications, allergies, social/family history
              </span>
            </div>
            <div className="char-count">
              Characters: {getCharCount('subjective')}/2000 |
              Words: {getWordCount('subjective')} |
              <span className={getCharCount('subjective') < 50 ? 'text-red-600' : 'text-green-600'}>
                Min: 50 chars
              </span>
            </div>
          </div>

          {errors.subjective && (
            <p className="error-message">{errors.subjective.message}</p>
          )}
        </div>

        {/* Objective Section */}
        <div className="soap-section">
          <label className="section-label">
            Objective
            <span className="section-hint">
              (Clinical findings, vital signs, examination)
            </span>
          </label>

          <textarea
            {...register('objective')}
            onKeyPress={() => handleKeyPress('objective')}
            rows={6}
            className={`soap-textarea ${errors.objective ? 'error' : ''}`}
            placeholder="Example: Vitals: T 38.5°C, HR 102, BP 128/82, RR 24, SpO2 94% on RA. General: Appears unwell, mildly dyspnoeic at rest. Chest: Reduced air entry right lower zone, coarse crackles, dull to percussion right base. CVS: Normal S1/S2, no murmurs. Abdo: Soft, non-tender."
          />

          <div className="section-meta">
            <div className="text-info">
              <Info size={14} />
              <span>
                Include: Vital signs (T, HR, BP, RR, SpO2), general appearance,
                systematic physical examination findings
              </span>
            </div>
            <div className="char-count">
              Characters: {getCharCount('objective')}/2000 |
              Words: {getWordCount('objective')}
            </div>
          </div>

          {errors.objective && (
            <p className="error-message">{errors.objective.message}</p>
          )}
        </div>

        {/* Assessment Section */}
        <div className="soap-section">
          <label className="section-label">
            Assessment
            <span className="section-hint">
              (Diagnosis, differential, problem list)
            </span>
          </label>

          <textarea
            {...register('assessment')}
            onKeyPress={() => handleKeyPress('assessment')}
            rows={5}
            className={`soap-textarea ${errors.assessment ? 'error' : ''}`}
            placeholder="Example: 1. Community-acquired pneumonia (CAP), right lower lobe - most likely bacterial given productive cough, fever, consolidation on examination. CURB-65 score: 1 (low risk). 2. Differential: Atypical pneumonia, bronchitis, pulmonary TB (recent travel). 3. Type 2 diabetes - monitor BSL closely during acute infection."
          />

          <div className="section-meta">
            <div className="text-info">
              <Info size={14} />
              <span>
                Include: Primary diagnosis with justification, 2-3 differential diagnoses,
                severity assessment, impact on existing conditions
              </span>
            </div>
            <div className="char-count">
              Characters: {getCharCount('assessment')}/1000 |
              Words: {getWordCount('assessment')}
            </div>
          </div>

          {errors.assessment && (
            <p className="error-message">{errors.assessment.message}</p>
          )}
        </div>

        {/* Plan Section */}
        <div className="soap-section">
          <label className="section-label">
            Plan
            <span className="section-hint">
              (Management, investigations, follow-up)
            </span>
          </label>

          <textarea
            {...register('plan')}
            onKeyPress={() => handleKeyPress('plan')}
            rows={6}
            className={`soap-textarea ${errors.plan ? 'error' : ''}`}
            placeholder="Example: 1. Investigations: CXR (AP/Lateral), FBC, CRP, U&E, blood cultures. Sputum MCS if productive. 2. Treatment: Commence amoxicillin 1g PO TDS for 5 days (PBS). Paracetamol 1g PO QID PRN. 3. Monitoring: Daily obs, SpO2. IV fluids if poor oral intake. Escalate if worsening dyspnoea or hypoxia. 4. Follow-up: Review in 48h, CXR in 6 weeks to confirm resolution. Safety-net advice: Return if fever persists >48h, worsening SOB, chest pain."
          />

          <div className="section-meta">
            <div className="text-info">
              <Info size={14} />
              <span>
                Include: Investigations to order (with MBS), medications to prescribe (with PBS),
                monitoring plan, follow-up timing, safety-netting advice
              </span>
            </div>
            <div className="char-count">
              Characters: {getCharCount('plan')}/1500 |
              Words: {getWordCount('plan')}
            </div>
          </div>

          {errors.plan && (
            <p className="error-message">{errors.plan.message}</p>
          )}
        </div>

        {/* Action Buttons */}
        <div className="editor-actions">
          <button
            type="button"
            onClick={handleSaveDraft}
            disabled={isSaving}
            className="btn-secondary"
          >
            <Save size={20} />
            {isSaving ? 'Saving...' : 'Save Draft'}
          </button>

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary"
          >
            <Send size={20} />
            {isSubmitting ? 'Submitting...' : 'Submit for AI Validation'}
          </button>
        </div>
      </form>
    </div>
  );
};
```

---

### 4. Medication Order Entry

#### Visual Design
```
┌──────────────────────────────────────────────────────────────┐
│ Medication Order                                   [PBS Help] │
│ PBS-compliant prescriptions                                   │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│ Medication Name *                                             │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 🔍 Search PBS medications...                              │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌─ PBS Search Results ─────────────────────────────────────┐ │
│ │ Amoxicillin 500mg capsules                                │ │
│ │ PBS Code: 2089Y | Unrestricted | $5.60                   │ │
│ ├──────────────────────────────────────────────────────────┤ │
│ │ Amoxicillin/Clavulanic Acid 875/125mg tablets            │ │
│ │ PBS Code: 8601E | Authority Required | $6.80             │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                                │
│ Dose *                    Route *                             │
│ ┌─────────────────────┐   ┌────────────────────┐             │
│ │ 1g                  │   │ PO (Oral) ▾        │             │
│ └─────────────────────┘   └────────────────────┘             │
│                                                                │
│ Frequency *               Duration *                          │
│ ┌─────────────────────┐   ┌────────────────────┐             │
│ │ Three times daily ▾ │   │ 5 days             │             │
│ └─────────────────────┘   └────────────────────┘             │
│                                                                │
│ Quantity *                Repeats                             │
│ ┌─────────────────────┐   ┌────────────────────┐             │
│ │ 15                  │   │ 0                  │             │
│ └─────────────────────┘   └────────────────────┘             │
│                                                                │
│ Indication * (PBS Requirement)                                │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Community-acquired pneumonia                              │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                                │
│ ⚠️ PBS Compliance Check                                       │
│ ✓ Medication is PBS-listed                                   │
│ ✓ Indication matches approved uses                           │
│ ⚠️ Authority may be required for this indication             │
│                                                                │
│ [Cancel]  [Add Prescription]                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Interaction Flows

### Flow 1: Complete SOAP Note
```
1. User clicks "Progress Note" in sidebar
2. System loads Progress Note Editor with patient context
3. User types in all 4 SOAP sections
   - Auto-save runs every 30 seconds
   - Character/word counts update in real-time
   - Typing WPM displayed
4. User clicks "Submit for AI Validation"
5. System shows loading spinner (2-3 seconds)
6. Validation Panel slides in from right
7. User reviews feedback
8. User either:
   - Clicks "Revise" → returns to editor with feedback visible
   - Clicks "Accept" → saves note and returns to dashboard
```

### Flow 2: Order PBS Medication
```
1. User clicks "Medications" in sidebar
2. System shows Medication Order Entry form
3. User types medication name in search box
4. System searches PBS database (debounced, 300ms delay)
5. PBS results appear below search box
6. User clicks desired medication
7. Form pre-fills with PBS data (code, restrictions)
8. User completes: dose, route, frequency, duration, quantity, repeats, indication
9. System validates:
   - PBS compliance check (instant)
   - Dose range check (instant)
   - Allergy check (instant, red alert if match)
   - Drug interaction check (instant, warnings appear)
10. User clicks "Add Prescription"
11. System shows confirmation
12. Prescription added to session, appears in medications list
```

---

## Technical Requirements

### Performance Targets
- Initial load: < 2 seconds
- Search response: < 300ms
- Auto-save: Background, non-blocking
- Validation: < 3 seconds
- Smooth 60fps animations

### Browser Support
- Chrome 100+ (primary)
- Firefox 100+
- Safari 15+
- Edge 100+

### Screen Sizes
- Desktop: 1920x1080 (primary), 1366x768 (min)
- Tablet: 1024x768
- Mobile: Not supported (show desktop warning)

---

## Assets Required

### Icons
- Lucide React icon library (already in use)
- Custom medical icons (heart, lungs, kidney, etc.)

### Fonts
- Inter (UI elements)
- Roboto Mono (SOAP note textarea - medical typing)

### Color Palette
```
Primary Blue: #3498db
Dark Gray: #2c3e50
Light Gray: #ecf0f1
Success Green: #27ae60
Warning Orange: #e67e22
Error Red: #e74c3c
Info Blue: #2980b9
```

---

**Next Document:** 02_EPIC_EHR_UI_PRD.md (Similar detail for Epic interface)
