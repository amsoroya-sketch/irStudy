/**
 * E2E seed helper (Phase 0 foundations).
 *
 * Starts an EMR practice session against the backend so E2E specs don't depend
 * on ambient DB state. Given a logged-in API context (or a bearer token), it
 * POSTs to {API_BASE_URL}/emr/sessions/start on a known case (mrn EMRP-0001)
 * and returns the created sessionId.
 *
 * No hardcoded secrets: the caller supplies the auth token; the base URL comes
 * from VITE_API_URL (matching src/utils/axiosInstance.ts).
 */

import type { APIRequestContext } from '@playwright/test';

/** Backend API base, mirroring the frontend's axiosInstance default. */
export const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8001/api/v1';

/** Default known, deterministic case seeded for E2E runs. */
export const DEFAULT_CASE_MRN = 'EMRP-0001';

export interface SeedEmrSessionOptions {
  /** Bearer token for the logged-in student. */
  token: string;
  /** Case MRN to start the session on (defaults to EMRP-0001). */
  mrn?: string;
  /** Optional explicit patient id, if the backend prefers id over mrn. */
  patientId?: string;
}

interface StartSessionResponse {
  session_id?: string;
  id?: string;
}

/**
 * Start an EMR session and return its sessionId.
 *
 * @param request  Playwright APIRequestContext (e.g. `playwright.request` fixture).
 * @param options  Auth token + which case to seed.
 */
export async function seedEmrSession(
  request: APIRequestContext,
  { token, mrn = DEFAULT_CASE_MRN, patientId }: SeedEmrSessionOptions
): Promise<string> {
  const response = await request.post(`${API_BASE_URL}/emr/sessions/start`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    data: patientId ? { patient_id: patientId } : { mrn },
  });

  if (!response.ok()) {
    const body = await response.text();
    throw new Error(
      `seedEmrSession failed: ${response.status()} ${response.statusText()} — ${body}`
    );
  }

  const payload = (await response.json()) as StartSessionResponse;
  const sessionId = payload.session_id ?? payload.id;
  if (!sessionId) {
    throw new Error(`seedEmrSession: no session id in response ${JSON.stringify(payload)}`);
  }
  return sessionId;
}
