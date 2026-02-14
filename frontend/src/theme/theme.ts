/**
 * theme.ts - Material-UI Custom Theme Configuration
 * Responsive breakpoints and typography for mobile-first design
 */

import { createTheme, responsiveFontSizes } from '@mui/material/styles';

// Create base theme with custom breakpoints
const baseTheme = createTheme({
  breakpoints: {
    values: {
      xs: 320,   // mobile small
      sm: 768,   // tablet
      md: 1024,  // desktop small
      lg: 1280,  // desktop large
      xl: 1920,  // desktop XL
    },
  },
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#dc004e',
      light: '#f73378',
      dark: '#9a0036',
      contrastText: '#ffffff',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
    },
    success: {
      main: '#4caf50',
      light: '#81c784',
      dark: '#388e3c',
    },
    error: {
      main: '#f44336',
      light: '#e57373',
      dark: '#d32f2f',
    },
    warning: {
      main: '#ff9800',
      light: '#ffb74d',
      dark: '#f57c00',
    },
    info: {
      main: '#2196f3',
      light: '#64b5f6',
      dark: '#1976d2',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    // Responsive typography - will be enhanced by responsiveFontSizes
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem', // Will scale to 1.25rem on mobile
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1rem', // Will scale to 0.875rem on mobile
      fontWeight: 500,
      lineHeight: 1.6,
    },
    body1: {
      fontSize: '1rem', // Will scale to 0.875rem on mobile
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.43,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      textTransform: 'uppercase',
      letterSpacing: '0.02857em',
    },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.66,
    },
    overline: {
      fontSize: '0.75rem',
      fontWeight: 500,
      textTransform: 'uppercase',
      letterSpacing: '0.08333em',
    },
  },
  spacing: 8, // Base spacing unit (8px)
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
          // Responsive padding
          '@media (max-width: 768px)': {
            padding: '8px 16px',
            fontSize: '0.875rem',
          },
          '@media (min-width: 769px)': {
            padding: '10px 24px',
            fontSize: '1rem',
          },
        },
        sizeLarge: {
          '@media (max-width: 768px)': {
            padding: '10px 20px',
          },
          '@media (min-width: 769px)': {
            padding: '12px 32px',
          },
        },
        sizeSmall: {
          padding: '6px 12px',
          fontSize: '0.8125rem',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          // Reduced elevation on mobile
          '@media (max-width: 768px)': {
            boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.12), 0px 1px 2px rgba(0, 0, 0, 0.24)',
          },
          '@media (min-width: 769px)': {
            boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1), 0px 4px 8px rgba(0, 0, 0, 0.1)',
          },
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          // Responsive padding
          '@media (max-width: 768px)': {
            padding: '12px',
            '&:last-child': {
              paddingBottom: '12px',
            },
          },
          '@media (min-width: 769px)': {
            padding: '16px',
            '&:last-child': {
              paddingBottom: '16px',
            },
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          // Larger touch target on mobile (44px minimum)
          '@media (max-width: 768px)': {
            padding: '12px',
            minWidth: '44px',
            minHeight: '44px',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          // Responsive chip sizing
          '@media (max-width: 768px)': {
            height: '28px',
            fontSize: '0.75rem',
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          // Responsive table cell padding
          '@media (max-width: 768px)': {
            padding: '8px 4px',
            fontSize: '0.8125rem',
          },
          '@media (min-width: 769px)': {
            padding: '16px',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          // Ensure touch-friendly input fields
          '& .MuiInputBase-root': {
            '@media (max-width: 768px)': {
              fontSize: '16px', // Prevents zoom on iOS
              minHeight: '44px',
            },
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          // Full-screen dialogs on mobile
          '@media (max-width: 768px)': {
            margin: '16px',
            maxHeight: 'calc(100% - 32px)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          // Responsive AppBar height
          '@media (max-width: 768px)': {
            minHeight: '56px',
          },
          '@media (min-width: 769px)': {
            minHeight: '64px',
          },
        },
      },
    },
    MuiToolbar: {
      styleOverrides: {
        root: {
          '@media (max-width: 768px)': {
            minHeight: '56px',
            paddingLeft: '8px',
            paddingRight: '8px',
          },
          '@media (min-width: 769px)': {
            minHeight: '64px',
            paddingLeft: '24px',
            paddingRight: '24px',
          },
        },
      },
    },
  },
});

// Apply responsive font sizes automatically
const theme = responsiveFontSizes(baseTheme, {
  breakpoints: ['xs', 'sm', 'md', 'lg', 'xl'],
  factor: 2, // Scaling factor for font size adjustments
});

export default theme;
