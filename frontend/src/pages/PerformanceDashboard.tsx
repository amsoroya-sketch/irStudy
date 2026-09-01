/**
 * Performance Dashboard Page
 * Comprehensive analytics dashboard with charts, metrics, and study recommendations
 */

import React, { useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Box,
  Paper,
} from '@mui/material';
import { useDashboard, useWeeklyTrends } from '../hooks/useDashboard';
import { useResponsive } from '../hooks/useResponsive';
import StatCard from '../components/dashboard/StatCard';
import PerformanceChart from '../components/dashboard/PerformanceChart';
import SpecialtyBreakdown from '../components/dashboard/SpecialtyBreakdown';
import WeakAreasPanel from '../components/dashboard/WeakAreasPanel';
import ExamReadinessGauge from '../components/dashboard/ExamReadinessGauge';

const PerformanceDashboard: React.FC = () => {
  // Responsive hook
  const { isMobile } = useResponsive();

  // Fetch dashboard data
  const {
    data: dashboardData,
    isLoading: isDashboardLoading,
    error: dashboardError,
  } = useDashboard();

  // Fetch weekly trends (last 8 weeks on desktop, 4 weeks on mobile)
  const trendWeeks = isMobile ? 4 : 8;
  const {
    data: trendsData,
    isLoading: isTrendsLoading,
    error: trendsError,
  } = useWeeklyTrends(trendWeeks);

  useEffect(() => {
    document.title = 'Performance Dashboard - AMC Clinical Exam';
  }, []);

  // Loading state
  if (isDashboardLoading || isTrendsLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress aria-label="Loading dashboard data" />
        </Box>
      </Container>
    );
  }

  // Error state
  if (dashboardError || trendsError) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          <Typography variant="body1">
            Failed to load dashboard data. Please try again later.
          </Typography>
          {dashboardError && (
            <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
              Error: {dashboardError instanceof Error ? dashboardError.message : 'Unknown error'}
            </Typography>
          )}
        </Alert>
      </Container>
    );
  }

  // No data state
  if (!dashboardData || !trendsData) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="info">
          <Typography variant="body1">No dashboard data available.</Typography>
        </Alert>
      </Container>
    );
  }

  // Extract data with safe defaults
  const weakAreas = dashboardData.weak_areas ?? [];
  const specialtyBreakdown = dashboardData.specialty_breakdown ?? [];
  const trends = trendsData.trends ?? [];

  // Build exam readiness factors from dashboard data
  const examReadinessFactors = {
    mcqAccuracyRate: dashboardData.mcq_accuracy_rate,
    osceCompletions: dashboardData.total_osce_completions,
    studyCardRetentionRate: dashboardData.study_card_retention_rate,
    weakAreaCount: weakAreas.length,
    studyStreakDays: 0, // Future: add from backend
  };

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3, md: 4 } }}>
      {/* Page Header */}
      <Paper
        elevation={0}
        sx={{ p: { xs: 2, sm: 3 }, mb: { xs: 2, sm: 3, md: 4 }, bgcolor: 'primary.main', color: 'white' }}
        role="banner"
      >
        <Typography variant="h4" gutterBottom sx={{ fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' } }}>
          Performance Dashboard
        </Typography>
        <Typography variant="body1" sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}>
          Track your progress, identify areas for improvement, and achieve your AMC Clinical Exam goals.
        </Typography>
      </Paper>

      {/* Stat Cards */}
      <Grid container spacing={{ xs: 2, sm: 3 }} sx={{ mb: { xs: 2, sm: 3, md: 4 } }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="MCQ Attempts"
            value={dashboardData.total_mcq_attempts}
            subtitle={`${dashboardData.mcq_accuracy_rate.toFixed(1)}% accuracy`}
            color="primary"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="OSCE Completions"
            value={dashboardData.total_osce_completions}
            subtitle="Clinical scenarios practiced"
            color="secondary"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Study Cards"
            value={dashboardData.study_cards_reviewed}
            subtitle={`${dashboardData.study_card_retention_rate.toFixed(1)}% retention`}
            color="success"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Weak Areas"
            value={weakAreas.length}
            subtitle="Specialties needing focus"
            color={weakAreas.length > 0 ? 'warning' : 'success'}
          />
        </Grid>
      </Grid>

      {/* Exam Readiness Gauge + Weak Areas */}
      <Grid container spacing={{ xs: 2, sm: 3 }} sx={{ mb: { xs: 2, sm: 3, md: 4 } }}>
        <Grid size={{ xs: 12, md: 5 }}>
          <ExamReadinessGauge factors={examReadinessFactors} />
        </Grid>
        <Grid size={{ xs: 12, md: 7 }}>
          <WeakAreasPanel weakAreas={weakAreas} />
        </Grid>
      </Grid>

      {/* Weekly Trends Chart */}
      <Grid container spacing={{ xs: 2, sm: 3 }} sx={{ mb: { xs: 2, sm: 3, md: 4 } }}>
        <Grid size={{ xs: 12 }}>
          {trends.length > 0 ? (
            <PerformanceChart trends={trends} />
          ) : (
            <Alert severity="info">
              <Typography variant="body2">
                No trend data available yet. Start practising MCQs to see your progress over time.
              </Typography>
            </Alert>
          )}
        </Grid>
      </Grid>

      {/* Specialty Breakdown */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12 }}>
          {specialtyBreakdown.length > 0 ? (
            <SpecialtyBreakdown specialties={specialtyBreakdown} />
          ) : (
            <Alert severity="info">
              <Typography variant="body2">
                No specialty data available yet. Start practising MCQs across different specialties
                to see your performance breakdown.
              </Typography>
            </Alert>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default PerformanceDashboard;
