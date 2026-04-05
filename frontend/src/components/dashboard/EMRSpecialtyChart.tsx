/**
 * EMR Specialty Breakdown Chart Component
 *
 * Displays bar chart showing EMR session count by medical specialty.
 *
 * Features:
 * - Bar chart visualization (MUI X Charts)
 * - Shows session count per specialty
 * - Responsive design
 * - Loading and error states
 * - WCAG 2.2 AA accessible
 */

import React from 'react';
import { Card, CardContent, Typography, Skeleton, Alert, Box } from '@mui/material';
import { BarChart } from '@mui/x-charts/BarChart';
import { SpecialtyMetric } from '../../types/emr';

interface EMRSpecialtyChartProps {
  specialtyStats?: SpecialtyMetric[];
  isLoading: boolean;
  error?: Error | null;
}

export const EMRSpecialtyChart: React.FC<EMRSpecialtyChartProps> = ({
  specialtyStats,
  isLoading,
  error,
}) => {
  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">Failed to load specialty breakdown: {error.message}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            EMR Practice by Specialty
          </Typography>
          <Skeleton variant="rectangular" height={300} />
        </CardContent>
      </Card>
    );
  }

  if (!specialtyStats || specialtyStats.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            EMR Practice by Specialty
          </Typography>
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No specialty data available yet. Complete EMR sessions to see your breakdown.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const specialties = specialtyStats.map((stat) => stat.specialty);
  const sessionCounts = specialtyStats.map((stat) => stat.session_count);
  const averageScores = specialtyStats.map((stat) => stat.average_score);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          EMR Practice by Specialty
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
          Session count and average validation score per specialty
        </Typography>
        <BarChart
          xAxis={[{ scaleType: 'band', data: specialties, label: 'Specialty' }]}
          series={[
            {
              data: sessionCounts,
              label: 'Session Count',
              color: '#1976d2',
            },
            {
              data: averageScores,
              label: 'Avg Score (/10)',
              color: '#4caf50',
            },
          ]}
          height={300}
          margin={{ top: 20, right: 20, bottom: 60, left: 60 }}
          slotProps={{
            legend: {
              direction: 'row',
              position: { vertical: 'bottom', horizontal: 'middle' },
              padding: 0,
            },
          }}
        />
      </CardContent>
    </Card>
  );
};

export default EMRSpecialtyChart;
