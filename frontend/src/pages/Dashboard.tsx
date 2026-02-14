/**
 * Dashboard Page
 * Main landing page after login with RBAC-based navigation
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
} from '@mui/material';
import { usePermissions } from '../hooks/usePermissions';
import { Permissions } from '../api/permissions';
import { PermissionGuard } from '../components/PermissionGuard';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { role, permissions, isLoading } = usePermissions();

  useEffect(() => {
    document.title = 'Dashboard - AMC Clinical Exam';
  }, []);

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Welcome Header */}
      <Paper elevation={0} sx={{ p: 3, mb: 4, bgcolor: 'primary.main', color: 'white' }}>
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

      {/* Quick Actions Grid */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Quick Actions
      </Typography>

      <Grid container spacing={3}>
        {/* MCQ Practice - Available to all with MCQ_VIEW */}
        <PermissionGuard permission={Permissions.MCQ_VIEW}>
          <Grid size={{ xs: 12, md: 6, lg: 4 }}>
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
          <Grid size={{ xs: 12, md: 6, lg: 4 }}>
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
          <Grid size={{ xs: 12, md: 6, lg: 4 }}>
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
          <Grid size={{ xs: 12, md: 6, lg: 4 }}>
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
          <Grid size={{ xs: 12, md: 6, lg: 4 }}>
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
          <Grid size={{ xs: 12, md: 6, lg: 4 }}>
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
              As a student, you can practice MCQs and OSCEs, track your progress, and view
              detailed explanations with citations from Australian medical sources.
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
