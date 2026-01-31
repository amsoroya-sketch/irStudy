# Phase 2: Hospital EMR Practice System
**Owner:** Full-Stack Developer
**Duration:** 80-120 hours (4 weeks full-time, 8 weeks part-time)
**Priority:** P1 (High - Clinical documentation skills)
**Status:** Ready to Start (after Phase 1)

---

## 📋 Overview

This phase builds a **Hospital EMR simulation system** that allows medical students to practice clinical documentation skills in realistic Cerner PowerChart and Epic EHR interfaces. Students will practice SOAP notes, prescription writing, and pathology ordering with AI validation against Australian standards (PBS, MBS, eTG).

**Key Achievement:** 80%+ validation accuracy for Australian medical documentation

---

## 🎯 Goals

1. **EMR UI Components** (30 hours)
   - Cerner PowerChart interface (React)
   - Epic EHR interface (React)
   - Multi-tab state management
   - Realistic EMR look and feel

2. **Backend API + Database** (20 hours)
   - FastAPI routes for patient management
   - SQLite schema (patients, sessions, documentation)
   - Alembic migrations
   - CRUD operations

3. **PBS/MBS Integration** (15 hours)
   - Download PBS database (4,000+ medications)
   - Medicare item numbers (MBS)
   - Validation rules
   - Australian-specific logic

4. **AI Validation Agent** (20 hours)
   - SOAP note validation (structure, terminology)
   - Prescription validation (dose, interactions, PBS)
   - Pathology validation (MBS items, indications)
   - Detailed feedback generation

5. **Progress Tracking** (15 hours)
   - Session management
   - Scoring algorithm
   - Performance analytics
   - Feedback UI

6. **Testing** (20 hours)
   - Unit tests (PyTest)
   - E2E tests (Playwright)
   - Validation test cases

---

## ✅ Prerequisites

- [x] Phase 1 completed (React components reusable)
- [x] FastAPI backend foundation
- [x] LLM integration (Claude 3.5 Sonnet)
- [x] RAG system for medical knowledge lookup

---

## 📝 Detailed Task Breakdown

### Task 1: Cerner/Epic UI Components (30 hours)

**Priority:** P0 (CRITICAL - foundation for documentation practice)

**Project Structure:**

```bash
cd /home/dev/Development/irStudy
mkdir -p emr-practice
cd emr-practice

# Create frontend directory
mkdir -p frontend
cd frontend

# Initialize React project
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install
npm install \
  react-router-dom \
  @tanstack/react-query \
  zustand \
  tailwindcss postcss autoprefixer \
  date-fns \
  clsx \
  lucide-react \
  react-hook-form \
  zod \
  @hookform/resolvers

# Initialize Tailwind
npx tailwindcss init -p

# Create directory structure
mkdir -p src/{components,pages,hooks,utils,types,services,store}
mkdir -p src/components/{cerner,epic,common}
mkdir -p src/pages/{dashboard,cerner,epic,analytics}
```

**TypeScript Types:**

```typescript
// src/types/index.ts

export interface SimulatedPatient {
  id: string;
  mrn: string; // Medical Record Number
  name: {
    first: string;
    last: string;
  };
  demographics: {
    dob: string;
    age: number;
    gender: 'Male' | 'Female' | 'Other';
    aboriginalTorresStrait: boolean;
  };
  allergies: Allergy[];
  medications: Medication[];
  medicalHistory: MedicalHistoryItem[];
  vitalSigns: VitalSigns;
  presenting_complaint: string;
  clinical_scenario: string;
}

export interface Allergy {
  allergen: string;
  reaction: string;
  severity: 'Mild' | 'Moderate' | 'Severe';
  verified: boolean;
}

export interface Medication {
  name: string;
  dose: string;
  route: string;
  frequency: string;
  startDate: string;
  indication: string;
}

export interface MedicalHistoryItem {
  condition: string;
  diagnosedDate: string;
  status: 'Active' | 'Resolved' | 'In Remission';
  notes?: string;
}

export interface VitalSigns {
  temperature: number;
  heartRate: number;
  bloodPressure: {
    systolic: number;
    diastolic: number;
  };
  respiratoryRate: number;
  oxygenSaturation: number;
  weight: number;
  height: number;
  bmi: number;
}

export interface SOAPNote {
  id: string;
  patientId: string;
  sessionId: string;
  createdAt: string;
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
}

export interface Prescription {
  id: string;
  patientId: string;
  sessionId: string;
  medication: string;
  dose: string;
  route: string;
  frequency: string;
  duration: string;
  quantity: number;
  repeats: number;
  indication: string;
  pbsCode?: string;
  streamlinedAuthority?: boolean;
}

export interface PathologyOrder {
  id: string;
  patientId: string;
  sessionId: string;
  testType: string;
  mbsItemNumber: string;
  indication: string;
  urgency: 'Routine' | 'Urgent' | 'Emergency';
  clinicalNotes: string;
}

export interface ValidationResult {
  isValid: boolean;
  score: number; // 0-100
  feedback: ValidationFeedback[];
  suggestions: string[];
}

export interface ValidationFeedback {
  field: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  suggestion?: string;
}

export interface EMRSession {
  id: string;
  userId: string;
  patientId: string;
  emrType: 'cerner' | 'epic';
  startTime: string;
  endTime?: string;
  soapNote?: SOAPNote;
  prescriptions: Prescription[];
  pathologyOrders: PathologyOrder[];
  validationResults: {
    soapNote?: ValidationResult;
    prescriptions: Record<string, ValidationResult>;
    pathologyOrders: Record<string, ValidationResult>;
  };
  overallScore?: number;
}
```

**Cerner PowerChart Sidebar:**

```typescript
// src/components/cerner/CernerSidebar.tsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  FileText,
  Pill,
  FlaskConical,
  Activity,
  User,
  AlertCircle
} from 'lucide-react';

const CernerSidebar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/cerner', icon: Home, label: 'Dashboard', color: 'text-blue-600' },
    { path: '/cerner/patient', icon: User, label: 'Patient Chart', color: 'text-green-600' },
    { path: '/cerner/soap', icon: FileText, label: 'Progress Note', color: 'text-purple-600' },
    { path: '/cerner/medications', icon: Pill, label: 'Medications', color: 'text-orange-600' },
    { path: '/cerner/orders', icon: FlaskConical, label: 'Orders', color: 'text-red-600' },
    { path: '/cerner/vitals', icon: Activity, label: 'Vital Signs', color: 'text-teal-600' },
    { path: '/cerner/alerts', icon: AlertCircle, label: 'Alerts', color: 'text-yellow-600' },
  ];

  return (
    <div className="w-64 bg-gray-900 text-white h-screen flex flex-col">
      {/* Header */}
      <div className="p-4 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
            <span className="font-bold text-sm">C</span>
          </div>
          <div>
            <div className="font-semibold">Cerner PowerChart</div>
            <div className="text-xs text-gray-400">irStudy Simulation</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {navItems.map(({ path, icon: Icon, label, color }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-3 px-4 py-3 hover:bg-gray-800 transition-colors ${
                isActive ? 'bg-gray-800 border-l-4 border-blue-500' : ''
              }`}
            >
              <Icon className={isActive ? color : 'text-gray-400'} size={20} />
              <span className={isActive ? 'text-white font-medium' : 'text-gray-300'}>
                {label}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 bg-gray-800 border-t border-gray-700 text-sm text-gray-400">
        <div>Practice Session</div>
        <div className="font-mono text-xs mt-1">ID: SIM-{Date.now().toString().slice(-6)}</div>
      </div>
    </div>
  );
};

export default CernerSidebar;
```

**Cerner Progress Note Editor:**

```typescript
// src/components/cerner/ProgressNoteEditor.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Save, Send, Loader2 } from 'lucide-react';
import { SOAPNote } from '../../types';

const soapNoteSchema = z.object({
  subjective: z.string().min(50, 'Subjective section must be at least 50 characters'),
  objective: z.string().min(50, 'Objective section must be at least 50 characters'),
  assessment: z.string().min(30, 'Assessment section must be at least 30 characters'),
  plan: z.string().min(30, 'Plan section must be at least 30 characters'),
});

type SOAPNoteFormData = z.infer<typeof soapNoteSchema>;

interface ProgressNoteEditorProps {
  patientId: string;
  sessionId: string;
  onSave: (note: SOAPNote) => void;
  onSubmitForValidation: (note: SOAPNote) => void;
}

const ProgressNoteEditor: React.FC<ProgressNoteEditorProps> = ({
  patientId,
  sessionId,
  onSave,
  onSubmitForValidation
}) => {
  const [isSaving, setIsSaving] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues
  } = useForm<SOAPNoteFormData>({
    resolver: zodResolver(soapNoteSchema),
    defaultValues: {
      subjective: '',
      objective: '',
      assessment: '',
      plan: ''
    }
  });

  const handleSaveDraft = () => {
    setIsSaving(true);
    const values = getValues();
    const note: SOAPNote = {
      id: `soap_${Date.now()}`,
      patientId,
      sessionId,
      createdAt: new Date().toISOString(),
      ...values
    };
    onSave(note);
    setTimeout(() => setIsSaving(false), 500);
  };

  const onSubmit = (data: SOAPNoteFormData) => {
    setIsSubmitting(true);
    const note: SOAPNote = {
      id: `soap_${Date.now()}`,
      patientId,
      sessionId,
      createdAt: new Date().toISOString(),
      ...data
    };
    onSubmitForValidation(note);
  };

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
        <h2 className="text-xl font-semibold">Progress Note - SOAP Format</h2>
        <p className="text-sm text-blue-100 mt-1">Document patient encounter following SOAP structure</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
        {/* Subjective Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Subjective
            <span className="text-gray-500 ml-2">(Patient's description, symptoms, history)</span>
          </label>
          <textarea
            {...register('subjective')}
            rows={6}
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm ${
              errors.subjective ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Example: Patient presents with 3-day history of fever (up to 39°C), productive cough with green sputum, and shortness of breath on exertion. Reports night sweats. Denies chest pain. Recently returned from overseas travel..."
          />
          {errors.subjective && (
            <p className="text-red-500 text-sm mt-1">{errors.subjective.message}</p>
          )}
          <p className="text-gray-500 text-xs mt-1">
            Include: Chief complaint, HPI, relevant PMHx, medications, allergies, social/family history
          </p>
        </div>

        {/* Objective Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Objective
            <span className="text-gray-500 ml-2">(Clinical findings, vital signs, examination)</span>
          </label>
          <textarea
            {...register('objective')}
            rows={6}
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm ${
              errors.objective ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Example: Vitals: T 38.5°C, HR 102, BP 128/82, RR 24, SpO2 94% on RA. General: Appears unwell, mildly dyspnoeic. Chest: Crackles at right lower zone, dullness to percussion. Cardiovascular: Normal S1/S2, no murmurs..."
          />
          {errors.objective && (
            <p className="text-red-500 text-sm mt-1">{errors.objective.message}</p>
          )}
          <p className="text-gray-500 text-xs mt-1">
            Include: Vital signs, physical examination findings, relevant investigations
          </p>
        </div>

        {/* Assessment Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Assessment
            <span className="text-gray-500 ml-2">(Diagnosis, differential, problem list)</span>
          </label>
          <textarea
            {...register('assessment')}
            rows={5}
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm ${
              errors.assessment ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Example: 1. Community-acquired pneumonia (CAP), right lower lobe - most likely bacterial (productive cough, fever, crackles). 2. Differential: Atypical pneumonia, bronchitis, pulmonary TB (recent travel). 3. Mild hypoxia requiring monitoring..."
          />
          {errors.assessment && (
            <p className="text-red-500 text-sm mt-1">{errors.assessment.message}</p>
          )}
          <p className="text-gray-500 text-xs mt-1">
            Include: Primary diagnosis, differential diagnoses, severity assessment
          </p>
        </div>

        {/* Plan Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Plan
            <span className="text-gray-500 ml-2">(Management, investigations, follow-up)</span>
          </label>
          <textarea
            {...register('plan')}
            rows={6}
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm ${
              errors.plan ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Example: 1. Investigations: Chest X-ray (AP/Lateral), FBC, CRP, U&E, blood cultures if febrile. Consider sputum culture if productive. 2. Treatment: Commence amoxicillin 1g PO TDS for 5 days (PBS). Paracetamol 1g PO QID PRN fever/pain. 3. Monitoring: Daily vital signs, SpO2. Escalate if worsening dyspnoea. 4. Follow-up: Review in 48 hours or sooner if deterioration..."
          />
          {errors.plan && (
            <p className="text-red-500 text-sm mt-1">{errors.plan.message}</p>
          )}
          <p className="text-gray-500 text-xs mt-1">
            Include: Investigations ordered, medications prescribed, monitoring plan, follow-up
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={handleSaveDraft}
            disabled={isSaving}
            className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50"
          >
            {isSaving ? (
              <Loader2 className="animate-spin" size={20} />
            ) : (
              <Save size={20} />
            )}
            Save Draft
          </button>

          <button
            type="submit"
            disabled={isSubmitting}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {isSubmitting ? (
              <Loader2 className="animate-spin" size={20} />
            ) : (
              <Send size={20} />
            )}
            Submit for AI Validation
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProgressNoteEditor;
```

**Cerner Medication Order Entry:**

```typescript
// src/components/cerner/MedicationOrderEntry.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Search, Plus, AlertTriangle } from 'lucide-react';
import { Prescription } from '../../types';

const prescriptionSchema = z.object({
  medication: z.string().min(2, 'Medication name required'),
  dose: z.string().min(1, 'Dose required'),
  route: z.enum(['PO', 'IV', 'IM', 'SC', 'Topical', 'Inhalation', 'PR', 'PV']),
  frequency: z.string().min(1, 'Frequency required'),
  duration: z.string().min(1, 'Duration required'),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
  repeats: z.number().min(0, 'Repeats cannot be negative'),
  indication: z.string().min(5, 'Indication required'),
});

type PrescriptionFormData = z.infer<typeof prescriptionSchema>;

interface MedicationOrderEntryProps {
  patientId: string;
  sessionId: string;
  onAdd: (prescription: Prescription) => void;
}

const MedicationOrderEntry: React.FC<MedicationOrderEntryProps> = ({
  patientId,
  sessionId,
  onAdd
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [pbsMatches, setPbsMatches] = useState<any[]>([]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue
  } = useForm<PrescriptionFormData>({
    resolver: zodResolver(prescriptionSchema),
    defaultValues: {
      medication: '',
      dose: '',
      route: 'PO',
      frequency: '',
      duration: '',
      quantity: 1,
      repeats: 0,
      indication: ''
    }
  });

  const handleSearchMedication = async (query: string) => {
    setSearchQuery(query);
    if (query.length < 2) {
      setPbsMatches([]);
      return;
    }

    // Simulate PBS search (in real implementation, call backend API)
    // This would query the PBS database
    const mockResults = [
      {
        name: 'Amoxicillin 500mg capsules',
        pbsCode: '2089Y',
        restrictions: 'None',
        price: '$5.60'
      },
      {
        name: 'Amoxicillin/Clavulanic Acid 875/125mg tablets',
        pbsCode: '8601E',
        restrictions: 'Authority required',
        price: '$6.80'
      }
    ].filter(m => m.name.toLowerCase().includes(query.toLowerCase()));

    setPbsMatches(mockResults);
  };

  const handleSelectPBSMedication = (medication: any) => {
    setValue('medication', medication.name);
    setPbsMatches([]);
    setSearchQuery('');
  };

  const onSubmit = (data: PrescriptionFormData) => {
    const prescription: Prescription = {
      id: `rx_${Date.now()}`,
      patientId,
      sessionId,
      ...data
    };

    onAdd(prescription);
    reset();
  };

  const commonFrequencies = [
    'Once daily',
    'Twice daily (BD)',
    'Three times daily (TDS)',
    'Four times daily (QID)',
    'Every 6 hours',
    'Every 8 hours',
    'Every 12 hours',
    'PRN (as needed)'
  ];

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="bg-orange-600 text-white px-6 py-4 rounded-t-lg">
        <h2 className="text-xl font-semibold">Medication Order</h2>
        <p className="text-sm text-orange-100 mt-1">PBS-compliant prescriptions</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
        {/* Medication Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Medication Name
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearchMedication(e.target.value)}
              placeholder="Search PBS medications..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>

          {/* PBS Search Results */}
          {pbsMatches.length > 0 && (
            <div className="mt-2 border border-gray-200 rounded-lg overflow-hidden">
              {pbsMatches.map((med, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleSelectPBSMedication(med)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                >
                  <div className="font-medium text-gray-900">{med.name}</div>
                  <div className="text-sm text-gray-600 mt-1">
                    PBS Code: {med.pbsCode} | {med.restrictions} | {med.price}
                  </div>
                </button>
              ))}
            </div>
          )}

          <input
            type="text"
            {...register('medication')}
            className="hidden"
          />
          {errors.medication && (
            <p className="text-red-500 text-sm mt-1">{errors.medication.message}</p>
          )}
        </div>

        {/* Dose and Route */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Dose
            </label>
            <input
              type="text"
              {...register('dose')}
              placeholder="e.g., 500mg"
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                errors.dose ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.dose && (
              <p className="text-red-500 text-sm mt-1">{errors.dose.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Route
            </label>
            <select
              {...register('route')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="PO">PO (Oral)</option>
              <option value="IV">IV (Intravenous)</option>
              <option value="IM">IM (Intramuscular)</option>
              <option value="SC">SC (Subcutaneous)</option>
              <option value="Topical">Topical</option>
              <option value="Inhalation">Inhalation</option>
              <option value="PR">PR (Rectal)</option>
              <option value="PV">PV (Vaginal)</option>
            </select>
          </div>
        </div>

        {/* Frequency and Duration */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Frequency
            </label>
            <select
              {...register('frequency')}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                errors.frequency ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select frequency</option>
              {commonFrequencies.map(freq => (
                <option key={freq} value={freq}>{freq}</option>
              ))}
            </select>
            {errors.frequency && (
              <p className="text-red-500 text-sm mt-1">{errors.frequency.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration
            </label>
            <input
              type="text"
              {...register('duration')}
              placeholder="e.g., 7 days"
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                errors.duration ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.duration && (
              <p className="text-red-500 text-sm mt-1">{errors.duration.message}</p>
            )}
          </div>
        </div>

        {/* Quantity and Repeats */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quantity
            </label>
            <input
              type="number"
              {...register('quantity', { valueAsNumber: true })}
              min="1"
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                errors.quantity ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.quantity && (
              <p className="text-red-500 text-sm mt-1">{errors.quantity.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Repeats
            </label>
            <input
              type="number"
              {...register('repeats', { valueAsNumber: true })}
              min="0"
              max="5"
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                errors.repeats ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.repeats && (
              <p className="text-red-500 text-sm mt-1">{errors.repeats.message}</p>
            )}
          </div>
        </div>

        {/* Indication */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Indication
          </label>
          <input
            type="text"
            {...register('indication')}
            placeholder="e.g., Community-acquired pneumonia"
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
              errors.indication ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.indication && (
            <p className="text-red-500 text-sm mt-1">{errors.indication.message}</p>
          )}
        </div>

        {/* Warning banner */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <AlertTriangle className="text-yellow-600 flex-shrink-0 mt-0.5" size={20} />
            <div className="text-sm text-yellow-800">
              <p className="font-medium mb-1">PBS Compliance Check</p>
              <p>Ensure medication is PBS-listed. Authority may be required for certain drugs. Check dose limits and indications.</p>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
        >
          <Plus size={20} />
          Add Prescription
        </button>
      </form>
    </div>
  );
};

export default MedicationOrderEntry;
```

**Epic EHR Components:**

Similar structure to Cerner but with Epic's UI patterns (purple color scheme, different layout). I'll provide the sidebar:

```typescript
// src/components/epic/EpicSidebar.tsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Pill,
  TestTube,
  Activity,
  UserCircle
} from 'lucide-react';

const EpicSidebar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/epic', icon: LayoutDashboard, label: 'Storyboard' },
    { path: '/epic/patient', icon: UserCircle, label: 'Patient Summary' },
    { path: '/epic/note', icon: FileText, label: 'Note Writer' },
    { path: '/epic/meds', icon: Pill, label: 'Med Manager' },
    { path: '/epic/orders', icon: TestTube, label: 'Order Entry' },
    { path: '/epic/vitals', icon: Activity, label: 'Flowsheet' },
  ];

  return (
    <div className="w-20 bg-purple-900 text-white h-screen flex flex-col items-center py-4">
      {/* Epic Logo */}
      <div className="w-12 h-12 bg-purple-700 rounded-lg flex items-center justify-center mb-8">
        <span className="font-bold text-xl">E</span>
      </div>

      {/* Navigation Icons */}
      <nav className="flex-1 flex flex-col gap-4">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              title={label}
              className={`w-12 h-12 rounded-lg flex items-center justify-center transition-colors ${
                isActive
                  ? 'bg-purple-700'
                  : 'hover:bg-purple-800'
              }`}
            >
              <Icon size={24} />
            </Link>
          );
        })}
      </nav>
    </div>
  );
};

export default EpicSidebar;
```

**Validation:**
- [ ] Cerner UI matches PowerChart look and feel
- [ ] Epic UI matches EHR design patterns
- [ ] Multi-tab navigation works smoothly
- [ ] Forms validate input correctly
- [ ] Mobile-responsive (or desktop-only warning displayed)
- [ ] State management works (Zustand for session)

**Time Estimate:** 30 hours

---

### Task 2: Backend API + Database (20 hours)

**Priority:** P0 (CRITICAL - data persistence)

**Setup FastAPI Backend:**

```bash
cd /home/dev/Development/irStudy/emr-practice
mkdir -p backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiosqlite==0.19.0
anthropic==0.8.0
httpx==0.26.0
python-dotenv==1.0.0
EOF

# Install dependencies
pip install -r requirements.txt

# Create directory structure
mkdir -p {api,models,schemas,services,db}
mkdir -p api/routes
```

**Database Models:**

```python
# backend/models/database.py
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./emr_practice.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True)
    mrn = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    dob = Column(String)
    age = Column(Integer)
    gender = Column(String)
    aboriginal_torres_strait = Column(Boolean, default=False)
    allergies = Column(JSON)  # List of allergy objects
    medications = Column(JSON)  # List of medication objects
    medical_history = Column(JSON)  # List of history items
    vital_signs = Column(JSON)  # Vital signs object
    presenting_complaint = Column(Text)
    clinical_scenario = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("EMRSession", back_populates="patient")

class EMRSession(Base):
    __tablename__ = "emr_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    patient_id = Column(String, ForeignKey("patients.id"))
    emr_type = Column(String)  # 'cerner' or 'epic'
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    overall_score = Column(Float, nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="sessions")
    soap_note = relationship("SOAPNote", back_populates="session", uselist=False)
    prescriptions = relationship("Prescription", back_populates="session")
    pathology_orders = relationship("PathologyOrder", back_populates="session")

class SOAPNote(Base):
    __tablename__ = "soap_notes"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("emr_sessions.id"))
    patient_id = Column(String)
    subjective = Column(Text)
    objective = Column(Text)
    assessment = Column(Text)
    plan = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Validation results
    validation_score = Column(Float, nullable=True)
    validation_feedback = Column(JSON, nullable=True)

    # Relationships
    session = relationship("EMRSession", back_populates="soap_note")

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("emr_sessions.id"))
    patient_id = Column(String)
    medication = Column(String)
    dose = Column(String)
    route = Column(String)
    frequency = Column(String)
    duration = Column(String)
    quantity = Column(Integer)
    repeats = Column(Integer)
    indication = Column(String)
    pbs_code = Column(String, nullable=True)
    streamlined_authority = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Validation results
    validation_score = Column(Float, nullable=True)
    validation_feedback = Column(JSON, nullable=True)

    # Relationships
    session = relationship("EMRSession", back_populates="prescriptions")

class PathologyOrder(Base):
    __tablename__ = "pathology_orders"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("emr_sessions.id"))
    patient_id = Column(String)
    test_type = Column(String)
    mbs_item_number = Column(String)
    indication = Column(String)
    urgency = Column(String)
    clinical_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Validation results
    validation_score = Column(Float, nullable=True)
    validation_feedback = Column(JSON, nullable=True)

    # Relationships
    session = relationship("EMRSession", back_populates="pathology_orders")

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Alembic Migration Setup:**

```bash
# Initialize Alembic
cd /home/dev/Development/irStudy/emr-practice/backend
alembic init alembic

# Edit alembic.ini - update sqlalchemy.url
# Edit alembic/env.py - import Base from models
```

```python
# alembic/env.py (modify)
from models.database import Base
target_metadata = Base.metadata

# Generate initial migration
alembic revision --autogenerate -m "Initial EMR practice schema"

# Apply migration
alembic upgrade head
```

**API Routes - Patients:**

```python
# backend/api/routes/patients.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from models.database import Patient, get_db
from schemas.patient import PatientCreate, PatientResponse

router = APIRouter(prefix="/api/patients", tags=["patients"])

@router.get("/", response_model=List[PatientResponse])
def get_patients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get list of simulated patients"""
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Get patient by ID"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Create new simulated patient"""
    db_patient = Patient(
        id=f"PAT_{uuid.uuid4().hex[:8]}",
        mrn=f"MRN{uuid.uuid4().hex[:6].upper()}",
        **patient.model_dump()
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/random/", response_model=PatientResponse)
def get_random_patient(db: Session = Depends(get_db)):
    """Get random patient for practice"""
    import random
    patients = db.query(Patient).all()
    if not patients:
        raise HTTPException(status_code=404, detail="No patients available")
    return random.choice(patients)
```

**API Routes - EMR Sessions:**

```python
# backend/api/routes/sessions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from models.database import EMRSession, SOAPNote, Prescription, PathologyOrder, get_db
from schemas.session import SessionCreate, SessionResponse, SOAPNoteCreate, PrescriptionCreate, PathologyOrderCreate

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.post("/", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Start new EMR practice session"""
    db_session = EMRSession(
        id=f"SES_{uuid.uuid4().hex[:8]}",
        **session.model_dump()
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get EMR session by ID"""
    session = db.query(EMRSession).filter(EMRSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/{session_id}/soap", response_model=dict)
def add_soap_note(session_id: str, soap: SOAPNoteCreate, db: Session = Depends(get_db)):
    """Add SOAP note to session"""
    # Verify session exists
    session = db.query(EMRSession).filter(EMRSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create SOAP note
    db_soap = SOAPNote(
        id=f"SOAP_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        **soap.model_dump()
    )
    db.add(db_soap)
    db.commit()
    db.refresh(db_soap)

    return {"message": "SOAP note saved", "id": db_soap.id}

@router.post("/{session_id}/prescriptions", response_model=dict)
def add_prescription(session_id: str, rx: PrescriptionCreate, db: Session = Depends(get_db)):
    """Add prescription to session"""
    session = db.query(EMRSession).filter(EMRSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_rx = Prescription(
        id=f"RX_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        **rx.model_dump()
    )
    db.add(db_rx)
    db.commit()
    db.refresh(db_rx)

    return {"message": "Prescription saved", "id": db_rx.id}

@router.post("/{session_id}/pathology", response_model=dict)
def add_pathology_order(session_id: str, order: PathologyOrderCreate, db: Session = Depends(get_db)):
    """Add pathology order to session"""
    session = db.query(EMRSession).filter(EMRSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_order = PathologyOrder(
        id=f"PATH_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        **order.model_dump()
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return {"message": "Pathology order saved", "id": db_order.id}

@router.put("/{session_id}/end")
def end_session(session_id: str, db: Session = Depends(get_db)):
    """End EMR practice session"""
    session = db.query(EMRSession).filter(EMRSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.end_time = datetime.utcnow()
    db.commit()

    return {"message": "Session ended", "duration_minutes": (session.end_time - session.start_time).total_seconds() / 60}
```

**Main FastAPI App:**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.database import init_db
from api.routes import patients, sessions

# Initialize database
init_db()

app = FastAPI(
    title="irStudy EMR Practice API",
    description="Backend API for hospital EMR simulation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router)
app.include_router(sessions.router)

@app.get("/")
def root():
    return {"message": "irStudy EMR Practice API v1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Validation:**
- [ ] Database schema created (check emr_practice.db)
- [ ] API endpoints functional (test with curl/Postman)
- [ ] CRUD operations work for all entities
- [ ] Relationships between tables correct
- [ ] Migrations work (alembic upgrade/downgrade)

**Time Estimate:** 20 hours

---

**(Continuing with Task 3 - PBS/MBS Integration...)**

Due to length constraints, I'll summarize the remaining tasks and provide key code snippets:

### Task 3: PBS/MBS Integration (15 hours)

**Download PBS Database:**

```bash
# Download PBS XML data
wget https://www.pbs.gov.au/pbs/home
# Parse XML to SQLite (script to be created)
python scripts/import_pbs_data.py
```

**PBS Validation Service:**

```python
# backend/services/pbs_validator.py
class PBSValidator:
    def validate_prescription(self, medication: str, indication: str) -> dict:
        # Check if medication is PBS-listed
        # Check if indication matches approved uses
        # Return validation result with PBS code if found
        pass
```

### Task 4: AI Validation Agent (20 hours)

```python
# backend/services/emr_validation_agent.py
from anthropic import Anthropic

class EMRValidationAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def validate_soap_note(self, soap: SOAPNote, patient: Patient) -> ValidationResult:
        # Construct validation prompt
        prompt = f"""You are a medical documentation expert. Validate this SOAP note for an Australian medical student.

Patient Context:
{patient.clinical_scenario}

SOAP Note:
Subjective: {soap.subjective}
Objective: {soap.objective}
Assessment: {soap.assessment}
Plan: {soap.plan}

Validate for:
1. Completeness (all sections adequately detailed)
2. Clinical accuracy (diagnoses match presentation)
3. Australian medical terminology
4. PBS/MBS compliance in plan
5. Safety (red flags addressed)

Provide score (0-100) and specific feedback."""

        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response and return ValidationResult
        return self._parse_validation_response(response.content[0].text)
```

### Task 5: Progress Tracking (15 hours)

**Analytics Dashboard Component:**

```typescript
// src/pages/analytics/AnalyticsPage.tsx
// Show session history, scores over time, weak areas
```

### Task 6: Testing (20 hours)

**PyTest Tests:**

```python
# backend/tests/test_validation.py
def test_soap_note_validation():
    # Test AI validation accuracy
    pass

def test_pbs_prescription_validation():
    # Test PBS compliance checking
    pass
```

**Playwright E2E Tests:**

```typescript
// frontend/tests/e2e/emr-workflow.spec.ts
test('complete EMR documentation workflow', async ({ page }) => {
  // 1. Start session
  // 2. View patient
  // 3. Write SOAP note
  // 4. Add prescription
  // 5. Submit for validation
  // 6. Review feedback
});
```

**Validation:**
- [ ] All backend tests pass (95%+ coverage)
- [ ] E2E tests cover critical workflows
- [ ] Manual testing checklist completed
- [ ] Performance benchmarks met (< 2s validation)

**Time Estimate:** 20 hours

---

## 📊 Success Metrics

### Completion Criteria
- [ ] Cerner and Epic UIs functional
- [ ] Backend API with SQLite database
- [ ] PBS/MBS databases integrated
- [ ] AI validation agent 80%+ accuracy
- [ ] Progress tracking dashboard
- [ ] 95%+ test coverage

### Quality Gates
- [ ] SOAP note validation accuracy: 80%+
- [ ] PBS prescription validation: 95%+
- [ ] Response time < 2 seconds
- [ ] All E2E tests passing

---

## 🔗 Related Documents

- **[README.md](./README.md)** - Overall plan
- **[01_PHASE1_MOBILE_QUICK_SEARCH.md](./01_PHASE1_MOBILE_QUICK_SEARCH.md)** - Previous phase
- **[03_PHASE3_AMC_SIMULATION.md](./03_PHASE3_AMC_SIMULATION.md)** - Next phase

---

**Last Updated:** 2026-02-01
**Owner:** Full-Stack Developer
**Estimated Completion:** 2026-03-15 (4 weeks after Phase 1)
