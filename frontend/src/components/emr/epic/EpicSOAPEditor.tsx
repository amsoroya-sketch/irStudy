/**
 * Epic SOAP Editor Component
 *
 * 4-tab interface for SOAP note documentation (Subjective, Objective, Assessment, Plan).
 * Integrates with auto-save hook for seamless UX.
 *
 * Features:
 * - Tabbed SOAP sections with rich text input
 * - Auto-save on changes (debounced)
 * - Word count tracking
 * - Validation feedback display
 * - WCAG 2.2 AA accessible (keyboard navigation, ARIA labels)
 * - Australian medical terminology (paracetamol, not acetaminophen)
 */

import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  TextField,
  Typography,
  Paper,
  Alert,
  Chip,
} from '@mui/material';
import {
  Person as SubjectiveIcon,
  MonitorHeart as ObjectiveIcon,
  Psychology as AssessmentIcon,
  Checklist as PlanIcon,
} from '@mui/icons-material';
import { SOAPNoteDraft } from '../../../types/emr';

interface EpicSOAPEditorProps {
  sessionId: string;
  draft: SOAPNoteDraft;
  onChange: (field: keyof SOAPNoteDraft, value: string) => void;
  validationFeedback?: string[];
  readonly?: boolean; // For viewing submitted sessions
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`soap-tabpanel-${index}`}
      aria-labelledby={`soap-tab-${index}`}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

const soapSections = [
  {
    id: 'subjective' as keyof SOAPNoteDraft,
    label: 'Subjective',
    icon: <SubjectiveIcon />,
    placeholder: `History of Present Illness (HPI):
- Presenting complaint and duration
- Symptom characteristics (SOCRATES: Site, Onset, Character, Radiation, Associated symptoms, Timing, Exacerbating/Relieving factors, Severity)
- Impact on daily activities

Past Medical History (PMHx):
- Previous diagnoses, surgeries, hospitalisations

Medications:
- Current medications and allergies

Family History (FHx):
- Relevant family conditions

Social History (SHx):
- Smoking, alcohol, occupation, living situation`,
    helperText: '9-step history taking, SOCRATES symptom analysis',
  },
  {
    id: 'objective' as keyof SOAPNoteDraft,
    label: 'Objective',
    icon: <ObjectiveIcon />,
    placeholder: `General Appearance:
- Alert, comfortable, well-appearing

Vital Signs:
- (See patient banner above)

Systemic Examination:
- Cardiovascular: Heart sounds, peripheral pulses, JVP, oedema
- Respiratory: Chest expansion, percussion, auscultation
- Abdominal: Inspection, palpation, bowel sounds
- Neurological: Cranial nerves, motor/sensory, reflexes, cerebellar
- Other systems as relevant`,
    helperText: 'Physical examination findings, objective measurements',
  },
  {
    id: 'assessment' as keyof SOAPNoteDraft,
    label: 'Assessment',
    icon: <AssessmentIcon />,
    placeholder: `Differential Diagnoses (ranked by likelihood):
1. [Most likely diagnosis]
   - Supporting evidence:
   - Red flags to monitor:

2. [Second diagnosis]
   - Supporting evidence:
   - Red flags to monitor:

3. [Third diagnosis]
   - Supporting evidence:
   - Red flags to monitor:

Clinical Reasoning:
- Justify your primary diagnosis
- Discuss ruling out alternatives`,
    helperText: 'Differential diagnoses, clinical reasoning, red flag identification',
  },
  {
    id: 'plan' as keyof SOAPNoteDraft,
    label: 'Plan',
    icon: <PlanIcon />,
    placeholder: `Investigations:
- Pathology: [e.g., FBC, UEC, LFTs, CRP]
- Imaging: [e.g., Chest X-ray, CT scan]
- Other: [e.g., ECG, spirometry]

Management:
- Pharmacological:
  • [Medication]: [Dose] [Frequency] [Duration] (PBS item if applicable)
  • Use Australian medication names (paracetamol, salbutamol, adrenaline)
- Non-pharmacological:
  • [e.g., Lifestyle modifications, physiotherapy]

Follow-up:
- Review in [timeframe]
- Red flags to return for: [list]

Patient Education:
- Condition explanation
- Safety netting advice`,
    helperText: 'Investigations, treatment plan, follow-up, patient education (Australian PBS/MBS)',
  },
];

export const EpicSOAPEditor: React.FC<EpicSOAPEditorProps> = ({
  draft,
  onChange,
  validationFeedback = [],
  readonly = false,
}) => {
  const [activeTab, setActiveTab] = useState(0);

  // Calculate word count for current tab
  const getCurrentWordCount = () => {
    const currentSection = soapSections[activeTab].id;
    const text = draft[currentSection] as string || '';
    return text.trim().split(/\s+/).filter(Boolean).length;
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Paper
      elevation={0}
      sx={{
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 1,
      }}
    >
      {/* Validation Feedback */}
      {validationFeedback.length > 0 && (
        <Box sx={{ p: 2, pb: 0 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
              Validation Feedback:
            </Typography>
            {validationFeedback.map((feedback, index) => (
              <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                • {feedback}
              </Typography>
            ))}
          </Alert>
        </Box>
      )}

      {/* SOAP Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="SOAP note sections"
          variant="fullWidth"
        >
          {soapSections.map((section, index) => (
            <Tab
              key={section.id}
              icon={section.icon}
              iconPosition="start"
              label={section.label}
              id={`soap-tab-${index}`}
              aria-controls={`soap-tabpanel-${index}`}
              sx={{ textTransform: 'none', fontWeight: 500 }}
            />
          ))}
        </Tabs>
      </Box>

      {/* Tab Panels */}
      {soapSections.map((section, index) => (
        <TabPanel key={section.id} value={activeTab} index={index}>
          <Box sx={{ px: 2 }}>
            <TextField
              fullWidth
              multiline
              rows={16}
              value={(draft[section.id] as string) || ''}
              onChange={(e) => onChange(section.id, e.target.value)}
              placeholder={section.placeholder}
              disabled={readonly}
              helperText={section.helperText}
              sx={{
                '& .MuiInputBase-root': {
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  lineHeight: 1.6,
                },
              }}
              inputProps={{
                'aria-label': `${section.label} section`,
                spellCheck: true,
              }}
            />

            {/* Word Count */}
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              sx={{ mt: 1 }}
            >
              <Typography variant="caption" color="text.secondary">
                {section.helperText}
              </Typography>
              <Chip
                label={`${getCurrentWordCount()} words`}
                size="small"
                variant="outlined"
                aria-label={`Word count: ${getCurrentWordCount()}`}
              />
            </Box>
          </Box>
        </TabPanel>
      ))}
    </Paper>
  );
};
