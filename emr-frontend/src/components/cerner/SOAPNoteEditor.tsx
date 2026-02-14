// src/components/cerner/SOAPNoteEditor.tsx

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Save, Clock, CheckCircle } from 'lucide-react';

// Simplified SOAP schema for now (full schema in Task 2.1)
const soapNoteSchema = z.object({
  subjective: z.object({
    chiefComplaint: z.string().min(5, 'At least 5 characters required'),
    hpi: z.string().min(50, 'At least 50 characters required'),
  }),
  objective: z.object({
    vitalSigns: z.object({
      temperature: z.number().min(35).max(42),
      heartRate: z.number().min(30).max(220),
      bloodPressureSystolic: z.number().min(60).max(250),
      bloodPressureDiastolic: z.number().min(40).max(150),
      respiratoryRate: z.number().min(8).max(60),
      oxygenSaturation: z.number().min(50).max(100),
    }),
    generalAppearance: z.string().min(20),
  }),
  assessment: z.object({
    workingDiagnosis: z.string().min(5),
    clinicalReasoning: z.string().min(100),
  }),
  plan: z.object({
    management: z.string().min(50),
    safetyNetting: z.string().min(50),
  }),
});

type SOAPNoteFormData = z.infer<typeof soapNoteSchema>;

interface SOAPNoteEditorProps {
  sessionId: string;
  onSave: (data: SOAPNoteFormData) => Promise<void>;
  initialData?: Partial<SOAPNoteFormData>;
}

export const SOAPNoteEditor: React.FC<SOAPNoteEditorProps> = ({
  sessionId,
  onSave,
  initialData,
}) => {
  const [autoSaveStatus, setAutoSaveStatus] = React.useState<'saved' | 'saving' | 'unsaved'>('saved');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SOAPNoteFormData>({
    resolver: zodResolver(soapNoteSchema),
    defaultValues: initialData,
  });

  // Auto-save every 30 seconds
  React.useEffect(() => {
    const subscription = watch(() => {
      setAutoSaveStatus('unsaved');
    });

    const autoSaveInterval = setInterval(async () => {
      if (autoSaveStatus === 'unsaved') {
        setAutoSaveStatus('saving');
        try {
          const data = watch();
          await onSave(data as SOAPNoteFormData);
          setAutoSaveStatus('saved');
        } catch (error) {
          console.error('Auto-save failed:', error);
          setAutoSaveStatus('unsaved');
        }
      }
    }, 30000); // 30 seconds

    return () => {
      subscription.unsubscribe();
      clearInterval(autoSaveInterval);
    };
  }, [watch, onSave, autoSaveStatus]);

  const onSubmit = async (data: SOAPNoteFormData) => {
    setAutoSaveStatus('saving');
    try {
      await onSave(data);
      setAutoSaveStatus('saved');
    } catch (error) {
      setAutoSaveStatus('unsaved');
    }
  };

  return (
    <div className="cerner-soap-editor">
      {/* Header */}
      <div className="cerner-editor-header">
        <h2 className="text-xl font-semibold">SOAP Note</h2>
        <div className="cerner-autosave-status">
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

      <form onSubmit={handleSubmit(onSubmit)} className="cerner-soap-form">
        {/* Subjective Section */}
        <div className="cerner-soap-section">
          <h3 className="cerner-section-title">SUBJECTIVE</h3>

          <div className="cerner-form-field">
            <label>Chief Complaint</label>
            <input
              {...register('subjective.chiefComplaint')}
              placeholder="e.g., Chest pain radiating to left arm"
              className="cerner-input"
            />
            {errors.subjective?.chiefComplaint && (
              <span className="cerner-error">{errors.subjective.chiefComplaint.message}</span>
            )}
          </div>

          <div className="cerner-form-field">
            <label>History of Present Illness (HPI)</label>
            <textarea
              {...register('subjective.hpi')}
              placeholder="Detailed history of present illness..."
              rows={6}
              className="cerner-textarea"
            />
            {errors.subjective?.hpi && (
              <span className="cerner-error">{errors.subjective.hpi.message}</span>
            )}
          </div>
        </div>

        {/* Objective Section */}
        <div className="cerner-soap-section">
          <h3 className="cerner-section-title">OBJECTIVE</h3>

          <div className="cerner-vitals-grid">
            <div className="cerner-form-field">
              <label>Temperature (°C)</label>
              <input
                type="number"
                step="0.1"
                {...register('objective.vitalSigns.temperature', { valueAsNumber: true })}
                className="cerner-input"
              />
            </div>

            <div className="cerner-form-field">
              <label>Heart Rate (bpm)</label>
              <input
                type="number"
                {...register('objective.vitalSigns.heartRate', { valueAsNumber: true })}
                className="cerner-input"
              />
            </div>

            <div className="cerner-form-field">
              <label>BP Systolic</label>
              <input
                type="number"
                {...register('objective.vitalSigns.bloodPressureSystolic', { valueAsNumber: true })}
                className="cerner-input"
              />
            </div>

            <div className="cerner-form-field">
              <label>BP Diastolic</label>
              <input
                type="number"
                {...register('objective.vitalSigns.bloodPressureDiastolic', { valueAsNumber: true })}
                className="cerner-input"
              />
            </div>

            <div className="cerner-form-field">
              <label>Resp Rate</label>
              <input
                type="number"
                {...register('objective.vitalSigns.respiratoryRate', { valueAsNumber: true })}
                className="cerner-input"
              />
            </div>

            <div className="cerner-form-field">
              <label>SpO2 (%)</label>
              <input
                type="number"
                {...register('objective.vitalSigns.oxygenSaturation', { valueAsNumber: true })}
                className="cerner-input"
              />
            </div>
          </div>

          <div className="cerner-form-field">
            <label>General Appearance</label>
            <textarea
              {...register('objective.generalAppearance')}
              placeholder="Patient general appearance and demeanor..."
              rows={3}
              className="cerner-textarea"
            />
          </div>
        </div>

        {/* Assessment Section */}
        <div className="cerner-soap-section">
          <h3 className="cerner-section-title">ASSESSMENT</h3>

          <div className="cerner-form-field">
            <label>Working Diagnosis</label>
            <input
              {...register('assessment.workingDiagnosis')}
              placeholder="Primary diagnosis"
              className="cerner-input"
            />
          </div>

          <div className="cerner-form-field">
            <label>Clinical Reasoning</label>
            <textarea
              {...register('assessment.clinicalReasoning')}
              placeholder="Explain your clinical reasoning..."
              rows={6}
              className="cerner-textarea"
            />
          </div>
        </div>

        {/* Plan Section */}
        <div className="cerner-soap-section">
          <h3 className="cerner-section-title">PLAN</h3>

          <div className="cerner-form-field">
            <label>Management Plan</label>
            <textarea
              {...register('plan.management')}
              placeholder="Investigations, medications, procedures..."
              rows={6}
              className="cerner-textarea"
            />
          </div>

          <div className="cerner-form-field">
            <label>Safety Netting</label>
            <textarea
              {...register('plan.safetyNetting')}
              placeholder="Red flag symptoms to watch for..."
              rows={4}
              className="cerner-textarea"
            />
          </div>
        </div>

        {/* Submit Button */}
        <div className="cerner-form-actions">
          <button type="submit" className="cerner-btn-primary">
            <Save className="w-4 h-4" />
            Save & Validate
          </button>
        </div>
      </form>
    </div>
  );
};
