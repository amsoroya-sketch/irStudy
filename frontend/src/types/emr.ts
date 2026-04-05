/**
 * EMR Type Definitions
 *
 * Type-safe interfaces for EMR Practice System components.
 * Matches backend API contracts from PRD_BACKEND_002.
 */

// EMR System Type
export type EMRSystem = 'epic' | 'cerner';

// Session Status
export type SessionStatus = 'in_progress' | 'submitted' | 'validated';

// Validation Status
export type ValidationStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

// Auto-Save Status
export type AutoSaveStatus = 'idle' | 'saving' | 'saved' | 'error';

/**
 * Mock Patient (from patient_personas table)
 */
export interface MockPatient {
  id: string;
  full_name: string;
  age_years: number;
  gender: 'Male' | 'Female' | 'Other';
  date_of_birth: string; // ISO date string
  medicare_number?: string;
  mrn: string; // Medical Record Number
  allergies: string[];
  medications: string[];
  medical_history: string[];
  social_history: string;
  family_history: string;
  presenting_complaint: string;
  vital_signs: VitalSigns;
  specialty: string;
}

/**
 * Vital Signs
 */
export interface VitalSigns {
  bp: string; // e.g., "120/80"
  hr: number; // Heart rate (bpm)
  rr: number; // Respiratory rate (breaths/min)
  temp: number; // Temperature (°C)
  spo2: number; // Oxygen saturation (%)
  height_cm?: number;
  weight_kg?: number;
  bmi?: number;
}

/**
 * SOAP Note Draft (stored in session_data JSON field)
 */
export interface SOAPNoteDraft {
  subjective: string; // HPI, PMHx, FHx, SHx
  objective: string; // Physical exam findings
  assessment: string; // Differential diagnoses
  plan: string; // Management plan
  prescriptions: PrescriptionDraft[];
  pathology_orders: PathologyOrderDraft[];
  imaging_orders: ImagingOrderDraft[];
}

/**
 * Prescription Draft (Australian PBS medications)
 */
export interface PrescriptionDraft {
  medication: string; // e.g., "Paracetamol 500mg tablets"
  dose: string; // e.g., "1-2 tablets"
  frequency: string; // e.g., "Every 4-6 hours as needed"
  route: string; // e.g., "Oral"
  duration: string; // e.g., "7 days"
  indication: string; // e.g., "Pain relief"
  pbs_item_code?: string; // PBS item code if applicable
}

/**
 * Pathology Order Draft (Australian MBS pathology)
 */
export interface PathologyOrderDraft {
  test_name: string; // e.g., "Full Blood Count"
  indication: string; // e.g., "Anaemia investigation"
  urgency: 'routine' | 'urgent' | 'stat';
  mbs_item_code?: string; // MBS item code if applicable
}

/**
 * Imaging Order Draft (Australian MBS imaging)
 */
export interface ImagingOrderDraft {
  imaging_type: string; // e.g., "Chest X-ray"
  indication: string; // e.g., "Suspected pneumonia"
  urgency: 'routine' | 'urgent' | 'stat';
  mbs_item_code?: string; // MBS item code if applicable
}

/**
 * Conversion Metadata (from OSCE-to-EMR conversion)
 */
export interface ConversionMetadata {
  pre_fill_percentage: number; // 0.0-1.0
  extraction_confidence: number; // 0.0-1.0
  tokens_used: number;
  api_response_time_ms: number;
}

/**
 * EMR Session (from emr_sessions table)
 */
export interface EMRSession {
  id: string;
  user_id: string;
  patient_id: string;
  emr_system: EMRSystem;
  status: SessionStatus;
  session_data: SOAPNoteDraft;
  word_count: number;
  typing_speed_wpm: number;
  time_spent_minutes: number;
  started_at: string; // ISO datetime string
  submitted_at?: string; // ISO datetime string
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  source_osce_attempt_id?: string; // UUID of source OSCE attempt (if converted)
  conversion_metadata?: ConversionMetadata; // Conversion metrics (if converted from OSCE)
}

/**
 * AMC Rubric Score (from validation results)
 */
export interface AMCRubricScore {
  category: 'history_taking' | 'physical_examination' | 'clinical_reasoning' | 'communication' | 'documentation';
  score: number; // 0-10
  max_score: number; // Always 10
  feedback: string;
}

/**
 * Validation Result (from emr_validations table)
 */
export interface ValidationResult {
  id: string;
  session_id: string;
  validation_status: ValidationStatus;
  overall_score: number; // 0-10 (weighted average)
  amc_rubric_scores: AMCRubricScore[];
  clinical_accuracy_feedback: string;
  ahpra_compliance: boolean;
  dangerous_medications: string[];
  missing_elements: string[];
  strengths: string[];
  areas_for_improvement: string[];
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

/**
 * Dashboard Metrics (from dashboard API)
 */
export interface EMRDashboardMetrics {
  total_sessions: number;
  sessions_this_week: number;
  average_score: number; // 0-10
  average_typing_wpm: number;
  improvement_percentage: number; // vs previous week
  ahpra_compliance_rate: number; // 0-100%
  total_time_spent_minutes: number;
  specialty_breakdown: SpecialtyMetric[];
  system_usage: SystemUsageMetric[];
}

/**
 * Specialty Metric (for specialty breakdown chart)
 */
export interface SpecialtyMetric {
  specialty: string;
  session_count: number;
  average_score: number;
}

/**
 * System Usage Metric (for Epic vs Cerner pie chart)
 */
export interface SystemUsageMetric {
  emr_system: EMRSystem;
  session_count: number;
  percentage: number;
}

/**
 * Recent EMR Session (for dashboard list)
 */
export interface RecentEMRSession {
  id: string;
  patient_name: string;
  specialty: string;
  emr_system: EMRSystem;
  status: SessionStatus;
  score?: number; // Only if validated
  started_at: string; // ISO datetime string
}
