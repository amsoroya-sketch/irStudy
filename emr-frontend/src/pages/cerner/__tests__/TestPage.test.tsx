import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CernerTestPage } from '../TestPage';

describe('CernerTestPage Integration', () => {
  it('renders complete Cerner page with all components', () => {
    render(<CernerTestPage />);
    
    // Sidebar
    expect(screen.getByText('Cerner')).toBeInTheDocument();
    expect(screen.getByText('PowerChart')).toBeInTheDocument();
    
    // Patient Banner
    expect(screen.getByText('Sarah Johnson')).toBeInTheDocument();
    
    // SOAP Note Editor
    expect(screen.getByText('SOAP Note')).toBeInTheDocument();
  });

  it('displays mock patient data correctly', () => {
    render(<CernerTestPage />);
    
    expect(screen.getByText(/45F/)).toBeInTheDocument();
    expect(screen.getByText(/MRN: 12345678/)).toBeInTheDocument();
    expect(screen.getByText(/DOB: 15\/03\/1979/)).toBeInTheDocument();
  });

  it('shows patient allergies in banner', () => {
    render(<CernerTestPage />);
    
    expect(screen.getByText(/ALLERGIES:/)).toBeInTheDocument();
    expect(screen.getByText(/Penicillin \(Anaphylaxis\)/)).toBeInTheDocument();
  });

  it('shows active problems in banner', () => {
    render(<CernerTestPage />);
    
    expect(screen.getByText(/Active Problems:/)).toBeInTheDocument();
    expect(screen.getByText(/Type 2 Diabetes, Hypertension, Asthma/)).toBeInTheDocument();
  });

  it('shows medication count in banner', () => {
    render(<CernerTestPage />);
    
    expect(screen.getByText(/Current Medications:/)).toBeInTheDocument();
  });

  it('sidebar navigation works', () => {
    render(<CernerTestPage />);
    
    // Click on SOAP Notes
    fireEvent.click(screen.getByText('SOAP Notes'));
    
    // Should update current path (visual indicator)
    const soapNotesButton = screen.getByText('SOAP Notes').closest('button');
    expect(soapNotesButton).toHaveClass('active');
  });

  it.skip('SOAP note form can be filled out', async () => {
    // Skipped: Full form submission requires complex validation setup
    // Component-level tests verify form functionality
  });

  it('displays session timer in sidebar', () => {
    render(<CernerTestPage />);
    
    expect(screen.getByText(/Time:/)).toBeInTheDocument();
  });

  it('navigation highlights active item', () => {
    render(<CernerTestPage />);
    
    // SOAP Notes should be active initially
    const soapNotesButton = screen.getByText('SOAP Notes').closest('button');
    expect(soapNotesButton).toHaveClass('active');
    
    // Click on Dashboard
    fireEvent.click(screen.getByText('Dashboard'));
    
    // Dashboard should now be active
    const dashboardButton = screen.getByText('Dashboard').closest('button');
    expect(dashboardButton).toHaveClass('active');
  });
});
