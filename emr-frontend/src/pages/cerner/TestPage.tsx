import { CernerSidebar } from '../../components/cerner/CernerSidebar';
import { PatientBanner } from '../../components/cerner/PatientBanner';
import { SOAPNoteEditor } from '../../components/cerner/SOAPNoteEditor';
import { useState } from 'react';

export const CernerTestPage = () => {
  const [currentPath, setCurrentPath] = useState('/cerner/soap-notes');

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
    activeProblems: ['Type 2 Diabetes', 'Hypertension', 'Asthma'],
    currentMedications: [
      { name: 'Metformin', dose: '500mg', frequency: 'BD' }
    ]
  };

  const handleSave = async (data: any) => {
    console.log('Saving SOAP note:', data);
    await new Promise((resolve) => setTimeout(resolve, 1000));
  };

  return (
    <div className="flex" data-theme="cerner">
      <CernerSidebar
        currentPath={currentPath}
        onNavigate={setCurrentPath}
        sessionId="test-session"
      />
      <div className="flex-1">
        <PatientBanner patient={mockPatient} />
        <div className="p-8">
          <SOAPNoteEditor sessionId="test-session" onSave={handleSave} />
        </div>
      </div>
    </div>
  );
};
