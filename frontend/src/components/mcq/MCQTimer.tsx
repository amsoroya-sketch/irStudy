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

  useEffect(() => {
    setDisplayTime(timeRemaining);
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

  return (
    <Box
      role="timer"
      aria-label={`Time remaining: ${formatTime(displayTime)}`}
      sx={{ width: '100%' }}
    >
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
        <TimerIcon
          color={colour}
          aria-hidden="true"
          sx={{ fontSize: 20 }}
        />
        <Typography
          variant="body2"
          color={colour === 'error' ? 'error' : colour === 'warning' ? 'warning.main' : 'success.main'}
          sx={{ fontWeight: 600, minWidth: 50 }}
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
