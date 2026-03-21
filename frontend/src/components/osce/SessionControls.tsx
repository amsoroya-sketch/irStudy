/**
 * SessionControls.tsx - OSCE Session Control Buttons
 * Material-UI controls for pause/resume/end session actions
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC Clinical Examination session management
 * - Confirmation dialog for session termination
 * - WCAG 2.2 AA compliant (keyboard navigation, ARIA labels)
 *
 * SECURITY:
 * - No session manipulation without user confirmation
 * - Loading states prevent duplicate API calls
 */

import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import PauseIcon from '@mui/icons-material/Pause';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';

/**
 * Component props
 */
export interface SessionControlsProps {
  sessionStatus: 'active' | 'paused' | 'ended';
  onPause: () => Promise<void>;               // Pause session callback
  onResume: () => Promise<void>;              // Resume session callback
  onEnd: () => Promise<void>;                 // End session callback
  disabled?: boolean;                         // Disable all controls
}

/**
 * Styled Components (Material-UI 7 pattern)
 */
const ControlsContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  alignItems: 'center',
  flexWrap: 'wrap',
  [theme.breakpoints.down('sm')]: {
    gap: theme.spacing(0.5),
  },
}));

const StyledIconButton = styled(IconButton)(({ theme }) => ({
  minWidth: '44px',
  minHeight: '44px',
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(1),
  },
}));

/**
 * SessionControls Component
 *
 * Provides pause/resume/end session controls with confirmation dialog
 *
 * @param props - Component props
 */
export function SessionControls({
  sessionStatus,
  onPause,
  onResume,
  onEnd,
  disabled = false,
}: SessionControlsProps): JSX.Element | null {
  // State
  const [endDialogOpen, setEndDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handle pause/resume toggle
   */
  const handlePauseResume = useCallback(async () => {
    if (disabled || loading) return;

    setLoading(true);
    setError(null);

    try {
      if (sessionStatus === 'active') {
        await onPause();
      } else if (sessionStatus === 'paused') {
        await onResume();
      }
    } catch (err) {
      console.error('[SessionControls] Failed to pause/resume session:', err);
      setError(
        sessionStatus === 'active'
          ? 'Failed to pause session. Please try again.'
          : 'Failed to resume session. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  }, [sessionStatus, onPause, onResume, disabled, loading]);

  /**
   * Handle end session (confirmed)
   */
  const handleEndSession = useCallback(async () => {
    if (disabled || loading) return;

    setLoading(true);
    setError(null);

    try {
      await onEnd();
      setEndDialogOpen(false);
      // Navigation handled by parent component
    } catch (err) {
      console.error('[SessionControls] Failed to end session:', err);
      setError('Failed to end session. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [onEnd, disabled, loading]);

  /**
   * Open end session confirmation dialog
   */
  const handleOpenEndDialog = useCallback(() => {
    if (disabled || loading) return;
    setEndDialogOpen(true);
    setError(null);
  }, [disabled, loading]);

  /**
   * Close end session confirmation dialog
   */
  const handleCloseEndDialog = useCallback(() => {
    if (loading) return;
    setEndDialogOpen(false);
    setError(null);
  }, [loading]);

  // Don't render controls if session has ended
  if (sessionStatus === 'ended') {
    return null;
  }

  return (
    <>
      <ControlsContainer>
        {/* Pause/Resume Button */}
        <StyledIconButton
          onClick={handlePauseResume}
          disabled={disabled || loading}
          color="primary"
          aria-label={sessionStatus === 'active' ? 'Pause session' : 'Resume session'}
          title={sessionStatus === 'active' ? 'Pause session' : 'Resume session'}
        >
          {loading && sessionStatus === 'active' ? (
            <CircularProgress size={24} />
          ) : sessionStatus === 'active' ? (
            <PauseIcon />
          ) : loading && sessionStatus === 'paused' ? (
            <CircularProgress size={24} />
          ) : (
            <PlayArrowIcon />
          )}
        </StyledIconButton>

        {/* End Session Button */}
        <Button
          variant="outlined"
          color="error"
          startIcon={<StopIcon />}
          onClick={handleOpenEndDialog}
          disabled={disabled || loading}
          aria-label="End OSCE session"
          sx={{
            minWidth: { xs: 'auto', sm: '120px' },
            px: { xs: 1.5, sm: 2 },
          }}
        >
          <Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>
            End Session
          </Box>
          <Box component="span" sx={{ display: { xs: 'inline', sm: 'none' } }}>
            End
          </Box>
        </Button>
      </ControlsContainer>

      {/* Error Alert */}
      {error && (
        <Alert
          severity="error"
          sx={{ mt: 2 }}
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}

      {/* End Session Confirmation Dialog */}
      <Dialog
        open={endDialogOpen}
        onClose={handleCloseEndDialog}
        aria-labelledby="end-session-dialog-title"
        aria-describedby="end-session-dialog-description"
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle id="end-session-dialog-title">
          End OSCE Session?
        </DialogTitle>
        <DialogContent>
          <Typography id="end-session-dialog-description" variant="body1" paragraph>
            Are you sure you want to end this session early?
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Your performance will be scored based on the conversation so far. You cannot
            resume this session after ending it.
          </Typography>

          {/* Additional context for time remaining */}
          <Alert severity="info" sx={{ mt: 2 }}>
            <strong>Note:</strong> Ending the session early may impact your score. Consider
            using the pause button if you need a break.
          </Alert>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            onClick={handleCloseEndDialog}
            disabled={loading}
            color="primary"
          >
            Cancel
          </Button>
          <Button
            onClick={handleEndSession}
            variant="contained"
            color="error"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={16} /> : <StopIcon />}
            autoFocus
          >
            {loading ? 'Ending...' : 'End Session'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default SessionControls;
