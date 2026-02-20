# PRD: TASK_008 - Performance Dashboard
**Product Requirements Document**

---

## Document Metadata
- **PRD ID**: TASK_008
- **Product Name**: irStudy - AMC Medical Education Platform
- **Feature**: Performance Dashboard with Exam Readiness Prediction
- **Version**: 1.0
- **Date**: 2026-02-15
- **Author**: Project Manager Coordinator
- **Status**: Ready for Implementation
- **Priority**: P1 (High - Student Progress Tracking)

---

## Executive Summary

### Problem Statement
Medical students need comprehensive visibility into their study progress, weak areas, and exam readiness. The current dashboard components (30% complete) exist but are not integrated with backend APIs and lack key features like exam readiness prediction and weekly trends analysis.

### Solution Overview
Create a world-class Performance Dashboard with:
- Real-time performance metrics (MCQ accuracy, OSCE completions, study cards)
- Exam Readiness Gauge (0-100% algorithm-based prediction)
- Weekly trends visualization (progress over time)
- Specialty breakdown (performance by medical specialty)
- Weak areas detection with recommendations
- AMC 15-mark rubric breakdown (OSCE performance)
- Backend API integration via TanStack Query

### Success Metrics
- **User Engagement**: >70% of students view dashboard weekly
- **Exam Readiness Accuracy**: ±10% prediction accuracy vs actual exam performance
- **Data Freshness**: Dashboard updates within 5 seconds of new attempt
- **Performance**: <2.5s page load time (including charts)
- **Test Coverage**: 75%+ for dashboard components

---

## User Stories & Requirements

### US-008-001: Performance Summary Cards
**As a** medical student
**I want to** see high-level performance metrics at a glance
**So that** I can quickly assess my overall progress

**Acceptance Criteria**:
- [ ] 4 summary stat cards displayed:
  1. MCQ Attempts (count + accuracy rate)
  2. OSCE Completions (count + average score)
  3. Study Cards (reviewed count + retention rate)
  4. Weak Areas (count + recommendation)
- [ ] Each card shows icon, title, value, subtitle
- [ ] Color-coded by performance (green >80%, yellow 60-80%, red <60%)
- [ ] Responsive grid (1 col mobile, 2 cols tablet, 4 cols desktop)
- [ ] Loading skeleton while fetching data

**Component Implementation**:
```typescript
// frontend/src/components/dashboard/StatCard.tsx (EXISTS - 100%)
interface StatCardProps {
  title: string;
  value: number;
  subtitle: string;
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  icon: React.ReactElement;
}
```

**Backend API Integration**:
```typescript
// frontend/src/hooks/useDashboard.ts (NEW)
export const useDashboard = () => {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/progress/dashboard');
      return response.data as DashboardResponse;
    },
    staleTime: 5 * 60 * 1000,  // 5 minutes
  });
};

// Response schema
interface DashboardResponse {
  total_mcq_attempts: number;
  mcq_accuracy_rate: number;  // 0-100
  total_osce_completions: number;
  study_cards_reviewed: number;
  study_card_retention_rate: number;
  specialty_breakdown: SpecialtyPerformance[];
  weak_areas: WeakArea[];
}
```

---

### US-008-002: Weekly Trends Chart
**As a** medical student
**I want to** see my progress trends over time
**So that** I can visualize improvement and identify plateaus

**Acceptance Criteria**:
- [ ] Line chart showing weekly trends (default: last 4 weeks)
- [ ] Metrics: MCQ accuracy, attempts, study cards reviewed
- [ ] X-axis: Week starting dates
- [ ] Y-axis: Percentage (accuracy) and count (attempts)
- [ ] Interactive tooltip on hover (shows exact values)
- [ ] Responsive chart (height adapts to viewport)
- [ ] Color-coded lines (accuracy=blue, attempts=green)

**Implementation**:
```typescript
// frontend/src/components/dashboard/PerformanceChart.tsx (ENHANCE)
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const PerformanceChart: React.FC<{ trends: WeeklyTrend[] }> = ({ trends }) => {
  const { isMobile } = useResponsive();
  const chartHeight = isMobile ? 200 : 300;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Weekly Progress Trends
        </Typography>

        <ResponsiveContainer width="100%" height={chartHeight}>
          <LineChart data={trends}>
            <XAxis dataKey="week_start" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="accuracy_rate" stroke="#1976d2" strokeWidth={2} />
            <Line type="monotone" dataKey="mcq_attempts" stroke="#2e7d32" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
```

**Backend API** (⚠️ MISSING - Use Mock Data):
```typescript
// frontend/src/hooks/useWeeklyTrends.ts (NEW)
export const useWeeklyTrends = (weeks: number = 4) => {
  return useQuery({
    queryKey: ['trends', 'weekly', weeks],
    queryFn: async () => {
      // TEMPORARY: Use mock data until backend endpoint exists
      if (process.env.NODE_ENV === 'development') {
        return generateMockTrends(weeks);
      }

      // FUTURE: When backend implements endpoint
      const response = await apiClient.get(`/api/v1/progress/trends/weekly?weeks=${weeks}`);
      return response.data.trends as WeeklyTrend[];
    },
  });
};

// Mock data generator
function generateMockTrends(weeks: number): WeeklyTrend[] {
  const trends: WeeklyTrend[] = [];
  const today = new Date();

  for (let i = weeks - 1; i >= 0; i--) {
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - (i * 7));

    trends.push({
      week_start: weekStart.toISOString().split('T')[0],
      mcq_attempts: Math.floor(Math.random() * 30) + 10,  // 10-40 attempts
      accuracy_rate: Math.floor(Math.random() * 30) + 60,  // 60-90%
      study_cards_reviewed: Math.floor(Math.random() * 20) + 5,  // 5-25 cards
    });
  }

  return trends;
}
```

---

### US-008-003: Exam Readiness Gauge
**As a** medical student
**I want to** see my exam readiness prediction
**So that** I know when I'm prepared for the AMC exam

**Acceptance Criteria**:
- [ ] Circular progress gauge (0-100%)
- [ ] Color-coded: Green (≥80%), Yellow (60-79%), Red (<60%)
- [ ] Algorithm-based calculation (weighted factors)
- [ ] Breakdown of contributing factors (MCQ accuracy, OSCE practice, study cards, weak areas, streak)
- [ ] Recommendation text based on score
- [ ] Updates in real-time as user practices

**Exam Readiness Algorithm**:
```typescript
// frontend/src/utils/examReadiness.ts (NEW)
interface ExamReadinessFactors {
  mcqAccuracy: number;      // 0-100
  osceCompletions: number;  // Count
  studyCardMastery: number; // 0-100
  weakAreasCount: number;   // Count
  studyStreak: number;      // Days
}

export function calculateExamReadiness(factors: ExamReadinessFactors): number {
  // Weighted scoring (total = 100%)
  const weights = {
    mcqAccuracy: 0.35,  // 35% weight (most important)
    osce: 0.25,         // 25% weight
    studyCards: 0.20,   // 20% weight
    weakAreas: 0.10,    // 10% weight (inverse - penalty)
    streak: 0.10,       // 10% weight (consistency bonus)
  };

  // MCQ score (target 75% accuracy = 100 readiness)
  const mcqScore = Math.min((factors.mcqAccuracy / 75) * 100, 100);

  // OSCE score (target 20 completions = 100 readiness)
  const osceScore = Math.min((factors.osceCompletions / 20) * 100, 100);

  // Study card score (direct mastery percentage)
  const studyCardScore = factors.studyCardMastery;

  // Weak areas penalty (each weak area reduces score by 10%)
  const weakAreasScore = Math.max(100 - (factors.weakAreasCount * 10), 0);

  // Study streak bonus (30 consecutive days = 100%)
  const streakScore = Math.min((factors.studyStreak / 30) * 100, 100);

  // Weighted sum
  const readiness = (
    mcqScore * weights.mcqAccuracy +
    osceScore * weights.osce +
    studyCardScore * weights.studyCards +
    weakAreasScore * weights.weakAreas +
    streakScore * weights.streak
  );

  return Math.round(readiness);
}

export function getExamReadinessRecommendation(score: number): string {
  if (score >= 80) {
    return 'Excellent! You are well-prepared for the AMC Clinical Exam. Continue practicing to maintain your skills.';
  } else if (score >= 60) {
    return 'Good progress! Focus on weak areas and increase OSCE practice to boost your readiness.';
  } else if (score >= 40) {
    return 'More practice needed. Aim for 30+ MCQ attempts per week and complete at least 3 OSCE stations weekly.';
  } else {
    return 'Early stage. Establish a consistent daily study routine with MCQs, OSCEs, and Study Cards.';
  }
}
```

**Component Implementation**:
```typescript
// frontend/src/components/dashboard/ExamReadinessGauge.tsx (NEW)
export const ExamReadinessGauge: React.FC<ExamReadinessGaugeProps> = (props) => {
  const readiness = calculateExamReadiness(props);
  const color = readiness >= 80 ? 'success' : readiness >= 60 ? 'warning' : 'error';
  const recommendation = getExamReadinessRecommendation(readiness);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          AMC Exam Readiness
        </Typography>

        {/* Circular progress gauge */}
        <Box sx={{ position: 'relative', display: 'inline-flex', width: '100%', justifyContent: 'center' }}>
          <CircularProgress
            variant="determinate"
            value={readiness}
            size={140}
            thickness={5}
            color={color}
          />
          <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
            <Typography variant="h3" color={`${color}.main`} fontWeight="bold">
              {readiness}%
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Ready
            </Typography>
          </Box>
        </Box>

        {/* Recommendation */}
        <Typography variant="body2" color="text.secondary" sx={{ mt: 3, textAlign: 'center' }}>
          {recommendation}
        </Typography>

        {/* Factor breakdown */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Readiness Factors:
          </Typography>
          <Stack spacing={1}>
            <FactorChip label="MCQ Accuracy" value={props.mcqAccuracy} target={75} unit="%" />
            <FactorChip label="OSCE Practice" value={props.osceCompletions} target={20} unit="" />
            <FactorChip label="Study Card Mastery" value={props.studyCardMastery} target={80} unit="%" />
            <FactorChip label="Study Streak" value={props.studyStreak} target={30} unit="days" />
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
};
```

---

### US-008-004: Weak Areas Panel
**As a** medical student
**I want to** see my weak areas with recommendations
**So that** I can focus my study efforts effectively

**Acceptance Criteria**:
- [ ] List of specialties with <70% accuracy (configurable threshold)
- [ ] Each weak area shows: specialty name, accuracy rate, attempt count
- [ ] Recommendation for each weak area ("Practice 10 more MCQs in Cardiology")
- [ ] Link to practice page filtered by that specialty
- [ ] Sorted by lowest accuracy first
- [ ] Empty state if no weak areas

**Component Implementation**:
```typescript
// frontend/src/components/dashboard/WeakAreasPanel.tsx (ENHANCE)
export const WeakAreasPanel: React.FC<{ weakAreas: WeakArea[] }> = ({ weakAreas }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Areas for Improvement
        </Typography>

        {weakAreas.length === 0 ? (
          <Alert severity="success">
            Great job! No weak areas detected. Keep up the good work!
          </Alert>
        ) : (
          <Stack spacing={2}>
            {weakAreas.map((area) => (
              <Box key={area.specialty}>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="body1" fontWeight="medium">
                    {area.specialty}
                  </Typography>
                  <Chip
                    label={`${area.accuracy_rate}%`}
                    color="warning"
                    size="small"
                  />
                </Stack>

                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {area.recommendation}
                </Typography>

                <Button
                  size="small"
                  href={`/practice/mcq?specialty=${area.specialty}`}
                  sx={{ mt: 1 }}
                >
                  Practice {area.specialty}
                </Button>
              </Box>
            ))}
          </Stack>
        )}
      </CardContent>
    </Card>
  );
};
```

---

### US-008-005: Specialty Breakdown
**As a** medical student
**I want to** see my performance across all medical specialties
**So that** I can identify strengths and weaknesses

**Acceptance Criteria**:
- [ ] Bar chart showing accuracy by specialty (11 AMC specialties)
- [ ] Each bar color-coded (green >80%, yellow 60-80%, red <60%)
- [ ] X-axis: Specialties (abbreviated on mobile)
- [ ] Y-axis: Accuracy percentage (0-100%)
- [ ] Tooltip shows exact accuracy + attempt count
- [ ] Responsive (horizontal scroll on mobile if needed)

**AMC Specialties**:
1. Cardiology
2. Respiratory
3. Gastroenterology
4. Neurology
5. Endocrinology
6. Renal
7. Musculoskeletal
8. Psychiatry
9. Obstetrics & Gynaecology
10. Paediatrics
11. Surgery

---

## Technical Specifications

### Dashboard Page

```typescript
// frontend/src/pages/PerformanceDashboard.tsx (NEW)
export const PerformanceDashboard: React.FC = () => {
  const { data: dashboard, isLoading, error } = useDashboard();
  const { data: trends } = useWeeklyTrends(4);

  if (isLoading) return <CircularProgress />;
  if (error) return <Alert severity="error">Failed to load dashboard</Alert>;
  if (!dashboard) return null;

  // Calculate exam readiness
  const readinessFactors = {
    mcqAccuracy: dashboard.mcq_accuracy_rate,
    osceCompletions: dashboard.total_osce_completions,
    studyCardMastery: dashboard.study_card_retention_rate,
    weakAreasCount: dashboard.weak_areas.length,
    studyStreak: dashboard.study_streak || 0,  // From backend (future)
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Performance Dashboard
      </Typography>

      {/* Summary Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="MCQ Attempts"
            value={dashboard.total_mcq_attempts}
            subtitle={`${dashboard.mcq_accuracy_rate.toFixed(1)}% accuracy`}
            color="primary"
            icon={<QuizIcon />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="OSCE Completions"
            value={dashboard.total_osce_completions}
            subtitle="Clinical scenarios"
            color="secondary"
            icon={<LocalHospitalIcon />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Study Cards"
            value={dashboard.study_cards_reviewed}
            subtitle={`${dashboard.study_card_retention_rate.toFixed(1)}% retention`}
            color="success"
            icon={<SchoolIcon />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Weak Areas"
            value={dashboard.weak_areas.length}
            subtitle="Need improvement"
            color="warning"
            icon={<WarningIcon />}
          />
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <PerformanceChart trends={trends || []} />
        </Grid>
        <Grid item xs={12} md={4}>
          <ExamReadinessGauge {...readinessFactors} />
        </Grid>
      </Grid>

      {/* Bottom Row */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <SpecialtyBreakdown specialties={dashboard.specialty_breakdown} />
        </Grid>
        <Grid item xs={12} md={4}>
          <WeakAreasPanel weakAreas={dashboard.weak_areas} />
        </Grid>
      </Grid>
    </Box>
  );
};
```

---

## Testing Requirements

### Unit Tests

```typescript
describe('examReadinessAlgorithm', () => {
  it('calculates readiness correctly', () => {
    const readiness = calculateExamReadiness({
      mcqAccuracy: 75,
      osceCompletions: 15,
      studyCardMastery: 80,
      weakAreasCount: 2,
      studyStreak: 20,
    });

    expect(readiness).toBeGreaterThan(70);
    expect(readiness).toBeLessThan(85);
  });

  it('returns correct recommendation for high score', () => {
    const recommendation = getExamReadinessRecommendation(85);
    expect(recommendation).toContain('Excellent');
  });
});

describe('PerformanceDashboard', () => {
  it('renders all stat cards', async () => {
    render(<PerformanceDashboard />);

    await waitFor(() => {
      expect(screen.getByText('MCQ Attempts')).toBeInTheDocument();
      expect(screen.getByText('OSCE Completions')).toBeInTheDocument();
      expect(screen.getByText('Study Cards')).toBeInTheDocument();
      expect(screen.getByText('Weak Areas')).toBeInTheDocument();
    });
  });
});
```

---

## Success Criteria

- ✅ Dashboard displays 4 summary stat cards
- ✅ Weekly trends chart functional
- ✅ Exam readiness gauge accurate (algorithm tested)
- ✅ Weak areas panel with recommendations
- ✅ Specialty breakdown displayed
- ✅ All data from backend APIs
- ✅ <2.5s page load time
- ✅ Test coverage ≥75%
- ✅ Mobile responsive

---

## Implementation Timeline

**Sprint 2 - Days 3-4 (8 hours)**:
- Create PerformanceDashboard page
- Implement useDashboard() and useWeeklyTrends() hooks
- Create ExamReadinessGauge component
- Enhance existing dashboard components
- Write unit tests

---

**Document Status**: ✅ Ready for Implementation
**Last Updated**: 2026-02-15
