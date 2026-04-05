/**
 * Cerner AppBar Component
 *
 * Dark-themed top navigation for Cerner PowerChart.
 * Reuses Epic AppBar logic with Cerner blue styling.
 */

import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Save as SaveIcon,
  Send as SendIcon,
  ExitToApp as ExitIcon,
  CheckCircle as CheckCircleIcon,
  Sync as SyncIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { MockPatient, AutoSaveStatus } from '../../../types/emr';

interface CernerAppBarProps {
  patient: MockPatient;
  onSave: () => void;
  onSubmit: () => void;
  onExit: () => void;
  autoSaveStatus: AutoSaveStatus;
  isSubmitting?: boolean;
}

export const CernerAppBar: React.FC<CernerAppBarProps> = ({
  patient,
  onSave,
  onSubmit,
  onExit,
  autoSaveStatus,
  isSubmitting = false,
}) => {
  const autoSaveConfig = {
    idle: { color: 'default' as const, icon: null, label: 'Not saved' },
    saving: { color: 'info' as const, icon: <SyncIcon />, label: 'Saving...' },
    saved: { color: 'success' as const, icon: <CheckCircleIcon />, label: 'All changes saved' },
    error: { color: 'error' as const, icon: <ErrorIcon />, label: 'Save failed' },
  };

  const currentConfig = autoSaveConfig[autoSaveStatus];

  return (
    <AppBar position="sticky" sx={{ backgroundColor: 'primary.main' }} role="banner">
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box display="flex" alignItems="center" gap={2}>
          <Typography
            variant="h6"
            component="h1"
            sx={{ fontWeight: 700, letterSpacing: 0.5, color: 'primary.contrastText' }}
          >
            Cerner PowerChart
          </Typography>
          <Typography variant="body2" sx={{ color: 'primary.contrastText', opacity: 0.9 }}>
            Practice System
          </Typography>
        </Box>

        <Box
          display="flex"
          alignItems="center"
          gap={1}
          sx={{
            px: 2,
            py: 0.5,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: 1,
          }}
          role="region"
          aria-label="Current patient"
        >
          <Typography variant="body1" sx={{ fontWeight: 600, color: 'primary.contrastText' }}>
            {patient.full_name}
          </Typography>
          <Typography variant="body2" sx={{ color: 'primary.contrastText', opacity: 0.9 }}>
            MRN: {patient.mrn}
          </Typography>
          <Typography variant="body2" sx={{ color: 'primary.contrastText', opacity: 0.9 }}>
            {patient.age_years}y • {patient.gender}
          </Typography>
        </Box>

        <Box display="flex" alignItems="center" gap={2}>
          <Tooltip title={currentConfig.label} arrow>
            <Chip
              icon={currentConfig.icon || undefined}
              label={currentConfig.label}
              color={currentConfig.color}
              size="small"
              sx={{ minWidth: 120 }}
              role="status"
              aria-live="polite"
            />
          </Tooltip>

          <Tooltip title="Save draft (Ctrl+S)" arrow>
            <Button
              variant="outlined"
              startIcon={<SaveIcon />}
              onClick={onSave}
              disabled={isSubmitting}
              sx={{
                color: 'primary.contrastText',
                borderColor: 'rgba(255, 255, 255, 0.3)',
                '&:hover': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
              aria-label="Save draft"
            >
              Save Draft
            </Button>
          </Tooltip>

          <Tooltip title="Submit for validation" arrow>
            <Button
              variant="contained"
              startIcon={<SendIcon />}
              onClick={onSubmit}
              disabled={isSubmitting}
              sx={{
                backgroundColor: 'secondary.main',
                color: 'secondary.contrastText',
                '&:hover': {
                  backgroundColor: 'secondary.dark',
                },
              }}
              aria-label="Submit for review"
            >
              {isSubmitting ? 'Submitting...' : 'Submit for Review'}
            </Button>
          </Tooltip>

          <Tooltip title="Exit session" arrow>
            <IconButton
              onClick={onExit}
              disabled={isSubmitting}
              sx={{
                color: 'primary.contrastText',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
              aria-label="Exit session"
            >
              <ExitIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};
