import React from 'react';
import { AlertCircle, Calendar, MapPin, Phone } from 'lucide-react';
import { motion } from 'framer-motion';

interface PatientData {
  firstName: string;
  lastName: string;
  mrn: string;
  dob: string; // ISO date string
  age: number;
  gender: 'M' | 'F' | 'Other';
  allergies: string[];
  alerts: string[];
  contact: {
    phone?: string;
    address?: string;
  };
}

interface EpicPatientBannerProps {
  patient: PatientData;
  encounterType?: string;
  location?: string;
}

export const EpicPatientBanner: React.FC<EpicPatientBannerProps> = ({
  patient,
  encounterType = 'Outpatient Visit',
  location = 'General Medicine Clinic'
}) => {
  const calculateAge = (dob: string): string => {
    const birthDate = new Date(dob);
    const today = new Date();
    const years = today.getFullYear() - birthDate.getFullYear();
    const months = today.getMonth() - birthDate.getMonth();

    if (years < 2) {
      const totalMonths = years * 12 + months;
      return `${totalMonths} mo`;
    }
    return `${years} y`;
  };

  const formatDOB = (dob: string): string => {
    return new Date(dob).toLocaleDateString('en-AU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <div className="epic-patient-banner">
      {/* Main Patient Info */}
      <div className="epic-banner-main">
        <div className="epic-banner-name">
          {patient.lastName.toUpperCase()}, {patient.firstName}
        </div>
        <div className="epic-banner-demographics">
          <span className="epic-demo-item">
            <Calendar size={14} />
            {formatDOB(patient.dob)} ({calculateAge(patient.dob)})
          </span>
          <span className="epic-demo-divider">•</span>
          <span className="epic-demo-item">
            {patient.gender === 'M' ? 'Male' : patient.gender === 'F' ? 'Female' : 'Other'}
          </span>
          <span className="epic-demo-divider">•</span>
          <span className="epic-demo-item">MRN: {patient.mrn}</span>
        </div>
      </div>

      {/* Encounter Info */}
      <div className="epic-banner-encounter">
        <div className="epic-encounter-type">{encounterType}</div>
        <div className="epic-encounter-location">
          <MapPin size={14} />
          {location}
        </div>
      </div>

      {/* Alerts and Allergies */}
      {(patient.allergies.length > 0 || patient.alerts.length > 0) && (
        <div className="epic-banner-alerts">
          {patient.allergies.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="epic-alert epic-alert-allergy"
            >
              <AlertCircle size={16} />
              <span className="epic-alert-label">Allergies:</span>
              <span className="epic-alert-value">
                {patient.allergies.join(', ')}
              </span>
            </motion.div>
          )}

          {patient.alerts.map((alert, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="epic-alert epic-alert-warning"
            >
              <AlertCircle size={16} />
              <span className="epic-alert-value">{alert}</span>
            </motion.div>
          ))}
        </div>
      )}

      {/* Contact Info (Collapsible) */}
      {patient.contact.phone && (
        <div className="epic-banner-contact">
          <Phone size={14} />
          <span>{patient.contact.phone}</span>
        </div>
      )}
    </div>
  );
};
