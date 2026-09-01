/**
 * EMR Case List Page (Phase 1b — "pick a case and practice")
 *
 * Primary entry point for EMR documentation practice. Lists available patient
 * cases grouped by specialty, with the difficulty shown as a chip on each card.
 * Selecting a case starts a session for that specific patient; a secondary
 * action starts a random case (preserving the existing quick-start flow).
 *
 * WCAG 2.2 AA:
 * - Cards are keyboard-navigable action areas with descriptive aria-labels.
 * - Difficulty chips use both colour and text (not colour alone).
 * - Loading/error states announced via CircularProgress/Alert.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Box,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Grid,
  Stack,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Casino as RandomIcon,
  ArrowBack as BackIcon,
} from '@mui/icons-material';
import type { SelectChangeEvent } from '@mui/material';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  listEMRCases,
  startEMRSession,
  type EMRCaseFilters,
} from '../../api/emr';
import type { EMRCaseSummary } from '../../types/emr';

/**
 * Map difficulty to a MUI chip colour. Falls back to default for unknowns.
 */
const difficultyColor = (
  difficulty: string
): 'success' | 'warning' | 'error' | 'default' => {
  switch (difficulty?.toLowerCase()) {
    case 'easy':
      return 'success';
    case 'medium':
    case 'moderate':
      return 'warning';
    case 'hard':
    case 'difficult':
      return 'error';
    default:
      return 'default';
  }
};

const EMRCaseListPage: React.FC = () => {
  const navigate = useNavigate();
  const [specialty, setSpecialty] = useState<string>('');
  const [difficulty, setDifficulty] = useState<string>('');

  useEffect(() => {
    document.title = 'Pick an EMR Case - irStudy';
  }, []);

  const filters: EMRCaseFilters = useMemo(
    () => ({
      specialty: specialty || undefined,
      difficulty: difficulty || undefined,
    }),
    [specialty, difficulty]
  );

  const {
    data,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['emr-cases', filters],
    queryFn: () => listEMRCases(filters),
  });

  // Shared post-start navigation: honour saved system preference, otherwise
  // fall through to the system selector. Mirrors StartEMRSessionPage.
  const navigateAfterStart = (sessionId: string) => {
    const savedPreference = localStorage.getItem('emr_system_preference');
    if (savedPreference === 'epic' || savedPreference === 'cerner') {
      navigate(`/emr/${savedPreference}/${sessionId}`);
    } else {
      navigate(`/emr/select/${sessionId}`);
    }
  };

  const startSessionMutation = useMutation({
    mutationFn: (patientId?: string) =>
      startEMRSession(patientId ? { patient_id: patientId } : undefined),
    onSuccess: (result) => {
      navigateAfterStart(result.session_id);
    },
  });

  const isStarting = startSessionMutation.isPending;

  // Group cases by specialty for section headers.
  const groupedBySpecialty = useMemo(() => {
    const groups = new Map<string, EMRCaseSummary[]>();
    (data?.cases ?? []).forEach((c) => {
      const key = c.specialty || 'Other';
      const list = groups.get(key) ?? [];
      list.push(c);
      groups.set(key, list);
    });
    return Array.from(groups.entries()).sort(([a], [b]) =>
      a.localeCompare(b)
    );
  }, [data]);

  // Distinct specialties/difficulties for the filter selects (from unfiltered
  // data is ideal, but we derive from current data which is adequate here).
  const specialtyOptions = useMemo(
    () =>
      Array.from(new Set((data?.cases ?? []).map((c) => c.specialty))).sort(),
    [data]
  );

  const handleSpecialtyChange = (event: SelectChangeEvent) => {
    setSpecialty(event.target.value);
  };
  const handleDifficultyChange = (event: SelectChangeEvent) => {
    setDifficulty(event.target.value);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Pick an EMR Case
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Choose a patient case to practise your clinical documentation, or
          start a random case. You&apos;ll document using Epic or Cerner EMR
          systems and submit for AMC-rubric validation.
        </Typography>
      </Box>

      {/* Actions + filters */}
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={2}
        alignItems={{ xs: 'stretch', sm: 'center' }}
        sx={{ mb: 4 }}
      >
        <Button
          variant="outlined"
          startIcon={<RandomIcon />}
          onClick={() => startSessionMutation.mutate(undefined)}
          disabled={isStarting}
          aria-label="Start a random EMR case"
        >
          Start a random case
        </Button>

        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="emr-specialty-filter-label">Specialty</InputLabel>
          <Select
            labelId="emr-specialty-filter-label"
            id="emr-specialty-filter"
            value={specialty}
            label="Specialty"
            onChange={handleSpecialtyChange}
          >
            <MenuItem value="">All specialties</MenuItem>
            {specialtyOptions.map((s) => (
              <MenuItem key={s} value={s}>
                {s}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel id="emr-difficulty-filter-label">Difficulty</InputLabel>
          <Select
            labelId="emr-difficulty-filter-label"
            id="emr-difficulty-filter"
            value={difficulty}
            label="Difficulty"
            onChange={handleDifficultyChange}
          >
            <MenuItem value="">All difficulties</MenuItem>
            <MenuItem value="easy">Easy</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="hard">Hard</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      {startSessionMutation.isError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to start session:{' '}
          {(startSessionMutation.error as Error).message}
        </Alert>
      )}

      {/* Loading */}
      {isLoading && (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
            py: 8,
          }}
        >
          <CircularProgress size={60} aria-label="Loading EMR cases" />
          <Typography variant="body2" color="text.secondary">
            Loading available cases...
          </Typography>
        </Box>
      )}

      {/* Error */}
      {isError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to load cases: {(error as Error).message}
        </Alert>
      )}

      {/* Empty */}
      {!isLoading && !isError && (data?.cases.length ?? 0) === 0 && (
        <Alert severity="info">
          No cases match the selected filters. Try clearing the filters or start
          a random case.
        </Alert>
      )}

      {/* Grouped case grid */}
      {!isLoading &&
        !isError &&
        groupedBySpecialty.map(([specialtyName, cases]) => (
          <Box key={specialtyName} sx={{ mb: 5 }}>
            <Typography variant="h5" component="h2" gutterBottom>
              {specialtyName}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={3}>
              {cases.map((emrCase) => (
                <Grid size={{ xs: 12, sm: 6, md: 4 }} key={emrCase.id}>
                  <Card sx={{ height: '100%', display: 'flex' }}>
                    <CardActionArea
                      onClick={() =>
                        startSessionMutation.mutate(emrCase.id)
                      }
                      disabled={isStarting}
                      aria-label={`Practise case: ${emrCase.name}, ${emrCase.age} year old ${emrCase.gender}, presenting with ${emrCase.presenting_complaint}. Difficulty ${emrCase.difficulty}.`}
                      sx={{
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'stretch',
                      }}
                    >
                      <CardContent sx={{ width: '100%' }}>
                        <Box
                          sx={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'flex-start',
                            gap: 1,
                            mb: 1,
                          }}
                        >
                          <Typography variant="h6" component="h3">
                            {emrCase.name}
                          </Typography>
                          <Chip
                            label={emrCase.difficulty || 'Unknown'}
                            color={difficultyColor(emrCase.difficulty)}
                            size="small"
                          />
                        </Box>

                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 1 }}
                        >
                          {emrCase.age} yo {emrCase.gender} · MRN {emrCase.mrn}
                        </Typography>

                        <Typography variant="body1" sx={{ mb: 2 }}>
                          {emrCase.presenting_complaint}
                        </Typography>

                        <Chip
                          label={emrCase.specialty}
                          variant="outlined"
                          size="small"
                          sx={{ mb: 2 }}
                        />

                        <Box>
                          <Button
                            component="span"
                            variant="contained"
                            fullWidth
                            startIcon={<StartIcon />}
                            disabled={isStarting}
                            aria-hidden="true"
                            tabIndex={-1}
                          >
                            Practice this case
                          </Button>
                        </Box>
                      </CardContent>
                    </CardActionArea>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        ))}

      <Box sx={{ mt: 4 }}>
        <Button
          variant="text"
          startIcon={<BackIcon />}
          onClick={() => navigate('/dashboard')}
        >
          Back to Dashboard
        </Button>
      </Box>
    </Container>
  );
};

export default EMRCaseListPage;
