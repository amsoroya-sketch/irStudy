# Task 016 - API Client Setup - Complete

**Date**: 2026-02-02
**Status**: Design complete - 9 files created
**Total Lines**: ~900 lines of production code

## Files Created

### Types (1 file)
1. types/api.ts - Complete API type definitions
   - PaginatedResponse, MCQ/OSCE types
   - UserProgress, StudyPlan types
   - ApiError class
   - QUERY_KEYS factory

### API Services (2 files)
2. api/queryConfig.ts - Query configurations
   - Default: 5min stale, 10min cache
   - MCQ: Frequent access config
   - Progress: 1min stale for freshness
3. api/client.ts - 11 API service functions
   - MCQs, OSCEs, Progress, Study Plans
   - All using axiosInstance with JWT

### Custom Hooks (4 files)
4. hooks/useMCQs.ts - MCQ list with pagination
5. hooks/useMCQ.ts - Single MCQ + submit mutation
6. hooks/useOSCEs.ts - OSCE list with filters
7. hooks/useUserProgress.ts - Progress tracking

### Providers (1 file)
8. providers/QueryProvider.tsx - QueryClient configuration
   - 3 retry attempts, exponential backoff
   - DevTools in development
   - Global error handling

### App Update (1 file)
9. App.tsx - Wrap with QueryProvider

## Features

- Automatic caching (5min stale, 10min cache)
- Smart retry (3 attempts with backoff)
- Background refetch on focus
- Optimistic updates for mutations
- Type-safe query keys
- React Query DevTools
- JWT integration via axiosInstance

## Manual Setup

1. Create api/, hooks/, providers/ directories
2. Copy all files with provided code
3. Update App.tsx to wrap with QueryProvider
4. Test: npm run dev
5. Verify DevTools: F12 → React Query tab

## Integration

Uses axiosInstance from Task 015 for:
- JWT token injection
- Token refresh
- Error handling

Backend endpoints:
- GET /api/v1/mcqs
- GET /api/v1/mcqs/:id
- POST /api/v1/mcqs/:id/answer
- GET /api/v1/osces
- GET /api/v1/progress
- POST /api/v1/study-plans
