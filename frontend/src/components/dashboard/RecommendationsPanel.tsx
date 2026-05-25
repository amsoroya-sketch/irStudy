/**
 * RecommendationsPanel Component
 * PRD-MVP-002 Phase 6: Personalized Recommendations Panel
 *
 * Displays personalized recommendations for improvement:
 * - Priority color-coding (high: red, medium: orange, low: blue)
 * - Each recommendation shows: module, specialty, reason, priority
 * - 3-5 actionable recommendations
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import { useDashboardOverview } from '../../api/dashboard';
import type { Recommendation } from '../../types/dashboard';

/**
 * Get color for priority badge
 */
const getPriorityColor = (
  priority: string
): 'error' | 'warning' | 'info' => {
  switch (priority) {
    case 'high':
      return 'error'; // Red
    case 'medium':
      return 'warning'; // Orange
    case 'low':
      return 'info'; // Blue
    default:
      return 'info';
  }
};

/**
 * Recommendation List Item Component
 */
interface RecommendationItemProps {
  recommendation: Recommendation;
}

const RecommendationItem: React.FC<RecommendationItemProps> = ({
  recommendation,
}) => (
  <ListItem>
    <ListItemText
      primary={
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant="body1" component="span">
            <strong>{recommendation.module}</strong> - {recommendation.specialty}
          </Typography>
          <Chip
            label={recommendation.priority.toUpperCase()}
            color={getPriorityColor(recommendation.priority)}
            size="small"
          />
        </Box>
      }
      secondary={recommendation.reason}
    />
  </ListItem>
);

/**
 * RecommendationsPanel Component
 */
const RecommendationsPanel: React.FC = () => {
  const { data, isLoading } = useDashboardOverview();

  if (isLoading || !data) {
    return null;
  }

  const { recommendations } = data;

  // Empty state
  if (!recommendations || recommendations.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            minHeight={150}
          >
            <Typography variant="body2" color="text.secondary">
              No recommendations at this time. Keep up the great work!
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recommendations
        </Typography>
        <List>
          {recommendations.map((recommendation, index) => (
            <RecommendationItem key={index} recommendation={recommendation} />
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default RecommendationsPanel;
