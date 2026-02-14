/**
 * Citation Panel Component Tests
 * Comprehensive test suite for CitationPanel component
 *
 * COVERAGE:
 * - Rendering citations
 * - Page number display
 * - RAG verification badge
 * - Copy-to-clipboard functionality
 * - Source icons
 * - Snackbar notifications
 * - Citations without metadata
 * - Section parsing
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CitationPanel } from '../../src/components/citations/CitationPanel';
import type { Citation } from '../../src/types/citation';

describe('CitationPanel', () => {
  // Mock clipboard API
  const mockClipboard = {
    writeText: vi.fn(),
  };

  beforeEach(() => {
    // Setup clipboard mock
    Object.assign(navigator, {
      clipboard: mockClipboard,
    });
    mockClipboard.writeText.mockClear();
    mockClipboard.writeText.mockResolvedValue(undefined);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders all citations', () => {
    const citations = [
      'eTG: Therapeutic Guidelines - Cardiovascular (Page 42, Section 3.2)',
      'PBS: Pharmaceutical Benefits Scheme - Paracetamol',
      'AMH: Australian Medicines Handbook 2024 (Page 156)',
    ];

    render(<CitationPanel citations={citations} />);

    expect(screen.getByText(/Therapeutic Guidelines - Cardiovascular/)).toBeInTheDocument();
    expect(screen.getByText(/Pharmaceutical Benefits Scheme - Paracetamol/)).toBeInTheDocument();
    expect(screen.getByText(/Australian Medicines Handbook 2024/)).toBeInTheDocument();
  });

  it('displays page numbers when present', () => {
    const citations = [
      'eTG: Cardiovascular Guidelines (Page 42)',
      'AMH: Analgesics (Page 156)',
    ];

    render(<CitationPanel citations={citations} />);

    expect(screen.getByLabelText('Page 42')).toBeInTheDocument();
    expect(screen.getByLabelText('Page 156')).toBeInTheDocument();
  });

  it('shows RAG verification badge when enabled and confidence provided', () => {
    const citations: Citation[] = [
      {
        source: 'eTG',
        title: 'Cardiovascular Guidelines',
        page: '42',
        section: null,
        url: null,
        confidence: 0.95,
        originalText: 'eTG: Cardiovascular Guidelines (Page 42)',
      },
    ];

    render(<CitationPanel citations={citations} showConfidence={true} />);

    expect(screen.getByText('RAG Verified')).toBeInTheDocument();
    expect(screen.getByText('95% confidence')).toBeInTheDocument();
  });

  it('does not show RAG badge when showConfidence is false', () => {
    const citations: Citation[] = [
      {
        source: 'eTG',
        title: 'Cardiovascular Guidelines',
        page: '42',
        section: null,
        url: null,
        confidence: 0.95,
        originalText: 'eTG: Cardiovascular Guidelines (Page 42)',
      },
    ];

    render(<CitationPanel citations={citations} showConfidence={false} />);

    expect(screen.queryByText('RAG Verified')).not.toBeInTheDocument();
  });

  it('copies citation to clipboard on button click', async () => {
    const citation = 'eTG: Cardiovascular Guidelines (Page 42)';

    render(<CitationPanel citations={[citation]} allowCopy={true} />);

    const copyButton = screen.getByLabelText('Copy citation to clipboard');
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(mockClipboard.writeText).toHaveBeenCalledWith(citation);
    });
  });

  it('displays snackbar after successful copy', async () => {
    const citation = 'eTG: Cardiovascular Guidelines (Page 42)';

    render(<CitationPanel citations={[citation]} allowCopy={true} />);

    const copyButton = screen.getByLabelText('Copy citation to clipboard');
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(screen.getByText('Citation copied to clipboard')).toBeInTheDocument();
    });
  });

  it('displays correct source icons for eTG (MenuBook)', () => {
    const citations = ['eTG: Cardiovascular Guidelines'];

    const { container } = render(<CitationPanel citations={citations} />);

    // Check for MenuBook icon (MUI renders it as an SVG)
    const icons = container.querySelectorAll('svg[data-testid="MenuBookIcon"]');
    expect(icons.length).toBeGreaterThan(0);
  });

  it('displays correct source icons for PBS (LocalHospital)', () => {
    const citations = ['PBS: Pharmaceutical Benefits'];

    const { container } = render(<CitationPanel citations={citations} />);

    // Check for LocalHospital icon
    const icons = container.querySelectorAll('svg[data-testid="LocalHospitalIcon"]');
    expect(icons.length).toBeGreaterThan(0);
  });

  it('handles citations without page numbers', () => {
    const citations = [
      'eTG: Cardiovascular Guidelines',
      'PBS: Pharmaceutical Benefits Scheme',
    ];

    render(<CitationPanel citations={citations} />);

    // Should render citations
    expect(screen.getByText(/Cardiovascular Guidelines/)).toBeInTheDocument();
    expect(screen.getByText(/Pharmaceutical Benefits Scheme/)).toBeInTheDocument();

    // Should not have page chips
    expect(screen.queryByText(/Page/)).not.toBeInTheDocument();
  });

  it('parses section information correctly', () => {
    const citations = [
      'eTG: Cardiovascular Guidelines (Section 3.2)',
      'AHPRA: Prescribing Guidelines (Section 2.1.5)',
    ];

    render(<CitationPanel citations={citations} />);

    expect(screen.getByLabelText('Section 3.2')).toBeInTheDocument();
    expect(screen.getByLabelText('Section 2.1.5')).toBeInTheDocument();
  });

  it('handles both page and section metadata', () => {
    const citations = ['eTG: Guidelines (Page 42, Section 3.2)'];

    render(<CitationPanel citations={citations} />);

    expect(screen.getByLabelText('Page 42')).toBeInTheDocument();
    expect(screen.getByLabelText('Section 3.2')).toBeInTheDocument();
  });

  it('renders header with title', () => {
    const citations = ['eTG: Test Citation'];

    render(<CitationPanel citations={citations} />);

    expect(screen.getByText('Australian Clinical Guidelines')).toBeInTheDocument();
  });

  it('handles empty citations array', () => {
    render(<CitationPanel citations={[]} />);

    expect(screen.getByText('No citations available')).toBeInTheDocument();
  });

  it('hides copy button when allowCopy is false', () => {
    const citations = ['eTG: Test Citation'];

    render(<CitationPanel citations={citations} allowCopy={false} />);

    expect(screen.queryByLabelText('Copy citation to clipboard')).not.toBeInTheDocument();
  });

  it('handles multiple source types correctly', () => {
    const citations = [
      'eTG: Therapeutic Guidelines',
      'PBS: Pharmaceutical Benefits',
      'AMH: Medicines Handbook',
      'AHPRA: Prescribing Guidelines',
      'RACGP: Red Book',
      'NSW Health: Emergency Care Guidelines',
    ];

    render(<CitationPanel citations={citations} />);

    expect(screen.getByText(/eTG: Therapeutic Guidelines/)).toBeInTheDocument();
    expect(screen.getByText(/PBS: Pharmaceutical Benefits/)).toBeInTheDocument();
    expect(screen.getByText(/AMH: Medicines Handbook/)).toBeInTheDocument();
    expect(screen.getByText(/AHPRA: Prescribing Guidelines/)).toBeInTheDocument();
    expect(screen.getByText(/RACGP: Red Book/)).toBeInTheDocument();
    expect(screen.getByText(/NSW Health: Emergency Care Guidelines/)).toBeInTheDocument();
  });

  it('parses page ranges correctly', () => {
    const citations = ['eTG: Guidelines (pp. 42-45)'];

    render(<CitationPanel citations={citations} />);

    expect(screen.getByLabelText('Page 42-45')).toBeInTheDocument();
  });

  it('handles clipboard API errors gracefully', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    mockClipboard.writeText.mockRejectedValue(new Error('Clipboard access denied'));

    const citation = 'eTG: Test Citation';
    render(<CitationPanel citations={[citation]} allowCopy={true} />);

    const copyButton = screen.getByLabelText('Copy citation to clipboard');
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Failed to copy citation:',
        expect.any(Error)
      );
    });

    consoleErrorSpy.mockRestore();
  });

  it('uses custom aria-label when provided', () => {
    const citations = ['eTG: Test Citation'];
    const customLabel = 'Custom citation label';

    render(<CitationPanel citations={citations} aria-label={customLabel} />);

    expect(screen.getByLabelText(customLabel)).toBeInTheDocument();
  });

  it('renders with default aria-label', () => {
    const citations = ['eTG: Test Citation'];

    render(<CitationPanel citations={citations} />);

    expect(
      screen.getByLabelText('Australian clinical guidelines citations')
    ).toBeInTheDocument();
  });
});
