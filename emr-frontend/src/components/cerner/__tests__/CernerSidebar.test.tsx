import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { CernerSidebar } from '../CernerSidebar';

describe('CernerSidebar', () => {
  const mockOnNavigate = vi.fn();

  const defaultProps = {
    currentPath: '/cerner',
    onNavigate: mockOnNavigate,
    sessionId: 'test-session-123',
  };

  beforeEach(() => {
    mockOnNavigate.mockClear();
  });

  it('renders the Cerner logo and PowerChart subtitle', () => {
    render(<CernerSidebar {...defaultProps} />);
    
    expect(screen.getByText('Cerner')).toBeInTheDocument();
    expect(screen.getByText('PowerChart')).toBeInTheDocument();
  });

  it('renders all navigation items', () => {
    render(<CernerSidebar {...defaultProps} />);
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('SOAP Notes')).toBeInTheDocument();
    expect(screen.getByText('Prescriptions')).toBeInTheDocument();
    expect(screen.getByText('Pathology')).toBeInTheDocument();
    expect(screen.getByText('Orders')).toBeInTheDocument();
    expect(screen.getByText('Patient Info')).toBeInTheDocument();
  });

  it('highlights the active navigation item', () => {
    render(<CernerSidebar {...defaultProps} currentPath="/cerner/soap-notes" />);
    
    const soapNotesButton = screen.getByText('SOAP Notes').closest('button');
    expect(soapNotesButton).toHaveClass('active');
  });

  it('calls onNavigate when a nav item is clicked', () => {
    render(<CernerSidebar {...defaultProps} />);
    
    fireEvent.click(screen.getByText('SOAP Notes'));
    expect(mockOnNavigate).toHaveBeenCalledWith('/cerner/soap-notes');
    
    fireEvent.click(screen.getByText('Prescriptions'));
    expect(mockOnNavigate).toHaveBeenCalledWith('/cerner/prescriptions');
  });

  it('displays session timer when sessionId is provided', () => {
    vi.useFakeTimers();
    render(<CernerSidebar {...defaultProps} />);
    
    expect(screen.getByText(/Time:/)).toBeInTheDocument();
    // Check timer is displayed with format MM:SS
    const timerRegex = /\d{2}:\d{2}/;
    expect(screen.getByText(timerRegex)).toBeInTheDocument();
    
    // Advance timer by 65 seconds
    act(() => {
      vi.advanceTimersByTime(65000);
    });
    
    // After 65 seconds, timer should show 01:05 (may be split across elements)
    expect(screen.getByText(/01.*05/)).toBeInTheDocument();
    
    vi.useRealTimers();
  });

  it('does not display timer when sessionId is null', () => {
    render(<CernerSidebar {...defaultProps} sessionId={null} />);
    
    expect(screen.queryByText(/Time:/)).not.toBeInTheDocument();
  });

  it('renders settings button', () => {
    render(<CernerSidebar {...defaultProps} />);
    
    const settingsButton = screen.getByText('Settings').closest('button');
    expect(settingsButton).toBeInTheDocument();
    
    fireEvent.click(settingsButton!);
    expect(mockOnNavigate).toHaveBeenCalledWith('/cerner/settings');
  });

  it('applies correct color classes to active nav items', () => {
    render(<CernerSidebar {...defaultProps} currentPath="/cerner/prescriptions" />);
    
    const prescriptionsButton = screen.getByText('Prescriptions').closest('button');
    expect(prescriptionsButton).toHaveClass('active');
  });

  it('template literal bug is fixed - active class applied correctly', () => {
    render(
      <CernerSidebar {...defaultProps} currentPath="/cerner" />
    );
    
    // Check that the active class is properly applied using template literals
    const dashboardButton = screen.getByText('Dashboard').closest('button');
    expect(dashboardButton).toHaveClass('cerner-nav-item');
    expect(dashboardButton).toHaveClass('active');
  });
});
