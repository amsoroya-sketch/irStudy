/**
 * TanStack Query Configuration
 * Global query client setup with caching and retry logic
 */

import { QueryClient, DefaultOptions } from '@tanstack/react-query';

/**
 * Default options for all queries
 */
const queryConfig: DefaultOptions = {
  queries: {
    // Stale time: How long data is considered fresh (5 minutes)
    staleTime: 5 * 60 * 1000,

    // Cache time: How long inactive data stays in cache (10 minutes)
    gcTime: 10 * 60 * 1000,

    // Retry failed requests
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

    // Refetch on window focus (good for real-time data)
    refetchOnWindowFocus: false,

    // Refetch on reconnect
    refetchOnReconnect: true,

    // Don't refetch on mount if data is fresh
    refetchOnMount: false,
  },
  mutations: {
    // Retry mutations once
    retry: 1,
  },
};

/**
 * Create and export query client
 */
export const queryClient = new QueryClient({
  defaultOptions: queryConfig,
});

/**
 * Query keys for consistent cache management
 */
export const queryKeys = {
  // MCQs
  mcqs: {
    all: ['mcqs'] as const,
    list: (params?: Record<string, unknown>) => ['mcqs', 'list', params] as const,
    detail: (id: string) => ['mcqs', 'detail', id] as const,
    statistics: () => ['mcqs', 'statistics'] as const,
  },

  // OSCEs
  osces: {
    all: ['osces'] as const,
    list: (params?: Record<string, unknown>) => ['osces', 'list', params] as const,
    detail: (id: string) => ['osces', 'detail', id] as const,
    statistics: () => ['osces', 'statistics'] as const,
  },

  // User & Progress
  user: {
    profile: () => ['user', 'profile'] as const,
    progress: {
      dashboard: () => ['user', 'progress', 'dashboard'] as const,
      weakAreas: () => ['user', 'progress', 'weak-areas'] as const,
      stats: () => ['user', 'progress', 'stats'] as const,
      specialty: (specialty: string) => ['user', 'progress', 'specialty', specialty] as const,
      trends: (weeks: number) => ['user', 'progress', 'trends', 'weekly', weeks] as const,
    },
  },

  // Authentication
  auth: {
    currentUser: () => ['auth', 'current-user'] as const,
  },
} as const;

export default queryClient;
