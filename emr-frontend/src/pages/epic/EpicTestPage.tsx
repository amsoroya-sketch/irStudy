import React, { useState } from 'react';
import { EpicSidebar } from '../../components/epic/EpicSidebar';
import { EpicPatientBanner } from '../../components/epic/EpicPatientBanner';
import { EpicNoteEditor } from '../../components/epic/EpicNoteEditor';

export const EpicTestPage: React.FC = () => {
  const [currentPath, setCurrentPath] = useState('/epic/notes');

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

  const handleSave = async (data: any) => {
    console.log('Saving note:', data);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
  };

  return (
    <div className="flex h-screen" data-theme="epic">
      <EpicSidebar
        currentPath={currentPath}
        onNavigate={setCurrentPath}
        sessionId="test-session-123"
      />
      <div className="flex-1 flex flex-col">
        <EpicPatientBanner patient={mockPatient} />
        <div className="flex-1 p-6 bg-gray-50 overflow-auto">
          <EpicNoteEditor
            sessionId="test-session-123"
            onSave={handleSave}
            autoSaveInterval={10}
          />
        </div>
      </div>
    </div>
  );
};
