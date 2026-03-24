/**
 * FlashcardCard Component
 * PRD-P1-006 Phase 2: Individual Flashcard with 60fps Flip Animation
 *
 * PERFORMANCE TARGET: 60fps (<16.67ms per frame)
 * ANIMATION STRATEGY: CSS transforms (GPU-accelerated)
 *
 * ACCESSIBILITY: WCAG 2.2 AA compliant
 * - Keyboard navigation (spacebar to flip)
 * - ARIA labels
 * - Reduced motion support
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Box,
  styled,
} from '@mui/material';
import { StudyCard } from '../../types/study-cards';

interface FlashcardCardProps {
  card: StudyCard;
}

// Styled components for 60fps flip animation
const FlashcardContainer = styled(Box)({
  perspective: '1000px',
  width: '100%',
  height: '500px',
  position: 'relative',
});

interface FlashcardInnerProps {
  isFlipped: boolean;
}

const FlashcardInner = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'isFlipped',
})<FlashcardInnerProps>(({ isFlipped }) => ({
  position: 'relative',
  width: '100%',
  height: '100%',
  textAlign: 'center',
  transition: 'transform 0.6s cubic-bezier(0.4, 0.0, 0.2, 1)',
  transformStyle: 'preserve-3d',
  transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
  willChange: 'transform',

  // Respect reduced motion preference (WCAG 2.2 AA)
  '@media (prefers-reduced-motion: reduce)': {
    transition: 'none',
  },
}));

interface FlashcardFaceProps {
  isVisible: boolean;
}

const FlashcardFace = styled(Card, {
  shouldForwardProp: (prop) => prop !== 'isVisible',
})<FlashcardFaceProps>(({ isVisible }) => ({
  position: 'absolute',
  width: '100%',
  height: '100%',
  backfaceVisibility: 'hidden',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  overflow: 'auto',
  // Hide from DOM when not visible (for accessibility and testing)
  visibility: isVisible ? 'visible' : 'hidden',
  pointerEvents: isVisible ? 'auto' : 'none',
}));

const FlashcardFront = styled(FlashcardFace)({
  zIndex: 2,
  transform: 'rotateY(0deg)',
});

const FlashcardBack = styled(FlashcardFace)({
  transform: 'rotateY(180deg)',
});

const QuestionText = styled(Typography)({
  overflowWrap: 'break-word',
  wordBreak: 'break-word',
  padding: '2rem',
});

const AnswerText = styled(Typography)({
  overflowWrap: 'break-word',
  wordBreak: 'break-word',
  padding: '2rem',
  textAlign: 'left',
});

const CitationList = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(3),
  padding: theme.spacing(2),
  backgroundColor: theme.palette.grey[50],
  borderRadius: theme.shape.borderRadius,
  textAlign: 'left',
}));

const CitationItem = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(1.5),
  '&:last-child': {
    marginBottom: 0,
  },
}));

/**
 * Get color for confidence score
 * Green ≥80%, Yellow 65-79%, Red <65%
 */
const getConfidenceColor = (confidence: number): 'success' | 'warning' | 'error' => {
  if (confidence >= 0.8) return 'success';
  if (confidence >= 0.65) return 'warning';
  return 'error';
};

export const FlashcardCard: React.FC<FlashcardCardProps> = ({ card }) => {
  const [isFlipped, setIsFlipped] = useState(false);

  /**
   * Toggle card flip state
   */
  const handleFlip = useCallback(() => {
    setIsFlipped((prev) => !prev);
  }, []);

  /**
   * Keyboard navigation (spacebar to flip)
   * ACCESSIBILITY: Keyboard shortcuts for better UX
   */
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.code === 'Space' && event.target === document.body) {
        event.preventDefault();
        handleFlip();
      }
    };

    document.addEventListener('keydown', handleKeyPress);

    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleFlip]);

  return (
    <FlashcardContainer>
      <FlashcardInner
        isFlipped={isFlipped}
        data-testid="flashcard-card-inner"
        role="region"
        aria-label={isFlipped ? 'Flashcard answer' : 'Flashcard question'}
      >
        {/* FRONT SIDE: Question */}
        <FlashcardFront elevation={3} isVisible={!isFlipped}>
          {!isFlipped && (
            <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="overline" color="text.secondary" gutterBottom>
                  Question
                </Typography>
                <QuestionText variant="h5" component="div">
                  {card.question}
                </QuestionText>
              </Box>

              <Box sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  onClick={handleFlip}
                  aria-label="Show answer"
                  aria-pressed={isFlipped}
                  fullWidth
                  size="large"
                >
                  Show Answer
                </Button>
              </Box>
            </CardContent>
          )}
        </FlashcardFront>

        {/* BACK SIDE: Answer + Citations */}
        <FlashcardBack elevation={3} isVisible={isFlipped}>
          {isFlipped && (
            <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'auto' }}>
              <Box>
                <Typography variant="overline" color="text.secondary" gutterBottom>
                  Answer
                </Typography>
                <AnswerText variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
                  {card.answer}
                </AnswerText>

                {/* Citations Section */}
                <CitationList data-testid="citation-list">
                  <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Citations
                  </Typography>

                  {card.citations.length === 0 ? (
                    <Typography variant="body2" color="text.secondary">
                      No citations available
                    </Typography>
                  ) : (
                    card.citations.map((citation, index) => (
                      <CitationItem key={citation.qdrant_point_id || index}>
                        <Typography variant="body2" gutterBottom>
                          <strong>{citation.source}</strong>
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                          <Chip
                            label={citation.page}
                            size="small"
                            variant="outlined"
                          />
                          <Chip
                            label={`${Math.round(citation.confidence * 100)}% confidence`}
                            size="small"
                            color={getConfidenceColor(citation.confidence)}
                          />
                        </Box>
                      </CitationItem>
                    ))
                  )}
                </CitationList>
              </Box>

              <Box sx={{ mt: 3 }}>
                <Button
                  variant="outlined"
                  onClick={handleFlip}
                  aria-label="Hide answer"
                  aria-pressed={!isFlipped}
                  fullWidth
                  size="large"
                >
                  Hide Answer
                </Button>
              </Box>
            </CardContent>
          )}
        </FlashcardBack>
      </FlashcardInner>
    </FlashcardContainer>
  );
};
