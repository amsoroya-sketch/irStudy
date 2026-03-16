/**
 * AMCRubricDisplay Component Tests
 * Tests for AMC 15-mark rubric display (TDD approach)
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AMCRubricDisplay } from './AMCRubricDisplay';
import { AMCRubricScore } from '../../types/osce';

// Mock data
const mockPassingScore: AMCRubricScore = {
  communicationSkills: 3,
  clinicalReasoning: 3,
  informationGathering: 2,
  managementPlan: 2,
  professionalismEthics: 2,
  totalScore: 12,
  passed: true,
};

const mockFailingScore: AMCRubricScore = {
  communicationSkills: 1,
  clinicalReasoning: 2,
  informationGathering: 1,
  managementPlan: 2,
  professionalismEthics: 1,
  totalScore: 7,
  passed: false,
};

const mockExcellentScore: AMCRubricScore = {
  communicationSkills: 3,
  clinicalReasoning: 4,
  informationGathering: 3,
  managementPlan: 3,
  professionalismEthics: 2,
  totalScore: 15,
  passed: true,
};

describe('AMCRubricDisplay', () => {
  describe('Domain Display', () => {
    it('displays all 5 AMC domains', () => {
      render(<AMCRubricDisplay score={mockPassingScore} />);

      // Domain names appear multiple times (domain cards + complete rubric reference)
      // so use getAllByText and verify at least one occurrence
      expect(screen.getAllByText(/Communication Skills/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/Clinical Reasoning/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/Information Gathering/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/Management Plan/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/Professionalism.*Ethics/i).length).toBeGreaterThanOrEqual(1);
    });

    it('shows correct maximum marks for each domain', () => {
      render(<AMCRubricDisplay score={mockPassingScore} />);

      // Check for chips with correct marks
      // Note: some score labels may appear multiple times (e.g., two domains with "2 / 3")
      expect(screen.getByText('3 / 3')).toBeInTheDocument(); // Communication (unique)
      expect(screen.getByText('3 / 4')).toBeInTheDocument(); // Clinical Reasoning (unique)
      // Info Gathering (2/3) AND Management Plan (2/3) both show "2 / 3"
      expect(screen.getAllByText('2 / 3').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('2 / 2')).toBeInTheDocument(); // Professionalism (unique)
    });

    it('displays current scores correctly', () => {
      render(<AMCRubricDisplay score={mockPassingScore} />);

      // Check that all score chips are displayed (using getAllByText for duplicates)
      const scoreChips = screen.getAllByText(/\d+ \/ \d+/);
      expect(scoreChips.length).toBeGreaterThanOrEqual(5); // At least 5 domains
    });
  });

  describe('Total Score Calculation', () => {
    it('displays total score out of 15', () => {
      render(<AMCRubricDisplay score={mockPassingScore} />);

      expect(screen.getByText(/Total Score: 12 \/ 15/i)).toBeInTheDocument();
    });

    it('calculates total correctly for all scores', () => {
      const { rerender } = render(<AMCRubricDisplay score={mockFailingScore} />);
      expect(screen.getByText(/Total Score: 7 \/ 15/i)).toBeInTheDocument();

      rerender(<AMCRubricDisplay score={mockExcellentScore} />);
      expect(screen.getByText(/Total Score: 15 \/ 15/i)).toBeInTheDocument();
    });
  });

  describe('Pass/Fail Threshold', () => {
    it('indicates pass when score ≥10', () => {
      render(<AMCRubricDisplay score={mockPassingScore} />);

      // Use exact text match to avoid matching "Pass Threshold" text
      expect(screen.getByText('Pass')).toBeInTheDocument();
      expect(screen.queryByText('Fail')).not.toBeInTheDocument();
    });

    it('indicates fail when score <10', () => {
      render(<AMCRubricDisplay score={mockFailingScore} />);

      expect(screen.getByText('Fail')).toBeInTheDocument();
    });

    it('uses success color for passing score', () => {
      render(<AMCRubricDisplay score={mockPassingScore} />);

      // Find the chip element by its exact label text (chip renders the label as its text content)
      const passChip = screen.getByText('Pass').closest('.MuiChip-root');
      expect(passChip).toHaveClass('MuiChip-colorSuccess');
    });

    it('uses error color for failing score', () => {
      render(<AMCRubricDisplay score={mockFailingScore} />);

      const failChip = screen.getByText('Fail').closest('.MuiChip-root');
      expect(failChip).toHaveClass('MuiChip-colorError');
    });
  });

  describe('Behavioral Anchors', () => {
    it('shows behavioral anchors for each domain', () => {
      render(<AMCRubricDisplay score={mockPassingScore} showBehavioralAnchors />);

      // "Excellent communication" appears in both Current Level and Complete Rubric Reference
      // Use getAllByText - at least one match expected
      expect(screen.getAllByText(/Excellent communication/i).length).toBeGreaterThanOrEqual(1);
    });

    it('can hide behavioral anchors when prop is false', () => {
      render(<AMCRubricDisplay score={mockPassingScore} showBehavioralAnchors={false} />);

      // Should not show detailed behavioral descriptions
      expect(screen.queryByText(/Excellent communication/i)).not.toBeInTheDocument();
    });
  });

  describe('Material-UI Components', () => {
    it('uses Material-UI Card for layout', () => {
      const { container } = render(<AMCRubricDisplay score={mockPassingScore} />);

      expect(container.querySelector('.MuiCard-root')).toBeInTheDocument();
    });

    it('uses Material-UI Typography for text', () => {
      const { container } = render(<AMCRubricDisplay score={mockPassingScore} />);

      expect(container.querySelector('.MuiTypography-root')).toBeInTheDocument();
    });

    it('uses Material-UI Chip for pass/fail indicator', () => {
      const { container } = render(<AMCRubricDisplay score={mockPassingScore} />);

      expect(container.querySelector('.MuiChip-root')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has semantic HTML structure', () => {
      render(<AMCRubricDisplay score={mockPassingScore} />);

      const rubricRegion = screen.getByRole('region', { name: /AMC.*rubric/i });
      expect(rubricRegion).toBeInTheDocument();
    });

    it('announces pass/fail status to screen readers', () => {
      render(<AMCRubricDisplay score={mockPassingScore} />);

      // The pass/fail Chip has aria-label="Passed" for screen readers
      // Find the chip element which has the accessible name
      const passChip = screen.getByText('Pass').closest('.MuiChip-root');
      expect(passChip).toBeInTheDocument();
      // The chip element has aria-label which provides accessibility
      expect(passChip).toHaveAttribute('aria-label');
    });
  });

  describe('Empty State', () => {
    it('handles zero score gracefully', () => {
      const zeroScore: AMCRubricScore = {
        communicationSkills: 0,
        clinicalReasoning: 0,
        informationGathering: 0,
        managementPlan: 0,
        professionalismEthics: 0,
        totalScore: 0,
        passed: false,
      };

      render(<AMCRubricDisplay score={zeroScore} />);

      expect(screen.getByText(/Total Score: 0 \/ 15/i)).toBeInTheDocument();
      expect(screen.getByText('Fail')).toBeInTheDocument();
    });
  });
});
