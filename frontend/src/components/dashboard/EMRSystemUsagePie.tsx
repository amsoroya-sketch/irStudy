/**
 * EMR System Usage Pie Chart Component
 *
 * Displays pie chart showing usage distribution between Epic and Cerner systems.
 *
 * Features:
 * - Pie chart visualization (MUI X Charts)
 * - Shows Epic vs Cerner usage percentage
 * - Responsive design
 * - Loading and error states
 * - WCAG 2.2 AA accessible
 */

import React from 'react';
import { Card, CardContent, Typography, Skeleton, Alert, Box } from '@mui/material';
import { PieChart } from '@mui/x-charts/PieChart';
import { SystemUsageMetric } from '../../types/emr';

interface EMRSystemUsagePieProps {
  systemUsage?: SystemUsageMetric[];
  isLoading: boolean;
  error?: Error | null;
}

export const EMRSystemUsagePie: React.FC<EMRSystemUsagePieProps> = ({
  systemUsage,
  isLoading,
  error,
}) => {
  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">Failed to load system usage: {error.message}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            EMR System Preference
          </Typography>
          <Skeleton variant="circular" width={200} height={200} sx={{ mx: 'auto' }} />
        </CardContent>
      </Card>
    );
  }

  if (!systemUsage || systemUsage.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            EMR System Preference
          </Typography>
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No system usage data available yet. Complete EMR sessions to see your preference.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const epicData = systemUsage.find((usage) => usage.emr_system === 'epic');
  const cernerData = systemUsage.find((usage) => usage.emr_system === 'cerner');

  const epicPercentage = epicData ? epicData.percentage.toFixed(1) : '0';
  const cernerPercentage = cernerData ? cernerData.percentage.toFixed(1) : '0';

  const pieData = [
    {
      id: 'epic',
      value: epicData?.session_count || 0,
      label: `Epic (${epicPercentage}%)`,
      color: '#D4C5A9',
    },
    {
      id: 'cerner',
      value: cernerData?.session_count || 0,
      label: `Cerner (${cernerPercentage}%)`,
      color: '#0066CC',
    },
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          EMR System Preference
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
          Distribution of sessions across Epic and Cerner systems
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <PieChart
            series={[
              {
                data: pieData,
                highlightScope: { faded: 'global', highlighted: 'item' },
                faded: { innerRadius: 30, additionalRadius: -10, color: 'gray' },
              },
            ]}
            height={250}
            width={400}
            slotProps={{
              legend: {
                direction: 'column',
                position: { vertical: 'middle', horizontal: 'right' },
                padding: 0,
              },
            }}
          />
        </Box>
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-around' }}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="primary">
              {epicData?.session_count || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Epic Sessions
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="primary">
              {cernerData?.session_count || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Cerner Sessions
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default EMRSystemUsagePie;
