/**
 * AMC Rubric Visualization Component
 *
 * Displays AMC Clinical Examination rubric scores with horizontal bars.
 *
 * Categories:
 * 1. History Taking (0-10)
 * 2. Physical Examination (0-10)
 * 3. Clinical Reasoning (0-10)
 * 4. Communication (0-10)
 * 5. Documentation (0-10)
 *
 * Features:
 * - Horizontal bar charts for each category
 * - Color-coded scores (red <5, orange 5-7, green ≥7)
 * - Feedback tooltips
 * - WCAG 2.2 AA accessible
 */

import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Info as InfoIcon,
} from '@mui/icons-material';
import { AMCRubricScore } from '../../../types/emr';

interface AMCRubricVisualizationProps {
  scores: AMCRubricScore[];
}

const categoryLabels: Record<string, string> = {
  history_taking: 'History Taking',
  physical_examination: 'Physical Examination',
  clinical_reasoning: 'Clinical Reasoning',
  communication: 'Communication',
  documentation: 'Documentation',
};

const getScoreColor = (score: number): 'error' | 'warning' | 'success' => {
  if (score < 5) return 'error';
  if (score < 7) return 'warning';
  return 'success';
};

const getScorePercentage = (score: number, maxScore: number): number => {
  return (score / maxScore) * 100;
};

export const AMCRubricVisualization: React.FC<AMCRubricVisualizationProps> = ({
  scores,
}) => {
  if (!scores || scores.length === 0) {
    return null;
  }

  return (
    <Paper elevation={0} sx={{ p: 3, border: '1px solid', borderColor: 'divider' }}>
      <Typography variant="h6" gutterBottom>
        AMC Rubric Scores
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Based on Australian Medical Council Clinical Examination standards
      </Typography>

      <Box display="flex" flexDirection="column" gap={2}>
        {scores.map((rubricScore) => {
          const percentage = getScorePercentage(rubricScore.score, rubricScore.max_score);
          const color = getScoreColor(rubricScore.score);
          const label = categoryLabels[rubricScore.category] || rubricScore.category;

          return (
            <Box key={rubricScore.category}>
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="center"
                sx={{ mb: 0.5 }}
              >
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="body2" fontWeight={600}>
                    {label}
                  </Typography>
                  {rubricScore.feedback && (
                    <Tooltip title={rubricScore.feedback} arrow>
                      <InfoIcon
                        fontSize="small"
                        color="action"
                        sx={{ cursor: 'help' }}
                      />
                    </Tooltip>
                  )}
                </Box>
                <Chip
                  label={`${rubricScore.score}/${rubricScore.max_score}`}
                  size="small"
                  color={color}
                  aria-label={`${label} score: ${rubricScore.score} out of ${rubricScore.max_score}`}
                />
              </Box>

              <Box
                sx={{
                  position: 'relative',
                  height: 32,
                  backgroundColor: 'action.hover',
                  borderRadius: 1,
                  overflow: 'hidden',
                }}
                role="progressbar"
                aria-valuenow={rubricScore.score}
                aria-valuemin={0}
                aria-valuemax={rubricScore.max_score}
                aria-label={`${label} score progress bar`}
              >
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    height: '100%',
                    width: `${percentage}%`,
                    backgroundColor: `${color}.main`,
                    transition: 'width 0.5s ease-in-out',
                  }}
                />
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography
                    variant="body2"
                    fontWeight={600}
                    sx={{
                      color: percentage > 50 ? 'white' : 'text.primary',
                      mixBlendMode: percentage > 50 ? 'difference' : 'normal',
                    }}
                  >
                    {percentage.toFixed(0)}%
                  </Typography>
                </Box>
              </Box>

              {rubricScore.feedback && (
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ mt: 0.5, display: 'block' }}
                >
                  {rubricScore.feedback}
                </Typography>
              )}
            </Box>
          );
        })}
      </Box>

      {/* Overall Summary */}
      <Box sx={{ mt: 3, p: 2, backgroundColor: 'action.hover', borderRadius: 1 }}>
        <Typography variant="body2" color="text.secondary">
          <strong>Legend:</strong> Red (&lt;5) = Needs improvement, Orange (5-7) = Satisfactory,
          Green (≥7) = Good/Excellent
        </Typography>
      </Box>
    </Paper>
  );
};
