/**
 * StatCard Component Tests
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import StatCard from './StatCard';

describe('StatCard', () => {
  it('renders title', () => {
    render(<StatCard title="MCQ Attempts" value={42} />);
    expect(screen.getByText('MCQ Attempts')).toBeInTheDocument();
  });

  it('renders numeric value', () => {
    render(<StatCard title="Test" value={123} />);
    expect(screen.getByText('123')).toBeInTheDocument();
  });

  it('renders string value', () => {
    render(<StatCard title="Test" value="95.5%" />);
    expect(screen.getByText('95.5%')).toBeInTheDocument();
  });

  it('renders subtitle when provided', () => {
    render(<StatCard title="Test" value={10} subtitle="Some subtitle text" />);
    expect(screen.getByText('Some subtitle text')).toBeInTheDocument();
  });

  it('does not render subtitle when not provided', () => {
    render(<StatCard title="Test" value={10} />);
    expect(screen.queryByRole('paragraph')).not.toBeInTheDocument();
  });

  it('renders with default color without crashing', () => {
    expect(() => render(<StatCard title="Test" value={0} />)).not.toThrow();
  });

  it('renders with all color variants', () => {
    const colors = ['primary', 'secondary', 'success', 'error', 'warning', 'info'] as const;
    colors.forEach((color) => {
      const { unmount } = render(<StatCard title="Test" value={1} color={color} />);
      expect(screen.getByText('Test')).toBeInTheDocument();
      unmount();
    });
  });
});
