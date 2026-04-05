/**
 * Recent EMR Sessions List Component
 *
 * Displays last 5 EMR practice sessions with Resume/Review actions.
 *
 * Features:
 * - Material-UI Table with session data
 * - System badges (Epic/Cerner)
 * - Status chips (in progress, submitted, validated)
 * - Action buttons (Resume for in-progress, Review for completed)
 * - Responsive table
 * - WCAG 2.2 AA accessible
 */

import React from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Box,
  Skeleton,
  Alert,
} from '@mui/material';
import {
  PlayArrow as ResumeIcon,
  Visibility as ReviewIcon,
} from '@mui/icons-material';
import { RecentEMRSession } from '../../types/emr';
import { useNavigate } from 'react-router-dom';

interface RecentEMRSessionsListProps {
  sessions?: RecentEMRSession[];
  isLoading: boolean;
  error?: Error | null;
}

export const RecentEMRSessionsList: React.FC<RecentEMRSessionsListProps> = ({
  sessions,
  isLoading,
  error,
}) => {
  const navigate = useNavigate();

  const handleResumeSession = (sessionId: string) => {
    navigate(`/emr/sessions/${sessionId}`);
  };

  const handleReviewSession = (sessionId: string) => {
    navigate(`/emr/sessions/${sessionId}/review`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_progress':
        return 'warning';
      case 'submitted':
        return 'info';
      case 'validated':
        return 'success';
      default:
        return 'default';
    }
  };

  const getSystemColor = (system: string) => {
    return system === 'epic' ? 'primary' : 'secondary';
  };

  const formatDate = (isoDate: string) => {
    return new Date(isoDate).toLocaleDateString('en-AU', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        Failed to load recent sessions: {error.message}
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent EMR Sessions
        </Typography>
        <Box display="flex" flexDirection="column" gap={2}>
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} variant="rectangular" height={60} />
          ))}
        </Box>
      </Paper>
    );
  }

  if (!sessions || sessions.length === 0) {
    return (
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent EMR Sessions
        </Typography>
        <Alert severity="info">No recent EMR sessions found. Start a new session!</Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Recent EMR Sessions
      </Typography>

      <TableContainer>
        <Table aria-label="Recent EMR sessions">
          <TableHead>
            <TableRow>
              <TableCell>Patient</TableCell>
              <TableCell>Specialty</TableCell>
              <TableCell>System</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Score</TableCell>
              <TableCell>Date</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sessions.map((session) => (
              <TableRow key={session.id} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight={600}>
                    {session.patient_name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{session.specialty}</Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={session.emr_system.toUpperCase()}
                    size="small"
                    color={getSystemColor(session.emr_system)}
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={session.status.replace('_', ' ').toUpperCase()}
                    size="small"
                    color={getStatusColor(session.status)}
                  />
                </TableCell>
                <TableCell>
                  {session.score !== undefined ? (
                    <Typography variant="body2" fontWeight={600}>
                      {session.score.toFixed(1)}/10
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      N/A
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(session.started_at)}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  {session.status === 'in_progress' ? (
                    <Button
                      size="small"
                      startIcon={<ResumeIcon />}
                      onClick={() => handleResumeSession(session.id)}
                      aria-label={`Resume session for ${session.patient_name}`}
                    >
                      Resume
                    </Button>
                  ) : (
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<ReviewIcon />}
                      onClick={() => handleReviewSession(session.id)}
                      aria-label={`Review session for ${session.patient_name}`}
                    >
                      Review
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};
