/**
 * MCQ Custom Hooks
 * TanStack Query hooks for MCQ operations
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - All MCQs use Australian drug names and guidelines
 * - Citations reference Australian sources (eTG, AHPRA, AMH, PBS)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getRandomMCQ, submitMCQAnswer } from '../api/mcqs';
import {
  MCQPublic,
  MCQAttemptCreate,
  MCQAttemptResponse,
  DifficultyLevel,
  MedicalSpecialty,
} from '../types/mcq';

/**
 * Query key factory for MCQ queries
 */
export const mcqKeys = {
  all: ['mcqs'] as const,
  random: (specialty?: MedicalSpecialty, difficulty?: DifficultyLevel) =>
    [...mcqKeys.all, 'random', specialty, difficulty] as const,
};

/**
 * Hook to fetch random MCQ with optional filtering
 *
 * @param specialty - Filter by medical specialty (optional)
 * @param difficulty - Filter by difficulty level (optional)
 * @returns Query result with MCQ data, loading state, and error
 *
 * Usage:
 * ```tsx
 * const { data: mcq, isLoading, error, refetch } = useMCQ('cardiology', 'medium');
 *
 * // Fetch new MCQ
 * refetch();
 * ```
 */
export const useMCQ = (specialty?: MedicalSpecialty, difficulty?: DifficultyLevel) => {
  return useQuery<MCQPublic, Error>({
    queryKey: mcqKeys.random(specialty, difficulty),
    queryFn: () => getRandomMCQ(specialty, difficulty),
    // Don't refetch automatically - user controls when to get new MCQ
    staleTime: Infinity,
    gcTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
};

/**
 * Hook to submit MCQ answer attempt
 *
 * @returns Mutation object with submit function and result
 *
 * Usage:
 * ```tsx
 * const { mutate: submitAnswer, isPending, data: result } = useSubmitMCQ();
 *
 * const handleSubmit = () => {
 *   submitAnswer({
 *     mcqId: 123,
 *     attemptData: {
 *       mcq_id: 123,
 *       selected_answer: 'C',
 *       time_taken_seconds: 45,
 *       confidence_level: 4,
 *     }
 *   }, {
 *     onSuccess: (result) => {
 *       if (result.is_correct) {
 *         console.log('Correct!');
 *       }
 *     }
 *   });
 * };
 * ```
 */
export const useSubmitMCQ = () => {
  const queryClient = useQueryClient();

  return useMutation<
    MCQAttemptResponse,
    Error,
    { mcqId: number; attemptData: MCQAttemptCreate }
  >({
    mutationFn: ({ mcqId, attemptData }) => submitMCQAnswer(mcqId, attemptData),
    onSuccess: () => {
      // Invalidate random MCQ query to allow fetching new questions
      queryClient.invalidateQueries({ queryKey: mcqKeys.all });
    },
  });
};