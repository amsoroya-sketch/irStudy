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
