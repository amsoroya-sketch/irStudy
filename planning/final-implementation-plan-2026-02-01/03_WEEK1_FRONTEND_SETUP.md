# Week 1: Frontend Setup & Component Library
**Owner:** Developer 3 - Frontend Lead
**Duration:** 10 hours
**Priority:** P0 (Critical - defines user interface)
**Status:** Ready to Start

---

## 📋 Overview

This plan establishes the React frontend foundation by reusing production-tested components from `/home/dev/Development/irStudy/respiratory-mcq-app/`. We'll create a modern, responsive interface with TypeScript, state management, and component library in 10 hours.

**Key Achievement:** Production-ready MCQ interface with routing and state management in 1 day

---

## ✅ Prerequisites

- [x] Backend API running (from Task 2 - Backend Setup)
- [x] API endpoints documented at `/api/docs`
- [ ] Node.js 18+ installed locally
- [ ] npm or yarn package manager

---

## 🎯 Goals

1. **React Component Library Setup** (2 hours)
   - Create React app with Vite
   - Configure TypeScript
   - Setup Material-UI or Tailwind CSS

2. **Port MCQ Interface** (4 hours)
   - Copy components from respiratory-mcq-app
   - Adapt for irStudy backend API
   - Implement question viewer

3. **Dashboard Wireframes** (2 hours)
   - Study statistics display
   - Performance analytics
   - Navigation components

4. **Routing & State Management** (2 hours)
   - React Router setup
   - Zustand or Redux Toolkit
   - API client configuration

---

## 📝 Detailed Task Breakdown

### Task 1: React Component Library Setup (2 hours)

**Priority:** P0 (CRITICAL - foundation for all frontend work)

**Steps:**

```bash
# 1. Navigate to project root
cd /home/dev/Development/irStudy

# 2. Create React frontend with Vite (faster than Create React App)
npm create vite@latest frontend -- --template react-ts

# Expected output:
# ✔ Select a framework: › React
# ✔ Select a variant: › TypeScript
# Scaffolding project in frontend/

# 3. Navigate to frontend directory
cd frontend

# 4. Install dependencies
npm install

# 5. Install additional packages
npm install \
  @mui/material @mui/icons-material @emotion/react @emotion/styled \
  react-router-dom \
  zustand \
  axios \
  react-query \
  date-fns \
  recharts

# Development dependencies
npm install -D \
  @types/react @types/react-dom \
  @typescript-eslint/eslint-plugin @typescript-eslint/parser \
  eslint eslint-plugin-react-hooks \
  prettier

# 6. Configure TypeScript (tsconfig.json already exists from Vite)
# Update for stricter checking
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@pages/*": ["src/pages/*"],
      "@hooks/*": ["src/hooks/*"],
      "@utils/*": ["src/utils/*"],
      "@types/*": ["src/types/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

# 7. Create directory structure
mkdir -p src/{components,pages,hooks,utils,types,services,store,assets}
mkdir -p src/components/{mcq,osce,common,layout}
mkdir -p src/pages/{auth,dashboard,study}

# 8. Configure Material-UI theme
cat > src/theme.ts << 'EOF'
import { createTheme } from '@mui/material/styles';

// Australian Medical Education theme
export const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Medical blue
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#2e7d32', // Success green (correct answers)
      light: '#4caf50',
      dark: '#1b5e20',
    },
    error: {
      main: '#d32f2f', // Error red (incorrect answers)
    },
    warning: {
      main: '#ed6c02', // Warning orange
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // No uppercase buttons
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});
EOF

# 9. Update main App.tsx
cat > src/App.tsx << 'EOF'
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';

import { theme } from './theme';
import { AppRoutes } from './routes';

// React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
EOF

# 10. Test development server
npm run dev

# Expected output:
# VITE v5.x.x ready in xxx ms
# ➜ Local:   http://localhost:5173/
# ➜ Network: use --host to expose
```

**Validation:**
- [ ] Vite dev server runs without errors
- [ ] TypeScript compilation passes
- [ ] Material-UI theme loads correctly
- [ ] Browser opens to http://localhost:5173/

**Time Estimate:** 2 hours

---

### Task 2: Port MCQ Interface from respiratory-mcq-app (4 hours)

**Priority:** P0 (CRITICAL - core user feature)

**Source:** `/home/dev/Development/irStudy/respiratory-mcq-app/src/`

**Steps:**

```bash
# 1. Explore existing MCQ components
cd /home/dev/Development/irStudy/respiratory-mcq-app/src
ls -la

# Expected components:
# - MCQCard.tsx (main question display)
# - AnswerOptions.tsx (A, B, C, D options)
# - ExplanationPanel.tsx (shows after answer)
# - ProgressTracker.tsx (tracks completion)
# - FilterControls.tsx (topic, difficulty filters)
```

**Create MCQ Types:**

Create `frontend/src/types/mcq.ts`:

```typescript
/**
 * MCQ Type Definitions
 * Matches backend API schema
 */

export interface MCQOption {
  [key: string]: string;
  A: string;
  B: string;
  C: string;
  D: string;
}

export interface Citation {
  source: string;
  page?: string;
  section?: string;
  url?: string;
}

export interface MCQ {
  id: number;
  question: string;
  options: MCQOption;
  correct_answer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
  topic: string;
  subtopic?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  week?: number;
  citations?: Citation[];
  image_url?: string;
  image_caption?: string;
  created_at: string;
}

export interface MCQAttempt {
  mcq_id: number;
  selected_answer: 'A' | 'B' | 'C' | 'D';
  is_correct: boolean;
  time_taken_seconds?: number;
}

export interface MCQListResponse {
  mcqs: MCQ[];
  total: number;
  skip: number;
  limit: number;
}
```

**Create MCQ Card Component:**

Create `frontend/src/components/mcq/MCQCard.tsx`:

```typescript
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Button,
  Box,
  Chip,
  Alert,
} from '@mui/material';
import { CheckCircle, Cancel } from '@mui/icons-material';

import { MCQ, MCQAttempt } from '@/types/mcq';

interface MCQCardProps {
  mcq: MCQ;
  onSubmit: (attempt: MCQAttempt) => void;
  showAnswer?: boolean;
}

export const MCQCard: React.FC<MCQCardProps> = ({ mcq, onSubmit, showAnswer = false }) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [submitted, setSubmitted] = useState(false);
  const [startTime] = useState(Date.now());

  const handleSubmit = () => {
    if (!selectedAnswer) return;

    const timeTaken = Math.floor((Date.now() - startTime) / 1000);
    const isCorrect = selectedAnswer === mcq.correct_answer;

    onSubmit({
      mcq_id: mcq.id,
      selected_answer: selectedAnswer as 'A' | 'B' | 'C' | 'D',
      is_correct: isCorrect,
      time_taken_seconds: timeTaken,
    });

    setSubmitted(true);
  };

  const getDifficultyColor = (difficulty: string) => {
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
    <Card sx={{ maxWidth: 800, margin: 'auto', mt: 2 }}>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Chip label={mcq.topic} color="primary" size="small" />
          <Chip
            label={mcq.difficulty}
            color={getDifficultyColor(mcq.difficulty)}
            size="small"
          />
        </Box>

        {/* Question */}
        <Typography variant="h6" gutterBottom>
          {mcq.question}
        </Typography>

        {/* Image (if available) */}
        {mcq.image_url && (
          <Box sx={{ my: 2 }}>
            <img
              src={mcq.image_url}
              alt={mcq.image_caption || 'MCQ image'}
              style={{ maxWidth: '100%', borderRadius: 8 }}
            />
            {mcq.image_caption && (
              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                {mcq.image_caption}
              </Typography>
            )}
          </Box>
        )}

        {/* Answer Options */}
        <FormControl component="fieldset" sx={{ width: '100%', mt: 2 }}>
          <RadioGroup value={selectedAnswer} onChange={(e) => setSelectedAnswer(e.target.value)}>
            {Object.entries(mcq.options).map(([key, value]) => (
              <FormControlLabel
                key={key}
                value={key}
                control={<Radio />}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography>{value}</Typography>
                    {submitted && key === mcq.correct_answer && (
                      <CheckCircle color="success" sx={{ ml: 1 }} />
                    )}
                    {submitted && key === selectedAnswer && key !== mcq.correct_answer && (
                      <Cancel color="error" sx={{ ml: 1 }} />
                    )}
                  </Box>
                }
                disabled={submitted}
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 2,
                  p: 1,
                  mb: 1,
                  backgroundColor:
                    submitted && key === mcq.correct_answer
                      ? 'success.light'
                      : submitted && key === selectedAnswer
                      ? 'error.light'
                      : 'background.paper',
                }}
              />
            ))}
          </RadioGroup>
        </FormControl>

        {/* Submit Button */}
        {!submitted && (
          <Button
            variant="contained"
            fullWidth
            sx={{ mt: 2 }}
            onClick={handleSubmit}
            disabled={!selectedAnswer}
          >
            Submit Answer
          </Button>
        )}

        {/* Explanation (after submission) */}
        {submitted && (
          <Box sx={{ mt: 3 }}>
            <Alert
              severity={selectedAnswer === mcq.correct_answer ? 'success' : 'error'}
              icon={
                selectedAnswer === mcq.correct_answer ? (
                  <CheckCircle fontSize="inherit" />
                ) : (
                  <Cancel fontSize="inherit" />
                )
              }
            >
              <Typography variant="subtitle2" gutterBottom>
                {selectedAnswer === mcq.correct_answer
                  ? 'Correct! Well done.'
                  : `Incorrect. The correct answer is ${mcq.correct_answer}.`}
              </Typography>
            </Alert>

            <Box sx={{ mt: 2, p: 2, backgroundColor: 'background.default', borderRadius: 2 }}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Explanation:
              </Typography>
              <Typography variant="body2">{mcq.explanation}</Typography>

              {/* Citations */}
              {mcq.citations && mcq.citations.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    References:
                  </Typography>
                  {mcq.citations.map((citation, index) => (
                    <Typography key={index} variant="caption" display="block">
                      • {citation.source}
                      {citation.page && ` (p. ${citation.page})`}
                      {citation.section && ` - ${citation.section}`}
                    </Typography>
                  ))}
                </Box>
              )}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
```

**Create MCQ List Component:**

Create `frontend/src/components/mcq/MCQList.tsx`:

```typescript
import React, { useState } from 'react';
import { Box, CircularProgress, Typography, Button, Stack } from '@mui/material';
import { useQuery } from 'react-query';

import { MCQ, MCQAttempt } from '@/types/mcq';
import { mcqService } from '@/services/mcq.service';
import { MCQCard } from './MCQCard';
import { MCQFilters } from './MCQFilters';

export const MCQList: React.FC = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [filters, setFilters] = useState({
    topic: '',
    difficulty: '',
    week: undefined as number | undefined,
  });

  // Fetch MCQs from API
  const { data, isLoading, error } = useQuery(
    ['mcqs', filters],
    () => mcqService.getMCQs(filters),
    {
      keepPreviousData: true,
    }
  );

  const handleSubmitAttempt = async (attempt: MCQAttempt) => {
    try {
      await mcqService.submitAttempt(attempt);
      console.log('Attempt submitted successfully');
    } catch (error) {
      console.error('Failed to submit attempt:', error);
    }
  };

  const handleNext = () => {
    if (data && currentIndex < data.mcqs.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Typography color="error">Failed to load MCQs. Please try again.</Typography>
      </Box>
    );
  }

  if (!data || data.mcqs.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Typography>No MCQs found. Try adjusting your filters.</Typography>
      </Box>
    );
  }

  const currentMCQ = data.mcqs[currentIndex];

  return (
    <Box>
      {/* Filters */}
      <MCQFilters filters={filters} onFilterChange={setFilters} />

      {/* Current MCQ */}
      <MCQCard mcq={currentMCQ} onSubmit={handleSubmitAttempt} />

      {/* Navigation */}
      <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 3 }}>
        <Button variant="outlined" onClick={handlePrevious} disabled={currentIndex === 0}>
          Previous
        </Button>
        <Typography sx={{ alignSelf: 'center' }}>
          {currentIndex + 1} / {data.mcqs.length}
        </Typography>
        <Button
          variant="outlined"
          onClick={handleNext}
          disabled={currentIndex === data.mcqs.length - 1}
        >
          Next
        </Button>
      </Stack>
    </Box>
  );
};
```

**Create API Service:**

Create `frontend/src/services/mcq.service.ts`:

```typescript
import axios from 'axios';
import { MCQ, MCQListResponse, MCQAttempt } from '@/types/mcq';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Axios instance with auth token
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const mcqService = {
  getMCQs: async (filters: {
    topic?: string;
    difficulty?: string;
    week?: number;
    skip?: number;
    limit?: number;
  }): Promise<MCQListResponse> => {
    const params = new URLSearchParams();
    if (filters.topic) params.append('topic', filters.topic);
    if (filters.difficulty) params.append('difficulty', filters.difficulty);
    if (filters.week) params.append('week', filters.week.toString());
    params.append('skip', (filters.skip || 0).toString());
    params.append('limit', (filters.limit || 20).toString());

    const response = await apiClient.get<MCQListResponse>(`/mcqs?${params}`);
    return response.data;
  },

  getMCQById: async (id: number): Promise<MCQ> => {
    const response = await apiClient.get<MCQ>(`/mcqs/${id}`);
    return response.data;
  },

  submitAttempt: async (attempt: MCQAttempt): Promise<void> => {
    await apiClient.post(`/mcqs/${attempt.mcq_id}/attempt`, attempt);
  },
};
```

**Validation:**
- [ ] MCQ components render correctly
- [ ] Answer selection works
- [ ] Explanation shows after submission
- [ ] API integration functional
- [ ] Navigation between questions works

**Time Estimate:** 4 hours

---

### Task 3: Dashboard Wireframes (2 hours)

**Priority:** P1 (High - improves UX)

**Create Dashboard Page:**

Create `frontend/src/pages/dashboard/Dashboard.tsx`:

```typescript
import React from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
} from '@mui/material';
import { BarChart, TrendingUp, CheckCircle, Timer } from '@mui/icons-material';

export const Dashboard: React.FC = () => {
  // TODO: Fetch real data from API
  const stats = {
    totalAttempted: 145,
    correctPercentage: 72,
    topicsMastered: 8,
    studyStreakDays: 12,
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Study Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Total MCQs Attempted */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <BarChart color="primary" sx={{ mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  MCQs Attempted
                </Typography>
              </Box>
              <Typography variant="h4">{stats.totalAttempted}</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Correct Percentage */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircle color="success" sx={{ mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Correct Answers
                </Typography>
              </Box>
              <Typography variant="h4">{stats.correctPercentage}%</Typography>
              <LinearProgress
                variant="determinate"
                value={stats.correctPercentage}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Topics Mastered */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp color="warning" sx={{ mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Topics Mastered
                </Typography>
              </Box>
              <Typography variant="h4">{stats.topicsMastered}</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Study Streak */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Timer color="error" sx={{ mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Study Streak
                </Typography>
              </Box>
              <Typography variant="h4">{stats.studyStreakDays} days</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity (placeholder) */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Your MCQ attempts will appear here
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance by Topic (placeholder) */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance by Topic
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Chart coming soon
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};
```

**Validation:**
- [ ] Dashboard renders with placeholder stats
- [ ] Cards display correctly on mobile and desktop
- [ ] Layout is responsive (Grid system)
- [ ] Icons and colors match theme

**Time Estimate:** 2 hours

---

### Task 4: Routing & State Management (2 hours)

**Priority:** P0 (CRITICAL - enables navigation)

**Setup React Router:**

Create `frontend/src/routes.tsx`:

```typescript
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import { Layout } from '@/components/layout/Layout';
import { Dashboard } from '@/pages/dashboard/Dashboard';
import { MCQStudy } from '@/pages/study/MCQStudy';
import { Login } from '@/pages/auth/Login';
import { Register } from '@/pages/auth/Register';
import { ProtectedRoute } from '@/components/common/ProtectedRoute';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected routes (require authentication) */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="study/mcqs" element={<MCQStudy />} />
        <Route path="study/osces" element={<div>OSCEs coming soon</div>} />
        <Route path="profile" element={<div>Profile coming soon</div>} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<div>Page not found</div>} />
    </Routes>
  );
};
```

**Setup Zustand Store:**

Create `frontend/src/store/authStore.ts`:

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  email: string;
  full_name: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;

  // Actions
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setTokens: (accessToken, refreshToken) =>
        set({ accessToken, refreshToken, isAuthenticated: true }),

      setUser: (user) => set({ user }),

      logout: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

**Create Protected Route Component:**

Create `frontend/src/components/common/ProtectedRoute.tsx`:

```typescript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
```

**Validation:**
- [ ] React Router configured
- [ ] Protected routes require authentication
- [ ] Zustand store persists auth state
- [ ] Navigation between pages works
- [ ] Logout clears auth state

**Time Estimate:** 2 hours

---

## 📊 Success Metrics

### Completion Criteria
- [ ] React app running on http://localhost:5173/
- [ ] MCQ interface ported and functional
- [ ] Dashboard displays placeholder stats
- [ ] Routing configured (5+ routes)
- [ ] State management setup (Zustand)
- [ ] Mobile responsive (tested on 375px width)

### Quality Gates
- [ ] TypeScript compilation: 0 errors
- [ ] ESLint: 0 errors
- [ ] Components render on mobile and desktop
- [ ] API client configured with auth tokens
- [ ] Protected routes redirect unauthenticated users

### Testing Checklist
```bash
# Build for production (should complete without errors)
npm run build

# Preview production build
npm run preview

# Type checking
npx tsc --noEmit

# Linting
npx eslint src/
```

---

## 🔗 Related Documents

- **[00_MASTER_PLAN.md](./00_MASTER_PLAN.md)** - Overall implementation plan
- **[02_WEEK1_BACKEND_SETUP.md](./02_WEEK1_BACKEND_SETUP.md)** - Backend API (dependency)
- **[04_WEEK1_AI_AGENT_OS.md](./04_WEEK1_AI_AGENT_OS.md)** - AI features integration
- **[12_IMMEDIATE_NEXT_STEPS.md](./12_IMMEDIATE_NEXT_STEPS.md)** - Getting started

---

## 🆘 Troubleshooting

### Issue: Vite dev server won't start
**Solution:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version (should be 18+)
node --version
```

### Issue: API requests fail with CORS errors
**Solution:**
```bash
# Verify backend CORS settings in backend/src/main.py
# Allow frontend origin: http://localhost:5173

# Alternatively, use Vite proxy (vite.config.ts):
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

### Issue: TypeScript errors in components
**Solution:**
```bash
# Install missing type definitions
npm install -D @types/node

# Restart TypeScript server in VSCode
# Cmd+Shift+P → "TypeScript: Restart TS Server"
```

---

## 📞 Support

**Questions?** Post in `#irstudy-frontend` Slack channel

**Critical Blocker?** Contact Project Manager immediately

---

**Last Updated:** 2026-02-01
**Owner:** Developer 3 - Frontend Lead
**Estimated Completion:** 2026-02-02 (Day 2 of Week 1)
