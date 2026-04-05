/**
 * OSCEToEMRModal.tsx - OSCE to EMR Conversion Modal
 *
 * Displays conversion progress and results for OSCE-to-EMR transformation
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - Converts AI OSCE conversation to pre-filled EMR SOAP note
 * - Uses Claude API for clinical data extraction
 * - AMC Clinical Examination workflow (history-taking → documentation)
 *
 * WCAG 2.2 AA COMPLIANT:
 * - Keyboard navigation (Tab, Enter, Escape)
 * - Screen reader announcements for conversion status
 * - Focus management (dialog title, close button)
 * - ARIA labels for all interactive elements
 *
 * @module components/integration
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  LinearProgress,
  Typography,
  Box,
  Alert,
  Chip,
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { convertOSCEToEMR, ConversionResponse } from '../../api/integration';

/**
 * OSCEToEMRModal Props
 */
export interface OSCEToEMRModalProps {
  /** Dialog open state */
  open: boolean;
  /** Close handler */
  onClose: () => void;
  /** OSCE attempt ID to convert */
  osceAttemptId: string;
}

/**
 * OSCEToEMRModal Component
 *
 * Handles OSCE-to-EMR conversion workflow:
 * 1. Show conversion explanation
 * 2. Display progress spinner during API call
 * 3. Show success with pre-fill percentage
 * 4. Navigate to EMR session on continue
 *
 * @param props - Component props
 */
export const OSCEToEMRModal: React.FC<OSCEToEMRModalProps> = ({
  open,
  onClose,
  osceAttemptId,
}) => {
  const navigate = useNavigate();
  const [conversionSuccess, setConversionSuccess] = useState(false);
  const [conversionData, setConversionData] = useState<ConversionResponse | null>(null);

  /**
   * Conversion mutation
   */
  const conversionMutation = useMutation({
    mutationFn: () => convertOSCEToEMR(osceAttemptId),
    onSuccess: (data: ConversionResponse) => {
      setConversionSuccess(true);
      setConversionData(data);

      // Announce success to screen readers
      const message = `Conversion successful. ${Math.round(data.pre_fill_percentage * 100)} percent of SOAP note pre-filled.`;
      announceToScreenReader(message);
    },
    onError: (error: unknown) => {
      console.error('[OSCEToEMR] Conversion failed:', error);

      // Announce error to screen readers
      announceToScreenReader('Conversion failed. Please try again or contact support.');
    },
  });

  /**
   * Handle convert button click
   */
  const handleConvert = () => {
    conversionMutation.mutate();
  };

  /**
   * Handle continue to EMR button click
   */
  const handleContinueToEMR = () => {
    if (!conversionData) return;

    navigate(`/emr/session/${conversionData.emr_session_id}`);
    onClose();
  };

  /**
   * Handle dialog close
   */
  const handleClose = () => {
    // Prevent closing during conversion
    if (conversionMutation.isPending) return;

    // Reset state
    setConversionSuccess(false);
    setConversionData(null);
    conversionMutation.reset();

    onClose();
  };

  /**
   * Announce message to screen readers
   * @param message - Message to announce
   */
  const announceToScreenReader = (message: string) => {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);

    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      aria-labelledby="conversion-dialog-title"
      aria-describedby="conversion-dialog-description"
    >
      <DialogTitle id="conversion-dialog-title">
        <Box display="flex" alignItems="center" gap={1}>
          <DescriptionIcon color="primary" />
          <Typography variant="h6" component="span">
            Convert to EMR Practice
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent id="conversion-dialog-description">
        {/* Initial State - Before Conversion */}
        {!conversionMutation.isPending && !conversionSuccess && !conversionMutation.isError && (
          <Box>
            <Typography variant="body1" gutterBottom>
              Transform your OSCE conversation into a pre-filled EMR SOAP note.
            </Typography>

            <Box sx={{ mt: 3, mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom fontWeight="bold">
                What will be auto-filled:
              </Typography>
              <Box component="ul" sx={{ pl: 2 }}>
                <Typography component="li" variant="body2" sx={{ mb: 1 }}>
                  <strong>Subjective:</strong> Patient history from conversation transcript
                </Typography>
                <Typography component="li" variant="body2" sx={{ mb: 1 }}>
                  <strong>Objective:</strong> Examination findings if discussed
                </Typography>
                <Typography component="li" variant="body2" sx={{ mb: 1 }}>
                  <strong>Assessment:</strong> Clinical reasoning and differential diagnoses
                </Typography>
                <Typography component="li" variant="body2" sx={{ mb: 1 }}>
                  <strong>Plan:</strong> Management recommendations based on conversation
                </Typography>
              </Box>
            </Box>

            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                This uses AI to extract clinical information from your OSCE conversation.
                Review and refine the auto-filled content before submission.
              </Typography>
            </Alert>
          </Box>
        )}

        {/* Loading State - During Conversion */}
        {conversionMutation.isPending && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CircularProgress size={60} aria-label="Converting OSCE to EMR" />
            <Typography variant="body1" sx={{ mt: 2 }} fontWeight="bold">
              Analyzing conversation transcript...
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Using AI to extract clinical information
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
              This may take 3-5 seconds
            </Typography>
          </Box>
        )}

        {/* Success State - Conversion Complete */}
        {conversionSuccess && conversionData && (
          <Box>
            <Alert
              severity="success"
              icon={<CheckCircleIcon fontSize="large" />}
              sx={{ mb: 3 }}
            >
              <Typography variant="body1" fontWeight="bold">
                Conversion successful! Your SOAP note is ready.
              </Typography>
            </Alert>

            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" gutterBottom fontWeight="bold">
                Pre-fill Progress:
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                <LinearProgress
                  variant="determinate"
                  value={conversionData.pre_fill_percentage * 100}
                  sx={{ flexGrow: 1, height: 10, borderRadius: 1 }}
                  aria-label={`${Math.round(conversionData.pre_fill_percentage * 100)} percent pre-filled`}
                />
                <Chip
                  label={`${Math.round(conversionData.pre_fill_percentage * 100)}%`}
                  size="small"
                  color="success"
                  aria-label="Pre-fill percentage"
                />
              </Box>
            </Box>

            <Box sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                Extraction Details:
              </Typography>
              <Typography variant="body2" sx={{ mb: 0.5 }}>
                <strong>Confidence:</strong>{' '}
                {Math.round(conversionData.conversion_metadata.extraction_confidence * 100)}%
              </Typography>
              <Typography variant="body2" sx={{ mb: 0.5 }}>
                <strong>Tokens Used:</strong> {conversionData.conversion_metadata.tokens_used}
              </Typography>
              <Typography variant="body2">
                <strong>Processing Time:</strong>{' '}
                {conversionData.conversion_metadata.api_response_time_ms}ms
              </Typography>
            </Box>

            <Alert severity="info">
              <Typography variant="body2">
                Your EMR session has been pre-filled from the OSCE conversation. Review and
                refine the auto-generated content before submitting for validation.
              </Typography>
            </Alert>
          </Box>
        )}

        {/* Error State - Conversion Failed */}
        {conversionMutation.isError && (
          <Alert severity="error" icon={<ErrorIcon fontSize="large" />}>
            <Typography variant="body1" fontWeight="bold" gutterBottom>
              Conversion failed
            </Typography>
            <Typography variant="body2">
              Unable to convert OSCE conversation to EMR SOAP note. Please try again or contact
              support if the problem persists.
            </Typography>
          </Alert>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        {/* Initial State Actions */}
        {!conversionSuccess && (
          <>
            <Button
              onClick={handleClose}
              disabled={conversionMutation.isPending}
              aria-label="Cancel conversion"
            >
              Cancel
            </Button>
            <Button
              onClick={handleConvert}
              variant="contained"
              color="primary"
              disabled={conversionMutation.isPending}
              startIcon={<DescriptionIcon />}
              aria-label="Start conversion to EMR"
            >
              Convert Now
            </Button>
          </>
        )}

        {/* Success State Actions */}
        {conversionSuccess && (
          <>
            <Button onClick={handleClose} aria-label="Close dialog">
              Close
            </Button>
            <Button
              onClick={handleContinueToEMR}
              variant="contained"
              color="success"
              startIcon={<CheckCircleIcon />}
              aria-label="Continue to EMR session"
            >
              Continue to EMR
            </Button>
          </>
        )}

        {/* Error State Actions */}
        {conversionMutation.isError && (
          <>
            <Button onClick={handleClose} aria-label="Close dialog">
              Close
            </Button>
            <Button
              onClick={handleConvert}
              variant="outlined"
              color="primary"
              aria-label="Retry conversion"
            >
              Try Again
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default OSCEToEMRModal;
