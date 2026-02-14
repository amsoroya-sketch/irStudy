# TASK 1.5: Custom React Hooks

**Task ID**: TASK_1.5
**Phase**: Phase 1 - Frontend Foundation
**Estimated Time**: 4 hours
**Prerequisites**: TASK_1.1 (Project Setup), TASK_1.4 (State Management)
**Dependencies**: React 18, TypeScript, Zustand stores

---

## Overview

Create custom React hooks for common functionality across the EMR practice system. These hooks will encapsulate reusable logic for auto-save, typing metrics, PBS search, and validation.

**Reference**: See `/home/dev/Development/irStudy/emr-practice-system/design-specs/MASTER_EMR_PRD.md` section on Custom Hooks.

---

## Hooks to Create

### 1. useAutoSave Hook (1 hour)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/hooks/useAutoSave.ts`

```typescript
import { useEffect, useRef, useCallback } from 'react';
import { useFormStore } from '@stores/formStore';

interface UseAutoSaveOptions {
  /**
   * Auto-save interval in seconds (default: 30)
   */
  interval?: number;

  /**
   * Callback function to save data
   */
  onSave: () => Promise<void>;

  /**
   * Whether auto-save is enabled (default: true)
   */
  enabled?: boolean;

  /**
   * Callback when save succeeds
   */
  onSuccess?: () => void;

  /**
   * Callback when save fails
   */
  onError?: (error: Error) => void;
}

interface UseAutoSaveReturn {
  /**
   * Trigger manual save
   */
  save: () => Promise<void>;

  /**
   * Whether save is in progress
   */
  isSaving: boolean;

  /**
   * Last save timestamp
   */
  lastSaved: Date | null;

  /**
   * Whether there are unsaved changes
   */
  isDirty: boolean;
}

export function useAutoSave(options: UseAutoSaveOptions): UseAutoSaveReturn {
  const {
    interval = 30,
    onSave,
    enabled = true,
    onSuccess,
    onError,
  } = options;

  const { isDirty, markClean } = useFormStore();
  const [isSaving, setIsSaving] = React.useState(false);
  const [lastSaved, setLastSaved] = React.useState<Date | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  // Manual save function
  const save = useCallback(async () => {
    if (isSaving || !isDirty) return;

    setIsSaving(true);

    try {
      await onSave();

      if (isMountedRef.current) {
        markClean();
        setLastSaved(new Date());
        setIsSaving(false);
        onSuccess?.();
      }
    } catch (error) {
      if (isMountedRef.current) {
        setIsSaving(false);
        onError?.(error as Error);
      }
    }
  }, [isSaving, isDirty, onSave, markClean, onSuccess, onError]);

  // Auto-save effect
  useEffect(() => {
    if (!enabled) return;

    // Clear existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    // Set up new interval
    intervalRef.current = setInterval(() => {
      if (isDirty && !isSaving) {
        save();
      }
    }, interval * 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, interval, isDirty, isSaving, save]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  return {
    save,
    isSaving,
    lastSaved,
    isDirty,
  };
}
```

**Usage Example**:

```typescript
function SOAPEditor() {
  const { soapNote } = useFormStore();

  const { save, isSaving, lastSaved, isDirty } = useAutoSave({
    interval: 30, // 30 seconds
    onSave: async () => {
      await api.saveSOAPNote(soapNote);
    },
    onSuccess: () => {
      console.log('Auto-save successful');
    },
    onError: (error) => {
      console.error('Auto-save failed:', error);
    },
  });

  return (
    <div>
      <button onClick={save} disabled={isSaving}>
        {isSaving ? 'Saving...' : 'Save'}
      </button>
      {lastSaved && <p>Last saved: {lastSaved.toLocaleTimeString()}</p>}
      {isDirty && <p>Unsaved changes</p>}
    </div>
  );
}
```

---

### 2. useTypingMetrics Hook (1 hour)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/hooks/useTypingMetrics.ts`

```typescript
import { useEffect, useRef, useCallback } from 'react';
import { useSessionStore } from '@stores/sessionStore';

interface TypingMetrics {
  totalKeystrokes: number;
  backspaceCount: number;
  wordsPerMinute: number;
  accuracyRate: number;
  averageWordLength: number;
}

interface UseTypingMetricsOptions {
  /**
   * Target element to track (default: document)
   */
  targetRef?: React.RefObject<HTMLElement>;

  /**
   * Whether tracking is enabled (default: true)
   */
  enabled?: boolean;

  /**
   * Callback when metrics update
   */
  onMetricsUpdate?: (metrics: TypingMetrics) => void;
}

export function useTypingMetrics(options: UseTypingMetricsOptions = {}) {
  const { targetRef, enabled = true, onMetricsUpdate } = options;

  const { updateTypingMetrics, typingMetrics } = useSessionStore();

  const startTimeRef = useRef<Date>(new Date());
  const wordCountRef = useRef(0);
  const characterCountRef = useRef(0);

  const calculateWPM = useCallback(() => {
    const elapsedMinutes =
      (new Date().getTime() - startTimeRef.current.getTime()) / 60000;

    if (elapsedMinutes === 0) return 0;

    return Math.round(wordCountRef.current / elapsedMinutes);
  }, []);

  const calculateAccuracy = useCallback(() => {
    const totalKeystrokes = typingMetrics.totalKeystrokes;
    const backspaces = typingMetrics.backspaceCount;

    if (totalKeystrokes === 0) return 100;

    const accuracy = ((totalKeystrokes - backspaces) / totalKeystrokes) * 100;
    return Math.max(0, Math.min(100, accuracy));
  }, [typingMetrics]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      // Ignore modifier keys
      if (event.ctrlKey || event.metaKey || event.altKey) {
        return;
      }

      const newMetrics = { ...typingMetrics };

      // Track backspace
      if (event.key === 'Backspace') {
        newMetrics.backspaceCount += 1;
      }
      // Track regular keystrokes
      else if (event.key.length === 1) {
        newMetrics.totalKeystrokes += 1;
        characterCountRef.current += 1;

        // Count words (space indicates word completion)
        if (event.key === ' ') {
          wordCountRef.current += 1;
        }
      }

      // Calculate derived metrics
      newMetrics.wordsPerMinute = calculateWPM();
      newMetrics.accuracyRate = calculateAccuracy();
      newMetrics.averageWordLength =
        wordCountRef.current > 0
          ? characterCountRef.current / wordCountRef.current
          : 0;

      updateTypingMetrics(newMetrics);
      onMetricsUpdate?.(newMetrics);
    },
    [enabled, typingMetrics, calculateWPM, calculateAccuracy, updateTypingMetrics, onMetricsUpdate]
  );

  // Attach event listener
  useEffect(() => {
    if (!enabled) return;

    const target = targetRef?.current || document;

    target.addEventListener('keydown', handleKeyDown as any);

    return () => {
      target.removeEventListener('keydown', handleKeyDown as any);
    };
  }, [enabled, targetRef, handleKeyDown]);

  // Reset metrics
  const resetMetrics = useCallback(() => {
    startTimeRef.current = new Date();
    wordCountRef.current = 0;
    characterCountRef.current = 0;

    updateTypingMetrics({
      totalKeystrokes: 0,
      backspaceCount: 0,
      wordsPerMinute: 0,
      accuracyRate: 100,
    });
  }, [updateTypingMetrics]);

  return {
    metrics: typingMetrics,
    resetMetrics,
  };
}
```

**Usage Example**:

```typescript
function DocumentationEditor() {
  const editorRef = useRef<HTMLDivElement>(null);

  const { metrics, resetMetrics } = useTypingMetrics({
    targetRef: editorRef,
    enabled: true,
    onMetricsUpdate: (metrics) => {
      console.log('WPM:', metrics.wordsPerMinute);
      console.log('Accuracy:', metrics.accuracyRate);
    },
  });

  return (
    <div>
      <div ref={editorRef}>
        <textarea />
      </div>
      <div className="metrics">
        <p>WPM: {metrics.wordsPerMinute}</p>
        <p>Accuracy: {metrics.accuracyRate.toFixed(1)}%</p>
        <p>Keystrokes: {metrics.totalKeystrokes}</p>
      </div>
    </div>
  );
}
```

---

### 3. usePBSSearch Hook (1 hour)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/hooks/usePBSSearch.ts`

```typescript
import { useState, useCallback, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

interface PBSMedication {
  code: string;
  name: string;
  strength: string;
  form: string;
  indications: string[];
  restrictions: string[];
  maxQuantity: number;
  repeats: number;
  authorityRequired: boolean;
}

interface UsePBSSearchOptions {
  /**
   * Debounce delay in ms (default: 300)
   */
  debounceDelay?: number;

  /**
   * Minimum search term length (default: 3)
   */
  minSearchLength?: number;

  /**
   * Auto-search on input (default: true)
   */
  autoSearch?: boolean;
}

interface UsePBSSearchReturn {
  /**
   * Search query
   */
  searchTerm: string;

  /**
   * Set search query
   */
  setSearchTerm: (term: string) => void;

  /**
   * Search results
   */
  results: PBSMedication[];

  /**
   * Whether search is loading
   */
  isLoading: boolean;

  /**
   * Search error
   */
  error: Error | null;

  /**
   * Manually trigger search
   */
  search: () => void;

  /**
   * Clear results
   */
  clearResults: () => void;
}

export function usePBSSearch(
  options: UsePBSSearchOptions = {}
): UsePBSSearchReturn {
  const {
    debounceDelay = 300,
    minSearchLength = 3,
    autoSearch = true,
  } = options;

  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedTerm, setDebouncedTerm] = useState('');
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  // Debounce search term
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      setDebouncedTerm(searchTerm);
    }, debounceDelay);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [searchTerm, debounceDelay]);

  // Query PBS API
  const {
    data: results = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['pbs-search', debouncedTerm],
    queryFn: async () => {
      if (debouncedTerm.length < minSearchLength) {
        return [];
      }

      const response = await fetch(
        `/api/pbs/search?q=${encodeURIComponent(debouncedTerm)}`
      );

      if (!response.ok) {
        throw new Error('PBS search failed');
      }

      return response.json();
    },
    enabled: autoSearch && debouncedTerm.length >= minSearchLength,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const search = useCallback(() => {
    refetch();
  }, [refetch]);

  const clearResults = useCallback(() => {
    setSearchTerm('');
    setDebouncedTerm('');
  }, []);

  return {
    searchTerm,
    setSearchTerm,
    results,
    isLoading,
    error: error as Error | null,
    search,
    clearResults,
  };
}
```

**Usage Example**:

```typescript
function PrescriptionForm() {
  const { searchTerm, setSearchTerm, results, isLoading } = usePBSSearch({
    debounceDelay: 300,
    minSearchLength: 3,
  });

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search PBS medications..."
      />

      {isLoading && <p>Searching...</p>}

      <ul>
        {results.map((med) => (
          <li key={med.code}>
            {med.name} - {med.strength}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

### 4. useValidation Hook (1 hour)

**File**: `/home/dev/Development/irStudy/emr-frontend/src/hooks/useValidation.ts`

```typescript
import { useState, useCallback } from 'react';
import { useValidationStore } from '@stores/validationStore';
import { useMutation } from '@tanstack/react-query';

interface ValidationOptions {
  /**
   * Validation type
   */
  type: 'soap' | 'prescription' | 'pathology';

  /**
   * Index for prescription/pathology validation
   */
  index?: number;

  /**
   * Auto-validate on change (default: false)
   */
  autoValidate?: boolean;

  /**
   * Validation layers to use
   */
  layers?: ('client' | 'python' | 'ai')[];

  /**
   * Callback when validation completes
   */
  onValidationComplete?: (result: any) => void;
}

interface UseValidationReturn {
  /**
   * Trigger validation
   */
  validate: (data: any) => Promise<void>;

  /**
   * Whether validation is running
   */
  isValidating: boolean;

  /**
   * Validation errors
   */
  errors: any[];

  /**
   * Validation warnings
   */
  warnings: any[];

  /**
   * Clear validation results
   */
  clearValidation: () => void;

  /**
   * Get validation score
   */
  score: number | null;
}

export function useValidation(
  options: ValidationOptions
): UseValidationReturn {
  const {
    type,
    index,
    autoValidate = false,
    layers = ['client', 'python'],
    onValidationComplete,
  } = options;

  const {
    soapValidation,
    prescriptionValidation,
    pathologyValidation,
    setSOAPValidation,
    setPrescriptionValidation,
    setPathologyValidation,
    clearSOAPValidation,
    clearPrescriptionValidation,
    clearPathologyValidation,
    setValidating,
  } = useValidationStore();

  // Get current validation result based on type
  const getValidationResult = () => {
    switch (type) {
      case 'soap':
        return soapValidation;
      case 'prescription':
        return index !== undefined ? prescriptionValidation[index] : null;
      case 'pathology':
        return index !== undefined ? pathologyValidation[index] : null;
      default:
        return null;
    }
  };

  const validationResult = getValidationResult();

  // Validation mutation
  const { mutateAsync: runValidation, isPending: isValidating } = useMutation({
    mutationFn: async (data: any) => {
      setValidating(true);

      const response = await fetch('/api/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type,
          data,
          layers,
        }),
      });

      if (!response.ok) {
        throw new Error('Validation failed');
      }

      return response.json();
    },
    onSuccess: (result) => {
      // Store validation result
      switch (type) {
        case 'soap':
          setSOAPValidation(result);
          break;
        case 'prescription':
          if (index !== undefined) {
            setPrescriptionValidation(index, result);
          }
          break;
        case 'pathology':
          if (index !== undefined) {
            setPathologyValidation(index, result);
          }
          break;
      }

      onValidationComplete?.(result);
    },
    onSettled: () => {
      setValidating(false);
    },
  });

  const validate = useCallback(
    async (data: any) => {
      await runValidation(data);
    },
    [runValidation]
  );

  const clearValidation = useCallback(() => {
    switch (type) {
      case 'soap':
        clearSOAPValidation();
        break;
      case 'prescription':
        if (index !== undefined) {
          clearPrescriptionValidation(index);
        }
        break;
      case 'pathology':
        if (index !== undefined) {
          clearPathologyValidation(index);
        }
        break;
    }
  }, [type, index, clearSOAPValidation, clearPrescriptionValidation, clearPathologyValidation]);

  return {
    validate,
    isValidating,
    errors: validationResult?.errors || [],
    warnings: validationResult?.warnings || [],
    clearValidation,
    score: validationResult?.score || null,
  };
}
```

**Usage Example**:

```typescript
function SOAPValidator() {
  const { soapNote } = useFormStore();

  const { validate, isValidating, errors, warnings, score } = useValidation({
    type: 'soap',
    layers: ['client', 'python', 'ai'],
    onValidationComplete: (result) => {
      console.log('Validation complete:', result);
    },
  });

  const handleValidate = async () => {
    await validate(soapNote);
  };

  return (
    <div>
      <button onClick={handleValidate} disabled={isValidating}>
        {isValidating ? 'Validating...' : 'Validate'}
      </button>

      {score !== null && <p>Score: {score}%</p>}

      {errors.length > 0 && (
        <div className="errors">
          {errors.map((error, idx) => (
            <p key={idx} className="text-red-600">
              {error.message}
            </p>
          ))}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="warnings">
          {warnings.map((warning, idx) => (
            <p key={idx} className="text-yellow-600">
              {warning.message}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Validation Checklist

Before marking this task complete, verify:

- [ ] All 4 hooks created and exported correctly
- [ ] TypeScript types properly defined
- [ ] Hooks follow React hooks rules (start with "use")
- [ ] useAutoSave:
  - [ ] Auto-saves at specified interval
  - [ ] Manual save works
  - [ ] Tracks isDirty state
  - [ ] Cleanup on unmount
- [ ] useTypingMetrics:
  - [ ] Tracks keystrokes correctly
  - [ ] Calculates WPM accurately
  - [ ] Calculates accuracy rate
  - [ ] Can target specific elements
  - [ ] Reset function works
- [ ] usePBSSearch:
  - [ ] Debounces search input
  - [ ] Queries API correctly
  - [ ] Returns results
  - [ ] Handles loading state
  - [ ] Clear results works
- [ ] useValidation:
  - [ ] Validates SOAP notes
  - [ ] Validates prescriptions
  - [ ] Validates pathology orders
  - [ ] Returns errors/warnings
  - [ ] Returns score
  - [ ] Clear validation works
- [ ] No TypeScript errors
- [ ] Import paths use aliases (@hooks/*, @stores/*)
- [ ] All dependencies listed correctly

---

## Time Breakdown

- useAutoSave: 1 hour
- useTypingMetrics: 1 hour
- usePBSSearch: 1 hour
- useValidation: 1 hour
- **Total**: 4 hours

---

## Phase 1 Complete!

After completing this task, Phase 1 (Frontend Foundation) is complete. Next steps:

1. **Phase 2**: Validation Layer (TASK_2.1 - TASK_2.3)
2. **Phase 3**: Backend (TASK_3.1 - TASK_3.4)
3. **Phase 4**: Integration (TASK_4.1 - TASK_4.2)

---

**Last Updated**: 2026-02-03
**Status**: Ready for Implementation
