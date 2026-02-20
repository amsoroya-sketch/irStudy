# Manual Accessibility Testing Guide

**Version**: 1.0
**Date**: 2026-02-16
**Platform**: AMC Clinical Exam EMR Practice System
**Target**: WCAG 2.2 AA compliance (AAA for dark theme)

---

## Table of Contents

1. [Screen Reader Testing (NVDA/JAWS)](#screen-reader-testing-nvdajaws)
2. [Keyboard Navigation Testing](#keyboard-navigation-testing)
3. [Color Contrast Testing](#color-contrast-testing)
4. [Visual Testing (Zoom & Font Size)](#visual-testing-zoom--font-size)
5. [Mobile Touch Testing](#mobile-touch-testing)
6. [Australian Medical Context Testing](#australian-medical-context-testing)

---

## Screen Reader Testing (NVDA/JAWS)

### Setup

#### NVDA (Free, Recommended for Testing)
1. Download: https://www.nvaccess.org/download/
2. Install NVDA
3. Start NVDA: Press `Insert + N`
4. Configure speech rate: `Insert + Control + V` (slower for testing)
5. Browse mode: `Insert + Space` (toggle between browse and focus mode)

#### JAWS (Licensed, Industry Standard)
1. Download: https://www.freedomscientific.com/products/software/jaws/
2. Install JAWS (free 40-minute demo mode available)
3. Start JAWS: Desktop icon or `Ctrl + Alt + J`
4. Configure speech rate: `Insert + V` (voice settings)

### Screen Reader Keyboard Commands

| Command | NVDA | JAWS | Action |
|---------|------|------|--------|
| Read current line | `Insert + Up Arrow` | `Insert + Up Arrow` | Announce current line |
| Read from cursor | `Insert + Down Arrow` | `Insert + Down Arrow` | Read from cursor to end |
| Next heading | `H` | `H` | Jump to next heading |
| Next form field | `F` | `F` | Jump to next form field |
| Next button | `B` | `B` | Jump to next button |
| Next link | `K` | `K` | Jump to next link |
| Toggle browse mode | `Insert + Space` | `Num Pad Plus` | Switch modes |

---

## Test Scenarios

### Test 1: Epic SOAP Editor Navigation

**Objective**: Verify Epic EMR interface is fully navigable with screen reader

**Steps**:

1. **Start NVDA**:
   - Press `Insert + N`
   - Verify NVDA announces: "NVDA started"

2. **Navigate to Epic EMR**:
   - Open browser: http://localhost:5173/emr/practice?system=epic
   - Wait for page load
   - Verify NVDA announces: "AMC Clinical Exam - EMR Practice System"

3. **Test Patient Banner**:
   - Press `H` (next heading)
   - Verify NVDA announces: "Patient: John Smith, age 65, male, heading level 2"
   - Press `Down Arrow`
   - Verify NVDA announces: "MRN: 12345678"
   - Press `Down Arrow`
   - Verify NVDA announces: "DOB: 15 March 1979"

4. **Test Allergy Alert** (if present):
   - Press `H` (next heading)
   - Verify NVDA announces: "Allergies, heading level 3, alert"
   - Press `Down Arrow`
   - Verify NVDA announces: "Penicillin - Anaphylaxis, severe"

5. **Test SOAP Note Form**:
   - Press `F` (next form field)
   - Verify NVDA announces: "Subjective section, edit text, blank"
   - Type: "Patient reports chest pain"
   - Verify NVDA announces each character typed
   - Press `Tab`
   - Verify NVDA announces: "Character count: 25 of 10,000"

6. **Test Objective Section**:
   - Press `F` (next form field)
   - Verify NVDA announces: "Objective findings section, edit text, blank"
   - Type: "BP 140/90, HR 88"
   - Press `Tab`
   - Verify NVDA announces: "Character count: 16 of 10,000"

7. **Test Auto-save Status**:
   - Wait 30 seconds (auto-save timer)
   - Verify NVDA announces: "Auto-save: Saved at 2:34 PM, status"
   - Note: aria-live="polite" should announce without interrupting

8. **Test Submit Button**:
   - Press `B` (next button)
   - Verify NVDA announces: "Submit Session button"
   - Press `Enter`
   - Verify NVDA announces: "Validating SOAP note, please wait, status"

9. **Test Validation Results**:
   - Wait 5 seconds for validation
   - Verify NVDA announces: "Validation complete, alert"
   - Press `H` (next heading)
   - Verify NVDA announces: "Validation Results, heading level 2"
   - Press `Down Arrow`
   - Verify NVDA announces: "Score: 12 out of 15, pass"

**Pass Criteria**:
- [ ] All headings announced with correct level
- [ ] All form fields have descriptive labels
- [ ] Character counters announced
- [ ] Auto-save status announced without interruption
- [ ] Validation results announced clearly
- [ ] No "unlabeled" or "blank" announcements

---

### Test 2: Cerner PowerChart Navigation (Dark Theme)

**Objective**: Verify Cerner dark theme is accessible with screen reader

**Steps**:

1. **Navigate to Cerner EMR**:
   - Open: http://localhost:5173/emr/practice?system=cerner
   - Verify NVDA announces: "Cerner PowerChart - AMC Clinical Exam"

2. **Test Sidebar Navigation**:
   - Press `R` (next region)
   - Verify NVDA announces: "Navigation, region"
   - Press `K` (next link)
   - Verify NVDA announces: "Patient Chart, link"

3. **Test Dark Theme Form Fields**:
   - Press `F` (next form field)
   - Verify NVDA announces: "Subjective section, edit text, blank"
   - Type: "Patient reports fever"
   - Verify text announced clearly (dark theme doesn't affect speech)

4. **Test Validation Badges** (Dark Theme):
   - Submit SOAP note
   - Navigate to validation results
   - Verify NVDA announces: "Pass, badge" or "Fail, badge"
   - Verify badge type (pass/fail) is announced

**Pass Criteria**:
- [ ] Dark theme doesn't interfere with screen reader
- [ ] Sidebar navigation announced correctly
- [ ] Form fields have descriptive labels
- [ ] Validation badges announced with status

---

### Test 3: Keyboard Shortcuts and Navigation

**Objective**: Verify keyboard shortcuts work as documented

**Steps**:

1. **Epic SOAP Editor - Tab Order**:
   - Navigate to Epic EMR
   - Press `Tab` repeatedly
   - Verify focus order:
     1. Subjective tab
     2. Objective tab
     3. Assessment tab
     4. Plan tab
     5. Subjective textarea
     6. Objective textarea
     7. Assessment textarea
     8. Plan textarea
     9. Submit button
     10. Cancel button

2. **Epic SOAP Editor - Keyboard Shortcuts**:
   - Fill Subjective field
   - Press `Ctrl + S` (manual save)
   - Verify: "Saved at [time]" status appears
   - Press `Ctrl + Enter` (submit)
   - Verify: Submit confirmation dialog appears
   - Press `Escape`
   - Verify: Dialog closes

3. **Cerner Sidebar - Arrow Key Navigation**:
   - Navigate to Cerner EMR
   - Focus sidebar (click or Tab)
   - Press `ArrowDown`
   - Verify: Focus moves to next sidebar item
   - Press `ArrowUp`
   - Verify: Focus moves to previous sidebar item

4. **Skip to Main Content Link**:
   - Navigate to Epic EMR
   - Press `Tab` (first element)
   - Verify: "Skip to main content" link focused
   - Press `Enter`
   - Verify: Focus jumps to SOAP editor

**Pass Criteria**:
- [ ] Tab order is logical (top to bottom, left to right)
- [ ] Ctrl+S triggers save
- [ ] Ctrl+Enter triggers submit
- [ ] Escape closes dialogs
- [ ] Arrow keys navigate sidebar
- [ ] Skip link works

---

## Color Contrast Testing

### Tools Required

1. **Chrome DevTools Color Picker**:
   - Right-click element → Inspect
   - In Styles panel, click color swatch
   - Contrast ratio shown at bottom

2. **WebAIM Contrast Checker** (Online):
   - URL: https://webaim.org/resources/contrastchecker/
   - Enter foreground and background colors
   - Verify meets WCAG AA (4.5:1) or AAA (7:1)

3. **Accessible Colors (Browser Extension)**:
   - Chrome: https://chrome.google.com/webstore/detail/accessible-colors/...
   - Highlights contrast violations on page

### Test Scenarios

#### Test 1: Epic Light Theme - Text Contrast

**Objective**: Verify Epic text has ≥4.5:1 contrast ratio (WCAG AA)

**Steps**:

1. Navigate to Epic EMR
2. Right-click Subjective tab → Inspect
3. In Styles panel, find `color` property
4. Click color swatch (e.g., `#2C2C2C`)
5. View contrast ratio at bottom of color picker
6. Verify: Contrast ratio ≥ 4.5:1 ✓

**Expected**:
- Epic text: `#2C2C2C` (dark gray)
- Epic background: `#FAFAF8` (off-white)
- Contrast ratio: ~12.5:1 ✓ (exceeds WCAG AA)

#### Test 2: Epic Primary Button - Contrast

**Objective**: Verify Epic purple button has sufficient contrast

**Steps**:

1. Inspect Submit button
2. Check `color` (white text) vs `background-color` (purple)
3. Verify contrast ratio ≥ 4.5:1

**Expected**:
- Button text: `#FFFFFF` (white)
- Button background: `#8b5cf6` (purple)
- Contrast ratio: ~4.8:1 ✓ (meets WCAG AA)

#### Test 3: Cerner Dark Theme - AAA Contrast

**Objective**: Verify Cerner dark theme has ≥7:1 contrast (WCAG AAA)

**Steps**:

1. Navigate to Cerner EMR
2. Inspect Subjective field
3. Check text color vs background color
4. Verify contrast ratio ≥ 7:1

**Expected**:
- Text: `#FFFFFF` (white)
- Background: `#2D2D2D` (dark gray)
- Contrast ratio: ~14.7:1 ✓ (exceeds WCAG AAA)

#### Test 4: Allergy Alert - Contrast

**Objective**: Verify allergy warnings are visible

**Steps**:

1. Navigate to Epic EMR with patient having allergies
2. Inspect allergy alert banner
3. Check text color vs background color

**Expected**:
- Severe allergy text: `#991b1b` (dark red)
- Severe allergy background: `#fee2e2` (light red)
- Contrast ratio: ≥4.5:1 ✓

**Pass Criteria**:
- [ ] Epic text: ≥4.5:1 (WCAG AA)
- [ ] Epic buttons: ≥4.5:1 (WCAG AA)
- [ ] Cerner dark theme: ≥7:1 (WCAG AAA)
- [ ] Allergy alerts: ≥4.5:1 (WCAG AA)

---

## Visual Testing (Zoom & Font Size)

### Test 1: 200% Browser Zoom

**Objective**: Verify interface usable at 200% zoom (WCAG 1.4.4)

**Steps**:

1. Navigate to Epic EMR
2. Press `Ctrl + Plus` twice (200% zoom)
3. Verify:
   - [ ] No horizontal scrolling required
   - [ ] All text readable
   - [ ] All buttons clickable
   - [ ] SOAP editor fields visible
   - [ ] Submit button accessible

4. Navigate to Cerner EMR at 200% zoom
5. Verify same criteria

**Pass Criteria**:
- [ ] No horizontal scroll at 200% zoom
- [ ] All interactive elements remain functional
- [ ] Text doesn't overflow containers

### Test 2: 400% Browser Zoom (WCAG 1.4.10)

**Objective**: Verify reflow at 400% zoom

**Steps**:

1. Navigate to Epic EMR
2. Press `Ctrl + Plus` four times (400% zoom)
3. Verify:
   - [ ] Content reflows (no 2D scrolling)
   - [ ] Critical elements still accessible
   - [ ] Can complete SOAP note workflow

**Pass Criteria**:
- [ ] Content reflows without breaking layout
- [ ] Main workflow still functional

### Test 3: Large Font Size (Browser Settings)

**Objective**: Verify interface adapts to user font size preferences

**Steps**:

1. Open browser settings
2. Set font size to "Very Large" (24px)
3. Navigate to Epic EMR
4. Verify:
   - [ ] Text readable
   - [ ] No text overflow
   - [ ] Buttons remain clickable

**Pass Criteria**:
- [ ] Layout adapts to larger font sizes
- [ ] No text cutoff

---

## Mobile Touch Testing

### Test 1: iPad Viewport (768x1024)

**Objective**: Verify touch targets ≥44x44px (WCAG 2.5.5 AAA)

**Steps**:

1. Open browser DevTools (F12)
2. Enable device emulation (Ctrl+Shift+M)
3. Select "iPad" preset
4. Navigate to Epic EMR
5. Inspect Submit button size:
   - Right-click → Inspect
   - Check computed height/width
   - Verify: ≥44px tall and ≥44px wide ✓

6. Test tabs (Subjective, Objective, etc.):
   - Verify: ≥44px tall ✓

**Pass Criteria**:
- [ ] All buttons ≥44x44px
- [ ] All tabs ≥44px tall
- [ ] All links ≥44px tall
- [ ] Form fields have adequate touch targets

### Test 2: Mobile Phone (375x667)

**Objective**: Verify mobile responsiveness

**Steps**:

1. Set DevTools to "iPhone SE" preset
2. Navigate to Epic EMR
3. Verify:
   - [ ] SOAP editor usable (may stack vertically)
   - [ ] Buttons accessible
   - [ ] Text readable without zooming

**Pass Criteria**:
- [ ] Interface functional on mobile
- [ ] Critical workflows accessible

---

## Australian Medical Context Testing

### Test 1: Terminology Validation - Screen Reader Announcements

**Objective**: Verify Australian terminology warnings are accessible

**Steps**:

1. Start NVDA
2. Navigate to Epic EMR
3. Fill Subjective field: "Patient took acetaminophen for pain"
4. Press Submit
5. Wait for validation
6. Verify NVDA announces:
   - "Terminology warning, alert"
   - "Use Australian terminology: 'paracetamol' instead of 'acetaminophen'"

**Pass Criteria**:
- [ ] Warnings announced via aria-live
- [ ] Warning severity clear (error vs warning)
- [ ] Suggested Australian term announced

### Test 2: PBS Medication Search - Keyboard Accessibility

**Objective**: Verify PBS search is keyboard accessible

**Steps**:

1. Navigate to Epic Medications panel
2. Tab to PBS search field
3. Type: "paracetamol"
4. Press `ArrowDown` to navigate results
5. Press `Enter` to select medication
6. Verify medication form appears
7. Tab through form fields (strength, route, frequency)

**Pass Criteria**:
- [ ] Search field keyboard accessible
- [ ] Results navigable with arrow keys
- [ ] Enter key selects medication
- [ ] All form fields tab-accessible

---

## Accessibility Testing Checklist

### Epic EMR Interface

- [ ] WCAG 2.2 AA automated scan passes (0 violations)
- [ ] Keyboard navigation works (Tab, Enter, Arrow keys)
- [ ] Screen reader announces all elements correctly
- [ ] Color contrast ≥4.5:1 (WCAG AA)
- [ ] Focus indicators visible
- [ ] Form validation errors announced
- [ ] Auto-save status announced
- [ ] 200% zoom works without horizontal scroll
- [ ] Touch targets ≥44x44px

### Cerner EMR Interface (Dark Theme)

- [ ] WCAG 2.2 AAA automated scan passes (0 violations)
- [ ] Dark theme color contrast ≥7:1 (WCAG AAA)
- [ ] Focus indicators visible on dark background
- [ ] Keyboard navigation works in dark theme
- [ ] Screen reader announces dark theme elements correctly
- [ ] Error messages visible in dark theme
- [ ] 200% zoom works without horizontal scroll

### Australian Medical Compliance

- [ ] Terminology warnings accessible
- [ ] PBS medication search keyboard accessible
- [ ] MBS pathology codes accessible
- [ ] Medicare number format announced
- [ ] Allergy alerts announced by screen reader

---

## Automated Testing Integration

### Run Automated A11y Tests

```bash
# Navigate to Playwright tests directory
cd /home/dev/Development/irStudy/testing/playwright

# Run Epic accessibility tests
npm run test:a11y -- tests/accessibility/a11y-epic-ui.spec.ts

# Run Cerner accessibility tests
npm run test:a11y -- tests/accessibility/a11y-cerner-ui.spec.ts

# Run all accessibility tests
npm run test:a11y
```

### Expected Results

```
Epic EMR UI - Accessibility
  ✓ Epic SOAP Editor - WCAG 2.2 AA compliance (3.2s)
  ✓ Epic Patient Banner - keyboard navigation (1.8s)
  ✓ Epic SOAP Editor - screen reader labels (2.1s)
  ✓ Epic color contrast - WCAG AA (1.4s)
  ✓ Epic form validation errors - accessible announcements (2.3s)
  
Cerner EMR UI - Accessibility (Dark Mode)
  ✓ Cerner SOAP Editor - WCAG AAA dark mode contrast (3.5s)
  ✓ Cerner dark theme - focus indicators visible (1.7s)
  
Total: 7 tests passed (0 failures)
```

---

## Reporting Accessibility Issues

### Issue Template

```markdown
**Issue**: [Brief description]
**Severity**: Critical | High | Medium | Low
**WCAG Criterion**: [e.g., 1.4.3 Contrast (Minimum)]
**Component**: [e.g., Epic Submit Button]

**Steps to Reproduce**:
1. Navigate to...
2. Use screen reader...
3. Observe...

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Screenshot**:
[Attach screenshot]

**Suggested Fix**:
[How to fix it]
```

### Example Issue

```markdown
**Issue**: Epic Submit button not announced by NVDA
**Severity**: High
**WCAG Criterion**: 4.1.2 Name, Role, Value
**Component**: Epic Submit Button

**Steps to Reproduce**:
1. Navigate to Epic EMR
2. Start NVDA
3. Tab to Submit button
4. Observe: NVDA announces "button" but not "Submit Session"

**Expected Behavior**:
NVDA should announce: "Submit Session button"

**Actual Behavior**:
NVDA announces: "button"

**Suggested Fix**:
Add aria-label="Submit Session" to button element

**Code Fix**:
```tsx
<button
  type="submit"
  aria-label="Submit Session"
  data-testid="submit-session"
>
  Submit
</button>
```
```

---

**Version**: 1.0
**Last Updated**: 2026-02-16
**Maintained By**: QA Team
**Contact**: qa@amcclinicalexam.com.au
