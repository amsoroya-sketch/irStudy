/**
 * OSCE API Client
 * Integrates with backend OSCE session endpoints
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC Clinical Examination preparation
 * - AI patient simulation sessions
 * - Real-time WebSocket connections for chat
 */

import axiosInstance from './client';

/**
 * OSCE attempt/session details
 */
export interface OSCEAttempt {
  attempt_id: string;          // UUID
  user_id: string;             // UUID
  persona_id: string;          // UUID
  started_at: string;          // ISO timestamp
  completed_at: string | null; // ISO timestamp
  score: number | null;        // 0-100
  status: 'in_progress' | 'completed' | 'abandoned';
  transcript: Array<{
    speaker: 'student' | 'patient';
    message: string;
    timestamp: string;
  }>;
  persona?: {
    persona_id: string;
    name: string;
    specialty: string;
    difficulty_level: string;
    chief_complaint: string;
  };
}

/**
 * Create new OSCE session
 *
 * @param personaId - Patient persona UUID
 * @returns Created OSCE attempt with WebSocket connection details
 *
 * Example usage:
 * ```typescript
 * const session = await createOSCESession('123e4567-e89b-12d3-a456-426614174000');
 * // Use session.attempt_id to connect to WebSocket
 * ```
 */
export const createOSCESession = async (personaId: string): Promise<OSCEAttempt> => {
  // Validate UUID format
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(personaId)) {
    throw new Error('Invalid persona ID format');
  }

  const response = await axiosInstance.post<OSCEAttempt>('/osce-sessions', {
    persona_id: personaId,
  });

  return response.data;
};

/**
 * Get OSCE session details
 *
 * @param attemptId - OSCE attempt UUID
 * @returns OSCE attempt details with transcript
 *
 * Throws:
 * - 404: Session not found
 * - 403: Unauthorized (user doesn't own session)
 */
export const getOSCESession = async (attemptId: string): Promise<OSCEAttempt> => {
  // Validate UUID format
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(attemptId)) {
    throw new Error('Invalid attempt ID format');
  }

  const response = await axiosInstance.get<OSCEAttempt>(`/osce-sessions/${attemptId}`);
  return response.data;
};

/**
 * Get user's OSCE session history
 *
 * @param userId - User UUID (optional, defaults to current user)
 * @returns List of OSCE attempts
 */
export const getOSCESessions = async (userId?: string): Promise<OSCEAttempt[]> => {
  const params = userId ? { user_id: userId } : {};
  const response = await axiosInstance.get<OSCEAttempt[]>('/osce-sessions', { params });
  return response.data;
};

/**
 * Pause OSCE session
 *
 * @param attemptId - OSCE attempt UUID
 * @returns Updated OSCE attempt with paused status
 *
 * Throws:
 * - 404: Session not found
 * - 403: Unauthorized (user doesn't own session)
 * - 400: Session cannot be paused (already ended or paused)
 */
export const pauseOSCESession = async (attemptId: string): Promise<void> => {
  // Validate UUID format
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(attemptId)) {
    throw new Error('Invalid attempt ID format');
  }

  await axiosInstance.put(`/osce-sessions/${attemptId}/pause`);
};

/**
 * Resume OSCE session
 *
 * @param attemptId - OSCE attempt UUID
 * @returns Updated OSCE attempt with active status
 *
 * Throws:
 * - 404: Session not found
 * - 403: Unauthorized (user doesn't own session)
 * - 400: Session cannot be resumed (not paused)
 */
export const resumeOSCESession = async (attemptId: string): Promise<void> => {
  // Validate UUID format
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(attemptId)) {
    throw new Error('Invalid attempt ID format');
  }

  await axiosInstance.put(`/osce-sessions/${attemptId}/resume`);
};

/**
 * End OSCE session
 *
 * @param attemptId - OSCE attempt UUID
 * @returns Final score and feedback
 *
 * Throws:
 * - 404: Session not found
 * - 403: Unauthorized (user doesn't own session)
 * - 400: Session already ended
 */
export const endOSCESession = async (attemptId: string): Promise<OSCEAttempt> => {
  // Validate UUID format
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(attemptId)) {
    throw new Error('Invalid attempt ID format');
  }

  const response = await axiosInstance.post<OSCEAttempt>(`/osce-sessions/${attemptId}/end`);
  return response.data;
};

/**
 * AI Examiner score breakdown for completed OSCE
 */
export interface OSCEExaminerScore {
  attempt_id: string;
  scores: {
    communication: number;
    clinical_reasoning: number;
    information_gathering: number;
    management: number;
    professionalism: number;
  };
  total_score: number;
  pass_fail: 'PASS' | 'FAIL';
  ai_examiner_feedback: string;
  strengths: string[];
  areas_for_improvement: string[];
  critical_errors: string[];
  scored_at: string;
  scoring_model_version: string;
}

/**
 * Get AI Examiner score for completed OSCE session
 *
 * @param attemptId - OSCE attempt UUID
 * @returns Detailed AMC rubric score breakdown
 *
 * Throws:
 * - 404: Session not found or score not available yet
 * - 403: Unauthorized
 */
export const getOSCEScore = async (attemptId: string): Promise<OSCEExaminerScore> => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(attemptId)) {
    throw new Error('Invalid attempt ID format');
  }

  const response = await axiosInstance.get<OSCEExaminerScore>(`/osce-sessions/${attemptId}/score`);
  return response.data;
};
