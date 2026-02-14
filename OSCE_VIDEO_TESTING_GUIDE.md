# OSCE Video Integration - Comprehensive Testing Guide

## 🎥 Video Recording & Testing Plan

This guide provides step-by-step instructions for testing the video integration feature and recording demonstration videos.

**Last Updated:** February 13, 2026
**Test Type:** End-to-End (E2E) with Playwright Video Recording

---

## 📋 Pre-Test Checklist

### Environment Setup

```bash
# 1. Start all Docker services
docker compose up -d postgres redis qdrant

# 2. Wait for services to be healthy
docker compose ps

# Expected output:
# irstudy-postgres   Up (healthy)
# irstudy-redis      Up (healthy)
# irstudy-qdrant     Up (healthy)

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install/update dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 5. Run database migration
cd ../backend
export DATABASE_PASSWORD="your-db-password"
alembic upgrade head

# Should see: Running upgrade ... -> 004_video_resources

# 6. Populate video data
cd ..
python scripts/populate_osce_videos.py
# Type 'y' when prompted

# Expected: ✅ Success! Updated 7 OSCEs with video resources
```

---

## 🎬 Test Scenarios

### Test 1: Video Component Renders

**Objective:** Verify video component displays correctly

```typescript
// frontend/tests/e2e/osce-videos.spec.ts

import { test, expect } from '@playwright/test';

test.describe('OSCE Video Resources', () => {
  test('should display video component on OSCE detail page', async ({ page }) => {
    // Navigate to OSCE with videos
    await page.goto('/osces/1'); // Cardiovascular OSCE

    // Check video component exists
    const videoSection = page.locator('h3:has-text("Video Demonstrations")');
    await expect(videoSection).toBeVisible();

    // Check essential videos category
    const essentialBadge = page.locator('text=Essential - Watch These First');
    await expect(essentialBadge).toBeVisible();

    // Check video cards render
    const videoCards = page.locator('[class*="video-card"]');
    await expect(videoCards).toHaveCount(4); // Cardiovascular has 4 essential videos
  });

  test('should display video details correctly', async ({ page }) => {
    await page.goto('/osces/1');

    // Check first video card
    const firstVideo = page.locator('[class*="video-card"]').first();

    // Title should be visible
    await expect(firstVideo.locator('h4')).toContainText('Cardiovascular Examination');

    // Source should be visible
    await expect(firstVideo).toContainText('Stanford Medicine 25');

    // Duration indicator
    await expect(firstVideo).toContainText('10 min');

    // Focus description
    await expect(firstVideo).toContainText('Complete systematic cardiac examination');

    // Watch button
    const watchButton = firstVideo.locator('text=Watch Video');
    await expect(watchButton).toBeVisible();
  });
});
```

### Test 2: Interactive Elements

```typescript
test('should expand "Why recommended?" section', async ({ page }) => {
  await page.goto('/osces/1');

  // Find collapse button
  const whyRecommendedButton = page.locator('button:has-text("Why recommended?")').first();

  // Initially collapsed
  await expect(whyRecommendedButton).toHaveAttribute('aria-expanded', 'false');

  // Click to expand
  await whyRecommendedButton.click();
  await expect(whyRecommendedButton).toHaveAttribute('aria-expanded', 'true');

  // Content should be visible
  const expandedContent = page.locator('text=Gold standard demonstration');
  await expect(expandedContent).toBeVisible();

  // Australian relevance section
  const australianRelevance = page.locator('text=Australian AMC Clinical Exam Relevance');
  await expect(australianRelevance).toBeVisible();
});

test('should toggle supplementary videos section', async ({ page }) => {
  await page.goto('/osces/1');

  // Find supplementary toggle
  const suppToggle = page.locator('button:has-text("Supplementary Videos")');

  if (await suppToggle.isVisible()) {
    // Click to show
    await suppToggle.click();

    // Supplementary videos should appear
    const suppVideos = page.locator('[class*="video-card"][category="supplementary"]');
    await expect(suppVideos.first()).toBeVisible();

    // Click to hide
    await suppToggle.click();
    await expect(suppVideos.first()).not.toBeVisible();
  }
});
```

### Test 3: External Links

```typescript
test('should open video links in new tab', async ({ page, context }) => {
  await page.goto('/osces/1');

  // Set up new page listener
  const [newPage] = await Promise.all([
    context.waitForEvent('page'),
    page.locator('text=Watch Video').first().click()
  ]);

  // Verify new tab opened
  expect(newPage.url()).toContain('https://');

  // Verify it's from trusted source
  const url = newPage.url();
  const trustedSources = [
    'stanfordmedicine25.stanford.edu',
    'geekymedics.com',
    'oxfordmedicaleducation.com'
  ];

  const isTrusted = trustedSources.some(source => url.includes(source));
  expect(isTrusted).toBeTruthy();
});
```

### Test 4: Responsive Design

```typescript
test('should display correctly on mobile', async ({ page }) => {
  // Set mobile viewport
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/osces/1');

  // Video section should still be visible
  await expect(page.locator('h3:has-text("Video Demonstrations")')).toBeVisible();

  // Cards should stack vertically (single column)
  const videoCards = page.locator('[class*="video-card"]');
  const firstCard = videoCards.first();
  const secondCard = videoCards.nth(1);

  // Get positions
  const firstBox = await firstCard.boundingBox();
  const secondBox = await secondCard.boundingBox();

  // Second card should be below first (not beside)
  expect(secondBox!.y).toBeGreaterThan(firstBox!.y + firstBox!.height);
});

test('should display correctly on tablet', async ({ page }) => {
  // Set tablet viewport
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.goto('/osces/1');

  // Should show 2-column grid
  const videoCards = page.locator('[class*="video-card"]');
  const firstCard = videoCards.first();
  const secondCard = videoCards.nth(1);

  const firstBox = await firstCard.boundingBox();
  const secondBox = await secondCard.boundingBox();

  // Second card should be beside first (same row)
  const rowTolerance = 50; // pixels
  expect(Math.abs(secondBox!.y - firstBox!.y)).toBeLessThan(rowTolerance);
});
```

### Test 5: Accessibility

```typescript
test('should be keyboard navigable', async ({ page }) => {
  await page.goto('/osces/1');

  // Tab through interactive elements
  await page.keyboard.press('Tab'); // Why recommended button
  await page.keyboard.press('Tab'); // Watch Video link
  await page.keyboard.press('Tab'); // Next video's Why recommended

  // Check focus is visible
  const focusedElement = await page.locator(':focus');
  await expect(focusedElement).toBeVisible();
});

test('should have proper ARIA labels', async ({ page }) => {
  await page.goto('/osces/1');

  // Collapsible button should have aria-expanded
  const collapseButton = page.locator('button:has-text("Why recommended?")').first();
  await expect(collapseButton).toHaveAttribute('aria-expanded');

  // Links should have proper role
  const watchLink = page.locator('a:has-text("Watch Video")').first();
  await expect(watchLink).toHaveAttribute('target', '_blank');
  await expect(watchLink).toHaveAttribute('rel', /noopener/);
});

test('should meet color contrast requirements', async ({ page }) => {
  await page.goto('/osces/1');

  // This test would use axe-core or similar
  // Example assertion:
  const videoTitle = page.locator('[class*="video-card"] h4').first();
  const titleColor = await videoTitle.evaluate(el =>
    window.getComputedStyle(el).color
  );
  const bgColor = await videoTitle.evaluate(el =>
    window.getComputedStyle(el).backgroundColor
  );

  // Verify contrast ratio >= 4.5:1 (WCAG AA)
  // (Would use contrast-ratio library)
});
```

---

## 🎥 Playwright Video Recording Setup

### playwright.config.ts Configuration

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }]
  ],

  // Video recording settings
  use: {
    baseURL: 'http://localhost:5174',
    trace: 'on-first-retry',
    video: 'on',  // Record video for all tests
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Record in 1080p for better quality
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'mobile',
      use: {
        ...devices['iPhone 12 Pro'],
      },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5174',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Running Tests with Video

```bash
# 1. Install Playwright
npm install --save-dev @playwright/test
npx playwright install chromium

# 2. Create test file
# frontend/tests/e2e/osce-videos.spec.ts
# (Copy tests from above)

# 3. Run tests with video recording
npx playwright test --project=chromium

# Videos saved to: test-results/
# Format: test-name-chromium/video.webm

# 4. View test report
npx playwright show-report

# 5. Extract specific video
# Videos are in test-results/<test-name>/video.webm
```

---

## 📹 Manual Video Recording Script

For creating demonstration videos:

```bash
#!/bin/bash
# record-osce-demo.sh

echo "🎬 Starting OSCE Video Integration Demo Recording"

# 1. Start recording (using OBS Studio or SimpleScreenRecorder)
echo "📹 Start your screen recorder now"
echo "Press ENTER when recording started..."
read

# 2. Open browser
google-chrome --new-window "http://localhost:5174/osces" &
sleep 3

# 3. Demo script
cat << 'EOF'

DEMO SCRIPT:
============

1. Navigate to OSCE List
   - Show list of OSCEs
   - Highlight "Cardiovascular Physical Examination"

2. Click on Cardiovascular OSCE
   - Wait for page to load

3. Scroll to Video Section
   - Point out "📺 Video Demonstrations" heading
   - Show "Essential - Watch These First" badge

4. Demonstrate Video Card
   - Hover over first video card
   - Point out:
     * Video title
     * Source (Stanford Medicine 25)
     * Duration (10 min)
     * Focus description

5. Click "Why recommended?"
   - Show expanded section
   - Point out:
     * Why recommended text
     * Australian AMC relevance section

6. Click "Watch Video" button
   - New tab opens
   - Show Stanford Medicine 25 page loading

7. Return to OSCE page
   - Demonstrate second video card
   - Show different source (Geeky Medics)

8. Toggle "Supplementary Videos"
   - Click to expand
   - Show supplementary section

9. Mobile Responsive Demo
   - Resize browser to mobile width
   - Show single-column layout
   - Demonstrate touch interactions

10. Accessibility Demo
    - Tab through elements
    - Show keyboard navigation
    - Activate "Why recommended?" with Enter key

EOF

echo ""
echo "Press ENTER when demo complete..."
read

echo "✅ Demo recording complete!"
echo "📁 Save video as: osce-video-integration-demo.mp4"
```

---

## 📊 Test Data Verification

### Verify Database Populated

```bash
# Connect to database
docker exec -it irstudy-postgres psql -U postgres -d irstudy_medical

# Check video resources
SELECT
  osce_id,
  station_title,
  video_resources IS NOT NULL as has_videos,
  jsonb_array_length(video_resources->'essential_videos') as essential_count,
  jsonb_array_length(video_resources->'supplementary_videos') as supplementary_count
FROM osces
WHERE station_type = 'physical_examination'
ORDER BY osce_id;

# Expected output:
# osce_id      | station_title        | has_videos | essential | supplementary
# -------------+----------------------+------------+-----------+--------------
# OSCE-MED-001 | Cardiovascular Exam  | t          | 4         | 0
# OSCE-MED-002 | Abdominal Exam       | t          | 3         | 0
# ... (more rows)

# View specific video data
SELECT
  station_title,
  video_resources->'essential_videos'->0->>'title' as first_video_title,
  video_resources->'essential_videos'->0->>'url' as first_video_url
FROM osces
WHERE osce_id = 'OSCE-MED-001';
```

### Verify API Response

```bash
# Test backend API
curl http://localhost:8000/api/v1/osces/1 | jq '.video_resources'

# Expected: JSON object with essential_videos and supplementary_videos arrays

# Example output:
{
  "essential_videos": [
    {
      "title": "Cardiovascular Examination - Stanford Medicine 25",
      "url": "https://stanfordmedicine25.stanford.edu/the25/cardiovascular.html",
      "source": "Stanford Medicine 25",
      "duration_minutes": 10,
      "focus": "Complete systematic cardiac examination...",
      "why_recommended": "Gold standard demonstration...",
      "australian_relevance": "Technique fully compatible..."
    }
  ],
  "supplementary_videos": []
}
```

---

## 🎯 Test Coverage Matrix

| Test Category | Test Cases | Status |
|---------------|------------|--------|
| **Rendering** | Component displays | ⏳ Pending |
| | Video cards render | ⏳ Pending |
| | Essential vs supplementary | ⏳ Pending |
| **Interaction** | Expand/collapse sections | ⏳ Pending |
| | External links open | ⏳ Pending |
| | Click "Watch Video" | ⏳ Pending |
| **Responsive** | Mobile layout | ⏳ Pending |
| | Tablet layout | ⏳ Pending |
| | Desktop layout | ⏳ Pending |
| **Accessibility** | Keyboard navigation | ⏳ Pending |
| | ARIA labels | ⏳ Pending |
| | Color contrast | ⏳ Pending |
| | Screen reader | ⏳ Pending |
| **Data** | Database populated | ⏳ Pending |
| | API returns videos | ⏳ Pending |
| | Valid URLs (HTTPS) | ⏳ Pending |
| **Performance** | Page load < 2s | ⏳ Pending |
| | Video section renders < 500ms | ⏳ Pending |

---

## 📝 Test Results Template

### Test Execution Report

```markdown
# OSCE Video Integration - Test Results

**Date:** [DATE]
**Tester:** [NAME]
**Environment:** [Dev/Staging/Prod]
**Browser:** Chrome 120 / Firefox 122 / Safari 17

## Summary
- Tests Run: X
- Passed: X
- Failed: X
- Skipped: X

## Detailed Results

### Test 1: Video Component Renders
- Status: ✅ PASS / ❌ FAIL
- Duration: Xms
- Notes: [Any observations]
- Screenshot: [path/to/screenshot.png]
- Video: [path/to/video.webm]

### Test 2: Interactive Elements
- Status: ✅ PASS / ❌ FAIL
- Duration: Xms
- Notes: [Any observations]

... (continue for all tests)

## Issues Found
1. [Issue description]
   - Severity: Critical/Major/Minor
   - Steps to reproduce
   - Expected vs Actual behavior

## Recommendations
- [Recommendation 1]
- [Recommendation 2]
```

---

## 🎬 Video Locations

After running Playwright tests:

```
test-results/
├── osce-videos-should-display-video-component-chromium/
│   └── video.webm
├── osce-videos-should-display-video-details-chromium/
│   └── video.webm
├── osce-videos-should-expand-why-recommended-chromium/
│   └── video.webm
└── ... (more test videos)
```

Convert to MP4 for sharing:

```bash
# Install ffmpeg if needed
sudo apt install ffmpeg

# Convert all videos
for video in test-results/*/video.webm; do
  output="${video%.webm}.mp4"
  ffmpeg -i "$video" -c:v libx264 -crf 23 -preset medium "$output"
done

# Create demo reel
ffmpeg -f concat -i <(for f in test-results/*/video.mp4; do echo "file '$f'"; done) \
  -c copy osce-video-integration-full-demo.mp4
```

---

## ✅ Sign-Off Checklist

- [ ] Database migration completed successfully
- [ ] Video data populated (7 OSCEs)
- [ ] Backend API returns video_resources
- [ ] Frontend component renders correctly
- [ ] All external links work (HTTPS verified)
- [ ] Responsive design works (mobile/tablet/desktop)
- [ ] Accessibility tests pass (keyboard, ARIA, contrast)
- [ ] Performance benchmarks met (<2s page load)
- [ ] Playwright tests recorded with video
- [ ] Test results documented
- [ ] Demo video created
- [ ] Ready for production deployment

---

**Testing Lead:** [Your Name]
**Date Completed:** [DATE]
**Status:** ⏳ In Progress / ✅ Complete
