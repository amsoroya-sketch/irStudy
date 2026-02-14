/**
 * StatCard Component
 * Displays a single statistic with title, value, and subtitle
 */

import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
}

const StatCard: React.FC<StatCardProps> = ({ title, value, subtitle, color = 'primary' }) => {
  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
      }}
    >
      <CardContent sx={{ textAlign: 'center', py: 3 }}>
        <Typography variant="overline" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h3" component="div" color={`${color}.main`} sx={{ my: 1 }}>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default StatCard;
