# Testing Guide - Respiratory MCQ Web Application

## Quick Test (2 minutes)

To quickly verify the application works:

```bash
cd /home/dev/Development/irStudy/respiratory-mcq-app

# Option 1: Test development version
python3 -m http.server 8000 --directory src

# Option 2: Test production build
python3 -m http.server 8000 --directory build

# Open in browser: http://localhost:8000
```

**Expected Result**: You should see a header "Week 3: Respiratory Medicine MCQs" with the first MCQ loaded.

---

## Functional Testing Checklist

### 1. MCQ Loading ✓
- [ ] Page loads without errors
- [ ] First MCQ (Q1) displays correctly
- [ ] Question scenario shows in gray box
- [ ] Question stem appears below scenario
- [ ] 4-5 answer options are visible
- [ ] All text is readable (no truncation)

**How to test**:
1. Open the application
2. Verify the loading overlay disappears
3. Check that MCQ content is visible and formatted correctly

---

### 2. Answer Selection & Submission ✓
- [ ] Clicking an option highlights it (blue border)
- [ ] Only one option can be selected at a time
- [ ] Submit button is disabled until option is selected
- [ ] Submit button becomes enabled after selecting an option
- [ ] After submission, correct answer is highlighted (green)
- [ ] If incorrect, wrong answer shows red, correct shows green
- [ ] Feedback message appears ("✓ Correct" or "✗ Incorrect")

**How to test**:
1. Click option A → verify it highlights
2. Click option B → verify A unhighlights, B highlights
3. Click "Submit Answer" → verify feedback appears
4. Verify correct answer is marked with green border and ✓ icon

---

### 3. Explanations & Citations ✓
- [ ] "Show Explanation" button appears after submitting answer
- [ ] Clicking it displays full explanation
- [ ] Summary section appears
- [ ] Citations list shows with 📚 icons
- [ ] Learning objectives list shows with ✓ icons
- [ ] All sections are readable and formatted

**How to test**:
1. Answer any MCQ
2. Click "Show Explanation"
3. Scroll down to verify all sections appear:
   - Explanation (main text)
   - Summary (boxed section)
   - References (with book icons)
   - Learning Objectives (with checkmarks)

---

### 4. Navigation ✓
- [ ] "Next" button moves to next MCQ
- [ ] "Previous" button moves to previous MCQ
- [ ] "Previous" is disabled on Q1
- [ ] "Next" is disabled on Q200
- [ ] Jump to MCQ: Enter number, click "Go" → jumps to that MCQ
- [ ] Keyboard shortcuts work (Arrow keys for next/prev)

**How to test**:
1. Click "Next" repeatedly → verify MCQ number increments
2. Click "Previous" → verify MCQ number decrements
3. Type "50" in "Jump to" input, click "Go" → verify you jump to Q50
4. Press Right Arrow key → verify next MCQ loads
5. Press Left Arrow key → verify previous MCQ loads

---

### 5. Progress Tracking ✓
- [ ] Answering MCQ increments "Answered" count
- [ ] Correct answer increments "Correct" count
- [ ] Incorrect answer does NOT increment "Correct" count
- [ ] Score percentage updates correctly
- [ ] Progress bar fills as questions are answered
- [ ] Progress saves to LocalStorage
- [ ] Progress persists after page refresh

**How to test**:
1. Answer 5 MCQs correctly → verify stats show "Answered: 5, Correct: 5, Score: 100%"
2. Answer 2 MCQs incorrectly → verify stats show "Answered: 7, Correct: 5, Score: 71%"
3. Refresh page (Ctrl+R) → verify stats remain the same
4. Navigate to previously answered MCQ → verify it shows as already answered
5. Verify correct/incorrect answers are still marked

---

### 6. Flagging ✓
- [ ] Flag button (flag icon) appears on each MCQ
- [ ] Clicking flag button toggles flag state (gray → yellow)
- [ ] Flagged count increments in footer stats
- [ ] Flagged state persists after page reload
- [ ] Navigating away and back preserves flag state

**How to test**:
1. Click flag button on Q1 → verify it turns yellow/orange
2. Check footer stats → verify "Flagged: 1"
3. Navigate to Q2, flag it → verify "Flagged: 2"
4. Refresh page → verify flag states persist
5. Navigate back to Q1 → verify it's still flagged

---

### 7. Filtering ✓
- [ ] Topic filter dropdown shows all topics
- [ ] Selecting a topic filters MCQs to that topic only
- [ ] Current question counter updates to show filtered count
- [ ] "All Topics" shows all 200 MCQs
- [ ] View Mode filter works:
  - [ ] "Unanswered Only" shows only unanswered MCQs
  - [ ] "Incorrect Only" shows only incorrectly answered MCQs
  - [ ] "Flagged for Review" shows only flagged MCQs

**How to test**:
1. Answer Q1 correctly, Q2 incorrectly, flag Q3
2. Select "Unanswered Only" → verify only unanswered MCQs show
3. Select "Incorrect Only" → verify only Q2 shows
4. Select "Flagged for Review" → verify only Q3 shows
5. Select "All Questions" → verify all 200 MCQs show again

---

### 8. Reset Progress ✓
- [ ] Clicking "Reset Progress" shows confirmation dialog
- [ ] Clicking "Cancel" does nothing
- [ ] Clicking "OK" clears all progress
- [ ] Stats reset to 0
- [ ] All flags are removed
- [ ] All answers are cleared

**How to test**:
1. Answer a few MCQs and flag some
2. Click "Reset Progress" → verify confirmation dialog appears
3. Click "Cancel" → verify nothing changes
4. Click "Reset Progress" again → click "OK"
5. Verify all stats show 0
6. Navigate to previously answered MCQ → verify it shows as unanswered

---

## Security Testing Checklist

### 1. Copy Protection ✓
- [ ] Right-click is disabled (no context menu)
- [ ] Ctrl+C / Cmd+C does not copy selected text
- [ ] Ctrl+A / Cmd+A does not select all text
- [ ] Text selection with mouse is disabled
- [ ] Drag & drop is disabled
- [ ] Input fields (Jump to) still allow text selection

**How to test**:
1. Try to right-click on MCQ text → verify context menu doesn't appear
2. Try to select text with mouse → verify selection doesn't work
3. Try Ctrl+C on highlighted text → verify nothing copies
4. Click in "Jump to" input field → verify you CAN select/copy text in inputs

---

### 2. Keyboard Shortcut Prevention ✓
- [ ] Ctrl+U / Cmd+U (view source) is blocked
- [ ] Ctrl+S / Cmd+S (save page) is blocked
- [ ] F12 (DevTools) is blocked
- [ ] Ctrl+Shift+I / Cmd+Option+I (inspect) is blocked
- [ ] Ctrl+Shift+J / Cmd+Option+J (console) is blocked

**How to test**:
1. Try each keyboard shortcut listed above
2. Verify none of them open DevTools or perform their default action
3. Note: Determined users can still open DevTools via menu

---

### 3. Code Obfuscation ✓
- [ ] Viewing page source (if possible) shows minified code
- [ ] Variable names are shortened (not readable)
- [ ] No readable MCQ data in source
- [ ] MCQ data is Base64 encoded
- [ ] JavaScript is minified and hard to read

**How to test** (production build only):
1. Open DevTools (via browser menu, not keyboard)
2. Go to Sources tab
3. Verify JavaScript is minified (all on one line)
4. Verify no readable MCQ content in source

---

### 4. Print Prevention ✓
- [ ] Attempting to print shows "Printing is disabled" message
- [ ] Ctrl+P / Cmd+P opens print dialog but page is blank
- [ ] Print preview shows warning instead of content

**How to test**:
1. Try Ctrl+P / Cmd+P
2. Verify print preview shows warning message, not MCQ content

---

## Responsive Design Testing

### Mobile (320px - 767px) ✓
Test on: iPhone SE (375px), Samsung Galaxy (360px)

- [ ] Layout is single-column
- [ ] Text is readable (no horizontal scrolling)
- [ ] Buttons are large enough to tap (44x44px minimum)
- [ ] Options stack vertically
- [ ] Navigation controls are accessible
- [ ] Progress bar is visible
- [ ] Filter dropdowns are usable

**How to test**:
1. Open Chrome DevTools (Ctrl+Shift+M for device mode)
2. Select "iPhone SE" or "Galaxy S5"
3. Navigate through MCQs
4. Verify all elements are accessible and readable

---

### Tablet (768px - 1023px) ✓
Test on: iPad (768px), iPad Pro (1024px)

- [ ] Layout uses CSS Grid (2-column for options)
- [ ] Header controls are in a row
- [ ] All text is readable
- [ ] Touch targets are large enough
- [ ] Footer stats are visible

**How to test**:
1. Open Chrome DevTools device mode
2. Select "iPad"
3. Verify options display in 2-column grid
4. Verify controls are laid out horizontally

---

### Desktop (1024px+) ✓
Test on: 1920x1080, 1440px, 1024px

- [ ] Maximum width is 1200px (centered)
- [ ] Options display in 2-column grid
- [ ] Plenty of white space
- [ ] Hover effects work on buttons
- [ ] All features are accessible

**How to test**:
1. Open in full-screen browser (1920px width)
2. Verify content is centered with margins
3. Hover over buttons → verify hover effects work
4. Resize browser → verify responsive breakpoints work

---

## Browser Compatibility Testing

### Chrome 90+ ✓
- [ ] All features work
- [ ] No console errors
- [ ] Animations smooth
- [ ] LocalStorage works

### Firefox 88+ ✓
- [ ] All features work
- [ ] No console errors
- [ ] CSS Grid displays correctly
- [ ] LocalStorage works

### Safari 14+ (macOS/iOS) ✓
- [ ] All features work
- [ ] Copy protection works (user-select: none)
- [ ] Touch gestures work on iOS
- [ ] LocalStorage works

### Edge 90+ ✓
- [ ] All features work
- [ ] No console errors
- [ ] LocalStorage works

---

## Performance Testing

### Load Time ✓
- [ ] Page loads in <2 seconds on fast connection
- [ ] Page loads in <5 seconds on 3G connection
- [ ] Loading overlay shows during initial load
- [ ] No layout shifts during load (CLS score)

**How to test**:
1. Open Chrome DevTools → Network tab
2. Select "Fast 3G" throttling
3. Hard refresh (Ctrl+Shift+R)
4. Verify page loads in under 5 seconds

---

### Runtime Performance ✓
- [ ] Smooth scrolling
- [ ] No lag when clicking options
- [ ] Navigation is instant
- [ ] Filtering is fast (<500ms)
- [ ] LocalStorage saves without lag

**How to test**:
1. Navigate through 20 MCQs rapidly
2. Verify no lag or stuttering
3. Apply different filters repeatedly
4. Verify filtering is responsive

---

## Edge Cases Testing

### 1. Empty Filters ✓
- [ ] Filtering to topic with no answered MCQs → shows "No MCQs match"
- [ ] View Mode "Incorrect Only" with no incorrect answers → shows message

**How to test**:
1. Don't answer any MCQs
2. Select View Mode "Incorrect Only"
3. Verify message appears instead of crashing

---

### 2. LocalStorage Full ✓
- [ ] If LocalStorage quota exceeded, app still works
- [ ] Graceful degradation (no saving, but app functional)

**How to test** (advanced):
1. Open DevTools Console
2. Run: `for(let i=0;i<10000;i++){localStorage.setItem('test'+i, 'x'.repeat(1000))}`
3. Verify app still loads and functions

---

### 3. Rapid Clicking ✓
- [ ] Rapidly clicking "Next" doesn't break navigation
- [ ] Rapidly clicking options doesn't select multiple
- [ ] Submit button can't be clicked twice

**How to test**:
1. Click "Next" button 10 times rapidly
2. Verify navigation works correctly
3. Click different options rapidly → verify only one is selected

---

## Accessibility Testing

### Keyboard Navigation ✓
- [ ] Tab key moves focus to all interactive elements
- [ ] Enter key activates buttons
- [ ] Arrow keys navigate between MCQs
- [ ] Focus indicators are visible (blue outline)

**How to test**:
1. Start at top of page
2. Press Tab repeatedly → verify focus moves through all buttons/inputs
3. Verify visible focus indicator (blue outline)

---

### Screen Reader Compatibility ✓
- [ ] All images have alt text (if any)
- [ ] All buttons have descriptive labels
- [ ] Form labels are associated with inputs
- [ ] Semantic HTML is used (header, main, footer)

**How to test** (basic):
1. Inspect HTML structure
2. Verify semantic tags are used
3. Verify all inputs have labels

---

## Automated Testing (Optional)

If you want to run automated tests:

### Lighthouse Audit
```bash
# In Chrome DevTools
1. Open DevTools (F12)
2. Go to "Lighthouse" tab
3. Select "Performance" + "Accessibility" + "Best Practices"
4. Click "Analyze page load"

# Expected scores:
- Performance: 90+
- Accessibility: 90+
- Best Practices: 90+
```

---

## Bug Reporting Template

If you find a bug, report it using this template:

```markdown
**Bug Description**: [Brief description]

**Steps to Reproduce**:
1. [First step]
2. [Second step]
3. [Third step]

**Expected Behavior**: [What should happen]

**Actual Behavior**: [What actually happens]

**Environment**:
- Browser: [e.g., Chrome 110]
- OS: [e.g., Windows 11]
- Device: [e.g., Desktop, iPhone 12]
- Build: [Development or Production]

**Screenshots**: [If applicable]

**Console Errors**: [Copy any errors from browser console]
```

---

## Testing Sign-Off

### Development Testing
- [ ] All functional tests pass
- [ ] All security tests pass
- [ ] Responsive design works on 3+ screen sizes
- [ ] Tested on 3+ browsers
- [ ] Performance is acceptable (<2s load time)

**Tester Name**: _________________
**Date**: _________________
**Build Version**: Development / Production
**Notes**: _________________

---

### Production Testing
- [ ] Build completes without errors
- [ ] Production build is minified and obfuscated
- [ ] All functional tests pass
- [ ] Copy protection works
- [ ] LocalStorage persistence works
- [ ] Responsive design works
- [ ] Browser compatibility confirmed

**Tester Name**: _________________
**Date**: _________________
**Build Size**: _________ KB
**Notes**: _________________

---

## Quick Regression Test (5 minutes)

After making changes, run this quick test:

1. ✓ Load page → verify no errors
2. ✓ Answer MCQ → verify feedback shows
3. ✓ Navigate (next/prev) → verify works
4. ✓ Filter by topic → verify filters
5. ✓ Refresh page → verify progress persists
6. ✓ Right-click → verify disabled
7. ✓ Resize window → verify responsive

**Pass/Fail**: _________
**Tested on**: _________________
**Date**: _________________
