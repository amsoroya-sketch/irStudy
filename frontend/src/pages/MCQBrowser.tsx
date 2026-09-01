/**
 * MCQ Browser Page
 * Browse and filter MCQs with RBAC-based actions
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Pagination,
} from '@mui/material';
import { getMCQs } from '../api/mcqs';
import { PermissionGuard } from '../components/PermissionGuard';
import { Permissions } from '../api/permissions';
import { MCQListParams } from '../types/mcq';

const MCQBrowser: React.FC = () => {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<MCQListParams>({
    skip: 0,
    limit: 20,
    category: undefined,
    difficulty: undefined,
    search: '',
  });

  const [page, setPage] = useState(1);

  useEffect(() => {
    document.title = 'MCQ Browser - AMC Clinical Exam';
  }, []);

  // Fetch MCQs with React Query
  const {
    data: mcqsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['mcqs', filters],
    queryFn: () => getMCQs(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Extract data with safe defaults to prevent runtime errors
  const items = mcqsData?.items ?? [];
  const total = mcqsData?.total ?? 0;

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
    setFilters((prev) => ({
      ...prev,
      skip: (value - 1) * (prev.limit || 20),
    }));
  };

  const handleFilterChange = (key: keyof MCQListParams, value: any) => {
    setPage(1);
    setFilters((prev) => ({
      ...prev,
      [key]: value,
      skip: 0,
    }));
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleFilterChange('search', event.target.value);
  };

  const handleCategoryChange = (event: any) => {
    handleFilterChange('category', event.target.value || undefined);
  };

  const handleDifficultyChange = (event: any) => {
    handleFilterChange('difficulty', event.target.value || undefined);
  };

  const getDifficultyColor = (
    difficulty: string
  ): 'success' | 'warning' | 'error' | 'default' => {
    switch (difficulty) {
      case 'easy':
        return 'success';
      case 'medium':
        return 'warning';
      case 'hard':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3, md: 4 } }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', sm: 'center' }, gap: { xs: 2, sm: 0 } }}>
        <Typography variant="h4" component="h1">
          MCQ Practice Browser
        </Typography>
        <PermissionGuard permission={Permissions.MCQ_CREATE}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/mcqs/create')}
          >
            Create MCQ
          </Button>
        </PermissionGuard>
      </Box>

      {/* Filters */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 4 }}>
            <TextField
              fullWidth
              label="Search"
              placeholder="Search questions..."
              value={filters.search || ''}
              onChange={handleSearchChange}
            />
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={filters.category || ''}
                onChange={handleCategoryChange}
                label="Category"
              >
                <MenuItem value="">All Categories</MenuItem>
                <MenuItem value="Cardiology">Cardiology</MenuItem>
                <MenuItem value="Respiratory">Respiratory</MenuItem>
                <MenuItem value="Psychiatry">Psychiatry</MenuItem>
                <MenuItem value="Surgery">Surgery</MenuItem>
                <MenuItem value="Medicine">Medicine</MenuItem>
                <MenuItem value="ObGyn">ObGyn</MenuItem>
                <MenuItem value="Paediatrics">Paediatrics</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <FormControl fullWidth>
              <InputLabel>Difficulty</InputLabel>
              <Select
                value={filters.difficulty || ''}
                onChange={handleDifficultyChange}
                label="Difficulty"
              >
                <MenuItem value="">All Difficulties</MenuItem>
                <MenuItem value="easy">Easy</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="hard">Hard</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* Loading State */}
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          Failed to load MCQs. Please try again later.
        </Alert>
      )}

      {/* MCQ Grid */}
      {!isLoading && !error && (
        <>
          <Grid container spacing={3}>
            {items.map((mcq) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={mcq.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={mcq.difficulty}
                        color={getDifficultyColor(mcq.difficulty)}
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      <Chip label={mcq.category} variant="outlined" size="small" />
                    </Box>
                    <Typography variant="h6" component="div" gutterBottom>
                      MCQ #{mcq.id}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {mcq.question}
                    </Typography>
                    {mcq.tags && mcq.tags.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        {mcq.tags.slice(0, 3).map((tag, index) => (
                          <Chip key={index} label={tag} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                        ))}
                      </Box>
                    )}
                  </CardContent>
                  <CardActions>
                    <PermissionGuard permission={Permissions.MCQ_ATTEMPT}>
                      <Button
                        size="small"
                        color="primary"
                        onClick={() => navigate(`/mcqs/${mcq.id}/attempt`)}
                      >
                        Attempt
                      </Button>
                    </PermissionGuard>
                    <PermissionGuard permission={Permissions.MCQ_VIEW}>
                      <Button size="small" onClick={() => navigate(`/mcqs/${mcq.id}`)}>
                        View
                      </Button>
                    </PermissionGuard>
                    <PermissionGuard permission={Permissions.MCQ_UPDATE}>
                      <Button size="small" onClick={() => navigate(`/mcqs/${mcq.id}/edit`)}>
                        Edit
                      </Button>
                    </PermissionGuard>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {total > (filters.limit || 20) && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={Math.ceil(total / (filters.limit || 20))}
                page={page}
                onChange={handlePageChange}
                color="primary"
              />
            </Box>
          )}

          {/* Empty State */}
          {items.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No MCQs found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Try adjusting your filters or search query
              </Typography>
            </Box>
          )}
        </>
      )}
    </Container>
  );
};

export default MCQBrowser;
