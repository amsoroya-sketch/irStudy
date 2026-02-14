// src/components/cerner/PatientBanner.tsx

import React from 'react';
import { AlertTriangle, User } from 'lucide-react';

interface Patient {
  id: string;
  name: string;
  age: number;
  sex: 'M' | 'F' | 'Other';
  mrn: string;
  dob: string;
  allergies: Array<{
    allergen: string;
    reaction: string;
    severity: 'mild' | 'moderate' | 'severe';
  }>;
  activeProblems: string[];
  currentMedications: Array<{
    name: string;
    dose: string;
    frequency: string;
  }>;
}

interface PatientBannerProps {
  patient: Patient;
}

export const PatientBanner: React.FC<PatientBannerProps> = ({ patient }) => {
  const hasAllergies = patient.allergies.length > 0 && patient.allergies[0].allergen !== 'NKDA';
  const severeAllergies = patient.allergies.filter((a) => a.severity === 'severe');

  return (
    <div className="cerner-patient-banner">
      {/* Main Patient Info */}
      <div className="cerner-banner-main">
        <User className="w-6 h-6 text-gray-600" />
        <div className="cerner-patient-name">
          <span className="font-bold text-lg">{patient.name}</span>
          <span className="text-gray-600 ml-2">
            {patient.age}{patient.sex}
          </span>
        </div>
        <div className="cerner-patient-identifiers">
          <span className="cerner-badge">MRN: {patient.mrn}</span>
          <span className="cerner-badge">DOB: {patient.dob}</span>
        </div>
      </div>

      {/* Allergy Alert */}
      {hasAllergies && (
        <div
          className={`cerner-allergy-alert ${
            severeAllergies.length > 0 ? 'severe' : ''
          }`}
        >
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <div>
            <span className="font-semibold">ALLERGIES: </span>
            <span>
              {patient.allergies
                .map((a) => `${a.allergen} (${a.reaction})`)
                .join(', ')}
            </span>
          </div>
        </div>
      )}

      {/* Clinical Summary */}
      <div className="cerner-banner-summary">
        <div className="cerner-summary-section">
          <span className="font-semibold">Active Problems:</span>
          <span className="ml-2">{patient.activeProblems.join(', ')}</span>
        </div>
        <div className="cerner-summary-section">
          <span className="font-semibold">Current Medications:</span>
          <span className="ml-2">
            {patient.currentMedications.length} medications
          </span>
        </div>
      </div>
    </div>
  );
};
