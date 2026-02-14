/**
 * Citation Panel Component
 * Displays Australian medical guideline citations with RAG verification
 *
 * FEATURES:
 * - Formats Australian medical sources (eTG, PBS, AMH, AHPRA, RACGP, NSW Health)
 * - Shows RAG verification badge
 * - Displays page numbers and sections as chips
 * - Copy-to-clipboard functionality
 * - Source-specific icons
 *
 * ACCESSIBILITY (WCAG 2.2 AA):
 * - Keyboard accessible
 * - Screen reader friendly
 * - ARIA labels and roles
 * - Sufficient colour contrast (≥4.5:1)
 */

import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Snackbar,
  Alert,
  Divider,
  Stack,
} from '@mui/material';
import {
  MenuBook as MenuBookIcon,
  LocalHospital as LocalHospitalIcon,
  VerifiedUser as VerifiedUserIcon,
  ContentCopy as ContentCopyIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

import type { CitationPanelProps, CitationSource } from '../../types/citation';
import { parseCitation } from '../../utils/citationParser';

/**
 * Get icon component for citation source
 */
function getSourceIcon(source: CitationSource): React.ReactElement {
  switch (source) {
    case 'eTG':
    case 'AMH':
    case 'RACGP':
      return <MenuBookIcon color="primary" aria-hidden="true" />;
    case 'PBS':
    case 'NSW Health':
      return <LocalHospitalIcon color="primary" aria-hidden="true" />;
    case 'AHPRA':
      return <VerifiedUserIcon color="primary" aria-hidden="true" />;
    case 'Other':
    default:
      return <MenuBookIcon color="primary" aria-hidden="true" />;
  }
}

/**
 * Citation Panel Component
 */
export const CitationPanel: React.FC<CitationPanelProps> = ({
  citations,
  showConfidence = false,
  allowCopy = true,
  'aria-label': ariaLabel = 'Australian clinical guidelines citations',
}) => {
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  /**
   * Handle copy citation to clipboard
   */
  const handleCopy = async (citation: string) => {
    try {
      await navigator.clipboard.writeText(citation);
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Failed to copy citation:', error);
    }
  };

  /**
   * Handle snackbar close
   */
  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  // Parse citations
  const parsedCitations = citations.map((citation) => {
    if (typeof citation === 'string') {
      const parsed = parseCitation(citation);
      return {
        ...parsed,
        originalText: citation,
        confidence: undefined,
      };
    } else {
      // Citation object
      const parsed = parseCitation(citation.originalText);
      return {
        ...parsed,
        originalText: citation.originalText,
        confidence: citation.confidence,
      };
    }
  });

  // Check if we should show RAG verification
  const showRagBadge = showConfidence && parsedCitations.some((c) => c.confidence !== undefined);

  return (
    <>
      <Card
        sx={{
          backgroundColor: '#f5f5f5',
          boxShadow: 1,
        }}
        role="region"
        aria-label={ariaLabel}
      >
        <CardContent>
          {/* Header */}
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
            <CheckCircleIcon color="success" fontSize="small" aria-hidden="true" />
            <Typography variant="subtitle1" sx={{ fontWeight: 600, flexGrow: 1 }}>
              Australian Clinical Guidelines
            </Typography>
            {showRagBadge && (
              <Chip
                icon={<VerifiedUserIcon />}
                label="RAG Verified"
                color="success"
                size="small"
                aria-label="Citations verified by RAG system"
              />
            )}
          </Stack>

          <Divider sx={{ mb: 2 }} />

          {/* Citations List */}
          <Stack spacing={2}>
            {parsedCitations.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No citations available
              </Typography>
            ) : (
              parsedCitations.map((citation, index) => (
                <Box key={index}>
                  <Stack direction="row" spacing={1} alignItems="flex-start">
                    {/* Source Icon */}
                    <Box sx={{ mt: 0.5 }}>{getSourceIcon(citation.source)}</Box>

                    {/* Citation Content */}
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography
                        variant="body2"
                        color="text.primary"
                        sx={{ fontWeight: 500, mb: 0.5 }}
                      >
                        {citation.displayText}
                      </Typography>

                      {/* Metadata Chips */}
                      <Stack direction="row" spacing={0.5} flexWrap="wrap" sx={{ gap: 0.5 }}>
                        {citation.page && (
                          <Chip
                            label={`Page ${citation.page}`}
                            size="small"
                            variant="outlined"
                            aria-label={`Page ${citation.page}`}
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                        )}
                        {citation.section && (
                          <Chip
                            label={`Section ${citation.section}`}
                            size="small"
                            variant="outlined"
                            aria-label={`Section ${citation.section}`}
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                        )}
                        {citation.confidence !== undefined && showConfidence && (
                          <Chip
                            label={`${Math.round(citation.confidence * 100)}% confidence`}
                            size="small"
                            color="success"
                            variant="outlined"
                            aria-label={`${Math.round(citation.confidence * 100)} percent confidence`}
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                        )}
                      </Stack>
                    </Box>

                    {/* Copy Button */}
                    {allowCopy && (
                      <Tooltip title="Copy citation">
                        <IconButton
                          size="small"
                          onClick={() => handleCopy(citation.originalText)}
                          aria-label="Copy citation to clipboard"
                          sx={{ mt: -0.5 }}
                        >
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Stack>

                  {/* Divider between citations (except last) */}
                  {index < parsedCitations.length - 1 && (
                    <Divider sx={{ mt: 2 }} />
                  )}
                </Box>
              ))
            )}
          </Stack>
        </CardContent>
      </Card>

      {/* Copy Success Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={2000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity="success"
          variant="filled"
          role="alert"
          sx={{ width: '100%' }}
        >
          Citation copied to clipboard
        </Alert>
      </Snackbar>
    </>
  );
};

export default CitationPanel;
