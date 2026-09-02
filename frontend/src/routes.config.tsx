/**
 * routes.config.tsx - Canonical application route table (data, not JSX tree)
 *
 * Single source of truth for EVERY route the app renders, declared in the SAME
 * order as the original inline <Routes> in App.tsx. App.tsx maps this array to
 * build the router; E2E coverage tooling parses the `path` strings to prove
 * every route has a passing journey test.
 *
 * `element` is the BARE page element. App.tsx wraps non-public entries in
 * <ProtectedRoute> at render time — this file stays free of the auth guard so
 * it can be imported/parsed without side effects.
 */

import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';

import {
  Login,
  Register,
  UnifiedDashboard,
  MCQBrowser,
  MCQAttempt,
  PerformanceDashboard,
  OSCEPractice,
  OSCESession,
  EMRCaseListPage,
  StartEMRSessionPage,
  EMRSelectSystemPage,
  EpicEMRPage,
  CernerEMRPage,
  EMRValidationPage,
  HTMLNotesPage,
  MockExamStart,
  MockExamStation,
  MockExamResults,
} from './routes';
import { FlashcardReview } from './components/study-cards/FlashcardReview';

/** A single application route. */
export interface AppRoute {
  /** react-router path pattern (may contain `:params`). */
  path: string;
  /** Bare page element; wrapped in <ProtectedRoute> unless `public`. */
  element: ReactNode;
  /** true = no auth guard (login/register + redirects). */
  public?: boolean;
}

/**
 * Every route, in render order. Order MUST match the original App.tsx so the
 * `*` fallback stays last. Keep redirects marked `public`.
 */
export const ROUTES: AppRoute[] = [
  // Public Routes
  { path: '/login', element: <Login />, public: true },
  { path: '/register', element: <Register />, public: true },

  // Protected Routes
  { path: '/dashboard', element: <UnifiedDashboard /> },
  { path: '/performance', element: <PerformanceDashboard /> },
  { path: '/mcqs', element: <MCQBrowser /> },
  { path: '/mcqs/:id/attempt', element: <MCQAttempt /> },
  { path: '/osce-practice', element: <OSCEPractice /> },
  { path: '/study-cards', element: <FlashcardReview /> },
  { path: '/html-notes', element: <HTMLNotesPage /> },
  { path: '/osce/session/:attemptId', element: <OSCESession /> },

  // EMR Routes
  { path: '/emr/cases', element: <EMRCaseListPage /> },
  { path: '/emr/start', element: <StartEMRSessionPage /> },
  { path: '/emr/select/:sessionId', element: <EMRSelectSystemPage /> },
  { path: '/emr/epic/:sessionId', element: <EpicEMRPage /> },
  { path: '/emr/cerner/:sessionId', element: <CernerEMRPage /> },
  { path: '/emr/validation/:sessionId', element: <EMRValidationPage /> },

  // Mock Exam Routes
  { path: '/osce/mock-exam/start', element: <MockExamStart /> },
  {
    path: '/osce/mock-exam/:examId/station/:stationNumber',
    element: <MockExamStation />,
  },
  { path: '/osce/mock-exam/:examId/results', element: <MockExamResults /> },

  // Fallback Routes (redirects — public so they never hit the auth guard)
  { path: '/', element: <Navigate to="/dashboard" replace />, public: true },
  { path: '*', element: <Navigate to="/login" replace />, public: true },
];
