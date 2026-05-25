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

// ===== MVP Dashboard Types (PRD-MVP-002) =====
// Matches backend schema from PRD-MVP-001 (backend/src/api/v1/dashboard/router.py)

export interface OverallProgress {
  total_sessions: number;
  completion_percentage: number;
  avg_score: number;
  total_time_minutes: number;
  last_activity: string | null;
}

export interface ModuleStats {
  total_attempts?: number; // MCQ, OSCE
  total_sessions?: number; // EMR
  total_exams?: number; // Mock Exam
  average_score: number;
  last_activity: string | null;
  completion_rate: number;
}

export interface SpecialtyBreakdown {
  specialty: string;
  attempts: number;
  avg_score: number;
  strength?: 'weak' | 'average' | 'good' | 'excellent';
}

export interface RecentActivity {
  type: 'mcq' | 'osce' | 'emr' | 'mock_exam';
  description: string;
  score: number | null;
  timestamp: string;
}

export interface Recommendation {
  module: string;
  specialty: string;
  reason: string;
  priority: 'high' | 'medium' | 'low';
}

export interface DashboardOverviewResponse {
  overall_progress: OverallProgress;
  modules: {
    mcq: ModuleStats;
    osce: ModuleStats;
    emr: ModuleStats;
    mock_exam: ModuleStats;
  };
  specialty_breakdown: SpecialtyBreakdown[];
  recent_activity: RecentActivity[];
  recommendations: Recommendation[];
}
