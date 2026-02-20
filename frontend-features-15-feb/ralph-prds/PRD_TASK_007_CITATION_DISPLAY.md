# PRD: TASK_007 - Citation Display Component
**Product Requirements Document**

---

## Document Metadata
- **PRD ID**: TASK_007
- **Product Name**: irStudy - AMC Medical Education Platform
- **Feature**: Citation Display Component with Australian Medical Sources
- **Version**: 1.0
- **Date**: 2026-02-15
- **Author**: Project Manager Coordinator
- **Status**: Ready for Implementation
- **Priority**: P1 (High - Academic Integrity)

---

## Executive Summary

### Problem Statement
Medical students need to verify the accuracy and source of clinical information provided in MCQ explanations. The current CitationPanel component (80% complete) displays basic citation information but lacks:
- Deep-dive modal for citation details
- Australian medical source verification (eTG, PBS, AMH, AHPRA, RACGP)
- RAG confidence indicators
- Direct links to source materials

### Solution Overview
Enhance CitationPanel component to provide comprehensive citation display with:
- Australian medical sources parser (eTG, PBS, AMH, AHPRA, RACGP)
- Citation details modal (full context, page numbers, sections)
- RAG verification badges (confidence scores)
- Copy-to-clipboard functionality
- Direct links to source materials (when URLs available)
- WCAG 2.2 AA accessibility

### Success Metrics
- **Citation Accuracy**: 100% of citations parsed correctly
- **User Engagement**: >60% of students view citation details
- **RAG Verification**: >80% of citations RAG-verified (>0.65 confidence)
- **Copy Rate**: >30% of students copy citations for notes
- **Test Coverage**: 85%+ for citation components

---

## User Stories & Requirements

### US-007-001: Display Citation with Australian Sources
**As a** medical student
**I want to** see the source of clinical information with Australian medical references
**So that** I can verify accuracy and learn from authoritative sources

**Acceptance Criteria**:
- [ ] Citation displayed with source name (eTG, PBS, AMH, AHPRA, RACGP)
- [ ] Page number and section displayed (if available)
- [ ] Source icon/badge for quick recognition
- [ ] Tooltip with full citation on hover
- [ ] Responsive layout (mobile, desktop)

**Australian Medical Sources**:
1. **eTG** (Therapeutic Guidelines)
2. **PBS** (Pharmaceutical Benefits Scheme)
3. **AMH** (Australian Medicines Handbook)
4. **AHPRA** (Australian Health Practitioner Regulation Agency)
5. **RACGP** (Royal Australian College of General Practitioners)
6. **NSW Health Guidelines**

**Citation Parser Implementation**:
```typescript
// frontend/src/utils/citationParser.ts
export function parseCitation(citation: string): ParsedCitation {
  const patterns = {
    eTG: /eTG:\s*(.+?)(?:\s*\(Page\s*(\d+)(?:,\s*Section\s*([\d.]+))?\))?/,
    PBS: /PBS:\s*(.+?)(?:\s*-\s*(.+))?/,
    AMH: /AMH:\s*(.+?)(?:\s*\(Page\s*(\d+)\))?/,
    AHPRA: /AHPRA:\s*(.+)/,
    RACGP: /RACGP:\s*(.+?)(?:\s*\((.+)\))?/,
  };

  for (const [source, pattern] of Object.entries(patterns)) {
    const match = citation.match(pattern);
    if (match) {
      return {
        source,
        displayText: match[1],
        page: match[2] || null,
        section: match[3] || null,
      };
    }
  }

  return { source: 'Other', displayText: citation };
}
```

---

### US-007-002: Citation Details Modal
**As a** medical student
**I want to** view full citation details in a modal
**So that** I can read the complete context and references

**Acceptance Criteria**:
- [ ] "View Details" button on each citation
- [ ] Modal opens with full citation context
- [ ] Page number and section clearly displayed
- [ ] Link to source (if URL available)
- [ ] Close modal with Escape key or X button
- [ ] Focus trapped in modal (accessibility)
- [ ] Mobile-friendly layout

**Component Implementation**:
```typescript
// frontend/src/components/citations/CitationDetailsModal.tsx
interface CitationDetailsModalProps {
  citation: ParsedCitation;
  open: boolean;
  onClose: () => void;
}

export const CitationDetailsModal: React.FC<CitationDetailsModalProps> = ({
  citation,
  open,
  onClose,
}) => {
  return (
    <Modal open={open} onClose={onClose}>
      <Card sx={{ maxWidth: 600, mx: 'auto', mt: 8, p: 3 }}>
        <Typography variant="h6">{citation.source}</Typography>
        <Typography variant="body1">{citation.displayText}</Typography>

        {/* Page and section */}
        {citation.page && (
          <Chip label={`Page ${citation.page}`} sx={{ mt: 2 }} />
        )}
        {citation.section && (
          <Chip label={`Section ${citation.section}`} sx={{ mt: 2, ml: 1 }} />
        )}

        {/* Full context (if available from RAG) */}
        {citation.fullContext && (
          <Typography variant="body2" sx={{ mt: 2 }}>
            {citation.fullContext}
          </Typography>
        )}

        {/* Link to source */}
        {citation.url && (
          <Button
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
            startIcon={<OpenInNewIcon />}
            sx={{ mt: 2 }}
          >
            View Source
          </Button>
        )}

        <Button onClick={onClose} sx={{ mt: 3 }}>
          Close
        </Button>
      </Card>
    </Modal>
  );
};
```

---

### US-007-003: RAG Verification Badge
**As a** medical student
**I want to** see RAG verification status for citations
**So that** I can trust the information accuracy

**Acceptance Criteria**:
- [ ] RAG verification badge displayed when enabled
- [ ] Confidence score shown (0-100%)
- [ ] Color-coded: Green (>80%), Yellow (65-80%), Red (<65%)
- [ ] Tooltip explains confidence meaning
- [ ] Only displayed for RAG-verified citations

**Implementation**:
```typescript
{showConfidence && citation.ragVerified && (
  <Chip
    label={`RAG Verified (${Math.round(citation.confidence * 100)}%)`}
    color={citation.confidence > 0.8 ? 'success' : citation.confidence > 0.65 ? 'warning' : 'error'}
    size="small"
    icon={<VerifiedIcon />}
  />
)}
```

---

### US-007-004: Copy to Clipboard
**As a** medical student
**I want to** copy citation to clipboard
**So that** I can paste it into my notes

**Acceptance Criteria**:
- [ ] Copy button on each citation
- [ ] Clipboard icon indicates action
- [ ] Success toast after copy
- [ ] Citation formatted as plain text
- [ ] Keyboard shortcut (Ctrl+C after clicking citation)

**Implementation**:
```typescript
const handleCopy = async () => {
  const citationText = `${citation.source}: ${citation.displayText}${
    citation.page ? ` (Page ${citation.page})` : ''
  }`;

  await navigator.clipboard.writeText(citationText);
  toast.success('Citation copied to clipboard');
};
```

---

## Technical Specifications

### Enhanced CitationPanel Component

```typescript
// frontend/src/components/citations/CitationPanel.tsx (ENHANCED)
interface CitationPanelProps {
  citations: string[];  // Raw citation strings from backend
  showConfidence?: boolean;  // Show RAG verification
  allowCopy?: boolean;  // Allow copy to clipboard
}

export const CitationPanel: React.FC<CitationPanelProps> = ({
  citations,
  showConfidence = false,
  allowCopy = true,
}) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<ParsedCitation | null>(null);

  // Parse citations
  const parsedCitations = citations.map(parseCitation);

  return (
    <>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            References
          </Typography>

          {parsedCitations.map((citation, idx) => (
            <Box key={idx} sx={{ mb: 2 }}>
              {/* Source badge */}
              <Chip
                label={citation.source}
                color="primary"
                size="small"
                icon={getSourceIcon(citation.source)}
              />

              {/* Citation text */}
              <Typography variant="body2" sx={{ mt: 1 }}>
                {citation.displayText}
              </Typography>

              {/* Page/section chips */}
              {citation.page && (
                <Chip label={`Page ${citation.page}`} size="small" sx={{ mr: 1 }} />
              )}
              {citation.section && (
                <Chip label={`Section ${citation.section}`} size="small" />
              )}

              {/* RAG verification badge */}
              {showConfidence && citation.ragVerified && (
                <Chip
                  label={`Verified (${Math.round(citation.confidence * 100)}%)`}
                  color="success"
                  size="small"
                  icon={<VerifiedIcon />}
                  sx={{ ml: 1 }}
                />
              )}

              {/* Actions */}
              <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                {/* View details button */}
                <IconButton
                  size="small"
                  onClick={() => {
                    setSelectedCitation(citation);
                    setModalOpen(true);
                  }}
                  aria-label="View citation details"
                >
                  <InfoIcon />
                </IconButton>

                {/* Copy button */}
                {allowCopy && (
                  <IconButton
                    size="small"
                    onClick={() => handleCopy(citation)}
                    aria-label="Copy citation to clipboard"
                  >
                    <ContentCopyIcon />
                  </IconButton>
                )}
              </Stack>
            </Box>
          ))}
        </CardContent>
      </Card>

      {/* Citation details modal */}
      <CitationDetailsModal
        citation={selectedCitation}
        open={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </>
  );
};
```

### Australian Medical Source URLs

```typescript
// frontend/src/utils/citationSources.ts
export const AUSTRALIAN_MEDICAL_SOURCES = {
  eTG: {
    name: 'Therapeutic Guidelines',
    baseUrl: 'https://www.tg.org.au',
    icon: 'BookIcon',
  },
  PBS: {
    name: 'Pharmaceutical Benefits Scheme',
    baseUrl: 'https://www.pbs.gov.au',
    icon: 'MedicationIcon',
  },
  AMH: {
    name: 'Australian Medicines Handbook',
    baseUrl: 'https://www.amh.net.au',
    icon: 'LocalPharmacyIcon',
  },
  AHPRA: {
    name: 'Australian Health Practitioner Regulation Agency',
    baseUrl: 'https://www.ahpra.gov.au',
    icon: 'GavelIcon',
  },
  RACGP: {
    name: 'Royal Australian College of General Practitioners',
    baseUrl: 'https://www.racgp.org.au',
    icon: 'SchoolIcon',
  },
};
```

---

## Testing Requirements

### Unit Tests

**Coverage Target**: 85%+

**Test Cases**:
```typescript
describe('citationParser', () => {
  it('parses eTG citations correctly', () => {
    const citation = 'eTG: Cardiovascular Guidelines (Page 42, Section 3.2)';
    const parsed = parseCitation(citation);

    expect(parsed.source).toBe('eTG');
    expect(parsed.displayText).toBe('Cardiovascular Guidelines');
    expect(parsed.page).toBe('42');
    expect(parsed.section).toBe('3.2');
  });

  it('parses PBS citations correctly', () => {
    const citation = 'PBS: Salbutamol - Asthma medication';
    const parsed = parseCitation(citation);

    expect(parsed.source).toBe('PBS');
    expect(parsed.displayText).toContain('Salbutamol');
  });
});

describe('CitationPanel', () => {
  it('displays all citations', () => {
    const citations = [
      'eTG: Test Citation 1',
      'PBS: Test Citation 2',
    ];

    render(<CitationPanel citations={citations} />);

    expect(screen.getByText(/Test Citation 1/)).toBeInTheDocument();
    expect(screen.getByText(/Test Citation 2/)).toBeInTheDocument();
  });

  it('copies citation to clipboard', async () => {
    const citations = ['eTG: Test Citation'];
    render(<CitationPanel citations={citations} allowCopy />);

    fireEvent.click(screen.getByLabelText(/copy citation/i));

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalled();
    });
  });

  it('opens modal on view details', () => {
    const citations = ['eTG: Test Citation'];
    render(<CitationPanel citations={citations} />);

    fireEvent.click(screen.getByLabelText(/view citation details/i));

    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });
});
```

---

## Success Criteria

- ✅ All Australian sources parsed correctly (eTG, PBS, AMH, AHPRA, RACGP)
- ✅ Citation details modal functional
- ✅ RAG verification badges displayed (when enabled)
- ✅ Copy to clipboard working
- ✅ Links to source (when URLs available)
- ✅ WCAG 2.2 AA compliant
- ✅ Test coverage ≥85%
- ✅ 0 TypeScript errors

---

## Implementation Timeline

**Sprint 2 - Days 1-2 (4 hours)**:
- Enhance CitationPanel component
- Create CitationDetailsModal
- Implement citation parser
- Add copy-to-clipboard
- Write unit tests

---

**Document Status**: ✅ Ready for Implementation
**Last Updated**: 2026-02-15
