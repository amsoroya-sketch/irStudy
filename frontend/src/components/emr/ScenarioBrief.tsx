/**
 * ScenarioBrief Component (PRD-EMR-PRACTICE-003)
 *
 * Shows the student the clinical challenge and their task BEFORE they start
 * documenting: the presenting complaint and the assessment task, plus optional
 * difficulty / specialty chips.
 *
 * Rendered at the top of the Epic / Cerner EMR editor bodies.
 *
 * Accessibility (WCAG 2.2 AA):
 * - Semantic heading structure (h2 region title, h3 sub-labels)
 * - Labelled region via aria-labelledby
 */

import React from 'react';
import { Paper, Typography, Box, Chip, Stack } from '@mui/material';
import AssignmentIcon from '@mui/icons-material/Assignment';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';

export interface ScenarioBriefProps {
  presentingComplaint: string;
  task: string;
  difficulty?: string;
  specialty?: string;
}

export const ScenarioBrief: React.FC<ScenarioBriefProps> = ({
  presentingComplaint,
  task,
  difficulty,
  specialty,
}) => {
  return (
    <Paper
      component="section"
      elevation={0}
      aria-labelledby="scenario-brief-title"
      sx={{
        p: 2.5,
        mb: 2,
        border: '1px solid',
        borderColor: 'primary.light',
        borderLeft: '4px solid',
        borderLeftColor: 'primary.main',
        backgroundColor: 'action.hover',
        borderRadius: 1,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
        <LocalHospitalIcon color="primary" fontSize="small" aria-hidden="true" />
        <Typography id="scenario-brief-title" variant="h6" component="h2" fontWeight={700}>
          Clinical Scenario
        </Typography>
        <Stack direction="row" spacing={1} sx={{ ml: 'auto' }}>
          {specialty && (
            <Chip label={specialty} size="small" color="primary" variant="outlined" />
          )}
          {difficulty && (
            <Chip label={difficulty} size="small" color="secondary" variant="outlined" />
          )}
        </Stack>
      </Box>

      <Typography variant="subtitle2" component="h3" color="text.secondary" gutterBottom>
        Presenting complaint
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }}>
        {presentingComplaint}
      </Typography>

      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
        <AssignmentIcon color="primary" fontSize="small" aria-hidden="true" sx={{ mt: 0.3 }} />
        <Box>
          <Typography variant="subtitle2" component="h3" color="text.secondary" gutterBottom>
            Your task
          </Typography>
          <Typography variant="body1" fontWeight={500}>
            {task}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default ScenarioBrief;
