/**
 * Integration API - OSCE-to-EMR Converter
 *
 * Provides API client methods for converting OSCE sessions to EMR SOAP notes
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - Converts AI OSCE conversation transcripts to EMR SOAP notes
 * - Uses Claude API for clinical data extraction
 * - Enforces Australian medical terminology (paracetamol, salbutamol)
 *
 * @module api/integration
 */

import axiosInstance from './client';

/**
 * Conversion request payload
 */
export interface ConversionRequest {
  osceAttemptId: string;
}

/**
 * Conversion response from backend
 */
export interface ConversionResponse {
  emr_session_id: string;
  pre_fill_percentage: number;
  redirect_url: string;
  conversion_metadata: {
    extraction_confidence: number;
    tokens_used: number;
    api_response_time_ms: number;
  };
}

/**
 * User's conversion statistics
 */
export interface ConversionStats {
  total_conversions: number;
  average_pre_fill_percentage: number;
  last_conversion_at: string | null;
}

/**
 * Error response from conversion API
 */
export interface ConversionError {
  detail: string;
  error_code: string;
  osce_attempt_id?: string;
}

/**
 * Convert OSCE attempt to EMR session
 *
 * @param osceAttemptId - UUID of completed OSCE attempt
 * @returns Conversion response with EMR session ID and pre-fill metadata
 *
 * @throws {AxiosError} If API request fails
 *
 * @example
 * ```typescript
 * const result = await convertOSCEToEMR('550e8400-e29b-41d4-a716-446655440000');
 * console.log(`EMR session created: ${result.emr_session_id}`);
 * console.log(`Pre-fill: ${Math.round(result.pre_fill_percentage * 100)}%`);
 * ```
 */
export const convertOSCEToEMR = async (
  osceAttemptId: string
): Promise<ConversionResponse> => {
  const response = await axiosInstance.post<ConversionResponse>(
    '/integration/osce-to-emr',
    { osceAttemptId }
  );
  return response.data;
};

/**
 * Get user's conversion statistics
 *
 * @returns Conversion statistics (total, average pre-fill, last conversion date)
 *
 * @throws {AxiosError} If API request fails
 *
 * @example
 * ```typescript
 * const stats = await getConversionStats();
 * console.log(`Total conversions: ${stats.total_conversions}`);
 * console.log(`Average pre-fill: ${Math.round(stats.average_pre_fill_percentage * 100)}%`);
 * ```
 */
export const getConversionStats = async (): Promise<ConversionStats> => {
  const response = await axiosInstance.get<ConversionStats>(
    '/integration/conversion-stats'
  );
  return response.data;
};
