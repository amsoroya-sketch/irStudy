/**
 * OSCE Type Definitions
 * Types for OSCE scenarios and AMC 15-mark rubric
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC (Australian Medical Council) 15-mark rubric
 * - Used for AMC Clinical Examination assessment
 * - Pass threshold: ≥10 marks out of 15
 */

/**
 * AMC 15-Mark Rubric Domain
 * Each domain has specific mark range and behavioral anchors
 */
export interface AMCRubricDomain {
  /** Domain name (e.g., "Communication Skills") */
  name: string;
  /** Maximum marks for this domain */
  maxMarks: number;
  /** Description of what this domain assesses */
  description: string;
  /** Behavioral anchors for each mark level */
  behavioralAnchors: Record<number, string>;
}

/**
 * AMC 15-Mark Rubric Score
 * Complete scoring breakdown for an OSCE station
 */
export interface AMCRubricScore {
  /** Communication Skills (0-3 marks) */
  communicationSkills: number;
  /** Clinical Reasoning (0-4 marks) */
  clinicalReasoning: number;
  /** Information Gathering (0-3 marks) */
  informationGathering: number;
  /** Management Plan (0-3 marks) */
  managementPlan: number;
  /** Professionalism & Ethics (0-2 marks) */
  professionalismEthics: number;
  /** Total score out of 15 */
  totalScore: number;
  /** Whether student passed (≥10 marks) */
  passed: boolean;
}

/**
 * OSCE Scenario
 * Clinical scenario for practice
 */
export interface OSCEScenario {
  /** Unique scenario ID */
  id: string;
  /** Title of scenario */
  title: string;
  /** Brief description */
  description: string;
  /** Medical specialty */
  specialty: string;
  /** Difficulty level */
  difficulty: 'easy' | 'medium' | 'hard';
  /** Time limit in minutes (usually 8 minutes) */
  timeLimitMinutes: number;
  /** Patient presentation summary */
  patientPresentation: string;
  /** Learning objectives */
  learningObjectives: string[];
}

/**
 * OSCE Session Status
 * Tracks current state of OSCE practice session
 */
export type OSCESessionStatus =
  | 'not_started'
  | 'in_progress'
  | 'completed'
  | 'abandoned';

/**
 * OSCE Session
 * Full OSCE practice session data
 */
export interface OSCESession {
  /** Unique session ID */
  id: string;
  /** Associated scenario */
  scenario: OSCEScenario;
  /** Session status */
  status: OSCESessionStatus;
  /** Start time */
  startedAt?: Date;
  /** End time */
  completedAt?: Date;
  /** Final rubric score (after completion) */
  rubricScore?: AMCRubricScore;
}
