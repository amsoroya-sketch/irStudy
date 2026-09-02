/**
 * HTMLNotesPage tests (Phase 3 — component/a11y layer, no backend).
 *
 * Mocks the useHTMLNotes React Query hooks (+ useResponsive) and verifies the
 * note grid renders, loading / empty / error states, and that opening a note
 * mounts the viewer dialog. The viewer renders untrusted note HTML inside a
 * sandboxed <iframe srcDoc> (NOT dangerouslySetInnerHTML), so we assert the
 * iframe carries the content + a restrictive sandbox attribute. a11y on the
 * loaded grid.
 *
 * Uses the Phase 0 foundations: renderWithProviders + expectNoA11yViolations.
 */

import { it, expect, vi, beforeEach, describe } from 'vitest';
import {
  renderWithProviders,
  screen,
  waitFor,
  userEvent,
} from '../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../test/axe';
import type { HTMLNote } from '../../types/api';

// --- Responsive hook (desktop) ---
vi.mock('../../hooks/useResponsive', () => ({
  useResponsive: () => ({ isMobile: false }),
}));

// --- HTML notes hooks ---
const useHTMLNotes = vi.fn();
const useHTMLNote = vi.fn();
const useHTMLNoteSpecialties = vi.fn();
const useHTMLNoteContent = vi.fn();
vi.mock('../../hooks/useHTMLNotes', () => ({
  useHTMLNotes: () => useHTMLNotes(),
  useHTMLNote: (id: string) => useHTMLNote(id),
  useHTMLNoteSpecialties: () => useHTMLNoteSpecialties(),
  useHTMLNoteContent: (id: string) => useHTMLNoteContent(id),
}));

import HTMLNotesPage from '../HTMLNotesPage';

const NOTE: HTMLNote = {
  note_id: 'note-1',
  title: 'Chest Pain Assessment',
  specialty: 'Cardiology',
  category: 'History Taking',
  file_size_kb: 42,
  estimated_reading_minutes: 8,
  topics: ['ACS', 'ECG', 'Troponin'],
  preview_text: 'Approach to the patient presenting with chest pain.',
};

const NOTE_HTML = '<h1>Chest Pain</h1><p>SOCRATES history framework.</p>';

const setNotes = (v: Partial<ReturnType<typeof useHTMLNotes>>) =>
  useHTMLNotes.mockReturnValue({ data: undefined, isLoading: false, error: null, ...v });

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  setNotes({ data: [NOTE] });
  useHTMLNoteSpecialties.mockReturnValue({
    data: [{ specialty: 'Cardiology', count: 1 }],
  });
  useHTMLNote.mockReturnValue({ data: NOTE });
  useHTMLNoteContent.mockReturnValue({ data: NOTE_HTML, isLoading: false });
});

describe('HTMLNotesPage', () => {
  it('renders the note grid from the mocked hook', () => {
    renderWithProviders(<HTMLNotesPage />);
    expect(
      screen.getByRole('heading', { name: /HTML OSCE Notes/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: 'Chest Pain Assessment' })
    ).toBeInTheDocument();
    expect(screen.getByText('Cardiology')).toBeInTheDocument();
  });

  it('shows a loading spinner while notes are fetching', () => {
    setNotes({ data: undefined, isLoading: true });
    renderWithProviders(<HTMLNotesPage />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows the empty state when no notes match', () => {
    setNotes({ data: [] });
    renderWithProviders(<HTMLNotesPage />);
    expect(screen.getByText(/No notes found/i)).toBeInTheDocument();
  });

  it('shows an error alert when notes fail to load', () => {
    setNotes({ data: undefined, error: new Error('boom') });
    renderWithProviders(<HTMLNotesPage />);
    expect(screen.getByText(/Failed to load HTML notes/i)).toBeInTheDocument();
  });

  it('filters the grid with the client-side search box', async () => {
    const user = userEvent.setup();
    renderWithProviders(<HTMLNotesPage />);

    await user.type(screen.getByLabelText('Search'), 'nomatchxyz');
    await waitFor(() =>
      expect(screen.getByText(/No notes found/i)).toBeInTheDocument()
    );
  });

  it('opens the sandboxed viewer dialog when a note is selected', async () => {
    const user = userEvent.setup();
    renderWithProviders(<HTMLNotesPage />);

    await user.click(screen.getByRole('heading', { name: 'Chest Pain Assessment' }));

    const dialog = await screen.findByRole('dialog');
    // Content is rendered in a sandboxed iframe (NOT dangerouslySetInnerHTML).
    const frame = dialog.querySelector('iframe') as HTMLIFrameElement;
    expect(frame).not.toBeNull();
    expect(frame.getAttribute('title')).toBe('Chest Pain Assessment');
    expect(frame.getAttribute('srcdoc')).toContain('SOCRATES history framework');
    expect(frame.getAttribute('sandbox')).toBe('allow-same-origin');
  });

  it('has no accessibility violations on the loaded grid', async () => {
    const { container } = renderWithProviders(<HTMLNotesPage />);
    await expectNoA11yViolations(container);
  });
});
