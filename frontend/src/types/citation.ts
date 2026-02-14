/**
 * Citation Type Definitions
 * For Australian medical guideline citations with RAG verification
 *
 * AUSTRALIAN MEDICAL SOURCES:
 * - eTG: Therapeutic Guidelines (therapeutic.tg.org.au)
 * - PBS: Pharmaceutical Benefits Scheme (pbs.gov.au)
 * - AMH: Australian Medicines Handbook (amh.net.au)
 * - AHPRA: Australian Health Practitioner Regulation Agency (ahpra.gov.au)
 * - RACGP: Royal Australian College of General Practitioners (racgp.org.au)
 * - NSW Health: NSW Health clinical guidelines (health.nsw.gov.au)
 */

/**
 * Australian medical guideline sources
 */
export type CitationSource =
  | 'eTG'
  | 'PBS'
  | 'AMH'
  | 'AHPRA'
  | 'RACGP'
  | 'NSW Health'
  | 'Other';

/**
 * Parsed citation data
 */
export interface Citation {
  /** Source identifier (eTG, PBS, AMH, etc.) */
  source: CitationSource;
  /** Citation title/description */
  title: string;
  /** Page number (if available) */
  page: string | null;
  /** Section reference (if available) */
  section: string | null;
  /** URL to source (if available) */
  url: string | null;
  /** RAG confidence score (0-1, if available) */
  confidence?: number;
  /** Original citation text */
  originalText: string;
}

/**
 * Parsed citation result from parser utility
 */
export interface ParsedCitation {
  /** Source identifier */
  source: CitationSource;
  /** Title text */
  title: string;
  /** Page number */
  page: string | null;
  /** Section reference */
  section: string | null;
  /** URL */
  url: string | null;
  /** Formatted display text */
  displayText: string;
}

/**
 * Props for CitationPanel component
 */
export interface CitationPanelProps {
  /** Array of citation strings or Citation objects */
  citations: (string | Citation)[];
  /** Show RAG verification badge */
  showConfidence?: boolean;
  /** Allow copy-to-clipboard functionality */
  allowCopy?: boolean;
  /** Custom aria-label for accessibility */
  'aria-label'?: string;
}

/**
 * Citation display settings
 */
export interface CitationDisplaySettings {
  /** Show page numbers */
  showPages: boolean;
  /** Show sections */
  showSections: boolean;
  /** Show source icons */
  showIcons: boolean;
  /** Enable copy button */
  enableCopy: boolean;
  /** Show confidence badge */
  showConfidence: boolean;
}

/**
 * Citation copy format options
 */
export type CitationFormat = 'plain' | 'markdown' | 'apa' | 'vancouver';

/**
 * Citation metadata for advanced features
 */
export interface CitationMetadata {
  /** Publication year */
  year?: number;
  /** Edition/version */
  edition?: string;
  /** Authors */
  authors?: string[];
  /** DOI */
  doi?: string;
  /** Last accessed date */
  accessedDate?: string;
}
