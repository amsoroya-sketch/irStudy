/**
 * useMCQs Hook
 * React Query hook for fetching and managing MCQs
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { axiosInstance } from '../api/client';
import { queryKeys } from '../api/queryConfig';
import type { MCQ, MCQListParams, MCQAttemptRequest, MCQAttemptResponse } from '../types/api';

/**
 * Fetch list of MCQs with optional filters
 */
export const useMCQs = (params?: MCQListParams) => {
  return useQuery({
    queryKey: queryKeys.mcqs.list(params as Record<string, unknown>),
    queryFn: async () => {
      const { data } = await axiosInstance.get<MCQ[]>('/mcqs', { params });
      return data;
    },
    enabled: true, // Always fetch
  });
};

/**
 * Fetch single MCQ by ID
 */
export const useMCQ = (questionId: string) => {
  return useQuery({
    queryKey: queryKeys.mcqs.detail(questionId),
    queryFn: async () => {
      const { data } = await axiosInstance.get<MCQ>(`/mcqs/${questionId}`);
      return data;
    },
    enabled: !!questionId, // Only fetch if ID provided
  });
};

/**
 * Submit MCQ attempt
 */
export const useSubmitMCQAttempt = (questionId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (attemptData: MCQAttemptRequest) => {
      const { data} = await axiosInstance.post<MCQAttemptResponse>(
        `/mcqs/${questionId}/attempt`,
        attemptData
      );
      return data;
    },
    onSuccess: () => {
      // Invalidate MCQ data to refetch updated statistics
      queryClient.invalidateQueries({ queryKey: queryKeys.mcqs.detail(questionId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.user.progress.dashboard() });
    },
  });
};

/**
 * Fetch MCQ statistics
 */
export const useMCQStatistics = () => {
  return useQuery({
    queryKey: queryKeys.mcqs.statistics(),
    queryFn: async () => {
      const { data } = await axiosInstance.get('/mcqs/statistics');
      return data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes - stats don't change frequently
  });
};

/**
 * Get MCQ explanation (after attempt)
 */
export const useMCQExplanation = (questionId: string, enabled = false) => {
  return useQuery({
    queryKey: [...queryKeys.mcqs.detail(questionId), 'explanation'],
    queryFn: async () => {
      const { data } = await axiosInstance.get(`/mcqs/${questionId}/explanation`);
      return data;
    },
    enabled, // Only fetch when explicitly enabled (after submission)
  });
};
