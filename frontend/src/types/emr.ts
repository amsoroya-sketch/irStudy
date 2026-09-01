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
  name: string;
  age: number;
  gender: 'Male' | 'Female' | 'Other';
  date_of_birth?: string; // ISO date string
  medicare_number?: string;
  mrn?: string; // Medical Record Number
  allergies?: string[];
  medications?: string[];
  medical_history?: string[];
  social_history?: string;
  family_history?: string;
  presenting_complaint: string;
  vital_signs?: VitalSigns;
  specialty: string;
  difficulty?: string;
  /** Assessment criteria for the scenario (task shown in the scenario brief). */
  validation_criteria?: ValidationCriteria;
}

/**
 * Validation Criteria (drives the ScenarioBrief task text)
 */
export interface ValidationCriteria {
  task?: string;
  required_elements?: string[];
  critical_errors?: string[];
}

/**
 * Vital Signs
 */
export interface VitalSigns {
  bp?: string; // e.g., "120/80"
  hr?: number; // Heart rate (bpm)
  rr?: number; // Respiratory rate (breaths/min)
  temp?: number; // Temperature (°C)
  spo2?: number; // Oxygen saturation (%)
  height_cm?: number;
  weight_kg?: number;
  weight?: number; // Backend may return weight instead of weight_kg
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
  session_id: string;
  validation_id?: string;
  patient: MockPatient;
  specialty: string;
  difficulty: string;
  started_at: string; // ISO datetime string
  submitted_at?: string; // ISO datetime string
  elapsed_time_seconds: number;
  status: 'in_progress' | 'graded';
  auto_save_count: number;
  last_auto_save_at?: string;
  validation_score?: number;
  total_amc_score?: number;
  validation_results?: ValidationResult;
  soap_note?: SOAPNoteDraft;
  typing_metrics?: Record<string, unknown>;
  performance_summary?: Record<string, unknown>;
  next_steps?: Record<string, unknown>;
  message?: string;
  source_osce_attempt_id?: string; // UUID of source OSCE attempt (if converted)
  conversion_metadata?: ConversionMetadata; // Conversion metrics (if converted from OSCE)
}

/**
 * AMC Rubric Score (from validation results)
 */
export interface AMCRubricScore {
  // AMC categories are well-known keys, but backend score_breakdown may emit
  // additional category keys — keep this a string so both are representable.
  category: string;
  score: number; // 0-3 (AMC category scale)
  max_score: number; // 3 for AMC categories
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
 * Rubric score entry as returned for the EMR validation results page.
 * `max_score` / `feedback` are optional because the score_breakdown payload
 * may omit them (defaults applied when rendering).
 */
export interface EMRRubricScore {
  category: string;
  score: number;
  max_score?: number;
  feedback?: string;
}

/**
 * Raw validation result payload consumed by the EMR validation results page.
 *
 * Models the flat "score_breakdown" shape the backend returns, and is tolerant
 * of the legacy nested `validation_results` envelope and alternate field names
 * (`red_flags` → critical errors, `improvements` → areas for improvement,
 * `category_scores` → rubric) so the page works across backend versions.
 */
export interface EMRValidationApiResult {
  status?: ValidationStatus;
  validation_status?: ValidationStatus;
  overall_score?: number;
  /**
   * Authoritative backend PASS/FAIL decision (threshold 9/15 plus automatic
   * FAIL on committed critical errors / omitted must-not-miss elements).
   * `null` only when the AI assessment layer was unavailable and the session
   * was left ungraded.
   */
  pass_fail?: boolean | string | null;
  amc_rubric_scores?: EMRRubricScore[];
  /** AMC category scores, each on a 0-3 scale (five categories, total 15). */
  category_scores?: Record<string, number>;
  missing_elements?: string[];
  /** Answer-key elements the student documented. */
  captured?: string[];
  /** Per-section completeness percentages (null when ungraded). */
  completeness?: EMRCompleteness | null;
  critical_errors_committed?: string[];
  red_flags?: string[];
  strengths?: string[];
  areas_for_improvement?: string[];
  improvements?: string[];
  ahpra_compliance?: boolean;
  /**
   * `true` when the Claude assessment layer was temporarily down: the session
   * is left `in_progress` (NOT graded), `pass_fail` is null and overall_score
   * is 0 — the student must re-submit.
   */
  ai_unavailable?: boolean | null;
  /** Legacy envelope: real backend SessionResponse nests results here. */
  validation_results?: EMRValidationApiResult;
}

/**
 * Per-section documentation completeness (%), as returned by the backend.
 */
export interface EMRCompleteness {
  subjective: number;
  objective: number;
  assessment: number;
  plan: number;
}

/**
 * Normalised, render-ready view of a validation result.
 */
export interface EMRValidationView {
  isComplete: boolean;
  /**
   * `true` when the AI assessment layer was unavailable: the session is
   * ungraded and the page must show a re-submit prompt instead of PASS/FAIL.
   */
  aiUnavailable: boolean;
  passed: boolean;
  overallScore: number;
  rubricScores: AMCRubricScore[];
  missingElements: string[];
  criticalErrors: string[];
  strengths: string[];
  areasForImprovement: string[];
  ahpraCompliance: boolean;
}

/**
 * EMR Case Summary (from GET /emr/cases — "pick a case and practice")
 *
 * A lightweight patient summary used to populate the case picker. `id` is the
 * patient UUID passed to POST /emr/sessions/start as `patient_id`.
 */
export interface EMRCaseSummary {
  id: string;
  mrn: string;
  name: string;
  age: number;
  gender: string;
  presenting_complaint: string;
  specialty: string;
  difficulty: string;
}

/**
 * Response envelope for GET /emr/cases.
 */
export interface EMRCaseListResponse {
  total: number;
  cases: EMRCaseSummary[];
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
