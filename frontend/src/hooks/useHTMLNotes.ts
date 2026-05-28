/**
 * useHTMLNotes Hook
 * React Query hooks for fetching and managing HTML OSCE Notes
 */

import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../api/queryConfig';
import {
  getHTMLNotes,
  getHTMLNote,
  getHTMLNoteContent,
  getHTMLNotesBySpecialty,
  getHTMLNoteSpecialties,
} from '../api/htmlNotes';
import type { HTMLNoteListParams } from '../types/api';

/**
 * Fetch list of HTML notes with optional filters
 */
export const useHTMLNotes = (params?: HTMLNoteListParams) => {
  return useQuery({
    queryKey: queryKeys.htmlNotes.list(params as Record<string, unknown>),
    queryFn: async () => {
      const data = await getHTMLNotes(params);
      return data;
    },
  });
};

/**
 * Fetch single HTML note metadata
 */
export const useHTMLNote = (noteId: string) => {
  return useQuery({
    queryKey: queryKeys.htmlNotes.detail(noteId),
    queryFn: async () => {
      const data = await getHTMLNote(noteId);
      return data;
    },
    enabled: !!noteId,
  });
};

/**
 * Fetch HTML note raw content
 */
export const useHTMLNoteContent = (noteId: string) => {
  return useQuery({
    queryKey: [...queryKeys.htmlNotes.detail(noteId), 'content'],
    queryFn: async () => {
      const data = await getHTMLNoteContent(noteId);
      return data;
    },
    enabled: !!noteId,
  });
};

/**
 * Fetch notes by specialty
 */
export const useHTMLNotesBySpecialty = (specialty: string) => {
  return useQuery({
    queryKey: [...queryKeys.htmlNotes.all, 'by-specialty', specialty],
    queryFn: async () => {
      const data = await getHTMLNotesBySpecialty(specialty);
      return data;
    },
    enabled: !!specialty,
  });
};

/**
 * Fetch specialties list with counts
 */
export const useHTMLNoteSpecialties = () => {
  return useQuery({
    queryKey: queryKeys.htmlNotes.specialties(),
    queryFn: async () => {
      const data = await getHTMLNoteSpecialties();
      return data;
    },
  });
};
