/**
 * OSCEPracticePlaceholder Component Tests
 * Tests for the OSCE placeholder component (TDD approach)
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { OSCEPracticePlaceholder } from './OSCEPracticePlaceholder';

describe('OSCEPracticePlaceholder', () => {
  describe('Coming Soon Message', () => {
    it('displays AI OSCE Practice Coming Soon alert', () => {
      render(<OSCEPracticePlaceholder />);

      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
      expect(alert).toHaveTextContent(/AI OSCE Practice/i);
      expect(alert).toHaveTextContent(/Coming Soon/i);
    });

    it('explains backend status', () => {
      render(<OSCEPracticePlaceholder />);

      expect(screen.getByText(/AI Patient and AI Examiner agents/i)).toBeInTheDocument();
      expect(screen.getByText(/not yet implemented/i)).toBeInTheDocument();
    });
  });

  describe('Connect Button', () => {
    it('shows disabled Connect to AI Patient button', () => {
      render(<OSCEPracticePlaceholder />);

      const button = screen.getByRole('button', { name: /connect to ai patient/i });
      expect(button).toBeInTheDocument();
      expect(button).toBeDisabled();
    });

    it('displays tooltip explaining backend requirement', async () => {
      const { container } = render(<OSCEPracticePlaceholder />);

      // Button should be wrapped in Tooltip component
      // Check for presence of disabled button (which indicates tooltip is needed)
      const button = screen.getByRole('button', { name: /connect to ai patient/i });
      expect(button).toBeDisabled();

      // Verify tooltip wrapper exists (MUI wraps in span)
      expect(button.parentElement?.tagName).toBe('SPAN');
    });
  });

  describe('Planned Features', () => {
    it('lists planned OSCE features', () => {
      render(<OSCEPracticePlaceholder />);

      expect(screen.getByText(/Real-time conversational AI patient/i)).toBeInTheDocument();
      expect(screen.getByText(/AI Examiner scoring/i)).toBeInTheDocument();
      expect(screen.getByText(/8-minute timer/i)).toBeInTheDocument();
    });
  });

  describe('Static Scenario Preview', () => {
    it('displays static OSCE scenario card', () => {
      render(<OSCEPracticePlaceholder />);

      // Should show a preview scenario
      expect(screen.getByText(/Scenario Preview/i)).toBeInTheDocument();
    });

    it('shows scenario details', () => {
      render(<OSCEPracticePlaceholder />);

      // Check for scenario metadata
      const scenarioCard = screen.getByRole('region', { name: /scenario preview/i });
      expect(scenarioCard).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<OSCEPracticePlaceholder />);

      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-live', 'polite');
    });

    it('button has aria-label', () => {
      render(<OSCEPracticePlaceholder />);

      const button = screen.getByRole('button', { name: /connect to ai patient/i });
      expect(button).toHaveAccessibleName();
    });
  });
});
