/**
 * FlashcardReview Component
 * PRD-P1-006 Phase 1: Flashcard Review Interface
 *
 * Displays study cards due for review with spaced repetition (SM-2 algorithm)
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - All content validated for Australian medical standards
 * - Citations reference Australian sources (eTG, Talley & O'Connor, AMH, PBS)
 * - Drug names follow Australian conventions (paracetamol NOT acetaminophen)
 */

import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Skeleton,
  Alert,
  Stack,
} from '@mui/material';
import { reviewCard } from '../../api/studyCards';
import { ReviewPerformance } from '../../types/study-cards';
import { useStudyCards } from '../../hooks/useStudyCards';

/**
 * Type guard to check if error has response property (Axios-like error)
 */
const hasErrorResponse = (
  error: unknown
): error is { response: { status: number; data: unknown } } => {
  return (
    typeof error === 'object' &&
    error !== null &&
    'response' in error &&
    typeof (error as { response?: unknown }).response === 'object'
  );
};

export const FlashcardReview: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);

  // Fetch study cards due for review
  const {
    data: cardsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useStudyCards(true);

  // Handle 401 errors - redirect to login
  useEffect(() => {
    if (isError && hasErrorResponse(error) && error.response.status === 401) {
      navigate('/login');
    }
  }, [isError, error, navigate]);

  // Review card mutation
  const reviewMutation = useMutation({
    mutationFn: ({ cardId, performance }: { cardId: string; performance: ReviewPerformance }) =>
      reviewCard(cardId, { performance }),
    onSuccess: () => {
      // Invalidate cache and refetch cards
      queryClient.invalidateQueries({ queryKey: ['studyCards', 'due'] });

      // Move to next card
      setCurrentCardIndex((prev) => prev + 1);
      setShowAnswer(false);
    },
  });

  // Handle errors
  if (isError) {
    const errorResponse = hasErrorResponse(error) ? error.response : undefined;

    // 401 Unauthorized (already handled in useEffect, but show nothing while redirecting)
    if (errorResponse?.status === 401) {
      return null;
    }

    // 403 Forbidden - show permission error
    if (errorResponse?.status === 403) {
      const errorDetail = (errorResponse.data as { detail?: string })?.detail;
      return (
        <Container maxWidth="md" sx={{ mt: 4 }}>
          <Alert severity="error">
            <Typography variant="h6">Permission Denied</Typography>
            <Typography variant="body2">
              {errorDetail || 'You do not own this session'}
            </Typography>
          </Alert>
        </Container>
      );
    }

    // Other errors - show retry option
    const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="h6">Failed to Load Cards</Typography>
          <Typography variant="body2">{errorMessage}</Typography>
        </Alert>
        <Button variant="contained" onClick={() => refetch()}>
          Retry
        </Button>
      </Container>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Skeleton
          variant="rectangular"
          width="100%"
          height={400}
          data-testid="flashcard-skeleton"
        />
      </Container>
    );
  }

  // Empty state - no cards due
  if (!cardsData || cardsData.cards.length === 0) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Box textAlign="center" py={8}>
          <Typography variant="h5" gutterBottom>
            No Cards Due for Review
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Great job! Check back tomorrow for more cards.
          </Typography>
        </Box>
      </Container>
    );
  }

  // Get current card
  const currentCard = cardsData.cards[currentCardIndex];

  // All cards reviewed
  if (!currentCard) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Box textAlign="center" py={8}>
          <Typography variant="h5" gutterBottom>
            All Cards Reviewed!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Great job! You've reviewed all cards due today.
          </Typography>
        </Box>
      </Container>
    );
  }

  // Handle review button click
  const handleReview = (performance: ReviewPerformance) => {
    reviewMutation.mutate({
      cardId: currentCard.card_id,
      performance,
    });
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      {/* Progress indicator */}
      <Typography variant="body2" color="text.secondary" align="center" mb={2}>
        Card {currentCardIndex + 1} of {cardsData.total_count}
      </Typography>

      {/* Flashcard */}
      <Card data-testid="flashcard-card" elevation={3}>
        <CardContent>
          <Stack spacing={3}>
            {/* Question */}
            <Box>
              <Typography variant="h6" color="primary" gutterBottom>
                Question
              </Typography>
              <Typography variant="body1">{currentCard.question}</Typography>
            </Box>

            {/* Answer (hidden until "Show Answer" clicked) */}
            {showAnswer && (
              <Box>
                <Typography variant="h6" color="secondary" gutterBottom>
                  Answer
                </Typography>
                <Typography variant="body1" whiteSpace="pre-line">
                  {currentCard.answer}
                </Typography>

                {/* Citations */}
                {currentCard.citations.length > 0 && (
                  <Box mt={2}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Sources:
                    </Typography>
                    {currentCard.citations.map((citation, index) => (
                      <Typography key={index} variant="caption" display="block">
                        {citation.source} (p. {citation.page}) - Confidence:{' '}
                        {(citation.confidence * 100).toFixed(0)}%
                      </Typography>
                    ))}
                  </Box>
                )}
              </Box>
            )}

            {/* Action buttons */}
            <Box>
              {!showAnswer ? (
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => setShowAnswer(true)}
                  size="large"
                >
                  Show Answer
                </Button>
              ) : (
                <Stack direction="row" spacing={1} justifyContent="center">
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => handleReview('again')}
                    disabled={reviewMutation.isPending}
                  >
                    Again
                  </Button>
                  <Button
                    variant="outlined"
                    color="warning"
                    onClick={() => handleReview('hard')}
                    disabled={reviewMutation.isPending}
                  >
                    Hard
                  </Button>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={() => handleReview('good')}
                    disabled={reviewMutation.isPending}
                  >
                    Good
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleReview('easy')}
                    disabled={reviewMutation.isPending}
                  >
                    Easy
                  </Button>
                </Stack>
              )}
            </Box>
          </Stack>
        </CardContent>
      </Card>

      {/* Metadata */}
      <Box mt={2} textAlign="center">
        <Typography variant="caption" color="text.secondary">
          {currentCard.specialty} • {currentCard.topic}
          {currentCard.subtopic && ` • ${currentCard.subtopic}`} • {currentCard.difficulty}
        </Typography>
      </Box>
    </Container>
  );
};
