/**
 * MCQ Attempt Page
 * Interactive MCQ practice with timer and immediate feedback
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Paper,
  Divider,
} from '@mui/material';
import { getMCQById, submitMCQAttempt } from '../api/mcqs';
import { PermissionGuard } from '../components/PermissionGuard';
import { Permissions } from '../api/permissions';

const MCQAttempt: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [showResult, setShowResult] = useState(false);
  const [attemptResult, setAttemptResult] = useState<any>(null);

  useEffect(() => {
    document.title = 'MCQ Practice - AMC Clinical Exam';
  }, []);

  // Fetch MCQ
  const {
    data: mcq,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['mcq', id],
    queryFn: () => getMCQById(Number(id)),
    enabled: !!id,
  });

  // Submit attempt mutation
  const submitMutation = useMutation({
    mutationFn: submitMCQAttempt,
    onSuccess: (data) => {
      setAttemptResult(data);
      setShowResult(true);
    },
    onError: (error: any) => {
      console.error('Failed to submit attempt:', error);
    },
  });

  useEffect(() => {
    // Reset state when component mounts
    setStartTime(Date.now());
    setSelectedAnswer('');
    setShowResult(false);
    setAttemptResult(null);
  }, [id]);

  const handleAnswerChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedAnswer(event.target.value);
  };

  const handleSubmit = () => {
    if (!selectedAnswer || !id) return;

    const timeSpentSeconds = Math.floor((Date.now() - startTime) / 1000);

    submitMutation.mutate({
      mcq_id: Number(id),
      selected_answer: selectedAnswer as 'A' | 'B' | 'C' | 'D' | 'E',
      time_taken_seconds: timeSpentSeconds,
    });
  };

  const handleTryAgain = () => {
    setSelectedAnswer('');
    setStartTime(Date.now());
    setShowResult(false);
    setAttemptResult(null);
  };

  const handleBackToBrowser = () => {
    navigate('/mcqs');
  };

  if (isLoading) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Alert severity="error">Failed to load MCQ. Please try again later.</Alert>
        <Button onClick={handleBackToBrowser} sx={{ mt: 2 }}>
          Back to Browser
        </Button>
      </Container>
    );
  }

  if (!mcq) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Alert severity="warning">MCQ not found.</Alert>
        <Button onClick={handleBackToBrowser} sx={{ mt: 2 }}>
          Back to Browser
        </Button>
      </Container>
    );
  }

  return (
    <PermissionGuard permission={Permissions.MCQ_ATTEMPT}>
      <Container maxWidth="md" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Button onClick={handleBackToBrowser} sx={{ mb: 2 }}>
            ← Back to Browser
          </Button>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h5" component="h1">
              MCQ #{mcq.id}
            </Typography>
            <Chip label={mcq.difficulty} color="primary" size="small" />
            <Chip label={mcq.specialty} variant="outlined" size="small" />
          </Box>
          {mcq.tags && mcq.tags.length > 0 && (
            <Box>
              {mcq.tags.map((tag, index) => (
                <Chip key={index} label={tag} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
              ))}
            </Box>
          )}
        </Box>

        {/* Question Card */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Question:
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 3 }}>
              {mcq.question_text}
            </Typography>

            {mcq.image_url && (
              <Box sx={{ mb: 3, textAlign: 'center' }}>
                <img
                  src={mcq.image_url}
                  alt="MCQ illustration"
                  style={{ maxWidth: '100%', height: 'auto', borderRadius: '8px' }}
                />
              </Box>
            )}

            {!showResult && (
              <FormControl component="fieldset" fullWidth>
                <RadioGroup value={selectedAnswer} onChange={handleAnswerChange}>
                  <FormControlLabel
                    value="A"
                    control={<Radio />}
                    label={`A. ${mcq.options?.A || ''}`}
                    sx={{ mb: 1, p: 1, border: '1px solid #e0e0e0', borderRadius: 1 }}
                  />
                  <FormControlLabel
                    value="B"
                    control={<Radio />}
                    label={`B. ${mcq.options?.B || ''}`}
                    sx={{ mb: 1, p: 1, border: '1px solid #e0e0e0', borderRadius: 1 }}
                  />
                  <FormControlLabel
                    value="C"
                    control={<Radio />}
                    label={`C. ${mcq.options?.C || ''}`}
                    sx={{ mb: 1, p: 1, border: '1px solid #e0e0e0', borderRadius: 1 }}
                  />
                  <FormControlLabel
                    value="D"
                    control={<Radio />}
                    label={`D. ${mcq.options?.D || ''}`}
                    sx={{ mb: 1, p: 1, border: '1px solid #e0e0e0', borderRadius: 1 }}
                  />
                  {mcq.options?.E && (
                    <FormControlLabel
                      value="E"
                      control={<Radio />}
                      label={`E. ${mcq.options.E}`}
                      sx={{ mb: 1, p: 1, border: '1px solid #e0e0e0', borderRadius: 1 }}
                    />
                  )}
                </RadioGroup>
              </FormControl>
            )}

            {showResult && attemptResult && (
              <Box sx={{ mt: 3 }}>
                <Alert
                  severity={attemptResult.is_correct ? 'success' : 'error'}
                  sx={{ mb: 2 }}
                >
                  {attemptResult.is_correct ? (
                    <Typography variant="body1">
                      <strong>Correct!</strong> Your answer ({selectedAnswer}) is correct.
                    </Typography>
                  ) : (
                    <Typography variant="body1">
                      <strong>Incorrect.</strong> Your answer: {selectedAnswer}. Correct answer:{' '}
                      {attemptResult.correct_answer}
                    </Typography>
                  )}
                </Alert>

                <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                    Explanation:
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {attemptResult.explanation}
                  </Typography>
                  {mcq.citation && (
                    <>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="caption" color="text.secondary">
                        Citation: {mcq.citation}
                      </Typography>
                    </>
                  )}
                </Paper>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Actions */}
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          {!showResult ? (
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleSubmit}
              disabled={!selectedAnswer || submitMutation.isPending}
            >
              {submitMutation.isPending ? 'Submitting...' : 'Submit Answer'}
            </Button>
          ) : (
            <>
              <Button variant="outlined" onClick={handleTryAgain}>
                Try Again
              </Button>
              <Button variant="contained" onClick={handleBackToBrowser}>
                Back to Browser
              </Button>
            </>
          )}
        </Box>
      </Container>
    </PermissionGuard>
  );
};

export default MCQAttempt;
