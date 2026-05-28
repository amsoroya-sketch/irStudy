/**
 * App.tsx - Main Application Component
 * Sets up routing and authentication provider with RBAC integration
 */

import { Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { CircularProgress, Box } from "@mui/material";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import theme from "./theme/theme";
import MobileBottomNav from "./components/layout/MobileBottomNav";
import { FlashcardReview } from "./components/study-cards/FlashcardReview";

// Lazy-loaded routes for code splitting
import {
  Login,
  Register,
  UnifiedDashboard,
  MCQBrowser,
  MCQAttempt,
  PerformanceDashboard,
  OSCEPractice,
  OSCESession,
  StartEMRSessionPage,
  EMRSelectSystemPage,
  EpicEMRPage,
  CernerEMRPage,
  HTMLNotesPage,
  MockExamStart,
  MockExamStation,
  MockExamResults,
} from "./routes";

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Loading fallback component
const LoadingFallback = () => (
  <Box
    sx={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      minHeight: "100vh",
      backgroundColor: "background.default",
    }}
  >
    <CircularProgress size={60} aria-label="Loading application" />
  </Box>
);

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider>
            <Suspense fallback={<LoadingFallback />}>
              <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Protected Routes */}
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <UnifiedDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/performance"
                  element={
                    <ProtectedRoute>
                      <PerformanceDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/mcqs"
                  element={
                    <ProtectedRoute>
                      <MCQBrowser />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/mcqs/:id/attempt"
                  element={
                    <ProtectedRoute>
                      <MCQAttempt />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/osce-practice"
                  element={
                    <ProtectedRoute>
                      <OSCEPractice />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/study-cards"
                  element={
                    <ProtectedRoute>
                      <FlashcardReview />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/html-notes"
                  element={
                    <ProtectedRoute>
                      <HTMLNotesPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/osce/session/:attemptId"
                  element={
                    <ProtectedRoute>
                      <OSCESession />
                    </ProtectedRoute>
                  }
                />

                {/* EMR Routes */}
                <Route
                  path="/emr/start"
                  element={
                    <ProtectedRoute>
                      <StartEMRSessionPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/emr/select/:sessionId"
                  element={
                    <ProtectedRoute>
                      <EMRSelectSystemPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/emr/epic/:sessionId"
                  element={
                    <ProtectedRoute>
                      <EpicEMRPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/emr/cerner/:sessionId"
                  element={
                    <ProtectedRoute>
                      <CernerEMRPage />
                    </ProtectedRoute>
                  }
                />

                {/* Mock Exam Routes */}
                <Route
                  path="/osce/mock-exam/start"
                  element={
                    <ProtectedRoute>
                      <MockExamStart />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/osce/mock-exam/:examId/station/:stationNumber"
                  element={
                    <ProtectedRoute>
                      <MockExamStation />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/osce/mock-exam/:examId/results"
                  element={
                    <ProtectedRoute>
                      <MockExamResults />
                    </ProtectedRoute>
                  }
                />

                {/* Fallback Routes */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<Navigate to="/login" replace />} />
              </Routes>
              {/* Mobile Bottom Navigation - shown only on mobile (<768px) */}
              <MobileBottomNav />
            </Suspense>
          </AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
