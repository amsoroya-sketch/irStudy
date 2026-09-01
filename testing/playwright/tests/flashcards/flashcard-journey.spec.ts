/**
 * Flashcard / Study-Card E2E Test Suite — REAL AUTH VERSION
 *
 * Uses actual backend login (student@test.com / Student123!@#)
 * Mocks only non-auth endpoints to keep tests deterministic and fast.
 *
 * Covers:
 *   1. Viewing due cards          — loading, progress, card display
 *   2. Flipping cards             — show answer, citations visibility
 *   3. SM-2 review submission     — quality ratings, advancing cards
 *   4. Completion state           — all cards reviewed message
 *   5. Empty state                — no cards due message
 *   6. Mobile navigation          — bottom nav to study cards
 */

import { test, expect, Page } from '@playwright/test';

const API_BASE_URL = 'http://localhost:8001/api/v1';

// ═════════════════════════════════════════════════════════════════════════════
// REAL USER CREDENTIALS (must exist in database with is_verified=true)
// ═════════════════════════════════════════════════════════════════════════════

const REAL_STUDENT = {
  email: 'student@test.com',
  password: 'Student123!@#',
};

// ═════════════════════════════════════════════════════════════════════════════
// MOCK DATA — Australian medical study cards
// ═════════════════════════════════════════════════════════════════════════════

const MOCK_CARDS = [
  {
    id: 1,
    card_id: 'CARD-CARD-0001',
    specialty: 'cardiology',
    topic: 'Medicine',
    subtopic: 'red_flags',
    question: 'What are the red flags for AAA rupture?',
    answer: 'Classic triad: hypotension, pulsatile abdominal mass, abdominal/back/flank pain.',
    explanation: 'Source: Medicine/01_GI_Abdominal_Pain_Differentials.html',
    citations: [
      { source: 'ICRP OSCE', qdrant_point_id: 'uuid-1', confidence: 0.92, page: '45' },
    ],
    difficulty: 'hard',
    tags: ['red-flag', 'critical'],
    card_type: 'clinical_pearl',
    next_review_date: new Date().toISOString(),
    interval_days: 1,
    ease_factor: 2.5,
    repetitions: 0,
    is_active: true,
    user_id: null,
  },
  {
    id: 2,
    card_id: 'CARD-CARD-0002',
    specialty: 'gastroenterology',
    topic: 'Medicine_Gastroenterology',
    subtopic: 'differentials',
    question: 'What are the causes of RUQ pain?',
    answer: 'Biliary colic, acute cholecystitis, ascending cholangitis, hepatitis, pyelonephritis, pneumonia.',
    explanation: 'Source: Medicine/01_GI_Abdominal_Pain_Differentials.html',
    citations: [
      { source: 'ICRP OSCE', qdrant_point_id: 'uuid-2', confidence: 0.88, page: '112' },
    ],
    difficulty: 'medium',
    tags: ['differential'],
    card_type: 'concept',
    next_review_date: new Date().toISOString(),
    interval_days: 1,
    ease_factor: 2.5,
    repetitions: 0,
    is_active: true,
    user_id: null,
  },
  {
    id: 3,
    card_id: 'GENE-CARD-0001',
    specialty: 'general_practice',
    topic: 'Australian Context',
    subtopic: 'australian',
    question: 'What is the PBS?',
    answer: 'Pharmaceutical Benefits Scheme — Australian government subsidy for medications.',
    explanation: 'Source: Australian Context/PBS_Guide.html',
    citations: [
      { source: 'PBS Schedule', qdrant_point_id: 'uuid-3', confidence: 0.95, page: '1' },
    ],
    difficulty: 'easy',
    tags: ['australian', 'PBS'],
    card_type: 'concept',
    next_review_date: new Date().toISOString(),
    interval_days: 1,
    ease_factor: 2.5,
    repetitions: 0,
    is_active: true,
    user_id: null,
  },
];

// ═════════════════════════════════════════════════════════════════════════════
// HELPERS
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Log in via the real UI using verified test credentials.
 * Dashboard endpoints are mocked beforehand so the post-login landing
 * page does not hit 404/500 backend errors.
 */
async function realLogin(page: Page) {
  // Set up non-auth mocks BEFORE navigating
  await setupDashboardMocks(page);

  await page.goto('/login');
  await page.fill('input[name="email"]', REAL_STUDENT.email);
  await page.fill('input[name="password"]', REAL_STUDENT.password);

  // Click submit and wait for client-side redirect to dashboard
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard', { timeout: 15000 });
}

/**
 * Mock dashboard and progress endpoints so the login → dashboard flow
 * renders quickly without relying on incomplete backend data.
 * Auth endpoints are intentionally NOT mocked — real tokens are used.
 */
async function setupDashboardMocks(page: Page) {
  // ── Progress / dashboard (prevent 404/500 on landing) ──
  await page.route(API_BASE_URL + '/progress/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_mcq_attempts: 42,
        mcq_accuracy_rate: 78.5,
        total_osce_completions: 15,
        study_cards_reviewed: 120,
        study_card_retention_rate: 85.0,
        weak_areas: ['Cardiology', 'Psychiatry'],
        specialty_breakdown: [{ specialty: 'Cardiology', attempts: 20, accuracy: 65.0 }],
      }),
    });
  });

  await page.route(API_BASE_URL + '/progress/weekly-trends**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        trends: [
          { week: '2026-W01', attempts: 10, accuracy: 70.0 },
          { week: '2026-W02', attempts: 15, accuracy: 80.0 },
        ],
      }),
    });
  });

  await page.route(API_BASE_URL + '/progress/dashboard/emr', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_sessions: 5,
        completed_sessions: 3,
        in_progress_sessions: 2,
        avg_validation_score: 78.5,
        avg_typing_wpm: 45,
        improvement_percentage: 12.5,
        ahpra_compliance_rate: 92.0,
        total_time_spent_seconds: 3600,
        epic_sessions: 3,
        cerner_sessions: 2,
        specialty_stats: [{ specialty: 'Cardiology', session_count: 2, avg_score: 80.0 }],
      }),
    });
  });

  await page.route(API_BASE_URL + '/emr/sessions**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sessions: [] }),
    });
  });

  await page.route(API_BASE_URL + '/progress/weekly-trends/unified**', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ trends: [] }) });
  });

  await page.route(API_BASE_URL + '/progress/weak-areas/emr**', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ weak_areas: [] }) });
  });

  await page.route(API_BASE_URL + '/integration/conversion-stats', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ total_conversions: 0, average_pre_fill_percentage: 0, last_conversion_at: null }),
    });
  });

  await page.route(API_BASE_URL + '/dashboard/overview', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        overall_progress: {
          total_sessions: 42,
          completion_percentage: 65,
          avg_score: 78.5,
          total_time_minutes: 360,
          last_activity: new Date().toISOString(),
        },
        modules: {
          mcq: { total_attempts: 120, average_score: 75, last_activity: new Date().toISOString(), completion_rate: 60 },
          osce: { total_attempts: 30, average_score: 82, last_activity: new Date().toISOString(), completion_rate: 45 },
          emr: { total_sessions: 15, average_score: 70, last_activity: new Date().toISOString(), completion_rate: 30 },
          mock_exam: { total_exams: 3, average_score: 68, last_activity: new Date().toISOString(), completion_rate: 25 },
        },
        specialty_breakdown: [
          { specialty: 'Cardiology', attempts: 25, avg_score: 72, strength: 'average' },
          { specialty: 'Respiratory', attempts: 20, avg_score: 80, strength: 'good' },
        ],
        recent_activity: [
          { type: 'mcq', description: 'Attempted 10 Cardiology MCQs', score: 80, timestamp: new Date().toISOString() },
        ],
        recommendations: [
          { module: 'MCQ', specialty: 'Cardiology', reason: 'Accuracy below 75%', priority: 'high' },
        ],
      }),
    });
  });
}

/**
 * Mock study-card endpoints for deterministic card content and counts.
 */
async function setupStudyCardMocks(page: Page, cards = MOCK_CARDS) {
  await page.route(API_BASE_URL + '/study-cards/due-cards**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ total_due: cards.length, cards }),
    });
  });

  await page.route(API_BASE_URL + '/study-cards/review', async (route, request) => {
    if (request.method() === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          card_id: 1,
          quality: 3,
          next_review_date: new Date(Date.now() + 86400000).toISOString(),
          interval_days: 1,
          ease_factor: 2.5,
          repetitions: 1,
          message: 'Good work! Next review in 1 day(s). Correct, after hesitation.',
          quality_description: 'Correct, after hesitation',
        }),
      });
      return;
    }
    await route.continue();
  });
}

// ═════════════════════════════════════════════════════════════════════════════
// TEST SUITE
// ═════════════════════════════════════════════════════════════════════════════

test.setTimeout(120000);

test.describe('🎴 Flashcard Review Journey (Real Auth)', () => {
  test('should display flashcards due for review', async ({ page }) => {
    await realLogin(page);
    await setupStudyCardMocks(page, MOCK_CARDS);

    await page.goto('/study-cards');

    const card = page.locator('[data-testid="flashcard-card"]');
    await expect(card).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(MOCK_CARDS[0].question)).toBeVisible();
    await expect(page.getByText(/Card 1 of 3/)).toBeVisible();
  });

  test('should flip card and show answer with citations', async ({ page }) => {
    await realLogin(page);
    await setupStudyCardMocks(page, [MOCK_CARDS[0]]);

    await page.goto('/study-cards');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 10000 });

    // Answer hidden initially
    await expect(page.getByText(MOCK_CARDS[0].answer)).not.toBeVisible();

    // Flip
    await page.getByRole('button', { name: /Show Answer/i }).click();
    await expect(page.getByText(MOCK_CARDS[0].answer)).toBeVisible();

    // Citations visible
    await expect(page.getByText(/Sources:/i)).toBeVisible();
    await expect(page.getByText(/ICRP OSCE/)).toBeVisible();
  });

  test('should submit review and advance to next card', async ({ page }) => {
    await realLogin(page);
    await setupStudyCardMocks(page, [MOCK_CARDS[0], MOCK_CARDS[1]]);

    await page.goto('/study-cards');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 10000 });

    await expect(page.getByText(MOCK_CARDS[0].question)).toBeVisible();
    await expect(page.getByText(/Card 1 of 2/)).toBeVisible();

    // Show answer and rate Good
    await page.getByRole('button', { name: /Show Answer/i }).click();
    await expect(page.getByText(MOCK_CARDS[0].answer)).toBeVisible();
    await page.getByRole('button', { name: /Good \(3\)/i }).click();

    // Advance to second card
    await expect(page.getByText(MOCK_CARDS[1].question)).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/Card 2 of 2/)).toBeVisible();
  });

  test('should show completion message when all cards reviewed', async ({ page }) => {
    await realLogin(page);
    await setupStudyCardMocks(page, [MOCK_CARDS[0]]);

    await page.goto('/study-cards');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 10000 });

    await page.getByRole('button', { name: /Show Answer/i }).click();
    await expect(page.getByText(MOCK_CARDS[0].answer)).toBeVisible();
    await page.getByRole('button', { name: /Good \(3\)/i }).click();

    await expect(page.getByText(/All Cards Reviewed!/i)).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/You've reviewed all cards due today/i)).toBeVisible();
  });

  test('should show empty state when no cards are due', async ({ page }) => {
    await realLogin(page);
    await setupStudyCardMocks(page, []);

    await page.goto('/study-cards');

    await expect(page.getByText(/No Cards Due for Review/i)).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/Great job! Check back tomorrow for more cards/i)).toBeVisible();
  });

  test('should navigate to study cards from bottom navigation', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 375, height: 667 } });
    const page = await context.newPage();

    await realLogin(page);
    await setupStudyCardMocks(page, MOCK_CARDS);

    // Start on dashboard
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/dashboard');
    await page.waitForSelector('h1:has-text("Dashboard")', { timeout: 15000 });

    // Click Study in bottom nav
    const studyNav = page.locator('[role="navigation"] button[aria-label="Study"]');
    await expect(studyNav).toBeVisible();
    await studyNav.click();

    await page.waitForURL('/study-cards', { timeout: 10000 });
    await expect(page).toHaveURL('/study-cards');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible();

    await context.close();
  });
});
