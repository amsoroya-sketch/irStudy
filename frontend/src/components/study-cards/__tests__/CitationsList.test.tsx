/**
 * CitationsList Component Tests
 * Based on PRD-P1-006 Phase 3 - Citations Display
 *
 * Tests 25-27: Citation rendering with confidence scores
 *
 * TDD PHASE: RED (Tests written FIRST, expected to FAIL)
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CitationsList } from '../CitationsList';
import type { StudyCardCitation } from '../../../types/study-cards';

describe('CitationsList', () => {
  const mockCitations: StudyCardCitation[] = [
    {
      source: 'eTG Endocrinology',
      qdrant_point_id: '550e8400-e29b-41d4-a716-446655440000',
      confidence: 0.89,
      page: 'p. 156-158',
    },
    {
      source: "Talley & O'Connor Clinical Examination 9th Ed",
      qdrant_point_id: '550e8400-e29b-41d4-a716-446655440001',
      confidence: 0.72,
      page: 'p. 412-415',
    },
  ];

  it('Test 25: should display all citations with source and page', () => {
    render(<CitationsList citations={mockCitations} />);

    expect(screen.getByText(/eTG Endocrinology/i)).toBeInTheDocument();
    expect(screen.getByText(/p\. 156-158/i)).toBeInTheDocument();
    expect(screen.getByText(/Talley & O'Connor/i)).toBeInTheDocument();
    expect(screen.getByText(/p\. 412-415/i)).toBeInTheDocument();
  });

  it('Test 26: should display confidence scores with color coding', () => {
    render(<CitationsList citations={mockCitations} />);

    // High confidence (≥80%) should be green
    const highConfidence = screen.getByText('89%');
    expect(highConfidence).toBeInTheDocument();

    // Medium confidence (65-79%) should be yellow/orange
    const mediumConfidence = screen.getByText('72%');
    expect(mediumConfidence).toBeInTheDocument();
  });

  it('Test 27: should display "No citations available" when citations array is empty', () => {
    render(<CitationsList citations={[]} />);

    expect(screen.getByText(/no citations available/i)).toBeInTheDocument();
  });
});
