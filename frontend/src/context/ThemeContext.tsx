/**
 * Theme Context for EMR Practice System
 *
 * Provides automatic theme switching between Epic (light) and Cerner (dark)
 * based on the active EMR session's emr_system field.
 *
 * Fix #2: Theme Switching Mechanism (Session-Based)
 * - Theme determined by active EMR session (not manual toggle)
 * - Epic sessions → epicTheme (beige, light background)
 * - Cerner sessions → cernerTheme (dark blue, dark background)
 *
 * Architecture:
 * <ThemeProvider>
 *   <EMRSessionProvider>  ← Provides session context
 *     <Routes />
 *   </EMRSessionProvider>
 * </ThemeProvider>
 */

import React, { createContext, useContext, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider, Theme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// TODO: Import actual theme files once created
// import { epicTheme } from '../theme/epicTheme';
// import { cernerTheme } from '../theme/cernerTheme';

// Placeholder themes (replace with actual imports)
import { createTheme } from '@mui/material/styles';

const epicTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#D4C5A9', // Beige/tan (Epic signature color)
      light: '#E6D9C4',
      dark: '#8B7355',
      contrastText: '#2C2C2C',
    },
    secondary: {
      main: '#8B7355', // Brown accent
      light: '#A68968',
      dark: '#6D5A43',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FAFAF8', // Off-white
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2C2C2C', // Dark gray
      secondary: '#5C5C5C',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
  shape: {
    borderRadius: 4, // Minimal rounded corners
  },
});

const cernerTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#0066CC', // Cerner blue
      light: '#3384D6',
      dark: '#004C99',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#003D7A', // Dark blue accent
      light: '#005BA8',
      dark: '#002952',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#1E1E1E', // Dark gray
      paper: '#2D2D2D', // Lighter gray for cards
    },
    text: {
      primary: '#FFFFFF', // White text
      secondary: '#B0B0B0', // Light gray text
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
  shape: {
    borderRadius: 8, // More rounded than Epic
  },
});

// Theme Context Interface
interface ThemeContextType {
  currentTheme: 'epic' | 'cerner';
  theme: Theme;
}

// Create context
export const ThemeContext = createContext<ThemeContextType>({
  currentTheme: 'epic',
  theme: epicTheme,
});

// Custom hook to access theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
  emrSystem?: 'epic' | 'cerner'; // Optional: for testing or default
}

/**
 * ThemeProvider Component
 *
 * Automatically switches between Epic and Cerner themes based on
 * the active EMR session's emr_system field.
 *
 * Usage:
 * ```tsx
 * <ThemeProvider>
 *   <EMRSessionProvider>
 *     <App />
 *   </EMRSessionProvider>
 * </ThemeProvider>
 * ```
 *
 * @param {React.ReactNode} children - Child components
 * @param {string} emrSystem - Optional: Override EMR system (for testing)
 */
export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  emrSystem,
}) => {
  // In production, get emrSystem from EMRSessionContext
  // For now, use prop or default to 'epic'
  // TODO: Uncomment when EMRSessionContext is available
  // const { session } = useEMRSession();
  // const currentTheme = session?.emr_system === 'cerner' ? 'cerner' : 'epic';

  const currentTheme = emrSystem || 'epic'; // Default to Epic

  // Memoize theme selection (performance optimization)
  const theme = useMemo(() => {
    return currentTheme === 'cerner' ? cernerTheme : epicTheme;
  }, [currentTheme]);

  const contextValue: ThemeContextType = {
    currentTheme,
    theme,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      <MuiThemeProvider theme={theme}>
        {/* CssBaseline: Resets CSS and applies theme background */}
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;
