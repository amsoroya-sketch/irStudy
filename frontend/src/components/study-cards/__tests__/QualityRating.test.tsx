import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QualityRating } from '../QualityRating';

describe('QualityRating', () => {
  it('Test 45: should display 6 rating buttons (0-5)', () => {
    render(<QualityRating onRate={vi.fn()} />);

    expect(screen.getByRole('button', { name: /blackout/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /wrong/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /hard/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /ok/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /easy/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /perfect/i })).toBeInTheDocument();
  });

  it('Test 46: should call onRate with quality 0 when Blackout is clicked', async () => {
    const onRate = vi.fn();
    render(<QualityRating onRate={onRate} />);

    await userEvent.click(screen.getByRole('button', { name: /blackout/i }));

    expect(onRate).toHaveBeenCalledWith(0);
  });

  it('Test 47: should call onRate with quality 5 when Perfect is clicked', async () => {
    const onRate = vi.fn();
    render(<QualityRating onRate={onRate} />);

    await userEvent.click(screen.getByRole('button', { name: /perfect/i }));

    expect(onRate).toHaveBeenCalledWith(5);
  });

  it('Test 48: should trigger keyboard shortcuts (0-5 keys)', async () => {
    const onRate = vi.fn();
    render(<QualityRating onRate={onRate} />);

    // Simulate keypress '0'
    await userEvent.keyboard('0');
    expect(onRate).toHaveBeenCalledWith(0);

    // Simulate keypress '5'
    await userEvent.keyboard('5');
    expect(onRate).toHaveBeenCalledWith(5);
  });

  it('Test 49: should display color-coded buttons', () => {
    render(<QualityRating onRate={vi.fn()} />);

    // Blackout (0) and Wrong (1) should be red
    const blackoutButton = screen.getByRole('button', { name: /blackout/i });
    expect(blackoutButton).toHaveStyle({ backgroundColor: '#f44336' });

    // Perfect (5) should be green
    const perfectButton = screen.getByRole('button', { name: /perfect/i });
    expect(perfectButton).toHaveStyle({ backgroundColor: '#4caf50' });
  });

  it('Test 50: should be disabled when disabled prop is true', () => {
    render(<QualityRating onRate={vi.fn()} disabled={true} />);

    const blackoutButton = screen.getByRole('button', { name: /blackout/i });
    expect(blackoutButton).toBeDisabled();

    const perfectButton = screen.getByRole('button', { name: /perfect/i });
    expect(perfectButton).toBeDisabled();
  });

  it('Test 51: should display helper text explaining the rating scale', () => {
    render(<QualityRating onRate={vi.fn()} />);

    expect(screen.getByText(/how well did you recall/i)).toBeInTheDocument();
  });
});
