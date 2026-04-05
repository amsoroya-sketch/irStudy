/**
 * EMR Metrics Grid Component
 *
 * Displays 6 EMR practice metrics in StatCard grid format.
 *
 * Metrics:
 * 1. Total Sessions Completed
 * 2. Average Validation Score
 * 3. Average Typing Speed (WPM)
 * 4. Improvement % (vs previous week)
 * 5. AHPRA Compliance Rate
 * 6. Total Time Spent (hours)
 *
 * Features:
 * - Reuses existing StatCard component
 * - Responsive grid layout
 * - Loading and error states
 * - WCAG 2.2 AA accessible
 */

import React from 'react';
import { Grid, Skeleton, Alert } from '@mui/material';
import {
  Assignment as SessionsIcon,
  TrendingUp as ScoreIcon,
  Speed as SpeedIcon,
  ShowChart as ImprovementIcon,
  VerifiedUser as ComplianceIcon,
  AccessTime as TimeIcon,
} from '@mui/icons-material';
import StatCard from './StatCard';
import { EMRDashboardMetrics } from '../../types/emr';

interface EMRMetricsGridProps {
  metrics?: EMRDashboardMetrics;
  isLoading: boolean;
  error?: Error | null;
}

export const EMRMetricsGrid: React.FC<EMRMetricsGridProps> = ({
  metrics,
  isLoading,
  error,
}) => {
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        Failed to load EMR metrics: {error.message}
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {Array.from({ length: 6 }).map((_, index) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
            <Skeleton variant="rectangular" height={120} />
          </Grid>
        ))}
      </Grid>
    );
  }

  if (!metrics) {
    return null;
  }

  const statCards = [
    {
      title: 'Total Sessions',
      value: metrics.total_sessions,
      subtitle: `${metrics.sessions_this_week} this week`,
      icon: <SessionsIcon />,
      color: 'primary' as const,
    },
    {
      title: 'Average Score',
      value: `${metrics.average_score.toFixed(1)}/10`,
      subtitle: 'AMC validation score',
      icon: <ScoreIcon />,
      color: 'success' as const,
    },
    {
      title: 'Typing Speed',
      value: `${Math.round(metrics.average_typing_wpm)} WPM`,
      subtitle: 'Words per minute',
      icon: <SpeedIcon />,
      color: 'info' as const,
    },
    {
      title: 'Improvement',
      value: `${metrics.improvement_percentage > 0 ? '+' : ''}${metrics.improvement_percentage.toFixed(1)}%`,
      subtitle: 'vs previous week',
      icon: <ImprovementIcon />,
      color: metrics.improvement_percentage >= 0 ? ('success' as const) : ('error' as const),
    },
    {
      title: 'AHPRA Compliance',
      value: `${Math.round(metrics.ahpra_compliance_rate)}%`,
      subtitle: 'Documentation standards',
      icon: <ComplianceIcon />,
      color: metrics.ahpra_compliance_rate >= 80 ? ('success' as const) : ('warning' as const),
    },
    {
      title: 'Time Spent',
      value: `${(metrics.total_time_spent_minutes / 60).toFixed(1)}h`,
      subtitle: 'Total practice time',
      icon: <TimeIcon />,
      color: 'primary' as const,
    },
  ];

  return (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      {statCards.map((card, index) => (
        <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
          <StatCard
            title={card.title}
            value={card.value}
            subtitle={card.subtitle}
            color={card.color}
          />
        </Grid>
      ))}
    </Grid>
  );
};
