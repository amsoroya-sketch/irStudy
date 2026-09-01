/**
 * EMRValidationPage tests (PRD-EMR-PRACTICE-003)
 *
 * Verifies the results page renders PASS/FAIL, score, missing elements,
 * critical errors, rubric bars, strengths and areas for improvement from the
 * ValidationResult (score_breakdown) shape the backend returns.
 */

import { it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { EMRValidationPage } from '../EMRValidationPage';
import type { EMRValidationApiResult } from '../../../types/emr';

const wrap = (result: EMRValidationApiResult) => {
  vi.spyOn(global, 'fetch').mockResolvedValue({
    ok: true,
    json: async () => result,
  } as unknown as Response);
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/emr/validation/sess-1']}>
        <Routes>
          <Route path="/emr/validation/:sessionId" element={<EMRValidationPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

const PASS: EMRValidationApiResult = {
  status: 'completed',
  overall_score: 12,
  pass_fail: true,
  amc_rubric_scores: [{ category: 'documentation', score: 8, feedback: 'good' }],
  missing_elements: [],
  critical_errors_committed: [],
  strengths: ['structured'],
  areas_for_improvement: ['more detail'],
};
const FAIL: EMRValidationApiResult = {
  ...PASS,
  overall_score: 6,
  pass_fail: false,
  missing_elements: ['aortic dissection considered'],
  critical_errors_committed: ['nitrates given in RV infarct'],
};

beforeEach(() => {
  vi.restoreAllMocks();
});
afterEach(() => {
  vi.restoreAllMocks();
});

it('Test 1: renders PASS state', async () => {
  wrap(PASS);
  await waitFor(() => expect(screen.getByText(/pass/i)).toBeInTheDocument());
  expect(screen.getByText(/12/)).toBeInTheDocument();
});
it('Test 2: renders FAIL state', async () => {
  wrap(FAIL);
  await waitFor(() => expect(screen.getByText(/fail/i)).toBeInTheDocument());
});
it('Test 3: lists critical errors committed', async () => {
  wrap(FAIL);
  await waitFor(() =>
    expect(screen.getByText(/nitrates given in RV infarct/i)).toBeInTheDocument()
  );
});
it('Test 4: lists missing elements', async () => {
  wrap(FAIL);
  await waitFor(() =>
    expect(screen.getByText(/aortic dissection considered/i)).toBeInTheDocument()
  );
});
it('Test 5: renders rubric bars from amc_rubric_scores', async () => {
  wrap(PASS);
  await waitFor(() => expect(screen.getByText(/documentation/i)).toBeInTheDocument());
});
it('Test 6: shows strengths and areas for improvement', async () => {
  wrap(PASS);
  await waitFor(() => expect(screen.getByText(/more detail/i)).toBeInTheDocument());
  expect(screen.getByText(/structured/i)).toBeInTheDocument();
});

// Bug 1: backend pass_fail is authoritative. overall_score 8.5 would have PASSED
// under the old local threshold of 8, but pass_fail=false must win → FAIL.
it('Test 7: pass_fail=false with overall_score 8.5 renders FAIL, never PASS', async () => {
  wrap({ ...PASS, overall_score: 8.5, pass_fail: false });
  await waitFor(() => expect(screen.getByText('FAIL')).toBeInTheDocument());
  expect(screen.queryByText('PASS')).not.toBeInTheDocument();
});

// Bug 2: AMC categories are scored 0-3, so a 3/3 rubric renders as full (100%).
it('Test 8: rubric score of 3 renders on the 0-3 scale (3/3, 100%)', async () => {
  wrap({
    ...PASS,
    amc_rubric_scores: [{ category: 'documentation', score: 3 }],
  });
  await waitFor(() => expect(screen.getByText('3/3')).toBeInTheDocument());
  expect(screen.getByText('100%')).toBeInTheDocument();
});

// Bug 3: when the AI layer is unavailable the session is ungraded — show a
// re-submit prompt, not a fake FAIL / 0 score.
it('Test 9: ai_unavailable shows the re-submit notice and no PASS/FAIL chip', async () => {
  wrap({
    status: 'in_progress',
    overall_score: 0,
    pass_fail: null,
    ai_unavailable: true,
  });
  await waitFor(() =>
    expect(screen.getByText(/temporarily unavailable/i)).toBeInTheDocument()
  );
  expect(
    screen.getByRole('button', { name: /return to documentation/i })
  ).toBeInTheDocument();
  expect(screen.queryByText('FAIL')).not.toBeInTheDocument();
  expect(screen.queryByText('PASS')).not.toBeInTheDocument();
});
