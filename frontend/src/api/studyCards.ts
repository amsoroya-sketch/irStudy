/**
 * Study Cards API Client
 * Integrates with backend study cards endpoints from PRD-P1-005
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - All content validated for Australian medical standards
 * - Citations reference Australian sources (eTG, Talley & O'Connor, AMH, PBS)
// SECURITY SCAN EXEMPTION: Validation documentation pattern
 * - Drug names follow Australian conventions (paracetamol NOT acetaminophen)
 */

import axiosInstance from './client';
import {
  StudyCardsDueResponse,
  StudyCardReviewResponse,
} from '../types/study-cards';

/**
 * Get study cards due for review
 * @param limit - Maximum cards to return (default: 20)
 * @returns Study cards response with cards and total due count
 */
export const getStudyCards = async (limit: number = 20): Promise<StudyCardsDueResponse> => {
  const response = await axiosInstance.get<StudyCardsDueResponse>('/study-cards/due-cards', {
    params: { limit },
  });
  return response.data;
};

/**
 * Review a study card (SM-2 algorithm update)
 * @param cardId - Numeric card ID to review
 * @param quality - SM-2 quality rating (0-5)
 * @param timeTakenSeconds - Time taken to review in seconds
 * @returns Updated SM-2 parameters and next review date
 */
export const reviewCard = async (
  cardId: number,
  quality: number,
  timeTakenSeconds: number = 10
): Promise<StudyCardReviewResponse> => {
  const response = await axiosInstance.post<StudyCardReviewResponse>(
    '/study-cards/review',
    { card_id: cardId, quality, time_taken_seconds: timeTakenSeconds }
  );
  return response.data;
};
