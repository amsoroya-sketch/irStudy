# PRD_FRONTEND_003: EMR Dashboard Integration

**PRD ID**: PRD_FRONTEND_003_EMR_DASHBOARD_INTEGRATION
**Title**: EMR Practice Metrics Dashboard Integration
**Category**: Frontend - Dashboard Components
**Priority**: P1-High (critical for student progress tracking)
**Owner**: Frontend Engineer (Flutter Desktop Expert)
**Estimated Effort**: 14-18 hours
**Dependencies**:
- PRD_BACKEND_001 (EMR Database Migration - user_progress EMR columns)
- PRD_BACKEND_002 (EMR Session API - session data endpoints)
- PRD_FRONTEND_001 (Epic EMR UI - Epic components for session resume)

**Blocks**:
- PRD_FRONTEND_005 (EMR Analytics Deep Dive - detailed reports)
- PRD_INTEGRATION_002 (Unified Progress Tracking - cross-module analytics)

**Created**: 2026-02-16
**Status**: Ready for Implementation

---

## R - REQUEST (What and Why)

### User Story

**AS A** medical student practicing for AMC Clinical Examination
**I WANT TO** see unified dashboard metrics showing MCQ, OSCE, and EMR practice progress in one place
**SO THAT** I can track my improvement across all practice modes, identify weak areas, and optimize my study plan

### Business Context

**Current State**:
- Existing dashboard shows MCQ and OSCE metrics only (`/frontend/src/components/dashboard/`)
- Components: StatCard (reusable), PerformanceChart (2-line MCQ chart), SpecialtyBreakdown (MCQ accuracy), WeakAreasPanel (MCQ weak areas)
- Dashboard uses Material-UI v7 + Recharts 2.15.4 + TanStack Query v5
- Backend has new `user_progress` EMR columns (PRD_BACKEND_001) but frontend doesn't display them

**Problem**:
- Students can't see EMR practice progress (sessions completed, typing speed, AHPRA compliance rate)
- No unified view of MCQ + OSCE + EMR trends (can't identify which practice mode is improving)
- No EMR-specific weak areas (can't identify which EMR specialties need more practice)
- Recent EMR sessions not visible (can't quickly resume last session)
- EMR system usage unknown (Cerner vs Epic preference data not shown)

**Desired State**:
- Dashboard extended with 6 new EMR metric cards (sessions, avg score, typing WPM, improvement %, AHPRA compliance, time spent)
- Unified progress chart showing 3 lines (MCQ accuracy, OSCE score, EMR validation score) over 4 weeks
- EMR specialty breakdown chart (horizontal bar chart: session count by specialty)
- Recent EMR sessions list (last 5 sessions with Resume/Review actions)
- EMR system usage pie chart (Epic vs Cerner distribution)
- Extended weak areas panel showing EMR weak specialties alongside MCQ weak areas

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Component Reuse** | ≥60% code reused | StatCard: 100%, PerformanceChart: 90%, SpecialtyBreakdown: 80% |
| **API Performance** | Dashboard load <1s (Fix #3) | **PARALLEL** API requests with TanStack Query useQueries |
| **Chart Render Speed** | All charts <500ms | Recharts ResponsiveContainer optimization |
| **Test Coverage** | ≥70% component coverage | Jest + React Testing Library |
| **Accessibility** | WCAG 2.2 AA compliance | Lighthouse score ≥90, keyboard nav, ARIA labels |
| **User Engagement** | 90%+ students use EMR metrics | Analytics tracking |

### Business Value

- **Unified Progress Tracking**: Students see holistic view of AMC preparation (MCQ theory + OSCE clinical skills + EMR documentation)
- **Actionable Insights**: Weak areas panel guides students to specific EMR specialties needing improvement
- **Reduced Friction**: Recent sessions list enables quick resume (reduces "where was I?" friction)
- **System Preference Data**: Usage pie chart helps prioritize Epic vs Cerner development
- **Australian Compliance**: AHPRA compliance metric ensures students meet documentation standards

---

## A - ARCHITECTURE (How It Will Be Built)

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                 EMR Dashboard Integration Architecture                │
└──────────────────────────────────────────────────────────────────────┘

LAYERS:
  │
  ├─► PRESENTATION LAYER (Material-UI v7 Components)
  │   ├─ EMRMetricsGrid (6 StatCards: sessions, avg score, typing WPM,
  │   │                   improvement %, AHPRA compliance, time spent)
  │   ├─ UnifiedProgressChart (3-line chart: MCQ + OSCE + EMR trends)
  │   ├─ EMRSpecialtyChart (horizontal bar chart: session count by specialty)
  │   ├─ RecentEMRSessionsList (MUI Table: last 5 sessions with actions)
  │   ├─ EMRSystemUsagePie (pie chart: Epic vs Cerner distribution)
  │   └─ UnifiedWeakAreasPanel (extended with EMR weak specialties)
  │
  ├─► DATA FETCHING LAYER (TanStack Query v5) - Fix #3: PARALLEL REQUESTS
  │   ├─ **IMPLEMENTED**: useEMRDashboardData hook (see `frontend/src/hooks/useEMRDashboardData.ts`)
  │   ├─ Uses TanStack Query useQueries for parallel API calls
  │   ├─ 4 endpoints fetched simultaneously (not sequential)
  │   ├─ Caching: 2-10min staleTime per endpoint
  │   └─ Performance: <1s dashboard load (vs 2s+ sequential)
  │
  ├─► STATE MANAGEMENT (React 19.2 Hooks)
  │   ├─ useState (chart filters, date range selection)
  │   ├─ useMemo (expensive chart data transformations)
  │   └─ useEffect (session resume navigation)
  │
  └─► BACKEND LAYER (FastAPI Endpoints - FROM PRD_BACKEND_005)
      ├─ GET /api/v1/progress/dashboard/emr (NEW - PRD_BACKEND_005)
      │   Response: {
      │     emr_metrics: { sessions_total, sessions_completed, avg_score,
      │                    avg_typing_wpm, improvement_pct, ahpra_compliance_rate,
      │                    total_time_spent_seconds },
      │     specialty_breakdown: [{ specialty, session_count, avg_score }],
      │     system_usage: { epic_sessions, cerner_sessions }
      │   }
      │
      ├─ GET /api/v1/emr/sessions?limit=5&sort_by=created_at&sort_order=desc (PRD_BACKEND_002)
      │   Response: {
      │     sessions: [{ session_id, patient_name, specialty, emr_system,
      │                  started_at, completed_at, validation_score, is_active }]
      │   }
      │
      ├─ GET /api/v1/progress/weekly-trends/unified?weeks=12 (NEW - PRD_BACKEND_005)
      │   Response: {
      │     trends: [{ week_start, mcq_accuracy, osce_avg_score, emr_avg_score,
      │                mcq_attempts, osce_completions, emr_sessions }]
      │   }
      │
      └─ GET /api/v1/progress/weak-areas/emr?limit=5 (NEW - PRD_BACKEND_005)
          Response: {
            weak_areas: [{ specialty, session_count, avg_score, gap_to_target,
                           recommended_practice_count }]
          }

DESIGN TOKENS (Consistent with existing dashboard):
- Primary: #1976d2 (Material-UI default blue)
- Secondary: #dc004e (Material-UI default pink)
- Success: #4caf50 (green - for improvements)
- Warning: #ff9800 (orange - for weak areas)
- Error: #f44336 (red - for low performance)
- Typography: Roboto (400, 500, 700)
- Spacing: 8px base unit (MUI default)
```

### Parallel API Requests Implementation (Fix #3)

**Problem**: Sequential API calls cause slow dashboard load
- 4 endpoints × 500ms each = 2000ms (2 seconds) total load time
- Poor user experience (long white screen)

**Solution**: TanStack Query useQueries (parallel requests)
```typescript
// File: frontend/src/hooks/useEMRDashboardData.ts (IMPLEMENTED)

export const useEMRDashboardData = (userId: string) => {
  // All 4 queries run in PARALLEL (not sequential)
  return useQueries({
    queries: [
      {
        queryKey: ['emr', 'dashboard', 'metrics', userId],
        queryFn: () => axiosInstance.get('/api/v1/progress/dashboard/emr'),
        staleTime: 5 * 60 * 1000, // 5 minutes
      },
      {
        queryKey: ['emr', 'sessions', 'recent', userId],
        queryFn: () => axiosInstance.get('/api/v1/emr/sessions?limit=10'),
        staleTime: 2 * 60 * 1000, // 2 minutes
      },
      {
        queryKey: ['progress', 'weekly-trends', userId],
        queryFn: () => axiosInstance.get('/api/v1/progress/weekly-trends/unified?weeks=12'),
        staleTime: 10 * 60 * 1000, // 10 minutes
      },
      {
        queryKey: ['progress', 'weak-areas', 'emr', userId],
        queryFn: () => axiosInstance.get('/api/v1/progress/weak-areas/emr?limit=5'),
        staleTime: 5 * 60 * 1000, // 5 minutes
      },
    ],
    combine: (results) => ({
      data: {
        metrics: results[0].data,
        recentSessions: results[1].data,
        weeklyTrends: results[2].data,
        weakAreas: results[3].data,
      },
      isLoading: results.some((r) => r.isLoading),
      isError: results.some((r) => r.isError),
    }),
  });
};

// Usage in EMRDashboard component:
const { data, isLoading, isError } = useEMRDashboardData(userId);

// Performance: max(500ms, 500ms, 500ms, 500ms) = 500ms (achievable!)
```

**Performance Improvement**:
- Before: 2000ms (sequential)
- After: 500-700ms (parallel + caching)
- **70% faster dashboard load**

### Error Boundary Implementation (Fix #5)

**Problem**: API errors crash entire dashboard (white screen of death)

**Solution**: ErrorBoundary component wraps dashboard
```typescript
// File: frontend/src/components/ErrorBoundary.tsx (IMPLEMENTED)

import { ErrorBoundary } from '../components/ErrorBoundary';

<ErrorBoundary>
  <EMRDashboard />
</ErrorBoundary>

// On error: Shows user-friendly error message with reload button
// On success: Renders dashboard normally
```

**User Experience Improvement**:
- Before: White screen → user confused → closes browser
- After: Error message → "Reload Page" button → recovers

---

### Component Architecture

#### Component 1: EMRMetricsGrid (6 StatCards)

```typescript
// File: frontend/src/components/dashboard/EMRMetricsGrid.tsx

import React from 'react';
import { Grid, Skeleton } from '@mui/material';
import StatCard from './StatCard';

interface EMRMetrics {
  sessions_total: number;
  sessions_completed: number;
  avg_validation_score: number;
  avg_typing_wpm: number;
  improvement_percentage: number;
  ahpra_compliance_rate: number;
  total_time_spent_seconds: number;
}

interface EMRMetricsGridProps {
  metrics: EMRMetrics | undefined;
  loading?: boolean;
}

const EMRMetricsGrid: React.FC<EMRMetricsGridProps> = ({ metrics, loading }) => {
  if (loading || !metrics) {
    return (
      <Grid container spacing={3}>
        {[...Array(6)].map((_, i) => (
          <Grid item xs={12} md={4} key={i}>
            <Skeleton variant="rectangular" height={140} />
          </Grid>
        ))}
      </Grid>
    );
  }

  // Calculate derived metrics
  const sessionsCompleted = metrics.sessions_completed;
  const sessionsTotal = metrics.sessions_total;
  const completionRate = sessionsTotal > 0
    ? ((sessionsCompleted / sessionsTotal) * 100).toFixed(1)
    : '0.0';

  const hoursSpent = (metrics.total_time_spent_seconds / 3600).toFixed(1);

  return (
    <Grid container spacing={3}>
      {/* Card 1: Sessions Completed */}
      <Grid item xs={12} md={4}>
        <StatCard
          title="EMR Sessions Completed"
          value={`${sessionsCompleted}/${sessionsTotal}`}
          subtitle={
            sessionsCompleted === sessionsTotal
              ? 'All sessions done!'
              : sessionsCompleted >= sessionsTotal * 0.75
              ? `${sessionsTotal - sessionsCompleted} remaining - great progress!`
              : `${sessionsTotal - sessionsCompleted} remaining`
          }
          color={
            sessionsCompleted === sessionsTotal
              ? 'success'
              : sessionsCompleted >= sessionsTotal * 0.75
              ? 'primary'
              : 'warning'
          }
        />
      </Grid>

      {/* Card 2: Average Validation Score */}
      <Grid item xs={12} md={4}>
        <StatCard
          title="Average Validation Score"
          value={`${metrics.avg_validation_score.toFixed(1)}%`}
          subtitle={
            metrics.avg_validation_score >= 80
              ? 'Excellent - AMC Clinical Exam ready!'
              : metrics.avg_validation_score >= 70
              ? 'Good - keep practicing'
              : 'Needs improvement - review AHPRA guidelines'
          }
          color={
            metrics.avg_validation_score >= 80
              ? 'success'
              : metrics.avg_validation_score >= 70
              ? 'primary'
              : 'error'
          }
        />
      </Grid>

      {/* Card 3: Typing Speed (WPM) */}
      <Grid item xs={12} md={4}>
        <StatCard
          title="Typing Speed (WPM)"
          value={metrics.avg_typing_wpm.toFixed(0)}
          subtitle={
            metrics.avg_typing_wpm >= 50
              ? 'Fast - efficient documentation'
              : metrics.avg_typing_wpm >= 35
              ? 'Good - clinic-ready pace'
              : 'Practice more for speed improvement'
          }
          color={
            metrics.avg_typing_wpm >= 50
              ? 'success'
              : metrics.avg_typing_wpm >= 35
              ? 'primary'
              : 'warning'
          }
        />
      </Grid>

      {/* Card 4: Improvement Percentage */}
      <Grid item xs={12} md={4}>
        <StatCard
          title="Improvement Rate"
          value={`${metrics.improvement_percentage >= 0 ? '+' : ''}${metrics.improvement_percentage.toFixed(1)}%`}
          subtitle={
            metrics.improvement_percentage >= 15
              ? 'Excellent progress - keep it up!'
              : metrics.improvement_percentage >= 5
              ? 'Steady improvement'
              : metrics.improvement_percentage >= 0
              ? 'Slight improvement'
              : 'Recent performance dip - review feedback'
          }
          color={
            metrics.improvement_percentage >= 10
              ? 'success'
              : metrics.improvement_percentage >= 0
              ? 'primary'
              : 'warning'
          }
        />
      </Grid>

      {/* Card 5: AHPRA Compliance Rate */}
      <Grid item xs={12} md={4}>
        <StatCard
          title="AHPRA Compliance Rate"
          value={`${metrics.ahpra_compliance_rate.toFixed(1)}%`}
          subtitle={
            metrics.ahpra_compliance_rate >= 95
              ? 'Outstanding - meets all Australian standards'
              : metrics.ahpra_compliance_rate >= 85
              ? 'Good compliance - minor improvements needed'
              : 'Review AHPRA documentation guidelines'
          }
          color={
            metrics.ahpra_compliance_rate >= 95
              ? 'success'
              : metrics.ahpra_compliance_rate >= 85
              ? 'primary'
              : 'error'
          }
        />
      </Grid>

      {/* Card 6: Total Time Spent */}
      <Grid item xs={12} md={4}>
        <StatCard
          title="Total Practice Time"
          value={`${hoursSpent}h`}
          subtitle={
            parseFloat(hoursSpent) >= 10
              ? 'Significant practice - excellent dedication!'
              : parseFloat(hoursSpent) >= 5
              ? 'Good practice volume'
              : 'Consider more practice time for mastery'
          }
          color="primary"
        />
      </Grid>
    </Grid>
  );
};

export default EMRMetricsGrid;
```

**Effort Estimate**: 2-3 hours (mostly configuration, StatCard reuse)

---

#### Component 2: UnifiedProgressChart (3-Line Chart)

```typescript
// File: frontend/src/components/dashboard/UnifiedProgressChart.tsx

import React from 'react';
import { Card, CardContent, Typography, Box, ToggleButtonGroup, ToggleButton } from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface UnifiedTrend {
  week_start: string; // ISO 8601 datetime
  mcq_accuracy: number; // 0-100
  osce_avg_score: number; // 0-100
  emr_avg_score: number; // 0-100
  mcq_attempts: number;
  osce_completions: number;
  emr_sessions: number;
}

interface UnifiedProgressChartProps {
  trends: UnifiedTrend[];
  loading?: boolean;
}

const UnifiedProgressChart: React.FC<UnifiedProgressChartProps> = ({ trends, loading }) => {
  const [timeRange, setTimeRange] = React.useState<'4weeks' | '8weeks' | '12weeks'>('4weeks');

  // Format data for Recharts
  const chartData = React.useMemo(() => {
    return trends.map((trend) => ({
      week: new Date(trend.week_start).toLocaleDateString('en-AU', {
        month: '2-digit',
        day: '2-digit',
      }),
      mcq: trend.mcq_accuracy,
      osce: trend.osce_avg_score,
      emr: trend.emr_avg_score,
      // Keep raw data for tooltip
      mcq_attempts: trend.mcq_attempts,
      osce_completions: trend.osce_completions,
      emr_sessions: trend.emr_sessions,
    }));
  }, [trends]);

  // Custom tooltip showing all metrics
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;

    return (
      <Box
        sx={{
          backgroundColor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1,
          p: 1.5,
          boxShadow: 2,
        }}
      >
        <Typography variant="body2" fontWeight="bold" gutterBottom>
          Week of {data.week}
        </Typography>
        <Typography variant="body2" color="primary">
          MCQ: {data.mcq.toFixed(1)}% ({data.mcq_attempts} attempts)
        </Typography>
        <Typography variant="body2" color="secondary">
          OSCE: {data.osce.toFixed(1)}% ({data.osce_completions} stations)
        </Typography>
        <Typography variant="body2" sx={{ color: '#ff9800' }}>
          EMR: {data.emr.toFixed(1)}% ({data.emr_sessions} sessions)
        </Typography>
      </Box>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Unified Progress Trends
          </Typography>
          <Box sx={{ width: '100%', height: 350, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">Loading chart data...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Unified Progress Trends
          </Typography>
          <ToggleButtonGroup
            value={timeRange}
            exclusive
            onChange={(e, newValue) => newValue && setTimeRange(newValue)}
            size="small"
            aria-label="Time range selection"
          >
            <ToggleButton value="4weeks" aria-label="4 weeks">
              4 Weeks
            </ToggleButton>
            <ToggleButton value="8weeks" aria-label="8 weeks">
              8 Weeks
            </ToggleButton>
            <ToggleButton value="12weeks" aria-label="12 weeks">
              12 Weeks
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        <Box sx={{ width: '100%', height: 350, mt: 2 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="week"
                label={{ value: 'Week Starting', position: 'insideBottom', offset: -5 }}
              />
              <YAxis
                label={{ value: 'Performance Score (%)', angle: -90, position: 'insideLeft' }}
                domain={[0, 100]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                formatter={(value) => {
                  if (value === 'mcq') return 'MCQ Accuracy';
                  if (value === 'osce') return 'OSCE Score';
                  if (value === 'emr') return 'EMR Validation Score';
                  return value;
                }}
              />
              {/* Line 1: MCQ Accuracy (Blue) */}
              <Line
                type="monotone"
                dataKey="mcq"
                stroke="#1976d2"
                strokeWidth={2}
                dot={{ r: 5 }}
                activeDot={{ r: 7 }}
                name="mcq"
              />
              {/* Line 2: OSCE Score (Pink) */}
              <Line
                type="monotone"
                dataKey="osce"
                stroke="#dc004e"
                strokeWidth={2}
                dot={{ r: 5 }}
                activeDot={{ r: 7 }}
                name="osce"
              />
              {/* Line 3: EMR Validation Score (Orange) */}
              <Line
                type="monotone"
                dataKey="emr"
                stroke="#ff9800"
                strokeWidth={2}
                dot={{ r: 5 }}
                activeDot={{ r: 7 }}
                name="emr"
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>

        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Track your progress across all AMC Clinical Examination preparation modes
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default UnifiedProgressChart;
```

**Effort Estimate**: 3-4 hours (extend existing PerformanceChart with 3rd line + toggle)

---

#### Component 3: EMRSpecialtyChart (Horizontal Bar Chart)

```typescript
// File: frontend/src/components/dashboard/EMRSpecialtyChart.tsx

import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface EMRSpecialtyData {
  specialty: string;
  session_count: number;
  avg_score: number;
}

interface EMRSpecialtyChartProps {
  specialties: EMRSpecialtyData[];
  loading?: boolean;
}

const EMRSpecialtyChart: React.FC<EMRSpecialtyChartProps> = ({ specialties, loading }) => {
  // Sort by session count (highest to lowest)
  const sortedData = React.useMemo(() => {
    return [...specialties]
      .sort((a, b) => b.session_count - a.session_count)
      .slice(0, 8) // Show top 8 specialties
      .map((specialty) => ({
        specialty: specialty.specialty
          .split('_')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' '),
        sessions: specialty.session_count,
        avgScore: specialty.avg_score,
      }));
  }, [specialties]);

  // Color bars based on session count (gradient from light to dark blue)
  const getBarColor = (sessions: number, maxSessions: number) => {
    const intensity = sessions / maxSessions;
    // Blue gradient: light #90caf9 to dark #1565c0
    if (intensity >= 0.75) return '#1565c0';
    if (intensity >= 0.5) return '#1976d2';
    if (intensity >= 0.25) return '#42a5f5';
    return '#90caf9';
  };

  const maxSessions = Math.max(...sortedData.map((d) => d.sessions), 1);

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            EMR Practice by Specialty
          </Typography>
          <Box sx={{ width: '100%', height: 350, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">Loading specialty data...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          EMR Practice by Specialty
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Session count by medical specialty (Australian focus)
        </Typography>

        <Box sx={{ width: '100%', height: 350, mt: 2 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={sortedData}
              layout="vertical"
              margin={{
                top: 5,
                right: 30,
                left: 120, // Space for specialty names
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                label={{ value: 'Sessions Completed', position: 'insideBottom', offset: -5 }}
              />
              <YAxis
                type="category"
                dataKey="specialty"
                tick={{ fontSize: 12 }}
                width={110}
              />
              <Tooltip
                formatter={(value: number, name: string, props: any) => {
                  if (name === 'sessions') {
                    return [
                      `${value} sessions (Avg Score: ${props.payload.avgScore.toFixed(1)}%)`,
                      'Sessions',
                    ];
                  }
                  return [value, name];
                }}
              />
              <Bar dataKey="sessions" name="sessions" radius={[0, 4, 4, 0]}>
                {sortedData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.sessions, maxSessions)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>

        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Focus on specialties with fewer sessions to build comprehensive AMC Clinical Exam preparation
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default EMRSpecialtyChart;
```

**Effort Estimate**: 2-3 hours (adapt SpecialtyBreakdown to horizontal layout + session count metric)

---

#### Component 4: RecentEMRSessionsList (MUI Table)

```typescript
// File: frontend/src/components/dashboard/RecentEMRSessionsList.tsx

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  Box,
  Skeleton,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { useNavigate } from 'react-router-dom';

interface RecentEMRSession {
  session_id: string;
  patient_name: string;
  specialty: string;
  emr_system: 'cerner' | 'epic';
  started_at: string; // ISO 8601
  completed_at: string | null; // ISO 8601 or null if active
  validation_score: number | null; // 0-100 or null if not validated
  is_active: boolean;
}

interface RecentEMRSessionsListProps {
  sessions: RecentEMRSession[];
  loading?: boolean;
}

const RecentEMRSessionsList: React.FC<RecentEMRSessionsListProps> = ({ sessions, loading }) => {
  const navigate = useNavigate();

  const handleResumeSession = (sessionId: string) => {
    navigate(`/emr/practice/${sessionId}`);
  };

  const handleReviewSession = (sessionId: string) => {
    navigate(`/emr/review/${sessionId}`);
  };

  const formatDate = (isoString: string) => {
    return new Date(isoString).toLocaleDateString('en-AU', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatSpecialty = (specialty: string) => {
    return specialty
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent EMR Sessions
          </Typography>
          <Box sx={{ mt: 2 }}>
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={60} sx={{ mb: 1 }} />
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent EMR Sessions
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Your last 5 EMR practice sessions - resume in progress or review completed
        </Typography>

        {sessions.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No EMR sessions yet. Start your first session to begin practicing!
            </Typography>
            <Button
              variant="contained"
              sx={{ mt: 2 }}
              onClick={() => navigate('/emr/practice/start')}
            >
              Start First EMR Session
            </Button>
          </Box>
        ) : (
          <TableContainer sx={{ mt: 2 }}>
            <Table size="small" aria-label="Recent EMR sessions table">
              <TableHead>
                <TableRow>
                  <TableCell>Patient</TableCell>
                  <TableCell>Specialty</TableCell>
                  <TableCell>System</TableCell>
                  <TableCell>Started</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sessions.map((session) => (
                  <TableRow
                    key={session.session_id}
                    hover
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      <Typography variant="body2" fontWeight="medium">
                        {session.patient_name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatSpecialty(session.specialty)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={session.emr_system === 'epic' ? 'Epic' : 'Cerner'}
                        size="small"
                        color={session.emr_system === 'epic' ? 'primary' : 'secondary'}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(session.started_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {session.is_active ? (
                        <Chip label="In Progress" size="small" color="warning" />
                      ) : session.validation_score !== null ? (
                        <Chip
                          label={`Completed (${session.validation_score.toFixed(0)}%)`}
                          size="small"
                          color={session.validation_score >= 80 ? 'success' : 'default'}
                        />
                      ) : (
                        <Chip label="Completed" size="small" color="default" />
                      )}
                    </TableCell>
                    <TableCell align="right">
                      {session.is_active ? (
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<PlayArrowIcon />}
                          onClick={() => handleResumeSession(session.session_id)}
                          aria-label={`Resume session with ${session.patient_name}`}
                        >
                          Resume
                        </Button>
                      ) : (
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<VisibilityIcon />}
                          onClick={() => handleReviewSession(session.session_id)}
                          aria-label={`Review session with ${session.patient_name}`}
                        >
                          Review
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );
};

export default RecentEMRSessionsList;
```

**Effort Estimate**: 2-3 hours (MUI Table + navigation logic)

---

#### Component 5: EMRSystemUsagePie (Pie Chart)

```typescript
// File: frontend/src/components/dashboard/EMRSystemUsagePie.tsx

import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface EMRSystemUsage {
  epic_sessions: number;
  cerner_sessions: number;
}

interface EMRSystemUsagePieProps {
  usage: EMRSystemUsage | undefined;
  loading?: boolean;
}

const EMRSystemUsagePie: React.FC<EMRSystemUsagePieProps> = ({ usage, loading }) => {
  const chartData = React.useMemo(() => {
    if (!usage) return [];

    return [
      { name: 'Epic', value: usage.epic_sessions, color: '#D4C5A9' },
      { name: 'Cerner', value: usage.cerner_sessions, color: '#FF4500' },
    ].filter((item) => item.value > 0); // Only show systems with sessions
  }, [usage]);

  const totalSessions = usage
    ? usage.epic_sessions + usage.cerner_sessions
    : 0;

  // Custom label showing percentage
  const renderLabel = (entry: any) => {
    const percent = ((entry.value / totalSessions) * 100).toFixed(0);
    return `${entry.name}: ${percent}%`;
  };

  if (loading || !usage) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            EMR System Usage
          </Typography>
          <Box sx={{ width: '100%', height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">Loading usage data...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (totalSessions === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            EMR System Usage
          </Typography>
          <Box sx={{ width: '100%', height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">
              No EMR sessions yet. Start practicing to see system usage breakdown.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          EMR System Usage
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Distribution of practice sessions across Epic and Cerner systems
        </Typography>

        <Box sx={{ width: '100%', height: 300, mt: 2 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderLabel}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number) => [
                  `${value} sessions (${((value / totalSessions) * 100).toFixed(1)}%)`,
                  'Sessions',
                ]}
              />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </Box>

        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Total EMR sessions: {totalSessions}
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block">
            Australian hospitals use both Epic and Cerner systems
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default EMRSystemUsagePie;
```

**Effort Estimate**: 1-2 hours (Recharts PieChart configuration)

---

#### Component 6: UnifiedWeakAreasPanel (Extended)

```typescript
// File: frontend/src/components/dashboard/UnifiedWeakAreasPanel.tsx

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Alert,
  Stack,
  Box,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import type { WeakArea } from '../../types/dashboard';

interface EMRWeakArea {
  specialty: string;
  avg_score: number;
  session_count: number;
  recommended_sessions: number;
}

interface UnifiedWeakAreasPanelProps {
  mcqWeakAreas: WeakArea[];
  emrWeakAreas: EMRWeakArea[];
  loading?: boolean;
}

const UnifiedWeakAreasPanel: React.FC<UnifiedWeakAreasPanelProps> = ({
  mcqWeakAreas,
  emrWeakAreas,
  loading,
}) => {
  const [activeTab, setActiveTab] = React.useState<'mcq' | 'emr'>('mcq');

  const formatSpecialty = (specialty: string) => {
    return specialty
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: 'mcq' | 'emr') => {
    setActiveTab(newValue);
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <WarningIcon color="warning" sx={{ mr: 1 }} />
            <Typography variant="h6">Areas for Improvement</Typography>
          </Box>
          <Typography color="text.secondary">Loading weak areas...</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <WarningIcon color="warning" sx={{ mr: 1 }} />
          <Typography variant="h6">Areas for Improvement</Typography>
        </Box>

        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="Weak areas by practice mode"
          sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}
        >
          <Tab
            label={`MCQ (${mcqWeakAreas.length})`}
            value="mcq"
            aria-label="MCQ weak areas"
          />
          <Tab
            label={`EMR (${emrWeakAreas.length})`}
            value="emr"
            aria-label="EMR weak areas"
          />
        </Tabs>

        {/* MCQ Weak Areas Tab */}
        {activeTab === 'mcq' && (
          <>
            {mcqWeakAreas.length === 0 ? (
              <Alert severity="success" icon={<CheckCircleIcon />}>
                <Typography variant="body2">
                  Great work! No MCQ weak areas identified. All specialties above 70% accuracy!
                </Typography>
              </Alert>
            ) : (
              <Stack spacing={2}>
                {mcqWeakAreas.map((area, index) => (
                  <Alert key={index} severity="warning" sx={{ textAlign: 'left' }}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      {formatSpecialty(area.specialty)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Accuracy: {area.accuracy_rate.toFixed(1)}% ({area.total_attempts} attempts)
                    </Typography>
                    <Typography variant="body2">
                      <strong>Recommendation:</strong> Review{' '}
                      {area.recommended_study_cards > 0
                        ? `${area.recommended_study_cards} study cards`
                        : 'more materials'}{' '}
                      and practice 10 more MCQs in this specialty.
                    </Typography>
                  </Alert>
                ))}
              </Stack>
            )}

            {mcqWeakAreas.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  MCQ weak areas: accuracy below 70% with at least 5 attempts
                </Typography>
              </Box>
            )}
          </>
        )}

        {/* EMR Weak Areas Tab */}
        {activeTab === 'emr' && (
          <>
            {emrWeakAreas.length === 0 ? (
              <Alert severity="success" icon={<CheckCircleIcon />}>
                <Typography variant="body2">
                  Excellent! No EMR weak areas identified. All specialties scoring above 70%!
                </Typography>
              </Alert>
            ) : (
              <Stack spacing={2}>
                {emrWeakAreas.map((area, index) => (
                  <Alert key={index} severity="warning" sx={{ textAlign: 'left' }}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      {formatSpecialty(area.specialty)} - EMR Documentation
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Average Score: {area.avg_score.toFixed(1)}% ({area.session_count} sessions)
                    </Typography>
                    <Typography variant="body2">
                      <strong>Recommendation:</strong> Complete{' '}
                      {area.recommended_sessions} more EMR sessions in {formatSpecialty(area.specialty)}.
                      Focus on AHPRA-compliant SOAP notes and Australian terminology (paracetamol, salbutamol).
                    </Typography>
                  </Alert>
                ))}
              </Stack>
            )}

            {emrWeakAreas.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  EMR weak areas: average validation score below 70% with at least 3 sessions
                </Typography>
              </Box>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default UnifiedWeakAreasPanel;
```

**Effort Estimate**: 2-3 hours (extend existing WeakAreasPanel with tabs + EMR section)

---

### API Integration Hooks

```typescript
// File: frontend/src/hooks/useEMRDashboard.ts

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

interface EMRMetrics {
  sessions_total: number;
  sessions_completed: number;
  avg_validation_score: number;
  avg_typing_wpm: number;
  improvement_percentage: number;
  ahpra_compliance_rate: number;
  total_time_spent_seconds: number;
}

interface EMRSpecialtyData {
  specialty: string;
  session_count: number;
  avg_score: number;
}

interface EMRSystemUsage {
  epic_sessions: number;
  cerner_sessions: number;
}

interface EMRDashboardData {
  emr_metrics: EMRMetrics;
  specialty_breakdown: EMRSpecialtyData[];
  system_usage: EMRSystemUsage;
}

export function useEMRDashboardData() {
  return useQuery<EMRDashboardData>({
    queryKey: ['emr', 'dashboard'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/progress/dashboard/emr');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes (dashboard data doesn't change frequently)
    retry: 2,
  });
}

// Recent EMR sessions hook
interface RecentEMRSession {
  session_id: string;
  patient_name: string;
  specialty: string;
  emr_system: 'cerner' | 'epic';
  started_at: string;
  completed_at: string | null;
  validation_score: number | null;
  is_active: boolean;
}

export function useRecentEMRSessions(limit: number = 5) {
  return useQuery<{ sessions: RecentEMRSession[] }>({
    queryKey: ['emr', 'sessions', 'recent', limit],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/emr/sessions', {
        params: {
          limit,
          sort_by: 'created_at',
          sort_order: 'desc',
        },
      });
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes (recent sessions may change)
    retry: 2,
  });
}

// Unified weekly trends hook (MCQ + OSCE + EMR)
interface UnifiedTrend {
  week_start: string;
  mcq_accuracy: number;
  osce_avg_score: number;
  emr_avg_score: number;
  mcq_attempts: number;
  osce_completions: number;
  emr_sessions: number;
}

export function useUnifiedWeeklyTrends(weeks: number = 4) {
  return useQuery<{ trends: UnifiedTrend[] }>({
    queryKey: ['progress', 'weekly-trends', 'unified', weeks],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/progress/weekly-trends/unified', {
        params: { weeks },
      });
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}

// EMR weak areas hook
interface EMRWeakArea {
  specialty: string;
  avg_score: number;
  session_count: number;
  recommended_sessions: number;
}

export function useEMRWeakAreas() {
  return useQuery<{ weak_areas: EMRWeakArea[] }>({
    queryKey: ['emr', 'weak-areas'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/progress/weak-areas/emr');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}
```

**Effort Estimate**: 1-2 hours (TanStack Query hooks configuration)

---

### TypeScript Interfaces

```typescript
// File: frontend/src/types/emr-dashboard.ts

/**
 * EMR Dashboard Analytics Types
 * TypeScript interfaces for EMR-specific dashboard components
 */

// ===== EMR Metrics =====

export interface EMRMetrics {
  sessions_total: number;
  sessions_completed: number;
  avg_validation_score: number; // 0-100
  avg_typing_wpm: number; // Words per minute
  improvement_percentage: number; // Can be negative if recent performance declined
  ahpra_compliance_rate: number; // 0-100 (percentage of AHPRA-compliant documentation)
  total_time_spent_seconds: number; // Total practice time
}

// ===== EMR Specialty Performance =====

export interface EMRSpecialtyData {
  specialty: string; // e.g., "cardiology", "respiratory", "emergency"
  session_count: number; // Number of sessions completed in this specialty
  avg_score: number; // 0-100 average validation score
}

// ===== EMR System Usage =====

export interface EMRSystemUsage {
  epic_sessions: number; // Sessions using Epic EHR
  cerner_sessions: number; // Sessions using Cerner PowerChart
}

// ===== Recent EMR Session =====

export interface RecentEMRSession {
  session_id: string; // UUID
  patient_name: string; // Mock patient name (e.g., "John Smith")
  specialty: string; // Patient's primary specialty
  emr_system: 'cerner' | 'epic'; // EMR system used
  started_at: string; // ISO 8601 datetime
  completed_at: string | null; // ISO 8601 or null if still active
  validation_score: number | null; // 0-100 or null if not yet validated
  is_active: boolean; // True if session still in progress
}

// ===== Unified Weekly Trend =====

export interface UnifiedTrend {
  week_start: string; // ISO 8601 datetime (Monday of week)
  mcq_accuracy: number; // 0-100 (MCQ accuracy rate for week)
  osce_avg_score: number; // 0-100 (OSCE average score for week)
  emr_avg_score: number; // 0-100 (EMR validation average for week)
  mcq_attempts: number; // Number of MCQ attempts
  osce_completions: number; // Number of OSCE stations completed
  emr_sessions: number; // Number of EMR sessions completed
}

// ===== EMR Weak Area =====

export interface EMRWeakArea {
  specialty: string; // Specialty needing improvement
  avg_score: number; // 0-100 (below 70% threshold)
  session_count: number; // Number of sessions completed (at least 3)
  recommended_sessions: number; // Number of additional sessions recommended
}

// ===== Dashboard Response Types =====

export interface EMRDashboardData {
  emr_metrics: EMRMetrics;
  specialty_breakdown: EMRSpecialtyData[];
  system_usage: EMRSystemUsage;
}

export interface RecentEMRSessionsResponse {
  sessions: RecentEMRSession[];
}

export interface UnifiedWeeklyTrendsResponse {
  weeks: number; // Number of weeks requested
  trends: UnifiedTrend[];
}

export interface EMRWeakAreasResponse {
  threshold: number; // Score threshold (default 70%)
  min_sessions: number; // Minimum sessions required (default 3)
  weak_areas: EMRWeakArea[];
}
```

**Effort Estimate**: 30 minutes (TypeScript interface definitions)

---

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **UI Components** | Material-UI | v7.3.7 | Component library (Card, Grid, Table, Chip) |
| **Charts** | Recharts | v2.15.4 | LineChart, BarChart, PieChart |
| **Framework** | React | 19.2.0 | UI rendering |
| **Type Safety** | TypeScript | 5.9.3 | Type checking |
| **API Client** | TanStack Query | v5.90.20 | Data fetching, caching, stale-while-revalidate |
| **Routing** | React Router | v7.13.0 | Navigation (resume session) |
| **Testing** | Jest + RTL | v16.3.2 | Unit/integration tests |
| **Build Tool** | Vite | v7.2.4 | Fast development server |

---

## L - LOOP (Iterative Development Plan)

### Development Phases

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Phase 1   │────►│   Phase 2   │────►│   Phase 3   │
│  Metrics    │     │    Charts   │     │    Polish   │
│   (3-4h)    │     │    (6-8h)   │     │    (5-6h)   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │
      ▼                    ▼                    ▼
EMRMetricsGrid      UnifiedProgressChart   Testing +
+ API hooks         + EMRSpecialtyChart    Accessibility +
                    + RecentSessions        Performance
                    + SystemUsagePie
                    + UnifiedWeakAreas
```

### Phase 1: Foundation - EMR Metrics Grid (3-4 hours)

**Goal**: Create EMR metrics grid (6 StatCards) with API integration

**Tasks**:
1. **Create EMRMetricsGrid component** (1.5h)
   - Reuse StatCard component (100% reuse)
   - Configure 6 cards (sessions, avg score, typing WPM, improvement %, AHPRA compliance, time spent)
   - Add loading skeletons (MUI Skeleton component)

2. **Create API hooks** (1h)
   - `useEMRDashboardData` hook (TanStack Query)
   - Configure staleTime (5 minutes), retry logic (2 attempts)
   - Error handling (display error state in grid)

3. **Create TypeScript interfaces** (0.5h)
   - `EMRMetrics`, `EMRDashboardData` types
   - Match backend PRD_BACKEND_001 schema

4. **Test metrics grid** (1h)
   - Unit test: StatCard rendering with mock data
   - Integration test: API hook data fetching
   - Manual test: Load dashboard, verify metrics accuracy

**Validation Gate**:
- [ ] EMRMetricsGrid renders all 6 cards correctly
- [ ] API hook fetches data successfully (mocked API)
- [ ] Loading state shows skeletons
- [ ] Error state shows user-friendly message
- [ ] TypeScript compiles (0 errors)
- [ ] Tests pass (100% pass rate)

**Deliverables**:
- `frontend/src/components/dashboard/EMRMetricsGrid.tsx` (120 lines)
- `frontend/src/hooks/useEMRDashboard.ts` (80 lines)
- `frontend/src/types/emr-dashboard.ts` (100 lines)
- `frontend/src/components/dashboard/__tests__/EMRMetricsGrid.test.tsx` (150 lines)

---

### Phase 2: Charts and Tables (6-8 hours)

**Goal**: Implement all charts, recent sessions table, and unified weak areas panel

**Tasks**:
1. **Create UnifiedProgressChart component** (2h)
   - Extend existing PerformanceChart with 3rd line (EMR validation score)
   - Add time range toggle (4/8/12 weeks)
   - Custom tooltip showing all 3 metrics
   - Legend labels (MCQ Accuracy, OSCE Score, EMR Validation Score)

2. **Create EMRSpecialtyChart component** (1.5h)
   - Horizontal bar chart (Recharts BarChart layout="vertical")
   - Sort by session count (descending)
   - Color gradient (light to dark blue based on session count)
   - Tooltip showing avg score

3. **Create RecentEMRSessionsList component** (2h)
   - MUI Table (responsive, accessible)
   - Action buttons (Resume for active, Review for completed)
   - Navigation logic (React Router)
   - Empty state (no sessions yet)

4. **Create EMRSystemUsagePie component** (1h)
   - Recharts PieChart (Epic vs Cerner)
   - Custom labels (percentage)
   - Color scheme (Epic beige, Cerner orange)
   - Handle edge case (0 sessions)

5. **Create UnifiedWeakAreasPanel component** (1.5h)
   - Extend existing WeakAreasPanel
   - Add Tabs (MCQ vs EMR)
   - Reuse Alert components
   - Format specialty names

6. **Create additional API hooks** (1h)
   - `useRecentEMRSessions` hook
   - `useUnifiedWeeklyTrends` hook
   - `useEMRWeakAreas` hook

**Validation Gate**:
- [ ] All 5 components render correctly with mock data
- [ ] UnifiedProgressChart shows 3 lines (MCQ, OSCE, EMR)
- [ ] EMRSpecialtyChart sorts correctly (highest to lowest)
- [ ] RecentEMRSessionsList navigation works (test Resume/Review)
- [ ] EMRSystemUsagePie handles 0 sessions gracefully
- [ ] UnifiedWeakAreasPanel tabs switch correctly
- [ ] API hooks configured with correct staleTime/retry
- [ ] TypeScript compiles (0 errors)

**Deliverables**:
- `frontend/src/components/dashboard/UnifiedProgressChart.tsx` (200 lines)
- `frontend/src/components/dashboard/EMRSpecialtyChart.tsx` (150 lines)
- `frontend/src/components/dashboard/RecentEMRSessionsList.tsx` (180 lines)
- `frontend/src/components/dashboard/EMRSystemUsagePie.tsx` (130 lines)
- `frontend/src/components/dashboard/UnifiedWeakAreasPanel.tsx` (180 lines)
- Updated `frontend/src/hooks/useEMRDashboard.ts` (+100 lines)

---

### Phase 3: Testing, Accessibility, Performance (5-6 hours)

**Goal**: Achieve WCAG 2.2 AA compliance, comprehensive testing, production readiness

**Tasks**:
1. **Write component tests** (3h)
   - Jest + React Testing Library
   - Test all 6 components (EMRMetricsGrid, UnifiedProgressChart, EMRSpecialtyChart, RecentEMRSessionsList, EMRSystemUsagePie, UnifiedWeakAreasPanel)
   - Test user interactions (click, navigation, tab switching)
   - Test API hook data fetching (mock TanStack Query)
   - Target: ≥70% coverage

2. **Implement accessibility** (1.5h)
   - ARIA labels on all charts and tables
   - Keyboard navigation (Tab, Enter, Arrow keys)
   - Screen reader testing (NVDA/JAWS - at least basic testing)
   - Focus indicators (visible on all interactive elements)
   - Color contrast verification (Lighthouse)

3. **Performance optimization** (1h)
   - Memoize expensive chart data transformations (useMemo)
   - Debounce time range selection (prevent excessive re-renders)
   - Lazy load charts (React.lazy + Suspense)
   - Verify API staleTime prevents excessive refetching

4. **Documentation** (0.5h)
   - Component prop documentation (JSDoc comments)
   - Usage examples in main dashboard component
   - Update README with EMR dashboard sections

**Validation Gate**:
- [ ] Test coverage ≥70% (unit + integration)
- [ ] Test pass rate 100% (zero-tolerance)
- [ ] Lighthouse accessibility score ≥90
- [ ] Keyboard navigation works (all charts/tables accessible)
- [ ] Screen reader compatible (basic NVDA test)
- [ ] Performance: Dashboard load <2s, chart render <500ms
- [ ] Documentation complete (JSDoc + usage examples)

**Deliverables**:
- `frontend/src/components/dashboard/__tests__/` (6 test files, ~900 lines total)
- Updated components with ARIA labels and keyboard handlers
- Performance optimizations (useMemo, debounce)
- Component documentation (JSDoc comments)

---

## P - PLAN (Detailed Task Breakdown)

### Phase 1 Tasks (Foundation)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **1.1** | Create TypeScript interfaces for EMR dashboard data | 30min | Frontend Engineer | None |
| **1.2** | Create `useEMRDashboardData` hook (TanStack Query) | 1h | Frontend Engineer | Task 1.1 |
| **1.3** | Create EMRMetricsGrid component (6 StatCards) | 1.5h | Frontend Engineer | Task 1.1, existing StatCard |
| **1.4** | Add loading skeletons to EMRMetricsGrid | 30min | Frontend Engineer | Task 1.3 |
| **1.5** | Write unit tests for EMRMetricsGrid | 1h | Frontend Engineer | Task 1.3 |
| **1.6** | Manual test: Verify metrics display with mock data | 30min | Frontend Engineer | Task 1.3 |

**Phase 1 Total**: 5 hours

---

### Phase 2 Tasks (Charts and Tables)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **2.1** | Create UnifiedProgressChart component (3-line chart) | 2h | Frontend Engineer | Phase 1 |
| **2.2** | Add time range toggle to UnifiedProgressChart | 30min | Frontend Engineer | Task 2.1 |
| **2.3** | Create EMRSpecialtyChart component (horizontal bar chart) | 1.5h | Frontend Engineer | Phase 1 |
| **2.4** | Create RecentEMRSessionsList component (MUI Table) | 2h | Frontend Engineer | Phase 1 |
| **2.5** | Add navigation logic to RecentEMRSessionsList | 30min | Frontend Engineer | Task 2.4 |
| **2.6** | Create EMRSystemUsagePie component (pie chart) | 1h | Frontend Engineer | Phase 1 |
| **2.7** | Create UnifiedWeakAreasPanel component (tabs) | 1.5h | Frontend Engineer | Phase 1 |
| **2.8** | Create additional API hooks (recent sessions, trends, weak areas) | 1h | Frontend Engineer | Phase 1 |
| **2.9** | Manual test: Verify all charts render correctly | 1h | Frontend Engineer | Tasks 2.1-2.7 |

**Phase 2 Total**: 11 hours

---

### Phase 3 Tasks (Testing, Accessibility, Performance)

| Task | Description | Effort | Owner | Dependencies |
|------|-------------|--------|-------|--------------|
| **3.1** | Write unit tests for UnifiedProgressChart | 45min | Frontend Engineer | Task 2.1 |
| **3.2** | Write unit tests for EMRSpecialtyChart | 30min | Frontend Engineer | Task 2.3 |
| **3.3** | Write unit tests for RecentEMRSessionsList | 45min | Frontend Engineer | Task 2.4 |
| **3.4** | Write unit tests for EMRSystemUsagePie | 30min | Frontend Engineer | Task 2.6 |
| **3.5** | Write unit tests for UnifiedWeakAreasPanel | 30min | Frontend Engineer | Task 2.7 |
| **3.6** | Add ARIA labels to all charts and tables | 1h | Frontend Engineer | Phase 2 |
| **3.7** | Implement keyboard navigation for all components | 1h | Frontend Engineer | Phase 2 |
| **3.8** | Run Lighthouse accessibility audit, fix issues | 1h | Frontend Engineer | Phase 2 |
| **3.9** | Performance optimization (useMemo, debounce) | 1h | Frontend Engineer | Phase 2 |
| **3.10** | Manual accessibility testing (NVDA screen reader) | 1h | Frontend Engineer + QA | All above |
| **3.11** | Write component documentation (JSDoc + README) | 30min | Frontend Engineer | All above |

**Phase 3 Total**: 8.5 hours

---

### Total Effort Summary

| Phase | Tasks | Effort | Key Deliverable |
|-------|-------|--------|-----------------|
| **Phase 1** | Foundation | 5h | EMRMetricsGrid + API hooks |
| **Phase 2** | Charts & Tables | 11h | 5 components + unified weak areas |
| **Phase 3** | Testing & Accessibility | 8.5h | WCAG compliance + ≥70% coverage |
| **TOTAL** | - | **24.5h** | Production-ready EMR dashboard |

**Note**: Original estimate was 14-18 hours. Revised to 24.5 hours after detailed task breakdown. The increase accounts for:
- Comprehensive component testing (6 components): +3h
- Accessibility implementation (ARIA, keyboard nav, screen reader): +2h
- Performance optimization (memoization, debounce): +1h
- Additional API hooks (recent sessions, trends, weak areas): +0.5h

**Risk Mitigation**: If behind schedule, Phase 3 can be split (testing first, then accessibility in follow-up sprint).

---

## H - HANDOFF (Acceptance Criteria and Delivery)

### Acceptance Criteria

#### Functional Requirements

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **F1** | EMR Metrics Grid | All 6 StatCards display correctly with accurate data | Manual test + unit test |
| **F2** | Unified Progress Chart | 3 lines (MCQ, OSCE, EMR) render correctly | Visual inspection + snapshot test |
| **F3** | EMR Specialty Chart | Horizontal bar chart sorted by session count | Chart data validation test |
| **F4** | Recent Sessions List | Last 5 sessions displayed, Resume/Review actions work | Navigation integration test |
| **F5** | System Usage Pie | Epic vs Cerner distribution shows correct percentages | Chart data validation test |
| **F6** | Unified Weak Areas Panel | MCQ and EMR tabs switch correctly, data displays accurately | Tab interaction test |
| **F7** | API Integration | All 4 API hooks fetch data successfully | Mock API integration test |
| **F8** | Loading States | Skeletons show during data fetch | Manual test (throttle network) |
| **F9** | Error Handling | User-friendly error messages on API failure | Simulate API error test |
| **F10** | Navigation | Resume session navigates to correct EMR practice page | React Router navigation test |

#### Quality Requirements

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **Q1** | Test coverage | ≥70% component coverage | Jest coverage report |
| **Q2** | Test pass rate | 100% (zero-tolerance) | `npm test` (all tests pass) |
| **Q3** | Type safety | 0 TypeScript errors | `npx tsc --noEmit` |
| **Q4** | Linting | 0 ESLint errors | `npm run lint` |
| **Q5** | Code quality | No code smells (complexity, duplication) | SonarQube analysis |
| **Q6** | Component reuse | ≥60% code reused from existing dashboard | Manual code review |

#### Performance Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| **P1** | Dashboard load | <2 seconds (LCP) | Lighthouse performance score |
| **P2** | Chart render | <500ms per chart | React DevTools Profiler |
| **P3** | API staleTime | 5 minutes (prevents excessive refetch) | TanStack Query DevTools |
| **P4** | Data transformation | Memoized (no re-computation on re-render) | React DevTools Profiler |

#### Accessibility Requirements (WCAG 2.2 AA)

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **A1** | Lighthouse score | ≥90 accessibility score | Lighthouse audit |
| **A2** | Keyboard navigation | All charts/tables accessible via keyboard | Manual keyboard-only testing |
| **A3** | Screen reader | All content readable by NVDA/JAWS | Manual screen reader testing |
| **A4** | Focus indicators | Visible focus ring on all interactive elements | Visual inspection |
| **A5** | Color contrast | 4.5:1 ratio for text, 3:1 for large text | Lighthouse + manual check |
| **A6** | ARIA labels | All charts, buttons, tables have proper labels | axe-core automated scan |
| **A7** | Semantic HTML | Proper heading hierarchy, table structure | HTML validator |

#### Australian Medical Compliance

| ID | Requirement | Success Criteria | Validation Method |
|----|-------------|------------------|-------------------|
| **C1** | Terminology | Australian drug names (paracetamol, salbutamol, adrenaline) | Content review |
| **C2** | Guidelines | References eTG/AMH/AHPRA in recommendations | Content review |
| **C3** | AMC Focus | AMC Clinical Examination focus (not ICRP) | Content review |
| **C4** | Units | SI units only (mmol/L, g/L, °C) | Data format validation |
| **C5** | AHPRA Compliance | AHPRA compliance metric displayed prominently | Visual inspection |

---

### Testing Requirements

#### Unit Tests (Jest + React Testing Library)

```typescript
// File: frontend/src/components/dashboard/__tests__/EMRMetricsGrid.test.tsx

import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import EMRMetricsGrid from '../EMRMetricsGrid';

const queryClient = new QueryClient();

const mockMetrics = {
  sessions_total: 20,
  sessions_completed: 15,
  avg_validation_score: 82.5,
  avg_typing_wpm: 45,
  improvement_percentage: 12.3,
  ahpra_compliance_rate: 88.7,
  total_time_spent_seconds: 36000, // 10 hours
};

describe('EMRMetricsGrid', () => {
  it('renders all 6 StatCards with correct values', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <EMRMetricsGrid metrics={mockMetrics} />
      </QueryClientProvider>
    );

    // Card 1: Sessions completed
    expect(screen.getByText('EMR Sessions Completed')).toBeInTheDocument();
    expect(screen.getByText('15/20')).toBeInTheDocument();

    // Card 2: Average score
    expect(screen.getByText('Average Validation Score')).toBeInTheDocument();
    expect(screen.getByText('82.5%')).toBeInTheDocument();

    // Card 3: Typing speed
    expect(screen.getByText('Typing Speed (WPM)')).toBeInTheDocument();
    expect(screen.getByText('45')).toBeInTheDocument();

    // Card 4: Improvement
    expect(screen.getByText('Improvement Rate')).toBeInTheDocument();
    expect(screen.getByText('+12.3%')).toBeInTheDocument();

    // Card 5: AHPRA compliance
    expect(screen.getByText('AHPRA Compliance Rate')).toBeInTheDocument();
    expect(screen.getByText('88.7%')).toBeInTheDocument();

    // Card 6: Time spent
    expect(screen.getByText('Total Practice Time')).toBeInTheDocument();
    expect(screen.getByText('10.0h')).toBeInTheDocument();
  });

  it('shows loading skeletons when loading', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <EMRMetricsGrid metrics={undefined} loading={true} />
      </QueryClientProvider>
    );

    // Should show 6 skeletons
    const skeletons = screen.getAllByTestId('skeleton');
    expect(skeletons).toHaveLength(6);
  });

  it('displays correct color based on performance', () => {
    const highPerformanceMetrics = {
      ...mockMetrics,
      sessions_completed: 20,
      avg_validation_score: 95,
    };

    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <EMRMetricsGrid metrics={highPerformanceMetrics} />
      </QueryClientProvider>
    );

    // Sessions completed card should be green (success)
    const sessionsCard = screen.getByText('15/20').closest('.MuiCard-root');
    expect(sessionsCard).toHaveStyle({ color: '#4caf50' }); // success color

    // Low performance test
    const lowPerformanceMetrics = {
      ...mockMetrics,
      avg_validation_score: 55,
    };

    rerender(
      <QueryClientProvider client={queryClient}>
        <EMRMetricsGrid metrics={lowPerformanceMetrics} />
      </QueryClientProvider>
    );

    // Should show error color for low score
    expect(screen.getByText('55.0%')).toBeInTheDocument();
  });
});

// File: frontend/src/components/dashboard/__tests__/UnifiedProgressChart.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import UnifiedProgressChart from '../UnifiedProgressChart';

const mockTrends = [
  {
    week_start: '2026-01-20T00:00:00Z',
    mcq_accuracy: 75,
    osce_avg_score: 80,
    emr_avg_score: 70,
    mcq_attempts: 50,
    osce_completions: 3,
    emr_sessions: 2,
  },
  {
    week_start: '2026-01-27T00:00:00Z',
    mcq_accuracy: 78,
    osce_avg_score: 82,
    emr_avg_score: 75,
    mcq_attempts: 55,
    osce_completions: 4,
    emr_sessions: 3,
  },
  {
    week_start: '2026-02-03T00:00:00Z',
    mcq_accuracy: 80,
    osce_avg_score: 85,
    emr_avg_score: 78,
    mcq_attempts: 60,
    osce_completions: 5,
    emr_sessions: 4,
  },
  {
    week_start: '2026-02-10T00:00:00Z',
    mcq_accuracy: 82,
    osce_avg_score: 88,
    emr_avg_score: 82,
    mcq_attempts: 65,
    osce_completions: 6,
    emr_sessions: 5,
  },
];

describe('UnifiedProgressChart', () => {
  it('renders chart with 3 lines (MCQ, OSCE, EMR)', () => {
    render(<UnifiedProgressChart trends={mockTrends} />);

    expect(screen.getByText('Unified Progress Trends')).toBeInTheDocument();

    // Check legend labels
    expect(screen.getByText('MCQ Accuracy')).toBeInTheDocument();
    expect(screen.getByText('OSCE Score')).toBeInTheDocument();
    expect(screen.getByText('EMR Validation Score')).toBeInTheDocument();
  });

  it('switches time range on toggle button click', () => {
    render(<UnifiedProgressChart trends={mockTrends} />);

    const eightWeeksButton = screen.getByRole('button', { name: '8 weeks' });
    fireEvent.click(eightWeeksButton);

    // Should update time range (would trigger API refetch in real app)
    expect(eightWeeksButton).toHaveAttribute('aria-pressed', 'true');
  });

  it('shows loading state', () => {
    render(<UnifiedProgressChart trends={[]} loading={true} />);

    expect(screen.getByText('Loading chart data...')).toBeInTheDocument();
  });

  it('displays custom tooltip on hover', async () => {
    render(<UnifiedProgressChart trends={mockTrends} />);

    // Recharts tooltip simulation (test with snapshot or visual regression)
    // In real test, use user interaction library to simulate chart hover
  });
});

// File: frontend/src/components/dashboard/__tests__/RecentEMRSessionsList.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RecentEMRSessionsList from '../RecentEMRSessionsList';

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const mockSessions = [
  {
    session_id: 'session-1',
    patient_name: 'John Smith',
    specialty: 'cardiology',
    emr_system: 'epic' as const,
    started_at: '2026-02-15T10:30:00Z',
    completed_at: null,
    validation_score: null,
    is_active: true,
  },
  {
    session_id: 'session-2',
    patient_name: 'Jane Doe',
    specialty: 'respiratory',
    emr_system: 'cerner' as const,
    started_at: '2026-02-14T14:00:00Z',
    completed_at: '2026-02-14T15:30:00Z',
    validation_score: 85,
    is_active: false,
  },
];

describe('RecentEMRSessionsList', () => {
  it('renders table with recent sessions', () => {
    render(
      <BrowserRouter>
        <RecentEMRSessionsList sessions={mockSessions} />
      </BrowserRouter>
    );

    expect(screen.getByText('Recent EMR Sessions')).toBeInTheDocument();
    expect(screen.getByText('John Smith')).toBeInTheDocument();
    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
  });

  it('shows Resume button for active sessions', () => {
    render(
      <BrowserRouter>
        <RecentEMRSessionsList sessions={mockSessions} />
      </BrowserRouter>
    );

    const resumeButton = screen.getByRole('button', { name: /Resume session with John Smith/ });
    expect(resumeButton).toBeInTheDocument();
  });

  it('shows Review button for completed sessions', () => {
    render(
      <BrowserRouter>
        <RecentEMRSessionsList sessions={mockSessions} />
      </BrowserRouter>
    );

    const reviewButton = screen.getByRole('button', { name: /Review session with Jane Doe/ });
    expect(reviewButton).toBeInTheDocument();
  });

  it('navigates to session page on Resume click', () => {
    render(
      <BrowserRouter>
        <RecentEMRSessionsList sessions={mockSessions} />
      </BrowserRouter>
    );

    const resumeButton = screen.getByRole('button', { name: /Resume session with John Smith/ });
    fireEvent.click(resumeButton);

    expect(mockNavigate).toHaveBeenCalledWith('/emr/practice/session-1');
  });

  it('shows empty state when no sessions', () => {
    render(
      <BrowserRouter>
        <RecentEMRSessionsList sessions={[]} />
      </BrowserRouter>
    );

    expect(screen.getByText(/No EMR sessions yet/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Start First EMR Session/ })).toBeInTheDocument();
  });

  it('displays validation score badge for completed sessions', () => {
    render(
      <BrowserRouter>
        <RecentEMRSessionsList sessions={mockSessions} />
      </BrowserRouter>
    );

    expect(screen.getByText('Completed (85%)')).toBeInTheDocument();
  });
});
```

**Minimum Test Cases**:
- [ ] EMRMetricsGrid: Renders all 6 cards, loading state, color based on performance
- [ ] UnifiedProgressChart: 3 lines render, time range toggle works, custom tooltip
- [ ] EMRSpecialtyChart: Horizontal bars sorted correctly, color gradient applied
- [ ] RecentEMRSessionsList: Resume/Review buttons work, navigation, empty state
- [ ] EMRSystemUsagePie: Pie chart renders, handles 0 sessions, percentage labels
- [ ] UnifiedWeakAreasPanel: Tabs switch, MCQ/EMR data displays correctly

#### Integration Tests

```typescript
// File: frontend/src/__tests__/EMRDashboard.integration.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import EMRDashboard from '../pages/EMRDashboard';

const server = setupServer(
  rest.get('/api/v1/progress/dashboard/emr', (req, res, ctx) => {
    return res(
      ctx.json({
        emr_metrics: {
          sessions_total: 20,
          sessions_completed: 15,
          avg_validation_score: 82.5,
          avg_typing_wpm: 45,
          improvement_percentage: 12.3,
          ahpra_compliance_rate: 88.7,
          total_time_spent_seconds: 36000,
        },
        specialty_breakdown: [
          { specialty: 'cardiology', session_count: 5, avg_score: 85 },
          { specialty: 'respiratory', session_count: 4, avg_score: 80 },
        ],
        system_usage: {
          epic_sessions: 10,
          cerner_sessions: 5,
        },
      })
    );
  }),
  rest.get('/api/v1/emr/sessions', (req, res, ctx) => {
    return res(
      ctx.json({
        sessions: [
          {
            session_id: 'session-1',
            patient_name: 'John Smith',
            specialty: 'cardiology',
            emr_system: 'epic',
            started_at: '2026-02-15T10:30:00Z',
            completed_at: null,
            validation_score: null,
            is_active: true,
          },
        ],
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const queryClient = new QueryClient();

describe('EMR Dashboard Integration', () => {
  it('loads all dashboard components successfully', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <EMRDashboard />
        </BrowserRouter>
      </QueryClientProvider>
    );

    // Wait for API data to load
    await waitFor(() => {
      expect(screen.getByText('EMR Sessions Completed')).toBeInTheDocument();
    });

    // Check metrics grid loaded
    expect(screen.getByText('15/20')).toBeInTheDocument();
    expect(screen.getByText('82.5%')).toBeInTheDocument();

    // Check charts loaded
    expect(screen.getByText('Unified Progress Trends')).toBeInTheDocument();
    expect(screen.getByText('EMR Practice by Specialty')).toBeInTheDocument();

    // Check recent sessions loaded
    expect(screen.getByText('Recent EMR Sessions')).toBeInTheDocument();
    expect(screen.getByText('John Smith')).toBeInTheDocument();
  });

  it('handles API error gracefully', async () => {
    server.use(
      rest.get('/api/v1/progress/dashboard/emr', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Internal server error' }));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <EMRDashboard />
        </BrowserRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/error loading dashboard/i)).toBeInTheDocument();
    });
  });
});
```

---

### Documentation Deliverables

#### 1. Component API Documentation

**File**: `frontend/src/components/dashboard/README-EMR.md`

```markdown
# EMR Dashboard Components

Material-UI components for EMR practice metrics dashboard.

## Components

### EMRMetricsGrid

Displays 6 EMR metric cards (sessions, avg score, typing WPM, improvement, AHPRA compliance, time spent).

**Props**:
- `metrics: EMRMetrics | undefined` - EMR metrics data
- `loading?: boolean` - Loading state

**Example**:
```tsx
import { useEMRDashboardData } from '../hooks/useEMRDashboard';
import EMRMetricsGrid from './EMRMetricsGrid';

const { data, isLoading } = useEMRDashboardData();

<EMRMetricsGrid metrics={data?.emr_metrics} loading={isLoading} />
```

### UnifiedProgressChart

3-line chart showing MCQ, OSCE, and EMR progress trends over 4-12 weeks.

**Props**:
- `trends: UnifiedTrend[]` - Weekly trend data
- `loading?: boolean` - Loading state

**Example**:
```tsx
import { useUnifiedWeeklyTrends } from '../hooks/useEMRDashboard';
import UnifiedProgressChart from './UnifiedProgressChart';

const { data, isLoading } = useUnifiedWeeklyTrends(4);

<UnifiedProgressChart trends={data?.trends || []} loading={isLoading} />
```

### EMRSpecialtyChart

Horizontal bar chart showing session count by medical specialty.

**Props**:
- `specialties: EMRSpecialtyData[]` - Specialty breakdown data
- `loading?: boolean` - Loading state

**Example**:
```tsx
import { useEMRDashboardData } from '../hooks/useEMRDashboard';
import EMRSpecialtyChart from './EMRSpecialtyChart';

const { data, isLoading } = useEMRDashboardData();

<EMRSpecialtyChart specialties={data?.specialty_breakdown || []} loading={isLoading} />
```

### RecentEMRSessionsList

MUI Table showing last 5 EMR sessions with Resume/Review actions.

**Props**:
- `sessions: RecentEMRSession[]` - Recent sessions data
- `loading?: boolean` - Loading state

**Example**:
```tsx
import { useRecentEMRSessions } from '../hooks/useEMRDashboard';
import RecentEMRSessionsList from './RecentEMRSessionsList';

const { data, isLoading } = useRecentEMRSessions(5);

<RecentEMRSessionsList sessions={data?.sessions || []} loading={isLoading} />
```

### EMRSystemUsagePie

Pie chart showing Epic vs Cerner EMR system usage distribution.

**Props**:
- `usage: EMRSystemUsage | undefined` - System usage data
- `loading?: boolean` - Loading state

**Example**:
```tsx
import { useEMRDashboardData } from '../hooks/useEMRDashboard';
import EMRSystemUsagePie from './EMRSystemUsagePie';

const { data, isLoading } = useEMRDashboardData();

<EMRSystemUsagePie usage={data?.system_usage} loading={isLoading} />
```

### UnifiedWeakAreasPanel

Tabbed panel showing MCQ and EMR weak areas with recommendations.

**Props**:
- `mcqWeakAreas: WeakArea[]` - MCQ weak areas
- `emrWeakAreas: EMRWeakArea[]` - EMR weak areas
- `loading?: boolean` - Loading state

**Example**:
```tsx
import { useWeakAreas, useEMRWeakAreas } from '../hooks/useEMRDashboard';
import UnifiedWeakAreasPanel from './UnifiedWeakAreasPanel';

const { data: mcqData } = useWeakAreas();
const { data: emrData } = useEMRWeakAreas();

<UnifiedWeakAreasPanel
  mcqWeakAreas={mcqData?.weak_areas || []}
  emrWeakAreas={emrData?.weak_areas || []}
/>
```

## API Hooks

All hooks use TanStack Query with 5-minute staleTime and 2 retry attempts.

### useEMRDashboardData

Fetches EMR metrics, specialty breakdown, and system usage.

```tsx
const { data, isLoading, error } = useEMRDashboardData();

// data: { emr_metrics, specialty_breakdown, system_usage }
```

### useRecentEMRSessions

Fetches last N EMR sessions.

```tsx
const { data, isLoading, error } = useRecentEMRSessions(5);

// data: { sessions: RecentEMRSession[] }
```

### useUnifiedWeeklyTrends

Fetches unified MCQ + OSCE + EMR weekly trends.

```tsx
const { data, isLoading, error } = useUnifiedWeeklyTrends(4);

// data: { trends: UnifiedTrend[] }
```

### useEMRWeakAreas

Fetches EMR weak areas (specialties below 70% avg score).

```tsx
const { data, isLoading, error } = useEMRWeakAreas();

// data: { weak_areas: EMRWeakArea[] }
```

## Accessibility

All components are WCAG 2.2 AA compliant:
- Keyboard navigation supported (Tab, Enter, Arrow keys)
- ARIA labels on all charts, tables, buttons
- Screen reader compatible (tested with NVDA)
- Color contrast ≥4.5:1

## Testing

Run component tests:
```bash
npm test -- dashboard
```

Run accessibility tests:
```bash
npm test -- accessibility
```
```

---

### Deployment Checklist

**Pre-Deployment**:
- [ ] All component tests pass (≥70% coverage)
- [ ] Test pass rate 100% (zero-tolerance)
- [ ] Lighthouse accessibility score ≥90
- [ ] TypeScript compiles with 0 errors
- [ ] ESLint passes with 0 errors
- [ ] Component reuse ≥60% (StatCard, PerformanceChart pattern)
- [ ] Code review approved (Frontend Lead)
- [ ] Manual accessibility testing complete (NVDA/JAWS)

**Deployment Steps**:
1. [ ] Merge PR to `main` branch
2. [ ] Deploy to staging environment
3. [ ] Run smoke tests (dashboard loads, all components render)
4. [ ] Verify API integration (backend endpoints working)
5. [ ] Performance testing (dashboard load <2s, chart render <500ms)
6. [ ] Deploy to production
7. [ ] Monitor error logs (first 24 hours)
8. [ ] Update IMPLEMENTATION_STATUS.md (mark PRD_FRONTEND_003 complete)

**Post-Deployment**:
- [ ] Monitor dashboard load time (Lighthouse CI)
- [ ] Monitor API call frequency (TanStack Query DevTools)
- [ ] Collect user feedback (student testing session)
- [ ] Fix any critical bugs within 48 hours

---

### Success Validation

**Definition of Done**:

✅ **Functional**:
- All 6 components render correctly with production data
- EMRMetricsGrid displays all 6 StatCards with accurate metrics
- UnifiedProgressChart shows 3 lines (MCQ, OSCE, EMR)
- EMRSpecialtyChart sorted correctly by session count
- RecentEMRSessionsList navigation working (Resume/Review)
- EMRSystemUsagePie handles Epic vs Cerner distribution
- UnifiedWeakAreasPanel tabs switch correctly (MCQ/EMR)

✅ **Quality**:
- Test coverage ≥70%
- Test pass rate 100%
- 0 TypeScript errors
- 0 ESLint errors
- Component reuse ≥60%

✅ **Performance**:
- Dashboard load <2 seconds (LCP)
- Chart render <500ms per chart
- API staleTime prevents excessive refetching (5 minutes)
- Data transformations memoized (no unnecessary re-computation)

✅ **Accessibility**:
- Lighthouse score ≥90
- WCAG 2.2 AA compliant
- Keyboard navigation working (all charts/tables accessible)
- Screen reader compatible (NVDA tested)
- Color contrast ≥4.5:1

✅ **Design**:
- Consistent with existing dashboard (Material-UI v7 theme)
- Recharts configuration matches existing charts
- Responsive layout (works on 1280x720 minimum)

**Acceptance Sign-Off**:
- [ ] Frontend Engineer: Code complete, tests passing
- [ ] PM Coordinator: Requirements met, documentation complete
- [ ] Designer: Visual consistency approved
- [ ] QA: Accessibility testing passed
- [ ] Backend Engineer: API endpoints ready (PRD_BACKEND_001, PRD_BACKEND_002)

---

## Related PRDs

**Depends On**:
- PRD_BACKEND_001: EMR Database Migration (needs user_progress EMR columns)
- PRD_BACKEND_002: EMR Session API (needs session endpoints for recent sessions list)
- PRD_FRONTEND_001: Epic EMR UI (needs Epic components for session resume navigation)

**Blocks**:
- PRD_FRONTEND_005: EMR Analytics Deep Dive (needs dashboard metrics for detailed reports)
- PRD_INTEGRATION_002: Unified Progress Tracking (needs unified progress chart architecture)

**Integrates With**:
- PRD_FRONTEND_002: Cerner UI Components (similar dashboard integration needed for Cerner)
- PRD_BACKEND_003: EMR Validation API (validation scores shown in recent sessions)

---

## Appendices

### Appendix A: API Request/Response Examples

```json
// GET /api/v1/progress/dashboard/emr
// Response: EMR Dashboard Data

{
  "emr_metrics": {
    "sessions_total": 20,
    "sessions_completed": 15,
    "avg_validation_score": 82.5,
    "avg_typing_wpm": 45,
    "improvement_percentage": 12.3,
    "ahpra_compliance_rate": 88.7,
    "total_time_spent_seconds": 36000
  },
  "specialty_breakdown": [
    {
      "specialty": "cardiology",
      "session_count": 5,
      "avg_score": 85.2
    },
    {
      "specialty": "respiratory",
      "session_count": 4,
      "avg_score": 80.5
    },
    {
      "specialty": "emergency",
      "session_count": 3,
      "avg_score": 78.9
    },
    {
      "specialty": "gastroenterology",
      "session_count": 2,
      "avg_score": 75.0
    },
    {
      "specialty": "neurology",
      "session_count": 1,
      "avg_score": 70.0
    }
  ],
  "system_usage": {
    "epic_sessions": 10,
    "cerner_sessions": 5
  }
}

// GET /api/v1/emr/sessions?limit=5&sort_by=created_at&sort_order=desc
// Response: Recent EMR Sessions

{
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440001",
      "patient_name": "John Smith",
      "specialty": "cardiology",
      "emr_system": "epic",
      "started_at": "2026-02-15T10:30:00Z",
      "completed_at": null,
      "validation_score": null,
      "is_active": true
    },
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440002",
      "patient_name": "Jane Doe",
      "specialty": "respiratory",
      "emr_system": "cerner",
      "started_at": "2026-02-14T14:00:00Z",
      "completed_at": "2026-02-14T15:30:00Z",
      "validation_score": 85.3,
      "is_active": false
    },
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440003",
      "patient_name": "Bob Johnson",
      "specialty": "emergency",
      "emr_system": "epic",
      "started_at": "2026-02-13T09:00:00Z",
      "completed_at": "2026-02-13T10:45:00Z",
      "validation_score": 78.9,
      "is_active": false
    },
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440004",
      "patient_name": "Alice Brown",
      "specialty": "gastroenterology",
      "emr_system": "cerner",
      "started_at": "2026-02-12T11:30:00Z",
      "completed_at": "2026-02-12T13:00:00Z",
      "validation_score": 82.1,
      "is_active": false
    },
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440005",
      "patient_name": "Charlie Wilson",
      "specialty": "neurology",
      "emr_system": "epic",
      "started_at": "2026-02-11T15:00:00Z",
      "completed_at": "2026-02-11T16:30:00Z",
      "validation_score": 70.0,
      "is_active": false
    }
  ]
}

// GET /api/v1/progress/weekly-trends/unified?weeks=4
// Response: Unified Weekly Trends (MCQ + OSCE + EMR)

{
  "weeks": 4,
  "trends": [
    {
      "week_start": "2026-01-20T00:00:00Z",
      "mcq_accuracy": 75.5,
      "osce_avg_score": 80.2,
      "emr_avg_score": 70.8,
      "mcq_attempts": 50,
      "osce_completions": 3,
      "emr_sessions": 2
    },
    {
      "week_start": "2026-01-27T00:00:00Z",
      "mcq_accuracy": 78.3,
      "osce_avg_score": 82.5,
      "emr_avg_score": 75.4,
      "mcq_attempts": 55,
      "osce_completions": 4,
      "emr_sessions": 3
    },
    {
      "week_start": "2026-02-03T00:00:00Z",
      "mcq_accuracy": 80.1,
      "osce_avg_score": 85.0,
      "emr_avg_score": 78.2,
      "mcq_attempts": 60,
      "osce_completions": 5,
      "emr_sessions": 4
    },
    {
      "week_start": "2026-02-10T00:00:00Z",
      "mcq_accuracy": 82.7,
      "osce_avg_score": 88.3,
      "emr_avg_score": 82.5,
      "mcq_attempts": 65,
      "osce_completions": 6,
      "emr_sessions": 5
    }
  ]
}

// GET /api/v1/progress/weak-areas/emr
// Response: EMR Weak Areas

{
  "threshold": 70.0,
  "min_sessions": 3,
  "weak_areas": [
    {
      "specialty": "neurology",
      "avg_score": 68.5,
      "session_count": 3,
      "recommended_sessions": 5
    },
    {
      "specialty": "gastroenterology",
      "avg_score": 65.2,
      "session_count": 4,
      "recommended_sessions": 3
    }
  ]
}
```

### Appendix B: Component File Structure

```
frontend/src/
├── components/
│   └── dashboard/
│       ├── EMRMetricsGrid.tsx (NEW - 120 lines)
│       ├── UnifiedProgressChart.tsx (NEW - 200 lines)
│       ├── EMRSpecialtyChart.tsx (NEW - 150 lines)
│       ├── RecentEMRSessionsList.tsx (NEW - 180 lines)
│       ├── EMRSystemUsagePie.tsx (NEW - 130 lines)
│       ├── UnifiedWeakAreasPanel.tsx (NEW - 180 lines)
│       ├── StatCard.tsx (EXISTING - 100% reuse)
│       ├── PerformanceChart.tsx (EXISTING - reference for UnifiedProgressChart)
│       ├── SpecialtyBreakdown.tsx (EXISTING - reference for EMRSpecialtyChart)
│       ├── WeakAreasPanel.tsx (EXISTING - reference for UnifiedWeakAreasPanel)
│       ├── README-EMR.md (NEW - documentation)
│       └── __tests__/
│           ├── EMRMetricsGrid.test.tsx (NEW - 150 lines)
│           ├── UnifiedProgressChart.test.tsx (NEW - 120 lines)
│           ├── EMRSpecialtyChart.test.tsx (NEW - 100 lines)
│           ├── RecentEMRSessionsList.test.tsx (NEW - 180 lines)
│           ├── EMRSystemUsagePie.test.tsx (NEW - 80 lines)
│           └── UnifiedWeakAreasPanel.test.tsx (NEW - 120 lines)
│
├── hooks/
│   └── useEMRDashboard.ts (NEW - 180 lines)
│
├── types/
│   └── emr-dashboard.ts (NEW - 100 lines)
│
└── __tests__/
    └── EMRDashboard.integration.test.tsx (NEW - 200 lines)

TOTAL NEW FILES: 14
TOTAL NEW LINES: ~2,200 lines
```

### Appendix C: Backend API Requirements

**New Endpoints Needed** (to be implemented in PRD_BACKEND_001, PRD_BACKEND_002):

1. **GET /api/v1/progress/dashboard/emr**
   - Returns: EMR metrics, specialty breakdown, system usage
   - Auth: JWT required
   - Performance: <200ms (indexed queries)

2. **GET /api/v1/emr/sessions** (with filters)
   - Query params: `limit`, `sort_by`, `sort_order`, `is_active`
   - Returns: List of EMR sessions
   - Auth: JWT required
   - Performance: <200ms (indexed queries)

3. **GET /api/v1/progress/weekly-trends/unified**
   - Query params: `weeks` (default 4)
   - Returns: Unified MCQ + OSCE + EMR trends
   - Auth: JWT required
   - Performance: <500ms (aggregated queries)

4. **GET /api/v1/progress/weak-areas/emr**
   - Query params: `threshold` (default 70), `min_sessions` (default 3)
   - Returns: EMR weak areas
   - Auth: JWT required
   - Performance: <200ms (indexed queries)

---

**End of PRD_FRONTEND_003**

**Next Steps**: After this PRD is approved, coordinate with backend team to implement API endpoints (PRD_BACKEND_001, PRD_BACKEND_002), then begin frontend implementation.

**Total Frontend PRDs**: 2 of 5 complete (40%)
**Total Project PRDs**: 7 of 14 complete (50%)

**Last Updated**: 2026-02-16
**Document Status**: Ready for Implementation
**Version**: 1.0
