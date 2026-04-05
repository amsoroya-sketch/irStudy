/**
 * Dashboard Page
 * Main landing page after login with RBAC-based navigation and EMR metrics
 */

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Paper,
  Divider,
} from '@mui/material';
import { usePermissions } from '../hooks/usePermissions';
import { Permissions } from '../api/permissions';
import { PermissionGuard } from '../components/PermissionGuard';
import { useAuth } from '../context/AuthContext';
import { useEMRDashboardData } from '../hooks/useEMRDashboardData';
import { EMRMetricsGrid } from '../components/dashboard/EMRMetricsGrid';
import { RecentEMRSessionsList } from '../components/dashboard/RecentEMRSessionsList';
import { EMRSpecialtyChart } from '../components/dashboard/EMRSpecialtyChart';
import { EMRSystemUsagePie } from '../components/dashboard/EMRSystemUsagePie';
import { EMRDashboardMetrics, RecentEMRSession } from '../types/emr';
import { getConversionStats } from '../api/integration';
import { useQuery } from '@tanstack/react-query';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { role, permissions, isLoading } = usePermissions();
  const { user } = useAuth();

  // Fetch EMR dashboard data (parallel queries)
  const { data: emrData, isLoading: emrLoading, isError: emrError } = useEMRDashboardData(
    user?.id || ''
  );

  // Fetch OSCE-to-EMR conversion statistics
  const { data: conversionStats } = useQuery({
    queryKey: ['conversion-stats'],
    queryFn: getConversionStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!user?.id,
  });

  useEffect(() => {
    document.title = 'Dashboard - AMC Clinical Exam';
  }, []);

  // Transform EMRMetrics to EMRDashboardMetrics
  const dashboardMetrics: EMRDashboardMetrics | undefined = emrData.metrics ? {
    total_sessions: emrData.metrics.total_sessions,
    sessions_this_week: emrData.metrics.completed_sessions, // Approximation
    average_score: emrData.metrics.avg_validation_score,
    average_typing_wpm: emrData.metrics.avg_typing_wpm,
    improvement_percentage: emrData.metrics.improvement_percentage,
    ahpra_compliance_rate: emrData.metrics.ahpra_compliance_rate,
    total_time_spent_minutes: Math.round(emrData.metrics.total_time_spent_seconds / 60),
    specialty_breakdown: emrData.metrics.specialty_stats.map(stat => ({
      specialty: stat.specialty,
      session_count: stat.session_count,
      average_score: stat.avg_score,
    })),
    system_usage: [
      {
        emr_system: 'epic' as const,
        session_count: emrData.metrics.epic_sessions,
        percentage: emrData.metrics.total_sessions > 0 ? (emrData.metrics.epic_sessions / emrData.metrics.total_sessions) * 100 : 0,
      },
      {
        emr_system: 'cerner' as const,
        session_count: emrData.metrics.cerner_sessions,
        percentage: emrData.metrics.total_sessions > 0 ? (emrData.metrics.cerner_sessions / emrData.metrics.total_sessions) * 100 : 0,
      },
    ],
  } : undefined;

  // Transform RecentSession[] to RecentEMRSession[]
  const recentEMRSessions: RecentEMRSession[] | undefined = emrData.recentSessions?.map(session => ({
    id: session.session_id,
    patient_name: session.patient_name,
    specialty: session.specialty,
    emr_system: session.emr_system,
    started_at: session.started_at,
    completed_at: session.completed_at,
    validation_score: session.validation_score,
    status: session.is_active ? ('in_progress' as const) : ('submitted' as const),
  }));

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3, md: 4 } }}>
      {/* Welcome Header */}
      <Paper elevation={0} sx={{ p: { xs: 2, sm: 3 }, mb: { xs: 2, sm: 3, md: 4 }, bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="h4" gutterBottom>
          Welcome to AMC Clinical Exam Simulation
        </Typography>
        <Typography variant="body1">
          Role: <strong>{role?.toUpperCase()}</strong>
        </Typography>
        <Typography variant="caption">
          Permissions: {permissions.length} active permissions
        </Typography>
      </Paper>

      {/* EMR Practice Section - NEW */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
          EMR Documentation Practice
        </Typography>

        <Card sx={{ mb: 3, bgcolor: 'info.light', border: '2px solid', borderColor: 'info.main' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Practice Clinical Documentation
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Develop your electronic medical record skills with Epic and Cerner systems.
              Practice SOAP notes, prescriptions, and pathology orders with real-time validation.
            </Typography>
          </CardContent>
          <CardActions>
            <Button
              size="large"
              variant="contained"
              color="primary"
              onClick={() => navigate('/emr/start')}
            >
              Start EMR Session
            </Button>
            <Button
              size="small"
              color="primary"
              onClick={() => navigate('/performance')}
            >
              View EMR Progress
            </Button>
          </CardActions>
        </Card>

        {/* EMR Metrics Grid */}
        <EMRMetricsGrid
          metrics={dashboardMetrics}
          isLoading={emrLoading}
          error={emrError ? new Error('Failed to load EMR metrics') : null}
        />

        {/* OSCE-to-EMR Conversion Stats */}
        {conversionStats && conversionStats.total_conversions > 0 && (
          <Card sx={{ mt: 3, bgcolor: 'success.light', border: '2px solid', borderColor: 'success.main' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                OSCE-to-EMR Conversions
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <Typography variant="h3" color="success.dark">
                    {conversionStats.total_conversions}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Conversions
                  </Typography>
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <Typography variant="h3" color="success.dark">
                    {Math.round(conversionStats.average_pre_fill_percentage * 100)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Average Pre-fill
                  </Typography>
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Last conversion:{' '}
                    {conversionStats.last_conversion_at
                      ? new Date(conversionStats.last_conversion_at).toLocaleDateString()
                      : 'Never'}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Recent EMR Sessions List */}
        <Box sx={{ mt: 3 }}>
          <RecentEMRSessionsList
            sessions={recentEMRSessions || []}
            isLoading={emrLoading}
            error={emrError ? new Error('Failed to load recent sessions') : null}
          />
        </Box>

        {/* EMR Specialty Chart */}
        <Box sx={{ mt: 3 }}>
          <EMRSpecialtyChart
            specialtyStats={dashboardMetrics?.specialty_breakdown || []}
            isLoading={emrLoading}
            error={emrError ? new Error('Failed to load specialty data') : null}
          />
        </Box>

        {/* EMR System Usage Pie Chart */}
        <Box sx={{ mt: 3 }}>
          <EMRSystemUsagePie
            systemUsage={dashboardMetrics?.system_usage || []}
            isLoading={emrLoading}
            error={emrError ? new Error('Failed to load system usage') : null}
          />
        </Box>
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* Mock Exam Section - NEW */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
          AMC Mock Examination
        </Typography>

        <Card sx={{ mb: 3, bgcolor: 'warning.light', border: '2px solid', borderColor: 'warning.main' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              16-Station Full Mock Exam
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Simulate the complete AMC Clinical Examination with 16 stations (8 minutes each).
              Test your skills across all specialties and receive comprehensive performance feedback.
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              <strong>Format:</strong> 16 stations | 8 minutes per station | 5-second breaks
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Pass Threshold:</strong> 198/240 (82.5%)
            </Typography>
          </CardContent>
          <CardActions>
            <Button
              size="large"
              variant="contained"
              color="warning"
              onClick={() => navigate('/osce/mock-exam/start')}
            >
              Start Mock Exam
            </Button>
            <Button
              size="small"
              color="warning"
              onClick={() => navigate('/performance')}
            >
              View Past Results
            </Button>
          </CardActions>
        </Card>
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* Quick Actions Grid */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Quick Actions
      </Typography>

      <Grid container spacing={{ xs: 2, sm: 3 }}>
        {/* MCQ Practice - Available to all with MCQ_VIEW */}
        <PermissionGuard permission={Permissions.MCQ_VIEW}>
          <Grid size={{ xs: 12, sm: 6, md: 6, lg: 4 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  MCQ Practice
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Browse and attempt multiple-choice questions across various medical specialties.
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary" onClick={() => navigate('/mcqs')}>
                  Browse MCQs
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </PermissionGuard>

        {/* OSCE Practice - Available to all with OSCE_VIEW */}
        <PermissionGuard permission={Permissions.OSCE_VIEW}>
          <Grid size={{ xs: 12, sm: 6, md: 6, lg: 4 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  OSCE Scenarios
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Practice clinical scenarios with structured checklists and feedback.
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary" onClick={() => navigate('/osces')}>
                  Browse OSCEs
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </PermissionGuard>

        {/* Progress Tracking - Available to all with PROGRESS_VIEW_OWN */}
        <PermissionGuard permission={Permissions.PROGRESS_VIEW_OWN}>
          <Grid size={{ xs: 12, sm: 6, md: 6, lg: 4 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  My Progress
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Track your performance, view analytics, and identify areas for improvement.
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary" onClick={() => navigate('/progress')}>
                  View Progress
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </PermissionGuard>

        {/* Create Content - Educators and Admins only */}
        <PermissionGuard anyOf={[Permissions.MCQ_CREATE, Permissions.OSCE_CREATE]}>
          <Grid size={{ xs: 12, sm: 6, md: 6, lg: 4 }}>
            <Card sx={{ border: '2px solid', borderColor: 'primary.main' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Create Content
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Create new MCQs and OSCE scenarios for students to practice.
                </Typography>
              </CardContent>
              <CardActions>
                <PermissionGuard permission={Permissions.MCQ_CREATE}>
                  <Button size="small" color="primary" onClick={() => navigate('/mcqs/create')}>
                    New MCQ
                  </Button>
                </PermissionGuard>
                <PermissionGuard permission={Permissions.OSCE_CREATE}>
                  <Button size="small" color="primary" onClick={() => navigate('/osces/create')}>
                    New OSCE
                  </Button>
                </PermissionGuard>
              </CardActions>
            </Card>
          </Grid>
        </PermissionGuard>

        {/* Admin Panel - Admins only */}
        <PermissionGuard permission={Permissions.ADMIN_PANEL}>
          <Grid size={{ xs: 12, sm: 6, md: 6, lg: 4 }}>
            <Card sx={{ border: '2px solid', borderColor: 'error.main' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom color="error">
                  Admin Panel
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage users, permissions, and system configuration.
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="error" onClick={() => navigate('/admin')}>
                  Admin Settings
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </PermissionGuard>

        {/* View All Progress - Educators and Admins */}
        <PermissionGuard permission={Permissions.PROGRESS_VIEW_ALL}>
          <Grid size={{ xs: 12, sm: 6, md: 6, lg: 4 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Student Progress
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Monitor student performance and provide feedback.
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  color="primary"
                  onClick={() => navigate('/progress/all')}
                >
                  View All Students
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </PermissionGuard>
      </Grid>

      {/* Role-Specific Information */}
      <Box sx={{ mt: 4 }}>
        <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            Your Role: {role?.toUpperCase()}
          </Typography>
          {role === 'student' && (
            <Typography variant="body2">
              As a student, you can practice MCQs, OSCEs, and EMR documentation. Track your progress
              and view detailed explanations with citations from Australian medical sources.
            </Typography>
          )}
          {role === 'educator' && (
            <Typography variant="body2">
              As an educator, you can create and manage MCQs/OSCEs, monitor student progress,
              and provide graded feedback on student attempts.
            </Typography>
          )}
          {role === 'admin' && (
            <Typography variant="body2">
              As an admin, you have full system access including user management, content
              management, and system configuration.
            </Typography>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default Dashboard;
