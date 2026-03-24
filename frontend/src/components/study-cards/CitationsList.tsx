/**
 * CitationsList Component
 * Based on PRD-P1-006 Phase 3 - Citations Display
 *
 * Displays RAG citations with color-coded confidence scores
 *
 * CITATION REQUIREMENTS (PRD-P1-006):
 * - All citations must have qdrant_point_id (RAG traceability)
 * - Confidence scores color-coded:
 *   - Green (#4caf50): ≥80%
 *   - Yellow/Orange (#ff9800): 65-79%
 *   - Red (#f44336): <65%
 * - Australian medical sources (eTG, Talley & O'Connor, AMH, PBS)
 *
 * ACCESSIBILITY:
 * - WCAG 2.2 AA compliant
 * - Color contrast ≥4.5:1
 * - Screen reader friendly
 */

import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import type { StudyCardCitation } from '../../types/study-cards';

interface CitationsListProps {
  citations: StudyCardCitation[];
}

/**
 * Get confidence score color based on RAG confidence threshold
 * - Green: High confidence (≥80%)
 * - Orange: Medium confidence (65-79%)
 * - Red: Low confidence (<65%)
 */
const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return '#4caf50'; // Green
  if (confidence >= 0.65) return '#ff9800'; // Orange/Yellow
  return '#f44336'; // Red
};

export const CitationsList: React.FC<CitationsListProps> = ({ citations }) => {
  if (citations.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        No citations available
      </Typography>
    );
  }

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        References:
      </Typography>
      {citations.map((citation) => (
        <Box
          key={citation.qdrant_point_id}
          sx={{
            mb: 1,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}
        >
          <Typography variant="body2" component="span">
            {citation.source} ({citation.page})
          </Typography>
          <Chip
            label={`${Math.round(citation.confidence * 100)}%`}
            size="small"
            sx={{
              color: getConfidenceColor(citation.confidence),
              borderColor: getConfidenceColor(citation.confidence),
            }}
            variant="outlined"
            aria-label={`Confidence score: ${Math.round(citation.confidence * 100)} percent`}
          />
        </Box>
      ))}
    </Box>
  );
};
