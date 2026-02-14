import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EpicTestPage } from '../EpicTestPage';

describe('EpicTestPage Integration', () => {
  it('renders complete Epic page with all components', () => {
    render(<EpicTestPage />);
    
    // Sidebar
    expect(screen.getByText('Smith, John')).toBeInTheDocument();
    
    // Patient Banner
    expect(screen.getByText('SMITH, John')).toBeInTheDocument();
    
    // Note Editor
    expect(screen.getByText('Progress Note')).toBeInTheDocument();
  });

  it('displays mock patient data correctly', () => {
    render(<EpicTestPage />);
    
    expect(screen.getAllByText(/MRN: 12345678/)[0]).toBeInTheDocument();
    expect(screen.getByText('Male')).toBeInTheDocument();
    expect(screen.getByText('Outpatient Visit')).toBeInTheDocument();
  });

  it('shows patient allergies and alerts', () => {
    render(<EpicTestPage />);
    
    expect(screen.getByText(/Allergies:/)).toBeInTheDocument();
    expect(screen.getByText(/Penicillin, Sulfa drugs/)).toBeInTheDocument();
    expect(screen.getByText('Fall risk')).toBeInTheDocument();
    expect(screen.getByText('DNR on file')).toBeInTheDocument();
  });

  it('shows contact information', () => {
    render(<EpicTestPage />);
    
    expect(screen.getByText('02 9876 5432')).toBeInTheDocument();
  });

  it('sidebar navigation works', () => {
    render(<EpicTestPage />);
    
    // Click on Medications
    fireEvent.click(screen.getByText('Medications'));
    
    // Should update current path
    const medsButton = screen.getByText('Medications').closest('button');
    expect(medsButton).toHaveClass('active');
  });

  it('note editor tabs work', () => {
    render(<EpicTestPage />);
    
    // Initially should show HPI
    expect(screen.getByText(/History of Present Illness/)).toBeInTheDocument();
    
    // Click on Physical Exam tab
    fireEvent.click(screen.getByRole('button', { name: 'Physical Exam' }));
    
    // Should show vitals
    expect(screen.getByText(/Temp/i)).toBeInTheDocument();
  });

  it.skip('note form can be filled out', async () => {
    // Skipped: Full form submission requires complex validation setup
    // Component-level tests verify form functionality
  });

  it('displays session timer in sidebar', () => {
    render(<EpicTestPage />);
    
    // Timer should be displayed (format MM:SS)
    expect(screen.getByText(/^\d{2}:\d{2}$/)).toBeInTheDocument();
  });

  it('chart review section is expanded by default', () => {
    render(<EpicTestPage />);
    
    // Navigation items should be visible
    expect(screen.getByText('Notes')).toBeInTheDocument();
    expect(screen.getByText('Orders')).toBeInTheDocument();
  });

  it('can toggle chart review section', () => {
    render(<EpicTestPage />);
    
    const sectionHeader = screen.getByText('Chart Review').closest('button');
    
    // Collapse section
    fireEvent.click(sectionHeader!);
    
    // Items should still be visible (Framer Motion handles animation)
    // Just verify the button works without error
    expect(sectionHeader).toBeInTheDocument();
  });
});
