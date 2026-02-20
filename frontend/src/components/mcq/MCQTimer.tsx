/**
 * MCQ Timer Component
 * Countdown timer with visual indicators for MCQ practice
 *
 * ACCESSIBILITY:
 * - ARIA role="timer" for screen readers
 * - Color coding with sufficient contrast (WCAG 2.2 AA)
 * - Visual and text indicators for time remaining
 */

import { useEffect, useState } from 'react';
import { Box, LinearProgress, Typography, Stack } from '@mui/material';
import { Timer as TimerIcon } from '@mui/icons-material';

export interface MCQTimerProps {
  /** Time remaining in seconds */
  timeRemaining: number;
  /** Callback when time updates (called every second) */
  onTimeUpdate: (time: number) => void;
  /** Pause the timer */
  isPaused: boolean;
  /** Total time allocated (default 120 seconds) */
  totalTime?: number;
}

/**
 * Format seconds as MM:SS
 */
const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

/**
 * Get colour coding based on time remaining
 * - green: >60s
 * - warning (yellow): 30-60s
 * - error (red): <30s
 */
const getColour = (seconds: number, total: number): 'success' | 'warning' | 'error' => {
  const percentage = (seconds / total) * 100;
  if (percentage > 50) return 'success';
  if (percentage > 25) return 'warning';
  return 'error';
};

/**
 * MCQ Timer Component
 */
export const MCQTimer: React.FC<MCQTimerProps> = ({
  timeRemaining,
  onTimeUpdate,
  isPaused,
  totalTime = 120,
}) => {
  const [displayTime, setDisplayTime] = useState(timeRemaining);
  const [announced30s, setAnnounced30s] = useState(false);
  const [announced10s, setAnnounced10s] = useState(false);

  useEffect(() => {
    setDisplayTime(timeRemaining);
    // Reset announcements when time resets
    if (timeRemaining > 30) {
      setAnnounced30s(false);
      setAnnounced10s(false);
    }
  }, [timeRemaining]);

  useEffect(() => {
    if (isPaused || displayTime <= 0) {
      return;
    }

    const interval = setInterval(() => {
      setDisplayTime((prev) => {
        const newTime = Math.max(0, prev - 1);
        onTimeUpdate(newTime);
        return newTime;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isPaused, displayTime, onTimeUpdate]);

  const colour = getColour(displayTime, totalTime);
  const progressPercentage = (displayTime / totalTime) * 100;

  // Determine if we should announce warnings
  const shouldAnnounce30s = displayTime === 30 && !announced30s && !isPaused;
  const shouldAnnounce10s = displayTime === 10 && !announced10s && !isPaused;

  // Mark announcements as done
  useEffect(() => {
    if (shouldAnnounce30s) setAnnounced30s(true);
    if (shouldAnnounce10s) setAnnounced10s(true);
  }, [shouldAnnounce30s, shouldAnnounce10s]);

  return (
    <Box
      role="timer"
      aria-label={`Time remaining: ${formatTime(displayTime)}`}
      sx={{ width: '100%' }}
    >
      {/* Screen reader announcements for time warnings */}
      <Box
        role="status"
        aria-live="polite"
        aria-atomic="true"
        sx={{
          position: 'absolute',
          left: '-10000px',
          width: '1px',
          height: '1px',
          overflow: 'hidden',
        }}
      >
        {shouldAnnounce30s && 'Warning: 30 seconds remaining'}
        {shouldAnnounce10s && 'Warning: 10 seconds remaining'}
      </Box>

      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
        <TimerIcon
          color={colour}
          aria-hidden="true"
          sx={{
            fontSize: 20,
            animation: displayTime < 10 && !isPaused ? 'pulse 1s infinite' : 'none',
            '@keyframes pulse': {
              '0%, 100%': { opacity: 1 },
              '50%': { opacity: 0.5 },
            },
          }}
        />
        <Typography
          variant="body2"
          color={colour === 'error' ? 'error' : colour === 'warning' ? 'warning.main' : 'success.main'}
          sx={{
            fontWeight: 600,
            minWidth: 50,
            animation: displayTime < 10 && !isPaused ? 'pulse 1s infinite' : 'none',
          }}
        >
          {formatTime(displayTime)}
        </Typography>
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ ml: 1 }}
        >
          {isPaused ? '(Paused)' : ''}
        </Typography>
      </Stack>
      <LinearProgress
        variant="determinate"
        value={progressPercentage}
        color={colour}
        aria-label={`${Math.round(progressPercentage)}% time remaining`}
        sx={{
          height: 8,
          borderRadius: 1,
          backgroundColor: (theme) =>
            theme.palette.mode === 'light' ? 'grey.200' : 'grey.800',
        }}
      />
    </Box>
  );
};

export default MCQTimer;
