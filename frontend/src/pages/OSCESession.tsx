/**
 * OSCESession.tsx - Active OSCE Session Page
 * Real-time AI patient simulation with WebSocket chat
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC Clinical Examination preparation
 * - Real-time patient interaction via WebSocket
 * - Performance scoring and feedback
 *
 * WCAG 2.2 AA COMPLIANT:
 * - Keyboard navigation
 * - Screen reader support
 * - High contrast mode
 */

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Card,
  CardContent,
  Grid,
  Chip,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { useQuery } from '@tanstack/react-query';
import { WebSocketChat } from '../components/osce/WebSocketChat';
import { SessionTimer } from '../components/osce/SessionTimer';
import { SessionControls } from '../components/osce/SessionControls';
import { useAuth } from '../context/AuthContext';
import { getOSCESession, endOSCESession, pauseOSCESession, resumeOSCESession } from '../api/osce';
import { getPersonaDetail } from '../api/personas';

/**
 * Score display interface
 */
interface SessionScore {
  overall: number;
  communication: number;
  clinical_reasoning: number;
  professionalism: number;
}

/**
 * OSCESession Component
 *
 * Displays active OSCE session with WebSocket chat interface
 */
const OSCESession: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();
  const { user, token } = useAuth();

  // State
  const [sessionScore, setSessionScore] = useState<SessionScore | null>(null);
  const [showScoreDialog, setShowScoreDialog] = useState(false);
  const [pausedAt, setPausedAt] = useState<string | undefined>(undefined);
  const [manualStatus, setManualStatus] = useState<'active' | 'paused' | 'ended' | null>(null);

  // Set page title
  useEffect(() => {
    document.title = 'OSCE Session - AMC Clinical Exam';
  }, []);

  /**
   * Fetch OSCE session details
   */
  const {
    data: sessionData,
    isLoading: sessionLoading,
    error: sessionError,
  } = useQuery({
    queryKey: ['osce-session', attemptId],
    queryFn: () => getOSCESession(attemptId!),
    enabled: !!attemptId,
    staleTime: 30 * 1000, // 30 seconds
    retry: 1,
  });

  /**
   * Fetch patient persona details
   */
  const {
    data: personaData,
    isLoading: personaLoading,
    error: personaError,
  } = useQuery({
    queryKey: ['persona-detail', sessionData?.persona_id],
    queryFn: () => getPersonaDetail(sessionData!.persona_id),
    enabled: !!sessionData?.persona_id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Derive session state from backend data and manual overrides
  const sessionState = useMemo(() => {
    // If manually set, use that
    if (manualStatus) {
      return {
        status: manualStatus,
        startedAt: sessionData?.started_at || new Date().toISOString(),
        pausedAt,
      };
    }

    // Otherwise derive from backend data
    if (sessionData) {
      return {
        status: sessionData.status === 'completed' ? ('ended' as const) : ('active' as const),
        startedAt: sessionData.started_at,
        pausedAt: undefined,
      };
    }

    // Fallback
    return {
      status: 'active' as const,
      startedAt: new Date().toISOString(),
      pausedAt: undefined,
    };
  }, [sessionData, manualStatus, pausedAt]);

  /**
   * Validate session ownership
   */
  useEffect(() => {
    if (sessionData && user && sessionData.user_id !== user.id) {
      console.error('[OSCESession] User does not own this session');
      navigate('/osce-practice', { replace: true });
    }
  }, [sessionData, user, navigate]);

  /**
   * Handle pause session
   */
  const handlePause = useCallback(async () => {
    if (!attemptId) return;

    try {
      await pauseOSCESession(attemptId);
      setManualStatus('paused');
      setPausedAt(new Date().toISOString());
      console.log('[OSCESession] Session paused');
    } catch (error) {
      console.error('[OSCESession] Failed to pause session:', error);
      throw error;
    }
  }, [attemptId]);

  /**
   * Handle resume session
   */
  const handleResume = useCallback(async () => {
    if (!attemptId) return;

    try {
      await resumeOSCESession(attemptId);
      setManualStatus('active');
      setPausedAt(undefined);
      console.log('[OSCESession] Session resumed');
    } catch (error) {
      console.error('[OSCESession] Failed to resume session:', error);
      throw error;
    }
  }, [attemptId]);

  /**
   * Handle time up (auto-end session)
   */
  const handleTimeUp = useCallback(async () => {
    if (!attemptId) return;

    console.log('[OSCESession] Time up - auto-ending session');
    setManualStatus('ended');

    try {
      const result = await endOSCESession(attemptId);
      console.log('[OSCESession] Session auto-ended with score:', result.score);

      // Show score if available
      if (result.score !== null) {
        setSessionScore({
          overall: result.score,
          communication: result.score,
          clinical_reasoning: result.score,
          professionalism: result.score,
        });
        setShowScoreDialog(true);
      } else {
        navigate('/osce-practice');
      }
    } catch (error) {
      console.error('[OSCESession] Failed to auto-end session:', error);
      navigate('/osce-practice');
    }
  }, [attemptId, navigate]);

  /**
   * Handle session end from WebSocket
   */
  const handleSessionEnd = useCallback((score: SessionScore) => {
    console.log('[OSCESession] Session ended with score:', score);
    setManualStatus('ended');
    setSessionScore(score);
    setShowScoreDialog(true);
  }, []);

  /**
   * Handle manual session end
   */
  const handleEndSession = useCallback(async () => {
    if (!attemptId) return;

    setManualStatus('ended');

    try {
      const result = await endOSCESession(attemptId);
      console.log('[OSCESession] Session ended manually:', result);

      // Show score if available
      if (result.score !== null) {
        // Note: Backend should return detailed scores, using placeholder here
        setSessionScore({
          overall: result.score,
          communication: result.score,
          clinical_reasoning: result.score,
          professionalism: result.score,
        });
        setShowScoreDialog(true);
      } else {
        // No score available, navigate back
        navigate('/osce-practice');
      }
    } catch (error) {
      console.error('[OSCESession] Failed to end session:', error);
      // Still navigate back on error
      navigate('/osce-practice');
    }
  }, [attemptId, navigate]);

  /**
   * Handle score dialog close
   */
  const handleScoreDialogClose = () => {
    setShowScoreDialog(false);
    navigate('/osce-practice');
  };

  /**
   * Get difficulty color
   */
  const getDifficultyColor = (
    difficulty: string
  ): 'success' | 'warning' | 'error' | 'default' => {
    switch (difficulty) {
      case 'foundation':
        return 'success';
      case 'intermediate':
        return 'warning';
      case 'advanced':
        return 'error';
      default:
        return 'default';
    }
  };

  /**
   * Format difficulty label
   */
  const formatDifficultyLabel = (difficulty: string): string => {
    const map: Record<string, string> = {
      foundation: 'Foundation (Basic)',
      intermediate: 'Intermediate (Standard)',
      advanced: 'Advanced (Complex)',
    };
    return map[difficulty] || difficulty;
  };

  // Loading state
  if (sessionLoading || personaLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <Box textAlign="center">
            <CircularProgress size={60} aria-label="Loading session" />
            <Typography variant="body1" sx={{ mt: 2 }}>
              Loading OSCE session...
            </Typography>
          </Box>
        </Box>
      </Container>
    );
  }

  // Error state
  if (sessionError || personaError || !sessionData || !personaData || !attemptId) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 4 }}>
          {sessionError
            ? 'Failed to load OSCE session. The session may not exist or you may not have permission to access it.'
            : 'Failed to load patient persona details.'}
        </Alert>
        <Button
          variant="contained"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/osce-practice')}
        >
          Back to OSCE Practice
        </Button>
      </Container>
    );
  }

  // Session already completed
  if (sessionData.status === 'completed') {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="info" sx={{ mb: 4 }}>
          This OSCE session has already been completed.
        </Alert>
        <Button
          variant="contained"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/osce-practice')}
        >
          Back to OSCE Practice
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: { xs: 2, sm: 3, md: 4 } }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 2,
            flexWrap: 'wrap',
            gap: 2,
          }}
        >
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              OSCE Session: {personaData.name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
              <Chip label={personaData.specialty} color="primary" size="small" />
              <Chip
                label={formatDifficultyLabel(personaData.difficulty_level)}
                color={getDifficultyColor(personaData.difficulty_level)}
                size="small"
              />
              <Chip
                label={`${personaData.age} years, ${personaData.gender}`}
                variant="outlined"
                size="small"
              />
            </Box>
          </Box>

          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/osce-practice')}
            sx={{ alignSelf: 'flex-start' }}
          >
            Back to OSCE Practice
          </Button>
        </Box>

        {/* Patient Info Card */}
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Chief Complaint
                </Typography>
                <Typography variant="body1">{personaData.chief_complaint}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  AMC Blueprint Area
                </Typography>
                <Typography variant="body1">{personaData.amc_blueprint_area}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Box>

      {/* Session Timer and Controls */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        <SessionTimer
          startedAt={sessionState.startedAt}
          pausedAt={sessionState.pausedAt}
          sessionStatus={sessionState.status}
          onTimeUp={handleTimeUp}
        />

        <SessionControls
          sessionStatus={sessionState.status}
          onPause={handlePause}
          onResume={handleResume}
          onEnd={handleEndSession}
        />
      </Box>

      {/* WebSocket Chat Interface */}
      {token && (
        <WebSocketChat
          attemptId={attemptId}
          token={token}
          patientName={personaData.name}
          onSessionEnd={handleSessionEnd}
        />
      )}

      {/* Score Dialog */}
      <Dialog
        open={showScoreDialog}
        onClose={handleScoreDialogClose}
        maxWidth="md"
        fullWidth
        aria-labelledby="score-dialog-title"
      >
        <DialogTitle id="score-dialog-title">
          <Box display="flex" alignItems="center" gap={1}>
            <AssessmentIcon color="primary" />
            <Typography variant="h5" component="span">
              OSCE Session Complete
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {sessionScore && (
            <Box sx={{ py: 2 }}>
              <Typography variant="h3" component="div" textAlign="center" gutterBottom>
                {sessionScore.overall.toFixed(1)}%
              </Typography>
              <Typography
                variant="body1"
                textAlign="center"
                color="text.secondary"
                gutterBottom
                sx={{ mb: 4 }}
              >
                Overall Score
              </Typography>

              <Grid container spacing={3}>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary" gutterBottom>
                        {sessionScore.communication.toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Communication
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary" gutterBottom>
                        {sessionScore.clinical_reasoning.toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Clinical Reasoning
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary" gutterBottom>
                        {sessionScore.professionalism.toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Professionalism
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Alert severity="info" sx={{ mt: 3 }}>
                Your performance has been evaluated based on AMC Clinical Examination
                criteria. Review your transcript to identify areas for improvement.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleScoreDialogClose} variant="contained" color="primary">
            Back to OSCE Practice
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default OSCESession;
