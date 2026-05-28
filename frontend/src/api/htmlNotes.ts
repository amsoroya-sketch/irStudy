/**
 * HTML OSCE Notes API Client
 * Fetch HTML notes metadata and content
 */

import { axiosInstance } from './client';
import type { HTMLNote, HTMLNoteListParams, HTMLNoteSpecialty } from '../types/api';

/**
 * Fetch list of HTML notes with optional filters
 */
export const getHTMLNotes = async (params?: HTMLNoteListParams): Promise<HTMLNote[]> => {
  const { data } = await axiosInstance.get<HTMLNote[]>('/html-notes/', { params });
  return data;
};

/**
 * Fetch single HTML note metadata by ID
 */
export const getHTMLNote = async (noteId: string): Promise<HTMLNote> => {
  const { data } = await axiosInstance.get<HTMLNote>(`/html-notes/${noteId}`);
  return data;
};

/**
 * Fetch raw HTML content for a note
 */
export const getHTMLNoteContent = async (noteId: string): Promise<string> => {
  const { data } = await axiosInstance.get<string>(`/html-notes/${noteId}/content`, {
    responseType: 'text',
  });
  return data;
};

/**
 * Fetch notes filtered by specialty
 */
export const getHTMLNotesBySpecialty = async (specialty: string): Promise<HTMLNote[]> => {
  const { data } = await axiosInstance.get<HTMLNote[]>(`/html-notes/by-specialty/${encodeURIComponent(specialty)}`);
  return data;
};

/**
 * Fetch list of specialties with note counts
 */
export const getHTMLNoteSpecialties = async (): Promise<HTMLNoteSpecialty[]> => {
  const { data } = await axiosInstance.get<HTMLNoteSpecialty[]>('/html-notes/specialties/list');
  return data;
};
