/**
 * useResponsive.ts - Custom Hooks for Responsive Design
 * Provides utilities to detect device type and current breakpoint
 */

import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import { Breakpoint } from '@mui/material/styles';

/**
 * Hook to detect device type based on screen size
 * @returns Object with boolean flags for device types
 *
 * @example
 * const { isMobile, isTablet, isDesktop } = useResponsive();
 * return isMobile ? <MobileView /> : <DesktopView />;
 */
export function useResponsive() {
  const theme = useTheme();

  // Mobile: screens < 768px (xs)
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Tablet: screens >= 768px and < 1024px (sm to md)
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));

  // Desktop: screens >= 1024px (md and up)
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));

  // Additional granular breakpoints
  const isXSmall = useMediaQuery(theme.breakpoints.only('xs'));  // 320-767px
  const isSmall = useMediaQuery(theme.breakpoints.only('sm'));   // 768-1023px
  const isMedium = useMediaQuery(theme.breakpoints.only('md'));  // 1024-1279px
  const isLarge = useMediaQuery(theme.breakpoints.only('lg'));   // 1280-1919px
  const isXLarge = useMediaQuery(theme.breakpoints.only('xl'));  // 1920px+

  return {
    // Primary device categories
    isMobile,
    isTablet,
    isDesktop,

    // Granular breakpoints
    isXSmall,
    isSmall,
    isMedium,
    isLarge,
    isXLarge,

    // Helper flags
    isTouchDevice: isMobile || isTablet,
    isPortrait: window.matchMedia('(orientation: portrait)').matches,
    isLandscape: window.matchMedia('(orientation: landscape)').matches,
  };
}

/**
 * Hook to get the current active breakpoint name
 * @returns Current breakpoint name ('xs' | 'sm' | 'md' | 'lg' | 'xl')
 *
 * @example
 * const breakpoint = useBreakpoint();
 * const spacing = breakpoint === 'xs' ? 1 : breakpoint === 'sm' ? 2 : 3;
 */
export function useBreakpoint(): Breakpoint {
  const theme = useTheme();

  const isXs = useMediaQuery(theme.breakpoints.only('xs'));
  const isSm = useMediaQuery(theme.breakpoints.only('sm'));
  const isMd = useMediaQuery(theme.breakpoints.only('md'));
  const isLg = useMediaQuery(theme.breakpoints.only('lg'));
  const isXl = useMediaQuery(theme.breakpoints.only('xl'));

  if (isXs) return 'xs';
  if (isSm) return 'sm';
  if (isMd) return 'md';
  if (isLg) return 'lg';
  if (isXl) return 'xl';

  // Fallback (should never happen)
  return 'md';
}

/**
 * Hook to check if screen size is above a specific breakpoint
 * @param breakpoint - Breakpoint to check ('xs' | 'sm' | 'md' | 'lg' | 'xl')
 * @returns Boolean indicating if screen is above the breakpoint
 *
 * @example
 * const isAboveMd = useBreakpointUp('md');
 * return isAboveMd ? <ComplexLayout /> : <SimpleLayout />;
 */
export function useBreakpointUp(breakpoint: Breakpoint): boolean {
  const theme = useTheme();
  return useMediaQuery(theme.breakpoints.up(breakpoint));
}

/**
 * Hook to check if screen size is below a specific breakpoint
 * @param breakpoint - Breakpoint to check ('xs' | 'sm' | 'md' | 'lg' | 'xl')
 * @returns Boolean indicating if screen is below the breakpoint
 *
 * @example
 * const isBelowSm = useBreakpointDown('sm');
 * return isBelowSm ? <MobileMenu /> : <DesktopMenu />;
 */
export function useBreakpointDown(breakpoint: Breakpoint): boolean {
  const theme = useTheme();
  return useMediaQuery(theme.breakpoints.down(breakpoint));
}

/**
 * Hook to get responsive spacing based on current breakpoint
 * @returns Spacing value for the current breakpoint
 *
 * @example
 * const spacing = useResponsiveSpacing();
 * return <Box p={spacing}>Content</Box>;
 */
export function useResponsiveSpacing(): number {
  const { isMobile, isTablet } = useResponsive();

  if (isMobile) return 1;    // 8px
  if (isTablet) return 2;    // 16px
  return 3;                  // 24px
}

/**
 * Hook to determine optimal grid columns based on screen size
 * @param maxColumns - Maximum columns for desktop (default: 12)
 * @returns Number of columns for current breakpoint
 *
 * @example
 * const columns = useResponsiveColumns();
 * return <Grid container columns={columns}>...</Grid>;
 */
export function useResponsiveColumns(maxColumns: number = 12): number {
  const { isMobile, isTablet } = useResponsive();

  if (isMobile) return 4;                    // 4 columns on mobile
  if (isTablet) return 8;                    // 8 columns on tablet
  return maxColumns;                         // Full columns on desktop
}
