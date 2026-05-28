/**
 * MobileBottomNav Component
 * Bottom navigation bar for mobile devices (<768px)
 *
 * ACCESSIBILITY:
 * - role="navigation" with aria-label for screen readers
 * - Active item communicated via aria-current
 * - Touch targets ≥56px height (WCAG 2.2)
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  BottomNavigation,
  BottomNavigationAction,
  Paper,
} from '@mui/material';
import {
  Home as HomeIcon,
  Quiz as QuizIcon,
  BarChart as DashboardIcon,
  Person as PersonIcon,
  School as SchoolIcon,
  MenuBook as MenuBookIcon,
} from '@mui/icons-material';
import { useResponsive } from '../../hooks/useResponsive';

const NAV_ITEMS = [
  { label: 'Home', value: '/dashboard', icon: <HomeIcon /> },
  { label: 'Practice', value: '/mcqs', icon: <QuizIcon /> },
  { label: 'Notes', value: '/html-notes', icon: <MenuBookIcon /> },
  { label: 'Progress', value: '/performance', icon: <DashboardIcon /> },
  { label: 'Profile', value: '/profile', icon: <PersonIcon /> },
] as const;

/**
 * Mobile Bottom Navigation
 *
 * Shown only on mobile devices (<768px). Routes to main sections of the app.
 * Hides on tablet and desktop (use sidebar navigation instead).
 */
const MobileBottomNav: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile } = useResponsive();

  // Derive active tab from current path
  const getActiveValue = (pathname: string): string => {
    const match = NAV_ITEMS.find((item) => pathname.startsWith(item.value));
    return match ? match.value : '/dashboard';
  };

  const [value, setValue] = useState(() => getActiveValue(location.pathname));

  // Keep active tab in sync with browser navigation (back/forward)
  useEffect(() => {
    setValue(getActiveValue(location.pathname));
  }, [location.pathname]);

  // Hidden on desktop — return null avoids rendering overhead
  if (!isMobile) return null;

  const handleChange = (_event: React.SyntheticEvent, newValue: string) => {
    setValue(newValue);
    navigate(newValue);
  };

  return (
    <Paper
      elevation={8}
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: (theme) => theme.zIndex.appBar,
        // Safe area for notched phones (iOS)
        paddingBottom: 'env(safe-area-inset-bottom)',
      }}
    >
      <BottomNavigation
        value={value}
        onChange={handleChange}
        aria-label="Bottom navigation"
        role="navigation"
        sx={{
          height: 56, // Thumb-friendly height; touch targets ≥44px each
          '& .MuiBottomNavigationAction-root': {
            minWidth: 64,
            padding: '6px 0',
            '&.Mui-selected': {
              paddingTop: '6px',
            },
          },
        }}
      >
        {NAV_ITEMS.map((item) => (
          <BottomNavigationAction
            key={item.value}
            label={item.label}
            value={item.value}
            icon={item.icon}
            aria-current={value === item.value ? 'page' : undefined}
            aria-label={item.label}
          />
        ))}
      </BottomNavigation>
    </Paper>
  );
};

export default MobileBottomNav;
