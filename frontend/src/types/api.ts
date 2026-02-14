/**
 * API Response Types
 * TypeScript interfaces for backend API responses
 */

// ===== Common Types =====

export type DifficultyLevel = 'easy' | 'medium' | 'hard';
export type MedicalSpecialty =
  | 'general_practice'
  | 'cardiology'
  | 'respiratory'
  | 'gastroenterology'
  | 'neurology'
  | 'psychiatry'
  | 'endocrinology'
  | 'pediatrics'
  | 'obstetrics_gynecology'
  | 'surgery';

export type OSCEType =
  | 'history_taking'
  | 'physical_examination'
  | 'counselling'
  | 'emergency_scenario'
  | 'procedural_skills'
  | 'communication';

// ===== MCQ Types =====

export interface MCQOption {
  A: string;
  B: string;
  C: string;
  D: string;
  E?: string;
}

export interface MCQ {
  id: number;
  question_id: string;
  question_text: string;
  options: MCQOption;
  correct_answer: string;
  explanation: string;
  specialty: MedicalSpecialty;
  difficulty: DifficultyLevel;
  tags: string[];
  image_url?: string | null;
  image_caption?: string | null;
  times_practiced: number;
  average_score: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface MCQListParams {
  skip?: number;
  limit?: number;
  specialty?: MedicalSpecialty;
  difficulty?: DifficultyLevel;
  tags?: string[];
}

export interface MCQAttemptRequest {
  selected_answer: string;
  time_taken_seconds?: number;
}

export interface MCQAttemptResponse {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  user_answer: string;
}

// ===== OSCE Types =====

export interface OSCERubricItem {
  item: string;
  points: number;
  description?: string;
}

export interface VideoResource {
  title: string;
  url: string;
  source: string;
  duration_minutes?: number;
  focus: string;
  why_recommended: string;
  australian_relevance?: string;
}

export interface VideoResources {
  essential_videos: VideoResource[];
  supplementary_videos: VideoResource[];
}

export interface OSCE {
  id: number;
  osce_id: string;
  station_title: string;
  station_type: OSCEType;
  patient_instructions: string;
  candidate_instructions: string;
  examiner_instructions?: string;
  rubric: OSCERubricItem[];
  specialty: MedicalSpecialty;
  difficulty: DifficultyLevel;
  time_limit_minutes: number;
  learning_objectives?: string[];
  key_points?: string[];
  red_flags?: string[];
  australian_guidelines?: Record<string, unknown>;
  supporting_documents?: Array<{
    type: string;
    url: string;
    caption: string;
  }>;
  video_resources?: VideoResources;
  times_practiced: number;
  average_score: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface OSCEListParams {
  skip?: number;
  limit?: number;
  specialty?: MedicalSpecialty;
  station_type?: OSCEType;
  difficulty?: DifficultyLevel;
}

export interface OSCEPracticeRequest {
  performance_notes?: string;
  time_taken_seconds?: number;
  self_score?: number;
}

export interface OSCEPracticeResponse {
  practice_id: number;
  feedback: string;
  created_at: string;
}

// ===== User & Progress Types =====

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'student' | 'educator' | 'admin';
  is_active: boolean;
  created_at: string;
}

export interface ProgressDashboard {
  total_mcqs_attempted: number;
  total_osces_practiced: number;
  overall_mcq_accuracy: number;
  overall_osce_score: number;
  weak_specialties: Array<{
    specialty: MedicalSpecialty;
    accuracy: number;
    count: number;
  }>;
  recent_activity: Array<{
    type: 'mcq' | 'osce';
    id: string;
    title: string;
    score: number;
    created_at: string;
  }>;
  study_streak_days: number;
  total_study_time_minutes: number;
}

export interface WeakArea {
  specialty: MedicalSpecialty;
  topic: string;
  accuracy: number;
  total_attempts: number;
  recommended_mcqs: number[];
}

export interface ProgressStats {
  mcqs_by_specialty: Record<MedicalSpecialty, {
    attempted: number;
    correct: number;
    accuracy: number;
  }>;
  osces_by_specialty: Record<MedicalSpecialty, {
    practiced: number;
    average_score: number;
  }>;
  daily_activity: Array<{
    date: string;
    mcqs_attempted: number;
    osces_practiced: number;
  }>;
}

// ===== Authentication Types =====

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface RegisterResponse {
  user: User;
  message: string;
}

// ===== API Error Response =====

export interface APIError {
  detail: string;
  status_code: number;
}
