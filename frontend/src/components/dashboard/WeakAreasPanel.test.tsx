/**
 * WeakAreasPanel Component Tests
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import WeakAreasPanel from './WeakAreasPanel';
import type { WeakArea } from '../../types/dashboard';

const mockWeakAreas: WeakArea[] = [
  {
    specialty: 'cardiology',
    accuracy_rate: 45.5,
    total_attempts: 22,
    recommended_study_cards: 8,
  },
  {
    specialty: 'respiratory',
    accuracy_rate: 58.0,
    total_attempts: 12,
    recommended_study_cards: 0,
  },
];

describe('WeakAreasPanel', () => {
  it('renders the panel heading', () => {
    render(<WeakAreasPanel weakAreas={mockWeakAreas} />);
    expect(screen.getByText('Areas for Improvement')).toBeInTheDocument();
  });

  it('renders success message when no weak areas', () => {
    render(<WeakAreasPanel weakAreas={[]} />);
    expect(screen.getByText(/No weak areas identified/i)).toBeInTheDocument();
  });

  it('renders each weak area specialty name', () => {
    render(<WeakAreasPanel weakAreas={mockWeakAreas} />);
    expect(screen.getByText('Cardiology')).toBeInTheDocument();
    expect(screen.getByText('Respiratory')).toBeInTheDocument();
  });

  it('formats underscore specialty names with title case', () => {
    const areas: WeakArea[] = [
      { specialty: 'obstetrics_gynaecology', accuracy_rate: 50, total_attempts: 10, recommended_study_cards: 5 },
    ];
    render(<WeakAreasPanel weakAreas={areas} />);
    expect(screen.getByText('Obstetrics Gynaecology')).toBeInTheDocument();
  });

  it('displays accuracy rates', () => {
    render(<WeakAreasPanel weakAreas={mockWeakAreas} />);
    expect(screen.getByText(/45\.5%/)).toBeInTheDocument();
    expect(screen.getByText(/58\.0%/)).toBeInTheDocument();
  });

  it('displays attempt counts', () => {
    render(<WeakAreasPanel weakAreas={mockWeakAreas} />);
    expect(screen.getByText(/22 attempts/)).toBeInTheDocument();
  });

  it('shows study cards recommendation when available', () => {
    render(<WeakAreasPanel weakAreas={mockWeakAreas} />);
    expect(screen.getByText(/8 study cards/)).toBeInTheDocument();
  });

  it('shows "more materials" recommendation when no study cards', () => {
    render(<WeakAreasPanel weakAreas={mockWeakAreas} />);
    expect(screen.getByText(/more materials/)).toBeInTheDocument();
  });

  it('shows threshold footnote when weak areas exist', () => {
    render(<WeakAreasPanel weakAreas={mockWeakAreas} />);
    expect(screen.getByText(/below 70%/i)).toBeInTheDocument();
  });

  it('does not show threshold footnote when no weak areas', () => {
    render(<WeakAreasPanel weakAreas={[]} />);
    expect(screen.queryByText(/below 70%/i)).not.toBeInTheDocument();
  });
});
