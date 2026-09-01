/**
 * AMC Rubric Visualization Component
 *
 * Displays AMC Clinical Examination rubric scores with horizontal bars.
 *
 * Categories (AMC 15-mark rubric, each scored 0-3):
 * 1. History Taking
 * 2. Clinical Reasoning
 * 3. Documentation Quality
 * 4. Patient Safety
 * 5. Professional Communication
 *
 * Features:
 * - Horizontal bar charts for each category
 * - Color-coded scores by proportion of max (red <50%, orange 50-70%, green ≥70%)
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
  clinical_reasoning: 'Clinical Reasoning',
  documentation_quality: 'Documentation Quality',
  patient_safety: 'Patient Safety',
  professional_communication: 'Professional Communication',
  // legacy keys (kept for backward compatibility)
  physical_examination: 'Physical Examination',
  communication: 'Communication',
  documentation: 'Documentation',
};

/** Map a backend category key (e.g. "History_Taking") to a human label. */
const labelFor = (category: string): string =>
  categoryLabels[category.toLowerCase()] || category.replace(/_/g, ' ');

// Colour by proportion of max, so it is correct regardless of the scale
// (0-3 per AMC category, or a legacy 0-10). Red <50%, orange 50-70%, green ≥70%.
const getScoreColor = (
  score: number,
  maxScore: number
): 'error' | 'warning' | 'success' => {
  const pct = maxScore > 0 ? (score / maxScore) * 100 : 0;
  if (pct < 50) return 'error';
  if (pct < 70) return 'warning';
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
          const color = getScoreColor(rubricScore.score, rubricScore.max_score);
          const label = labelFor(rubricScore.category);

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
          <strong>Legend:</strong> Red (&lt;50%) = Needs improvement, Orange (50-70%) = Satisfactory,
          Green (≥70%) = Good/Excellent
        </Typography>
      </Box>
    </Paper>
  );
};
