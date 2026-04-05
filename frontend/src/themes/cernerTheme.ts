/**
 * Cerner EMR Theme Configuration
 *
 * Visual Design:
 * - Primary: Blue (#0066CC) - Cerner's signature medical blue
 * - Secondary: Light blue (#00A3E0) - Accent for interactive elements
 * - Background: Dark gray (#1E1E1E) - Reduces eye strain in low light
 * - Typography: Roboto - Professional medical UI standard
 * - Borders: Moderate rounding (8px) - Modern, friendly appearance
 *
 * This dark theme provides a modern interface that matches
 * Cerner PowerChart systems used in Australian hospitals.
 */

import { createTheme } from '@mui/material/styles';

export const cernerTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#0066CC', // Cerner signature blue
      light: '#3384D6',
      dark: '#004B99',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#00A3E0', // Light blue accent
      light: '#33B5E6',
      dark: '#0082B3',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#1E1E1E', // Dark gray (main background)
      paper: '#2D2D2D', // Lighter gray (cards, panels)
    },
    text: {
      primary: '#FFFFFF', // White (high contrast on dark)
      secondary: '#B0B0B0', // Light gray (secondary text)
    },
    success: {
      main: '#4CAF50', // Green (for positive validation)
      light: '#81C784',
      dark: '#388E3C',
    },
    error: {
      main: '#F44336', // Red (for critical alerts)
      light: '#EF5350',
      dark: '#D32F2F',
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
    divider: '#3A3A3A', // Subtle divider on dark background
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
      lineHeight: 1.2,
      color: '#FFFFFF',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      lineHeight: 1.3,
      color: '#FFFFFF',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      lineHeight: 1.4,
      color: '#FFFFFF',
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
      lineHeight: 1.4,
      color: '#FFFFFF',
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: 1.5,
      color: '#FFFFFF',
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      lineHeight: 1.6,
      color: '#FFFFFF',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
      color: '#FFFFFF',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.43,
      color: '#B0B0B0',
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      textTransform: 'none', // Sentence case (more professional)
    },
  },
  shape: {
    borderRadius: 8, // More rounding than Epic (modern appearance)
  },
  spacing: 8, // 8px base unit (Material-UI default)
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
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
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)', // Stronger shadow on dark
          backgroundColor: '#2D2D2D',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          backgroundColor: '#2D2D2D',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '& fieldset': {
              borderColor: '#3A3A3A',
            },
            '&:hover fieldset': {
              borderColor: '#00A3E0',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#0066CC',
            },
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)', // Stronger shadow
          backgroundColor: '#2D2D2D',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRadius: 0, // Full height sidebars have no rounding
          backgroundColor: '#2D2D2D',
          borderRight: '1px solid #3A3A3A',
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: '#3A3A3A',
        },
      },
    },
  },
});
