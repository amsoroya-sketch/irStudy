/**
 * Epic EMR Theme Configuration
 *
 * Visual Design:
 * - Primary: Beige/tan (#D4C5A9) - Epic's signature professional color
 * - Secondary: Brown (#8B7355) - Warm accent for actions
 * - Background: Off-white (#FAFAF8) - Reduces eye strain
 * - Typography: Roboto - Professional medical UI standard
 * - Borders: Minimal rounding (4px) - Clinical, structured appearance
 *
 * This theme provides a light, professional interface that matches
 * real Epic EMR systems used in Australian hospitals.
 */

import { createTheme } from '@mui/material/styles';

export const epicTheme = createTheme({
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
      default: '#FAFAF8', // Off-white (reduces eye strain)
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2C2C2C', // Dark gray (high contrast)
      secondary: '#5A5A5A', // Medium gray
    },
    success: {
      main: '#4CAF50', // Green (for positive validation)
      light: '#81C784',
      dark: '#388E3C',
    },
    error: {
      main: '#D32F2F', // Red (for critical alerts)
      light: '#EF5350',
      dark: '#C62828',
    },
    warning: {
      main: '#FFA726', // Orange (for warnings)
      light: '#FFB74D',
      dark: '#F57C00',
    },
    info: {
      main: '#29B6F6', // Light blue (for info messages)
      light: '#4FC3F7',
      dark: '#0288D1',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
      lineHeight: 1.2,
      color: '#2C2C2C',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      lineHeight: 1.3,
      color: '#2C2C2C',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      lineHeight: 1.4,
      color: '#2C2C2C',
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
      lineHeight: 1.4,
      color: '#2C2C2C',
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: 1.5,
      color: '#2C2C2C',
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      lineHeight: 1.6,
      color: '#2C2C2C',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
      color: '#2C2C2C',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.43,
      color: '#5A5A5A',
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      textTransform: 'none', // Sentence case (more professional)
    },
  },
  shape: {
    borderRadius: 4, // Minimal rounding (clinical appearance)
  },
  spacing: 8, // 8px base unit (Material-UI default)
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          textTransform: 'none', // Sentence case
          fontWeight: 500,
        },
        contained: {
          boxShadow: 'none', // Flat design
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)', // Subtle shadow
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 4,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 4,
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)', // Subtle shadow
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRadius: 0, // Full height sidebars have no rounding
        },
      },
    },
  },
});
