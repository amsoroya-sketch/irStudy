/**
 * App.tsx - Main Application Component
 * Sets up routing and authentication provider with RBAC integration
 */

import React, { Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { CircularProgress, Box } from "@mui/material";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import theme from "./theme/theme";

// Lazy-loaded routes for code splitting
import {
  Login,
  Register,
  Dashboard,
  MCQBrowser,
  MCQAttempt,
  PerformanceDashboard,
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
                      <Dashboard />
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

                {/* Fallback Routes */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<Navigate to="/login" replace />} />
              </Routes>
            </Suspense>
          </AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
