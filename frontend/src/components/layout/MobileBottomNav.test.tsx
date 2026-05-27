/**
 * MobileBottomNav Component Tests
 * Tests for mobile bottom navigation bar (visible only on mobile <768px)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import MobileBottomNav from './MobileBottomNav';

// ── Mock react-router-dom navigate ──────────────────────────────────────────
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// ── Mock useResponsive hook ──────────────────────────────────────────────────
const mockUseResponsive = vi.fn();
vi.mock('../../hooks/useResponsive', () => ({
  useResponsive: () => mockUseResponsive(),
}));

// Helper: render inside MemoryRouter to provide location context
const renderNav = (initialPath = '/dashboard') => {
  mockNavigate.mockClear();
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <MobileBottomNav />
    </MemoryRouter>,
  );
};

describe('MobileBottomNav', () => {
  // ── Visibility ─────────────────────────────────────────────────────────────
  describe('visibility', () => {
    it('renders when isMobile is true', () => {
      mockUseResponsive.mockReturnValue({ isMobile: true });
      renderNav();
      expect(screen.getByRole('navigation', { name: /bottom navigation/i })).toBeInTheDocument();
    });

    it('does not render when isMobile is false (desktop)', () => {
      mockUseResponsive.mockReturnValue({ isMobile: false });
      renderNav();
      expect(screen.queryByRole('navigation', { name: /bottom navigation/i })).not.toBeInTheDocument();
    });
  });

  // ── Navigation items ───────────────────────────────────────────────────────
  describe('navigation items', () => {
    beforeEach(() => {
      mockUseResponsive.mockReturnValue({ isMobile: true });
    });

    it('renders all 5 navigation labels', () => {
      renderNav();
      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Practice')).toBeInTheDocument();
      expect(screen.getByText('Study')).toBeInTheDocument();
      expect(screen.getByText('Progress')).toBeInTheDocument();
      expect(screen.getByText('Profile')).toBeInTheDocument();
    });

    it('marks "Home" as active on /dashboard route', () => {
      renderNav('/dashboard');
      const homeAction = screen.getByLabelText('Home');
      expect(homeAction).toHaveAttribute('aria-current', 'page');
    });

    it('marks "Practice" as active on /mcqs route', () => {
      renderNav('/mcqs');
      const practiceAction = screen.getByLabelText('Practice');
      expect(practiceAction).toHaveAttribute('aria-current', 'page');
    });

    it('marks "Study" as active on /study-cards route', () => {
      renderNav('/study-cards');
      const studyAction = screen.getByLabelText('Study');
      expect(studyAction).toHaveAttribute('aria-current', 'page');
    });

    it('marks "Progress" as active on /performance route', () => {
      renderNav('/performance');
      const progressAction = screen.getByLabelText('Progress');
      expect(progressAction).toHaveAttribute('aria-current', 'page');
    });

    it('non-active items do not have aria-current="page"', () => {
      renderNav('/dashboard');
      const practiceAction = screen.getByLabelText('Practice');
      expect(practiceAction).not.toHaveAttribute('aria-current', 'page');
    });
  });

  // ── Navigation behaviour ───────────────────────────────────────────────────
  describe('navigation behaviour', () => {
    beforeEach(() => {
      mockUseResponsive.mockReturnValue({ isMobile: true });
    });

    it('calls navigate with /mcqs when Practice is clicked', () => {
      renderNav('/dashboard');
      fireEvent.click(screen.getByText('Practice'));
      expect(mockNavigate).toHaveBeenCalledWith('/mcqs');
    });

    it('calls navigate with /study-cards when Study is clicked', () => {
      renderNav('/dashboard');
      fireEvent.click(screen.getByText('Study'));
      expect(mockNavigate).toHaveBeenCalledWith('/study-cards');
    });

    it('calls navigate with /performance when Progress is clicked', () => {
      renderNav('/dashboard');
      fireEvent.click(screen.getByText('Progress'));
      expect(mockNavigate).toHaveBeenCalledWith('/performance');
    });

    it('calls navigate with /dashboard when Home is clicked', () => {
      renderNav('/mcqs');
      fireEvent.click(screen.getByText('Home'));
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  // ── Accessibility ──────────────────────────────────────────────────────────
  describe('accessibility', () => {
    beforeEach(() => {
      mockUseResponsive.mockReturnValue({ isMobile: true });
    });

    it('has role="navigation" landmark', () => {
      renderNav();
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    it('has accessible aria-label on navigation landmark', () => {
      renderNav();
      expect(screen.getByRole('navigation', { name: /bottom navigation/i })).toBeInTheDocument();
    });

    it('each nav action has an aria-label', () => {
      renderNav();
      expect(screen.getByLabelText('Home')).toBeInTheDocument();
      expect(screen.getByLabelText('Practice')).toBeInTheDocument();
      expect(screen.getByLabelText('Study')).toBeInTheDocument();
      expect(screen.getByLabelText('Progress')).toBeInTheDocument();
      expect(screen.getByLabelText('Profile')).toBeInTheDocument();
    });
  });
});
