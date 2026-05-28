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
  LinearProgress,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AssessmentIcon from '@mui/icons-material/Assessment';
import DescriptionIcon from '@mui/icons-material/Description';
import { useQuery } from '@tanstack/react-query';
import { WebSocketChat } from '../components/osce/WebSocketChat';
import { SessionTimer } from '../components/osce/SessionTimer';
import { SessionControls } from '../components/osce/SessionControls';
import { OSCEToEMRModal } from '../components/integration/OSCEToEMRModal';
import { useAuth } from '../context/AuthContext';
import { getOSCESession, endOSCESession, pauseOSCESession, resumeOSCESession, getOSCEScore, OSCEExaminerScore } from '../api/osce';
import { getPersonaDetail } from '../api/personas';

/**
 * Score display interface (matches backend AMC rubric)
 */
interface SessionScore {
  total_score: number;
  max_score: number;
  pass_fail: 'PASS' | 'FAIL';
  breakdown: {
    communication: { score: number; max: number; feedback: string };
    clinical_reasoning: { score: number; max: number; feedback: string };
    information_gathering: { score: number; max: number; feedback: string };
    management: { score: number; max: number; feedback: string };
    professionalism: { score: number; max: number; feedback: string };
  };
  strengths: string[];
  areas_for_improvement: string[];
  overall_feedback: string;
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
  const [showConversionModal, setShowConversionModal] = useState(false);
  const [pausedAt, setPausedAt] = useState<string | undefined>(undefined);
  const [manualStatus, setManualStatus] = useState<'active' | 'paused' | 'ended' | null>(null);
  const [isScoring, setIsScoring] = useState(false);

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
   * Poll for AI Examiner score after session ends (fallback if WebSocket disconnects)
   */
  useEffect(() => {
    if (manualStatus !== 'ended' || !attemptId || showScoreDialog) return;

    let intervalId: NodeJS.Timeout;
    let pollAttempts = 0;
    const maxPollAttempts = 30; // 30 × 5s = 2.5 minutes max

    const pollScore = async () => {
      try {
        const scoreData = await getOSCEScore(attemptId);
        console.log('[OSCESession] Score received via polling:', scoreData);
        setIsScoring(false);
        setSessionScore({
          total_score: scoreData.total_score,
          max_score: 15,
          pass_fail: scoreData.pass_fail,
          breakdown: {
            communication: { score: scoreData.scores.communication, max: 3, feedback: '' },
            clinical_reasoning: { score: scoreData.scores.clinical_reasoning, max: 4, feedback: '' },
            information_gathering: { score: scoreData.scores.information_gathering, max: 4, feedback: '' },
            management: { score: scoreData.scores.management, max: 2, feedback: '' },
            professionalism: { score: scoreData.scores.professionalism, max: 2, feedback: '' },
          },
          strengths: scoreData.strengths || [],
          areas_for_improvement: scoreData.areas_for_improvement || [],
          overall_feedback: scoreData.ai_examiner_feedback || '',
        });
        setShowScoreDialog(true);
        clearInterval(intervalId);
      } catch (err: any) {
        if (err.response?.status === 404) {
          // Score not ready yet, keep polling
          pollAttempts++;
          if (pollAttempts >= maxPollAttempts) {
            console.error('[OSCESession] Score polling timed out');
            setIsScoring(false);
            clearInterval(intervalId);
          }
        } else {
          console.error('[OSCESession] Score polling error:', err);
          setIsScoring(false);
          clearInterval(intervalId);
        }
      }
    };

    // Poll immediately, then every 5 seconds
    pollScore();
    intervalId = setInterval(pollScore, 5000);

    return () => clearInterval(intervalId);
  }, [manualStatus, attemptId, showScoreDialog]);

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
    setIsScoring(true);

    try {
      await endOSCESession(attemptId);
      console.log('[OSCESession] Session ended, waiting for AI scoring...');
      // Don't navigate away — scoring happens in background
      // Polling effect below will catch the score
    } catch (error) {
      console.error('[OSCESession] Failed to auto-end session:', error);
    }
  }, [attemptId]);

  /**
   * Handle session end from WebSocket (scoring_complete)
   */
  const handleSessionEnd = useCallback((score: SessionScore) => {
    console.log('[OSCESession] Scoring complete:', score);
    setManualStatus('ended');
    setIsScoring(false);
    setSessionScore(score);
    setShowScoreDialog(true);
  }, []);

  /**
   * Handle manual session end
   */
  const handleEndSession = useCallback(async () => {
    if (!attemptId) return;

    setManualStatus('ended');
    setIsScoring(true);

    try {
      await endOSCESession(attemptId);
      console.log('[OSCESession] Session ended manually, waiting for AI scoring...');
      // Don't navigate away — polling effect below will catch the score
    } catch (error) {
      console.error('[OSCESession] Failed to end session:', error);
      setIsScoring(false);
    }
  }, [attemptId]);

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

      {/* Scoring in progress overlay */}
      {isScoring && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" gap={2}>
            <CircularProgress size={20} />
            <Typography>
              AI Examiner is analyzing your session... This may take 10-30 seconds.
            </Typography>
          </Box>
        </Alert>
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
              {/* Overall Score & Pass/Fail */}
              <Box textAlign="center" sx={{ mb: 3 }}>
                <Typography variant="h2" component="div" gutterBottom>
                  {sessionScore.total_score}/{sessionScore.max_score}
                </Typography>
                <Chip
                  label={sessionScore.pass_fail}
                  color={sessionScore.pass_fail === 'PASS' ? 'success' : 'error'}
                  size="medium"
                  sx={{ fontSize: '1.1rem', fontWeight: 700, px: 2, py: 0.5 }}
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {sessionScore.pass_fail === 'PASS'
                    ? 'Congratulations! You met the AMC passing standard (≥9/15).'
                    : 'You did not meet the AMC passing standard (≥9/15). Keep practicing!'}
                </Typography>
              </Box>

              {/* AMC Rubric Breakdown */}
              <Typography variant="h6" gutterBottom>
                AMC Rubric Breakdown
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary" gutterBottom>
                        {sessionScore.breakdown.communication.score}/{sessionScore.breakdown.communication.max}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Communication
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary" gutterBottom>
                        {sessionScore.breakdown.clinical_reasoning.score}/{sessionScore.breakdown.clinical_reasoning.max}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Clinical Reasoning
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary" gutterBottom>
                        {sessionScore.breakdown.information_gathering.score}/{sessionScore.breakdown.information_gathering.max}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Information Gathering
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 6 }}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary" gutterBottom>
                        {sessionScore.breakdown.management.score}/{sessionScore.breakdown.management.max}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Management
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid size={{ xs: 12, sm: 12, md: 6 }}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary" gutterBottom>
                        {sessionScore.breakdown.professionalism.score}/{sessionScore.breakdown.professionalism.max}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Professionalism
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* AI Examiner Feedback */}
              {sessionScore.overall_feedback && (
                <>
                  <Typography variant="h6" gutterBottom>
                    AI Examiner Feedback
                  </Typography>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    {sessionScore.overall_feedback}
                  </Alert>
                </>
              )}

              {/* Strengths */}
              {sessionScore.strengths.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                    Strengths
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                    {sessionScore.strengths.map((s, i) => (
                      <Chip key={i} label={s} color="success" size="small" />
                    ))}
                  </Box>
                </>
              )}

              {/* Areas for Improvement */}
              {sessionScore.areas_for_improvement.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Areas for Improvement
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                    {sessionScore.areas_for_improvement.map((a, i) => (
                      <Chip key={i} label={a} color="warning" size="small" />
                    ))}
                  </Box>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ flexDirection: 'column', alignItems: 'stretch', gap: 2, p: 3 }}>
          {/* Convert to EMR Button */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Button
              variant="contained"
              color="primary"
              onClick={() => setShowConversionModal(true)}
              startIcon={<DescriptionIcon />}
              fullWidth
              aria-label="Convert OSCE to EMR practice session"
            >
              Convert to EMR Practice
            </Button>
            <Typography variant="caption" color="text.secondary" textAlign="center">
              Transform this conversation into a pre-filled SOAP note for documentation practice
            </Typography>
          </Box>

          {/* Back Button */}
          <Button onClick={handleScoreDialogClose} variant="outlined" color="primary" fullWidth>
            Back to OSCE Practice
          </Button>
        </DialogActions>
      </Dialog>

      {/* OSCE-to-EMR Conversion Modal */}
      {attemptId && (
        <OSCEToEMRModal
          open={showConversionModal}
          onClose={() => setShowConversionModal(false)}
          osceAttemptId={attemptId}
        />
      )}
    </Container>
  );
};

export default OSCESession;
