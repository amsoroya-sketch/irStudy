/**
 * Mock Exam API Client
 * Integrates with backend mock exam orchestration endpoints
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC Clinical Examination mock exam simulation
 * - 16 stations (8 specialties, 2 stations each)
 * - 8 minutes per station + 5-second breaks
 * - AMC pass threshold: 198/240 (82.5%)
 */

import axiosInstance from './client';

/**
 * Persona info for mock exam station
 */
export interface PersonaInfo {
  persona_id: string;
  name: string;
  specialty: string;
  chief_complaint: string;
  difficulty_level: 'INTERMEDIATE' | 'ADVANCED';
}

/**
 * Create mock exam request
 */
export interface MockExamCreateRequest {
  exam_name?: string;
}

/**
 * Create mock exam response
 */
export interface MockExamCreateResponse {
  exam_id: string;
  stations_config: PersonaInfo[];
  estimated_duration_minutes: number;
  start_url: string;
}

/**
 * Mock exam status response
 */
export interface MockExamStatusResponse {
  exam_id: string;
  exam_state: 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED';
  current_station_number: number;
  stations_completed: number;
  total_score: number;
  time_elapsed_minutes?: number;
  stations_config: PersonaInfo[];
}

/**
 * Complete station request
 */
export interface StationCompleteRequest {
  attemptId: string;
  stationScore: number;
  passFail: 'PASS' | 'FAIL';
}

/**
 * Complete station response
 */
export interface StationCompleteResponse {
  next_station_number: number | null;
  station_score: number;
  overall_progress: number;
  exam_complete: boolean;
}

/**
 * Station result details
 */
export interface StationResult {
  station_number: number;
  specialty: string;
  persona_name: string;
  score: number;
  pass_fail: 'PASS' | 'FAIL';
  attempt_id: string;
}

/**
 * Performance by specialty
 */
export interface SpecialtyPerformance {
  specialty: string;
  total_score: number;
  max_score: number;
  percentage: number;
  stations_passed: number;
  total_stations: number;
}

/**
 * Summary statistics
 */
export interface SummaryStatistics {
  stations_passed: number;
  stations_failed: number;
  average_score_per_station: number;
  performance_by_specialty?: SpecialtyPerformance[];
}

/**
 * Mock exam results response
 */
export interface MockExamResultsResponse {
  overall_score: number;
  percentage: number;
  overall_pass_fail: 'PASS' | 'FAIL';
  stations: StationResult[];
  summary_statistics: SummaryStatistics;
}

/**
 * Create new mock exam
 *
 * @param request - Mock exam configuration
 * @returns Created mock exam with 16 stations
 *
 * Example usage:
 * ```typescript
 * const exam = await createMockExam({ exam_name: 'Mock Exam 1' });
 * // Navigate to exam.start_url
 * ```
 */
export const createMockExam = async (
  request: MockExamCreateRequest
): Promise<MockExamCreateResponse> => {
  const response = await axiosInstance.post<MockExamCreateResponse>(
    '/mock-exams/',
    request
  );
  return response.data;
};

/**
 * Get mock exam status
 *
 * @param examId - Mock exam UUID
 * @returns Current exam status and progress
 *
 * Throws:
 * - 404: Exam not found
 * - 403: Unauthorized (user doesn't own exam)
 */
export const getMockExamStatus = async (
  examId: string
): Promise<MockExamStatusResponse> => {
  const response = await axiosInstance.get<MockExamStatusResponse>(
    `/mock-exams/${examId}/`
  );
  return response.data;
};

/**
 * Complete station and advance to next
 *
 * @param examId - Mock exam UUID
 * @param stationNumber - Station number (1-16)
 * @param request - Station completion data
 * @returns Next station info or exam completion status
 *
 * Throws:
 * - 404: Exam not found
 * - 403: Unauthorized (user doesn't own exam)
 * - 400: Invalid station number or already completed
 */
export const completeStation = async (
  examId: string,
  stationNumber: number,
  request: StationCompleteRequest
): Promise<StationCompleteResponse> => {
  const response = await axiosInstance.put<StationCompleteResponse>(
    `/mock-exams/${examId}/station/${stationNumber}/complete/`
    request
  );
  return response.data;
};

/**
 * Get mock exam results
 *
 * @param examId - Mock exam UUID
 * @returns Comprehensive results with specialty breakdowns
 *
 * Throws:
 * - 404: Exam not found
 * - 403: Unauthorized (user doesn't own exam)
 * - 400: Exam not completed yet
 */
export const getMockExamResults = async (
  examId: string
): Promise<MockExamResultsResponse> => {
  const response = await axiosInstance.get<MockExamResultsResponse>(
    `/mock-exams/${examId}/results/`
  );
  return response.data;
};
