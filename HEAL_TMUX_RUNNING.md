# HEAL Download Running in Tmux

**Status:** 🟢 RUNNING
**Session:** `heal_download`
**Started:** 2026-02-03
**Phase:** Phase 1 (High-Priority)

---

## Current Download

**What's being downloaded:**
- **Hematology:** 50 topics × 10 images = 500 images
- **Dermatology:** 35 topics × 10 images = 350 images
- **Cardiology:** 35 topics × 10 images = 350 images

**Total:** 120 topics → ~1,200 images (estimated)

**Estimated time:** 50 minutes - 1.5 hours

**Log file:** `heal_download_phase1.log`

---

## Monitor Progress

### Option 1: Quick Status (Recommended)

```bash
./monitor_heal_download.sh
```

This shows:
- Recent output (last 30 lines)
- Progress from log file
- Downloaded files count
- Total size

### Option 2: Watch Live in Tmux

```bash
tmux attach -t heal_download
```

**To detach (leave running):** Press `Ctrl+B`, then press `D`

### Option 3: Watch Log File

```bash
tail -f heal_download_phase1.log
```

Press `Ctrl+C` to stop watching.

### Option 4: Check Downloaded Files

```bash
# Count images
find data/medical_images/heal -name "*.jpg" | wc -l

# Show folder structure
tree -L 3 data/medical_images/heal/ | head -50

# Check total size
du -sh data/medical_images/heal/

# List topics downloaded
ls data/medical_images/heal/hematology/
ls data/medical_images/heal/dermatology/
ls data/medical_images/heal/cardiology/
```

---

## Progress Tracking

### Real-Time Statistics

Run this command anytime:
```bash
./monitor_heal_download.sh
```

Example output:
```
✓ Tmux session 'heal_download' is running

Progress from log file:
  Total log lines: 187
  Topics completed: 3
  Download operations: 3

Downloaded so far:
  Images: 25 files
  Topic folders: 5
  Total size: 5.2M
```

### Expected Progress

| Time | Topics | Images | Size |
|------|--------|--------|------|
| 10 min | 12 | ~120 | ~30 MB |
| 20 min | 24 | ~240 | ~60 MB |
| 30 min | 36 | ~360 | ~90 MB |
| 40 min | 48 | ~480 | ~120 MB |
| 50 min | 60 | ~600 | ~150 MB |
| 1 hour | 72 | ~720 | ~180 MB |
| 1.5 hours | 120 | ~1,200 | ~300 MB |

---

## Commands Reference

### Monitor
```bash
# Quick status
./monitor_heal_download.sh

# Watch live (in tmux)
tmux attach -t heal_download
# Press Ctrl+B, then D to detach

# Follow log file
tail -f heal_download_phase1.log
```

### Check Files
```bash
# Count downloaded images
find data/medical_images/heal -name "*.jpg" | wc -l

# View structure
tree -L 3 data/medical_images/heal/

# Check size
du -sh data/medical_images/heal/

# List specialties
ls data/medical_images/heal/
```

### Manage Session
```bash
# List all tmux sessions
tmux list-sessions

# Attach to session
tmux attach -t heal_download

# Kill session (if needed)
tmux kill-session -t heal_download
```

---

## When Download Completes

The download will automatically complete and show a summary like:

```
======================================================================
BATCH DOWNLOAD COMPLETE!
======================================================================

Summary:
  Specialties: 3
  Topics: 120
  Images downloaded: 1,137
  Total time: 53m 24s
  Output: data/medical_images/heal

Breakdown:
  hematology: 482 images (50 topics)
  dermatology: 328 images (35 topics)
  cardiology: 327 images (35 topics)
```

### Next Steps After Completion

1. **Review Downloaded Images**
   ```bash
   ls -lh data/medical_images/heal/hematology/ | head -20
   ls -lh data/medical_images/heal/dermatology/ | head -20
   ls -lh data/medical_images/heal/cardiology/ | head -20
   ```

2. **Check Metadata**
   ```bash
   cat data/medical_images/heal/heal_comprehensive_metadata.json | jq '.total_images'
   ```

3. **Process Metadata**
   ```bash
   python3 scripts/process_image_metadata.py \
       --source data/medical_images/heal \
       --output data/heal_processed_metadata.json
   ```

4. **Enrich with Citations**
   ```bash
   python3 scripts/enrich_heal_metadata.py \
       --metadata data/heal_processed_metadata.json
   ```

5. **Upload to CDN**
   ```bash
   # Set credentials
   export R2_ENDPOINT_URL="https://<account-id>.r2.cloudflarestorage.com"
   export R2_ACCESS_KEY_ID="<your-key>"
   export R2_SECRET_ACCESS_KEY="<your-secret>"

   # Upload
   python3 scripts/upload_to_cdn.py \
       --source data/medical_images/heal \
       --bucket irstudy-medical-images \
       --metadata data/heal_processed_metadata.json
   ```

6. **Index in Database**
   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost/irstudy"

   python3 scripts/index_images.py \
       --metadata data/heal_processed_metadata.json
   ```

---

## Troubleshooting

### Download stopped/frozen

```bash
# Check if still running
tmux capture-pane -t heal_download -p | tail -20

# Attach and check
tmux attach -t heal_download

# If frozen, restart:
tmux kill-session -t heal_download
tmux new-session -s heal_download
source venv/bin/activate
./download_heal_comprehensive.sh --phase 1
```

### Can't attach to session

```bash
# List all sessions
tmux list-sessions

# If no sessions, download stopped
# Check log file for errors
tail -50 heal_download_phase1.log
```

### Errors in download

```bash
# Check log for errors
grep -i "error\|failed" heal_download_phase1.log

# Check which topics failed
grep "⚠ No results" heal_download_phase1.log
```

---

## Download Phases

### Currently Running: Phase 1 ✅

- ✅ Hematology (50 topics)
- ✅ Dermatology (35 topics)
- ✅ Cardiology (35 topics)

### After Phase 1 Completes

You can optionally run:

**Phase 2 (Medium-Priority):**
```bash
tmux new-session -s heal_phase2
source venv/bin/activate
./download_heal_comprehensive.sh --phase 2
```

This downloads:
- Anatomy (42 topics)
- Bone/Marrow (14 topics)
- Respiratory (10 topics)
- Pediatrics (10 topics)
- Pathology (20 topics)

**Phase 3 (Low-Priority):**
```bash
tmux new-session -s heal_phase3
source venv/bin/activate
./download_heal_comprehensive.sh --phase 3
```

This downloads:
- Gastrointestinal (8 topics)
- Infectious Disease (4 topics)

---

## Output Structure

```
data/medical_images/heal/
├── hematology/
│   ├── acute_myeloid_leukemia/
│   │   ├── heal_889318.jpg
│   │   ├── heal_889688.jpg
│   │   ├── acute_myeloid_leukemia_metadata.json
│   │   └── acute_myeloid_leukemia_metadata.csv
│   ├── sickle_cell_anemia/
│   ├── multiple_myeloma/
│   ├── ... (50 topics total)
│   └── hematology_summary.json
│
├── dermatology/
│   ├── melanoma/
│   ├── psoriasis/
│   ├── atopic_dermatitis/
│   ├── ... (35 topics total)
│   └── dermatology_summary.json
│
├── cardiology/
│   ├── atrial_fibrillation_ECG/
│   ├── ST_elevation_myocardial_infarction/
│   ├── left_bundle_branch_block/
│   ├── ... (35 topics total)
│   └── cardiology_summary.json
│
└── heal_comprehensive_metadata.json
```

---

## Quick Reference

**Monitor:** `./monitor_heal_download.sh`

**Watch live:** `tmux attach -t heal_download` (Ctrl+B, D to detach)

**View log:** `tail -f heal_download_phase1.log`

**Count images:** `find data/medical_images/heal -name "*.jpg" | wc -l`

**Check size:** `du -sh data/medical_images/heal/`

**Kill session:** `tmux kill-session -t heal_download`

---

## Status Updates

Check progress anytime:
```bash
./monitor_heal_download.sh
```

The download will continue running even if you:
- Close your terminal
- Disconnect from SSH
- Log out

To stop the download completely:
```bash
tmux kill-session -t heal_download
```

---

**Started:** 2026-02-03, ~13:00
**Expected completion:** 2026-02-03, ~14:00-14:30
**Estimated total:** 1,200 images, ~300 MB
