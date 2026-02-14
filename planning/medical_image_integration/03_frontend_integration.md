# Task 03: Frontend Integration Testing

**Duration:** 2 hours
**Priority:** P0 (Critical Path)
**Dependencies:** Task 02 (API Endpoint Verification)
**Output:** Verified React components displaying MCQs/OSCEs

---

## Objective

Verify React frontend correctly displays MCQs and OSCEs from PostgreSQL database via FastAPI, with proper filtering, pagination, and user interactions working end-to-end.

---

## Scope

### In Scope
- Verify MCQ list component displays data
- Verify OSCE list component displays data
- Test filtering UI (specialty, difficulty dropdowns)
- Test pagination controls
- Verify individual MCQ/OSCE detail views
- Test answer submission and feedback
- Mobile responsiveness check
- Accessibility audit (WCAG 2.2 AA)

### Out of Scope
- User authentication (covered separately)
- Progress tracking (covered separately)
- Image display (Task 09)
- Performance optimization beyond basic checks

---

## Prerequisites

### Completed Tasks
- ✅ Task 01: Database seeded with data
- ✅ Task 02: API endpoints verified and working

### Running Services
- FastAPI backend running on `http://localhost:8000`
- React frontend dev server running on `http://localhost:5173`
- PostgreSQL database accessible

### Frontend Stack
- React 18+
- TanStack Query (React Query) for API calls
- React Router for navigation
- Tailwind CSS for styling

---

## Implementation Steps

### Step 1: Start Frontend Dev Server (5 min)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (if not done)
npm install

# Start dev server
npm run dev

# Expected output:
#   VITE ready in 324 ms
#   ➜  Local:   http://localhost:5173/
#   ➜  Network: use --host to expose
```

**Verify frontend loads:**
```bash
curl -s http://localhost:5173 | grep -i "react"
# Should return HTML with React app
```

---

### Step 2: Verify TanStack Query API Client (15 min)

Check that API client is configured correctly:

**File:** `frontend/src/api/client.ts`

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
```

**File:** `frontend/src/api/mcqs.ts`

```typescript
import { apiClient } from './client';
import type { MCQ, MCQListResponse, MCQFilters } from '@/types/mcq';

export const mcqApi = {
  /**
   * Get paginated list of MCQs with optional filtering
   */
  getMCQs: async (params: {
    limit?: number;
    offset?: number;
    specialty?: string;
    difficulty?: string;
    tags?: string[];
  }): Promise<MCQListResponse> => {
    const response = await apiClient.get<MCQListResponse>('/mcqs', { params });
    return response.data;
  },

  /**
   * Get single MCQ by ID
   */
  getMCQById: async (questionId: string): Promise<MCQ> => {
    const response = await apiClient.get<MCQ>(`/mcqs/${questionId}`);
    return response.data;
  },
};
```

**File:** `frontend/src/api/osces.ts`

```typescript
import { apiClient } from './client';
import type { OSCE, OSCEListResponse, OSCECategories } from '@/types/osce';

export const osceApi = {
  /**
   * Get paginated list of OSCEs
   */
  getOSCEs: async (params: {
    limit?: number;
    offset?: number;
    specialty?: string;
    station_type?: string;
  }): Promise<OSCEListResponse> => {
    const response = await apiClient.get<OSCEListResponse>('/osces', { params });
    return response.data;
  },

  /**
   * Get OSCE categories for filtering
   */
  getCategories: async (): Promise<OSCECategories> => {
    const response = await apiClient.get<OSCECategories>('/osces/categories');
    return response.data;
  },

  /**
   * Get single OSCE by ID
   */
  getOSCEById: async (osceId: string): Promise<OSCE> => {
    const response = await apiClient.get<OSCE>(`/osces/${osceId}`);
    return response.data;
  },
};
```

---

### Step 3: Test MCQ List Component (30 min)

**Navigate to MCQ page:**
```
http://localhost:5173/mcqs
```

**Expected behavior:**

1. **Initial Load:**
   - Page displays loading spinner
   - After 1-2 seconds, displays list of 20 MCQs
   - Each MCQ card shows:
     - Question ID (e.g., "WEEK3-CARDIO-001")
     - Specialty badge (color-coded)
     - Topic
     - Difficulty indicator
     - First line of scenario text
     - "View Details" button

2. **Filtering:**
   - Specialty dropdown populated with:
     - All Specialties (default)
     - Cardiology
     - Respiratory
     - Psychiatry
     - etc.
   - Selecting "Cardiology" filters to only cardiology MCQs
   - Difficulty dropdown works (Easy, Medium, Hard)
   - Filters update URL: `/mcqs?specialty=CARDIOLOGY&difficulty=HARD`

3. **Pagination:**
   - Shows "Page 1 of 50" (or similar)
   - "Next" button loads next 20 MCQs
   - "Previous" button loads previous page
   - Direct page number input works

4. **Search:**
   - Search box filters by question text, topic, or tags
   - Typing "ECG" shows only ECG-related MCQs
   - Search is debounced (waits 300ms after typing stops)

**Component verification:**

```typescript
// frontend/src/pages/MCQList.tsx

import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { mcqApi } from '@/api/mcqs';
import { MCQCard } from '@/components/MCQCard';
import { FilterBar } from '@/components/FilterBar';
import { Pagination } from '@/components/Pagination';

export function MCQList() {
  const [filters, setFilters] = useState({
    specialty: '',
    difficulty: '',
    limit: 20,
    offset: 0,
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['mcqs', filters],
    queryFn: () => mcqApi.getMCQs(filters),
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">MCQ Practice</h1>

      <FilterBar filters={filters} onChange={setFilters} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        {data?.mcqs.map((mcq) => (
          <MCQCard key={mcq.question_id} mcq={mcq} />
        ))}
      </div>

      <Pagination
        total={data?.total || 0}
        limit={filters.limit}
        offset={filters.offset}
        onPageChange={(offset) => setFilters({ ...filters, offset })}
      />
    </div>
  );
}
```

**Test checklist:**
- [ ] Page loads without errors
- [ ] 20 MCQs displayed
- [ ] Specialty filter works
- [ ] Difficulty filter works
- [ ] Pagination works (Next/Previous)
- [ ] Search works
- [ ] URL updates with filters
- [ ] Loading states display correctly
- [ ] Error states handled

---

### Step 4: Test MCQ Detail View (20 min)

**Navigate to single MCQ:**
```
http://localhost:5173/mcqs/WEEK3-CARDIO-001
```

**Expected behavior:**

1. **Question Display:**
   - Full scenario text displayed
   - Question stem clear and readable
   - 5 options (A, B, C, D, E) in radio buttons or cards
   - "Submit Answer" button enabled after selection

2. **Answer Submission:**
   - User selects option "E"
   - Clicks "Submit Answer"
   - Correct answer highlighted in green
   - Incorrect options grayed out
   - If wrong, shows correct answer

3. **Explanation Display:**
   - After submission, explanation appears
   - Learning points displayed as bullet list
   - Citation shown at bottom
   - Tags displayed as badges

4. **Navigation:**
   - "Next Question" button loads next MCQ
   - "Back to List" button returns to MCQ list

**Component verification:**

```typescript
// frontend/src/pages/MCQDetail.tsx

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { useState } from 'react';
import { mcqApi } from '@/api/mcqs';

export function MCQDetail() {
  const { questionId } = useParams<{ questionId: string }>();
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const { data: mcq, isLoading } = useQuery({
    queryKey: ['mcq', questionId],
    queryFn: () => mcqApi.getMCQById(questionId!),
    enabled: !!questionId,
  });

  if (isLoading) return <LoadingSpinner />;
  if (!mcq) return <div>MCQ not found</div>;

  const handleSubmit = () => {
    setSubmitted(true);
    // TODO: Track user progress
  };

  const isCorrect = selectedAnswer === mcq.correct_answer;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Metadata */}
      <div className="flex gap-2 mb-4">
        <span className="badge">{mcq.specialty}</span>
        <span className="badge">{mcq.difficulty}</span>
      </div>

      {/* Question */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Scenario</h2>
        <p className="text-gray-700 mb-6">{mcq.question.scenario}</p>

        <h2 className="text-xl font-semibold mb-4">Question</h2>
        <p className="text-gray-900 font-medium mb-6">{mcq.question.stem}</p>

        {/* Options */}
        <div className="space-y-3">
          {Object.entries(mcq.options).map(([key, value]) => (
            <label
              key={key}
              className={`block p-4 border rounded-lg cursor-pointer ${
                submitted
                  ? key === mcq.correct_answer
                    ? 'border-green-500 bg-green-50'
                    : selectedAnswer === key
                    ? 'border-red-500 bg-red-50'
                    : 'border-gray-300'
                  : selectedAnswer === key
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-blue-300'
              }`}
            >
              <input
                type="radio"
                name="answer"
                value={key}
                checked={selectedAnswer === key}
                onChange={() => setSelectedAnswer(key)}
                disabled={submitted}
                className="mr-3"
              />
              <span className="font-medium">{key}.</span> {value}
            </label>
          ))}
        </div>

        {/* Submit Button */}
        {!submitted && (
          <button
            onClick={handleSubmit}
            disabled={!selectedAnswer}
            className="btn btn-primary mt-6"
          >
            Submit Answer
          </button>
        )}
      </div>

      {/* Explanation (shown after submission) */}
      {submitted && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className={`mb-4 p-4 rounded ${isCorrect ? 'bg-green-100' : 'bg-red-100'}`}>
            {isCorrect ? '✓ Correct!' : `✗ Incorrect. Correct answer: ${mcq.correct_answer}`}
          </div>

          <h3 className="text-lg font-semibold mb-3">Explanation</h3>
          <p className="text-gray-700 mb-4">{mcq.explanation}</p>

          {mcq.learning_points && (
            <>
              <h3 className="text-lg font-semibold mb-3">Key Learning Points</h3>
              <ul className="list-disc list-inside space-y-2">
                {mcq.learning_points.map((point, idx) => (
                  <li key={idx} className="text-gray-700">{point}</li>
                ))}
              </ul>
            </>
          )}

          <div className="mt-6 pt-6 border-t">
            <p className="text-sm text-gray-600">
              <strong>Citation:</strong> {mcq.citation}
            </p>
          </div>

          <div className="flex gap-2 mt-4">
            {mcq.tags.map((tag) => (
              <span key={tag} className="badge badge-outline">{tag}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

**Test checklist:**
- [ ] Question displays correctly
- [ ] All options visible
- [ ] Can select an option
- [ ] Submit button works
- [ ] Correct answer highlighted green
- [ ] Explanation shows after submission
- [ ] Learning points displayed
- [ ] Citation visible
- [ ] Tags displayed

---

### Step 5: Test OSCE List Component (20 min)

**Navigate to OSCE page:**
```
http://localhost:5173/osces
```

**Expected behavior:**

1. **Category Selector:**
   - Dropdown shows specialties with counts
     - Cardiology (50)
     - Obstetrics & Gynaecology (20)
     - Psychiatry (30)
   - Selecting specialty shows topics for that specialty
   - Selecting topic shows station types

2. **OSCE Cards:**
   - Each card shows:
     - OSCE title
     - Specialty and topic
     - Station type (History Taking, Physical Exam, etc.)
     - Duration (8 minutes)
     - Difficulty indicator
     - "Start Station" button

3. **Filtering:**
   - Filter by specialty
   - Filter by station type
   - Filters persist in URL

**Component verification:**

```typescript
// frontend/src/pages/OSCEList.tsx

import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { osceApi } from '@/api/osces';
import { OSCECard } from '@/components/OSCECard';

export function OSCEList() {
  const [filters, setFilters] = useState({
    specialty: '',
    station_type: '',
    limit: 20,
    offset: 0,
  });

  const { data: osces, isLoading } = useQuery({
    queryKey: ['osces', filters],
    queryFn: () => osceApi.getOSCEs(filters),
  });

  const { data: categories } = useQuery({
    queryKey: ['osce-categories'],
    queryFn: osceApi.getCategories,
  });

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">OSCE Stations</h1>

      {/* Category-based filter */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filters.specialty}
            onChange={(e) => setFilters({ ...filters, specialty: e.target.value })}
            className="select"
          >
            <option value="">All Specialties</option>
            {categories?.specialties.map((spec) => (
              <option key={spec.specialty} value={spec.specialty}>
                {spec.specialty} ({spec.count})
              </option>
            ))}
          </select>

          <select
            value={filters.station_type}
            onChange={(e) => setFilters({ ...filters, station_type: e.target.value })}
            className="select"
          >
            <option value="">All Station Types</option>
            <option value="HISTORY_TAKING">History Taking</option>
            <option value="PHYSICAL_EXAMINATION">Physical Examination</option>
            <option value="BREAKING_BAD_NEWS">Breaking Bad News</option>
            <option value="MANAGEMENT">Management</option>
          </select>
        </div>
      </div>

      {/* OSCE Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {osces?.osces.map((osce) => (
          <OSCECard key={osce.osce_id} osce={osce} />
        ))}
      </div>

      <Pagination
        total={osces?.total || 0}
        limit={filters.limit}
        offset={filters.offset}
        onPageChange={(offset) => setFilters({ ...filters, offset })}
      />
    </div>
  );
}
```

**Test checklist:**
- [ ] Page loads with OSCEs
- [ ] Category dropdown populated from API
- [ ] Specialty filter works
- [ ] Station type filter works
- [ ] OSCE cards display correctly
- [ ] Pagination works
- [ ] Counts match API data

---

### Step 6: Mobile Responsiveness (15 min)

**Test on different screen sizes:**

```bash
# Open browser DevTools
# Toggle device toolbar (Ctrl+Shift+M or Cmd+Shift+M)
```

**Test these viewports:**
- Mobile: 375x667 (iPhone SE)
- Tablet: 768x1024 (iPad)
- Desktop: 1920x1080

**Check:**
- [ ] MCQ cards stack vertically on mobile
- [ ] Filter dropdowns work on mobile
- [ ] Buttons are touch-friendly (min 44x44px)
- [ ] Text is readable (min 16px font size)
- [ ] No horizontal scrolling
- [ ] Navigation menu collapses on mobile

---

### Step 7: Accessibility Audit (20 min)

**Run Lighthouse audit:**

```bash
# In Chrome DevTools
# Lighthouse tab > Generate report
```

**Target scores:**
- Performance: >90
- Accessibility: >95
- Best Practices: >90
- SEO: >90

**Manual accessibility checks:**

```bash
# Install axe DevTools extension
# Run automated scan
```

**Check:**
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Focus indicators visible
- [ ] Color contrast ratio ≥4.5:1 for text
- [ ] Headings in logical order (h1 → h2 → h3)
- [ ] Screen reader announces page changes
- [ ] ARIA labels on interactive elements

**Test keyboard navigation:**
- [ ] Tab through all MCQ options
- [ ] Enter submits answer
- [ ] Tab to "Next Question" button
- [ ] Arrow keys navigate pagination

---

### Step 8: Error Handling (10 min)

**Test error scenarios:**

1. **API Offline:**
   ```bash
   # Stop FastAPI backend
   pkill uvicorn
   ```
   - [ ] Frontend shows "Connection error" message
   - [ ] Retry button works

2. **Invalid MCQ ID:**
   ```
   http://localhost:5173/mcqs/DOES-NOT-EXIST
   ```
   - [ ] Shows "MCQ not found" page
   - [ ] "Back to list" link works

3. **Slow Network:**
   ```bash
   # In Chrome DevTools
   # Network tab > Throttling > Slow 3G
   ```
   - [ ] Loading spinners show
   - [ ] Data loads without errors

---

## Testing Checklist

### MCQ Features
- [ ] MCQ list displays 1,000+ questions
- [ ] Filtering by specialty works
- [ ] Filtering by difficulty works
- [ ] Search works
- [ ] Pagination works
- [ ] MCQ detail page displays correctly
- [ ] Answer submission works
- [ ] Correct/incorrect feedback shows
- [ ] Explanation displays after submission
- [ ] Next question navigation works

### OSCE Features
- [ ] OSCE list displays 140+ stations
- [ ] Category dropdown populated from API
- [ ] Filtering by specialty works
- [ ] Filtering by station type works
- [ ] OSCE cards display correctly
- [ ] Pagination works

### Responsiveness
- [ ] Mobile layout works (375px width)
- [ ] Tablet layout works (768px width)
- [ ] Desktop layout works (1920px width)
- [ ] No horizontal scrolling on any size

### Accessibility
- [ ] Lighthouse accessibility score >95
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast meets WCAG 2.2 AA

### Error Handling
- [ ] API errors show user-friendly messages
- [ ] 404 pages work
- [ ] Loading states display
- [ ] Retry functionality works

---

## Success Criteria

- ✅ MCQ list component displays all 1,000+ MCQs
- ✅ OSCE list component displays all 140+ OSCEs
- ✅ Filtering works for all parameters
- ✅ Pagination works correctly
- ✅ MCQ detail view fully functional
- ✅ Answer submission and feedback works
- ✅ Mobile responsive (375px+)
- ✅ Accessibility score >95 (Lighthouse)
- ✅ No console errors
- ✅ Error handling works properly

---

## Rollback Plan

If frontend issues found:

1. Check API connectivity:
   ```bash
   curl http://localhost:8000/api/v1/mcqs?limit=1
   ```

2. Check browser console for errors:
   ```
   F12 > Console tab
   ```

3. Verify environment variables:
   ```bash
   # frontend/.env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. Clear cache and rebuild:
   ```bash
   npm run clean
   npm install
   npm run dev
   ```

---

## Common Issues

### Issue 1: "Network Error" in browser
**Solution:** Ensure backend is running on port 8000

### Issue 2: "CORS Error"
**Solution:** Add CORS middleware in FastAPI:
```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: Data not displaying
**Solution:** Check TanStack Query DevTools for failed queries

### Issue 4: Filters not working
**Solution:** Verify URL params are being sent to API

---

## Next Task

After successful frontend verification, proceed to **Task 04: Image Metadata Processing**

File: `04_image_metadata_processing.md`
