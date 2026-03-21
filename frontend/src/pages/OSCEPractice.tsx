/**
 * OSCE Practice Page
 * Patient persona selector for AMC Clinical Examination preparation
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - All 207 personas validated for AMC Clinical Examination
 * - RAG-verified citations (7,245 citations, 66% Australian sources)
 * - Specialties: Cardiology, Emergency, General Practice, Pediatrics, Respiratory
 * - Difficulty levels: foundation (basic), intermediate (standard), advanced (complex)
 */

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Divider,
  Chip,
  Button,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { getPersonas, getPersonaDetail, PersonaListParams } from '../api/personas';
import { createOSCESession } from '../api/osce';

const OSCEPractice: React.FC = () => {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<PersonaListParams>({
    specialty: undefined,
    difficulty: undefined,
    skip: 0,
    limit: 100,
  });

  const [selectedPersonaId, setSelectedPersonaId] = useState<string>('');

  useEffect(() => {
    document.title = 'OSCE Practice - AMC Clinical Exam';
  }, []);

  // Mutation for creating OSCE session
  const createSessionMutation = useMutation({
    mutationFn: (personaId: string) => createOSCESession(personaId),
    onSuccess: (data) => {
      // Navigate to session page with attempt_id
      console.log('[OSCEPractice] Session created:', data.attempt_id);
      navigate(`/osce/session/${data.attempt_id}`);
    },
    onError: (error: unknown) => {
      console.error('[OSCEPractice] Failed to create session:', error);
      alert('Failed to start OSCE session. Please try again.');
    },
  });

  /**
   * Handle Start Session button click
   */
  const handleStartSession = () => {
    if (selectedPersonaId) {
      createSessionMutation.mutate(selectedPersonaId);
    }
  };

  // Fetch personas list with filters
  const {
    data: personas,
    isLoading: personasLoading,
    error: personasError,
  } = useQuery({
    queryKey: ['personas', filters.specialty, filters.difficulty],
    queryFn: () => getPersonas(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Fetch selected persona detail
  const {
    data: personaDetail,
    isLoading: detailLoading,
    error: detailError,
  } = useQuery({
    queryKey: ['persona-detail', selectedPersonaId],
    queryFn: () => getPersonaDetail(selectedPersonaId),
    enabled: selectedPersonaId !== '', // Only fetch when persona is selected
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const handleSpecialtyChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setFilters((prev) => ({
      ...prev,
      specialty: (event.target.value as string) || undefined,
    }));
    setSelectedPersonaId(''); // Clear selection when filters change
  };

  const handleDifficultyChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setFilters((prev) => ({
      ...prev,
      difficulty: (event.target.value as string) || undefined,
    }));
    setSelectedPersonaId(''); // Clear selection when filters change
  };

  const handlePersonaChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSelectedPersonaId(event.target.value as string);
  };

  const getDifficultyColor = (
    difficulty: string
  ): 'success' | 'warning' | 'error' | 'default' => {
    switch (difficulty) {
      case 'foundation':
        return 'success';
      case 'intermediate':
        return 'warning';
      case 'advanced':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDifficultyLabel = (difficulty: string): string => {
    const map: Record<string, string> = {
      foundation: 'Foundation (Basic)',
      intermediate: 'Intermediate (Standard)',
      advanced: 'Advanced (Complex)',
    };
    return map[difficulty] || difficulty;
  };

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3, md: 4 } }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          OSCE Practice - Patient Personas
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Select a patient persona to begin AMC Clinical Examination practice.
          All personas are validated with Australian medical guidelines.
        </Typography>
      </Box>

      {/* Filters */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 4 }}>
            <FormControl fullWidth>
              <InputLabel id="specialty-filter-label">Specialty</InputLabel>
              <Select
                labelId="specialty-filter-label"
                id="specialty-filter"
                value={filters.specialty || ''}
                onChange={handleSpecialtyChange}
                label="Specialty"
              >
                <MenuItem value="">All Specialties</MenuItem>
                <MenuItem value="Cardiology">Cardiology</MenuItem>
                <MenuItem value="Emergency">Emergency</MenuItem>
                <MenuItem value="General Practice">General Practice</MenuItem>
                <MenuItem value="Pediatrics">Pediatrics</MenuItem>
                <MenuItem value="Respiratory">Respiratory</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <FormControl fullWidth>
              <InputLabel id="difficulty-filter-label">Difficulty</InputLabel>
              <Select
                labelId="difficulty-filter-label"
                id="difficulty-filter"
                value={filters.difficulty || ''}
                onChange={handleDifficultyChange}
                label="Difficulty"
              >
                <MenuItem value="">All Difficulties</MenuItem>
                <MenuItem value="foundation">Foundation (Basic)</MenuItem>
                <MenuItem value="intermediate">Intermediate (Standard)</MenuItem>
                <MenuItem value="advanced">Advanced (Complex)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <FormControl fullWidth disabled={personasLoading || !personas}>
              <InputLabel id="persona-selector-label">
                Select Patient ({personas?.length || 0} available)
              </InputLabel>
              <Select
                labelId="persona-selector-label"
                id="persona-selector"
                value={selectedPersonaId}
                onChange={handlePersonaChange}
                label={`Select Patient (${personas?.length || 0} available)`}
              >
                <MenuItem value="">
                  <em>Choose a patient...</em>
                </MenuItem>
                {personas?.map((persona) => (
                  <MenuItem key={persona.persona_id} value={persona.persona_id}>
                    {persona.name} - {persona.chief_complaint} ({persona.difficulty_level})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* Loading State - Personas */}
      {personasLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress aria-label="Loading patient personas" />
        </Box>
      )}

      {/* Error State - Personas */}
      {personasError && (
        <Alert severity="error" sx={{ mb: 4 }}>
          Failed to load patient personas. Please try again later.
        </Alert>
      )}

      {/* Empty State */}
      {!personasLoading && !personasError && personas && personas.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No patient personas found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your filters to see available patients
          </Typography>
        </Box>
      )}

      {/* Persona Detail View */}
      {selectedPersonaId && (
        <>
          <Divider sx={{ my: 4 }} />

          {/* Loading State - Detail */}
          {detailLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress aria-label="Loading patient details" />
            </Box>
          )}

          {/* Error State - Detail */}
          {detailError && (
            <Alert severity="error" sx={{ mb: 4 }}>
              Failed to load patient details. Please try again.
            </Alert>
          )}

          {/* Detail Content */}
          {!detailLoading && !detailError && personaDetail && (
            <Box>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mb: 3,
                }}
              >
                <Typography variant="h5" component="h2">
                  Patient Details
                </Typography>
                <Button
                  variant="contained"
                  size="large"
                  color="primary"
                  startIcon={<PlayArrowIcon />}
                  onClick={handleStartSession}
                  disabled={createSessionMutation.isPending}
                  sx={{ minWidth: '200px' }}
                >
                  {createSessionMutation.isPending ? 'Starting...' : 'Start Session'}
                </Button>
              </Box>

              <Grid container spacing={3}>
                {/* Patient Demographics */}
                <Grid size={{ xs: 12, md: 6 }}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Demographics
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Name
                        </Typography>
                        <Typography variant="body1">{personaDetail.name}</Typography>
                      </Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Age / Gender
                        </Typography>
                        <Typography variant="body1">
                          {personaDetail.age} years old, {personaDetail.gender}
                        </Typography>
                      </Box>
                      {personaDetail.occupation && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            Occupation
                          </Typography>
                          <Typography variant="body1">{personaDetail.occupation}</Typography>
                        </Box>
                      )}
                      {personaDetail.cultural_background && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            Cultural Background
                          </Typography>
                          <Typography variant="body1">
                            {personaDetail.cultural_background}
                          </Typography>
                        </Box>
                      )}
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Preferred Language
                        </Typography>
                        <Typography variant="body1">
                          {personaDetail.preferred_language}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Clinical Information */}
                <Grid size={{ xs: 12, md: 6 }}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Clinical Information
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Specialty
                        </Typography>
                        <Typography variant="body1">{personaDetail.specialty}</Typography>
                      </Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Difficulty Level
                        </Typography>
                        <Chip
                          label={formatDifficultyLabel(personaDetail.difficulty_level)}
                          color={getDifficultyColor(personaDetail.difficulty_level)}
                          size="small"
                        />
                      </Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          AMC Blueprint Area
                        </Typography>
                        <Typography variant="body1">
                          {personaDetail.amc_blueprint_area}
                        </Typography>
                      </Box>
                      {personaDetail.estimated_pass_rate !== null && (
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Estimated Pass Rate
                          </Typography>
                          <Typography variant="body1">
                            {(personaDetail.estimated_pass_rate * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                {/* Chief Complaint */}
                <Grid size={{ xs: 12 }}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Chief Complaint
                      </Typography>
                      <Typography variant="body1">{personaDetail.chief_complaint}</Typography>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Opening Statement */}
                <Grid size={{ xs: 12 }}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Opening Statement
                      </Typography>
                      <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                        "{personaDetail.opening_statement}"
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Key Differentials */}
                {personaDetail.key_differentials && personaDetail.key_differentials.length > 0 && (
                  <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Key Differentials
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {personaDetail.key_differentials.map((diff, index) => (
                            <Chip key={index} label={diff} variant="outlined" />
                          ))}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {/* AMC Competencies */}
                {personaDetail.amc_competencies && personaDetail.amc_competencies.length > 0 && (
                  <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          AMC Competencies
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {personaDetail.amc_competencies.map((comp, index) => (
                            <Chip key={index} label={comp} color="primary" variant="outlined" />
                          ))}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </>
      )}

      {/* Instructions (shown when no persona selected) */}
      {!selectedPersonaId && !personasLoading && personas && personas.length > 0 && (
        <Box sx={{ mt: 4, p: 3, bgcolor: 'background.paper', borderRadius: 1 }}>
          <Typography variant="h6" gutterBottom>
            How to Use
          </Typography>
          <Typography variant="body2" paragraph>
            1. Use the filters above to narrow down personas by specialty or difficulty level
          </Typography>
          <Typography variant="body2" paragraph>
            2. Select a patient from the dropdown to view their details
          </Typography>
          <Typography variant="body2">
            3. Review the patient's demographics, chief complaint, and clinical information
            before starting your OSCE practice session
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default OSCEPractice;
