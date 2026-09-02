/**
 * MockExamResults.tsx - Mock Exam Results Summary Page
 * Material-UI page displaying comprehensive mock exam results
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC OSCE pass threshold: 198/240 (82.5%)
 * - Station-by-station breakdown
 * - Specialty performance analysis
 *
 * WCAG 2.2 AA COMPLIANT:
 * - Keyboard navigation
 * - Screen reader support
 * - High contrast pass/fail indicators
 */

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Box,
  Grid,
  Alert,
  Button,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  CheckCircle as PassIcon,
  Cancel as FailIcon,
  EmojiEvents as TrophyIcon,
  Home as HomeIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { getMockExamResults } from '../../api/mockExams';

/**
 * Mock Exam Results Page Component
 */
export const MockExamResults: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();

  const { data: results, isLoading, error } = useQuery({
    queryKey: ['mock-exam-results', examId],
    queryFn: () => getMockExamResults(examId!),
    enabled: !!examId,
  });

  if (isLoading) {
    return (
      <Container sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading results...
        </Typography>
      </Container>
    );
  }

  if (error || !results) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="error">
          <Typography variant="body1">
            Failed to load exam results. Please try again or contact support.
          </Typography>
        </Alert>
        <Button
          variant="contained"
          onClick={() => navigate('/dashboard')}
          sx={{ mt: 2 }}
          startIcon={<HomeIcon />}
        >
          Return to Dashboard
        </Button>
      </Container>
    );
  }

  const isPassed = results.overall_pass_fail === 'PASS';
  const percentage = results.percentage;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Overall Result Banner */}
      <Card
        sx={{
          mb: 3,
          bgcolor: isPassed ? 'success.light' : 'error.light',
          borderLeft: 6,
          borderColor: isPassed ? 'success.main' : 'error.main',
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            {isPassed ? (
              <TrophyIcon
                sx={{ fontSize: 80, color: 'success.dark' }}
                aria-hidden="true"
              />
            ) : (
              <FailIcon
                sx={{ fontSize: 80, color: 'error.dark' }}
                aria-hidden="true"
              />
            )}

            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                {isPassed ? 'Congratulations! You Passed' : 'Not Passed - Keep Practicing'}
              </Typography>

              <Typography variant="h4" sx={{ mt: 1, fontWeight: 600 }}>
                Overall Score: {results.overall_score}/240 ({percentage.toFixed(1)}%)
              </Typography>

              <Typography variant="body1" sx={{ mt: 1 }}>
                AMC Pass Threshold: 198/240 (82.5%)
                {isPassed
                  ? ` - You exceeded the threshold by ${results.overall_score - 198} points!`
                  : ` - ${198 - results.overall_score} points below threshold`}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Summary Statistics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h5" gutterBottom>
                Stations Passed
              </Typography>
              <Typography variant="h3" component="p" color="success.main" sx={{ fontWeight: 700 }}>
                {results.summary_statistics.stations_passed}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                out of 16 stations
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h5" gutterBottom>
                Stations Failed
              </Typography>
              <Typography variant="h3" component="p" color="error.main" sx={{ fontWeight: 700 }}>
                {results.summary_statistics.stations_failed}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                out of 16 stations
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h5" gutterBottom>
                Average Per Station
              </Typography>
              <Typography variant="h3" component="p" color="primary.main" sx={{ fontWeight: 700 }}>
                {results.summary_statistics.average_score_per_station.toFixed(1)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                out of 15 points
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h5" gutterBottom>
                Pass Rate
              </Typography>
              <Typography variant="h3" component="p" color="primary.main" sx={{ fontWeight: 700 }}>
                {((results.summary_statistics.stations_passed / 16) * 100).toFixed(0)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                of stations passed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Station-by-Station Breakdown */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
            Station-by-Station Breakdown
          </Typography>

          <TableContainer component={Paper} sx={{ mt: 2 }}>
            <Table aria-label="Mock exam station results">
              <TableHead>
                <TableRow sx={{ bgcolor: 'background.default' }}>
                  <TableCell sx={{ fontWeight: 600 }}>Station</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Specialty</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Patient</TableCell>
                  <TableCell align="center" sx={{ fontWeight: 600 }}>
                    Score
                  </TableCell>
                  <TableCell align="center" sx={{ fontWeight: 600 }}>
                    Result
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.stations.map((station) => (
                  <TableRow
                    key={station.station_number}
                    sx={{
                      '&:hover': { bgcolor: 'action.hover' },
                      bgcolor:
                        station.pass_fail === 'PASS'
                          ? 'success.lighter'
                          : 'error.lighter',
                    }}
                  >
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        Station {station.station_number}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={station.specialty}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{station.persona_name}</Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={`${station.score}/15`}
                        color={station.pass_fail === 'PASS' ? 'success' : 'error'}
                        size="small"
                        sx={{ fontWeight: 600 }}
                      />
                    </TableCell>
                    <TableCell align="center">
                      {station.pass_fail === 'PASS' ? (
                        <PassIcon color="success" aria-label="Passed" />
                      ) : (
                        <FailIcon color="error" aria-label="Failed" />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Performance by Specialty */}
      {results.summary_statistics.performance_by_specialty &&
        results.summary_statistics.performance_by_specialty.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                Performance by Specialty
              </Typography>

              <Grid container spacing={2} sx={{ mt: 1 }}>
                {results.summary_statistics.performance_by_specialty.map(
                  (specialty) => (
                    <Grid size={{ xs: 12, sm: 6, md: 4 }} key={specialty.specialty}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            {specialty.specialty}
                          </Typography>

                          <Divider sx={{ my: 1 }} />

                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">Score:</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {specialty.total_score}/{specialty.max_score}
                            </Typography>
                          </Box>

                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">Percentage:</Typography>
                            <Typography
                              variant="body2"
                              sx={{
                                fontWeight: 600,
                                color:
                                  specialty.percentage >= 82.5
                                    ? 'success.main'
                                    : 'error.main',
                              }}
                            >
                              {specialty.percentage.toFixed(1)}%
                            </Typography>
                          </Box>

                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2">Stations Passed:</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {specialty.stations_passed}/{specialty.total_stations}
                            </Typography>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  )
                )}
              </Grid>
            </CardContent>
          </Card>
        )}

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 4 }}>
        <Button
          variant="outlined"
          size="large"
          onClick={() => navigate('/dashboard')}
          startIcon={<HomeIcon />}
        >
          Return to Dashboard
        </Button>

        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/performance')}
          startIcon={<AssessmentIcon />}
        >
          View All Performance
        </Button>

        <Button
          variant="contained"
          color="success"
          size="large"
          onClick={() => navigate('/osce/mock-exam/start')}
          startIcon={<TrophyIcon />}
        >
          Start New Mock Exam
        </Button>
      </Box>
    </Container>
  );
};

export default MockExamResults;
