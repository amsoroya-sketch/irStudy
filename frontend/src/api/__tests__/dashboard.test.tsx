/**
 * Dashboard API Hook Tests
 * Test-Driven Development (TDD) for useDashboardOverview hook
 *
 * Phase 1 - Tests 1-4 (API Hook)
 * Author: react-frontend-developer
 * Date: 2026-05-25
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useDashboardOverview } from '../dashboard';
import axiosInstance from '../../utils/axiosInstance';
import type { DashboardOverviewResponse } from '../../types/dashboard';

// Mock axios instance
vi.mock('../../utils/axiosInstance');
const mockedAxiosInstance = vi.mocked(axiosInstance);

describe('Dashboard API Hook - useDashboardOverview', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    // Create fresh query client for each test (prevents cache pollution)
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false, // Disable retries for faster tests
          gcTime: 0, // Disable cache time
        },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  /**
   * Test 1: Fetch Dashboard Data Successfully
   *
   * RED Phase Expected: Hook not found error (useDashboardOverview doesn't exist)
   * GREEN Phase Expected: Test passes when hook implemented
   */
  it('Test 1: should fetch dashboard data successfully', async () => {
    // Arrange: Mock successful API response
    const mockDashboardData: DashboardOverviewResponse = {
      overall_progress: {
        total_sessions: 127,
        completion_percentage: 68.5,
        avg_score: 76.2,
        total_time_minutes: 2340,
        last_activity: '2026-05-25T14:30:00Z',
      },
      modules: {
        mcq: {
          total_attempts: 45,
          average_score: 78.5,
          last_activity: '2026-05-25T14:30:00Z',
          completion_rate: 71.1,
        },
        osce: {
          total_attempts: 32,
          average_score: 74.8,
          last_activity: '2026-05-24T16:20:00Z',
          completion_rate: 65.6,
        },
        emr: {
          total_sessions: 28,
          average_score: 72.3,
          last_activity: '2026-05-25T10:15:00Z',
          completion_rate: 60.7,
        },
        mock_exam: {
          total_exams: 22,
          average_score: 80.1,
          last_activity: '2026-05-23T09:45:00Z',
          completion_rate: 81.8,
        },
      },
      specialty_breakdown: [
        { specialty: 'cardiology', attempts: 15, avg_score: 82.3 },
        { specialty: 'respiratory', attempts: 12, avg_score: 75.1 },
      ],
      recent_activity: [
        {
          type: 'mcq',
          description: 'Completed MCQ on Chest Pain',
          score: 85,
          timestamp: '2026-05-25T14:30:00Z',
        },
      ],
      recommendations: [
        {
          module: 'mcq',
          specialty: 'psychiatry',
          reason: 'Focus on psychiatry - 15% below average',
          priority: 'high',
        },
      ],
    };

    mockedAxiosInstance.get.mockResolvedValueOnce({ data: mockDashboardData });

    // Act: Render hook
    const { result } = renderHook(() => useDashboardOverview(), { wrapper });

    // Assert: Wait for success state
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockDashboardData);
    expect(mockedAxiosInstance.get).toHaveBeenCalledWith('/dashboard/overview');
    expect(mockedAxiosInstance.get).toHaveBeenCalledTimes(1);
  });

  /**
   * Test 2: Handle API Error Gracefully
   *
   * RED Phase Expected: Hook not found error
   * GREEN Phase Expected: Test passes (error state handled correctly)
   */
  it('Test 2: should handle API error gracefully', async () => {
    // Arrange: Mock API error
    const errorMessage = 'Network error';
    mockedAxiosInstance.get.mockRejectedValueOnce(new Error(errorMessage));

    // Act: Render hook
    const { result } = renderHook(() => useDashboardOverview(), { wrapper });

    // Assert: Wait for error state
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.data).toBeUndefined();
    expect(mockedAxiosInstance.get).toHaveBeenCalledWith('/dashboard/overview');
  });

  /**
   * Test 3: Show Loading State While Fetching
   *
   * RED Phase Expected: Hook not found error
   * GREEN Phase Expected: Test passes (loading state shown initially)
   */
  it('Test 3: should show loading state while fetching', () => {
    // Arrange: Mock pending promise (never resolves)
    mockedAxiosInstance.get.mockImplementationOnce(() => new Promise(() => {}));

    // Act: Render hook
    const { result } = renderHook(() => useDashboardOverview(), { wrapper });

    // Assert: Initial loading state
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();
    expect(result.current.isError).toBe(false);
  });

  /**
   * Test 4: Refetch Data When Invalidated
   *
   * RED Phase Expected: Hook not found error
   * GREEN Phase Expected: Test passes (refetch updates data)
   */
  it('Test 4: should refetch data when invalidated', async () => {
    // Arrange: Mock two different responses
    const mockData1: DashboardOverviewResponse = {
      overall_progress: {
        total_sessions: 100,
        completion_percentage: 50,
        avg_score: 70,
        total_time_minutes: 1000,
        last_activity: '2026-05-24T10:00:00Z',
      },
      modules: {
        mcq: { total_attempts: 10, average_score: 70, last_activity: null, completion_rate: 50 },
        osce: { total_attempts: 10, average_score: 70, last_activity: null, completion_rate: 50 },
        emr: { total_sessions: 10, average_score: 70, last_activity: null, completion_rate: 50 },
        mock_exam: { total_exams: 10, average_score: 70, last_activity: null, completion_rate: 50 },
      },
      specialty_breakdown: [],
      recent_activity: [],
      recommendations: [],
    };

    const mockData2: DashboardOverviewResponse = {
      ...mockData1,
      overall_progress: {
        ...mockData1.overall_progress,
        total_sessions: 105, // Updated value
      },
    };

    mockedAxiosInstance.get
      .mockResolvedValueOnce({ data: mockData1 })
      .mockResolvedValueOnce({ data: mockData2 });

    // Act: Render hook
    const { result } = renderHook(() => useDashboardOverview(), { wrapper });

    // Assert: Wait for initial data
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.overall_progress.total_sessions).toBe(100);

    // Act: Refetch data
    await result.current.refetch();

    // Assert: Data updated after refetch
    await waitFor(() =>
      expect(result.current.data?.overall_progress.total_sessions).toBe(105)
    );
    expect(mockedAxiosInstance.get).toHaveBeenCalledTimes(2);
  });
});
