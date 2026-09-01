/**
 * EMR Validation Results Page (PRD-EMR-PRACTICE-003)
 *
 * Destination of the "Submit for review" action from the Epic / Cerner EMR
 * editors. Fetches the validation result for a session and renders PASS/FAIL,
 * the overall score, the AMC rubric bars, missing required elements, critical
 * errors committed, strengths and areas for improvement.
 *
 * Param note: submit navigates with the `sessionId`; the backend exposes
 * GET /emr/validation/{id} where the validation id is an alias for the session
 * id (backward compatible), so the page fetches by `sessionId` directly.
 *
 * Accessibility (WCAG 2.2 AA):
 * - Semantic heading hierarchy (h1 page title, h2 section titles)
 * - Pass/fail status exposed via role="status" + aria-label + aria-live
 */

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Container,
  Box,
  Paper,
  Typography,
  Chip,
  CircularProgress,
  Alert,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Stack,
} from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ReplayIcon from '@mui/icons-material/Replay';
import { API_BASE_URL } from '../../utils/axiosInstance';
import { AMCRubricVisualization } from '../../components/emr/validation/AMCRubricVisualization';
import { ValidationStatusBanner } from '../../components/emr/validation/ValidationStatusBanner';
import type {
  AMCRubricScore,
  EMRSystem,
  EMRValidationApiResult,
  EMRValidationView,
} from '../../types/emr';

/**
 * Last-resort fallback pass mark on the 0-15 rubric. The backend `pass_fail`
 * field is AUTHORITATIVE (threshold 9/15 plus automatic FAIL on committed
 * critical errors / omitted must-not-miss elements). This constant is only ever
 * used when `pass_fail` is genuinely absent (undefined) and the AI layer was
 * available — never to override a backend decision.
 */
const PASS_THRESHOLD = 9;

const isPass = (raw: EMRValidationApiResult): boolean => {
  const pf = raw.pass_fail;
  // The backend boolean decision is the sole source of truth when present.
  if (typeof pf === 'boolean') return pf;
  if (typeof pf === 'string') return pf.toLowerCase() === 'pass';
  // pf is undefined or null here: last-resort local fallback only.
  return (raw.overall_score ?? 0) >= PASS_THRESHOLD;
};

const toRubricScores = (raw: EMRValidationApiResult): AMCRubricScore[] => {
  if (raw.amc_rubric_scores && raw.amc_rubric_scores.length > 0) {
    return raw.amc_rubric_scores.map((s) => ({
      category: s.category,
      score: s.score,
      // AMC categories are scored 0-3 (five categories, total 15).
      max_score: s.max_score ?? 3,
      feedback: s.feedback ?? '',
    }));
  }
  if (raw.category_scores) {
    return Object.entries(raw.category_scores).map(([category, score]) => ({
      category,
      score,
      // AMC categories are scored 0-3 (five categories, total 15).
      max_score: 3,
      feedback: '',
    }));
  }
  return [];
};

/** Normalise the raw payload (flat or nested, legacy field names) for rendering. */
export const normalizeValidationResult = (
  raw: EMRValidationApiResult
): EMRValidationView => {
  const src = raw.validation_results ?? raw;
  const status = src.status ?? src.validation_status;
  const rubricScores = toRubricScores(src);
  // Explicit guard: `pass_fail` is null (not undefined) when the AI layer was
  // unavailable, so `typeof src.pass_fail !== 'undefined'` alone would be true.
  const aiUnavailable = src.ai_unavailable === true;
  const isComplete =
    // ai_unavailable is a terminal state: stop polling and show the notice.
    aiUnavailable ||
    typeof src.pass_fail !== 'undefined' ||
    status === 'completed' ||
    rubricScores.length > 0;

  return {
    isComplete,
    aiUnavailable,
    passed: isPass(src),
    overallScore: src.overall_score ?? 0,
    rubricScores,
    missingElements: src.missing_elements ?? [],
    criticalErrors: src.critical_errors_committed ?? src.red_flags ?? [],
    strengths: src.strengths ?? [],
    areasForImprovement: src.areas_for_improvement ?? src.improvements ?? [],
    ahpraCompliance: Boolean(src.ahpra_compliance),
  };
};

export const EMRValidationPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const { data, isLoading, error, refetch } = useQuery<EMRValidationApiResult>({
    queryKey: ['emr-validation', sessionId],
    queryFn: async () => {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${API_BASE_URL}/emr/validation/${sessionId}`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
      if (!response.ok) {
        throw new Error('Failed to load validation results');
      }
      return (await response.json()) as EMRValidationApiResult;
    },
    enabled: !!sessionId,
  });

  if (isLoading) {
    return (
      <Container sx={{ py: 6, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress aria-label="Loading validation results" />
      </Container>
    );
  }

  if (error || !data) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="error">
          Failed to load validation results
          {error instanceof Error ? `: ${error.message}` : ''}.
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/dashboard')}
          sx={{ mt: 2 }}
        >
          Back to dashboard
        </Button>
      </Container>
    );
  }

  const view = normalizeValidationResult(data);

  // The session is still in_progress (ungraded); send the student back to the
  // EMR editor they used so they can re-submit and re-run the assessment.
  const returnToEditor = () => {
    if (!sessionId) return;
    const system: EMRSystem =
      localStorage.getItem('emr_system_preference') === 'cerner' ? 'cerner' : 'epic';
    navigate(`/emr/${system}/${sessionId}`);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
        EMR Validation Results
      </Typography>

      {/* While the AI is still grading, poll via the shared status banner. */}
      {!view.isComplete && !view.aiUnavailable && sessionId && (
        <ValidationStatusBanner validationId={sessionId} onComplete={() => refetch()} />
      )}

      {/* AI assessment temporarily unavailable: session left ungraded. */}
      {view.aiUnavailable && (
        <>
          <Alert
            severity="warning"
            role="status"
            aria-live="polite"
            sx={{ mb: 3 }}
          >
            <Typography variant="body1" fontWeight={600} gutterBottom>
              AI assessment is temporarily unavailable
            </Typography>
            <Typography variant="body2">
              Your documentation was saved — please re-submit shortly to have it
              assessed. No score has been recorded for this attempt.
            </Typography>
          </Alert>
          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              startIcon={<ReplayIcon />}
              onClick={returnToEditor}
            >
              Return to documentation
            </Button>
            <Button
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/dashboard')}
            >
              Back to dashboard
            </Button>
          </Stack>
        </>
      )}

      {view.isComplete && !view.aiUnavailable && (
        <>
          {/* Pass / fail + overall score */}
          <Paper
            elevation={0}
            role="status"
            aria-live="polite"
            aria-label={`Assessment result: ${
              view.passed ? 'Pass' : 'Fail'
            }, overall score ${view.overallScore} out of 15`}
            sx={{
              p: 3,
              mb: 3,
              border: '1px solid',
              borderColor: view.passed ? 'success.main' : 'error.main',
              borderRadius: 1,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Chip
              label={view.passed ? 'PASS' : 'FAIL'}
              color={view.passed ? 'success' : 'error'}
              sx={{ fontWeight: 700, fontSize: '1rem', px: 1 }}
            />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Overall score
              </Typography>
              <Typography variant="h5" component="p" fontWeight={700}>
                {view.overallScore} / 15
              </Typography>
            </Box>
            {view.ahpraCompliance && (
              <Chip
                label="AHPRA standards met"
                color="success"
                variant="outlined"
                size="small"
                sx={{ ml: 'auto' }}
              />
            )}
          </Paper>

          {/* AMC rubric bars (reused presentational component) */}
          {view.rubricScores.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <AMCRubricVisualization scores={view.rubricScores} />
            </Box>
          )}

          {/* Critical errors committed */}
          {view.criticalErrors.length > 0 && (
            <Paper
              elevation={0}
              sx={{ p: 3, mb: 3, border: '1px solid', borderColor: 'error.light' }}
            >
              <Typography variant="h6" component="h2" gutterBottom color="error">
                Critical Errors
              </Typography>
              <List dense>
                {view.criticalErrors.map((item, idx) => (
                  <ListItem key={`critical-${idx}`} disableGutters>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <ReportProblemIcon color="error" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={item} />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}

          {/* Missing required elements */}
          {view.missingElements.length > 0 && (
            <Paper
              elevation={0}
              sx={{ p: 3, mb: 3, border: '1px solid', borderColor: 'warning.light' }}
            >
              <Typography variant="h6" component="h2" gutterBottom>
                Missing Required Elements
              </Typography>
              <List dense>
                {view.missingElements.map((item, idx) => (
                  <ListItem key={`missing-${idx}`} disableGutters>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <ErrorOutlineIcon color="warning" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={item} />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}

          {/* Strengths + areas for improvement */}
          {(view.strengths.length > 0 || view.areasForImprovement.length > 0) && (
            <Paper
              elevation={0}
              sx={{ p: 3, mb: 3, border: '1px solid', borderColor: 'divider' }}
            >
              {view.strengths.length > 0 && (
                <>
                  <Typography variant="h6" component="h2" gutterBottom>
                    Strengths
                  </Typography>
                  <List dense>
                    {view.strengths.map((item, idx) => (
                      <ListItem key={`strength-${idx}`} disableGutters>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckCircleOutlineIcon color="success" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={item} />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}

              {view.strengths.length > 0 && view.areasForImprovement.length > 0 && (
                <Divider sx={{ my: 2 }} />
              )}

              {view.areasForImprovement.length > 0 && (
                <>
                  <Typography variant="h6" component="h2" gutterBottom>
                    Areas for Improvement
                  </Typography>
                  <List dense>
                    {view.areasForImprovement.map((item, idx) => (
                      <ListItem key={`improve-${idx}`} disableGutters>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <TrendingUpIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={item} />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}
            </Paper>
          )}

          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/dashboard')}
            >
              Back to dashboard
            </Button>
            <Button variant="outlined" onClick={() => navigate('/emr/cases')}>
              Practise another case
            </Button>
          </Stack>
        </>
      )}
    </Container>
  );
};

export default EMRValidationPage;
