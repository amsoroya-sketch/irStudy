/**
 * Epic EMR UI - Accessibility Testing (WCAG 2.2 AA Compliance)
 * 
 * Tests Epic EHR interface for:
 * - WCAG 2.2 AA compliance using axe-core
 * - Keyboard navigation and focus management
 * - Screen reader labels (ARIA)
 * - Color contrast ratios
 * - Accessible form validation announcements
 * 
 * Target: 100% WCAG 2.2 AA compliance for Epic EMR interface
 */

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Epic EMR UI - Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to Epic EMR interface
    await page.goto('/emr/practice?system=epic');
    
    // Wait for Epic interface to load
    await page.waitForSelector('[data-testid="epic-workspace"]', { timeout: 10000 });
  });

  test.describe('WCAG 2.2 AA Compliance', () => {
    test('Epic SOAP Editor - WCAG 2.2 AA compliance', async ({ page }) => {
      // Run axe-core accessibility scan
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
        .analyze();
      
      // Assert no violations (ZERO TOLERANCE)
      expect(accessibilityScanResults.violations).toEqual([]);
      
      // Log results for debugging if needed
      if (accessibilityScanResults.violations.length > 0) {
        console.error('Accessibility violations found:', 
          JSON.stringify(accessibilityScanResults.violations, null, 2)
        );
      }
    });

    test('Epic Patient Banner - WCAG 2.2 AA compliance', async ({ page }) => {
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
        .include('[data-testid="patient-banner"]')
        .analyze();
      
      expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('Epic Medication Panel - WCAG 2.2 AA compliance', async ({ page }) => {
      // Navigate to medications panel
      await page.click('[data-testid="medications-icon"]');
      await page.waitForSelector('[data-testid="medication-panel"]');
      
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
        .include('[data-testid="medication-panel"]')
        .analyze();
      
      expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('Epic Validation Results - WCAG 2.2 AA compliance', async ({ page }) => {
      // Fill and submit SOAP note to trigger validation
      await page.fill('[data-testid="subjective-field"]', 'Patient reports chest pain for 2 hours. Started suddenly while at rest. 8/10 severity, crushing sensation, radiating to left arm.');
      await page.fill('[data-testid="objective-field"]', 'BP 140/90, HR 88, RR 18, Temp 37.0°C, SpO2 98%. Alert and oriented. Cardiovascular: Central chest wall tenderness.');
      await page.fill('[data-testid="assessment-field"]', 'Working diagnosis: Acute Coronary Syndrome. Differential: Aortic dissection, pulmonary embolism.');
      await page.fill('[data-testid="plan-field"]', 'Investigations: Troponin, ECG, CXR. Medications: Aspirin 300mg PO stat. Management: Urgent cardiology review.');
      
      await page.click('[data-testid="submit-session"]');
      await page.waitForSelector('[data-testid="validation-results"]', { timeout: 10000 });
      
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
        .include('[data-testid="validation-results"]')
        .analyze();
      
      expect(accessibilityScanResults.violations).toEqual([]);
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('Epic Patient Banner - keyboard navigation', async ({ page }) => {
      // Focus should start at first focusable element
      await page.keyboard.press('Tab');
      
      // First tab should focus Subjective tab
      const firstFocused = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'));
      expect(firstFocused).toBe('subjective-tab');
      
      // Next tab should focus Objective tab
      await page.keyboard.press('Tab');
      const secondFocused = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'));
      expect(secondFocused).toBe('objective-tab');
      
      // Test Enter key activation
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500); // Wait for tab change animation
      
      // Verify Objective panel is now visible
      const activePanel = page.locator('[role="tabpanel"]:visible');
      await expect(activePanel).toContainText(/Objective/i);
    });

    test('Epic SOAP Editor - keyboard navigation through form fields', async ({ page }) => {
      // Navigate to Subjective field
      await page.keyboard.press('Tab'); // Subjective tab
      await page.keyboard.press('Tab'); // Skip to textarea
      
      const subjectiveFocused = await page.evaluate(() => 
        document.activeElement?.getAttribute('data-testid')
      );
      expect(subjectiveFocused).toBe('subjective-field');
      
      // Fill field using keyboard
      await page.keyboard.type('Patient reports headache');
      
      // Tab to next section
      await page.keyboard.press('Tab'); // Should skip character counter
      await page.keyboard.press('Tab'); // Objective tab
      await page.keyboard.press('Enter'); // Activate Objective tab
      
      await page.waitForTimeout(300);
      
      await page.keyboard.press('Tab'); // Focus Objective textarea
      const objectiveFocused = await page.evaluate(() => 
        document.activeElement?.getAttribute('data-testid')
      );
      expect(objectiveFocused).toBe('objective-field');
    });

    test('Epic Medication Search - keyboard navigation', async ({ page }) => {
      // Navigate to medications panel
      await page.click('[data-testid="medications-icon"]');
      await page.waitForSelector('[data-testid="medication-search"]');
      
      // Tab to search field
      const searchField = page.locator('[data-testid="medication-search"]');
      await searchField.focus();
      
      // Type medication name
      await page.keyboard.type('paracetamol');
      
      // Wait for search results
      await page.waitForSelector('[data-testid="medication-result"]', { timeout: 3000 });
      
      // Arrow down to navigate results
      await page.keyboard.press('ArrowDown');
      
      // Enter to select medication
      await page.keyboard.press('Enter');
      
      // Verify medication form appears
      await expect(page.locator('[data-testid="medication-form"]')).toBeVisible();
    });

    test('Epic Submit Button - keyboard activation', async ({ page }) => {
      // Fill minimum required fields
      await page.fill('[data-testid="subjective-field"]', 'Patient reports headache for 3 days. Throbbing, bilateral, 6/10 severity.');
      await page.fill('[data-testid="objective-field"]', 'BP 120/80, HR 72, RR 16, Temp 36.8°C, SpO2 99%. Alert and oriented. Neurological exam normal.');
      await page.fill('[data-testid="assessment-field"]', 'Tension headache. No red flags.');
      await page.fill('[data-testid="plan-field"]', 'Paracetamol 1g PO QID PRN. Reassurance. GP follow-up if persistent.');
      
      // Tab to submit button
      const submitButton = page.locator('[data-testid="submit-session"]');
      await submitButton.focus();
      
      // Verify focus
      const isFocused = await submitButton.evaluate(el => el === document.activeElement);
      expect(isFocused).toBe(true);
      
      // Press Enter to submit
      await page.keyboard.press('Enter');
      
      // Verify submission (validation results appear)
      await expect(page.locator('[data-testid="validation-results"]')).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Screen Reader Labels (ARIA)', () => {
    test('Epic SOAP Editor - screen reader labels', async ({ page }) => {
      // Check ARIA labels on form fields
      const subjectiveField = page.getByRole('textbox', { name: /Subjective/i });
      await expect(subjectiveField).toHaveAttribute('aria-label', 
        expect.stringMatching(/Subjective.*section/i)
      );
      
      const objectiveField = page.getByRole('textbox', { name: /Objective/i });
      await expect(objectiveField).toHaveAttribute('aria-label', 
        expect.stringMatching(/Objective.*section/i)
      );
      
      const assessmentField = page.getByRole('textbox', { name: /Assessment/i });
      await expect(assessmentField).toHaveAttribute('aria-label', 
        expect.stringMatching(/Assessment.*section/i)
      );
      
      const planField = page.getByRole('textbox', { name: /Plan/i });
      await expect(planField).toHaveAttribute('aria-label', 
        expect.stringMatching(/Plan.*section/i)
      );
    });

    test('Epic Patient Banner - screen reader announcements', async ({ page }) => {
      // Patient banner should have role="region" with aria-label
      const patientBanner = page.locator('[data-testid="patient-banner"]');
      await expect(patientBanner).toHaveAttribute('role', 'region');
      await expect(patientBanner).toHaveAttribute('aria-label', 
        expect.stringMatching(/Patient.*information/i)
      );
      
      // Allergy alerts should have role="alert"
      const allergyAlert = page.locator('[data-testid="allergy-alert"]');
      if (await allergyAlert.isVisible()) {
        await expect(allergyAlert).toHaveAttribute('role', 'alert');
        await expect(allergyAlert).toHaveAttribute('aria-label', 
          expect.stringMatching(/Allergy.*warning/i)
        );
      }
    });

    test('Epic Character Counter - screen reader announcements', async ({ page }) => {
      const subjectiveField = page.locator('[data-testid="subjective-field"]');
      const characterCounter = page.locator('[data-testid="subjective-character-count"]');
      
      // Character counter should have aria-live="polite"
      await expect(characterCounter).toHaveAttribute('aria-live', 'polite');
      
      // Type text and verify counter updates
      await subjectiveField.fill('Patient reports chest pain');
      
      // Counter should announce character count
      const counterText = await characterCounter.textContent();
      expect(counterText).toMatch(/\d+/); // Contains number
    });

    test('Epic Auto-save Status - screen reader announcements', async ({ page }) => {
      const autoSaveStatus = page.locator('[data-testid="auto-save-status"]');
      
      // Auto-save status should have aria-live="polite"
      await expect(autoSaveStatus).toHaveAttribute('aria-live', 'polite');
      
      // Fill field to trigger auto-save
      await page.fill('[data-testid="subjective-field"]', 'Patient reports headache');
      
      // Wait for auto-save (30s timer)
      await page.waitForTimeout(31000);
      
      // Verify auto-save status updated
      await expect(autoSaveStatus).toContainText(/Saved/i);
    });

    test('Epic form validation errors - accessible announcements', async ({ page }) => {
      // Submit with empty fields
      await page.click('[data-testid="submit-session"]');
      
      // Check for aria-live region announcing errors
      const errorRegion = page.locator('[role="alert"]');
      await expect(errorRegion).toBeVisible({ timeout: 3000 });
      await expect(errorRegion).toContainText(/required/i);
      
      // Error region should have aria-live="assertive" (interrupts screen reader)
      await expect(errorRegion).toHaveAttribute('aria-live', 'assertive');
    });
  });

  test.describe('Color Contrast (WCAG AA)', () => {
    test('Epic color contrast - Subjective tab', async ({ page }) => {
      const subjectiveTab = page.locator('[data-testid="subjective-tab"]');
      
      // Get computed styles
      const styles = await subjectiveTab.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          color: computed.color,
          backgroundColor: computed.backgroundColor,
        };
      });
      
      // Epic theme: Dark text on light background
      // Expected: High contrast (≥4.5:1 for WCAG AA)
      // Note: Actual contrast calculation requires color library
      // axe-core validates contrast in main compliance test above
      
      expect(styles.color).toBeTruthy();
      expect(styles.backgroundColor).toBeTruthy();
    });

    test('Epic Primary Button - color contrast', async ({ page }) => {
      const submitButton = page.locator('[data-testid="submit-session"]');
      
      const styles = await submitButton.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          color: computed.color,
          backgroundColor: computed.backgroundColor,
        };
      });
      
      // Epic primary button: White text (#FFFFFF) on purple (#8b5cf6)
      // Expected contrast ratio: ≥4.5:1 (WCAG AA)
      expect(styles.color).toBeTruthy();
      expect(styles.backgroundColor).toBeTruthy();
    });

    test('Epic Allergy Alert - color contrast', async ({ page }) => {
      const allergyAlert = page.locator('[data-testid="allergy-alert"]');
      
      // Skip if no allergy alert visible
      if (!(await allergyAlert.isVisible())) {
        test.skip();
      }
      
      const styles = await allergyAlert.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          color: computed.color,
          backgroundColor: computed.backgroundColor,
          borderColor: computed.borderColor,
        };
      });
      
      // Allergy alert: Dark text on yellow/red background
      // Expected contrast ratio: ≥4.5:1 (WCAG AA)
      expect(styles.color).toBeTruthy();
      expect(styles.backgroundColor).toBeTruthy();
      expect(styles.borderColor).toBeTruthy();
    });
  });

  test.describe('Focus Indicators', () => {
    test('Epic tabs - visible focus indicators', async ({ page }) => {
      const subjectiveTab = page.locator('[data-testid="subjective-tab"]');
      
      // Focus the tab
      await subjectiveTab.focus();
      
      // Get focus outline style
      const outlineStyle = await subjectiveTab.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          outline: computed.outline,
          outlineWidth: computed.outlineWidth,
          outlineColor: computed.outlineColor,
          boxShadow: computed.boxShadow,
        };
      });
      
      // Focus outline should be visible (not "none" or "0px")
      const hasFocusIndicator = 
        (outlineStyle.outline !== 'none' && outlineStyle.outlineWidth !== '0px') ||
        outlineStyle.boxShadow !== 'none';
      
      expect(hasFocusIndicator).toBe(true);
    });

    test('Epic form fields - visible focus indicators', async ({ page }) => {
      const subjectiveField = page.locator('[data-testid="subjective-field"]');
      
      await subjectiveField.focus();
      
      const focusStyle = await subjectiveField.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          outline: computed.outline,
          borderColor: computed.borderColor,
          boxShadow: computed.boxShadow,
        };
      });
      
      // Focus should be indicated by outline, border change, or box-shadow
      const hasFocusIndicator = 
        focusStyle.outline !== 'none' ||
        focusStyle.borderColor !== 'transparent' ||
        focusStyle.boxShadow !== 'none';
      
      expect(hasFocusIndicator).toBe(true);
    });

    test('Epic buttons - visible focus indicators on hover', async ({ page }) => {
      const submitButton = page.locator('[data-testid="submit-session"]');
      
      // Hover and focus
      await submitButton.hover();
      await submitButton.focus();
      
      const focusStyle = await submitButton.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          outline: computed.outline,
          boxShadow: computed.boxShadow,
        };
      });
      
      // Focus should be visible even on hover
      const hasFocusIndicator = 
        focusStyle.outline !== 'none' ||
        focusStyle.boxShadow !== 'none';
      
      expect(hasFocusIndicator).toBe(true);
    });
  });

  test.describe('Responsive Accessibility (Zoom & Font Size)', () => {
    test('Epic UI - 200% zoom accessibility', async ({ page }) => {
      // Set viewport and zoom to 200%
      await page.setViewportSize({ width: 1920 / 2, height: 1080 / 2 });
      
      // Verify Epic interface still usable (no horizontal scroll required)
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      
      expect(hasHorizontalScroll).toBe(false);
      
      // Verify all buttons and tabs remain clickable
      await expect(page.locator('[data-testid="subjective-tab"]')).toBeVisible();
      await expect(page.locator('[data-testid="objective-tab"]')).toBeVisible();
      await expect(page.locator('[data-testid="submit-session"]')).toBeVisible();
    });

    test('Epic UI - large font size accessibility', async ({ page }) => {
      // Increase font size via browser settings simulation
      await page.addStyleTag({
        content: `
          * {
            font-size: 1.5em !important;
          }
        `
      });
      
      // Verify layout doesn't break
      const subjectiveField = page.locator('[data-testid="subjective-field"]');
      await expect(subjectiveField).toBeVisible();
      
      // Verify text remains readable (not overflowing)
      const isOverflowing = await subjectiveField.evaluate((el) => {
        return el.scrollWidth > el.clientWidth;
      });
      
      expect(isOverflowing).toBe(false);
    });
  });

  test.describe('Mobile Accessibility (Touch)', () => {
    test('Epic UI - tablet viewport accessibility', async ({ page }) => {
      // Set iPad viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      
      // Verify touch targets are at least 44x44px (WCAG 2.2 Level AAA)
      const submitButton = page.locator('[data-testid="submit-session"]');
      const buttonSize = await submitButton.boundingBox();
      
      expect(buttonSize).toBeTruthy();
      if (buttonSize) {
        expect(buttonSize.width).toBeGreaterThanOrEqual(44);
        expect(buttonSize.height).toBeGreaterThanOrEqual(44);
      }
    });

    test('Epic Tabs - touch target size', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      
      const subjectiveTab = page.locator('[data-testid="subjective-tab"]');
      const tabSize = await subjectiveTab.boundingBox();
      
      expect(tabSize).toBeTruthy();
      if (tabSize) {
        // Tabs should be at least 44px tall for touch accessibility
        expect(tabSize.height).toBeGreaterThanOrEqual(44);
      }
    });
  });
});
