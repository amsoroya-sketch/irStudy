/**
 * Validation Status Banner Component
 *
 * Displays real-time validation status with polling.
 *
 * Features:
 * - Polls validation endpoint every 2 seconds until complete
 * - Progress indicator during validation
 * - Success/error alerts
 * - WCAG 2.2 AA accessible
 */

import React from 'react';
import { Box, LinearProgress, Alert, Typography } from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Sync as SyncIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import axiosInstance from '../../../utils/axiosInstance';
import { ValidationResult } from '../../../types/emr';

interface ValidationStatusBannerProps {
  validationId: string;
  onComplete?: (result: ValidationResult) => void;
}

export const ValidationStatusBanner: React.FC<ValidationStatusBannerProps> = ({
  validationId,
  onComplete,
}) => {
  const { data, isLoading } = useQuery<ValidationResult>({
    queryKey: ['validation', validationId],
    queryFn: async () => {
      const response = await axiosInstance.get(`/emr/validation/${validationId}`);
      return response.data;
    },
    refetchInterval: (query) => {
      // Stop polling when validation is complete or failed
      const status = query.state.data?.validation_status;
      return status === 'completed' || status === 'failed' ? false : 2000;
    },
    enabled: !!validationId,
  });

  React.useEffect(() => {
    if (data?.validation_status === 'completed' && onComplete) {
      onComplete(data);
    }
  }, [data, onComplete]);

  if (isLoading || !data) {
    return (
      <Box sx={{ mb: 2 }}>
        <Alert severity="info" icon={<SyncIcon />}>
          <Typography variant="body2">Initializing validation...</Typography>
        </Alert>
        <LinearProgress />
      </Box>
    );
  }

  if (data.validation_status === 'pending' || data.validation_status === 'in_progress') {
    return (
      <Box sx={{ mb: 2 }}>
        <Alert
          severity="info"
          icon={<SyncIcon className="animate-spin" />}
          role="status"
          aria-live="polite"
        >
          <Typography variant="body2" fontWeight={600}>
            Validation in progress...
          </Typography>
          <Typography variant="body2" color="text.secondary">
            AI agent is reviewing your SOAP note, prescriptions, and pathology orders.
            This may take 30-60 seconds.
          </Typography>
        </Alert>
        <LinearProgress />
      </Box>
    );
  }

  if (data.validation_status === 'failed') {
    return (
      <Box sx={{ mb: 2 }}>
        <Alert severity="error" icon={<ErrorIcon />} role="alert">
          <Typography variant="body2" fontWeight={600}>
            Validation failed
          </Typography>
          <Typography variant="body2">
            An error occurred during validation. Please try again.
          </Typography>
        </Alert>
      </Box>
    );
  }

  if (data.validation_status === 'completed') {
    return (
      <Box sx={{ mb: 2 }}>
        <Alert severity="success" icon={<SuccessIcon />} role="status" aria-live="polite">
          <Typography variant="body2" fontWeight={600}>
            Validation complete!
          </Typography>
          <Typography variant="body2">
            Overall Score: <strong>{data.overall_score.toFixed(1)}/10</strong>
          </Typography>
          {data.ahpra_compliance && (
            <Typography variant="body2" color="success.dark">
              ✓ AHPRA documentation standards met
            </Typography>
          )}
        </Alert>
      </Box>
    );
  }

  return null;
};
