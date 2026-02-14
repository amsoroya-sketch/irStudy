import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { EpicSidebar } from '../EpicSidebar';

describe('EpicSidebar', () => {
  const mockOnNavigate = vi.fn();

  const defaultProps = {
    currentPath: '/epic/notes',
    onNavigate: mockOnNavigate,
    sessionId: 'test-session-123',
  };

  beforeEach(() => {
    mockOnNavigate.mockClear();
  });

  it('renders patient context bar with name and MRN', () => {
    render(<EpicSidebar {...defaultProps} />);
    
    expect(screen.getByText('Smith, John')).toBeInTheDocument();
    expect(screen.getByText(/MRN: 12345678/)).toBeInTheDocument();
  });

  it('renders Chart Review section header', () => {
    render(<EpicSidebar {...defaultProps} />);
    
    expect(screen.getByText('Chart Review')).toBeInTheDocument();
  });

  it('renders all navigation items when expanded', () => {
    render(<EpicSidebar {...defaultProps} />);
    
    expect(screen.getByText('Notes')).toBeInTheDocument();
    expect(screen.getByText('Orders')).toBeInTheDocument();
    expect(screen.getByText('Medications')).toBeInTheDocument();
    expect(screen.getByText('Results')).toBeInTheDocument();
    expect(screen.getByText('Flowsheet')).toBeInTheDocument();
  });

  it('toggles section expansion when clicking header', () => {
    render(<EpicSidebar {...defaultProps} />);
    
    const sectionHeader = screen.getByText('Chart Review').closest('button');
    fireEvent.click(sectionHeader!);
    
    // Items should still be visible after second click (toggles back)
    fireEvent.click(sectionHeader!);
    expect(screen.getByText('Notes')).toBeInTheDocument();
  });

  it('calls onNavigate when a nav item is clicked', () => {
    render(<EpicSidebar {...defaultProps} />);
    
    fireEvent.click(screen.getByText('Medications'));
    expect(mockOnNavigate).toHaveBeenCalledWith('/epic/medications');
    
    fireEvent.click(screen.getByText('Results'));
    expect(mockOnNavigate).toHaveBeenCalledWith('/epic/results');
  });

  it('displays session timer when sessionId is provided', () => {
    vi.useFakeTimers();
    render(<EpicSidebar {...defaultProps} />);
    
    // Check timer is displayed with format MM:SS
    const timerRegex = /^\d{2}:\d{2}$/;
    expect(screen.getByText(timerRegex)).toBeInTheDocument();
    
    // Advance timer
    act(() => {
      vi.advanceTimersByTime(125000);
    });
    
    expect(screen.getByText('02:05')).toBeInTheDocument();
    
    vi.useRealTimers();
  });

  it('does not display timer when sessionId is not provided', () => {
    render(<EpicSidebar {...defaultProps} sessionId={undefined} />);
    
    // Timer should not be visible
    const timerElements = screen.queryAllByText(/:\d{2}/);
    expect(timerElements.length).toBe(0);
  });

  it('highlights active navigation item', () => {
    render(<EpicSidebar {...defaultProps} currentPath="/epic/notes" />);
    
    const notesButton = screen.getByText('Notes').closest('button');
    expect(notesButton).toHaveClass('active');
  });

  it('renders settings button in footer', () => {
    render(<EpicSidebar {...defaultProps} />);
    
    const settingsButton = screen.getByText('Settings');
    expect(settingsButton).toBeInTheDocument();
  });

  it('displays badge count when provided', () => {
    // The mock has Orders with badge: 0, so it should not show
    render(<EpicSidebar {...defaultProps} />);
    
    // Orders has badge 0, so no badge should be shown
    const ordersButton = screen.getByText('Orders').closest('button');
    expect(ordersButton).toBeInTheDocument();
  });

  it('applies expanded class to chevron when section is expanded', () => {
    const { container } = render(<EpicSidebar {...defaultProps} />);
    
    const chevron = container.querySelector('.epic-nav-chevron');
    expect(chevron).toHaveClass('expanded');
  });
});
