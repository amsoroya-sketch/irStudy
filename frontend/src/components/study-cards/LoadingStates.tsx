/**
 * LoadingStates Component
 * PRD-P1-006 Phase 4: Loading and Skeleton States
 *
 * ACCESSIBILITY: WCAG 2.2 AA compliant
 * - aria-busy for loading state
 * - role="status" for screen readers
 * - aria-label for context
 *
 * TDD Workflow: GREEN Phase
 * - Minimal implementation to pass Tests 28-29
 */

import React from 'react';
import { Box, Skeleton, Card, CardContent } from '@mui/material';

interface FlashcardSkeletonProps {
  count?: number;
}

export const FlashcardSkeleton: React.FC<FlashcardSkeletonProps> = ({ count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <Box
          key={index}
          data-testid="flashcard-skeleton-item"
          sx={{ mb: 2 }}
          role="status"
          aria-busy="true"
          aria-label="Loading flashcards"
        >
          <Card
            data-testid={index === 0 ? 'flashcard-skeleton' : undefined}
            sx={{ minHeight: '400px' }}
          >
            <CardContent>
              {/* Question skeleton */}
              <Skeleton variant="text" width="80%" height={40} />
              <Skeleton variant="text" width="60%" height={40} />

              {/* Answer skeleton (multiple lines) */}
              <Skeleton
                variant="rectangular"
                width="100%"
                height={200}
                sx={{ mt: 2, mb: 2 }}
              />

              {/* Citations skeleton */}
              <Skeleton variant="text" width="40%" height={30} />
              <Skeleton variant="text" width="50%" height={30} />
            </CardContent>
          </Card>
        </Box>
      ))}
    </>
  );
};
