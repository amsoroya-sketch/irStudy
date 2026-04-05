# Overnight OSCE Regeneration - User Guide

**Started:** 2026-04-03 16:50 UTC
**Status:** ✅ RUNNING in background
**Estimated completion:** 2026-04-03 22:30 UTC (~5.5 hours)

---

## What's Running

Sequential regeneration of 106 OSCEs with improved rate limiting:

1. **Cardiology:** 50 OSCEs (~2.5 hours)
2. **Respiratory:** 50 OSCEs (~2.5 hours)
3. **Psychiatry Retry:** 6 failed OSCEs (~20 minutes)

**Rate limiting:** 5 seconds between Claude API calls (max 12 calls/min)

---

## How to Monitor Progress

### Quick Check
```bash
./monitor_regeneration.sh
```

Shows:
- Current progress (completed/failed counts)
- Estimated time remaining
- Last 20 log lines

### Live View (Attach to Session)
```bash
tmux attach -t osce-regen
```

To exit **without stopping** the process:
- Press `Ctrl+B`, then press `D` (detach)

To check if still running:
```bash
tmux list-sessions | grep osce-regen
```

---

## Files and Locations

### Log Directory
```
logs/osce_regeneration_20260403_165058/
├── Cardiology_165058.log       (Phase 1)
├── Respiratory_HHMMSS.log       (Phase 2)
├── Psychiatry_Retry_HHMMSS.log (Phase 3)
└── SUMMARY.txt                  (Final report)
```

### Output Files (Being Updated)
- `data/osces/cardiology_50_osces.json` (will grow from 164KB to ~800KB)
- `data/osces/respiratory_50_osces.json` (will grow from 174KB to ~900KB)
- `data/osces/psychiatry_40_osces_regenerated.json` (already 460KB, will add 6 more)

---

## Expected Timeline

| Phase | OSCEs | Duration | Start | End (Est) |
|-------|-------|----------|-------|-----------|
| **Cardiology** | 50 | 2.5 hrs | 16:50 | 19:20 |
| **Respiratory** | 50 | 2.5 hrs | 19:20 | 21:50 |
| **Psychiatry** | 6 | 20 min | 21:50 | 22:10 |

**Total:** ~5 hours 20 minutes

---

## What to Expect

### Success Indicators
- ✅ Log shows "Generated successfully" for most OSCEs
- ✅ File sizes increase significantly (164KB → 800KB)
- ✅ Summary shows high completion rate (>90%)

### Known Issues
- Some OSCEs may fail JSON extraction (~15% based on psychiatry run)
- These will be marked as "Generation failed - keeping NULL"
- Can be retried manually later

---

## When Complete

### 1. Check Summary
```bash
cat logs/osce_regeneration_20260403_165058/SUMMARY.txt
```

### 2. Validate Quality
```bash
# Check for placeholders (target: 0%)
python3 scripts/detect_placeholder_content.py data/osces/*_regenerated.json

# Spot check random OSCEs
python3 -c "import json; f=open('data/osces/cardiology_50_osces.json'); print(json.load(f)['osces'][0])" | head -50
```

### 3. Run Full Evaluation
```bash
python3 evaluation-system/run_evaluation.py --osces
```

Expected improvement:
- **Before:** 0.36/10 average (97.6% placeholders)
- **After:** >8.0/10 average (0-15% incomplete)

---

## Troubleshooting

### Session Disappeared
```bash
# Check if still running
tmux list-sessions

# If not listed, check if script completed
ls -lh logs/osce_regeneration_20260403_165058/SUMMARY.txt
```

### Script Stopped Early
```bash
# Check last log for errors
tail -n 50 logs/osce_regeneration_20260403_165058/*.log

# Resume manually from where it stopped
./run_overnight_regeneration.sh  # Will skip completed OSCEs
```

### Rate Limiting Issues
If seeing many "Claude CLI error" messages:
```bash
# Script already has 5-second delays
# If still failing, increase to 10 seconds:
# Edit scripts/complete_partial_osces.py line 368:
# Change: time.sleep(5)
# To: time.sleep(10)
```

---

## Manual Intervention (If Needed)

### Kill Session
```bash
tmux kill-session -t osce-regen
```

### Restart from Specific Phase
```bash
# Cardiology only
python3 scripts/complete_partial_osces.py \
    data/osces/cardiology_50_osces.json \
    data/osces/cardiology_50_osces.json \
    cardiology

# Respiratory only
python3 scripts/complete_partial_osces.py \
    data/osces/respiratory_50_osces.json \
    data/osces/respiratory_50_osces.json \
    respiratory

# Psychiatry retry only
python3 scripts/complete_partial_osces.py \
    data/osces/psychiatry_40_osces_regenerated.json \
    data/osces/psychiatry_40_osces.json \
    psychiatry
```

---

## Next Steps After Completion

1. **Review logs** for any systematic errors
2. **Validate** placeholder rate (target: <15%)
3. **Run evaluation** to confirm quality improvement
4. **Deploy** regenerated files to production
5. **Update documentation** with final statistics

---

## Scripts Created

1. `run_overnight_regeneration.sh` - Main sequential execution script
2. `monitor_regeneration.sh` - Progress monitoring
3. `scripts/complete_partial_osces.py` - Modified with 5s rate limiting

---

**Questions or Issues?**

Check the latest log file or attach to the tmux session for live progress.

**Last Updated:** 2026-04-03 16:50 UTC
