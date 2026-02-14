# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_008 - Performance Dashboard (6-8 hours)

**EXECUTE NOW**:

```bash
cd /home/dev/Development/irStudy/frontend

# Create Dashboard page component
mkdir -p src/pages src/components/dashboard

# Install Recharts (if not installed)
npm install recharts@^2.0.0

cat > src/pages/DashboardPage.tsx <<'EOF'
// Dashboard page will be implemented here
EOF

npx tsc --noEmit && echo "✅ TypeScript: 0 errors"
```

**DO NOT**:
- ❌ Ask "Would you like me to create the charts first?"
- ❌ Ask "Should I use a different charting library?"
- ❌ Wait for approval
- ❌ Ask "Which metrics should be displayed?"

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📋 Metadata

- **Week:** 2
- **Day:** 4-5 (Feb 17-18, 2026)
- **Duration:** 6-8 hours
- **Priority:** P1-High
- **Dependencies:** TASK_004 (User Progress API)
- **Owner:** flutter-desktop-expert (React/TypeScript)
- **Status:** 🟡 Not Started
- **Blocks:** TASK_009 (Mobile Design)

---

## 🎯 Objectives

1. **Create DashboardPage component** with comprehensive analytics
2. **Implement Recharts visualizations** (line charts, bar charts, pie charts)
3. **Display specialty breakdown** (11 medical specialties)
4. **Show weak area highlights** with study recommendations
5. **Add study streak tracker** (consecutive days)
6. **TypeScript: 0 errors**
7. **Page load time: <2 seconds**

---

## 📝 Implementation Guide

### Step 1: Create Dashboard Types (20 min)

```bash
cat > src/types/dashboard.ts <<'EOF'
export interface DashboardData {
  total_mcq_attempts: number;
  mcq_accuracy_rate: number;
  total_osce_completions: number;
  study_cards_reviewed: number;
  study_card_retention_rate: number;
  specialty_breakdown: SpecialtyPerformance[];
  weak_areas: string[];
}

export interface SpecialtyPerformance {
  specialty: string;
  total_attempts: number;
  correct_attempts: number;
  accuracy_rate: number;
  average_time_seconds: number;
}

export interface WeeklyTrend {
  week_start: string;
  mcq_attempts: number;
  accuracy_rate: number;
  study_cards_reviewed: number;
}
EOF
```

### Step 2: Create Dashboard API Hooks (30 min)

```bash
cat > src/hooks/useDashboard.ts <<'EOF'
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { DashboardData, WeeklyTrend } from '../types/dashboard';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const useDashboard = () => {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: async (): Promise<DashboardData> => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/progress/dashboard`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` }
      });
      return response.data;
    }
  });
};

export const useWeeklyTrends = (weeks: number = 4) => {
  return useQuery({
    queryKey: ['trends', 'weekly', weeks],
    queryFn: async (): Promise<WeeklyTrend[]> => {
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/progress/trends/weekly?weeks=${weeks}`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` }
        }
      );
      return response.data;
    }
  });
};
EOF
```

### Step 3: Create Dashboard Components (4 hours)

```bash
cat > src/pages/DashboardPage.tsx <<'EOF'
import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert
} from '@mui/material';
import { useDashboard, useWeeklyTrends } from '../hooks/useDashboard';
import { PerformanceChart } from '../components/dashboard/PerformanceChart';
import { SpecialtyBreakdown } from '../components/dashboard/SpecialtyBreakdown';
import { WeakAreasPanel } from '../components/dashboard/WeakAreasPanel';
import { StatCard } from '../components/dashboard/StatCard';

export const DashboardPage: React.FC = () => {
  const { data: dashboard, isLoading, error } = useDashboard();
  const { data: trends } = useWeeklyTrends(4);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Failed to load dashboard data</Alert>;
  }

  if (!dashboard) return null;

  return (
    <Box sx={{ padding: 3 }}>
      <Typography variant="h4" gutterBottom>
        Performance Dashboard
      </Typography>

      {/* Summary Stats */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="MCQ Attempts"
            value={dashboard.total_mcq_attempts}
            subtitle={`${dashboard.mcq_accuracy_rate}% accuracy`}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="OSCE Completions"
            value={dashboard.total_osce_completions}
            subtitle="Clinical scenarios"
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Study Cards"
            value={dashboard.study_cards_reviewed}
            subtitle={`${dashboard.study_card_retention_rate}% retention`}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Weak Areas"
            value={dashboard.weak_areas.length}
            subtitle="Need improvement"
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Weekly Progress Trends
              </Typography>
              <PerformanceChart trends={trends || []} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <WeakAreasPanel weakAreas={dashboard.weak_areas} />
        </Grid>
      </Grid>

      {/* Specialty Breakdown */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Performance by Specialty
          </Typography>
          <SpecialtyBreakdown specialties={dashboard.specialty_breakdown} />
        </CardContent>
      </Card>
    </Box>
  );
};
EOF

# Create child components
cat > src/components/dashboard/StatCard.tsx <<'EOF'
import { Card, CardContent, Typography, Box } from '@mui/material';

interface StatCardProps {
  title: string;
  value: number;
  subtitle: string;
  color: 'primary' | 'secondary' | 'success' | 'warning';
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, subtitle, color }) => (
  <Card>
    <CardContent>
      <Typography color="text.secondary" gutterBottom>
        {title}
      </Typography>
      <Typography variant="h3" color={`${color}.main`}>
        {value}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {subtitle}
      </Typography>
    </CardContent>
  </Card>
);
EOF

cat > src/components/dashboard/PerformanceChart.tsx <<'EOF'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { WeeklyTrend } from '../../types/dashboard';

interface PerformanceChartProps {
  trends: WeeklyTrend[];
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ trends }) => {
  const data = trends.map((trend) => ({
    name: new Date(trend.week_start).toLocaleDateString(),
    accuracy: trend.accuracy_rate,
    attempts: trend.mcq_attempts
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis yAxisId="left" />
        <YAxis yAxisId="right" orientation="right" />
        <Tooltip />
        <Legend />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="accuracy"
          stroke="#8884d8"
          name="Accuracy (%)"
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="attempts"
          stroke="#82ca9d"
          name="MCQ Attempts"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
EOF

cat > src/components/dashboard/SpecialtyBreakdown.tsx <<'EOF'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { SpecialtyPerformance } from '../../types/dashboard';

interface SpecialtyBreakdownProps {
  specialties: SpecialtyPerformance[];
}

export const SpecialtyBreakdown: React.FC<SpecialtyBreakdownProps> = ({ specialties }) => {
  const data = specialties.map((spec) => ({
    name: spec.specialty,
    accuracy: spec.accuracy_rate
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Bar dataKey="accuracy" fill="#8884d8" name="Accuracy (%)" />
      </BarChart>
    </ResponsiveContainer>
  );
};
EOF
```

### Step 4: Create Tests & Verify (1 hour)

```bash
cat > tests/pages/DashboardPage.test.tsx <<'EOF'
import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardPage } from '../../src/pages/DashboardPage';

const queryClient = new QueryClient();

describe('DashboardPage', () => {
  it('renders dashboard title', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <DashboardPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Performance Dashboard')).toBeInTheDocument();
    });
  });

  it('displays stat cards', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <DashboardPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('MCQ Attempts')).toBeInTheDocument();
      expect(screen.getByText('OSCE Completions')).toBeInTheDocument();
      expect(screen.getByText('Study Cards')).toBeInTheDocument();
    });
  });
});
EOF

npm test
npx tsc --noEmit
```

---

## ✅ Success Criteria

1. ✅ DashboardPage component created
2. ✅ Recharts visualizations (line, bar charts)
3. ✅ Specialty breakdown (11 specialties)
4. ✅ Weak area highlights
5. ✅ Study streak tracker
6. ✅ TypeScript: 0 errors
7. ✅ Page load: <2 seconds

---

## 🔄 When Complete

```bash
sed -i 's/TASK_008.*TODO/TASK_008: ✅ DONE/' @fix_plan.md

git commit -m "feat(frontend): Complete TASK_008 Performance Dashboard - Recharts analytics

- DashboardPage with comprehensive metrics
- Recharts line/bar charts for trends
- Specialty breakdown (11 medical specialties)
- Weak area recommendations
- TypeScript: 0 errors

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ TASK_008 complete. Starting TASK_009..."
```

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
