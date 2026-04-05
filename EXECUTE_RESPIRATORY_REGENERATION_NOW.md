# 🚀 EXECUTE RESPIRATORY OSCE REGENERATION - QUICK START

## TL;DR - Run These Commands

```bash
cd /home/dev/Development/irStudy

# Step 1: Make scripts executable
chmod +x validate_prerequisites.sh run_respiratory_regeneration.sh

# Step 2: Validate prerequisites (30 seconds)
./validate_prerequisites.sh

# Step 3: If validation passes, execute regeneration (100-150 minutes)
./run_respiratory_regeneration.sh
```

## What Will Happen

1. **Validation (30 seconds):**
   - Checks input file exists
   - Verifies Python 3.8+ installed
   - Confirms API key configured
   - Validates directory permissions

2. **Regeneration (100-150 minutes):**
   - Generates 50 respiratory OSCEs with real clinical content
   - Each OSCE takes 2-3 minutes
   - Progress will be shown in terminal
   - Output file: `data/osces/respiratory_50_osces_regenerated.json`

3. **Validation (automatic):**
   - Checks JSON structure
   - Counts OSCEs (must be 50)
   - Runs 8 quality gates
   - Spot checks 3 random OSCEs
   - Reports placeholder rate (must be 0%)

## Expected Results

### Before (Current State)
- Placeholder rate: **100%**
- Content: Generic templates
- Example: *"A patient presents for respiratory assessment"*

### After (Target State)
- Placeholder rate: **0%**
- Content: Specific clinical scenarios with:
  - Complete patient demographics and backstory
  - Specific spirometry values (FEV1/FVC with % predicted)
  - Correct oxygen targets (88-92% for COPD, 94-98% for non-COPD)
  - Inhaler devices with technique (MDI, Turbuhaler, etc.)
  - Medications with doses and PBS codes
  - Australian guidelines (COPD-X, National Asthma Council, TSANZ)

## Quality Gates (ALL MUST PASS)

After regeneration, the script will automatically check:

| Gate | Requirement | Target | Critical |
|------|-------------|--------|----------|
| 1 | Spirometry values (FEV1/FVC) | ≥40 OSCEs | ⚠️ High |
| 2 | Oxygen targets (88-92% vs 94-98%) | ≥30 OSCEs | 🔴 CRITICAL |
| 3 | Inhaler devices (MDI/Turbuhaler/etc) | ≥25 OSCEs | ⚠️ High |
| 4 | PBS codes | ≥100 codes | ⚠️ High |
| 5 | Australian guidelines | ≥40 references | ⚠️ High |
| 6 | Severity classification | All OSCEs | Standard |
| 7 | Zero placeholder content | 0% rate | 🔴 CRITICAL |
| 8 | Complete structure (17 fields) | All OSCEs | Standard |

## Monitoring Progress

Open a second terminal to watch progress:

```bash
cd /home/dev/Development/irStudy

# Watch file size grow
watch -n 30 'ls -lh data/osces/respiratory_50_osces_regenerated.json 2>/dev/null || echo "Not created yet"'
```

Expected file size progression:
- Start: File doesn't exist
- After 10 OSCEs: ~100 KB
- After 25 OSCEs: ~250 KB
- After 50 OSCEs: ~500 KB (final)

## If Something Goes Wrong

### Problem: Prerequisites fail
```bash
# Check the error message from validate_prerequisites.sh
# Fix the specific issue (missing file, wrong Python version, no API key, etc.)
# Re-run validation
./validate_prerequisites.sh
```

### Problem: Regeneration fails mid-way
```bash
# Check how many OSCEs were generated
python3 -c "import json; data = json.load(open('data/osces/respiratory_50_osces_regenerated.json')); print(len(data.get('osces', [])))"

# If partial success (e.g., 30/50 OSCEs), you can:
# 1. Review the logs for error patterns
# 2. Wait 1 minute (rate limit reset)
# 3. Re-run the script (it should continue from where it failed if designed to do so)
```

### Problem: Quality gates fail
```bash
# The script will show which gate(s) failed
# Example: "Spirometry mentions found: 25 (FAIL, ≥40 required)"

# Check specific content:
grep -B5 -A5 "FEV1" data/osces/respiratory_50_osces_regenerated.json | head -50

# If widespread failure, may need to adjust generation prompt and re-run
```

## Deployment (After All Gates Pass)

Once regeneration is complete and all quality gates pass:

```bash
# Backup original
cp data/osces/respiratory_50_osces.json \
   data/osces/respiratory_50_osces_backup_$(date +%Y%m%d_%H%M%S).json

# Deploy regenerated version
cp data/osces/respiratory_50_osces_regenerated.json \
   data/osces/respiratory_50_osces.json

echo "✓ Respiratory OSCEs regenerated and deployed"
```

## Documentation

For more details, see:
- **Full Guide:** `RESPIRATORY_REGENERATION_EXECUTION_GUIDE.md`
- **Status:** `RESPIRATORY_REGENERATION_STATUS.md`

## Timeline

| Stage | Duration | Notes |
|-------|----------|-------|
| Prerequisites | 30 seconds | Run validate_prerequisites.sh |
| Regeneration | 100-150 min | Run run_respiratory_regeneration.sh |
| Validation | 2 minutes | Automatic (part of regeneration script) |
| Review | 5-10 minutes | Manual spot check of sample OSCEs |
| **TOTAL** | **~2.5 hours** | Mostly automated waiting |

## Success Confirmation

You'll know it worked when you see:

```
========================================
VALIDATION COMPLETE
========================================

✓ File created: respiratory_50_osces_regenerated.json
✓ JSON valid
✓ Count: 50 OSCEs
✓ Placeholder rate: 0%
✓ Spirometry: 43 matches (PASS)
✓ Oxygen targets: 35 matches (PASS)
✓ Inhaler devices: 28 matches (PASS)
✓ PBS codes: 124 matches (PASS)
✓ Australian guidelines: 47 matches (PASS)

All quality gates PASSED.
Ready for deployment.
```

## Ready to Start?

Run these commands now:

```bash
cd /home/dev/Development/irStudy
chmod +x validate_prerequisites.sh run_respiratory_regeneration.sh
./validate_prerequisites.sh && ./run_respiratory_regeneration.sh
```

The `&&` ensures regeneration only starts if prerequisites pass.

---

**Last Updated:** 2026-03-29
**Estimated Total Time:** 2.5 hours
**Difficulty:** Low (fully automated)
**Risk:** Low (creates new file, doesn't modify original)

**GO FOR IT! 🚀**
