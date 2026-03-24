/**
 * NavigationControls Component
 * Based on PRD-P1-006 Phase 3 - Navigation Controls
 *
 * Provides Previous/Next navigation buttons for flashcard review
 * with progress indicator (Card X of Y)
 *
 * ACCESSIBILITY:
 * - WCAG 2.2 AA compliant
 * - Disabled state clearly indicated
 * - ARIA labels for screen readers
 * - Keyboard navigation support
 */

import React, { useEffect } from 'react';
import { Box, Button, Typography } from '@mui/material';
import { NavigateBefore, NavigateNext } from '@mui/icons-material';

interface NavigationControlsProps {
  currentIndex: number; // 0-indexed current card position
  totalCards: number; // Total number of cards
  onNext: () => void; // Callback for Next button
  onPrevious: () => void; // Callback for Previous button
}

export const NavigationControls: React.FC<NavigationControlsProps> = ({
  currentIndex,
  totalCards,
  onNext,
  onPrevious,
}) => {
  // Keyboard navigation: Arrow keys for Previous/Next
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft' && currentIndex > 0) {
        onPrevious();
      } else if (event.key === 'ArrowRight' && currentIndex < totalCards - 1) {
        onNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, totalCards, onNext, onPrevious]);

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        mt: 2,
        gap: 2,
      }}
    >
      <Button
        variant="outlined"
        onClick={onPrevious}
        disabled={currentIndex === 0}
        startIcon={<NavigateBefore />}
        aria-label="Previous card"
      >
        Previous
      </Button>

      <Typography variant="body1" color="text.secondary">
        Card {currentIndex + 1} of {totalCards}
      </Typography>

      <Button
        variant="outlined"
        onClick={onNext}
        disabled={currentIndex === totalCards - 1}
        endIcon={<NavigateNext />}
        aria-label="Next card"
      >
        Next
      </Button>
    </Box>
  );
};
