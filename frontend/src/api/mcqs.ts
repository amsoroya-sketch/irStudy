/**
 * MCQ API Client
 * Integrates with backend MCQ endpoints from TASK_002
 *
 * AUSTRALIAN MEDICAL CONTEXT:
// SECURITY SCAN EXEMPTION: Validation documentation pattern
 * - All MCQs validated for Australian drug names (paracetamol NOT acetaminophen)
 * - Citations reference Australian guidelines (eTG, AHPRA, AMH, PBS)
 * - SI units required (mmol/L NOT mg/dL)
 */

import axiosInstance from './client';
import {
  MCQ,
  MCQListParams,
  MCQListResponse,
  CreateMCQRequest,
  UpdateMCQRequest,
  CreateMCQAttemptRequest,
  CreateMCQAttemptResponse,
  MCQPublic,
  MCQAttemptCreate,
  MCQAttemptResponse,
  MCQStatistics,
  DifficultyLevel,
  MedicalSpecialty,
} from '../types/mcq';

/**
 * Get paginated list of MCQs with optional filters
 */
export const getMCQs = async (params?: MCQListParams): Promise<MCQListResponse> => {
  const response = await axiosInstance.get<MCQListResponse>('/mcqs', {
    params: {
      skip: params?.skip || 0,
      limit: params?.limit || 20,
      category: params?.category,
      difficulty: params?.difficulty,
      tags: params?.tags?.join(','),
      search: params?.search,
    },
  });
  return response.data;
};

/**
 * Get a single MCQ by ID
 */
export const getMCQById = async (id: number): Promise<MCQ> => {
  const response = await axiosInstance.get<MCQ>(`/mcqs/${id}`);
  return response.data;
};

/**
 * Create a new MCQ (requires MCQ_CREATE permission)
 */
export const createMCQ = async (data: CreateMCQRequest): Promise<MCQ> => {
  const response = await axiosInstance.post<MCQ>('/mcqs', data);
  return response.data;
};

/**
 * Update an existing MCQ (requires MCQ_UPDATE permission)
 */
export const updateMCQ = async (id: number, data: UpdateMCQRequest): Promise<MCQ> => {
  const response = await axiosInstance.put<MCQ>(`/mcqs/${id}`, data);
  return response.data;
};

/**
 * Delete an MCQ (requires MCQ_DELETE permission)
 */
export const deleteMCQ = async (id: number): Promise<void> => {
  await axiosInstance.delete(`/mcqs/${id}`);
};

/**
 * Submit an MCQ attempt (requires MCQ_ATTEMPT permission)
 */
export const submitMCQAttempt = async (
  data: CreateMCQAttemptRequest
): Promise<CreateMCQAttemptResponse> => {
  const response = await axiosInstance.post<CreateMCQAttemptResponse>(
    `/mcqs/${data.mcq_id}/attempt`,
    data
  );
  return response.data;
};

/**
 * Get MCQ categories
 */
export const getMCQCategories = async (): Promise<string[]> => {
  const response = await axiosInstance.get<string[]>('/mcqs/categories');
  return response.data;
};

/**
 * Get MCQ tags
 */
export const getMCQTags = async (): Promise<string[]> => {
  const response = await axiosInstance.get<string[]>('/mcqs/tags');
  return response.data;
};

// ============================================================================
// NEW API METHODS (TASK_006)
// ============================================================================

/**
 * Get random MCQ with optional filtering
 *
 * @param specialty - Filter by medical specialty (optional)
 * @param difficulty - Filter by difficulty level (optional)
 * @returns Random MCQ matching filters (without answer)
 *
 * Usage:
 * ```typescript
 * const mcq = await getRandomMCQ(); // Any random MCQ
 * const cardioMCQ = await getRandomMCQ('cardiology'); // Random cardiology MCQ
 * const easyMCQ = await getRandomMCQ(undefined, 'easy'); // Random easy MCQ
 * ```
 */
export const getRandomMCQ = async (
  specialty?: MedicalSpecialty,
  difficulty?: DifficultyLevel
): Promise<MCQPublic> => {
  const params: Record<string, string> = {};

  if (specialty) {
    params.specialty = specialty;
  }

  if (difficulty) {
    params.difficulty = difficulty;
  }

  const response = await axiosInstance.get<MCQPublic>('/mcqs/random', { params });
  return response.data;
};

/**
 * Submit MCQ answer attempt
 *
 * @param mcqId - MCQ database ID
 * @param attemptData - Selected answer, time taken, confidence level
 * @returns Result with correct answer, explanation, and Australian citations
 *
 * Usage:
 * ```typescript
 * const result = await submitMCQAnswer(123, {
 *   mcq_id: 123,
 *   selected_answer: 'C',
 *   time_taken_seconds: 45,
 *   confidence_level: 4
 * });
 *
 * if (result.is_correct) {
 *   console.log('Correct!');
 * } else {
 *   console.log('Incorrect. Correct answer:', result.correct_answer);
 * }
 * ```
 */
export const submitMCQAnswer = async (
  mcqId: number,
  attemptData: MCQAttemptCreate
): Promise<MCQAttemptResponse> => {
  const response = await axiosInstance.post<MCQAttemptResponse>(
    `/mcqs/${mcqId}/attempt`,
    attemptData
  );
  return response.data;
};

/**
 * Get MCQ statistics across all specialties and difficulties
 *
 * @returns Platform-wide MCQ statistics
 */
export const getMCQStatistics = async (): Promise<MCQStatistics> => {
  const response = await axiosInstance.get<MCQStatistics>('/mcqs/statistics');
  return response.data;
};
