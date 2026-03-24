/**
 * Study Cards API Client
 * Integrates with backend study cards endpoints from PRD-P1-005
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - All content validated for Australian medical standards
 * - Citations reference Australian sources (eTG, Talley & O'Connor, AMH, PBS)
 * - Drug names follow Australian conventions (paracetamol NOT acetaminophen)
 */

import axiosInstance from './client';
import {
  StudyCardsResponse,
  ReviewCardRequest,
  ReviewCardResponse,
} from '../types/study-cards';

/**
 * Get study cards due for review
 * @param due - Filter by cards due for review (default: true)
 * @returns Study cards response with cards and total count
 */
export const getStudyCards = async (due: boolean = true): Promise<StudyCardsResponse> => {
  const response = await axiosInstance.get<StudyCardsResponse>('/study-cards', {
    params: { due },
  });
  return response.data;
};

/**
 * Review a study card (SM-2 algorithm update)
 * @param cardId - Card ID to review
 * @param request - Review performance rating
 * @returns Updated SM-2 parameters and next review date
 */
export const reviewCard = async (
  cardId: string,
  request: ReviewCardRequest
): Promise<ReviewCardResponse> => {
  const response = await axiosInstance.post<ReviewCardResponse>(
    `/study-cards/${cardId}/review`,
    request
  );
  return response.data;
};
