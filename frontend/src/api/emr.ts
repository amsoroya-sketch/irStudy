/**
 * EMR API Client (Phase 1b — "pick a case and practice")
 *
 * Typed client for the EMR case picker and session start endpoints.
 * Uses the shared axios instance (JWT attached via interceptor, baseURL
 * configured from VITE_API_URL) — no hardcoded hosts.
 */

import axiosInstance from '../utils/axiosInstance';
import type { EMRCaseListResponse } from '../types/emr';

/**
 * Optional filters for listing EMR cases.
 */
export interface EMRCaseFilters {
  specialty?: string;
  difficulty?: string;
}

/**
 * Body for starting an EMR session.
 * - Random start: pass no body (or an empty object).
 * - Case start: pass `{ patient_id }` from a chosen case.
 */
export interface StartEMRSessionBody {
  patient_id?: string;
  specialty?: string;
  difficulty?: string;
}

/**
 * Response from POST /emr/sessions/start.
 * Only `session_id` is required by the navigation flow; other fields the
 * backend returns are preserved but not strongly typed here.
 */
export interface StartEMRSessionResponse {
  session_id: string;
  [key: string]: unknown;
}

/**
 * List available EMR cases, optionally filtered by specialty / difficulty.
 */
export const listEMRCases = async (
  filters?: EMRCaseFilters
): Promise<EMRCaseListResponse> => {
  const params: Record<string, string> = {};
  if (filters?.specialty) {
    params.specialty = filters.specialty;
  }
  if (filters?.difficulty) {
    params.difficulty = filters.difficulty;
  }

  const response = await axiosInstance.get<EMRCaseListResponse>('/emr/cases', {
    params,
  });
  return response.data;
};

/**
 * Start a new EMR documentation session.
 * Pass `{ patient_id }` to practice a specific case, or no argument for a
 * random case (preserves the existing quick-start flow).
 */
export const startEMRSession = async (
  body?: StartEMRSessionBody
): Promise<StartEMRSessionResponse> => {
  const response = await axiosInstance.post<StartEMRSessionResponse>(
    '/emr/sessions/start',
    body ?? {}
  );
  return response.data;
};
