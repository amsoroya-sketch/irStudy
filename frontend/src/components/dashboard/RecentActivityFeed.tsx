/**
 * RecentActivityFeed Component
 * PRD-MVP-002 Phase 5: Recent Activity Timeline
 *
 * Displays timeline/list of last 10 activities across all modules:
 * - MCQ, OSCE, EMR, Mock Exam activities
 * - Sorted by timestamp (most recent first)
 * - Max 10 items displayed
 * - Each item shows: module icon, description, score, timestamp
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  Quiz as QuizIcon,
  MedicalServices as OSCEIcon,
  HealthAndSafety as EMRIcon,
  Assessment as MockExamIcon,
} from '@mui/icons-material';
import { useDashboardOverview } from '../../api/dashboard';
import type { RecentActivity } from '../../types/dashboard';

/**
 * Get icon for activity type
 */
const getActivityIcon = (type: string) => {
  switch (type) {
    case 'mcq':
      return <QuizIcon color="primary" />;
    case 'osce':
      return <OSCEIcon color="success" />;
    case 'emr':
      return <EMRIcon color="secondary" />;
    case 'mock_exam':
      return <MockExamIcon color="warning" />;
    default:
      return <QuizIcon />;
  }
};

/**
 * Format relative time
 */
const formatRelativeTime = (isoTimestamp: string): string => {
  const now = new Date();
  const activityTime = new Date(isoTimestamp);
  const diffMs = now.getTime() - activityTime.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
};

/**
 * Activity List Item Component
 */
interface ActivityItemProps {
  activity: RecentActivity;
}

const ActivityItem: React.FC<ActivityItemProps> = ({ activity }) => (
  <ListItem>
    <ListItemIcon>{getActivityIcon(activity.type)}</ListItemIcon>
    <ListItemText
      primary={activity.description}
      secondary={formatRelativeTime(activity.timestamp)}
    />
    {activity.score !== null && (
      <Chip label={`${activity.score}%`} size="small" color="default" />
    )}
  </ListItem>
);

/**
 * RecentActivityFeed Component
 */
const RecentActivityFeed: React.FC = () => {
  const { data, isLoading } = useDashboardOverview();

  if (isLoading || !data) {
    return null;
  }

  const { recent_activity } = data;

  // Empty state
  if (!recent_activity || recent_activity.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activity
          </Typography>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
            <Typography variant="body2" color="text.secondary">
              No recent activity. Start practicing to see your progress here.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Sort by timestamp (most recent first) and take max 10
  const sortedActivities = [...recent_activity]
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 10);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>
        <List>
          {sortedActivities.map((activity, index) => (
            <ActivityItem key={index} activity={activity} />
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default RecentActivityFeed;
