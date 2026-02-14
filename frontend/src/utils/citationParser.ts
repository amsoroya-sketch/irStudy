/**
 * Citation Parser Utility
 * Parses Australian medical guideline citations into structured data
 *
 * SUPPORTED FORMATS:
 * - "eTG: Therapeutic Guidelines - Cardiovascular (Page 42, Section 3.2)"
 * - "PBS: Pharmaceutical Benefits Scheme - Paracetamol (Schedule 4)"
 * - "AMH: Australian Medicines Handbook 2024 (Page 156)"
 * - "AHPRA: Guidelines for safe prescribing (Section 2.1)"
 * - "RACGP: Red Book - Immunisation (Page 23)"
 * - "NSW Health: Clinical Guidelines - Emergency Medicine (Page 5, Section 1.4)"
 */

import type { CitationSource, ParsedCitation } from '../types/citation';

/**
 * Known Australian medical sources
 */
const KNOWN_SOURCES: CitationSource[] = [
  'eTG',
  'PBS',
  'AMH',
  'AHPRA',
  'RACGP',
  'NSW Health',
];

/**
 * Regular expressions for parsing citation components
 */
const PAGE_REGEX = /(?:page|p\.?|pp\.?)\s*(\d+(?:-\d+)?)/gi;
const SECTION_REGEX = /(?:section|sec\.?)\s*([0-9]+(?:\.[0-9]+)*)/gi;
const URL_REGEX = /(https?:\/\/[^\s,)]+)/gi;

/**
 * Extract source from citation text
 * Returns the source identifier and the remaining text
 */
function extractSource(citation: string): { source: CitationSource; remainingText: string } {
  const trimmed = citation.trim();

  // Check for known sources with colon separator
  for (const source of KNOWN_SOURCES) {
    const prefix = `${source}:`;
    if (trimmed.startsWith(prefix)) {
      return {
        source,
        remainingText: trimmed.slice(prefix.length).trim(),
      };
    }
  }

  // Check for source name at start (case-insensitive)
  const lowerCitation = trimmed.toLowerCase();
  for (const source of KNOWN_SOURCES) {
    const lowerSource = source.toLowerCase();
    if (lowerCitation.startsWith(lowerSource)) {
      const endIndex = source.length;
      // Check if followed by space, colon, or dash
      if (
        trimmed.length > endIndex &&
        [' ', ':', '-'].includes(trimmed[endIndex])
      ) {
        return {
          source,
          remainingText: trimmed.slice(endIndex + 1).trim(),
        };
      }
    }
  }

  // Default to 'Other' if no known source found
  return {
    source: 'Other',
    remainingText: trimmed,
  };
}

/**
 * Extract page numbers from text
 * Supports formats: "Page 42", "p. 42", "pp. 42-45"
 */
function extractPage(text: string): string | null {
  PAGE_REGEX.lastIndex = 0; // Reset regex state
  const match = PAGE_REGEX.exec(text);
  return match ? match[1] : null;
}

/**
 * Extract section reference from text
 * Supports formats: "Section 3.2", "Sec. 3.2.1"
 */
function extractSection(text: string): string | null {
  SECTION_REGEX.lastIndex = 0; // Reset regex state
  const match = SECTION_REGEX.exec(text);
  return match ? match[1] : null;
}

/**
 * Extract URL from text
 */
function extractUrl(text: string): string | null {
  URL_REGEX.lastIndex = 0; // Reset regex state
  const match = URL_REGEX.exec(text);
  return match ? match[1] : null;
}

/**
 * Extract title by removing metadata (page, section, URL)
 */
function extractTitle(text: string): string {
  let title = text;

  // Remove page references
  title = title.replace(PAGE_REGEX, '');

  // Remove section references
  title = title.replace(SECTION_REGEX, '');

  // Remove URLs
  title = title.replace(URL_REGEX, '');

  // Remove parentheses and brackets if they're now empty
  title = title.replace(/\(\s*,?\s*\)/g, '');
  title = title.replace(/\[\s*,?\s*\]/g, '');

  // Clean up extra spaces and commas
  title = title.replace(/\s*,\s*,\s*/g, ', ');
  title = title.replace(/\s+/g, ' ');
  title = title.replace(/,\s*$/g, '');
  title = title.replace(/\(\s*,/g, '(');
  title = title.replace(/,\s*\)/g, ')');

  return title.trim();
}

/**
 * Format display text with source, title, and metadata
 */
function formatDisplayText(
  source: CitationSource,
  title: string,
  page: string | null,
  section: string | null
): string {
  let display = source === 'Other' ? title : `${source}: ${title}`;

  const metadata: string[] = [];
  if (page) metadata.push(`Page ${page}`);
  if (section) metadata.push(`Section ${section}`);

  if (metadata.length > 0) {
    display += ` (${metadata.join(', ')})`;
  }

  return display;
}

/**
 * Parse a citation string into structured data
 *
 * @param citation - Raw citation string
 * @returns Parsed citation object
 *
 * @example
 * ```typescript
 * const result = parseCitation('eTG: Cardiovascular (Page 42, Section 3.2)');
 * // {
 * //   source: 'eTG',
 * //   title: 'Cardiovascular',
 * //   page: '42',
 * //   section: '3.2',
 * //   url: null,
 * //   displayText: 'eTG: Cardiovascular (Page 42, Section 3.2)'
 * // }
 * ```
 */
export function parseCitation(citation: string): ParsedCitation {
  if (!citation || typeof citation !== 'string') {
    return {
      source: 'Other',
      title: '',
      page: null,
      section: null,
      url: null,
      displayText: '',
    };
  }

  // Extract source
  const { source, remainingText } = extractSource(citation);

  // Extract metadata
  const page = extractPage(remainingText);
  const section = extractSection(remainingText);
  const url = extractUrl(remainingText);

  // Extract title (text without metadata)
  const title = extractTitle(remainingText);

  // Format display text
  const displayText = formatDisplayText(source, title, page, section);

  return {
    source,
    title,
    page,
    section,
    url,
    displayText,
  };
}

/**
 * Parse multiple citations
 *
 * @param citations - Array of citation strings
 * @returns Array of parsed citations
 */
export function parseCitations(citations: string[]): ParsedCitation[] {
  return citations.map(parseCitation);
}

/**
 * Check if a string contains a known Australian medical source
 */
export function isAustralianSource(citation: string): boolean {
  const lowerCitation = citation.toLowerCase();
  return KNOWN_SOURCES.some((source) =>
    lowerCitation.includes(source.toLowerCase())
  );
}

/**
 * Get source display name
 */
export function getSourceDisplayName(source: CitationSource): string {
  switch (source) {
    case 'eTG':
      return 'Therapeutic Guidelines';
    case 'PBS':
      return 'Pharmaceutical Benefits Scheme';
    case 'AMH':
      return 'Australian Medicines Handbook';
    case 'AHPRA':
      return 'AHPRA Guidelines';
    case 'RACGP':
      return 'RACGP Guidelines';
    case 'NSW Health':
      return 'NSW Health Guidelines';
    case 'Other':
    default:
      return 'Clinical Reference';
  }
}
