/**
 * SpecialtyBreakdown Component
 * Bar chart showing accuracy percentage by medical specialty
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
import type { SpecialtyPerformance } from '../../types/dashboard';
import { useResponsive } from '../../hooks/useResponsive';

interface SpecialtyBreakdownProps {
  specialties: SpecialtyPerformance[];
}

const SpecialtyBreakdown: React.FC<SpecialtyBreakdownProps> = ({ specialties }) => {
  const { isMobile } = useResponsive();

  // Sort by accuracy (lowest to highest) for visibility
  const sortedData = [...specialties].sort(
    (a, b) => a.accuracy_rate - b.accuracy_rate
  );

  // Format specialty names for display (capitalize and replace underscores)
  const chartData = sortedData.map((specialty) => ({
    specialty: specialty.specialty
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' '),
    accuracy: specialty.accuracy_rate,
    attempts: specialty.total_attempts,
  }));

  // Color bars based on performance (red < 60%, yellow 60-80%, green >= 80%)
  const getBarColor = (accuracy: number) => {
    if (accuracy >= 80) return '#4caf50'; // green
    if (accuracy >= 60) return '#ff9800'; // orange
    return '#f44336'; // red
  };

  const chartHeight = isMobile ? 280 : 400;

  const chartMargin = isMobile
    ? { top: 5, right: 5, left: -10, bottom: 80 }
    : { top: 5, right: 30, left: 20, bottom: 100 };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Performance by Specialty
        </Typography>
        <Box sx={{ width: '100%', height: chartHeight, mt: 2 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={chartMargin}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="specialty"
                angle={-45}
                textAnchor="end"
                height={100}
                interval={0}
                tick={{ fontSize: isMobile ? 9 : 12 }}
              />
              <YAxis
                label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft' }}
                domain={[0, 100]}
              />
              <Tooltip
                formatter={(value: number, name: string) => {
                  if (name === 'accuracy') {
                    return [`${value.toFixed(1)}%`, 'Accuracy'];
                  }
                  return [value, 'Attempts'];
                }}
              />
              <Bar dataKey="accuracy" name="accuracy" radius={[8, 8, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.accuracy)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SpecialtyBreakdown;
