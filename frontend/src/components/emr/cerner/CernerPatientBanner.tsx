/**
 * Cerner Patient Banner Component
 *
 * Dark-themed patient information banner for Cerner PowerChart.
 * Reuses Epic PatientBanner logic with Cerner styling.
 */

import React from 'react';
import { Box, Typography, Alert, Chip, Paper, Grid } from '@mui/material';
import {
  Person as PersonIcon,
  Warning as WarningIcon,
  MonitorHeart as VitalsIcon,
} from '@mui/icons-material';
import { MockPatient } from '../../../types/emr';

interface CernerPatientBannerProps {
  patient: MockPatient;
  compact?: boolean;
}

export const CernerPatientBanner: React.FC<CernerPatientBannerProps> = ({
  patient,
  compact = false,
}) => {
  const hasAllergies = (patient.allergies?.length ?? 0) > 0;

  return (
    <Paper
      elevation={2}
      sx={{
        p: compact ? 1.5 : 2,
        mb: 2,
        backgroundColor: 'background.paper',
        borderLeft: 4,
        borderColor: 'primary.main',
      }}
      role="region"
      aria-label="Patient information banner"
    >
      <Grid container spacing={2} alignItems="center">
        <Grid size={{ xs: 12, md: compact ? 12 : 4 }}>
          <Box display="flex" alignItems="center" gap={1}>
            <PersonIcon color="primary" aria-hidden="true" />
            <Box>
              <Typography variant="h6" component="h2" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                {patient.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {patient.gender} • {patient.age}y
                {patient.date_of_birth && ` • DOB: ${patient.date_of_birth}`}
              </Typography>
              {!compact && (
                <Typography variant="body2" color="text.secondary">
                  {patient.mrn && `MRN: ${patient.mrn}`}
                  {patient.medicare_number && ` • Medicare: ${patient.medicare_number}`}
                </Typography>
              )}
            </Box>
          </Box>
        </Grid>

        <Grid size={{ xs: 12, md: compact ? 12 : 4 }}>
          <Box display="flex" alignItems="center" gap={1}>
            <WarningIcon color={hasAllergies ? 'warning' : 'disabled'} aria-hidden="true" />
            {hasAllergies ? (
              <Alert severity="warning" sx={{ py: 0, px: 1, flexGrow: 1 }} icon={false} role="alert" aria-live="polite">
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Allergies: {patient.allergies?.join(', ')}
                </Typography>
              </Alert>
            ) : (
              <Typography variant="body2" color="text.secondary">
                NKDA (No Known Drug Allergies)
              </Typography>
            )}
          </Box>
        </Grid>

        {!compact && patient.vital_signs && (
          <Grid size={{ xs: 12, md: 4 }}>
            <Box display="flex" alignItems="center" gap={1}>
              <VitalsIcon color="primary" aria-hidden="true" />
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Vital Signs
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                  {patient.vital_signs.bp && (
                    <Chip
                      label={`BP: ${patient.vital_signs.bp}`}
                      size="small"
                      variant="outlined"
                      aria-label={`Blood pressure: ${patient.vital_signs.bp}`}
                    />
                  )}
                  {patient.vital_signs.hr !== undefined && (
                    <Chip
                      label={`HR: ${patient.vital_signs.hr}`}
                      size="small"
                      variant="outlined"
                      aria-label={`Heart rate: ${patient.vital_signs.hr} beats per minute`}
                    />
                  )}
                  {patient.vital_signs.rr !== undefined && (
                    <Chip
                      label={`RR: ${patient.vital_signs.rr}`}
                      size="small"
                      variant="outlined"
                      aria-label={`Respiratory rate: ${patient.vital_signs.rr} breaths per minute`}
                    />
                  )}
                  {patient.vital_signs.temp !== undefined && (
                    <Chip
                      label={`Temp: ${patient.vital_signs.temp}°C`}
                      size="small"
                      variant="outlined"
                      aria-label={`Temperature: ${patient.vital_signs.temp} degrees Celsius`}
                    />
                  )}
                  {patient.vital_signs.spo2 !== undefined && (
                    <Chip
                      label={`SpO2: ${patient.vital_signs.spo2}%`}
                      size="small"
                      variant="outlined"
                      aria-label={`Oxygen saturation: ${patient.vital_signs.spo2} percent`}
                    />
                  )}
                </Box>
              </Box>
            </Box>
          </Grid>
        )}
      </Grid>
    </Paper>
  );
};
