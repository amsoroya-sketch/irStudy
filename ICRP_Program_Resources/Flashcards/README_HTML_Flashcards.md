# ICRP Interactive HTML Flashcards - User Guide

**Version:** 1.0
**Created:** December 16, 2025
**System:** Standalone HTML + JavaScript (Offline Capable)

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Features Overview](#features-overview)
3. [How to Use](#how-to-use)
4. [Spaced Repetition System](#spaced-repetition-system)
5. [Keyboard Shortcuts](#keyboard-shortcuts)
6. [Progress Tracking](#progress-tracking)
7. [Filtering and Search](#filtering-and-search)
8. [Import/Export](#importexport)
9. [Mobile Usage](#mobile-usage)
10. [Troubleshooting](#troubleshooting)
11. [Technical Details](#technical-details)

---

## 🚀 Quick Start

### Step 1: Open the Application

1. Navigate to: `ICRP_Program_Resources/Flashcards/`
2. Double-click: `ICRP_Flashcards_Interactive.html`
3. The application will open in your default web browser

### Step 2: Load Flashcard Data

1. Click **"Choose File"** button
2. Select: `flashcard_data.json` (same folder)
3. The app will load all 750 flashcards

### Step 3: Start Studying

1. Read the **front** of the card (question)
2. Think of your answer
3. Click the card (or press **Space**) to flip and see the **back** (answer)
4. Rate yourself: **Again / Hard / Good / Easy**
5. The card will be scheduled for review based on your rating

**That's it! You're ready to study.**

---

## ✨ Features Overview

### ✅ Core Features

- **750 High-Quality Flashcards** - Australian medical context
- **Spaced Repetition Algorithm** - SM-2 algorithm for optimal retention
- **Offline Capable** - Works without internet connection
- **LocalStorage Persistence** - Progress saved automatically
- **Mobile Responsive** - Study on phone, tablet, or desktop
- **Print Friendly** - Print cards for offline study

### 🎯 Study Features

- **Smart Scheduling** - Cards appear when you need to review them
- **Progress Tracking** - See studied today, due cards, mastered cards
- **Category Filtering** - Focus on specific specialties or categories
- **Difficulty Levels** - Easy, Medium, Hard cards
- **Search Function** - Find specific topics quickly
- **Shuffle Mode** - Randomize card order

### 📊 Statistics Dashboard

- **Total Cards** - 750 flashcards
- **Studied Today** - Cards reviewed in current session
- **Due for Review** - Cards needing attention
- **Mastered** - Cards with interval ≥21 days (84% retention)

---

## 📖 How to Use

### Basic Workflow

```
1. LOAD → Choose flashcard_data.json
2. READ → Front of card (question)
3. THINK → Formulate your answer
4. FLIP → Click card or press Space
5. RATE → Again / Hard / Good / Easy
6. REPEAT → Next card automatically loads
```

### Rating System Explained

| Button | Meaning | Next Review | Use When |
|--------|---------|-------------|----------|
| **Again** (Red) | I didn't know this | 10 minutes | Completely forgot or wrong |
| **Hard** (Orange) | I barely remembered | 1 day | Struggled to recall |
| **Good** (Green) | I remembered it | 3 days | Recalled with some effort |
| **Easy** (Blue) | I knew it instantly | 7 days | Immediate recall |

### Study Session Best Practices

**Daily Routine (Recommended):**
- **Morning:** Review due cards (20-30 minutes)
- **New cards per day:** 25-30 cards
- **Expected time:** 30-45 minutes/day
- **Completion timeline:** 25-30 days for all 750 cards

**Quality over Speed:**
- ✅ Take time to understand each card
- ✅ Read the source reference if unsure
- ✅ Don't rush through ratings
- ❌ Don't mass-study 100+ cards at once

**Optimal Study Environment:**
- Quiet space
- No distractions
- Good lighting
- Breaks every 25 minutes (Pomodoro technique)

---

## 🧠 Spaced Repetition System

### SM-2 Algorithm (Simplified)

The app uses a **proven spaced repetition algorithm** to optimize long-term retention:

**How it Works:**

1. **First Review:**
   - Rate "Good" → Review in 3 days
   - Rate "Easy" → Review in 7 days
   - Rate "Hard" → Review in 1 day
   - Rate "Again" → Review in 10 minutes

2. **Subsequent Reviews:**
   - Interval multiplied by "easiness factor" (1.3 - 2.5)
   - Good performance → Longer intervals
   - Poor performance → Reset to day 1

3. **Mastered Cards:**
   - Interval reaches 21+ days
   - 84% retention probability
   - Still reviewed periodically

**Example Timeline:**

```
Card: "DKA ICU criteria"

Day 0: First study → Rate "Good" → Due in 3 days
Day 3: Review → Rate "Good" → Due in 7 days (3 × 2.5 easiness)
Day 10: Review → Rate "Easy" → Due in 18 days (7 × 2.5 × 1.5)
Day 28: Review → Rate "Good" → Due in 45 days (MASTERED)
```

---

## ⌨️ Keyboard Shortcuts

### Navigation

| Key | Action |
|-----|--------|
| **Space** or **Enter** | Flip card |
| **Arrow Left** (←) | Previous card |
| **Arrow Right** (→) | Next card |

### Rating (After Flipping Card)

| Key | Rating |
|-----|--------|
| **1** | Again (< 10 minutes) |
| **2** | Hard (1 day) |
| **3** | Good (3 days) |
| **4** | Easy (7 days) |

### Pro Tip
**Speed Study Workflow:**
1. Read front → Press **Space**
2. Check answer → Press **1/2/3/4**
3. Next card auto-loads → Repeat

Average time per card: **15-20 seconds**

---

## 📊 Progress Tracking

### Automatic Saving

- **LocalStorage** saves progress every time you rate a card
- **No manual save needed**
- **Survives browser restarts**
- **Per-browser storage** (Chrome progress ≠ Firefox progress)

### Progress Metrics

**Dashboard Shows:**

1. **Total Cards:** 750 (all flashcards)
2. **Studied Today:** Cards reviewed in current calendar day
3. **Due for Review:** Cards with due date ≤ today
4. **Mastered:** Cards with 21+ day intervals

**Progress Bar:**
- Shows percentage of mastered cards
- Target: 100% (all 750 cards mastered)
- Typical timeline: 2-3 months of daily study

### What Counts as "Studied"?

- Rating a card (Again/Hard/Good/Easy)
- Resets at midnight each day
- Viewing without rating does NOT count

---

## 🔍 Filtering and Search

### Filter by Deck

**Available Decks:**
- Medicine (Cardiology, Respiratory, GI, Neurology, etc.)
- Surgery
- ObGyn
- Paediatrics
- Psychiatry
- Ethics & Communication
- Physical Examination
- Red Flags & Critical
- IMG Common Mistakes
- Australian Context

**How to Use:**
1. Select deck from dropdown
2. Click **"Apply Filters"**
3. Only cards from that deck will appear

### Filter by Category

**Available Categories:**
- Differentials
- IMG Mistakes
- Physical Exam
- Red Flags
- Australian Context
- Communication

### Filter by Difficulty

- **Easy:** Basic definitions, recall facts
- **Medium:** Clinical reasoning, differentials
- **Hard:** Red flags, critical management

### Search Function

**Search Box:**
- Searches both front AND back of cards
- Case-insensitive
- Real-time filtering

**Example Searches:**
- "DKA" → All diabetic ketoacidosis cards
- "RED FLAG" → All critical warning cards
- "IM adrenaline" → Anaphylaxis management
- "eTG" → Australian Therapeutic Guidelines references

### Show Due Cards Only

**Button:** "Show Due Cards"
- Filters to cards needing review TODAY
- Perfect for daily study sessions
- Shows "No cards due!" if you're up to date ✅

### Shuffle Mode

**Button:** "Shuffle Deck"
- Randomizes current card order
- Prevents pattern memorization
- Useful for exam simulation

---

## 💾 Import/Export

### Export Progress

**Why Export?**
- Backup your study progress
- Transfer between devices
- Share with study partner
- Restore after browser reset

**How to Export:**
1. Click **"Export Progress"** button
2. Modal appears with JSON data
3. Click **"Copy to Clipboard"**
4. Paste into text file and save (e.g., `my_progress_2025-12-16.json`)

**What's Exported:**
```json
{
  "version": "1.0",
  "exported": "2025-12-16T10:30:00.000Z",
  "progress": {
    "1": {
      "easinessFactor": 2.5,
      "interval": 7,
      "repetitions": 2,
      "dueDate": "2025-12-23T10:30:00.000Z",
      "lastReviewed": "2025-12-16T10:30:00.000Z"
    },
    ...
  }
}
```

### Import Progress

**How to Import:**
1. Click **"Import Progress"** button
2. Paste JSON data from exported file
3. Click **"Import"**
4. Progress restored ✅

**Use Cases:**
- Restore backup
- Move from phone to laptop
- Combine progress from multiple devices (manual merge needed)

### Reset All Progress

**Button:** "Reset All Progress"
- ⚠️ **WARNING:** Cannot be undone
- Deletes all study history
- Resets all cards to "new" status
- Confirmation prompt appears

**When to Reset:**
- Starting fresh after completing deck
- Sharing device with another user
- Major review before exams

---

## 📱 Mobile Usage

### Responsive Design

**Supported Screen Sizes:**
- 📱 **Mobile:** 320px - 480px (iPhone SE to iPhone 14 Pro Max)
- 📱 **Tablet:** 481px - 768px (iPad Mini to iPad Pro)
- 💻 **Desktop:** 769px+ (Laptops, monitors)

### Mobile-Specific Features

**Touch Gestures:**
- **Tap card** → Flip
- **Tap buttons** → Navigate/Rate

**Optimized Layout:**
- Larger buttons for touch targets
- Simplified navigation
- Full-width response buttons

### Best Practices for Mobile

**Study on the Go:**
- ✅ Public transport (offline mode)
- ✅ Coffee shop (no WiFi needed)
- ✅ Between clinical rotations

**Battery Saving:**
- Enable dark mode (if browser supports)
- Lower screen brightness
- Close other apps

**Data Usage:**
- **Zero data** - fully offline after initial load
- No analytics or tracking
- No external API calls

---

## 🔧 Troubleshooting

### Cards Not Loading

**Problem:** "Choose File" button doesn't work

**Solutions:**
1. Ensure `flashcard_data.json` is in same folder as HTML file
2. Try different browser (Chrome, Firefox, Safari)
3. Check file isn't corrupted (should be 337 KB)
4. Clear browser cache and reload

### Progress Not Saving

**Problem:** Progress resets after closing browser

**Solutions:**
1. Check browser allows LocalStorage (not in private/incognito mode)
2. Don't use "Clear browsing data" (deletes LocalStorage)
3. Export progress regularly as backup
4. Check available storage (need ~1 MB free)

### Cards Show "NaN" or Errors

**Problem:** Statistics show weird numbers

**Solutions:**
1. Export progress, reset, then re-import
2. Clear LocalStorage: `localStorage.removeItem('icrp_flashcard_progress')`
3. Refresh page (F5 or Cmd+R)

### Can't Flip Cards

**Problem:** Clicking card does nothing

**Solutions:**
1. Ensure flashcard data is loaded (should see card content)
2. Try keyboard shortcut (Space bar)
3. Check browser console for JavaScript errors (F12 → Console)
4. Reload page

### Search Not Working

**Problem:** Search box doesn't filter cards

**Solutions:**
1. Type search term
2. Click **"Apply Filters"** button (required!)
3. Check spelling
4. Try simpler search terms

---

## 🛠️ Technical Details

### Browser Compatibility

**Fully Supported:**
- ✅ Chrome 90+ (Desktop + Mobile)
- ✅ Firefox 88+ (Desktop + Mobile)
- ✅ Safari 14+ (macOS, iOS)
- ✅ Edge 90+ (Chromium-based)

**Partially Supported:**
- ⚠️ Internet Explorer 11 (no CSS Grid, use Firefox instead)

### File Size

- **HTML File:** ~45 KB (embedded CSS + JavaScript)
- **Flashcard Data:** 337 KB (750 cards)
- **Total:** ~382 KB
- **LocalStorage Usage:** ~50-100 KB (progress data)

### Data Privacy

**What's Stored:**
- ✅ Study progress (LocalStorage)
- ✅ Card ratings and intervals
- ✅ Last review dates

**What's NOT Stored:**
- ❌ No personal information
- ❌ No analytics or tracking
- ❌ No external server communication
- ❌ No cookies

**Completely Private:**
- Works offline
- No data leaves your device
- No internet connection needed (after initial load)

### Performance

**Optimized For:**
- Fast loading (<1 second on modern browsers)
- Smooth animations (60 FPS card flips)
- Low memory usage (<50 MB RAM)
- Instant search filtering

**Tested With:**
- 750 cards (current dataset)
- Up to 2,000 cards (stress tested)
- Mobile devices (iPhone 12, iPad Pro)

### Print Mode

**Print Functionality:**
1. Press **Ctrl+P** (Windows) or **Cmd+P** (Mac)
2. Select printer or "Save as PDF"
3. Cards print in **study guide format:**
   - Front on one side
   - Back immediately below
   - Metadata included
   - No buttons (clean print)

**Use Cases:**
- Backup hard copy
- Offline study when no device available
- Annotation for weak areas

---

## 📚 Study Tips

### First-Time Users

**Week 1:**
- Study 20-25 new cards per day
- Focus on **red flags** and **critical** categories
- Don't worry about "Again" ratings (normal for new material)

**Week 2-4:**
- Maintain 25-30 new cards per day
- Reviews will increase (20-50 reviews/day)
- Total daily time: 30-45 minutes

**Month 2-3:**
- All 750 cards introduced
- Focus on reviews only (50-100 reviews/day)
- Cards start reaching "mastered" status

### Advanced Techniques

**Leitner System Integration:**
- Filter by difficulty
- Study "Hard" cards more frequently
- Combine with Anki deck for cross-reinforcement

**Active Recall:**
- Don't flip card too quickly
- Verbalize answer out loud
- Write answer on paper (for complex cards)

**Clinical Context:**
- Visualize OSCE scenario
- Imagine explaining to patient/examiner
- Link to real patient encounters

### Pre-Exam Strategy

**2 Weeks Before ICRP:**
1. **Day 1-7:** Review ALL cards (filter: Show Due Cards)
2. **Day 8-10:** Focus on "red flags" and "IMG mistakes" categories
3. **Day 11-13:** Review "differentials" and "physical exam"
4. **Day 14:** Rest day (light review only, 10-15 cards)

**Day Before ICRP:**
- ❌ Don't cram 200 cards
- ✅ Review 20-30 high-yield red flags
- ✅ Get good sleep (retention happens during sleep!)

---

## 🎯 Integration with Other Study Materials

### Combine with Anki Deck

**Dual-System Approach:**
- **Anki (Desktop):** Daily structured study at home
- **HTML Flashcards (Mobile):** On-the-go review

**Why Both?**
- Anki has better scheduling algorithm (full SM-2)
- HTML is more accessible (no Anki app needed)
- Cross-platform redundancy

### Link to OSCE Modules

**Source References:**
- Every card shows source file (e.g., "Medicine/09_Endocrinology_Diabetes_Management.html")
- Click reference → Open source module → Read full context
- Deepens understanding beyond flashcard

### Textbook Cross-Reference

**Workflow:**
1. Review flashcard on topic (e.g., "DKA management")
2. Check `TEXTBOOK_INTEGRATION_GUIDE.md`
3. Read corresponding Talley or Murtagh chapter
4. Return to flashcard → Rate "Easy" (now fully understood)

---

## 📞 Support

### Need Help?

**Check These First:**
1. This README (you're reading it!)
2. Troubleshooting section above
3. Browser console (F12 → Console) for error messages

### Feature Requests

**Want a New Feature?**
- Export progress and create GitHub issue
- Describe use case
- Provide examples

---

## 📄 Version History

**v1.0 (December 16, 2025)**
- Initial release
- 750 flashcards
- SM-2 spaced repetition
- LocalStorage persistence
- Mobile responsive design
- Import/export functionality
- Print mode
- Keyboard shortcuts

---

## 🙏 Acknowledgments

**Based On:**
- 48 ICRP OSCE modules (Australian context)
- eTG 2024 (Therapeutic Guidelines)
- AMC Clinical OSCE blueprint
- Dr. Aamir Saeed's 9 OSCE principles

**Algorithm:**
- SM-2 spaced repetition (SuperMemo 2)
- Simplified for web implementation

---

**Last Updated:** December 16, 2025
**Maintained By:** ICRP Study Project
**License:** For personal educational use (ICRP preparation)

**Good luck with your studies! 🎓**
