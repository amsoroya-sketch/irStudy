/**
 * MockExamStation.tsx - Individual Mock Exam Station Page
 * Material-UI page for conducting single OSCE station in mock exam context
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - 8-minute station with countdown timer
 * - 5-second break between stations
 * - Auto-advance to next station or results
 *
 * WCAG 2.2 AA COMPLIANT:
 * - Keyboard navigation
 * - Screen reader announcements
 * - Clear focus indicators
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  LinearProgress,
  Chip,
  Alert,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  AccessTime as TimerIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMockExamStatus, completeStation } from '../../api/mockExams';
import { createOSCESession } from '../../api/osce';

/**
 * Simple countdown timer component for mock exam
 */
const StationCountdownTimer: React.FC<{
  duration: number;
  onTimeUp: () => void;
}> = ({ duration, onTimeUp }) => {
  const [timeRemaining, setTimeRemaining] = useState(duration);

  useEffect(() => {
    if (timeRemaining <= 0) {
      onTimeUp();
      return;
    }

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeRemaining, onTimeUp]);

  const minutes = Math.floor(timeRemaining / 60);
  const seconds = timeRemaining % 60;
  const isWarning = timeRemaining <= 60;

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        p: 2,
        bgcolor: isWarning ? 'warning.light' : 'background.paper',
        borderRadius: 1,
        border: 1,
        borderColor: isWarning ? 'warning.main' : 'divider',
      }}
      role="timer"
      aria-live="polite"
      aria-atomic="true"
    >
      <TimerIcon color={isWarning ? 'warning' : 'primary'} />
      <Typography
        variant="h4"
        sx={{
          fontFamily: 'monospace',
          fontWeight: 700,
          color: isWarning ? 'warning.dark' : 'text.primary',
        }}
      >
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {isWarning ? 'Last minute!' : 'Remaining'}
      </Typography>
    </Box>
  );
};

/**
 * Break screen component (5 seconds between stations)
 */
const StationBreakScreen: React.FC<{
  stationNumber: number;
  score: number;
  countdown: number;
}> = ({ stationNumber, score, countdown }) => {
  return (
    <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
      <CheckIcon color="success" sx={{ fontSize: 80, mb: 2 }} />

      <Typography variant="h4" gutterBottom>
        Station {stationNumber} Complete
      </Typography>

      <Typography variant="h6" color="text.secondary" gutterBottom>
        Score: {score}/15
      </Typography>

      <Typography variant="h2" sx={{ my: 4, fontFamily: 'monospace' }}>
        {countdown}
      </Typography>

      <Typography variant="body1" gutterBottom>
        Next station starting in {countdown} seconds...
      </Typography>

      <LinearProgress
        variant="determinate"
        value={((5 - countdown) / 5) * 100}
        sx={{ mt: 2, height: 8, borderRadius: 1 }}
      />
    </Container>
  );
};

/**
 * Mock Exam Station Page Component
 */
export const MockExamStation: React.FC = () => {
  const { examId, stationNumber } = useParams<{
    examId: string;
    stationNumber: string;
  }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [attemptId, setAttemptId] = useState<string>('');
  const [showBreak, setShowBreak] = useState(false);
  const [breakCountdown, setBreakCountdown] = useState(5);
  const [stationScore, setStationScore] = useState<number>(0);
  const [sessionStarted, setSessionStarted] = useState(false);

  // Get exam status
  const { data: examStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['mock-exam-status', examId],
    queryFn: () => getMockExamStatus(examId!),
    enabled: !!examId && !showBreak,
    refetchInterval: showBreak ? false : 10000, // Poll every 10s during station
  });

  // Get current station persona
  const currentStation = examStatus?.stations_config?.[parseInt(stationNumber!) - 1];

  // Create OSCE session for this station
  const createSessionMutation = useMutation({
    mutationFn: (personaId: string) => createOSCESession(personaId),
    onSuccess: (data) => {
      setAttemptId(data.attempt_id);
      setSessionStarted(true);
    },
  });

  // Complete station mutation
  const completeStationMutation = useMutation({
    mutationFn: (data: { score: number; passFail: 'PASS' | 'FAIL' }) =>
      completeStation(examId!, parseInt(stationNumber!), {
        attemptId,
        stationScore: data.score,
        passFail: data.passFail,
      }),
    onSuccess: (data) => {
      setStationScore(data.station_score);
      queryClient.invalidateQueries({ queryKey: ['mock-exam-status', examId] });

      if (data.next_station_number) {
        // Show 5-second break
        setShowBreak(true);
        let countdown = 5;
        const interval = setInterval(() => {
          countdown -= 1;
          setBreakCountdown(countdown);

          if (countdown <= 0) {
            clearInterval(interval);
            // Navigate to next station
            navigate(`/osce/mock-exam/${examId}/station/${data.next_station_number}`);
          }
        }, 1000);
      } else {
        // Exam complete - navigate to results
        navigate(`/osce/mock-exam/${examId}/results`);
      }
    },
  });

  // Auto-create session when component mounts
  useEffect(() => {
    if (currentStation?.persona_id && !sessionStarted && !attemptId) {
      createSessionMutation.mutate(currentStation.persona_id);
    }
  }, [currentStation?.persona_id, sessionStarted, attemptId]);

  // Handle time up - auto-finalize station
  const handleTimeUp = () => {
    if (attemptId && !completeStationMutation.isPending) {
      // Calculate score based on session (placeholder - real score comes from backend)
      const score = Math.floor(Math.random() * 6) + 10; // 10-15 for demo
      const passFail = score >= 12 ? 'PASS' : 'FAIL';
      completeStationMutation.mutate({ score, passFail });
    }
  };

  if (showBreak) {
    return (
      <StationBreakScreen
        stationNumber={parseInt(stationNumber!)}
        score={stationScore}
        countdown={breakCountdown}
      />
    );
  }

  if (statusLoading || !examStatus || !currentStation) {
    return (
      <Container sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading station...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Exam Progress Header */}
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
          <Typography variant="h5" component="h1">
            Station {stationNumber} of 16
          </Typography>

          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Chip
              label={`${examStatus.stations_completed}/16 Completed`}
              color="primary"
              size="small"
            />
            <Chip
              label={currentStation.specialty}
              color="secondary"
              size="small"
            />
          </Box>
        </Box>

        <LinearProgress
          variant="determinate"
          value={((parseInt(stationNumber!) - 1) / 16) * 100}
          sx={{ height: 8, borderRadius: 1 }}
          aria-label={`Exam progress: ${parseInt(stationNumber!) - 1} of 16 stations complete`}
        />
      </Box>

      {/* Timer */}
      <Box sx={{ mb: 2 }}>
        <StationCountdownTimer duration={480} onTimeUp={handleTimeUp} />
      </Box>

      {/* Station Content Card */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {currentStation.name}
          </Typography>

          <Typography variant="body2" color="text.secondary" gutterBottom>
            Chief Complaint: {currentStation.chief_complaint}
          </Typography>

          <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
            <Typography variant="body2">
              You have 8 minutes to complete this station. Take a focused history
              and examination as you would in a real AMC Clinical Examination.
            </Typography>
          </Alert>

          {/* Placeholder for WebSocket Chat Integration */}
          {sessionStarted && attemptId ? (
            <Box sx={{ mt: 3, p: 3, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary" align="center">
                [WebSocket Chat Integration Placeholder]
              </Typography>
              <Typography variant="caption" display="block" align="center" sx={{ mt: 1 }}>
                Attempt ID: {attemptId}
              </Typography>
              <Typography variant="caption" display="block" align="center">
                In production, the WebSocketChat component would be rendered here
              </Typography>
            </Box>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <CircularProgress />
              <Typography variant="body2" sx={{ mt: 2 }}>
                Starting session...
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default MockExamStation;
