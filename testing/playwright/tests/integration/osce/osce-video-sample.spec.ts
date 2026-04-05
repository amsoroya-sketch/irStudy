import { test, expect } from '@playwright/test';

/**
 * Sample OSCE Video Resources Test for Autonomous Testing
 *
 * This is a starter test that Claude will run autonomously to:
 * 1. Navigate to an OSCE page
 * 2. Verify video resources section appears
 * 3. Detect any bugs (missing elements, broken styling, etc.)
 * 4. Fix bugs automatically
 * 5. Re-run until all tests pass
 *
 * Run with MCP: Claude will monitor this test and fix any errors found
 */

test.describe('OSCE Video Resources - Autonomous Testing Sample', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to OSCE page (adjust URL based on your routing)
    await page.goto('/osces/OSCE-MED-CARDIO-001');

    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
  });

  test('should display OSCE page with basic information', async ({ page }) => {
    // Verify page loaded
    await expect(page).toHaveURL(/\/osces\//);

    // Verify OSCE title is visible
    const title = page.locator('h1');
    await expect(title).toBeVisible();

    // Verify OSCE has some content
    const content = page.locator('main');
    await expect(content).toBeVisible();
  });

  test('should display essential videos section if videos exist', async ({ page }) => {
    // Check if essential videos section exists
    const essentialVideosSection = page.locator('h2:has-text("Essential Video Demonstrations")');

    // This test will help Claude identify if the section is missing
    await expect(essentialVideosSection).toBeVisible({ timeout: 5000 });

    // Verify video items are displayed
    const videoItems = page.locator('[data-testid="video-item"]');
    const count = await videoItems.count();

    // Should have at least 1 essential video
    expect(count).toBeGreaterThan(0);
  });

  test('should display video metadata for each video', async ({ page }) => {
    // Get first video item
    const firstVideo = page.locator('[data-testid="video-item"]').first();
    await expect(firstVideo).toBeVisible();

    // Verify video has title
    const videoTitle = firstVideo.locator('[data-testid="video-title"]');
    await expect(videoTitle).toBeVisible();

    // Verify video has source
    const videoSource = firstVideo.locator('[data-testid="video-source"]');
    await expect(videoSource).toBeVisible();

    // Verify video has link
    const videoLink = firstVideo.locator('a[href^="https://"]');
    await expect(videoLink).toBeVisible();
  });

  test('should have supplementary videos section with expand/collapse', async ({ page }) => {
    // Check for supplementary videos section
    const supplementarySection = page.locator('h3:has-text("Supplementary Videos")');

    // Section should exist
    await expect(supplementarySection).toBeVisible();

    // Find expand/collapse button
    const expandButton = page.locator('button:has-text("Show More"), button[aria-label*="expand"]');
    await expect(expandButton).toBeVisible();

    // Click to expand
    await expandButton.click();

    // Verify supplementary videos become visible
    const supplementaryVideos = page.locator('[data-testid="supplementary-video"]');
    await expect(supplementaryVideos.first()).toBeVisible();
  });

  test('should have proper accessibility attributes', async ({ page }) => {
    // Check heading hierarchy
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();

    // Check video links have descriptive labels
    const videoLinks = page.locator('[data-testid="video-item"] a');
    const firstLink = videoLinks.first();

    // Link should have accessible name (aria-label or text content)
    const ariaLabel = await firstLink.getAttribute('aria-label');
    const textContent = await firstLink.textContent();

    expect(ariaLabel || textContent).toBeTruthy();

    // External links should have target="_blank" and rel="noopener noreferrer"
    const target = await firstLink.getAttribute('target');
    const rel = await firstLink.getAttribute('rel');

    expect(target).toBe('_blank');
    expect(rel).toContain('noopener');
  });

  test('should be responsive on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Verify content is still visible and not cut off
    const essentialSection = page.locator('h2:has-text("Essential Video Demonstrations")');
    await expect(essentialSection).toBeVisible();

    // Verify videos stack vertically (not in grid)
    const videoItems = page.locator('[data-testid="video-item"]');

    // Get positions of first two videos
    if (await videoItems.count() >= 2) {
      const first = videoItems.nth(0);
      const second = videoItems.nth(1);

      const firstBox = await first.boundingBox();
      const secondBox = await second.boundingBox();

      // On mobile, second video should be below first (not side-by-side)
      expect(secondBox!.y).toBeGreaterThan(firstBox!.y + firstBox!.height);
    }
  });

  test('should handle missing videos gracefully', async ({ page }) => {
    // Navigate to OSCE without videos (if one exists)
    // This is a negative test to ensure app doesn't crash

    // For now, just verify the page doesn't show video section if no videos
    const hasVideos = await page.locator('[data-testid="video-section"]').isVisible();

    if (!hasVideos) {
      // Should show some alternative content or message
      const mainContent = page.locator('main');
      await expect(mainContent).toBeVisible();

      // Should NOT show video section headers
      const essentialHeader = page.locator('h2:has-text("Essential Video Demonstrations")');
      await expect(essentialHeader).not.toBeVisible();
    }
  });
});
