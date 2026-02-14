import { http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const handlers = [
  // Mock login endpoint
  http.post(`${API_BASE_URL}/auth/login`, async ({ request }) => {
    const body: any = await request.json();

    // Mock student login
    if (body.email === 'student@test.com' && body.password === 'Student123!@#') {
      return HttpResponse.json({
        access_token: 'mock-student-access-token',
        refresh_token: 'mock-student-refresh-token',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'student@test.com',
          full_name: 'Test Student',
          role: 'student',
          is_verified: true,
          is_active: true,
          created_at: new Date().toISOString(),
        },
      });
    }

    // Mock educator login
    if (body.email === 'educator@test.com' && body.password === 'Educator123!@#') {
      return HttpResponse.json({
        access_token: 'mock-educator-access-token',
        refresh_token: 'mock-educator-refresh-token',
        token_type: 'bearer',
        user: {
          id: 2,
          email: 'educator@test.com',
          full_name: 'Test Educator',
          role: 'educator',
          is_verified: true,
          is_active: true,
          created_at: new Date().toISOString(),
        },
      });
    }

    // Mock invalid credentials
    return HttpResponse.json(
      { detail: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  // Mock permissions endpoint
  http.get(`${API_BASE_URL}/permissions/me`, ({ request }) => {
    const auth = request.headers.get('Authorization');
    
    if (auth?.includes('mock-student-access-token')) {
      return HttpResponse.json({
        role: 'student',
        permissions: [
          'mcq.view',
          'mcq.attempt',
          'osce.view',
          'osce.attempt',
          'progress.view.own',
          'studycard.view',
        ],
      });
    }

    if (auth?.includes('mock-educator-access-token')) {
      return HttpResponse.json({
        role: 'educator',
        permissions: [
          'mcq.view', 'mcq.attempt', 'mcq.create', 'mcq.update', 'mcq.delete',
          'osce.view', 'osce.attempt', 'osce.create', 'osce.update', 'osce.delete',
          'progress.view.all', 'progress.view.own', 'progress.grade',
          'studycard.view', 'studycard.create',
        ],
      });
    }

    return HttpResponse.json({ detail: 'Unauthorized' }, { status: 401 });
  }),

  // Mock MCQ list endpoint
  http.get(`${API_BASE_URL}/mcqs`, ({ request }) => {
    const auth = request.headers.get('Authorization');
    
    if (auth?.includes('mock-student-access-token') || auth?.includes('mock-educator-access-token')) {
      return HttpResponse.json({
        items: [],
        total: 0,
        page: 1,
        size: 10,
      });
    }

    return HttpResponse.json({ detail: 'Unauthorized' }, { status: 401 });
  }),

  // Mock OSCE list endpoint
  http.get(`${API_BASE_URL}/osces`, ({ request }) => {
    const auth = request.headers.get('Authorization');
    
    if (auth?.includes('mock-student-access-token') || auth?.includes('mock-educator-access-token')) {
      return HttpResponse.json({
        items: [],
        total: 0,
        page: 1,
        size: 10,
      });
    }

    return HttpResponse.json({ detail: 'Unauthorized' }, { status: 401 });
  }),

  // Mock progress endpoint
  http.get(`${API_BASE_URL}/progress/me`, ({ request }) => {
    const auth = request.headers.get('Authorization');
    
    if (auth?.includes('mock-student-access-token') || auth?.includes('mock-educator-access-token')) {
      return HttpResponse.json({
        user_id: 1,
        mcq_completed: 0,
        mcq_total: 0,
        osce_completed: 0,
        osce_total: 0,
        average_score: 0,
      });
    }

    return HttpResponse.json({ detail: 'Unauthorized' }, { status: 401 });
  }),
];
