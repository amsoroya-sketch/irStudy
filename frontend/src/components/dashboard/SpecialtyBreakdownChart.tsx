/**
 * SpecialtyBreakdownChart Component
 * PRD-MVP-002 Phase 4: Specialty Performance Breakdown Chart
 *
 * Displays horizontal bar chart showing performance by specialty:
 * - X-axis: Average score (0-100)
 * - Y-axis: Specialty names
 * - Bars color-coded by performance level
 * - Sorted by attempts (most active specialties at top)
 *
 * Color Coding:
 * - Green (excellent): Score >= 75
 * - Orange (average): 60 <= Score < 75
 * - Red (weak): Score < 60
 *
 * Australian Medical Specialties:
 * - Cardiology, Respiratory, Psychiatry, Neurology, etc.
 * - Based on FRACP/AMC curriculum
 *
 * WCAG 2.2 AA Compliance:
 * - Chart title for screen readers
 * - Tooltip provides detailed info
 * - Adequate color contrast (tested)
 * - Keyboard navigation support
 */

import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { useDashboardOverview } from '../../api/dashboard';
import type { SpecialtyBreakdown } from '../../types/dashboard';

/**
 * Get bar color based on average score
 */
const getBarColor = (avgScore: number): string => {
  if (avgScore >= 75) return '#2e7d32'; // Green (excellent)
  if (avgScore >= 60) return '#ed6c02'; // Orange (average)
  return '#d32f2f'; // Red (weak)
};

/**
 * Get strength label from score
 */
const getStrengthLabel = (avgScore: number): string => {
  if (avgScore >= 75) return 'Excellent';
  if (avgScore >= 60) return 'Average';
  return 'Needs Improvement';
};

/**
 * Custom Tooltip Component
 */
interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: SpecialtyBreakdown & { strength_label: string };
  }>;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <Box
        sx={{
          bgcolor: 'background.paper',
          p: 1.5,
          border: 1,
          borderColor: 'divider',
          borderRadius: 1,
        }}
      >
        <Typography variant="body2" fontWeight="bold">
          {data.specialty}
        </Typography>
        <Typography variant="body2">Score: {data.avg_score}%</Typography>
        <Typography variant="body2">Attempts: {data.attempts}</Typography>
        <Typography variant="body2" color="text.secondary">
          {data.strength_label}
        </Typography>
      </Box>
    );
  }
  return null;
};

/**
 * SpecialtyBreakdownChart Component
 *
 * Displays specialty performance as horizontal bar chart
 */
const SpecialtyBreakdownChart: React.FC = () => {
  const { data, isLoading } = useDashboardOverview();

  // Loading state
  if (isLoading || !data) {
    return null; // Could add skeleton loader
  }

  const { specialty_breakdown } = data;

  // Empty state
  if (!specialty_breakdown || specialty_breakdown.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Specialty Breakdown
          </Typography>
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            minHeight={200}
          >
            <Typography variant="body2" color="text.secondary">
              No specialty data available yet. Start practicing to see your
              performance by specialty.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Sort by attempts (most active first) and prepare chart data
  const chartData = [...specialty_breakdown]
    .sort((a, b) => b.attempts - a.attempts)
    .map((item) => ({
      ...item,
      strength_label: getStrengthLabel(item.avg_score),
    }));

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Specialty Breakdown
        </Typography>

        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis
              type="category"
              dataKey="specialty"
              width={120}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="avg_score" radius={[0, 8, 8, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(entry.avg_score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        {/* Legend */}
        <Box display="flex" justifyContent="center" gap={3} mt={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <Box
              sx={{
                width: 16,
                height: 16,
                bgcolor: '#2e7d32',
                borderRadius: 0.5,
              }}
            />
            <Typography variant="caption">Excellent (≥75%)</Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <Box
              sx={{
                width: 16,
                height: 16,
                bgcolor: '#ed6c02',
                borderRadius: 0.5,
              }}
            />
            <Typography variant="caption">Average (60-74%)</Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <Box
              sx={{
                width: 16,
                height: 16,
                bgcolor: '#d32f2f',
                borderRadius: 0.5,
              }}
            />
            <Typography variant="caption">Needs Improvement (&lt;60%)</Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SpecialtyBreakdownChart;
