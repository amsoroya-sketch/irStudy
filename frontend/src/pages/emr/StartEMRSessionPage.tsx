/**
 * Start EMR Session Page
 *
 * Entry point for starting a new EMR documentation practice session.
 *
 * Features:
 * - Starts new session with random patient
 * - Redirects to system selector
 * - Loading state
 * - Error handling
 */

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { PlayArrow as StartIcon } from '@mui/icons-material';
import { useMutation } from '@tanstack/react-query';
import axiosInstance from '../../utils/axiosInstance';

const StartEMRSessionPage: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    document.title = 'Start EMR Session - irStudy';
  }, []);

  // Start session mutation
  const startSessionMutation = useMutation({
    mutationFn: async () => {
      const response = await axiosInstance.post('/emr/sessions/start', {});
      return response.data;
    },
    onSuccess: (data) => {
      const sessionId = data.session_id;
      // Check if user has preference
      const savedPreference = localStorage.getItem('emr_system_preference');
      if (savedPreference === 'epic' || savedPreference === 'cerner') {
        // Go directly to preferred system
        navigate(`/emr/${savedPreference}/${sessionId}`);
      } else {
        // Go to system selector
        navigate(`/emr/select/${sessionId}`);
      }
    },
  });

  const handleStartSession = () => {
    startSessionMutation.mutate();
  };

  return (
    <Container maxWidth="md" sx={{ py: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h3" gutterBottom align="center">
          EMR Documentation Practice
        </Typography>

        <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
          Practice your clinical documentation skills with realistic patient cases.
          You'll be assigned a random patient and can document using either Epic or Cerner EMR systems.
        </Typography>

        <Box sx={{ textAlign: 'center', mb: 4 }}>
          {startSessionMutation.isError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              Failed to start session: {(startSessionMutation.error as Error).message}
            </Alert>
          )}

          {startSessionMutation.isPending ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
              <CircularProgress size={60} />
              <Typography variant="body2" color="text.secondary">
                Starting your EMR session...
              </Typography>
            </Box>
          ) : (
            <Button
              variant="contained"
              size="large"
              startIcon={<StartIcon />}
              onClick={handleStartSession}
              sx={{ px: 6, py: 2, fontSize: '1.1rem' }}
            >
              Start New EMR Session
            </Button>
          )}
        </Box>

        <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            What to Expect:
          </Typography>
          <Typography variant="body2" component="div" sx={{ pl: 2 }}>
            <ul>
              <li>You'll be assigned a random patient with a realistic medical case</li>
              <li>Choose between Epic (light theme) or Cerner (dark theme) EMR systems</li>
              <li>Document the patient encounter using SOAP format</li>
              <li>Prescribe medications (Australian PBS)</li>
              <li>Order pathology and imaging (MBS)</li>
              <li>Your work auto-saves every 5 seconds</li>
              <li>Submit for AI validation when complete (AMC rubric scoring)</li>
            </ul>
          </Typography>
        </Paper>

        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Button variant="text" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default StartEMRSessionPage;
