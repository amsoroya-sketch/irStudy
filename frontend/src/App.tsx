/**
 * App.tsx - Main Application Component
 * Sets up routing and authentication provider with RBAC integration
 */

import { Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { CircularProgress, Box } from "@mui/material";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import theme from "./theme/theme";
import MobileBottomNav from "./components/layout/MobileBottomNav";

// Canonical route table (data). Re-exported so tests can import the route set.
import { ROUTES } from "./routes.config";
export { ROUTES } from "./routes.config";
export type { AppRoute } from "./routes.config";

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
                {ROUTES.map(({ path, element, public: isPublic }) => (
                  <Route
                    key={path}
                    path={path}
                    element={
                      isPublic ? (
                        element
                      ) : (
                        <ProtectedRoute>{element}</ProtectedRoute>
                      )
                    }
                  />
                ))}
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
