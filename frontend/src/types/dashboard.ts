/**
 * Dashboard Analytics Types
 * TypeScript interfaces matching backend progress API schemas
 */

// ===== Specialty Performance =====

export interface SpecialtyPerformance {
  specialty: string;
  total_attempts: number;
  correct_attempts: number;
  accuracy_rate: number;
  average_time_seconds: number;
}

// ===== Weak Area =====

export interface WeakArea {
  specialty: string;
  accuracy_rate: number;
  total_attempts: number;
  recommended_study_cards: number;
}

// ===== Weekly Trend =====

export interface WeeklyTrend {
  week_start: string; // ISO 8601 datetime string
  mcq_attempts: number;
  accuracy_rate: number;
  study_cards_reviewed: number;
}

// ===== Dashboard Response =====

export interface DashboardData {
  total_mcq_attempts: number;
  mcq_accuracy_rate: number;
  total_osce_completions: number;
  study_cards_reviewed: number;
  study_card_retention_rate: number;
  specialty_breakdown: SpecialtyPerformance[];
  weak_areas: WeakArea[];
}

// ===== Weekly Trends Response =====

export interface WeeklyTrendsResponse {
  weeks: number;
  trends: WeeklyTrend[];
}

// ===== Weak Areas Response =====

export interface WeakAreasResponse {
  threshold: number;
  min_attempts: number;
  weak_areas: WeakArea[];
}
