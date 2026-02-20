/**
 * EMR Dashboard Data Hook
 *
 * Fix #3: Dashboard Load Performance (Parallel API Requests)
 *
 * Problem: Sequential API calls cause slow dashboard load (>2s)
 * Solution: Use TanStack Query's useQueries to fetch all data in PARALLEL
 *
 * Performance Improvement:
 * - Before: 500ms + 500ms + 500ms + 500ms = 2000ms (sequential)
 * - After: max(500ms, 500ms, 500ms, 500ms) = 500ms (parallel)
 *
 * Features:
 * - Fetches 4 API endpoints simultaneously
 * - Caching with staleTime (5-10 minutes)
 * - Loading state aggregation (any loading = true)
 * - Error state aggregation (any error = true)
 * - Type-safe data structure
 *
 * Usage:
 * ```tsx
 * const { data, isLoading, isError } = useEMRDashboardData(userId);
 *
 * if (isLoading) return <Skeleton />;
 * if (isError) return <ErrorMessage />;
 *
 * return (
 *   <div>
 *     <EMRMetricsGrid metrics={data.metrics} />
 *     <RecentSessionsList sessions={data.recentSessions} />
 *     <UnifiedProgressChart trends={data.weeklyTrends} />
 *     <WeakAreasPanel weakAreas={data.weakAreas} />
 *   </div>
 * );
 * ```
 */

import { useQueries } from '@tanstack/react-query';
import { axiosInstance } from '../api/axiosInstance';

// Type Definitions
interface EMRMetrics {
  total_sessions: number;
  completed_sessions: number;
  in_progress_sessions: number;
  avg_validation_score: number;
  avg_typing_wpm: number;
  improvement_percentage: number;
  ahpra_compliance_rate: number;
  total_time_spent_seconds: number;
  epic_sessions: number;
  cerner_sessions: number;
  specialty_stats: Array<{
    specialty: string;
    session_count: number;
    avg_score: number;
  }>;
}

interface RecentSession {
  session_id: string;
  patient_name: string;
  specialty: string;
  emr_system: 'epic' | 'cerner';
  started_at: string;
  completed_at: string | null;
  validation_score: number | null;
  is_active: boolean;
}

interface WeeklyTrend {
  week_start: string;
  mcq_accuracy: number | null;
  osce_avg_score: number | null;
  emr_avg_score: number | null;
  mcq_attempts: number;
  osce_completions: number;
  emr_sessions: number;
}

interface WeakArea {
  specialty: string;
  session_count: number;
  avg_score: number;
  gap_to_target: number;
  recommended_practice_count: number;
}

interface DashboardData {
  metrics: EMRMetrics | undefined;
  recentSessions: RecentSession[] | undefined;
  weeklyTrends: WeeklyTrend[] | undefined;
  weakAreas: WeakArea[] | undefined;
}

interface DashboardQueryResult {
  data: DashboardData;
  isLoading: boolean;
  isError: boolean;
  errors: Array<Error | null>;
}

/**
 * Fetch EMR Dashboard Data (Parallel Queries)
 *
 * @param userId - Current user ID (from auth context)
 * @returns Dashboard data + loading/error states
 */
export const useEMRDashboardData = (userId: string): DashboardQueryResult => {
  // Run 4 queries in PARALLEL (not sequential)
  const results = useQueries({
    queries: [
      // Query 1: EMR Metrics (sessions, avg score, compliance)
      {
        queryKey: ['emr', 'dashboard', 'metrics', userId],
        queryFn: async () => {
          const response = await axiosInstance.get<EMRMetrics>(
            '/api/v1/progress/dashboard/emr'
          );
          return response.data;
        },
        staleTime: 5 * 60 * 1000, // 5 minutes (dashboard data doesn't change often)
        retry: 2, // Retry failed requests 2 times
        retryDelay: 1000, // Wait 1s between retries
      },

      // Query 2: Recent EMR Sessions (last 10 sessions)
      {
        queryKey: ['emr', 'sessions', 'recent', userId],
        queryFn: async () => {
          const response = await axiosInstance.get<{ sessions: RecentSession[] }>(
            '/api/v1/emr/sessions',
            {
              params: {
                limit: 10,
                sort_by: 'created_at',
                sort_order: 'desc',
              },
            }
          );
          return response.data.sessions;
        },
        staleTime: 2 * 60 * 1000, // 2 minutes (recent sessions update frequently)
        retry: 2,
        retryDelay: 1000,
      },

      // Query 3: Unified Weekly Trends (MCQ + OSCE + EMR)
      {
        queryKey: ['progress', 'weekly-trends', 'unified', userId],
        queryFn: async () => {
          const response = await axiosInstance.get<{ trends: WeeklyTrend[] }>(
            '/api/v1/progress/weekly-trends/unified',
            {
              params: {
                weeks: 12, // Last 12 weeks
              },
            }
          );
          return response.data.trends;
        },
        staleTime: 10 * 60 * 1000, // 10 minutes (trends data is expensive to calculate)
        retry: 2,
        retryDelay: 1000,
      },

      // Query 4: EMR Weak Areas (specialties <70% avg score)
      {
        queryKey: ['progress', 'weak-areas', 'emr', userId],
        queryFn: async () => {
          const response = await axiosInstance.get<{ weak_areas: WeakArea[] }>(
            '/api/v1/progress/weak-areas/emr',
            {
              params: {
                limit: 5, // Top 5 weak areas
              },
            }
          );
          return response.data.weak_areas;
        },
        staleTime: 5 * 60 * 1000, // 5 minutes
        retry: 2,
        retryDelay: 1000,
      },
    ],
  });

  // Combine results
  return {
    data: {
      metrics: results[0].data,
      recentSessions: results[1].data,
      weeklyTrends: results[2].data,
      weakAreas: results[3].data,
    },
    isLoading: results.some((result) => result.isLoading),
    isError: results.some((result) => result.isError),
    errors: results.map((result) => result.error as Error | null),
  };
};

export default useEMRDashboardData;
