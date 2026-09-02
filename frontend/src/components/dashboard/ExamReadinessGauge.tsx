/**
 * ExamReadinessGauge Component
 * Circular progress gauge (0–100%) predicting AMC Clinical Exam readiness.
 *
 * Uses the weighted exam readiness algorithm from utils/examReadiness.ts:
 *   35% MCQ Accuracy | 25% OSCE Completions | 20% Study Cards
 *   10% Weak Areas   | 10% Study Streak
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  LinearProgress,
  Stack,
  Tooltip,
  Typography,
} from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import {
  calculateExamReadiness,
  type ExamReadinessFactors,
  type ExamReadinessFactorBreakdown,
} from '../../utils/examReadiness';

interface ExamReadinessGaugeProps {
  factors: ExamReadinessFactors;
}

// ── Colour helpers ──────────────────────────────────────────────────────────
function gaugeColor(score: number): 'success' | 'warning' | 'error' {
  if (score >= 80) return 'success';
  if (score >= 60) return 'warning';
  return 'error';
}

function gaugeBgColor(score: number): string {
  if (score >= 80) return '#e8f5e9';
  if (score >= 60) return '#fff8e1';
  return '#ffebee';
}

function gaugeHexColor(score: number): string {
  if (score >= 80) return '#4caf50';
  if (score >= 60) return '#ff9800';
  return '#f44336';
}

// ── Factor row ──────────────────────────────────────────────────────────────
function FactorRow({ factor }: { factor: ExamReadinessFactorBreakdown }) {
  const isWeakAreas = factor.label === 'Weak Areas';
  // For weak areas, lower actual is better
  const progressValue = isWeakAreas
    ? Math.max(0, 100 - (factor.actual / Math.max(factor.target + 5, 5)) * 100)
    : Math.min((factor.actual / factor.target) * 100, 100);

  const progressColor = progressValue >= 80 ? 'success' : progressValue >= 50 ? 'warning' : 'error';

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="caption" fontWeight="medium">
          {factor.label}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {isWeakAreas
            ? `${factor.actual}${factor.unit}`
            : `${factor.actual}${factor.unit} / ${factor.target}${factor.unit}`}
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={progressValue}
        color={progressColor}
        sx={{ height: 6, borderRadius: 3 }}
        aria-label={`${factor.label} progress`}
      />
    </Box>
  );
}

// ── Main component ──────────────────────────────────────────────────────────
const ExamReadinessGauge: React.FC<ExamReadinessGaugeProps> = ({ factors }) => {
  const result = calculateExamReadiness(factors);
  const { score, grade, recommendation, factors: breakdown } = result;
  const color = gaugeColor(score);
  const hexColor = gaugeHexColor(score);

  const gradeLabel =
    grade === 'excellent'
      ? 'Excellent'
      : grade === 'good'
        ? 'Good Progress'
        : 'Needs Work';

  const gradeChipColor = color;

  return (
    <Card
      sx={{ height: '100%' }}
      role="region"
      aria-label="Exam Readiness Gauge"
    >
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" component="h2" sx={{ flex: 1 }}>
            AMC Exam Readiness
          </Typography>
          <Tooltip
            title="Calculated from MCQ accuracy (35%), OSCE completions (25%), study card mastery (20%), weak areas (10%), and study streak (10%)."
            arrow
          >
            <InfoOutlinedIcon
              fontSize="small"
              color="action"
              sx={{ cursor: 'help' }}
              aria-label="Readiness score information"
            />
          </Tooltip>
        </Box>

        {/* Circular gauge */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            py: 2,
          }}
        >
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            {/* Background ring */}
            <CircularProgress
              variant="determinate"
              value={100}
              size={140}
              thickness={5}
              sx={{ color: '#e0e0e0', position: 'absolute' }}
              aria-hidden="true"
            />
            {/* Score ring */}
            <CircularProgress
              variant="determinate"
              value={score}
              size={140}
              thickness={5}
              sx={{ color: hexColor }}
              aria-label={`Exam readiness score: ${score} percent`}
            />
            {/* Score label inside ring */}
            <Box
              sx={{
                top: 0,
                left: 0,
                bottom: 0,
                right: 0,
                position: 'absolute',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                bgcolor: gaugeBgColor(score),
                borderRadius: '50%',
                m: '10px',
              }}
            >
              <Typography
                variant="h4"
                component="div"
                fontWeight="bold"
                sx={{ color: hexColor, lineHeight: 1 }}
                aria-hidden="true"
              >
                {score}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Ready
              </Typography>
            </Box>
          </Box>

          {/* Grade chip */}
          <Chip
            label={gradeLabel}
            color={gradeChipColor}
            size="small"
            sx={{ mt: 2, fontWeight: 'bold' }}
            aria-label={`Readiness grade: ${gradeLabel}`}
          />
        </Box>

        {/* Recommendation */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ textAlign: 'center', mb: 2, fontStyle: 'italic', px: 1 }}
          role="status"
          aria-live="polite"
        >
          {recommendation}
        </Typography>

        <Divider sx={{ mb: 2 }} />

        {/* Factor breakdown */}
        <Typography variant="subtitle2" component="div" gutterBottom>
          Score Breakdown
        </Typography>
        <Stack spacing={1.5}>
          {breakdown.map((factor) => (
            <FactorRow key={factor.label} factor={factor} />
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
};

export default ExamReadinessGauge;
