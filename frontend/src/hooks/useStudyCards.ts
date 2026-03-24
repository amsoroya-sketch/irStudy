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
import { StudyCardsResponse } from '../types/study-cards';

/**
 * Hook to fetch study cards due for review
 * @param due - Filter by cards due for review (default: true)
 * @returns React Query result with cards data
 */
export const useStudyCards = (
  due: boolean = true
): UseQueryResult<StudyCardsResponse, Error> => {
  return useQuery({
    queryKey: ['studyCards', due ? 'due' : 'all'],
    queryFn: () => getStudyCards(due),
  });
};
