import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PatientBanner } from '../PatientBanner';

describe('PatientBanner', () => {
  const mockPatient = {
    id: '1',
    name: 'Sarah Johnson',
    age: 45,
    sex: 'F' as const,
    mrn: '12345678',
    dob: '15/03/1979',
    allergies: [
      { allergen: 'Penicillin', reaction: 'Anaphylaxis', severity: 'severe' as const }
    ],
    activeProblems: ['Type 2 Diabetes', 'Hypertension'],
    currentMedications: [
      { name: 'Metformin', dose: '500mg', frequency: 'BD' }
    ]
  };

  it('renders patient name and demographics', () => {
    render(<PatientBanner patient={mockPatient} />);
    
    expect(screen.getByText('Sarah Johnson')).toBeInTheDocument();
    expect(screen.getByText(/45F/)).toBeInTheDocument();
  });

  it('renders patient identifiers (MRN and DOB)', () => {
    render(<PatientBanner patient={mockPatient} />);
    
    expect(screen.getByText(/MRN: 12345678/)).toBeInTheDocument();
    expect(screen.getByText(/DOB: 15\/03\/1979/)).toBeInTheDocument();
  });

  it('displays allergy alert when patient has allergies', () => {
    render(<PatientBanner patient={mockPatient} />);
    
    expect(screen.getByText(/ALLERGIES:/)).toBeInTheDocument();
    expect(screen.getByText(/Penicillin \(Anaphylaxis\)/)).toBeInTheDocument();
  });

  it('applies severe class for severe allergies', () => {
    const { container } = render(<PatientBanner patient={mockPatient} />);
    
    const allergyAlert = container.querySelector('.cerner-allergy-alert');
    expect(allergyAlert).toHaveClass('severe');
  });

  it('does not show allergy alert for NKDA patients', () => {
    const nkdaPatient = {
      ...mockPatient,
      allergies: [{ allergen: 'NKDA', reaction: 'None', severity: 'mild' as const }]
    };
    
    const { container } = render(<PatientBanner patient={nkdaPatient} />);
    
    const allergyAlert = container.querySelector('.cerner-allergy-alert');
    expect(allergyAlert).not.toBeInTheDocument();
  });

  it('displays active problems', () => {
    render(<PatientBanner patient={mockPatient} />);
    
    expect(screen.getByText(/Active Problems:/)).toBeInTheDocument();
    expect(screen.getByText(/Type 2 Diabetes, Hypertension/)).toBeInTheDocument();
  });

  it('displays medication count', () => {
    render(<PatientBanner patient={mockPatient} />);
    
    expect(screen.getByText(/Current Medications:/)).toBeInTheDocument();
    expect(screen.getByText(/1 medications/)).toBeInTheDocument();
  });

  it('handles patient with no allergies gracefully', () => {
    const noAllergyPatient = {
      ...mockPatient,
      allergies: []
    };
    
    const { container } = render(<PatientBanner patient={noAllergyPatient} />);
    
    const allergyAlert = container.querySelector('.cerner-allergy-alert');
    expect(allergyAlert).not.toBeInTheDocument();
  });

  it('renders User icon for patient avatar', () => {
    const { container } = render(<PatientBanner patient={mockPatient} />);
    
    // Check for the presence of the User icon (svg with lucide classes)
    const userIcon = container.querySelector('.lucide-user');
    expect(userIcon).toBeInTheDocument();
  });
});
