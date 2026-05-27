/**
 * useStudyCards Hook
 * React Query hook for fetching study cards
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - All content validated for Australian medical standards
 * - Citations reference Australian sources (eTG, Talley & O'Connor, AMH, PBS)
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { getStudyCards } from '../api/studyCards';
import { StudyCardsDueResponse } from '../types/study-cards';

/**
 * Hook to fetch study cards due for review
 * @param limit - Maximum cards to return (default: 20)
 * @returns React Query result with cards data
 */
export const useStudyCards = (
  limit: number = 20
): UseQueryResult<StudyCardsDueResponse, Error> => {
  return useQuery({
    queryKey: ['studyCards', 'due'],
    queryFn: () => getStudyCards(limit),
  });
};
