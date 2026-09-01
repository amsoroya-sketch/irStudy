/**
 * PerformanceChart Component
 * Line chart displaying weekly MCQ performance trends
 */

import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { WeeklyTrend } from '../../types/dashboard';
import { useResponsive } from '../../hooks/useResponsive';

interface PerformanceChartProps {
  trends: WeeklyTrend[];
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({ trends = [] }) => {
  const { isMobile } = useResponsive();

  // Format data for Recharts
  const chartData = trends.map((trend) => ({
    week: new Date(trend.week_start).toLocaleDateString('en-AU', {
      month: '2-digit',
      day: '2-digit',
    }),
    accuracy: trend.accuracy_rate,
    attempts: trend.mcq_attempts,
  }));

  const chartHeight = isMobile ? 200 : 300;

  const chartMargin = isMobile
    ? { top: 5, right: 5, left: -10, bottom: 5 }
    : { top: 5, right: 30, left: 20, bottom: 5 };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Weekly Performance Trends
        </Typography>
        <Box sx={{ width: '100%', height: chartHeight, mt: 2 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={chartMargin}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="week"
                label={{ value: 'Week', position: 'insideBottom', offset: -5 }}
                tick={{ fontSize: isMobile ? 10 : 12 }}
              />
              <YAxis
                yAxisId="left"
                label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft' }}
                domain={[0, 100]}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                label={{ value: 'Attempts', angle: 90, position: 'insideRight' }}
              />
              <Tooltip
                formatter={(value: number, name: string) => {
                  if (name === 'accuracy') {
                    return [`${value.toFixed(1)}%`, 'Accuracy'];
                  }
                  return [value, 'Attempts'];
                }}
              />
              {!isMobile && (
                <Legend
                  formatter={(value) => {
                    if (value === 'accuracy') return 'Accuracy (%)';
                    if (value === 'attempts') return 'MCQ Attempts';
                    return value;
                  }}
                />
              )}
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="accuracy"
                stroke="#8884d8"
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
                name="accuracy"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="attempts"
                stroke="#82ca9d"
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
                name="attempts"
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PerformanceChart;
