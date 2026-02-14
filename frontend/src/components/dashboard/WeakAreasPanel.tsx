/**
 * WeakAreasPanel Component
 * Displays specialties needing improvement with recommendations
 */

import React from 'react';
import { Card, CardContent, Typography, Alert, Stack, Box } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import type { WeakArea } from '../../types/dashboard';

interface WeakAreasPanelProps {
  weakAreas: WeakArea[];
}

const WeakAreasPanel: React.FC<WeakAreasPanelProps> = ({ weakAreas }) => {
  // Format specialty names for display
  const formatSpecialty = (specialty: string) => {
    return specialty
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <WarningIcon color="warning" sx={{ mr: 1 }} />
          <Typography variant="h6">Areas for Improvement</Typography>
        </Box>

        {weakAreas.length === 0 ? (
          <Alert severity="success" icon={<CheckCircleIcon />}>
            <Typography variant="body2">
              Great work! No weak areas identified. Keep up the excellent performance!
            </Typography>
          </Alert>
        ) : (
          <Stack spacing={2}>
            {weakAreas.map((area, index) => (
              <Alert key={index} severity="warning" sx={{ textAlign: 'left' }}>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  {formatSpecialty(area.specialty)}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Accuracy: {area.accuracy_rate.toFixed(1)}% ({area.total_attempts} attempts)
                </Typography>
                <Typography variant="body2">
                  <strong>Recommendation:</strong> Review{' '}
                  {area.recommended_study_cards > 0
                    ? `${area.recommended_study_cards} study cards`
                    : 'more materials'}{' '}
                  and practice 10 more MCQs in this specialty.
                </Typography>
              </Alert>
            ))}
          </Stack>
        )}

        {weakAreas.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Weak areas are identified as specialties with accuracy below 70% and at least 5
              attempts.
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default WeakAreasPanel;
