/**
 * MockExamStart.tsx - Mock Exam Introduction Page
 * Material-UI page for starting AMC Clinical Examination mock exam
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC OSCE format: 16 stations, 8 minutes each
 * - 8 specialties (Cardiology, Respiratory, Psychiatry, etc.)
 * - Pass threshold: 198/240 (82.5%)
 *
 * WCAG 2.2 AA COMPLIANT:
 * - Keyboard navigation
 * - Screen reader support
 * - Clear focus indicators
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  CircularProgress,
} from '@mui/material';
import {
  Timer as TimerIcon,
  Assignment as AssignmentIcon,
  BarChart as ChartIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useMutation } from '@tanstack/react-query';
import { createMockExam } from '../../api/mockExams';

/**
 * Mock Exam Start Page Component
 */
export const MockExamStart: React.FC = () => {
  const navigate = useNavigate();
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);

  // Create exam mutation
  const createExamMutation = useMutation({
    mutationFn: () =>
      createMockExam({
        exam_name: `Mock Exam - ${new Date().toLocaleDateString('en-AU', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })}`,
      }),
    onSuccess: (data) => {
      // Navigate to first station
      navigate(`/osce/mock-exam/${data.exam_id}/station/1`);
    },
    onError: (error: Error) => {
      console.error('Failed to create mock exam:', error);
    },
  });

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography
        variant="h3"
        component="h1"
        gutterBottom
        sx={{ fontWeight: 600 }}
      >
        AMC Clinical Examination Mock Exam
      </Typography>

      <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 3 }}>
        <Typography variant="body2">
          This mock exam simulates the full AMC OSCE with 16 stations (8 minutes
          each). Once started, the exam cannot be paused or interrupted. Ensure
          you have approximately 2 hours 30 minutes available.
        </Typography>
      </Alert>

      {/* Exam Format Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
            Exam Format
          </Typography>

          <List>
            <ListItem>
              <ListItemIcon>
                <AssignmentIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="16 Stations"
                secondary="8 specialties, 2 stations per specialty (Cardiology, Respiratory, Psychiatry, Neurology, Gastroenterology, Endocrinology, Rheumatology, Haematology)"
              />
            </ListItem>

            <ListItem>
              <ListItemIcon>
                <TimerIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="150 Minutes Total"
                secondary="8 minutes per station + 5-second breaks between stations"
              />
            </ListItem>

            <ListItem>
              <ListItemIcon>
                <ChartIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="AMC Pass Threshold: 198/240 (82.5%)"
                secondary="Comprehensive results with specialty breakdowns and detailed feedback"
              />
            </ListItem>

            <ListItem>
              <ListItemIcon>
                <WarningIcon color="warning" />
              </ListItemIcon>
              <ListItemText
                primary="Balanced Difficulty"
                secondary="50% intermediate, 50% advanced scenarios reflecting real AMC exam distribution"
              />
            </ListItem>
          </List>

          <Box sx={{ mt: 3 }}>
            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={() => setConfirmDialogOpen(true)}
              disabled={createExamMutation.isPending}
              startIcon={
                createExamMutation.isPending ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  <AssignmentIcon />
                )
              }
              aria-label="Start mock exam"
            >
              {createExamMutation.isPending
                ? 'Preparing Exam...'
                : 'Start Mock Exam'}
            </Button>

            {createExamMutation.isError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Failed to create mock exam. Please try again or contact support
                  if the issue persists.
                </Typography>
              </Alert>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Tips Card */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Preparation Tips
          </Typography>

          <List dense>
            <ListItem>
              <ListItemText primary="• Find a quiet environment free from distractions" />
            </ListItem>
            <ListItem>
              <ListItemText primary="• Ensure stable internet connection" />
            </ListItem>
            <ListItem>
              <ListItemText primary="• Have pen and paper ready for notes" />
            </ListItem>
            <ListItem>
              <ListItemText primary="• Treat this as a real exam - full focus and professionalism" />
            </ListItem>
            <ListItem>
              <ListItemText primary="• Use headphones for better audio quality" />
            </ListItem>
          </List>
        </CardContent>
      </Card>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-description"
      >
        <DialogTitle id="confirm-dialog-title">Ready to Begin?</DialogTitle>
        <DialogContent>
          <Typography id="confirm-dialog-description">
            This will start a 16-station mock exam (approximately 2 hours 30
            minutes). The exam cannot be paused once started. Are you in a quiet
            environment and ready to proceed?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setConfirmDialogOpen(false)}
            disabled={createExamMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              setConfirmDialogOpen(false);
              createExamMutation.mutate();
            }}
            disabled={createExamMutation.isPending}
            autoFocus
            aria-label="Confirm and start exam"
          >
            {createExamMutation.isPending ? 'Starting...' : 'Start Now'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default MockExamStart;
