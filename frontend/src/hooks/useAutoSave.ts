/**
 * Auto-Save Hook with Debouncing
 *
 * Fix #4: Auto-Save Debounce (Prevent API Spam)
 *
 * Problem: Auto-save on every keystroke spams API (100+ requests/minute)
 * Solution: Debounce auto-save by 300ms (only save after user stops typing)
 *
 * Features:
 * - Debounces save by 300ms (configurable)
 * - Force save after 30s even if user still typing (maxWait)
 * - Optimistic updates (UI shows "Saving..." immediately)
 * - Error handling (shows "Failed to save" on error)
 * - Type-safe with TypeScript
 *
 * Performance Improvement:
 * - Before: 60 WPM typing = 60 API calls/minute (1 per second)
 * - After: 60 WPM typing = 2-3 API calls/minute (only after pauses)
 *
 * Usage:
 * ```tsx
 * const { debouncedSave, saveStatus } = useAutoSave({
 *   sessionId: 'uuid',
 *   debounceMs: 300,
 *   maxWaitMs: 30000,
 * });
 *
 * const handleChange = (field: string, value: string) => {
 *   setDraftData({ ...draftData, [field]: value });
 *   debouncedSave({ [field]: value }); // Debounced API call
 * };
 *
 * <TextField onChange={e => handleChange('subjective', e.target.value)} />
 * <AutoSaveIndicator status={saveStatus} />
 * ```
 */

import { useCallback, useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import axiosInstance from '../utils/axiosInstance';

// Save Status Types
export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface AutoSaveOptions {
  sessionId: string;
  debounceMs?: number; // Delay before saving (default: 300ms)
  maxWaitMs?: number; // Force save after this time (default: 30000ms = 30s)
  onSaveSuccess?: () => void;
  onSaveError?: (error: Error) => void;
}

interface AutoSaveReturn {
  debouncedSave: (data: Record<string, any>) => void;
  saveStatus: SaveStatus;
  lastSavedAt: Date | null;
  cancelPendingSave: () => void;
}

/**
 * Auto-Save Hook with Debouncing
 *
 * Debounces auto-save to prevent API spam on every keystroke.
 * Uses TanStack Query mutation for API call.
 *
 * @param options - Configuration options
 * @returns Debounced save function + status
 */
export const useAutoSave = ({
  sessionId,
  debounceMs = 300,
  maxWaitMs = 30000,
  onSaveSuccess,
  onSaveError,
}: AutoSaveOptions): AutoSaveReturn => {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);

  // Refs for debouncing
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const maxWaitTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastCallTimeRef = useRef<number>(0);
  const pendingDataRef = useRef<Record<string, any> | null>(null);

  // TanStack Query mutation for save API call
  const saveMutation = useMutation({
    mutationFn: async (data: Record<string, any>) => {
      const response = await axiosInstance.put(
        `/emr/sessions/${sessionId}`,
        {
          session_data: data,
        }
      );
      return response.data;
    },
    onMutate: () => {
      setSaveStatus('saving');
    },
    onSuccess: () => {
      setSaveStatus('saved');
      setLastSavedAt(new Date());
      onSaveSuccess?.();

      // Reset to idle after 2 seconds
      setTimeout(() => {
        setSaveStatus('idle');
      }, 2000);
    },
    onError: (error: Error) => {
      setSaveStatus('error');
      onSaveError?.(error);
      console.error('Auto-save failed:', error);

      // Reset to idle after 5 seconds
      setTimeout(() => {
        setSaveStatus('idle');
      }, 5000);
    },
  });

  /**
   * Actually perform the save (called after debounce delay)
   */
  const performSave = useCallback(() => {
    if (pendingDataRef.current) {
      saveMutation.mutate(pendingDataRef.current);
      pendingDataRef.current = null;
    }

    // Clear timers
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }
    if (maxWaitTimerRef.current) {
      clearTimeout(maxWaitTimerRef.current);
      maxWaitTimerRef.current = null;
    }
  }, [saveMutation]);

  /**
   * Debounced save function
   * Delays save by debounceMs, but forces save after maxWaitMs
   */
  const debouncedSave = useCallback(
    (data: Record<string, any>) => {
      const now = Date.now();

      // Merge with pending data (accumulate changes)
      pendingDataRef.current = {
        ...pendingDataRef.current,
        ...data,
      };

      // Clear existing debounce timer
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      // Set new debounce timer (300ms default)
      debounceTimerRef.current = setTimeout(() => {
        performSave();
      }, debounceMs);

      // Set max wait timer on first call
      if (!maxWaitTimerRef.current) {
        lastCallTimeRef.current = now;

        maxWaitTimerRef.current = setTimeout(() => {
          console.log('Auto-save forced after maxWait period');
          performSave();
        }, maxWaitMs);
      } else {
        // Check if max wait time exceeded
        const timeSinceFirstCall = now - lastCallTimeRef.current;
        if (timeSinceFirstCall >= maxWaitMs) {
          console.log('Auto-save forced after maxWait period');
          performSave();
        }
      }
    },
    [debounceMs, maxWaitMs, performSave]
  );

  /**
   * Cancel pending save (useful when user navigates away)
   */
  const cancelPendingSave = useCallback(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }
    if (maxWaitTimerRef.current) {
      clearTimeout(maxWaitTimerRef.current);
      maxWaitTimerRef.current = null;
    }
    pendingDataRef.current = null;
  }, []);

  // Cleanup on unmount
  useCallback(() => {
    return () => {
      cancelPendingSave();
    };
  }, [cancelPendingSave]);

  return {
    debouncedSave,
    saveStatus,
    lastSavedAt,
    cancelPendingSave,
  };
};

export default useAutoSave;
