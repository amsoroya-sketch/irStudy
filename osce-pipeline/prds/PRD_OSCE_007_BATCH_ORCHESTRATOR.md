# PRD_OSCE_007_BATCH_ORCHESTRATOR

## R — Request

Orchestrate the full pipeline across all 34 YouTube videos sequentially. Track progress,
handle failures gracefully, support resume from any step, and report overall completion status.

**Context**: Ralph loop runs this orchestrator. Each video goes through PRD 001–006 in sequence.
A video is only marked complete when report.html + report.md both exist.

---

## A — Architecture

### Pipeline Flow Per Video
```
URL → Download (PRD001) → Transcribe (PRD002) → Analyze (PRD003)
    → Enhance (PRD004) → Diagrams (PRD005) → Report (PRD006) → DONE
```

### Resume Logic
Read `status.json` from each slug dir. Resume from last incomplete step:
```
step: "downloaded"   → start from PRD002
step: "transcribed"  → start from PRD003
step: "analyzed"     → start from PRD004
step: "enhanced"     → start from PRD005
step: "diagrams"     → start from PRD006
step: "complete"     → skip (already done)
(missing)            → start from PRD001 (download)
```

### Global State Files
```
osce-pipeline/
├── pipeline_progress.json   ← {total: 34, done: N, failed: [], in_progress: slug}
└── pipeline_log.txt         ← timestamped log of all actions
```

---

## L — Loop / Phases

### Phase 1: Read URL List
```bash
#!/bin/bash
PIPELINE_DIR="/home/dev/Development/irStudy/osce-pipeline"
URLS_FILE="$PIPELINE_DIR/urls.txt"
LOG="$PIPELINE_DIR/pipeline_log.txt"
PROGRESS="$PIPELINE_DIR/pipeline_progress.json"

# Count total
TOTAL=$(wc -l < "$URLS_FILE")
DONE=0
FAILED=()

echo "[$(date)] Starting batch pipeline for $TOTAL videos" >> "$LOG"
```

### Phase 2: Per-Video Loop
```bash
while IFS= read -r URL; do
    [ -z "$URL" ] && continue
    [[ "$URL" == \#* ]] && continue  # skip comments

    echo "[$(date)] Processing: $URL" >> "$LOG"

    # Get slug from yt-dlp
    SLUG=$(yt-dlp --print "%(title)s" "$URL" 2>/dev/null | \
           tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -dc 'a-z0-9_' | cut -c1-60)

    if [ -z "$SLUG" ]; then
        echo "[$(date)] ERROR: Could not get slug for $URL" >> "$LOG"
        FAILED+=("$URL")
        continue
    fi

    OUTDIR="$PIPELINE_DIR/output/$SLUG"
    STATUS_FILE="$OUTDIR/status.json"
    CURRENT_STEP="none"

    [ -f "$STATUS_FILE" ] && CURRENT_STEP=$(jq -r '.step // "none"' "$STATUS_FILE")

    # Skip if complete
    if [ "$CURRENT_STEP" == "complete" ]; then
        echo "[$(date)] SKIP (complete): $SLUG" >> "$LOG"
        DONE=$((DONE + 1))
        continue
    fi

    echo "[$(date)] Processing $SLUG from step: $CURRENT_STEP" >> "$LOG"

    # Update progress
    echo "{\"total\": $TOTAL, \"done\": $DONE, \"in_progress\": \"$SLUG\", \"failed\": []}" > "$PROGRESS"

    # Run pipeline steps
    run_step "download"    "$CURRENT_STEP" "$SLUG" "$URL" || { FAILED+=("$URL"); continue; }
    run_step "transcribe"  "$CURRENT_STEP" "$SLUG" "$URL" || { FAILED+=("$URL"); continue; }
    run_step "analyze"     "$CURRENT_STEP" "$SLUG" "$URL" || { FAILED+=("$URL"); continue; }
    run_step "enhance"     "$CURRENT_STEP" "$SLUG" "$URL" || { FAILED+=("$URL"); continue; }
    run_step "diagrams"    "$CURRENT_STEP" "$SLUG" "$URL" || { FAILED+=("$URL"); continue; }
    run_step "report"      "$CURRENT_STEP" "$SLUG" "$URL" || { FAILED+=("$URL"); continue; }

    DONE=$((DONE + 1))
    echo "[$(date)] COMPLETE: $SLUG ($DONE/$TOTAL)" >> "$LOG"

done < "$URLS_FILE"
```

### Phase 3: run_step Helper
```bash
run_step() {
    local STEP="$1"
    local CURRENT="$2"
    local SLUG="$3"
    local URL="$4"

    # Determine if step needs to run
    local STEP_ORDER=("download" "transcribe" "analyze" "enhance" "diagrams" "report")
    local STEP_DONE=("downloaded" "transcribed" "analyzed" "enhanced" "diagrams" "complete")

    # Map step name to completion marker
    local IDX; IDX=$(echo "${STEP_ORDER[@]}" | tr ' ' '\n' | grep -n "^$STEP$" | cut -d: -f1)
    IDX=$((IDX - 1))
    local DONE_MARKER="${STEP_DONE[$IDX]}"

    # Skip if already done
    [ "$CURRENT" == "$DONE_MARKER" ] && return 0

    echo "[$(date)]   Running step: $STEP for $SLUG" >> "$LOG"

    case "$STEP" in
        download)   bash "$PIPELINE_DIR/scripts/02_download.sh" "$URL" "$SLUG" ;;
        transcribe) bash "$PIPELINE_DIR/scripts/03_transcribe.sh" "$SLUG" ;;
        analyze)    bash "$PIPELINE_DIR/scripts/05_analyze.sh" "$SLUG" ;;
        enhance)    bash "$PIPELINE_DIR/scripts/06_enhance.sh" "$SLUG" ;;
        diagrams)   "$MSDEV_VENV/bin/python" "$PIPELINE_DIR/scripts/07_diagrams.py" "$SLUG" ;;
        report)     "$MSDEV_VENV/bin/python" "$PIPELINE_DIR/scripts/08_assemble.py" "$SLUG" ;;
    esac

    local EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        echo "[$(date)]   ERROR in step $STEP for $SLUG (exit: $EXIT_CODE)" >> "$LOG"
        return 1
    fi
    return 0
}
```

### Phase 4: Final Summary
```bash
echo "" >> "$LOG"
echo "[$(date)] BATCH COMPLETE" >> "$LOG"
echo "[$(date)] Done: $DONE/$TOTAL" >> "$LOG"
echo "[$(date)] Failed: ${#FAILED[@]}" >> "$LOG"
for f in "${FAILED[@]}"; do echo "  FAILED: $f" >> "$LOG"; done

# Update progress
FAILED_JSON=$(printf '%s\n' "${FAILED[@]}" | jq -R . | jq -s .)
echo "{\"total\": $TOTAL, \"done\": $DONE, \"in_progress\": null, \"failed\": $FAILED_JSON}" > "$PROGRESS"
```

---

## P — Plan / Tasks

| Task | Script | Acceptance Criterion |
|------|--------|---------------------|
| Setup orchestrator | `scripts/run_pipeline.sh` | Script exits 0 on dry-run |
| Process all 34 URLs | `run_pipeline.sh` | 34 entries in output/ |
| Handle failures | included | Failed URLs logged, pipeline continues |
| Resume support | included | Re-running picks up from last step |
| Final summary | included | `pipeline_progress.json` shows done=34 |

---

## H — Handoff / Acceptance

### Done When:
- [ ] `pipeline_progress.json` shows `"done": 34` (or shows remaining with failed list)
- [ ] Each of 34 slugs has `status.json` with `"step": "complete"`
- [ ] `pipeline_log.txt` has no unhandled errors
- [ ] Failed list in `pipeline_progress.json` is empty (or documented for retry)

### Hands Off To: PRD_OSCE_008_MASTER_INDEX
