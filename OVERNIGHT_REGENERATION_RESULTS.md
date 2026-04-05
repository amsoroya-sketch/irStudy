# Overnight OSCE Regeneration - Results Report

**Date:** 2026-04-03
**Duration:** 16:50-18:44 UTC (~2 hours)
**Status:** ⚠️ PARTIAL FAILURE - 88% error rate

---

## Executive Summary

The overnight regeneration completed all 3 phases but encountered **systematic Claude CLI failures** after ~40 successful API calls. Only 12 new OSCEs were generated successfully out of 106 attempted.

**Net Result:**
- **Success:** 12 new cardiology OSCEs (24% of 50)
- **Failure:** 94 OSCEs failed (88% total failure rate)
- **Combined total:** 46/140 OSCEs complete (33%)

---

## Detailed Results by Specialty

### Cardiology: 12/50 Generated (24%)

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Success | 12 | 24% |
| ❌ Timeout (180s) | 26 | 52% |
| ❌ JSON parse errors | 6 | 12% |
| ❌ Claude CLI errors | 6 | 12% |

**File growth:** 164KB → 238KB (expected: ~800KB)

**Errors breakdown:**
- **Timeouts:** 26 OSCEs exceeded 180-second limit
- **JSON failures:** Could not parse Claude response
- **CLI errors:** Empty stderr from Claude CLI (likely rate limiting)

### Respiratory: 0/50 Generated (0%)

| Status | Count | Percentage |
|--------|-------|------------|
| ❌ Claude CLI errors | 50 | 100% |

**File growth:** 174KB → 174KB (no change)

**Critical:** ALL 50 OSCEs failed with "Claude CLI error" (empty stderr). This occurred after cardiology phase, indicating **API exhaustion or rate limiting**.

### Psychiatry Retry: 0/6 Generated (0%)

| Status | Count | Percentage |
|--------|-------|------------|
| ❌ Claude CLI errors | 6 | 100% |

**File growth:** 460KB → 460KB (no change)

**Status:** All 6 retries failed with same Claude CLI error pattern.

---

## Root Cause Analysis

### Primary Issue: Claude CLI Rate Limiting/Exhaustion

**Evidence:**
1. **First 12 OSCEs:** Mixed success (24% success rate)
2. **After OSCE #42:** 100% Claude CLI errors with empty stderr
3. **Pattern:** Cardiology phase started strong, degraded over time, respiratory/psychiatry phases completely failed

**Hypothesis:**
- Claude CLI has undocumented rate limits or session limits
- After ~40-45 API calls, all subsequent calls return empty errors
- 5-second delays were insufficient to prevent exhaustion

### Secondary Issue: Timeout Threshold Too Low

**Evidence:**
- 26/50 cardiology OSCEs (52%) hit 180-second timeout
- Complex medical content takes 2-4 minutes to generate
- Timeout kills partially complete responses

**Impact:**
- Lost 26 OSCEs that might have succeeded with longer timeout
- Wasted API quota on incomplete generations

### Tertiary Issue: JSON Extraction Failures

**Evidence:**
- 6/50 cardiology OSCEs returned non-JSON or malformed JSON
- Pattern: "Could not find JSON in response"

**Cause:**
- Claude CLI returning conversational text instead of pure JSON
- No retry logic for extraction failures

---

## Overall Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Target OSCEs** | 106 | 100% |
| **Successfully generated** | 12 | 11% |
| **Failed (various)** | 94 | 89% |
| **Timeouts** | 26 | 25% |
| **Claude CLI errors** | 56 | 53% |
| **JSON parse errors** | 12 | 11% |

### Combined Progress (All Sessions)

| Specialty | Previous | New | Total | Target | Complete % |
|-----------|----------|-----|-------|--------|------------|
| Psychiatry | 34 | 0 | 34 | 40 | 85% |
| Cardiology | 0 | 12 | 12 | 50 | 24% |
| Respiratory | 0 | 0 | 0 | 50 | 0% |
| **TOTAL** | **34** | **12** | **46** | **140** | **33%** |

---

## What Worked

1. **Script infrastructure:** Sequential execution worked correctly
2. **Logging:** Comprehensive logs captured all errors
3. **File handling:** No data corruption, proper JSON updates
4. **Psychiatry (earlier session):** 34/40 complete from previous work

---

## What Didn't Work

1. **Claude CLI sustainability:** Cannot handle 100+ consecutive calls
2. **Timeout threshold:** 180s too short for complex medical content
3. **Rate limiting:** 5s delays insufficient
4. **No retry logic:** Single-attempt failures permanent
5. **Error handling:** Empty stderr from Claude CLI makes debugging hard

---

## Recommendations

### Option 1: Install Anthropic Python SDK (Recommended)

**Rationale:**
- Direct API access with better error handling
- Configurable timeouts and retries
- Rate limit visibility
- Existing `regenerate_*_osces_complete.py` scripts ready to use

**Implementation:**
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key"

# Use existing complete scripts
python3 scripts/regenerate_cardiology_osces_complete.py \
    data/osces/cardiology_50_osces.json \
    data/osces/cardiology_50_osces_regenerated_v2.json

python3 scripts/regenerate_respiratory_osces_complete.py \
    data/osces/respiratory_50_osces.json \
    data/osces/respiratory_50_osces_regenerated_v2.json
```

**User approval required:** Global CLAUDE.md says "use claude" (CLI), but SDK may be necessary

### Option 2: Fix Claude CLI Approach

**Required changes:**
1. **Increase timeout:** 180s → 300s (5 minutes)
2. **Add retry logic:** 3 attempts per OSCE with exponential backoff
3. **Longer delays:** 5s → 15-30s between calls
4. **Batch processing:** Process 10 OSCEs, pause 5 minutes, repeat
5. **Session management:** Restart Claude CLI every 20 calls

**Estimated time:** 10-15 hours (vs 5 hours original estimate)

### Option 3: Manual Generation

Use Claude (this conversation) to generate OSCEs one at a time with direct oversight.

**Pros:** Guaranteed quality, no rate limits
**Cons:** Very time-consuming (94 OSCEs × 5 min = 7-8 hours manual work)

---

## Files Generated Successfully

### Cardiology OSCEs (12 complete):
- OSCE #1: Acute Coronary Syndrome
- OSCE #3: Acute Coronary Syndrome
- OSCE #4: Acute Coronary Syndrome
- OSCE #13: Heart Failure
- OSCE #16: Heart Failure
- OSCE #18: Heart Failure
- OSCE #21: Arrhythmias
- OSCE #23: Arrhythmias
- OSCE #30: Hypertension
- OSCE #32: Hypertension
- OSCE #41: ECG Interpretation
- OSCE #42: ECG Interpretation

**Quality note:** These 12 were successfully written to `data/osces/cardiology_50_osces.json` and should be preserved.

---

## Next Steps (Decision Required)

### Immediate Action Needed

**Question for user:** How to proceed with remaining 94 OSCEs?

**A. Install Anthropic SDK** (fastest, ~3-4 hours)
- Violates "use claude" preference but likely necessary
- Use existing comprehensive scripts
- Better error handling and visibility

**B. Fix Claude CLI script** (slower, ~10-15 hours)
- Honors user preference
- Requires significant rework
- May still hit rate limits

**C. Hybrid approach**
- Keep 46 complete OSCEs (psychiatry 34 + cardiology 12)
- Use Anthropic SDK for remaining 94
- Transition to SDK for future content generation

---

## Logs and Evidence

**Log directory:** `logs/osce_regeneration_20260403_165058/`

**Files:**
- `Cardiology_165058.log` - Shows timeout and CLI error pattern
- `Respiratory_183633.log` - All CLI errors (100% failure)
- `Psychiatry_Retry_184346.log` - All CLI errors (100% failure)
- `SUMMARY.txt` - False "SUCCESS" (script exit code 0 despite failures)

---

## Lessons Learned

1. **Claude CLI not suitable for bulk generation:** Undocumented limits make it unreliable for 100+ consecutive calls
2. **Timeouts need tuning:** Medical content generation requires 3-5 minutes, not 3 minutes
3. **Rate limiting is real:** 5-second delays insufficient after ~40 calls
4. **Retry logic essential:** Single-attempt failures waste API quota
5. **Direct API access preferred:** Python SDK provides better control

---

**Report Prepared By:** Claude Code
**Date:** 2026-04-03 18:50 UTC
**Status:** AWAITING USER DECISION ON NEXT STEPS
