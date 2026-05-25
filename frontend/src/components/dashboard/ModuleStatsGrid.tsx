/**
 * ModuleStatsGrid Component
 * PRD-MVP-002 Phase 3: Module Statistics Grid Display
 *
 * Displays a 2x2 grid of module statistics cards:
 * - MCQ Practice (blue theme)
 * - OSCE (green theme)
 * - EMR Practice (purple theme)
 * - Mock Exam (orange theme)
 *
 * Each card shows:
 * - Module name and icon
 * - Attempts/sessions count
 * - Average score
 * - Last activity timestamp
 * - Clickable to navigate to respective module page
 *
 * WCAG 2.2 AA Compliance:
 * - Clickable cards with keyboard support (CardActionArea)
 * - Color-coded by module with adequate contrast
 * - ARIA labels for screen readers
 * - Responsive grid layout (mobile-first)
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Box,
  Grid,
} from '@mui/material';
import {
  Quiz as QuizIcon,
  MedicalServices as OSCEIcon,
  HealthAndSafety as EMRIcon,
  Assessment as MockExamIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useDashboardOverview } from '../../api/dashboard';
import type { ModuleStats } from '../../types/dashboard';

/**
 * Format relative time from ISO timestamp
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
 * Module Card Configuration
 */
interface ModuleConfig {
  key: 'mcq' | 'osce' | 'emr' | 'mock_exam';
  name: string;
  icon: React.ReactElement;
  color: string;
  route: string;
  countLabel: string;
}

const moduleConfigs: ModuleConfig[] = [
  {
    key: 'mcq',
    name: 'MCQ Practice',
    icon: <QuizIcon fontSize="large" />,
    color: '#1976d2', // Blue
    route: '/mcqs',
    countLabel: 'Attempts',
  },
  {
    key: 'osce',
    name: 'OSCE',
    icon: <OSCEIcon fontSize="large" />,
    color: '#2e7d32', // Green
    route: '/osces',
    countLabel: 'Attempts',
  },
  {
    key: 'emr',
    name: 'EMR Practice',
    icon: <EMRIcon fontSize="large" />,
    color: '#7b1fa2', // Purple
    route: '/emr',
    countLabel: 'Sessions',
  },
  {
    key: 'mock_exam',
    name: 'Mock Exam',
    icon: <MockExamIcon fontSize="large" />,
    color: '#ed6c02', // Orange
    route: '/mock-exam',
    countLabel: 'Exams',
  },
];

/**
 * Get count value from module stats
 */
const getModuleCount = (module: ModuleStats, key: string): number => {
  if (key === 'mcq' || key === 'osce') {
    return module.total_attempts || 0;
  }
  if (key === 'emr') {
    return module.total_sessions || 0;
  }
  if (key === 'mock_exam') {
    return module.total_exams || 0;
  }
  return 0;
};

/**
 * Module Stats Card Component
 */
interface ModuleCardProps {
  config: ModuleConfig;
  stats: ModuleStats;
  onClick: () => void;
}

const ModuleCard: React.FC<ModuleCardProps> = ({ config, stats, onClick }) => {
  const count = getModuleCount(stats, config.key);
  const hasActivity = count > 0;

  return (
    <Card>
      <CardActionArea onClick={onClick} role="button">
        <CardContent>
          {/* Module Icon and Name */}
          <Box display="flex" alignItems="center" mb={2}>
            <Box
              sx={{
                color: config.color,
                mr: 1.5,
                display: 'flex',
                alignItems: 'center',
              }}
            >
              {config.icon}
            </Box>
            <Typography variant="h6" component="h3">
              {config.name}
            </Typography>
          </Box>

          {/* Module Stats */}
          <Box>
            {/* Count */}
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body2" color="text.secondary">
                {config.countLabel}
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {count}
              </Typography>
            </Box>

            {/* Average Score */}
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body2" color="text.secondary">
                Avg Score
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {stats.average_score}%
              </Typography>
            </Box>

            {/* Last Activity */}
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Last Activity
              </Typography>
              <Typography variant="body2">
                {formatRelativeTime(stats.last_activity)}
              </Typography>
            </Box>

            {/* Empty State Message */}
            {!hasActivity && (
              <Box mt={2}>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  fontStyle="italic"
                >
                  No activity yet - Get started!
                </Typography>
              </Box>
            )}
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

/**
 * ModuleStatsGrid Component
 *
 * Displays 2x2 grid of module statistics cards
 */
const ModuleStatsGrid: React.FC = () => {
  const navigate = useNavigate();
  const { data, isLoading } = useDashboardOverview();

  // Loading state
  if (isLoading || !data) {
    return null; // Could add skeleton loaders here
  }

  const { modules } = data;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Module Progress
      </Typography>

      <Grid container spacing={3}>
        {moduleConfigs.map((config) => (
          <Grid item xs={12} sm={6} md={6} key={config.key}>
            <ModuleCard
              config={config}
              stats={modules[config.key]}
              onClick={() => navigate(config.route)}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ModuleStatsGrid;
