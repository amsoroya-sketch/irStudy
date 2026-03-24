import { Box, Button, Typography } from '@mui/material';
import { useEffect } from 'react';

interface QualityRatingProps {
  /** Callback invoked when user selects a quality rating (0-5) */
  onRate: (quality: number) => void;
  /** Disables all rating buttons and keyboard shortcuts */
  disabled?: boolean;
}

/**
 * SM-2 Algorithm Quality Rating Scale
 * Based on SuperMemo 2 algorithm specification
 */
const QUALITY_LEVELS = [
  { quality: 0, label: 'Blackout', description: 'Complete failure', color: '#f44336' },
  { quality: 1, label: 'Wrong', description: 'Incorrect, unfamiliar', color: '#f44336' },
  { quality: 2, label: 'Hard', description: 'Incorrect, familiar', color: '#ff9800' },
  { quality: 3, label: 'OK', description: 'Correct with difficulty', color: '#ffc107' },
  { quality: 4, label: 'Easy', description: 'Correct with hesitation', color: '#8bc34a' },
  { quality: 5, label: 'Perfect', description: 'Perfect recall', color: '#4caf50' },
] as const;

/**
 * QualityRating Component
 *
 * Displays 6 color-coded buttons (quality 0-5) for users to rate their
 * flashcard recall performance according to the SM-2 algorithm.
 *
 * Features:
 * - Color-coded buttons (red → orange → yellow → green)
 * - Keyboard shortcuts (0-5 keys)
 * - Accessible (ARIA labels, keyboard navigation)
 * - Disabled state support
 *
 * @example
 * ```tsx
 * <QualityRating
 *   onRate={(quality) => handleRating(quality)}
 *   disabled={isSubmitting}
 * />
 * ```
 */
export const QualityRating: React.FC<QualityRatingProps> = ({ onRate, disabled = false }) => {
  // Keyboard shortcuts (0-5 keys)
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      const key = event.key;
      if (key >= '0' && key <= '5' && !disabled) {
        event.preventDefault();
        onRate(parseInt(key, 10));
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [onRate, disabled]);

  return (
    <Box sx={{ mt: 3 }} role="region" aria-label="Rate your recall quality">
      <Typography variant="body2" color="text.secondary" gutterBottom id="rating-instruction">
        How well did you recall this answer?
      </Typography>

      <Box
        sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}
        role="group"
        aria-labelledby="rating-instruction"
      >
        {QUALITY_LEVELS.map(({ quality, label, description, color }) => (
          <Button
            key={quality}
            variant="contained"
            onClick={() => onRate(quality)}
            disabled={disabled}
            aria-label={`${quality}. ${label}: ${description}`}
            aria-keyshortcuts={`${quality}`}
            sx={{
              backgroundColor: color,
              '&:hover': {
                backgroundColor: color,
                filter: 'brightness(0.9)',
              },
              '&:focus-visible': {
                outline: '3px solid',
                outlineColor: 'primary.main',
                outlineOffset: '2px',
              },
              '&.Mui-disabled': {
                backgroundColor: color,
                opacity: 0.5,
              },
              minWidth: '100px',
              textTransform: 'none',
            }}
          >
            <Box>
              <Typography variant="button" sx={{ color: 'white', fontWeight: 'bold' }}>
                {quality}. {label}
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: 'white', opacity: 0.9 }}>
                {description}
              </Typography>
            </Box>
          </Button>
        ))}
      </Box>

      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
        Keyboard shortcuts: Press 0-5
      </Typography>
    </Box>
  );
};
