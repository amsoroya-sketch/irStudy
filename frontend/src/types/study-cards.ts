/**
 * Study Cards TypeScript Types
 * Based on PRD-P1-005 Auto Study Card Generation
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - All citations reference Australian sources (eTG, Talley & O'Connor, AMH, PBS)
// SECURITY SCAN EXEMPTION: Validation documentation pattern
 * - Drug names follow Australian conventions (paracetamol NOT acetaminophen)
 * - SI units required (mmol/L NOT mg/dL)
 */

/**
 * Citation for study card content (RAG-based)
 */
export interface StudyCardCitation {
  source: string; // e.g., "Talley & O'Connor Clinical Examination 9th Ed"
  qdrant_point_id: string; // UUID reference to Qdrant vector database
  confidence: number; // 0.0-1.0 (RAG confidence score)
  page: string; // Page number or section reference
}

/**
 * SM-2 Algorithm Parameters
 * Based on SuperMemo-2 spaced repetition algorithm
 */
export interface SM2Params {
  ease_factor: number; // 1.3-3.0 (default 2.5)
  interval_days: number; // Days until next review
  repetitions: number; // Number of successful repetitions
}

/**
 * Study Card (single flashcard)
 */
export interface StudyCard {
  id: number; // Database primary key
  card_id: string; // Format: "CARD-{session_id}-{index}"
  user_id: number | null; // User ID or null for public cards
  session_id: string; // UUID (OSCE session reference)
  question: string; // Clinical question
  answer: string; // Clinical answer with explanation
  citations: StudyCardCitation[]; // RAG citations (min 1, max 5)
  sm2_params: SM2Params; // Spaced repetition parameters
  next_review_date: string; // ISO 8601 datetime
  last_reviewed_at: string | null; // ISO 8601 datetime or null
  specialty: string; // e.g., "cardiology", "neurology"
  topic: string; // e.g., "Chest Pain Assessment"
  subtopic: string | null; // Optional subtopic
  difficulty: 'easy' | 'medium' | 'hard';
  tags: string[]; // e.g., ["SOCRATES", "red flags", "differential diagnosis"]
  card_type: 'history_taking' | 'physical_exam' | 'differential_dx' | 'investigation' | 'management';
  is_active: boolean;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}

/**
 * Study Cards Due Response (from GET /api/v1/study-cards/due-cards)
 */
export interface StudyCardsDueResponse {
  cards: StudyCard[];
  total_due: number;
}

/**
 * Performance to SM-2 quality mapping
 * Maps user-friendly ratings to SM-2 integer quality values (0-5)
 */
export const performanceToQuality = {
  again: 0,
  hard: 1,
  good: 3,
  easy: 5,
} as const;

export type PerformanceRating = keyof typeof performanceToQuality;

/**
 * Review Request (POST /api/v1/study-cards/review)
 */
export interface ReviewCardRequest {
  card_id: number;
  quality: number; // 0-5
  time_taken_seconds: number;
}

/**
 * Review Response
 */
export interface StudyCardReviewResponse {
  card_id: number;
  quality: number;
  next_review_date: string;
  interval_days: number;
  ease_factor: number;
  repetitions: number;
  message: string;
  quality_description: string;
}
