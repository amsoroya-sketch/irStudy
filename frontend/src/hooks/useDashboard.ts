/**
 * useDashboard Hooks
 * React Query hooks for dashboard analytics and progress tracking
 */

import { useQuery } from '@tanstack/react-query';
import { axiosInstance } from '../api/client';
import { queryKeys } from '../api/queryConfig';
import type { DashboardData, WeeklyTrendsResponse, WeakAreasResponse } from '../types/dashboard';

/**
 * Fetch comprehensive dashboard analytics
 *
 * Endpoint: GET /api/v1/progress/dashboard
 *
 * Returns:
 * - Total MCQ attempts and accuracy
 * - Total OSCE completions
 * - Study cards reviewed and retention rate
 * - Specialty breakdown (performance per specialty)
 * - Weak areas (specialties below 70% threshold)
 *
 * Cache: 5 minutes (staleTime)
 */
export const useDashboard = () => {
  return useQuery({
    queryKey: queryKeys.user.progress.dashboard(),
    queryFn: async () => {
      const { data } = await axiosInstance.get<DashboardData>('/progress/dashboard');
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Fetch weekly progress trends
 *
 * Endpoint: GET /api/v1/progress/trends/weekly?weeks=X
 *
 * Args:
 * - weeks: Number of weeks to retrieve (1-12, default 4)
 *
 * Returns:
 * - Weekly trend data (most recent first)
 *   - week_start: Start date of the week
 *   - mcq_attempts: MCQ attempts during this week
 *   - accuracy_rate: Success percentage for this week
 *   - study_cards_reviewed: Study cards reviewed during this week
 *
 * Cache: 5 minutes (staleTime)
 */
export const useWeeklyTrends = (weeks: number = 4) => {
  return useQuery({
    queryKey: queryKeys.user.progress.trends(weeks),
    queryFn: async () => {
      const { data } = await axiosInstance.get<WeeklyTrendsResponse>(
        '/progress/trends/weekly',
        { params: { weeks } }
      );
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    enabled: weeks > 0 && weeks <= 12, // Only fetch if weeks is valid
  });
};

/**
 * Fetch weak areas (specialties needing improvement)
 *
 * Endpoint: GET /api/v1/progress/weak-areas?threshold=X&min_attempts=Y
 *
 * Query Parameters:
 * - threshold: Accuracy threshold percentage (0-100, default 70.0)
 * - min_attempts: Minimum attempts required (1-50, default 5)
 *
 * Returns:
 * - Weak specialties with recommendations
 *   - specialty: Specialty name
 *   - accuracy_rate: Success percentage
 *   - total_attempts: Total attempts
 *   - recommended_study_cards: Available study cards count
 *
 * Cache: 5 minutes (staleTime)
 */
export const useWeakAreas = (threshold: number = 70.0, minAttempts: number = 5) => {
  return useQuery({
    queryKey: [...queryKeys.user.progress.weakAreas(), threshold, minAttempts],
    queryFn: async () => {
      const { data } = await axiosInstance.get<WeakAreasResponse>('/progress/weak-areas', {
        params: {
          threshold,
          min_attempts: minAttempts,
        },
      });
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    enabled: threshold >= 0 && threshold <= 100 && minAttempts >= 1 && minAttempts <= 50,
  });
};
