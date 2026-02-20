/**
 * Error Boundary Component
 *
 * Fix #5: Error Boundaries (Prevent Dashboard Crashes)
 *
 * Catches React errors in component tree and displays fallback UI
 * instead of crashing the entire application.
 *
 * Features:
 * - Catches errors in child components (render, lifecycle, constructors)
 * - Displays user-friendly error message with reload button
 * - Logs errors to console (can be extended to send to Sentry/monitoring)
 * - Prevents white screen of death on API errors
 *
 * Usage:
 * ```tsx
 * <ErrorBoundary>
 *   <EMRDashboard />
 * </ErrorBoundary>
 * ```
 *
 * WCAG 2.2 AA Compliance:
 * - Error icon with sufficient contrast (4.5:1)
 * - Keyboard accessible reload button
 * - Screen reader announces error message
 */

import { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

interface Props {
  children: ReactNode;
  fallback?: ReactNode; // Optional custom fallback UI
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * ErrorBoundary Class Component
 *
 * React Error Boundaries must be class components (hooks don't support
 * componentDidCatch lifecycle method).
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  /**
   * Update state when error is caught
   * This enables rendering fallback UI instead of crashing
   */
  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
    };
  }

  /**
   * Log error details for debugging
   * In production, send to error monitoring service (Sentry, LogRocket, etc.)
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught error:', error, errorInfo);

    // Store error info in state for display (dev mode)
    this.setState({
      errorInfo,
    });

    // TODO: Send to error monitoring service
    // if (process.env.NODE_ENV === 'production') {
    //   Sentry.captureException(error, { extra: errorInfo });
    // }
  }

  /**
   * Reset error state (used by "Try Again" button)
   */
  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  /**
   * Reload entire page (used by "Reload Page" button)
   */
  handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // Custom fallback UI if provided
      if (fallback) {
        return fallback;
      }

      // Default error UI
      return (
        <Container maxWidth="md">
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '60vh',
              textAlign: 'center',
              py: 4,
            }}
            role="alert"
            aria-live="assertive"
          >
            {/* Error Icon */}
            <ErrorOutlineIcon
              sx={{
                fontSize: 80,
                color: 'error.main',
                mb: 3,
              }}
              aria-hidden="true"
            />

            {/* Error Title */}
            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              sx={{ fontWeight: 600 }}
            >
              Something went wrong
            </Typography>

            {/* Error Message */}
            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ mb: 4, maxWidth: 600 }}
            >
              {error?.message ||
                'An unexpected error occurred. Please try reloading the page.'}
            </Typography>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                color="primary"
                onClick={this.handleReload}
                size="large"
              >
                Reload Page
              </Button>

              <Button
                variant="outlined"
                color="primary"
                onClick={this.handleReset}
                size="large"
              >
                Try Again
              </Button>
            </Box>

            {/* Developer Info (Dev Mode Only) */}
            {process.env.NODE_ENV === 'development' && errorInfo && (
              <Box
                sx={{
                  mt: 4,
                  p: 2,
                  bgcolor: 'grey.100',
                  borderRadius: 1,
                  maxWidth: '100%',
                  overflow: 'auto',
                  textAlign: 'left',
                }}
              >
                <Typography
                  variant="caption"
                  component="pre"
                  sx={{
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {error?.stack}
                  {'\n\n'}
                  {errorInfo.componentStack}
                </Typography>
              </Box>
            )}
          </Box>
        </Container>
      );
    }

    // No error: render children normally
    return children;
  }
}

export default ErrorBoundary;
