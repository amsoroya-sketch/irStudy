/**
 * Patient Personas API Client
 * Integrates with backend AI OSCE patient persona endpoints
 *
 * AUSTRALIAN MEDICAL CONTEXT:
 * - All 207 personas validated for AMC Clinical Examination preparation
 * - RAG-verified citations (7,245 citations, 66% Australian sources)
 * - Specialties align with AMC blueprint areas
 * - Difficulty levels: foundation (easy), intermediate (medium), advanced (hard)
 */

import axiosInstance from './client';

/**
 * Patient Persona Summary (List View)
 * Matches backend response from GET /patient-personas
 */
export interface PersonaListItem {
  persona_id: string;        // UUID
  persona_code: string;      // e.g., "cardiology_001_stemi_male_65"
  name: string;              // e.g., "John Brown"
  age: number;               // 0-95
  gender: string;            // "male" | "female"
  specialty: string;         // One of 5 specialties
  chief_complaint: string;   // e.g., "Patient presenting with symptoms consistent with STEMI"
  difficulty_level: string;  // "foundation" | "intermediate" | "advanced"
  estimated_pass_rate: number | null;
  amc_blueprint_area: string;
}

/**
 * Patient Persona Full Details (Detail View)
 * Includes progressive disclosure structure for AI OSCE simulation
 */
export interface PersonaDetail extends PersonaListItem {
  occupation: string | null;
  cultural_background: string | null;
  preferred_language: string;
  opening_statement: string;
  symptoms: Record<string, any>;           // Progressive disclosure: immediate vs on_questioning
  medical_history: Record<string, any>;    // Past medical, medications, allergies
  emotional_profile: Record<string, any>;  // State machine for AI behavior
  rag_query_hints: string[];               // Keywords for RAG system
  key_differentials: string[];             // Expected diagnoses
  critical_actions: string[];              // Must-do actions for pass
  amc_competencies: string[];              // AMC framework alignment
}

/**
 * Query parameters for listing personas
 */
export interface PersonaListParams {
  specialty?: string;        // Filter by specialty
  difficulty?: string;       // Filter by difficulty_level
  skip?: number;             // Pagination offset
  limit?: number;            // Results per page (default 100, max 100)
}

/**
 * Get paginated list of patient personas with optional filters
 *
 * @param params - Optional filter parameters (specialty, difficulty, pagination)
 * @returns List of persona summaries (without full progressive disclosure details)
 *
 * Example usage:
 * ```typescript
 * // Get all personas
 * const allPersonas = await getPersonas();
 *
 * // Filter by specialty
 * const cardioPersonas = await getPersonas({ specialty: 'Cardiology' });
 *
 * // Filter by difficulty
 * const advancedPersonas = await getPersonas({ difficulty: 'advanced' });
 *
 * // Combined filters
 * const filtered = await getPersonas({
 *   specialty: 'Emergency',
 *   difficulty: 'intermediate',
 *   limit: 50
 * });
 * ```
 */
export const getPersonas = async (params?: PersonaListParams): Promise<PersonaListItem[]> => {
  const response = await axiosInstance.get<PersonaListItem[]>('/patient-personas', {
    params: {
      specialty: params?.specialty,
      difficulty: params?.difficulty,
      skip: params?.skip || 0,
      limit: params?.limit || 100,
    },
  });
  return response.data;
};

/**
 * Get complete patient persona details by ID
 *
 * @param personaId - UUID of the patient persona
 * @returns Full persona details with progressive disclosure structure
 *
 * Example usage:
 * ```typescript
 * const persona = await getPersonaDetail('123e4567-e89b-12d3-a456-426614174000');
 * console.log(persona.opening_statement);  // What AI Patient says first
 * console.log(persona.symptoms);           // Progressive disclosure symptoms
 * console.log(persona.critical_actions);   // Must-do actions for pass
 * ```
 *
 * Throws:
 * - 404: Patient persona not found
 * - 401: Authentication required (handled by axiosInstance interceptor)
 */
export const getPersonaDetail = async (personaId: string): Promise<PersonaDetail> => {
  // Validate UUID format before API call (security)
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(personaId)) {
    throw new Error('Invalid persona ID format');
  }

  const response = await axiosInstance.get<PersonaDetail>(`/patient-personas/${personaId}`);
  return response.data;
};
