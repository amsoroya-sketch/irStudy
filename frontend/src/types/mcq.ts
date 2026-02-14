/**
 * MCQ Type Definitions
 * Matches backend MCQ schemas from TASK_002
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - All drug names must be Australian (paracetamol NOT acetaminophen)
 * - Citations reference Australian guidelines (eTG, AHPRA, AMH, PBS)
 * - SI units only (mmol/L NOT mg/dL)
 */

/**
 * Difficulty levels matching backend enum
 */
export type DifficultyLevel = 'easy' | 'medium' | 'hard';

/**
 * Medical specialties matching backend enum
 */
export type MedicalSpecialty =
  | 'cardiology'
  | 'respiratory'
  | 'gastroenterology'
  | 'neurology'
  | 'psychiatry'
  | 'endocrinology'
  | 'emergency_medicine'
  | 'general_practice'
  | 'paediatrics'
  | 'obstetrics_gynaecology'
  | 'surgery';

/**
 * Answer option letter (A-E)
 */
export type AnswerOption = 'A' | 'B' | 'C' | 'D' | 'E';

/**
 * MCQ options dictionary (matches backend Dict[str, str])
 */
export interface MCQOptions {
  A: string;
  B: string;
  C: string;
  D: string;
  E?: string;
}

/**
 * Public MCQ (for practice - no answer revealed)
 * Matches backend MCQPublic schema
 */
export interface MCQPublic {
  id: number;
  question_id: string;
  question_text: string;
  options: MCQOptions;
  specialty: MedicalSpecialty;
  difficulty: DifficultyLevel;
  tags: string[] | null;
  image_url: string | null;
  image_caption: string | null;
  times_attempted: number;
  success_rate: number;
  created_at: string;
}

/**
 * MCQ with answer (for review after attempt)
 * Matches backend MCQWithAnswer schema
 */
export interface MCQWithAnswer extends MCQPublic {
  correct_answer: AnswerOption;
  explanation: string;
  citation: string;
  learning_points: string[] | null;
}

/**
 * MCQ attempt submission
 * Matches backend MCQAttemptCreate schema
 */
export interface MCQAttemptCreate {
  mcq_id: number;
  selected_answer: AnswerOption;
  time_taken_seconds: number;
  confidence_level?: number; // 1-5
}

/**
 * Response after submitting MCQ attempt
 * Matches backend MCQAttemptResponse schema
 */
export interface MCQAttemptResponse {
  id: number;
  is_correct: boolean;
  selected_answer: AnswerOption;
  correct_answer: AnswerOption;
  explanation: string;
  citation: string;
  learning_points: string[] | null;
  time_taken_seconds: number;
  attempt_number: number;
}

/**
 * MCQ practice state for UI component
 */
export interface MCQPracticeState {
  currentMCQ: MCQPublic | null;
  selectedAnswer: AnswerOption | null;
  isSubmitted: boolean;
  result: MCQAttemptResponse | null;
  timeRemaining: number;
  isLoading: boolean;
  error: string | null;
}

/**
 * MCQ statistics
 * Matches backend MCQStatistics schema
 */
export interface MCQStatistics {
  total_mcqs: number;
  by_specialty: Record<string, number>;
  by_difficulty: Record<string, number>;
  average_success_rate: number;
}

// ============================================================================
// LEGACY INTERFACES (Backwards compatibility - to be deprecated)
// ============================================================================

/**
 * @deprecated Use MCQPublic instead
 */
export interface MCQ {
  id: number;
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  option_e: string;
  correct_answer: AnswerOption;
  explanation: string;
  category: string;
  difficulty: DifficultyLevel;
  tags: string[];
  image_url?: string;
  citation?: string;
  created_at: string;
  updated_at: string;
}

/**
 * @deprecated Use MCQPublic with filters instead
 */
export interface MCQListParams extends Record<string, unknown> {
  skip?: number;
  limit?: number;
  category?: string;
  difficulty?: DifficultyLevel;
  tags?: string[];
  search?: string;
}

/**
 * @deprecated Use MCQPublic[] instead
 */
export interface MCQListResponse {
  items: MCQ[];
  total: number;
  skip: number;
  limit: number;
}

/**
 * @deprecated Use MCQAttemptResponse instead
 */
export interface MCQAttempt {
  id: number;
  mcq_id: number;
  user_id: number;
  selected_answer: AnswerOption;
  is_correct: boolean;
  time_spent_seconds: number;
  attempted_at: string;
}

/**
 * @deprecated Use MCQAttemptCreate instead
 */
export interface CreateMCQAttemptRequest {
  mcq_id: number;
  selected_answer: AnswerOption;
  time_spent_seconds: number;
}

/**
 * @deprecated Use MCQAttemptResponse instead
 */
export interface CreateMCQAttemptResponse {
  attempt: MCQAttempt;
  is_correct: boolean;
  correct_answer: AnswerOption;
  explanation: string;
}

/**
 * @deprecated Not used in current API
 */
export interface CreateMCQRequest {
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  option_e: string;
  correct_answer: AnswerOption;
  explanation: string;
  category: string;
  difficulty: DifficultyLevel;
  tags: string[];
  image_url?: string;
  citation?: string;
}

/**
 * @deprecated Not used in current API
 */
export type UpdateMCQRequest = Partial<CreateMCQRequest>;
