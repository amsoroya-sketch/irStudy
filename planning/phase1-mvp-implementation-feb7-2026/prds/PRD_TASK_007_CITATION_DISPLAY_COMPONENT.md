# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_007 - Citation Display Component (3-4 hours)

**EXECUTE NOW**:

```bash
cd /home/dev/Development/irStudy/frontend

# Create Citation Panel component
mkdir -p src/components/citations

cat > src/components/citations/CitationPanel.tsx <<'EOF'
// Citation panel component will be implemented here
EOF

# Verify TypeScript
npx tsc --noEmit && echo "✅ TypeScript: 0 errors" || echo "❌ TypeScript errors"
```

**DO NOT**:
- ❌ Ask "Would you like me to implement the copy-to-clipboard feature?"
- ❌ Ask "Should I add Australian guideline formatting?"
- ❌ Wait for approval
- ❌ Ask "Which citation format should I use?"

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📋 Metadata

- **Week:** 2
- **Day:** 3 (Feb 16, 2026)
- **Duration:** 3-4 hours
- **Priority:** P1-High
- **Dependencies:** TASK_006 (Quiz Interface)
- **Owner:** flutter-desktop-expert (React/TypeScript)
- **Status:** 🟡 Not Started

---

## 🎯 Objectives

1. **Create CitationPanel component** with formatted Australian guidelines
2. **Implement citation formatting** for eTG, PBS, AMH, AHPRA sources
3. **Add page number linking** (where applicable)
4. **Display RAG verification badge** (confidence score >0.65)
5. **Implement copy-to-clipboard** functionality
6. **TypeScript: 0 errors**

---

## 📝 Implementation Guide

### Step 1: Create Citation Types (15 min)

```bash
cat > src/types/citation.ts <<'EOF'
export interface Citation {
  source: 'eTG' | 'PBS' | 'AMH' | 'AHPRA' | 'Other';
  title: string;
  page?: string;
  section?: string;
  url?: string;
  confidence?: number;  // RAG confidence score
}

export interface CitationPanelProps {
  citations: string[];
  showConfidence?: boolean;
  allowCopy?: boolean;
}
EOF
```

### Step 2: Create Citation Panel Component (2 hours)

```bash
cat > src/components/citations/CitationPanel.tsx <<'EOF'
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Snackbar,
  Link,
  Divider
} from '@mui/material';
import {
  ContentCopy,
  VerifiedUser,
  MenuBook,
  LocalHospital
} from '@mui/icons-material';

interface CitationPanelProps {
  citations: string[];
  showConfidence?: boolean;
}

export const CitationPanel: React.FC<CitationPanelProps> = ({
  citations,
  showConfidence = false
}) => {
  const [copySuccess, setCopySuccess] = useState(false);

  const parseCitation = (citation: string) => {
    // Parse citation format: "Source: Title (Page XX, Section YY)"
    const sourceMatch = citation.match(/^(eTG|PBS|AMH|AHPRA):/i);
    const source = sourceMatch ? sourceMatch[1].toUpperCase() : 'Other';

    const pageMatch = citation.match(/page\s+(\d+)/i);
    const page = pageMatch ? pageMatch[1] : null;

    return { source, text: citation, page };
  };

  const handleCopy = (citation: string) => {
    navigator.clipboard.writeText(citation);
    setCopySuccess(true);
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'ETG':
        return <MenuBook />;
      case 'PBS':
        return <LocalHospital />;
      case 'AMH':
        return <MenuBook />;
      case 'AHPRA':
        return <VerifiedUser />;
      default:
        return <MenuBook />;
    }
  };

  return (
    <>
      <Card elevation={1} sx={{ backgroundColor: '#f5f5f5' }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <VerifiedUser color="primary" />
            <Typography variant="h6">
              Australian Clinical Guidelines
            </Typography>
            {showConfidence && (
              <Chip
                label="RAG Verified"
                size="small"
                color="success"
                icon={<VerifiedUser />}
              />
            )}
          </Box>

          <Divider sx={{ mb: 2 }} />

          {citations.map((citation, idx) => {
            const parsed = parseCitation(citation);

            return (
              <Box key={idx} mb={2}>
                <Box display="flex" alignItems="flex-start" gap={1}>
                  <Box sx={{ color: 'primary.main' }}>
                    {getSourceIcon(parsed.source)}
                  </Box>
                  <Box flexGrow={1}>
                    <Typography variant="body2" color="text.secondary">
                      {parsed.text}
                    </Typography>
                    {parsed.page && (
                      <Chip
                        label={`Page ${parsed.page}`}
                        size="small"
                        variant="outlined"
                        sx={{ mt: 0.5 }}
                      />
                    )}
                  </Box>
                  <Tooltip title="Copy citation">
                    <IconButton
                      size="small"
                      onClick={() => handleCopy(citation)}
                      aria-label="Copy citation"
                    >
                      <ContentCopy fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
            );
          })}
        </CardContent>
      </Card>

      <Snackbar
        open={copySuccess}
        autoHideDuration={2000}
        onClose={() => setCopySuccess(false)}
        message="Citation copied to clipboard"
      />
    </>
  );
};
EOF
```

### Step 3: Create Tests (45 min)

```bash
cat > tests/components/CitationPanel.test.tsx <<'EOF'
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CitationPanel } from '../../src/components/citations/CitationPanel';

describe('CitationPanel', () => {
  const mockCitations = [
    'eTG: Therapeutic Guidelines (Page 42, Section 3.2)',
    'PBS: Pharmaceutical Benefits Scheme - Paracetamol',
    'AMH: Australian Medicines Handbook (Page 156)'
  ];

  it('renders all citations', () => {
    render(<CitationPanel citations={mockCitations} />);

    expect(screen.getByText(/eTG: Therapeutic Guidelines/)).toBeInTheDocument();
    expect(screen.getByText(/PBS: Pharmaceutical Benefits/)).toBeInTheDocument();
    expect(screen.getByText(/AMH: Australian Medicines/)).toBeInTheDocument();
  });

  it('displays page numbers when present', () => {
    render(<CitationPanel citations={mockCitations} />);

    expect(screen.getByText('Page 42')).toBeInTheDocument();
    expect(screen.getByText('Page 156')).toBeInTheDocument();
  });

  it('shows RAG verification badge when enabled', () => {
    render(<CitationPanel citations={mockCitations} showConfidence />);

    expect(screen.getByText('RAG Verified')).toBeInTheDocument();
  });

  it('copies citation to clipboard on button click', async () => {
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn()
      }
    });

    render(<CitationPanel citations={mockCitations} />);

    const copyButtons = screen.getAllByLabelText('Copy citation');
    fireEvent.click(copyButtons[0]);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockCitations[0]);
    expect(screen.getByText('Citation copied to clipboard')).toBeInTheDocument();
  });
});
EOF

npm test
```

---

## ✅ Success Criteria

1. ✅ CitationPanel component created
2. ✅ Australian guideline formatting (eTG, PBS, AMH, AHPRA)
3. ✅ Page number display
4. ✅ RAG verification badge
5. ✅ Copy-to-clipboard functional
6. ✅ TypeScript: 0 errors

---

## 🔄 When Complete

```bash
sed -i 's/TASK_007.*TODO/TASK_007: ✅ DONE/' @fix_plan.md

git commit -m "feat(frontend): Complete TASK_007 Citation Display Component

- CitationPanel with Australian guideline formatting
- Page number linking for eTG, PBS, AMH sources
- RAG verification badge (confidence >0.65)
- Copy-to-clipboard functionality
- TypeScript: 0 errors

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ TASK_007 complete. Starting TASK_008..."
```

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
