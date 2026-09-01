/**
 * ScenarioBrief tests (PRD-EMR-PRACTICE-003)
 *
 * Verifies the scenario brief panel renders the presenting complaint and the
 * student's task so the challenge is visible before documenting.
 */

import { it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ScenarioBrief } from '../ScenarioBrief';

it('Test 7: renders presenting complaint and task', () => {
  render(
    <ScenarioBrief
      presentingComplaint="Central chest pain 40 min"
      task="Document assessment and initial management."
    />
  );
  expect(screen.getByText(/central chest pain/i)).toBeInTheDocument();
  expect(screen.getByText(/document assessment/i)).toBeInTheDocument();
});
