/**
 * EmotionalStateIndicator.tsx - AI Patient Emotional State Display
 * Real-time emotional state tracking for OSCE practice sessions
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - AMC Clinical Examination communication skills assessment
 * - Real-time patient emotional state visualization
 * - Communication strategy guidance based on patient state
 *
 * ACCESSIBILITY (WCAG 2.2 AA):
 * - High contrast colors (≥4.5:1 ratio)
 * - Text labels + icons (not color alone)
 * - ARIA labels for screen readers
 * - Tooltip explanations
 *
 * PERFORMANCE:
 * - Smooth transitions (200ms fade)
 * - Optimized re-renders with React.memo
 */

import React from 'react';
import { Box, Chip, Typography, Tooltip, Fade } from '@mui/material';
import { styled } from '@mui/material/styles';
import SentimentSatisfiedIcon from '@mui/icons-material/SentimentSatisfied';
import SentimentNeutralIcon from '@mui/icons-material/SentimentNeutral';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import WarningIcon from '@mui/icons-material/Warning';

/**
 * AI Patient Emotional States
 * Matches backend emotional state enum
 */
export type EmotionalState =
  | 'COOPERATIVE'
  | 'ANXIOUS_GUARDED'
  | 'RESISTANT'
  | 'EMOTIONAL_DISTRESS'
  | 'CRISIS';

/**
 * Component props
 */
export interface EmotionalStateIndicatorProps {
  /** Current emotional state of AI patient */
  currentState: EmotionalState;
  /** Show tooltip on hover (default: true) */
  showTooltip?: boolean;
  /** Show communication tips section (default: true) */
  showCommunicationTips?: boolean;
}

/**
 * State configuration interface
 */
interface StateConfig {
  label: string;
  color: string;
  icon: React.ReactNode;
  tooltip: string;
  communicationTips: string;
  ariaLabel: string;
}

/**
 * AMC Clinical Exam Color Mapping
 * Colors optimized for:
 * - WCAG 2.2 AA compliance (≥4.5:1 contrast with white text)
 * - Colorblind accessibility
 * - AMC rubric visual cues
 */
const stateConfigs: Record<EmotionalState, StateConfig> = {
  COOPERATIVE: {
    label: 'Cooperative',
    color: '#2e7d32', // Dark green - positive engagement (4.5:1 contrast with white text)
    icon: <SentimentSatisfiedIcon />,
    tooltip: 'Patient is engaged and cooperative',
    communicationTips:
      'Continue with open-ended questions. Build rapport. Use active listening.',
    ariaLabel: 'Patient emotional state: Cooperative - engaged and cooperative',
  },
  ANXIOUS_GUARDED: {
    label: 'Anxious/Guarded',
    color: '#bf5000', // Dark orange - caution (4.81:1 contrast with white text)
    icon: <SentimentNeutralIcon />,
    tooltip: 'Patient is nervous or guarded',
    communicationTips:
      'Use reassuring language. Acknowledge their concerns. Slow down. Normalize their feelings.',
    ariaLabel: 'Patient emotional state: Anxious/Guarded - nervous or guarded',
  },
  RESISTANT: {
    label: 'Resistant',
    color: '#c62828', // Dark red - challenging interaction (4.5:1 contrast with white text)
    icon: <SentimentDissatisfiedIcon />,
    tooltip: 'Patient is resistant or defensive',
    communicationTips:
      'Use empathetic listening. Avoid confrontation. Explore underlying concerns. Validate emotions.',
    ariaLabel: 'Patient emotional state: Resistant - resistant or defensive',
  },
  EMOTIONAL_DISTRESS: {
    label: 'Emotional Distress',
    color: '#7b1fa2', // Dark purple - requires empathy (6.3:1 contrast with white text)
    icon: <ErrorOutlineIcon />,
    tooltip: 'Patient is emotionally distressed',
    communicationTips:
      'Offer tissues if crying. Pause if needed. Show empathy: "I can see this is difficult..." Allow silence.',
    ariaLabel:
      'Patient emotional state: Emotional Distress - emotionally distressed',
  },
  CRISIS: {
    label: 'Crisis',
    color: '#b71c1c', // Very dark red - urgent intervention (7.3:1 contrast with white text)
    icon: <WarningIcon />,
    tooltip: 'Patient is in crisis - immediate intervention needed',
    communicationTips:
      'URGENT: Assess safety immediately. Consider urgent referral. Show calm presence. Use direct communication.',
    ariaLabel:
      'Patient emotional state: Crisis - in crisis, immediate intervention needed',
  },
};

/**
 * Styled Components (Material-UI 7 pattern)
 */
const StateContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(1.5),
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  border: `2px solid ${theme.palette.divider}`,
  boxShadow: theme.shadows[1],
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(1.5),
    gap: theme.spacing(1),
  },
}));

const StateChip = styled(Chip, {
  shouldForwardProp: (prop) => prop !== 'stateColor',
})<{ stateColor: string }>(({ stateColor }) => ({
  backgroundColor: stateColor,
  color: '#ffffff',
  fontWeight: 600,
  fontSize: '0.875rem',
  padding: '4px 8px',
  height: 'auto',
  transition: 'all 200ms ease-in-out',
  '& .MuiChip-icon': {
    color: '#ffffff',
  },
  '&:hover': {
    transform: 'scale(1.02)',
    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
  },
}));

const TipsBox = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1.5),
  backgroundColor: theme.palette.grey[50],
  borderRadius: theme.shape.borderRadius,
  borderLeft: `4px solid ${theme.palette.info.main}`,
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(1),
  },
}));

/**
 * EmotionalStateIndicator Component
 *
 * Displays the AI patient's current emotional state with:
 * - Color-coded visual indicator
 * - Icon representation
 * - Communication strategy tips
 * - WCAG 2.2 AA compliant accessibility
 *
 * @param props - Component props
 */
export const EmotionalStateIndicator = React.memo<EmotionalStateIndicatorProps>(
  ({
    currentState,
    showTooltip = true,
    showCommunicationTips = true,
  }: EmotionalStateIndicatorProps): JSX.Element => {
    const config = stateConfigs[currentState];

    // State chip element (with or without tooltip)
    const stateChip = (
      <StateChip
        icon={config.icon}
        label={config.label}
        stateColor={config.color}
        aria-label={config.ariaLabel}
        data-testid={`emotional-state-${currentState}`}
      />
    );

    return (
      <Fade in timeout={200}>
        <StateContainer
          role="status"
          aria-live="polite"
          aria-atomic="true"
          data-testid="emotional-state-indicator"
        >
          {/* State Header */}
          <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
            <Typography
              variant="subtitle2"
              color="textSecondary"
              sx={{ fontWeight: 600 }}
            >
              Patient State:
            </Typography>

            {showTooltip ? (
              <Tooltip title={config.tooltip} arrow placement="top">
                {stateChip}
              </Tooltip>
            ) : (
              stateChip
            )}
          </Box>

          {/* Communication Strategy Tips */}
          {showCommunicationTips && (
            <TipsBox>
              <Typography
                variant="caption"
                color="textSecondary"
                display="block"
                gutterBottom
                sx={{ fontWeight: 600 }}
              >
                Communication Strategy:
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  fontSize: '0.875rem',
                  lineHeight: 1.5,
                }}
              >
                {config.communicationTips}
              </Typography>
            </TipsBox>
          )}
        </StateContainer>
      </Fade>
    );
  }
);

// Display name for React DevTools
EmotionalStateIndicator.displayName = 'EmotionalStateIndicator';

export default EmotionalStateIndicator;
