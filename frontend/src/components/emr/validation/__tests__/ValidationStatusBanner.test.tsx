/**
 * ValidationStatusBanner component tests.
 *
 * The component polls GET /emr/validation/{id} every 2s (react-query
 * refetchInterval) until the status is completed/failed. It uses the shared
 * axiosInstance (NOT global.fetch), so we mock axiosInstance and drive the
 * poll with fake timers.
 *
 * States covered: initializing, in_progress, failed, completed (+ overall
 * score), and that onComplete fires once on completion — including the
 * in_progress -> completed poll transition.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

const get = vi.fn();
vi.mock('../../../../utils/axiosInstance', () => ({
  default: { get: (...args: unknown[]) => get(...args) },
}));

import {
  renderWithProviders,
  screen,
} from '../../../../test/renderWithProviders';
import { ValidationStatusBanner } from '../ValidationStatusBanner';

beforeEach(() => {
  vi.clearAllMocks();
  vi.useFakeTimers();
});
afterEach(() => {
  vi.useRealTimers();
});

const resp = (status: string, overall_score = 0, extra = {}) => ({
  data: { validation_status: status, overall_score, ...extra },
});

describe('ValidationStatusBanner', () => {
  it('shows the initializing state while the first poll is in flight', () => {
    // Never resolves -> stays loading.
    get.mockReturnValue(new Promise(() => {}));
    renderWithProviders(<ValidationStatusBanner validationId="v1" />);
    expect(screen.getByText('Initializing validation...')).toBeInTheDocument();
  });

  it('shows the in-progress status (role=status)', async () => {
    get.mockResolvedValue(resp('in_progress'));
    renderWithProviders(<ValidationStatusBanner validationId="v1" />);
    await vi.advanceTimersByTimeAsync(1);
    const status = screen.getByRole('status');
    expect(status).toHaveTextContent('Validation in progress...');
  });

  it('shows the failed status (role=alert)', async () => {
    get.mockResolvedValue(resp('failed'));
    renderWithProviders(<ValidationStatusBanner validationId="v1" />);
    await vi.advanceTimersByTimeAsync(1);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent('Validation failed');
  });

  it('shows the completed status with the overall score and fires onComplete', async () => {
    get.mockResolvedValue(resp('completed', 8.5));
    const onComplete = vi.fn();
    renderWithProviders(
      <ValidationStatusBanner validationId="v1" onComplete={onComplete} />
    );
    await vi.advanceTimersByTimeAsync(1);

    const status = screen.getByRole('status');
    expect(status).toHaveTextContent('Validation complete!');
    expect(status).toHaveTextContent('Overall Score: 8.5/10');
    expect(onComplete).toHaveBeenCalledTimes(1);
    expect(onComplete.mock.calls[0][0].validation_status).toBe('completed');
  });

  it('polls: transitions from in_progress to completed after ~2s', async () => {
    get
      .mockResolvedValueOnce(resp('in_progress'))
      .mockResolvedValue(resp('completed', 7.0));
    const onComplete = vi.fn();
    renderWithProviders(
      <ValidationStatusBanner validationId="v1" onComplete={onComplete} />
    );

    await vi.advanceTimersByTimeAsync(1);
    expect(screen.getByRole('status')).toHaveTextContent(
      'Validation in progress...'
    );

    // Advance past the 2s poll interval -> second fetch returns completed.
    await vi.advanceTimersByTimeAsync(2100);
    expect(screen.getByRole('status')).toHaveTextContent('Validation complete!');
    expect(onComplete).toHaveBeenCalledTimes(1);
  });
});
