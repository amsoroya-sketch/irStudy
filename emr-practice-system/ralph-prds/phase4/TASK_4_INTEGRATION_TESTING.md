# TASK 4: Integration & End-to-End Testing

**Task ID**: TASK_4
**Phase**: Phase 4 - Integration
**Estimated Time**: 10 hours total
**Prerequisites**: Phase 1, 2, 3 complete
**Dependencies**: All previous tasks

---

## Overview

Integrate frontend with backend, implement E2E workflows, and validate the complete EMR practice system. This phase ensures all components work together seamlessly for ICRP preparation.

**Reference**: See `/home/dev/Development/irStudy/emr-practice-system/design-specs/MASTER_EMR_PRD.md` for integration requirements.

---

## Sub-Tasks

### 4.1: Frontend-Backend Integration (4 hours)

#### API Client Configuration

**File**: `/home/dev/Development/irStudy/emr-frontend/src/api/client/axios.ts`

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add JWT token)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (handle errors)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

#### Authentication Hook

**File**: `/home/dev/Development/irStudy/emr-frontend/src/hooks/useAuth.ts`

```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@api/client/axios';

interface LoginCredentials {
  username: string; // email
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

interface User {
  id: string;
  email: string;
  full_name: string;
}

export function useAuth() {
  const queryClient = useQueryClient();

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const formData = new FormData();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      return response.data;
    },
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: async (data: RegisterData) => {
      const response = await apiClient.post('/auth/register', data);
      return response.data;
    },
  });

  // Get current user
  const { data: user, isLoading } = useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      const response = await apiClient.get('/auth/me');
      return response.data as User;
    },
    enabled: !!localStorage.getItem('access_token'),
  });

  // Logout
  const logout = () => {
    localStorage.removeItem('access_token');
    queryClient.setQueryData(['user'], null);
    window.location.href = '/login';
  };

  return {
    user,
    isLoading,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout,
    isAuthenticated: !!user,
  };
}
```

#### Session API Integration

**File**: `/home/dev/Development/irStudy/emr-frontend/src/api/hooks/useSessions.ts`

```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@api/client/axios';

interface CreateSessionData {
  patient_id: string;
  emr_type: 'cerner' | 'epic';
  linked_osce_id?: string;
}

export function useSessions() {
  const queryClient = useQueryClient();

  // Create session
  const createSession = useMutation({
    mutationFn: async (data: CreateSessionData) => {
      const response = await apiClient.post('/sessions', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });

  // Get session
  const useSession = (sessionId: string) => {
    return useQuery({
      queryKey: ['sessions', sessionId],
      queryFn: async () => {
        const response = await apiClient.get(`/sessions/${sessionId}`);
        return response.data;
      },
      enabled: !!sessionId,
    });
  };

  // Complete session
  const completeSession = useMutation({
    mutationFn: async ({
      sessionId,
      score,
    }: {
      sessionId: string;
      score: number;
    }) => {
      const response = await apiClient.put(
        `/sessions/${sessionId}/complete`,
        { score }
      );
      return response.data;
    },
  });

  return {
    createSession: createSession.mutate,
    useSession,
    completeSession: completeSession.mutate,
  };
}
```

#### SOAP Note API Integration

**File**: `/home/dev/Development/irStudy/emr-frontend/src/api/hooks/useSOAPNotes.ts`

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@api/client/axios';

export function useSOAPNotes() {
  const queryClient = useQueryClient();

  // Save SOAP note
  const saveSoapNote = useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/soap-notes', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['soap-notes'] });
    },
  });

  // Update SOAP note
  const updateSoapNote = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      const response = await apiClient.put(`/soap-notes/${id}`, data);
      return response.data;
    },
  });

  return {
    saveSoapNote: saveSoapNote.mutate,
    updateSoapNote: updateSoapNote.mutate,
    isSaving: saveSoapNote.isPending,
  };
}
```

#### Validation API Integration

**File**: `/home/dev/Development/irStudy/emr-frontend/src/api/hooks/useValidationAPI.ts`

```typescript
import { useMutation } from '@tanstack/react-query';
import apiClient from '@api/client/axios';

interface ValidationRequest {
  type: 'soap' | 'prescription' | 'pathology';
  data: any;
  layers: ('client' | 'python' | 'ai')[];
}

export function useValidationAPI() {
  // Python validation
  const pythonValidation = useMutation({
    mutationFn: async (request: ValidationRequest) => {
      const response = await apiClient.post('/validation/validate', {
        type: request.type,
        data: request.data,
        layers: ['python'],
      });
      return response.data;
    },
  });

  // AI validation
  const aiValidation = useMutation({
    mutationFn: async (request: ValidationRequest) => {
      const response = await apiClient.post('/ai-validation/validate', {
        type: request.type,
        data: request.data,
        context: request.data.context,
      });
      return response.data;
    },
  });

  return {
    validatePython: pythonValidation.mutate,
    validateAI: aiValidation.mutate,
    isPythonValidating: pythonValidation.isPending,
    isAIValidating: aiValidation.isPending,
  };
}
```

---

### 4.2: Complete User Flows (3 hours)

#### Login Flow

**File**: `/home/dev/Development/irStudy/emr-frontend/src/pages/auth/LoginPage.tsx`

```typescript
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const loginSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    login(
      { username: data.email, password: data.password },
      {
        onSuccess: () => {
          navigate('/dashboard');
        },
      }
    );
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <h1 className="text-2xl font-bold mb-6">EMR Practice Login</h1>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              {...register('email')}
              className="w-full px-4 py-2 border rounded-lg"
            />
            {errors.email && (
              <p className="text-red-600 text-sm mt-1">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              {...register('password')}
              className="w-full px-4 py-2 border rounded-lg"
            />
            {errors.password && (
              <p className="text-red-600 text-sm mt-1">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
};
```

#### Dashboard Flow

**File**: `/home/dev/Development/irStudy/emr-frontend/src/pages/dashboard/Dashboard.tsx`

```typescript
import React from 'react';
import { useAuth } from '@hooks/useAuth';
import { useSessions } from '@api/hooks/useSessions';
import { useNavigate } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const { createSession } = useSessions();
  const navigate = useNavigate();

  const handleStartCernerSession = () => {
    createSession(
      {
        patient_id: 'mock-patient-id', // In real app, select from list
        emr_type: 'cerner',
      },
      {
        onSuccess: (session) => {
          navigate(`/cerner/session/${session.id}`);
        },
      }
    );
  };

  const handleStartEpicSession = () => {
    createSession(
      {
        patient_id: 'mock-patient-id',
        emr_type: 'epic',
      },
      {
        onSuccess: (session) => {
          navigate(`/epic/session/${session.id}`);
        },
      }
    );
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">EMR Practice Dashboard</h1>
          <div className="flex items-center gap-4">
            <span>{user?.full_name}</span>
            <button
              onClick={logout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-8">
        <div className="grid grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Cerner PowerChart</h2>
            <p className="text-gray-600 mb-4">
              Practice EMR documentation in Cerner PowerChart interface
            </p>
            <button
              onClick={handleStartCernerSession}
              className="px-6 py-3 bg-cerner-primary text-white rounded-lg w-full"
            >
              Start Cerner Session
            </button>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Epic EHR</h2>
            <p className="text-gray-600 mb-4">
              Practice EMR documentation in Epic EHR interface
            </p>
            <button
              onClick={handleStartEpicSession}
              className="px-6 py-3 bg-epic-primary text-white rounded-lg w-full"
            >
              Start Epic Session
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};
```

#### Complete EMR Session Flow

**File**: `/home/dev/Development/irStudy/emr-frontend/src/pages/cerner/CernerSession.tsx`

```typescript
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { CernerSidebar } from '@components/cerner/CernerSidebar';
import { PatientBanner } from '@components/cerner/PatientBanner';
import { SOAPNoteEditor } from '@components/cerner/SOAPNoteEditor';
import { useSessions } from '@api/hooks/useSessions';
import { useSOAPNotes } from '@api/hooks/useSOAPNotes';
import { useAutoSave } from '@hooks/useAutoSave';
import { useFormStore } from '@stores/formStore';

export const CernerSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { useSession, completeSession } = useSessions();
  const { saveSoapNote } = useSOAPNotes();
  const { soapNote } = useFormStore();

  const { data: session, isLoading } = useSession(sessionId!);

  // Auto-save SOAP note
  const { isSaving, lastSaved } = useAutoSave({
    interval: 30,
    onSave: async () => {
      if (soapNote && sessionId) {
        await saveSoapNote({
          session_id: sessionId,
          ...soapNote,
        });
      }
    },
  });

  const handleComplete = async () => {
    if (sessionId) {
      completeSession({ sessionId, score: 85 }); // Score from validation
    }
  };

  if (isLoading) return <div>Loading session...</div>;

  return (
    <div className="flex h-screen" data-theme="cerner">
      <CernerSidebar
        currentPath="/cerner/notes"
        onNavigate={(path) => console.log(path)}
        sessionId={sessionId}
      />

      <div className="flex-1 flex flex-col">
        <PatientBanner patient={session.patient} />

        <div className="flex-1 overflow-auto p-6 bg-cerner-bg-dark">
          <SOAPNoteEditor
            sessionId={sessionId!}
            onSave={async (data) => {
              await saveSoapNote({ session_id: sessionId!, ...data });
            }}
          />
        </div>

        <div className="p-4 bg-white border-t flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {isSaving ? 'Saving...' : `Last saved: ${lastSaved?.toLocaleTimeString()}`}
          </div>
          <button
            onClick={handleComplete}
            className="px-6 py-3 bg-green-600 text-white rounded-lg"
          >
            Complete Session
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

### 4.3: End-to-End Testing (3 hours)

#### E2E Test Setup

**File**: `/home/dev/Development/irStudy/emr-frontend/tests/e2e/setup.ts`

```typescript
import { test as base } from '@playwright/test';

// Extend base test with custom fixtures
export const test = base.extend({
  // Authenticated page
  authenticatedPage: async ({ page }, use) => {
    // Login
    await page.goto('http://localhost:5174/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    await use(page);
  },
});

export { expect } from '@playwright/test';
```

#### E2E Tests

**File**: `/home/dev/Development/irStudy/emr-frontend/tests/e2e/complete-session.spec.ts`

```typescript
import { test, expect } from './setup';

test.describe('Complete EMR Session Flow', () => {
  test('should complete Cerner session end-to-end', async ({
    authenticatedPage: page,
  }) => {
    // Step 1: Start session from dashboard
    await page.click('text=Start Cerner Session');
    await expect(page).toHaveURL(/.*\/cerner\/session\/.*/);

    // Step 2: Verify patient banner
    await expect(page.locator('.patient-banner')).toBeVisible();

    // Step 3: Fill SOAP note
    await page.fill('input[name="chiefComplaint"]', 'Chest pain');
    await page.fill(
      'textarea[name="hpi"]',
      'Patient presents with 2 hours of central chest pain, sharp in nature...'
    );

    // Step 4: Fill vitals
    await page.fill('input[name="temperature"]', '37.0');
    await page.fill('input[name="heartRate"]', '85');
    await page.fill('input[name="bloodPressureSystolic"]', '130');
    await page.fill('input[name="bloodPressureDiastolic"]', '80');

    // Step 5: Fill assessment
    await page.fill(
      'textarea[name="assessment"]',
      'Suspected acute coronary syndrome...'
    );

    // Step 6: Fill plan
    await page.fill(
      'textarea[name="plan"]',
      'ECG, troponin, cardiology review...'
    );

    // Step 7: Wait for auto-save
    await expect(page.locator('text=Saved')).toBeVisible({ timeout: 35000 });

    // Step 8: Complete session
    await page.click('text=Complete Session');

    // Step 9: Verify completion
    await expect(page).toHaveURL(/.*\/dashboard/);
    await expect(page.locator('text=Session completed')).toBeVisible();
  });

  test('should validate SOAP note with AI', async ({
    authenticatedPage: page,
  }) => {
    // Start session
    await page.click('text=Start Cerner Session');

    // Fill minimal SOAP note
    await page.fill('input[name="chiefComplaint"]', 'Headache');
    await page.fill(
      'textarea[name="hpi"]',
      'Patient has headache for 2 days...'
    );

    // Trigger AI validation
    await page.click('text=Validate with AI');

    // Wait for validation result
    await expect(page.locator('.validation-feedback')).toBeVisible({
      timeout: 10000,
    });

    // Check for feedback elements
    await expect(page.locator('.clinical-accuracy')).toBeVisible();
    await expect(page.locator('.strengths')).toBeVisible();
    await expect(page.locator('.areas-for-improvement')).toBeVisible();
  });
});
```

---

## Integration Testing Checklist

**Frontend-Backend Integration**:
- [ ] API client configured correctly
- [ ] Authentication flow working (login/logout)
- [ ] JWT token stored and sent correctly
- [ ] 401 redirects to login
- [ ] Session creation working
- [ ] SOAP note save/update working
- [ ] Prescription save working
- [ ] Pathology order save working
- [ ] Auto-save triggering correctly
- [ ] All API hooks working

**User Flows**:
- [ ] Login → Dashboard → Start Session → Document → Complete
- [ ] Theme switching (Cerner/Epic)
- [ ] Patient banner displays correctly
- [ ] SOAP note editor functional
- [ ] Validation triggers correctly
- [ ] Error handling graceful

**E2E Tests**:
- [ ] Playwright configured
- [ ] Authentication test passing
- [ ] Complete session flow passing
- [ ] SOAP note creation passing
- [ ] Validation test passing
- [ ] All tests run successfully

**Performance**:
- [ ] Auto-save completes < 1s
- [ ] Python validation < 1s
- [ ] AI validation 3-5s
- [ ] Page load times acceptable
- [ ] No memory leaks

**Error Handling**:
- [ ] Network errors handled
- [ ] Validation errors displayed
- [ ] API errors shown to user
- [ ] Fallback for AI failures

---

## Deployment Readiness

**Frontend**:
- [ ] Production build works (`npm run build`)
- [ ] Environment variables configured
- [ ] No console errors
- [ ] Lighthouse score > 90

**Backend**:
- [ ] Docker image builds
- [ ] docker-compose up works
- [ ] Database migrations run
- [ ] All endpoints documented
- [ ] API health check working

**Security**:
- [ ] JWT secret changed from default
- [ ] Database credentials secured
- [ ] Anthropic API key in environment
- [ ] CORS origins configured correctly
- [ ] No secrets in git

---

## Time Breakdown

- Frontend-Backend Integration: 4 hours
- Complete User Flows: 3 hours
- End-to-End Testing: 3 hours
- **Total**: 10 hours

---

## Project Complete!

After completing this task, the EMR Practice System is ready for deployment and use in ICRP preparation.

**Total Project Time**: ~60 hours
- Phase 1 (Frontend): 24 hours
- Phase 2 (Validation): 22 hours
- Phase 3 (Backend): 20 hours
- Phase 4 (Integration): 10 hours

---

**Last Updated**: 2026-02-03
**Status**: Ready for Implementation
