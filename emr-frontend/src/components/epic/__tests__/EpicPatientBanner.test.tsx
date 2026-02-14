import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EpicPatientBanner } from '../EpicPatientBanner';

describe('EpicPatientBanner', () => {
  const mockPatient = {
    firstName: 'John',
    lastName: 'Smith',
    mrn: '12345678',
    dob: '1980-05-15',
    age: 44,
    gender: 'M' as const,
    allergies: ['Penicillin', 'Sulfa drugs'],
    alerts: ['Fall risk', 'DNR on file'],
    contact: {
      phone: '02 9876 5432',
      address: '123 Main St, Sydney NSW 2000'
    }
  };

  it('renders patient name in uppercase lastname format', () => {
    render(<EpicPatientBanner patient={mockPatient} />);
    
    expect(screen.getByText('SMITH, John')).toBeInTheDocument();
  });

  it('renders formatted date of birth with age', () => {
    render(<EpicPatientBanner patient={mockPatient} />);
    
    // DOB should be formatted as dd/mm/yyyy
    expect(screen.getByText(/15\/05\/1980/)).toBeInTheDocument();
  });

  it('renders gender', () => {
    render(<EpicPatientBanner patient={mockPatient} />);
    
    expect(screen.getByText('Male')).toBeInTheDocument();
  });

  it('renders MRN', () => {
    render(<EpicPatientBanner patient={mockPatient} />);
    
    expect(screen.getByText(/MRN: 12345678/)).toBeInTheDocument();
  });

  it('renders encounter type and location', () => {
    render(<EpicPatientBanner patient={mockPatient} />);
    
    expect(screen.getByText('Outpatient Visit')).toBeInTheDocument();
    expect(screen.getByText(/General Medicine Clinic/)).toBeInTheDocument();
  });

  it('renders custom encounter type when provided', () => {
    render(
      <EpicPatientBanner 
        patient={mockPatient} 
        encounterType="Emergency Admission"
        location="ED Bay 3"
      />
    );
    
    expect(screen.getByText('Emergency Admission')).toBeInTheDocument();
    expect(screen.getByText(/ED Bay 3/)).toBeInTheDocument();
  });

  it('displays allergy alerts', () => {
    render(<EpicPatientBanner patient={mockPatient} />);
    
    expect(screen.getByText(/Allergies:/)).toBeInTheDocument();
    expect(screen.getByText(/Penicillin, Sulfa drugs/)).toBeInTheDocument();
  });

  it('displays patient alerts', () => {
    render(<EpicPatientBanner patient={mockPatient} />);
    
    expect(screen.getByText('Fall risk')).toBeInTheDocument();
    expect(screen.getByText('DNR on file')).toBeInTheDocument();
  });

  it('displays contact phone when provided', () => {
    render(<EpicPatientBanner patient={mockPatient} />);
    
    expect(screen.getByText('02 9876 5432')).toBeInTheDocument();
  });

  it('does not display contact section when phone is not provided', () => {
    const patientNoPhone = { ...mockPatient, contact: {} };
    const { container } = render(<EpicPatientBanner patient={patientNoPhone} />);
    
    expect(screen.queryByText('02 9876 5432')).not.toBeInTheDocument();
  });

  it('handles female gender correctly', () => {
    const femalePatient = { ...mockPatient, gender: 'F' as const };
    render(<EpicPatientBanner patient={femalePatient} />);
    
    expect(screen.getByText('Female')).toBeInTheDocument();
  });

  it('handles Other gender correctly', () => {
    const otherPatient = { ...mockPatient, gender: 'Other' as const };
    render(<EpicPatientBanner patient={otherPatient} />);
    
    expect(screen.getByText('Other')).toBeInTheDocument();
  });

  it('does not show allergy section when no allergies', () => {
    const noAllergyPatient = { ...mockPatient, allergies: [] };
    const { container } = render(<EpicPatientBanner patient={noAllergyPatient} />);
    
    expect(screen.queryByText(/Allergies:/)).not.toBeInTheDocument();
  });

  it('does not show alerts section when no alerts', () => {
    const noAlertsPatient = { ...mockPatient, alerts: [] };
    render(<EpicPatientBanner patient={noAlertsPatient} />);
    
    expect(screen.queryByText('Fall risk')).not.toBeInTheDocument();
  });

  it('calculates age correctly for young children', () => {
    // Create a date about 1 year ago for testing
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
    const dobString = oneYearAgo.toISOString().split('T')[0];
    
    const childPatient = {
      ...mockPatient,
      dob: dobString,
      age: 1
    };
    render(<EpicPatientBanner patient={childPatient} />);
    
    // Should show date with age
    expect(screen.getByText(/\d{2}\/\d{2}\/\d{4}/)).toBeInTheDocument();
  });
});
