import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';

describe('App Integration', () => {
  it('renders home screen with title', () => {
    render(<App />);
    
    expect(screen.getByText('EMR Practice System')).toBeInTheDocument();
  });

  it('displays Cerner PowerChart card on home screen', () => {
    render(<App />);
    
    expect(screen.getByText('✅ Cerner PowerChart')).toBeInTheDocument();
    expect(screen.getByText(/Dark theme with blue accents/)).toBeInTheDocument();
  });

  it('displays Epic EHR card on home screen', () => {
    render(<App />);
    
    expect(screen.getByText('✅ Epic EHR')).toBeInTheDocument();
    expect(screen.getByText(/Light theme with purple accents/)).toBeInTheDocument();
  });

  it('navigates to Cerner demo when Cerner Demo button is clicked', () => {
    render(<App />);
    
    const cernerButton = screen.getByText('Cerner Demo');
    fireEvent.click(cernerButton);
    
    // Should now show Cerner components
    expect(screen.getByText('Cerner')).toBeInTheDocument();
    expect(screen.getByText('PowerChart')).toBeInTheDocument();
  });

  it('navigates to Epic demo when Epic Demo button is clicked', () => {
    render(<App />);
    
    const epicButton = screen.getByText('Epic Demo');
    fireEvent.click(epicButton);
    
    // Should now show Epic components
    expect(screen.getByText('Smith, John')).toBeInTheDocument();
  });

  it('displays summary section with both systems features', () => {
    render(<App />);
    
    expect(screen.getByText(/Both Systems Complete!/)).toBeInTheDocument();
    expect(screen.getByText(/Cerner Features:/)).toBeInTheDocument();
    expect(screen.getByText(/Epic Features:/)).toBeInTheDocument();
  });

  it('shows Cerner feature list', () => {
    render(<App />);
    
    expect(screen.getByText(/Dark sidebar/)).toBeInTheDocument();
    expect(screen.getByText(/SOAP note validation/)).toBeInTheDocument();
    expect(screen.getByText(/Auto-save/)).toBeInTheDocument();
  });

  it('shows Epic feature list', () => {
    render(<App />);
    
    expect(screen.getByText(/Tabbed note editor/)).toBeInTheDocument();
    expect(screen.getByText(/Framer Motion animations/)).toBeInTheDocument();
    expect(screen.getByText(/Review of Systems grid/)).toBeInTheDocument();
  });

  it('lists Cerner components in the card', () => {
    render(<App />);
    
    expect(screen.getByText(/CernerSidebar - Navigation/)).toBeInTheDocument();
    expect(screen.getByText(/PatientBanner - Demographics/)).toBeInTheDocument();
    expect(screen.getByText(/SOAPNoteEditor - Full SOAP form/)).toBeInTheDocument();
  });

  it('lists Epic components in the card', () => {
    render(<App />);
    
    expect(screen.getByText(/EpicSidebar - Collapsible nav/)).toBeInTheDocument();
    expect(screen.getByText(/EpicPatientBanner - Enhanced alerts/)).toBeInTheDocument();
    expect(screen.getByText(/ EpicNoteEditor - Tabbed interface/)).toBeInTheDocument();
  });

  it('has working Launch Cerner Demo button', () => {
    render(<App />);
    
    const launchButton = screen.getByText('Launch Cerner Demo →');
    expect(launchButton).toBeInTheDocument();
    
    fireEvent.click(launchButton);
    
    // Should navigate to Cerner
    expect(screen.getByText('PowerChart')).toBeInTheDocument();
  });

  it('has working Launch Epic Demo button', () => {
    render(<App />);
    
    const launchButton = screen.getByText('Launch Epic Demo →');
    expect(launchButton).toBeInTheDocument();
    
    fireEvent.click(launchButton);
    
    // Should navigate to Epic
    expect(screen.getByText('Progress Note')).toBeInTheDocument();
  });
});
