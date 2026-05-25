/**
 * OverallProgressCard Component
 * PRD-MVP-002 Phase 2: Overall Progress Metrics Display
 *
 * Displays high-level overview of student's progress across all modules:
 * - Total sessions completed
 * - Completion percentage (progress bar)
 * - Average score (color-coded by performance)
 * - Total time spent studying
 * - Last activity timestamp (relative time)
 *
 * Color Coding:
 * - Red (error): Score < 60
 * - Orange (warning): 60 <= Score < 75
 * - Green (success): Score >= 75
 *
 * WCAG 2.2 AA Compliance:
 * - Semantic HTML (Card, Typography)
 * - Color contrast >= 4.5:1
 * - Keyboard navigation support
 * - Screen reader labels
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Grid,
  Skeleton,
  Alert,
} from '@mui/material';
import { useDashboardOverview } from '../../api/dashboard';

/**
 * Format minutes to hours:minutes display
 * @param minutes Total minutes
 * @returns Formatted string like "72h 30m"
 */
const formatTimeMinutes = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

/**
 * Format ISO timestamp to relative time
 * @param isoTimestamp ISO 8601 datetime string
 * @returns Relative time like "2 hours ago"
 */
const formatRelativeTime = (isoTimestamp: string | null): string => {
  if (!isoTimestamp) return 'Never';

  const now = new Date();
  const activityTime = new Date(isoTimestamp);
  const diffMs = now.getTime() - activityTime.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
};

/**
 * Get color for score display based on performance
 * @param score Average score (0-100)
 * @returns MUI color variant
 */
const getScoreColor = (score: number): 'error' | 'warning' | 'success' => {
  if (score < 60) return 'error';
  if (score < 75) return 'warning';
  return 'success';
};

/**
 * Metric Display Component
 * Reusable component for displaying a single metric
 */
interface MetricDisplayProps {
  label: string;
  value: string | number;
  color?: 'error' | 'warning' | 'success' | 'primary';
  testId?: string;
}

const MetricDisplay: React.FC<MetricDisplayProps> = ({
  label,
  value,
  color = 'primary',
  testId,
}) => (
  <Box textAlign="center">
    <Typography variant="h3" component="div" color={color} data-testid={testId}>
      {value}
    </Typography>
    <Typography variant="body2" color="text.secondary">
      {label}
    </Typography>
  </Box>
);

/**
 * Skeleton Loader for Metric
 */
const MetricSkeleton: React.FC = () => (
  <Box textAlign="center">
    <Skeleton
      variant="text"
      width={100}
      height={60}
      data-testid="skeleton-metric"
      sx={{ mx: 'auto' }}
    />
    <Skeleton
      variant="text"
      width={80}
      height={20}
      data-testid="skeleton-label"
      sx={{ mx: 'auto' }}
    />
  </Box>
);

/**
 * OverallProgressCard Component
 *
 * Fetches and displays overall progress metrics from dashboard API
 */
const OverallProgressCard: React.FC = () => {
  const { data, isLoading, error, isError } = useDashboardOverview();

  // Error State
  if (isError && error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">{error.message}</Alert>
        </CardContent>
      </Card>
    );
  }

  // Loading State
  if (isLoading || !data) {
    return (
      <Card>
        <CardContent>
          <Grid container spacing={3}>
            {[1, 2, 3, 4, 5].map((i) => (
              <Grid item xs={12} sm={6} md={2.4} key={i}>
                <MetricSkeleton />
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  }

  const { overall_progress } = data;
  const scoreColor = getScoreColor(overall_progress.avg_score);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Overall Progress
        </Typography>

        {/* Completion Progress Bar */}
        <Box mb={3}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Completion
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {overall_progress.completion_percentage}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={overall_progress.completion_percentage}
            sx={{ height: 8, borderRadius: 1 }}
          />
        </Box>

        {/* Metrics Grid */}
        <Grid container spacing={3}>
          {/* Total Sessions */}
          <Grid item xs={12} sm={6} md={3}>
            <MetricDisplay
              label="Total Sessions"
              value={overall_progress.total_sessions}
              testId="total-sessions"
            />
          </Grid>

          {/* Average Score */}
          <Grid item xs={12} sm={6} md={3}>
            <MetricDisplay
              label="Average Score"
              value={`${overall_progress.avg_score}%`}
              color={scoreColor}
              testId="avg-score"
            />
          </Grid>

          {/* Total Time */}
          <Grid item xs={12} sm={6} md={3}>
            <MetricDisplay
              label="Total Time"
              value={formatTimeMinutes(overall_progress.total_time_minutes)}
              testId="total-time"
            />
          </Grid>

          {/* Last Activity */}
          <Grid item xs={12} sm={6} md={3}>
            <MetricDisplay
              label="Last Activity"
              value={formatRelativeTime(overall_progress.last_activity)}
              testId="last-activity"
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default OverallProgressCard;
