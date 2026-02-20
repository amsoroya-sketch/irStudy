#!/bin/bash
# ============================================================
# OSCE Pipeline — Main Orchestrator
# PRD_OSCE_007: Batch Orchestrator
# Usage: ./scripts/run_pipeline.sh [--dry-run] [--resume]
# ============================================================

set -uo pipefail

PIPELINE_DIR="/home/dev/Development/irStudy/osce-pipeline"
CONFIG="$PIPELINE_DIR/config.yaml"
URLS_FILE="$PIPELINE_DIR/urls_clean.txt"
LOG="$PIPELINE_DIR/pipeline_log.txt"
PROGRESS="$PIPELINE_DIR/pipeline_progress.json"

# Read config values (simple YAML parsing)
WHISPER_VENV=$(grep "whisper_venv:" "$CONFIG" | awk '{print $2}' | tr -d '"')
MSDEV_VENV=$(grep "msdev_venv:" "$CONFIG" | awk '{print $2}' | tr -d '"')
OUTPUT_DIR=$(grep "output_dir:" "$CONFIG" | awk '{print $2}' | tr -d '"')

WHISPER_PYTHON="$WHISPER_VENV/bin/python"
MSDEV_PYTHON="$MSDEV_VENV/bin/python"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

echo "[$(date -Iseconds)] ============================================" | tee -a "$LOG"
echo "[$(date -Iseconds)] OSCE Pipeline starting" | tee -a "$LOG"
echo "[$(date -Iseconds)] URLs file: $URLS_FILE" | tee -a "$LOG"
[[ "$DRY_RUN" == "true" ]] && echo "[$(date -Iseconds)] DRY RUN MODE" | tee -a "$LOG"

# Count actual URLs (non-comment, non-empty lines)
TOTAL=$(grep -v '^\s*#' "$URLS_FILE" | grep -v '^\s*$' | wc -l || true)
DONE=0
FAILED=()

echo "[$(date -Iseconds)] Total videos to process: $TOTAL" | tee -a "$LOG"

# ============================================================
# Helper: run a single step
# ============================================================
run_step() {
    local STEP="$1"
    local SLUG="$2"
    local URL="${3:-}"

    [[ "$DRY_RUN" == "true" ]] && { echo "  [DRY-RUN] Would run: $STEP for $SLUG"; return 0; }

    echo "[$(date -Iseconds)]   Step: $STEP | Slug: $SLUG" | tee -a "$LOG"

    case "$STEP" in
        download)
            bash "$PIPELINE_DIR/scripts/02_download.sh" "$URL" "$SLUG" 2>>"$LOG"
            ;;
        transcribe)
            bash "$PIPELINE_DIR/scripts/03_transcribe.sh" "$SLUG" 2>>"$LOG"
            ;;
        analyze)
            bash "$PIPELINE_DIR/scripts/05_analyze.sh" "$SLUG" 2>>"$LOG"
            ;;
        enhance)
            bash "$PIPELINE_DIR/scripts/06_enhance.sh" "$SLUG" 2>>"$LOG"
            ;;
        diagrams)
            "$MSDEV_PYTHON" "$PIPELINE_DIR/scripts/07_diagrams.py" "$SLUG" 2>>"$LOG"
            ;;
        report)
            "$MSDEV_PYTHON" "$PIPELINE_DIR/scripts/08_assemble.py" "$SLUG" 2>>"$LOG"
            ;;
    esac
}

# ============================================================
# Load all URLs into array upfront (avoids while-read pipe corruption)
# ============================================================
mapfile -t URLS < "$URLS_FILE"

# ============================================================
# Main loop
# ============================================================
for URL in "${URLS[@]}"; do
    [[ -z "$URL" ]] && continue
    [[ "$URL" == \#* ]] && continue
    [[ "$URL" != https://* ]] && { echo "[$(date -Iseconds)] SKIP: $URL" | tee -a "$LOG"; continue; }

    echo "" | tee -a "$LOG"
    echo "[$(date -Iseconds)] Processing URL: $URL" | tee -a "$LOG"

    # Get slug — use yt-dlp directly in bash, pipe title to python for slug generation
    RAW_TITLE=$(yt-dlp --print "%(title)s" \
        --cookies-from-browser chrome \
        --js-runtimes node \
        --no-playlist \
        "$URL" 2>/dev/null || echo "")
    SLUG=$(echo "$RAW_TITLE" | python3 -c "
import sys, re
title = sys.stdin.read().strip()
slug = re.sub(r'[^a-z0-9_]', '', title.lower().replace(' ', '_'))[:60]
slug = re.sub(r'_+', '_', slug).strip('_')
print(slug)
" 2>/dev/null || echo "")

    if [ -z "$SLUG" ]; then
        # Fallback: use URL hash
        SLUG="video_$(echo "$URL" | md5sum | cut -c1-12)"
        echo "[$(date -Iseconds)]   WARNING: Could not get title, using slug: $SLUG" | tee -a "$LOG"
    fi

    OUTDIR="$OUTPUT_DIR/$SLUG"
    mkdir -p "$OUTDIR"

    STATUS_FILE="$OUTDIR/status.json"
    CURRENT_STEP="none"
    [ -f "$STATUS_FILE" ] && CURRENT_STEP=$(python3 -c "import json; d=json.load(open('$STATUS_FILE')); print(d.get('step','none'))" 2>/dev/null || echo "none")

    # Skip complete
    if [ "$CURRENT_STEP" == "complete" ]; then
        echo "[$(date -Iseconds)]   SKIP (complete): $SLUG" | tee -a "$LOG"
        DONE=$((DONE + 1))
        continue
    fi

    echo "[$(date -Iseconds)]   Slug: $SLUG | Resume from: $CURRENT_STEP" | tee -a "$LOG"

    # Update progress
    python3 -c "
import json, datetime
d = {'total': $TOTAL, 'done': $DONE, 'in_progress': '$SLUG', 'failed': [], 'updated_at': datetime.datetime.now().isoformat()}
json.dump(d, open('$PROGRESS', 'w'), indent=2)
" 2>/dev/null || true

    # Run each step (only if not already past it)
    STEPS=("download:downloaded" "transcribe:transcribed" "analyze:analyzed" "enhance:enhanced" "diagrams:diagrams" "report:complete")
    STEP_ORDER=("none" "downloaded" "transcribed" "analyzed" "enhanced" "diagrams" "complete")

    get_order() {
        local s="$1"
        for i in "${!STEP_ORDER[@]}"; do
            [[ "${STEP_ORDER[$i]}" == "$s" ]] && echo "$i" && return
        done
        echo "0"
    }

    CURRENT_IDX=$(get_order "$CURRENT_STEP")

    PIPELINE_FAILED=false
    for STEP_PAIR in "${STEPS[@]}"; do
        STEP_NAME="${STEP_PAIR%%:*}"
        STEP_DONE="${STEP_PAIR##*:}"

        DONE_IDX=$(get_order "$STEP_DONE")

        # Skip if already completed
        [ "$CURRENT_IDX" -ge "$DONE_IDX" ] && continue

        if ! run_step "$STEP_NAME" "$SLUG" "$URL"; then
            echo "[$(date -Iseconds)]   ERROR in step $STEP_NAME for $SLUG" | tee -a "$LOG"
            echo "{\"step\": \"error\", \"slug\": \"$SLUG\", \"error\": \"$STEP_NAME failed\", \"url\": \"$URL\"}" > "$STATUS_FILE"
            PIPELINE_FAILED=true
            break
        fi
    done

    if [ "$PIPELINE_FAILED" == "true" ]; then
        FAILED+=("$URL")
        echo "[$(date -Iseconds)]   FAILED: $SLUG" | tee -a "$LOG"
    else
        DONE=$((DONE + 1))
        echo "[$(date -Iseconds)]   COMPLETE: $SLUG ($DONE/$TOTAL)" | tee -a "$LOG"
        echo "RALPH_STATUS: COMPLETE | Video: $SLUG | Step: complete | Progress: $DONE/$TOTAL"
    fi

done

# ============================================================
# Final summary
# ============================================================
echo "" | tee -a "$LOG"
echo "[$(date -Iseconds)] ============================================" | tee -a "$LOG"
echo "[$(date -Iseconds)] BATCH COMPLETE: $DONE/$TOTAL done, ${#FAILED[@]} failed" | tee -a "$LOG"

for f in "${FAILED[@]}"; do
    echo "[$(date -Iseconds)]   FAILED URL: $f" | tee -a "$LOG"
done

# Update final progress
FAILED_JSON=$(printf '%s\n' "${FAILED[@]}" | python3 -c "import sys, json; print(json.dumps([l.rstrip() for l in sys.stdin]))" 2>/dev/null || echo "[]")
python3 -c "
import json, datetime
d = {'total': $TOTAL, 'done': $DONE, 'in_progress': None,
     'failed': $FAILED_JSON, 'updated_at': datetime.datetime.now().isoformat()}
json.dump(d, open('$PROGRESS', 'w'), indent=2)
" 2>/dev/null || true

# Generate master index
if [ "$DONE" -gt 0 ]; then
    echo "[$(date -Iseconds)] Generating master index..." | tee -a "$LOG"
    "$MSDEV_PYTHON" "$PIPELINE_DIR/scripts/09_index.py" 2>>"$LOG" || true
fi

echo "RALPH_STATUS: PIPELINE_COMPLETE | Total: $TOTAL | Done: $DONE | Failed: ${#FAILED[@]} | Index: osce-pipeline/index.html"
