/**
 * Dashboard API Client
 * React Query hooks for MVP dashboard overview endpoint
 *
 * Author: react-frontend-developer
 * Date: 2026-05-25
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - Dashboard aggregates progress across MCQ, OSCE, EMR, Mock Exam modules
 * - Specialty breakdown includes Australian specialties (cardiology, respiratory, psychiatry)
 * - All scores based on Australian medical standards (FRACP/AMC)
 *
 * SECURITY:
 * - Uses environment variable for API URL (VITE_API_URL)
 * - JWT token automatically added by axiosInstance interceptor
 * - No hardcoded credentials or API endpoints
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import axiosInstance from '../utils/axiosInstance';
import { queryKeys } from './queryConfig';
import type { DashboardOverviewResponse } from '../types/dashboard';

/**
 * Fetch dashboard overview data
 *
 * Endpoint: GET /api/v1/dashboard/overview
 *
 * Returns:
 * - overall_progress: Total sessions, completion %, avg score, time spent
 * - modules: Stats for MCQ, OSCE, EMR, Mock Exam (attempts, scores, completion rates)
 * - specialty_breakdown: Performance by specialty (cardiology, respiratory, psychiatry, etc.)
 * - recent_activity: Last 10 activities across all modules
 * - recommendations: Personalized suggestions for improvement
 *
 * Cache: 5 minutes (staleTime)
 * Refetch: On window focus disabled (user-initiated only)
 *
 * Example:
 * ```tsx
 * const { data, isLoading, error, refetch } = useDashboardOverview();
 *
 * if (isLoading) return <CircularProgress />;
 * if (error) return <Alert severity="error">{error.message}</Alert>;
 *
 * return (
 *   <Box>
 *     <Typography>Total Sessions: {data.overall_progress.total_sessions}</Typography>
 *     <Typography>Avg Score: {data.overall_progress.avg_score}%</Typography>
 *   </Box>
 * );
 * ```
 */
export const useDashboardOverview = (): UseQueryResult<DashboardOverviewResponse, Error> => {
  return useQuery({
    queryKey: queryKeys.user.progress.dashboard(),
    queryFn: async () => {
      const { data } = await axiosInstance.get<DashboardOverviewResponse>('/dashboard/overview');
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    refetchOnWindowFocus: false, // Only refetch when user explicitly requests
    refetchOnReconnect: true, // Refetch when internet reconnects
  });
};
