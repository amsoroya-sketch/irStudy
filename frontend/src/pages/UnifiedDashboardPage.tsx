/**
 * UnifiedDashboardPage Component
 * PRD-MVP-002 Phase 7: Dashboard Page Integration
 *
 * Assembles all dashboard components into unified layout:
 * - OverallProgressCard (top)
 * - ModuleStatsGrid (below progress)
 * - Two-column layout:
 *   - SpecialtyBreakdownChart (left)
 *   - RecentActivityFeed (right)
 * - RecommendationsPanel (bottom)
 *
 * WCAG 2.2 AA Compliance:
 * - Semantic HTML (<main>, <section>)
 * - Proper heading hierarchy
 * - Keyboard navigation support
 * - Responsive design (mobile-first)
 */

import React from 'react';
import { Container, Typography, Box, Grid, IconButton, Tooltip } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import OverallProgressCard from '../components/dashboard/OverallProgressCard';
import ModuleStatsGrid from '../components/dashboard/ModuleStatsGrid';
import SpecialtyBreakdownChart from '../components/dashboard/SpecialtyBreakdownChart';
import RecentActivityFeed from '../components/dashboard/RecentActivityFeed';
import RecommendationsPanel from '../components/dashboard/RecommendationsPanel';
import { useDashboardOverview } from '../api/dashboard';

/**
 * UnifiedDashboardPage Component
 *
 * Main dashboard page showing comprehensive student progress
 */
const UnifiedDashboardPage: React.FC = () => {
  const { refetch, isFetching } = useDashboardOverview();

  /**
   * Handle refresh button click
   */
  const handleRefresh = () => {
    refetch();
  };

  return (
    <Container maxWidth="lg" component="main">
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4} mt={3}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Tooltip title="Refresh dashboard data">
          <IconButton
            onClick={handleRefresh}
            disabled={isFetching}
            aria-label="Refresh dashboard"
          >
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Overall Progress Card */}
      <Box mb={4}>
        <OverallProgressCard />
      </Box>

      {/* Module Stats Grid */}
      <Box mb={4}>
        <ModuleStatsGrid />
      </Box>

      {/* Two-Column Layout: Chart + Activity Feed */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={6}>
          <SpecialtyBreakdownChart />
        </Grid>
        <Grid item xs={12} md={6}>
          <RecentActivityFeed />
        </Grid>
      </Grid>

      {/* Recommendations Panel */}
      <Box mb={4}>
        <RecommendationsPanel />
      </Box>
    </Container>
  );
};

export default UnifiedDashboardPage;
