/**
 * SessionTimer.tsx - 8-minute OSCE Session Countdown Timer
 * Material-UI timer component with AMC Clinical Exam standards
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC Clinical Examination standard: 8 minutes per station
 * - 1-minute warning notification (60 seconds)
 * - Auto-end session at 0:00
 *
 * WCAG 2.2 AA COMPLIANT:
 * - ARIA live region for timer updates
 * - High contrast warning colors
 * - Keyboard accessible
 *
 * PERFORMANCE:
 * - ±100ms timer accuracy over full session
 * - Cleanup on unmount (useEffect return)
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Box, Typography, Alert } from '@mui/material';
import { styled } from '@mui/material/styles';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';

/**
 * Component props
 */
export interface SessionTimerProps {
  startedAt: string;           // ISO timestamp when session started
  pausedAt?: string;           // ISO timestamp when session was paused
  sessionStatus: 'active' | 'paused' | 'ended';
  onTimeUp: () => void;        // Callback when timer reaches 0:00
}

/**
 * Styled Components (Material-UI 7 pattern)
 */
const TimerContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  border: `2px solid ${theme.palette.divider}`,
  minWidth: '200px',
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(1.5),
    gap: theme.spacing(1),
    minWidth: '160px',
  },
}));

const TimerText = styled(Typography, {
  shouldForwardProp: (prop) => prop !== 'warning',
})<{ warning?: boolean }>(({ theme, warning }) => ({
  fontSize: '2rem',
  fontWeight: 700,
  fontFamily: 'monospace',
  color: warning ? theme.palette.warning.main : theme.palette.text.primary,
  minWidth: '85px',
  textAlign: 'center',
  [theme.breakpoints.down('sm')]: {
    fontSize: '1.5rem',
    minWidth: '70px',
  },
}));

const StatusText = styled(Typography)(({ theme }) => ({
  fontSize: '0.875rem',
  color: theme.palette.text.secondary,
  fontWeight: 500,
  [theme.breakpoints.down('sm')]: {
    fontSize: '0.75rem',
  },
}));

/**
 * AMC Clinical Exam Standards
 */
const TOTAL_SECONDS = 480;      // 8 minutes
const WARNING_THRESHOLD = 60;   // 1 minute warning

/**
 * SessionTimer Component
 *
 * 8-minute countdown timer with pause/resume support and 1-minute warning
 *
 * @param props - Component props
 */
export function SessionTimer({
  startedAt,
  pausedAt,
  sessionStatus,
  onTimeUp,
}: SessionTimerProps): JSX.Element {
  // State
  const [remainingSeconds, setRemainingSeconds] = useState(TOTAL_SECONDS);
  const [showWarning, setShowWarning] = useState(false);
  const [accumulatedPauseTime, setAccumulatedPauseTime] = useState(0);

  // Refs
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const onTimeUpRef = useRef(onTimeUp);
  const lastPauseTimeRef = useRef<number>(0);

  // Update onTimeUp ref when it changes
  useEffect(() => {
    onTimeUpRef.current = onTimeUp;
  }, [onTimeUp]);

  /**
   * Calculate remaining seconds based on start time and pause time
   */
  const calculateRemainingSeconds = useCallback((): number => {
    const startTime = new Date(startedAt).getTime();
    const currentTime = Date.now();

    // Calculate elapsed time (excluding pauses)
    let elapsedSeconds: number;

    if (sessionStatus === 'paused' && pausedAt) {
      // Session is paused - use pause time as current time
      const pauseTime = new Date(pausedAt).getTime();
      elapsedSeconds = Math.floor((pauseTime - startTime - accumulatedPauseTime) / 1000);
    } else {
      // Session is active - use current time
      elapsedSeconds = Math.floor((currentTime - startTime - accumulatedPauseTime) / 1000);
    }

    const remaining = Math.max(0, TOTAL_SECONDS - elapsedSeconds);
    return remaining;
  }, [startedAt, pausedAt, sessionStatus, accumulatedPauseTime]);

  /**
   * Update accumulated pause time when session is paused/resumed
   */
  useEffect(() => {
    if (sessionStatus === 'paused' && pausedAt) {
      // Record when pause started
      lastPauseTimeRef.current = new Date(pausedAt).getTime();
    } else if (sessionStatus === 'active' && lastPauseTimeRef.current > 0) {
      // Session resumed - add pause duration to accumulated time
      const pauseDuration = Date.now() - lastPauseTimeRef.current;
      setAccumulatedPauseTime((prev) => prev + pauseDuration);
      lastPauseTimeRef.current = 0;
    }
  }, [sessionStatus, pausedAt]);

  /**
   * Timer tick effect
   */
  useEffect(() => {
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Don't run timer if session is ended
    if (sessionStatus === 'ended') {
      return;
    }

    // Calculate initial remaining time
    const updateTimer = () => {
      const remaining = calculateRemainingSeconds();
      setRemainingSeconds(remaining);

      // Show warning at 1 minute
      setShowWarning(remaining <= WARNING_THRESHOLD && remaining > 0);

      // Call onTimeUp when timer reaches 0
      if (remaining <= 0) {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        onTimeUpRef.current();
      }
    };

    // Initial update
    updateTimer();

    // Check if time is already up
    const initial = calculateRemainingSeconds();
    if (initial <= 0) {
      onTimeUpRef.current();
      return;
    }

    // Only run interval if session is active
    if (sessionStatus === 'active') {
      // Update timer every 100ms for ±100ms accuracy over 8 minutes
      intervalRef.current = setInterval(updateTimer, 100);
    }

    // Cleanup interval on unmount or status change
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [startedAt, sessionStatus, calculateRemainingSeconds]);

  /**
   * Format seconds as MM:SS
   */
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  /**
   * Get status text
   */
  const getStatusText = (): string => {
    if (sessionStatus === 'ended') {
      return 'Session ended';
    }
    if (sessionStatus === 'paused') {
      return 'Paused';
    }
    return 'remaining';
  };

  return (
    <>
      <TimerContainer role="timer" aria-live="polite" aria-atomic="true">
        <AccessTimeIcon
          color={remainingSeconds <= WARNING_THRESHOLD ? 'warning' : 'action'}
          fontSize="large"
          aria-hidden="true"
        />
        <Box>
          <TimerText
            warning={remainingSeconds <= WARNING_THRESHOLD}
            component="div"
            aria-label={`${formatTime(remainingSeconds)} ${getStatusText()}`}
          >
            {formatTime(remainingSeconds)}
          </TimerText>
          <StatusText variant="body2">
            {getStatusText()}
          </StatusText>
        </Box>
      </TimerContainer>

      {/* 1-minute warning notification */}
      {showWarning && remainingSeconds > 0 && sessionStatus === 'active' && (
        <Alert
          severity="warning"
          icon={<WarningAmberIcon />}
          sx={{ mt: 2 }}
          role="alert"
          aria-live="assertive"
        >
          <strong>1 minute remaining!</strong> Please begin wrapping up your consultation.
        </Alert>
      )}
    </>
  );
}

export default SessionTimer;
