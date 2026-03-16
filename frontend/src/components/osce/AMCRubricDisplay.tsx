/**
 * AMC Rubric Display Component
 * Displays AMC 15-mark rubric with scoring breakdown
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC (Australian Medical Council) standardized rubric
 * - 5 domains, 15 marks total
 * - Pass threshold: ≥10 marks
 * - Excellence threshold: 14-15 marks
 *
 * ACCESSIBILITY (WCAG 2.2 AA):
 * - Semantic HTML structure
 * - Color coding with text labels (not color alone)
 * - Screen reader friendly aria labels
 */

import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import Grid from '@mui/material/GridLegacy';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material';
import { AMCRubricScore, AMCRubricDomain } from '../../types/osce';

export interface AMCRubricDisplayProps {
  /** AMC rubric score breakdown */
  score: AMCRubricScore;
  /** Show behavioral anchors for each domain (default: true) */
  showBehavioralAnchors?: boolean;
  /** Show progress bars (default: true) */
  showProgressBars?: boolean;
}

/**
 * AMC 15-Mark Rubric Definition
 * Official AMC domains with behavioral anchors
 */
const AMC_RUBRIC_DOMAINS: AMCRubricDomain[] = [
  {
    name: 'Communication Skills',
    maxMarks: 3,
    description: 'Clarity, empathy, active listening, patient-centered communication',
    behavioralAnchors: {
      0: 'Poor communication, patient confused or distressed',
      1: 'Basic communication with significant clarity issues',
      2: 'Good communication, mostly clear and empathetic',
      3: 'Excellent communication, highly empathetic and clear',
    },
  },
  {
    name: 'Clinical Reasoning',
    maxMarks: 4,
    description: 'Differential diagnosis, systematic approach, evidence-based thinking',
    behavioralAnchors: {
      0: 'No systematic approach, poor reasoning',
      1: 'Limited differential, unsystematic approach',
      2: 'Basic differential, some systematic thinking',
      3: 'Good differential, systematic and logical',
      4: 'Excellent reasoning, comprehensive and evidence-based',
    },
  },
  {
    name: 'Information Gathering',
    maxMarks: 3,
    description: 'History taking, physical examination, appropriate investigations',
    behavioralAnchors: {
      0: 'Inadequate history/examination',
      1: 'Limited information gathering, key gaps',
      2: 'Adequate information gathering, minor gaps',
      3: 'Comprehensive and focused information gathering',
    },
  },
  {
    name: 'Management Plan',
    maxMarks: 3,
    description: 'Evidence-based management, safety considerations, follow-up planning',
    behavioralAnchors: {
      0: 'Inappropriate or unsafe management',
      1: 'Basic plan with significant gaps',
      2: 'Appropriate management with minor gaps',
      3: 'Comprehensive, safe, and evidence-based plan',
    },
  },
  {
    name: 'Professionalism & Ethics',
    maxMarks: 2,
    description: 'Ethics, consent, cultural safety, confidentiality, professionalism',
    behavioralAnchors: {
      0: 'Unprofessional or unethical behavior',
      1: 'Basic professionalism, some ethical concerns',
      2: 'Excellent professionalism and ethical conduct',
    },
  },
];

/**
 * Get domain score from AMCRubricScore
 */
const getDomainScore = (score: AMCRubricScore, domainName: string): number => {
  switch (domainName) {
    case 'Communication Skills':
      return score.communicationSkills;
    case 'Clinical Reasoning':
      return score.clinicalReasoning;
    case 'Information Gathering':
      return score.informationGathering;
    case 'Management Plan':
      return score.managementPlan;
    case 'Professionalism & Ethics':
      return score.professionalismEthics;
    default:
      return 0;
  }
};

/**
 * AMC Rubric Display Component
 */
export const AMCRubricDisplay: React.FC<AMCRubricDisplayProps> = ({
  score,
  showBehavioralAnchors = true,
  showProgressBars = true,
}) => {
  const isPassed = score.passed;
  const isExcellent = score.totalScore >= 14;

  return (
    <Card
      sx={{ maxWidth: 900, margin: '0 auto' }}
      role="region"
      aria-label="AMC 15-mark rubric"
    >
      <CardContent>
        {/* Header */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
            AMC 15-Mark Rubric
          </Typography>

          {/* Pass/Fail Chip */}
          <Chip
            icon={isPassed ? <CheckCircleIcon /> : <CancelIcon />}
            label={isPassed ? 'Pass' : 'Fail'}
            color={isPassed ? 'success' : 'error'}
            size="medium"
            aria-label={isPassed ? 'Passed' : 'Failed'}
          />
        </Box>

        {/* Total Score */}
        <Box
          sx={{
            p: 2,
            mb: 3,
            backgroundColor: isExcellent
              ? 'success.light'
              : isPassed
                ? 'info.light'
                : 'error.light',
            borderRadius: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isExcellent && <TrophyIcon color="success" />}
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Total Score: {score.totalScore} / 15
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Pass Threshold: ≥10 marks
          </Typography>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Domain Breakdown */}
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
          Domain Breakdown
        </Typography>

        <Grid container spacing={3}>
          {AMC_RUBRIC_DOMAINS.map((domain) => {
            const domainScore = getDomainScore(score, domain.name);
            const percentage = (domainScore / domain.maxMarks) * 100;

            return (
              <Grid item xs={12} md={6} key={domain.name}>
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent>
                    {/* Domain Header */}
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        mb: 1,
                      }}
                    >
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {domain.name}
                      </Typography>
                      <Chip
                        label={`${domainScore} / ${domain.maxMarks}`}
                        size="small"
                        color={
                          percentage >= 75
                            ? 'success'
                            : percentage >= 50
                              ? 'warning'
                              : 'error'
                        }
                      />
                    </Box>

                    {/* Domain Description */}
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 2, fontSize: '0.875rem' }}
                    >
                      {domain.description}
                    </Typography>

                    {/* Progress Bar */}
                    {showProgressBars && (
                      <LinearProgress
                        variant="determinate"
                        value={percentage}
                        sx={{
                          mb: 2,
                          height: 8,
                          borderRadius: 1,
                          backgroundColor: 'grey.200',
                        }}
                        color={
                          percentage >= 75
                            ? 'success'
                            : percentage >= 50
                              ? 'warning'
                              : 'error'
                        }
                      />
                    )}

                    {/* Behavioral Anchors */}
                    {showBehavioralAnchors && (
                      <Box>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ fontWeight: 600, mb: 0.5, display: 'block' }}
                        >
                          Current Level ({domainScore} marks):
                        </Typography>
                        <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                          {domain.behavioralAnchors[domainScore]}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>

        {/* Full Behavioral Anchors (Optional) */}
        {showBehavioralAnchors && (
          <>
            <Divider sx={{ my: 3 }} />
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
              Complete Rubric Reference
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Behavioral anchors for each domain:
            </Typography>

            {AMC_RUBRIC_DOMAINS.map((domain) => (
              <Box key={domain.name} sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  {domain.name} (0-{domain.maxMarks} marks)
                </Typography>
                <List dense>
                  {Object.entries(domain.behavioralAnchors).map(([marks, description]) => (
                    <ListItem key={marks} sx={{ py: 0.5 }}>
                      <ListItemText
                        primary={
                          <Typography variant="body2" component="span">
                            <strong>{marks} mark{Number(marks) !== 1 ? 's' : ''}:</strong>{' '}
                            {description}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            ))}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default AMCRubricDisplay;
