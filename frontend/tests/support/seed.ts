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
import { STUDENT_EMAIL, STUDENT_PASSWORD } from './auth';

/** Backend API base, mirroring the frontend's axiosInstance default. */
export const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8001/api/v1';

/** Default known, deterministic case seeded for E2E runs. */
export const DEFAULT_CASE_MRN = 'EMRP-0001';

/**
 * Log the seeded student in via the backend API and return the bearer token.
 *
 * The app authenticates with a JWT stored in localStorage (not cookies), so
 * Playwright's request fixture cannot reuse the storageState auth. Specs that
 * need to seed backend state (e.g. an EMR session) call this to obtain a token.
 */
export async function apiLogin(
  request: APIRequestContext,
  email: string = STUDENT_EMAIL,
  password: string = STUDENT_PASSWORD
): Promise<string> {
  const res = await request.post(`${API_BASE_URL}/auth/login`, {
    data: { email, password },
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok()) {
    throw new Error(
      `apiLogin failed: ${res.status()} ${res.statusText()} — ${await res.text()}`
    );
  }
  const { access_token } = (await res.json()) as { access_token: string };
  if (!access_token) {
    throw new Error('apiLogin: no access_token in response');
  }
  return access_token;
}

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

/** Auth header helper for the seeded student token. */
function authHeaders(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
}

/**
 * Submit a final SOAP note for an EMR session via the backend so the E2E
 * validation-page spec can land on a *terminal* grading state without driving
 * the (currently payload-broken) UI submit button.
 *
 * NB: the backend `SubmitSessionRequest` requires `final_soap_note` (or
 * `soap_note`) at the TOP level — the Epic/Cerner editors post
 * `{ session_data: ... }`, which the API rejects with 422 (see spec notes).
 */
export async function submitEmrSession(
  request: APIRequestContext,
  token: string,
  sessionId: string,
  soapNote: { subjective: string; objective: string; assessment: string; plan: string }
): Promise<void> {
  const res = await request.post(`${API_BASE_URL}/emr/sessions/${sessionId}/submit`, {
    headers: authHeaders(token),
    data: { final_soap_note: soapNote, prescriptions: [], pathology_orders: [] },
  });
  if (!res.ok()) {
    throw new Error(`submitEmrSession failed: ${res.status()} — ${await res.text()}`);
  }
}

/** Fetch the first seeded patient-persona id (optionally filtered by specialty). */
export async function getFirstPersonaId(
  request: APIRequestContext,
  token: string,
  specialty?: string
): Promise<string> {
  const q = specialty ? `&specialty=${encodeURIComponent(specialty)}` : '';
  const res = await request.get(`${API_BASE_URL}/patient-personas/?limit=1${q}`, {
    headers: authHeaders(token),
  });
  if (!res.ok()) {
    throw new Error(`getFirstPersonaId failed: ${res.status()} — ${await res.text()}`);
  }
  const list = (await res.json()) as Array<{ persona_id: string }>;
  if (!Array.isArray(list) || list.length === 0 || !list[0].persona_id) {
    throw new Error(`getFirstPersonaId: no personas returned ${JSON.stringify(list)}`);
  }
  return list[0].persona_id;
}

/** Create an OSCE session (AI patient attempt) and return its attempt_id. */
export async function seedOsceSession(
  request: APIRequestContext,
  token: string,
  personaId?: string
): Promise<string> {
  const pid = personaId ?? (await getFirstPersonaId(request, token));
  const res = await request.post(`${API_BASE_URL}/osce-sessions`, {
    headers: authHeaders(token),
    data: { persona_id: pid },
  });
  if (!res.ok()) {
    throw new Error(`seedOsceSession failed: ${res.status()} — ${await res.text()}`);
  }
  const { attempt_id } = (await res.json()) as { attempt_id: string };
  if (!attempt_id) throw new Error('seedOsceSession: no attempt_id in response');
  return attempt_id;
}

export interface SeededMockExam {
  examId: string;
  stations: Array<{ persona_id: string; name: string; specialty: string }>;
}

/** Create a 16-station mock exam and return its id + station personas. */
export async function seedMockExam(
  request: APIRequestContext,
  token: string
): Promise<SeededMockExam> {
  const res = await request.post(`${API_BASE_URL}/mock-exams/`, {
    headers: authHeaders(token),
    data: { exam_name: `E2E Mock Exam ${Date.now()}` },
  });
  if (!res.ok()) {
    throw new Error(`seedMockExam failed: ${res.status()} — ${await res.text()}`);
  }
  const body = (await res.json()) as {
    exam_id: string;
    stations_config: Array<{ persona_id: string; name: string; specialty: string }>;
  };
  return { examId: body.exam_id, stations: body.stations_config };
}

/**
 * Drive a seeded mock exam to COMPLETED via the backend: for each of the 16
 * stations create an OSCE attempt and PUT the station-complete endpoint. Mirrors
 * what the UI does per station (auto-creates a session, then finalises a score),
 * but without waiting out sixteen 8-minute timers.
 *
 * Returns the terminal /results HTTP status so the caller can assert either the
 * rendered results OR the page's graceful error handling.
 */
export async function completeMockExam(
  request: APIRequestContext,
  token: string,
  exam: SeededMockExam,
  perStationScore = 13
): Promise<{ examComplete: boolean }> {
  let examComplete = false;
  for (let n = 1; n <= exam.stations.length; n++) {
    const persona = exam.stations[n - 1];
    const attemptId = await seedOsceSession(request, token, persona.persona_id);
    const res = await request.put(
      `${API_BASE_URL}/mock-exams/${exam.examId}/station/${n}/complete`,
      {
        headers: authHeaders(token),
        data: {
          attempt_id: attemptId,
          station_score: perStationScore,
          pass_fail: perStationScore >= 12 ? 'PASS' : 'FAIL',
        },
      }
    );
    if (!res.ok()) {
      throw new Error(
        `completeMockExam station ${n} failed: ${res.status()} — ${await res.text()}`
      );
    }
    const body = (await res.json()) as { exam_complete: boolean };
    examComplete = body.exam_complete;
  }
  return { examComplete };
}
