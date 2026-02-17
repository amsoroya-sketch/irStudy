/**
 * OSCE Practice Placeholder Component
 * Displays placeholder for AI OSCE practice (backend not yet implemented)
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC (Australian Medical Council) OSCE format
 * - 8-minute stations with AI Patient and AI Examiner
 * - Assessed using AMC 15-mark rubric
 *
 * ACCESSIBILITY (WCAG 2.2 AA):
 * - Clear messaging about feature status
 * - Disabled button with tooltip explanation
 * - Screen reader friendly
 */

import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Construction as ConstructionIcon,
  VideoCall as VideoCallIcon,
  Timer as TimerIcon,
  Psychology as PsychologyIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { OSCEScenario } from '../../types/osce';

export interface OSCEPracticePlaceholderProps {
  /** Optional: Show specific scenario preview */
  previewScenario?: OSCEScenario;
}

/**
 * Mock scenario for preview
 */
const mockScenario: OSCEScenario = {
  id: 'OSCE-PREVIEW-001',
  title: 'Acute Chest Pain Assessment',
  description: 'Assess a patient presenting with acute chest pain in the emergency department',
  specialty: 'Emergency Medicine',
  difficulty: 'medium',
  timeLimitMinutes: 8,
  patientPresentation: '55-year-old male with sudden onset central chest pain, radiating to left arm',
  learningObjectives: [
    'Perform focused cardiovascular history',
    'Assess for red flag symptoms',
    'Develop appropriate management plan',
    'Demonstrate professional communication',
  ],
};

/**
 * OSCE Practice Placeholder Component
 */
export const OSCEPracticePlaceholder: React.FC<OSCEPracticePlaceholderProps> = ({
  previewScenario = mockScenario,
}) => {
  return (
    <Box sx={{ maxWidth: 900, margin: '0 auto', p: 2 }}>
      {/* Coming Soon Alert */}
      <Alert
        severity="info"
        icon={<ConstructionIcon />}
        sx={{ mb: 3 }}
        aria-live="polite"
      >
        <AlertTitle sx={{ fontWeight: 600 }}>
          AI OSCE Practice - Coming Soon
        </AlertTitle>
        <Typography variant="body2">
          The AI Patient and AI Examiner agents are not yet implemented.
          Backend infrastructure for real-time conversational OSCE practice is currently in development.
        </Typography>
      </Alert>

      {/* Planned Features Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Planned Features
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            When the backend is ready, you will be able to:
          </Typography>

          <List dense>
            <ListItem>
              <ListItemIcon>
                <VideoCallIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Real-time conversational AI patient (via WebSocket)"
                secondary="Natural conversation with simulated patient responses"
              />
            </ListItem>

            <ListItem>
              <ListItemIcon>
                <AssessmentIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="AI Examiner scoring with AMC 15-mark rubric"
                secondary="Automated assessment across 5 domains"
              />
            </ListItem>

            <ListItem>
              <ListItemIcon>
                <TimerIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="8-minute timer with emotional state simulation"
                secondary="Realistic time pressure like actual AMC exam"
              />
            </ListItem>

            <ListItem>
              <ListItemIcon>
                <PsychologyIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Detailed performance feedback"
                secondary="Comprehensive rubric breakdown with improvement suggestions"
              />
            </ListItem>
          </List>

          <Divider sx={{ my: 2 }} />

          {/* Disabled Connect Button */}
          <Tooltip
            title="Requires backend implementation"
            arrow
            placement="top"
          >
            <span>
              <Button
                variant="contained"
                startIcon={<ConstructionIcon />}
                disabled
                fullWidth
                size="large"
                aria-label="Connect to AI Patient (requires backend implementation)"
              >
                Connect to AI Patient
              </Button>
            </span>
          </Tooltip>
        </CardContent>
      </Card>

      {/* Scenario Preview Card */}
      <Card
        sx={{ backgroundColor: 'grey.50' }}
        role="region"
        aria-label="Scenario Preview"
      >
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Scenario Preview
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Example OSCE scenario (for demonstration only):
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              {previewScenario.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {previewScenario.description}
            </Typography>
          </Box>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
              gap: 2,
              mb: 2,
            }}
          >
            <Box>
              <Typography variant="caption" color="text.secondary">
                Specialty
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {previewScenario.specialty}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Difficulty
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>
                {previewScenario.difficulty}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Time Limit
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {previewScenario.timeLimitMinutes} minutes
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
            Patient Presentation:
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {previewScenario.patientPresentation}
          </Typography>

          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
            Learning Objectives:
          </Typography>
          <List dense sx={{ pl: 2 }}>
            {previewScenario.learningObjectives.map((objective, index) => (
              <ListItem key={index} sx={{ display: 'list-item', listStyleType: 'disc', pl: 0 }}>
                <ListItemText primary={objective} />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

export default OSCEPracticePlaceholder;
