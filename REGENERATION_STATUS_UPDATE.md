# OSCE Regeneration - Status Update

**Date:** 2026-04-03
**Time:** 05:45 UTC
**Session:** Continuation from previous work

---

## Current Status Summary

| Specialty | Total OSCEs | Complete | Incomplete | Success Rate |
|-----------|-------------|----------|------------|--------------|
| **Psychiatry** | 40 | 34 | 6 | 85% ✅ |
| **Cardiology** | 50 | 0 | 50 | 0% ❌ |
| **Respiratory** | 50 | 1 | 49 | 2% ❌ |
| **TOTAL** | 140 | 35 | 105 | 25% |

---

## What's Working

### Psychiatry: 34/40 Complete (85%)

**Success:** The smart completion script successfully regenerated 18 psychiatry OSCEs in the previous session, bringing the total from 16 to 34.

**Quality Sample (OSCE #1):**
- Title: "Major Depressive Disorder with Active Suicidal Ideation - Emergency Department Assessment"
- Patient: David Chen, 38-year-old plumber, business collapsed ($180k debt)
- Complete SAFE-T protocol with specific risk assessment
- All medications with doses + PBS codes
- Australian crisis contacts (Lifeline 13 11 14, Beyond Blue 1300 224 636)

**6 Failed OSCEs:** #7, #20, #28, #30, #36, #38 - JSON extraction failures

---

## Critical Issue: Rate Limiting

### Problem Identified

**What Happened:**
- Launched 6 parallel regeneration processes simultaneously
- All processes calling Claude CLI with no rate limiting
- Result: Claude API blocked all calls after 1-2 successful generations

**Evidence:**
```
Cardiology: 0/50 generated - ALL Claude CLI errors (empty stderr)
Respiratory: 1/50 generated successfully, then 49 failures
```

**Root Cause:** Too many concurrent Claude CLI calls triggering API rate limits

---

## Solutions Considered

### Option 1: Use Existing Regeneration Scripts ❌

**Files Found:**
- `scripts/regenerate_cardiology_osces_complete.py`
- `scripts/regenerate_respiratory_osces_complete.py`

**Problem:** These scripts use `from anthropic import Anthropic` (Python SDK), which isn't installed

**User Constraint:** Global CLAUDE.md says "don't use anthropic key, use claude" (CLI)

**Verdict:** Cannot use these scripts without violating user preferences

### Option 2: Fix Completion Script with Rate Limiting ✅

**Approach:**
1. Stop all parallel processes
2. Modify `scripts/complete_partial_osces.py` to add delays
3. Run sequentially (not in parallel)
4. Add retry logic for transient failures

**Implementation:**
```python
# Add after each successful/failed generation
time.sleep(3)  # 3-second delay between calls (20 calls/min max)

# Add retry logic
max_retries = 3
for retry in range(max_retries):
    result = subprocess.run(['claude', '--model', CLAUDE_MODEL], ...)
    if result.returncode == 0:
        break
    time.sleep(5 * (retry + 1))  # Exponential backoff
```

### Option 3: Install Anthropic SDK ⚠️

**Would enable:** Use of existing complete scripts with comprehensive prompts

**Concerns:**
- User preference is to use Claude CLI
- Might conflict with global configuration

---

## Recommended Next Steps

### Immediate (Fix Rate Limiting)

1. **Increase delay in completion script:**
   ```python
   # Line 368 in scripts/complete_partial_osces.py
   time.sleep(1)  # Change to time.sleep(3)
   ```

2. **Add retry logic for transient failures**

3. **Run ONE specialty at a time** (not parallel)

### Sequential Execution

```bash
# Run cardiology ONLY (wait for completion)
python3 scripts/complete_partial_osces.py \
    data/osces/cardiology_50_osces.json \
    data/osces/cardiology_50_osces.json \
    cardiology
# Expected time: 50 OSCEs × 3 min = 150 minutes (2.5 hours)

# Then run respiratory
python3 scripts/complete_partial_osces.py \
    data/osces/respiratory_50_osces.json \
    data/osces/respiratory_50_osces.json \
    respiratory
# Expected time: 50 OSCEs × 3 min = 150 minutes (2.5 hours)

# Finally retry 6 failed psychiatry OSCEs
python3 scripts/complete_partial_osces.py \
    data/osces/psychiatry_40_osces_regenerated.json \
    data/osces/psychiatry_40_osces.json \
    psychiatry
# Expected time: 6 OSCEs × 3 min = 18 minutes
```

**Total estimated time:** 5.5 hours

---

## Alternative: Use Anthropic SDK

If user approves using the Anthropic Python SDK instead of Claude CLI:

```bash
# Install SDK
pip install anthropic

# Run existing complete scripts (have comprehensive prompts built in)
python3 scripts/regenerate_cardiology_osces_complete.py \
    data/osces/cardiology_50_osces.json \
    data/osces/cardiology_50_osces_regenerated_v2.json

python3 scripts/regenerate_respiratory_osces_complete.py \
    data/osces/respiratory_50_osces.json \
    data/osces/respiratory_50_osces_regenerated_v2.json
```

**Advantages:**
- Scripts have comprehensive prompts (100+ lines per specialty)
- May have better error handling
- Created specifically for this project

**Disadvantages:**
- Violates user's "use claude" preference
- Requires API key configuration

---

## Files Modified This Session

1. **Created:** `scripts/complete_partial_osces.py` (370 lines)
2. **Modified:** `data/osces/psychiatry_40_osces_regenerated.json` (34/40 complete)
3. **Created:** `constraints/16-osce-requirements.md` (53KB)
4. **Created:** `REGENERATION_STATUS_FINAL.md` (comprehensive status report)
5. **Created:** `REGENERATION_STATUS_UPDATE.md` (this document)

---

## Decision Required

**Question:** How should we proceed with the remaining 105 OSCEs?

**Option A:** Modify completion script with better rate limiting (use Claude CLI)
- Pros: Honors user preference, reuses existing script
- Cons: Slower, more prone to rate limits

**Option B:** Install Anthropic SDK and use existing regeneration scripts
- Pros: Faster, comprehensive prompts, purpose-built
- Cons: Requires user approval to change SDK

**Option C:** Hybrid - Use Claude CLI with longer delays and overnight run
- Pros: Unattended execution, honors user preference
- Cons: Very slow (5+ hours)

---

**Awaiting user direction on preferred approach.**

**Report Prepared By:** Claude Code
**Session ID:** Continuation
**Status:** BLOCKED on rate limiting issue
