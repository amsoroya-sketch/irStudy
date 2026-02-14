/**
 * MCQ Practice Interface Component
 * Main component for MCQ practice with timer, images, and instant feedback
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - All MCQs use Australian drug names (paracetamol NOT acetaminophen)
 * - Citations reference Australian guidelines (eTG, AHPRA, AMH, PBS)
 * - Australian spelling throughout (anaesthetise, paediatric, oesophagus)
 *
 * ACCESSIBILITY (WCAG 2.2 AA):
 * - ARIA labels for all interactive elements
 * - Keyboard navigation support
 * - Screen reader friendly
 * - Sufficient colour contrast (≥4.5:1)
 */

import { useState } from 'react';
import { useSwipeable } from 'react-swipeable';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Stack,
  Divider,
  List,
  ListItem,
  ListItemText,
  Snackbar,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  ArrowForward as ArrowForwardIcon,
  SwipeLeft as SwipeLeftIcon,
  SwipeRight as SwipeRightIcon,
} from '@mui/icons-material';
import { useMCQ, useSubmitMCQ } from '../../hooks/useMCQ';
import { MCQTimer } from './MCQTimer';
import { ImageLightbox } from '../common/ImageLightbox';
import { CitationPanel } from '../citations/CitationPanel';
import { AnswerOption, DifficultyLevel, MedicalSpecialty } from '../../types/mcq';
import { useResponsive } from '../../hooks/useResponsive';

export interface MCQPracticeInterfaceProps {
  /** Filter by medical specialty (optional) */
  specialty?: MedicalSpecialty;
  /** Filter by difficulty level (optional) */
  difficulty?: DifficultyLevel;
  /** Total time allocated per question (default 120 seconds) */
  totalTime?: number;
}

/**
 * Get difficulty colour for chip
 */
const getDifficultyColour = (difficulty: DifficultyLevel): 'success' | 'warning' | 'error' => {
  switch (difficulty) {
    case 'easy':
      return 'success';
    case 'medium':
      return 'warning';
    case 'hard':
      return 'error';
  }
};

/**
 * Format specialty for display (convert snake_case to Title Case)
 */
const formatSpecialty = (specialty: string): string => {
  return specialty
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * MCQ Practice Interface Component
 */
export const MCQPracticeInterface: React.FC<MCQPracticeInterfaceProps> = ({
  specialty,
  difficulty,
  totalTime = 120,
}) => {
  // Responsive hooks
  const { isMobile } = useResponsive();

  // API hooks
  const { data: mcq, isLoading, error, refetch } = useMCQ(specialty, difficulty);
  const { mutate: submitAnswer, isPending: isSubmitting, data: result } = useSubmitMCQ();

  // State - initialize based on MCQ ID to trigger reset on new question
  const mcqKey = mcq?.id ?? 0;
  const [currentMcqId, setCurrentMcqId] = useState(mcqKey);
  const [selectedAnswer, setSelectedAnswer] = useState<AnswerOption | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(totalTime);
  const [startTime] = useState(() => Date.now()); // Use function initializer for Date.now()
  const [swipeHint, setSwipeHint] = useState<string | null>(null);

  // Reset state when MCQ changes (different ID)
  if (mcqKey !== currentMcqId && mcqKey !== 0) {
    setCurrentMcqId(mcqKey);
    setSelectedAnswer(null);
    setIsSubmitted(false);
    setTimeRemaining(totalTime);
  }

  // Handle answer selection
  const handleAnswerChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!isSubmitted) {
      setSelectedAnswer(event.target.value as AnswerOption);
    }
  };

  // Handle submit
  const handleSubmit = () => {
    if (!selectedAnswer || !mcq) return;

    const timeTaken = Math.floor((Date.now() - startTime) / 1000);

    submitAnswer(
      {
        mcqId: mcq.id,
        attemptData: {
          mcq_id: mcq.id,
          selected_answer: selectedAnswer,
          time_taken_seconds: Math.min(timeTaken, totalTime),
        },
      },
      {
        onSuccess: () => {
          setIsSubmitted(true);
        },
      }
    );
  };

  // Handle next question
  const handleNextQuestion = () => {
    refetch();
  };

  // Handle time update
  const handleTimeUpdate = (time: number) => {
    setTimeRemaining(time);
  };

  // Touch gesture handlers (mobile only)
  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => {
      if (isMobile && isSubmitted) {
        // Swipe left to go to next question
        handleNextQuestion();
        setSwipeHint('Swipe detected: Next question');
      } else if (isMobile && !isSubmitted) {
        setSwipeHint('Submit your answer first');
      }
    },
    onSwipedRight: () => {
      if (isMobile && !isSubmitted) {
        // Swipe right to refresh current question
        refetch();
        setSwipeHint('Swipe detected: Refreshing question');
      } else if (isMobile && isSubmitted) {
        setSwipeHint('Already submitted');
      }
    },
    trackMouse: false, // Only track touch events, not mouse
    preventScrollOnSwipe: false, // Allow vertical scrolling
    delta: 80, // Minimum swipe distance (pixels)
  });

  // Loading state
  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'centre',
          alignItems: 'centre',
          minHeight: 400,
        }}
      >
        <CircularProgress aria-label="Loading MCQ" />
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert severity="error" aria-live="polite">
        <Typography variant="body1">
          Failed to load MCQ: {error.message}
        </Typography>
        <Button onClick={() => refetch()} sx={{ mt: 2 }}>
          Try Again
        </Button>
      </Alert>
    );
  }

  // No MCQ found
  if (!mcq) {
    return (
      <Alert severity="info" aria-live="polite">
        <Typography variant="body1">
          No MCQs found matching your filters. Try different specialty or difficulty.
        </Typography>
      </Alert>
    );
  }

  const isCorrect = result?.is_correct ?? false;
  const answerOptions: AnswerOption[] = ['A', 'B', 'C', 'D', 'E'];

  return (
    <>
      <Card
        {...(isMobile ? swipeHandlers : {})}
        sx={{
          maxWidth: 900,
          margin: '0 auto',
          boxShadow: { xs: 1, md: 3 },
          position: 'relative',
        }}
        role="region"
        aria-label="MCQ practice interface"
      >
        <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
        {/* Header with metadata */}
        <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
          <Chip
            label={formatSpecialty(mcq.specialty)}
            color="primary"
            size="small"
            aria-label={`Specialty: ${formatSpecialty(mcq.specialty)}`}
          />
          <Chip
            label={mcq.difficulty.toUpperCase()}
            color={getDifficultyColour(mcq.difficulty)}
            size="small"
            aria-label={`Difficulty: ${mcq.difficulty}`}
          />
          {mcq.tags && mcq.tags.length > 0 && (
            <Chip
              label={mcq.tags[0]}
              variant="outlined"
              size="small"
              aria-label={`Topic: ${mcq.tags[0]}`}
            />
          )}
        </Stack>

        {/* Timer */}
        <Box sx={{ mb: 3 }}>
          <MCQTimer
            timeRemaining={timeRemaining}
            onTimeUpdate={handleTimeUpdate}
            isPaused={isSubmitted}
            totalTime={totalTime}
          />
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Mobile Swipe Hint */}
        {isMobile && (
          <Stack
            direction="row"
            spacing={1}
            sx={{
              mb: 2,
              p: 1,
              backgroundColor: 'info.light',
              borderRadius: 1,
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <SwipeRightIcon fontSize="small" />
            <Typography variant="caption" color="text.secondary">
              {isSubmitted ? 'Swipe left for next question' : 'Swipe right to refresh'}
            </Typography>
            <SwipeLeftIcon fontSize="small" />
          </Stack>
        )}

        {/* Question */}
        <Typography
          variant="h6"
          component="h2"
          sx={{ mb: 3, fontWeight: 500, lineHeight: 1.6, fontSize: { xs: '1rem', sm: '1.25rem' } }}
          id="mcq-question"
        >
          {mcq.question_text}
        </Typography>

        {/* Medical Images */}
        {mcq.image_url && (
          <Box sx={{ mb: 3 }}>
            <ImageLightbox
              images={[mcq.image_url]}
              altPrefix={mcq.image_caption || 'Medical image for MCQ'}
            />
            {mcq.image_caption && (
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ mt: 1, display: 'block' }}
              >
                {mcq.image_caption}
              </Typography>
            )}
          </Box>
        )}

        {/* Answer Options */}
        <FormControl component="fieldset" sx={{ width: '100%', mb: 3 }}>
          <RadioGroup
            aria-labelledby="mcq-question"
            value={selectedAnswer || ''}
            onChange={handleAnswerChange}
          >
            {answerOptions.map((option) => {
              const optionText = mcq.options[option];
              if (!optionText) return null;

              const isSelected = selectedAnswer === option;
              const isCorrectAnswer = result?.correct_answer === option;
              const showCorrect = isSubmitted && isCorrectAnswer;
              const showIncorrect = isSubmitted && isSelected && !isCorrectAnswer;

              return (
                <Card
                  key={option}
                  variant="outlined"
                  sx={{
                    mb: { xs: 1.5, sm: 1 },
                    minHeight: { xs: 44, sm: 'auto' }, // Minimum touch target
                    backgroundColor: showCorrect
                      ? 'success.light'
                      : showIncorrect
                        ? 'error.light'
                        : isSelected
                          ? 'action.selected'
                          : 'background.paper',
                    borderColor: showCorrect
                      ? 'success.main'
                      : showIncorrect
                        ? 'error.main'
                        : isSelected
                          ? 'primary.main'
                          : 'divider',
                    borderWidth: isSelected ? 2 : 1,
                  }}
                >
                  <FormControlLabel
                    value={option}
                    control={<Radio disabled={isSubmitted} />}
                    label={
                      <Stack direction="row" spacing={1} alignItems="centre" sx={{ py: 1 }}>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {option}.
                        </Typography>
                        <Typography variant="body1" sx={{ flex: 1 }}>
                          {optionText}
                        </Typography>
                        {showCorrect && (
                          <CheckCircleIcon
                            color="success"
                            aria-label="Correct answer"
                            sx={{ ml: 'auto' }}
                          />
                        )}
                        {showIncorrect && (
                          <CancelIcon
                            color="error"
                            aria-label="Incorrect answer"
                            sx={{ ml: 'auto' }}
                          />
                        )}
                      </Stack>
                    }
                    sx={{
                      width: '100%',
                      m: 0,
                      px: 2,
                      '& .MuiFormControlLabel-label': {
                        width: '100%',
                      },
                    }}
                  />
                </Card>
              );
            })}
          </RadioGroup>
        </FormControl>

        {/* Submit Button */}
        {!isSubmitted && (
          <Button
            variant="contained"
            color="primary"
            size="large"
            fullWidth
            onClick={handleSubmit}
            disabled={!selectedAnswer || isSubmitting}
            aria-label="Submit answer"
            sx={{ mb: 2 }}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Submit Answer'}
          </Button>
        )}

        {/* Explanation Panel */}
        {isSubmitted && result && (
          <Box sx={{ mt: 3 }}>
            {/* Result message */}
            <Alert
              severity={isCorrect ? 'success' : 'error'}
              sx={{ mb: 3 }}
              aria-live="polite"
            >
              <Typography variant="h6" sx={{ mb: 1 }}>
                {isCorrect ? 'Correct!' : 'Incorrect'}
              </Typography>
              <Typography variant="body2">
                {isCorrect
                  ? `Well done! You answered correctly in ${result.time_taken_seconds} seconds.`
                  : `The correct answer is ${result.correct_answer}. Review the explanation below.`}
              </Typography>
            </Alert>

            {/* Explanation */}
            <Card variant="outlined" sx={{ mb: 3, p: 2, backgroundColor: 'background.default' }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                Explanation:
              </Typography>
              <Typography variant="body2" sx={{ lineHeight: 1.8, mb: 2 }}>
                {result.explanation}
              </Typography>

              {/* Learning Points */}
              {result.learning_points && result.learning_points.length > 0 && (
                <>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                    Key Learning Points:
                  </Typography>
                  <List dense sx={{ pl: 2 }}>
                    {result.learning_points.map((point, index) => (
                      <ListItem key={index} sx={{ display: 'list-item', listStyleType: 'disc' }}>
                        <ListItemText primary={point} />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}

              {/* Australian Citations */}
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                References:
              </Typography>
              <CitationPanel
                citations={[result.citation]}
                showConfidence={true}
                allowCopy={true}
              />
            </Card>

            {/* Next Question Button */}
            <Button
              variant="contained"
              color="primary"
              size="large"
              fullWidth
              onClick={handleNextQuestion}
              endIcon={<ArrowForwardIcon />}
              aria-label="Next question"
            >
              Next Question
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>

      {/* Swipe feedback Snackbar */}
      <Snackbar
        open={!!swipeHint}
        autoHideDuration={2000}
        onClose={() => setSwipeHint(null)}
        message={swipeHint}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </>
  );
};

export default MCQPracticeInterface;
