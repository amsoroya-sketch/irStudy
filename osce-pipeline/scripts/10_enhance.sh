#!/bin/bash
# ============================================================
# OSCE Pipeline — Enhancement Script (v1)
# PRD_OSCE_007: Clinical Notes Generator
#
# For each valid slug:
#   1. Reads transcript.txt + analysis.json
#   2. Calls claude CLI with expert agent persona
#   3. Writes clinical_notes.md + key_facts.json
#   4. Re-runs 07_diagrams.py (4 diagrams, station-type aware)
#   5. Re-runs 08_assemble.py (text-first layout)
#
# Skips: thin transcripts (<750 words), failed slugs, already-enhanced slugs
#
# Usage: ./scripts/10_enhance.sh [--force] [--slug <slug>]
#   --force   : re-enhance even if clinical_notes.md already exists
#   --slug X  : only process single slug X
# ============================================================

set -uo pipefail

PIPELINE_DIR="/home/dev/Development/irStudy/osce-pipeline"
OUTPUT_DIR="$PIPELINE_DIR/output"
SCRIPTS_DIR="$PIPELINE_DIR/scripts"
LOG="$PIPELINE_DIR/enhance_log.txt"

MSDEV_VENV="/home/dev/Development/MSDev/Archive/docs/ai-agents/diagrams/venv"
MSDEV_PYTHON="$MSDEV_VENV/bin/python"

FORCE=false
SINGLE_SLUG=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force) FORCE=true; shift ;;
        --slug)  SINGLE_SLUG="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; shift ;;
    esac
done

# Slugs to permanently skip (thin transcripts + failed pipeline)
SKIP_SLUGS=(
    "2025_abdominal_pain_case_1516"    # 478 words
    "last_abdominal_pain_case_1616"    # 681 words
    "welcome_to_the_workshop_110"      # 738 words
    "video_7fffade6669f"               # pipeline failure, no transcript
)

is_skipped() {
    local slug="$1"
    for s in "${SKIP_SLUGS[@]}"; do
        [[ "$s" == "$slug" ]] && return 0
    done
    return 1
}

echo "[$(date -Iseconds)] ============================================" | tee -a "$LOG"
echo "[$(date -Iseconds)] OSCE Enhancement Pipeline starting" | tee -a "$LOG"
[[ "$FORCE" == "true" ]] && echo "[$(date -Iseconds)] FORCE mode: re-enhancing all" | tee -a "$LOG"

DONE=0
SKIPPED=0
FAILED=0

# ============================================================
# Expert agent prompt templates per station type
# ============================================================
build_prompt() {
    local station_type="$1"
    local transcript="$2"
    local analysis_json="$3"
    local slug="$4"

    local expert_role
    local expert_focus
    case "$station_type" in
        history_taking)
            expert_role="You are an expert clinical educator in Australian medical history taking, with BCBA-level knowledge of AMC Clinical Examination standards. You specialise in systematic history taking, SOCRATES methodology, and differential diagnosis for the Australian clinical context."
            expert_focus="Focus on: SOCRATES methodology, systematic history structure, differentials, red flags, ICE (Ideas Concerns Expectations), and Australian clinical practice standards."
            ;;
        physical_examination)
            expert_role="You are an expert clinical educator in Australian physical examination, with deep knowledge of AMC Clinical Examination standards. You specialise in systematic examination technique, clinical signs, and examination sequencing for the Australian clinical context."
            expert_focus="Focus on: systematic examination sequence, clinical signs and their significance, examination technique (inspection/palpation/percussion/auscultation), special tests, and interpretation of findings."
            ;;
        *)
            expert_role="You are an expert clinical educator in Australian medical communication and counselling, with deep knowledge of AMC Clinical Examination standards. You specialise in patient communication, breaking bad news, counselling frameworks, and shared decision making."
            expert_focus="Focus on: ICE framework (Ideas, Concerns, Expectations), patient-centred communication, information giving, shared decision making, health literacy, safety netting, and cultural sensitivity in the Australian clinical context."
            ;;
    esac

    cat << PROMPT_EOF
${expert_role}

Your task is to produce comprehensive AMC Clinical Examination study notes based on the teaching transcript provided below.

## STATION TYPE
${station_type//_/ } station — Australian Medical Council Clinical Examination

${expert_focus}

## CRITICAL INSTRUCTIONS
- Write in clear, precise clinical prose suitable for a published medical reference book
- Use Australian medical terminology and practice standards throughout
- Do NOT reference videos, recordings, transcripts, or any media
- Do NOT say "the video shows" or "as mentioned in the recording"
- Write as authoritative clinical notes, not a transcript summary
- Include concrete clinical examples, not abstract descriptions
- Use structured headings with specific clinical content under each
- All red flags, differentials, and management steps must be specific to this clinical scenario
- Do NOT include ICRP, USMLE, UK GMC, or non-Australian references
- AMC = Australian Medical Council (not American)
- Structure your output EXACTLY as specified in the OUTPUT FORMAT below

## ANALYSIS DATA (from automated pipeline)
\`\`\`json
${analysis_json}
\`\`\`

## SOURCE TRANSCRIPT
(This is a teaching video transcript. Extract the clinical content — ignore any meta-commentary about the video, exam tips about "watching the video", etc.)

\`\`\`
${transcript}
\`\`\`

## OUTPUT FORMAT (write EXACTLY this structure — no preamble, start directly with the H1)

# [Station Title]

## Clinical Presentation

[2-3 paragraphs describing the clinical scenario, what the patient presents with, and why this station is clinically important for AMC candidates. Be specific about the clinical context.]

## Station Framework — What the Examiner Expects

[Describe the structured approach required for this station type. For history taking: opening, systematic history, ICE, red flag screen, closing. For physical examination: preparation, inspection, palpation, percussion, auscultation, special tests. For communication: opening, ICE elicitation, information giving, shared decision making, safety netting.]

## Systematic Approach

### [First major subheading — e.g., "SOCRATES Assessment" / "Examination Sequence" / "ICE Framework"]

[Detailed clinical content with bullet points and prose. Be specific — include actual questions to ask, actual clinical signs to look for, actual information to provide.]

### [Second major subheading]

[Continue with systematic clinical content...]

### [Third major subheading]

[Continue...]

## Differential Diagnosis

[For history/PE stations: structured differential with Common / Important / Must-Not-Miss categories. For communication stations: key conditions or scenarios the patient may present, or management pathways.]

| Category | Diagnosis | Key Distinguishing Features |
|----------|-----------|----------------------------|
| Common | [diagnosis] | [features] |
| Common | [diagnosis] | [features] |
| Important | [diagnosis] | [features] |
| Must Not Miss | [diagnosis] | [features] |
| Must Not Miss | [diagnosis] | [features] |

## Red Flags — Must Not Miss

[List all clinically significant red flags for this presentation. Be specific:]

- **[Red flag 1]** — [why it matters clinically, what action to take]
- **[Red flag 2]** — [why it matters clinically, what action to take]
[Continue for all red flags...]

## Investigations

[Structured investigation plan:]

**Bedside:** [list]
**Bloods:** [list]
**Imaging:** [list]
**Specialist:** [list]

## Management

[Structured management approach appropriate to the station type and diagnosis. Include both acute and ongoing management.]

## Communication & Patient Education

[Key communication points for this clinical scenario: how to explain the diagnosis, what questions to expect, how to address patient concerns, written information to provide, follow-up plan.]

## AMC Exam Tips — High-Yield Points

[8-12 bullet points of specific, actionable exam tips based on common candidate mistakes for this type of station and presentation. Be specific to this clinical scenario, not generic advice.]

- [Specific tip 1]
- [Specific tip 2]
[Continue...]

## Safety Net

[Specific safety net instructions for this presentation: when to return to ED, red flag symptoms to watch for, follow-up timeline, written resources.]

PROMPT_EOF
}

# ============================================================
# Build key_facts.json from claude output
# ============================================================
extract_key_facts() {
    local slug="$1"
    local base="$OUTPUT_DIR/$slug"
    local notes_file="$base/clinical_notes.md"
    local analysis_file="$base/analysis.json"

    if [[ ! -f "$notes_file" ]]; then
        return 1
    fi

    OSCE_SLUG="$slug" OSCE_BASE="$base" python3 - << 'PYEOF'
import json, re, os
from pathlib import Path

BASE = Path(os.environ["OSCE_BASE"])
notes = (BASE / "clinical_notes.md").read_text(encoding="utf-8")
analysis = json.loads((BASE / "analysis.json").read_text()) if (BASE / "analysis.json").exists() else {}

def extract_list_under(heading_pattern, text, max_items=10):
    """Extract bullet list items under a heading."""
    pattern = rf"{heading_pattern}.*?\n((?:\s*[-*•]\s*.+\n?)+)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    items = []
    for line in match.group(1).split("\n"):
        line = line.strip().lstrip("-*•").strip()
        # Remove bold markers
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        # Remove em-dash and everything after (keep just the flag name)
        line = re.sub(r"\s*—.*$", "", line).strip()
        if line and len(line) > 3:
            items.append(line)
    return items[:max_items]

def extract_table_column(header_pattern, text, col_idx=1, max_items=10):
    """Extract items from a specific column of a markdown table."""
    items = []
    in_table = False
    header_found = False
    for line in text.split("\n"):
        if re.search(header_pattern, line, re.IGNORECASE):
            in_table = True
            header_found = True
            continue
        if in_table and header_found:
            if line.strip().startswith("|"):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) > col_idx and cells[col_idx] and cells[col_idx] != "---":
                    val = cells[col_idx].strip()
                    val = re.sub(r"\*\*(.*?)\*\*", r"\1", val)
                    if val and len(val) > 2 and "---" not in val:
                        items.append(val)
                        if len(items) >= max_items:
                            break
            elif line.strip() and not line.startswith("|"):
                in_table = False
    return items[:max_items]

def extract_section(heading, text, max_chars=2000):
    """Extract text of a section under a heading."""
    pattern = rf"##\s+{heading}.*?\n(.*?)(?=\n##\s|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()[:max_chars]
    return ""

# Extract key structured data from notes
red_flags = extract_list_under(r"##\s+Red Flags", notes)
amc_criteria = extract_list_under(r"##\s+AMC Exam Tips", notes)
ddx = extract_table_column(r"Diagnosis|Differential", notes, col_idx=1)
investigations_raw = extract_section("Investigations", notes)
management_raw = extract_section("Management", notes)

# Parse investigations
investigations = []
for line in investigations_raw.split("\n"):
    line = line.strip().lstrip("-*•").strip()
    line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
    if ":" in line:
        # e.g. "Bedside: urine, ECG, BSL" → split
        parts = line.split(":", 1)
        if len(parts) == 2:
            items = [i.strip() for i in parts[1].split(",") if i.strip()]
            investigations.extend(items[:4])
    elif len(line) > 3:
        investigations.append(line)
investigations = investigations[:12]

# Parse management steps
management_steps = []
for line in management_raw.split("\n"):
    line = line.strip()
    if re.match(r"^\d+\.", line):
        step = re.sub(r"^\d+\.\s*", "", line).strip()
        step = re.sub(r"\*\*(.*?)\*\*", r"\1", step)
        if step and len(step) > 3:
            management_steps.append(step)
    elif line.startswith(("-", "•", "*")) and len(line) > 5:
        step = line.lstrip("-*•").strip()
        step = re.sub(r"\*\*(.*?)\*\*", r"\1", step)
        if step:
            management_steps.append(step)
management_steps = management_steps[:8]

# Safety net
safety_net = extract_section("Safety Net", notes)

key_facts = {
    "red_flags": red_flags or analysis.get("red_flags_mentioned", []),
    "amc_criteria": amc_criteria,
    "differential_diagnoses": ddx or analysis.get("ddx_mentioned", []),
    "investigations": investigations or analysis.get("investigations_mentioned", []),
    "management_steps": management_steps,
    "safety_net": safety_net,
    "station_type": analysis.get("station_type", "history_taking"),
}

(BASE / "key_facts.json").write_text(json.dumps(key_facts, indent=2), encoding="utf-8")
print(f"  key_facts.json: {len(key_facts['red_flags'])} red flags, {len(key_facts['differential_diagnoses'])} DDx, {len(key_facts['amc_criteria'])} AMC tips")
PYEOF
}

# ============================================================
# Process a single slug
# ============================================================
process_slug() {
    local SLUG="$1"
    local BASE="$OUTPUT_DIR/$SLUG"

    echo "" | tee -a "$LOG"
    echo "[$(date -Iseconds)] Processing: $SLUG" | tee -a "$LOG"

    # Check skip list
    if is_skipped "$SLUG"; then
        echo "[$(date -Iseconds)]   SKIP (thin/failed): $SLUG" | tee -a "$LOG"
        SKIPPED=$((SKIPPED + 1))
        return 0
    fi

    # Check required files
    TRANSCRIPT="$BASE/transcript.txt"
    ANALYSIS="$BASE/analysis.json"

    if [[ ! -f "$TRANSCRIPT" ]]; then
        echo "[$(date -Iseconds)]   SKIP (no transcript): $SLUG" | tee -a "$LOG"
        SKIPPED=$((SKIPPED + 1))
        return 0
    fi

    if [[ ! -f "$ANALYSIS" ]]; then
        echo "[$(date -Iseconds)]   SKIP (no analysis.json): $SLUG" | tee -a "$LOG"
        SKIPPED=$((SKIPPED + 1))
        return 0
    fi

    # Check word count
    WORD_COUNT=$(wc -w < "$TRANSCRIPT")
    if [[ $WORD_COUNT -lt 750 ]]; then
        echo "[$(date -Iseconds)]   SKIP (${WORD_COUNT} words < 750 minimum): $SLUG" | tee -a "$LOG"
        SKIPPED=$((SKIPPED + 1))
        return 0
    fi

    # Check if already enhanced (unless --force)
    NOTES_FILE="$BASE/clinical_notes.md"
    if [[ -f "$NOTES_FILE" && "$FORCE" == "false" ]]; then
        NOTES_SIZE=$(wc -c < "$NOTES_FILE")
        if [[ $NOTES_SIZE -gt 2000 ]]; then
            echo "[$(date -Iseconds)]   SKIP (already enhanced, ${NOTES_SIZE} bytes): $SLUG" | tee -a "$LOG"
            # Still re-run diagrams + assemble to pick up new templates
            echo "[$(date -Iseconds)]   Re-running diagrams + assemble for: $SLUG" | tee -a "$LOG"
            run_diagrams_and_assemble "$SLUG"
            DONE=$((DONE + 1))
            return 0
        fi
    fi

    # Read station type and transcript
    STATION_TYPE=$(python3 -c "import json; d=json.load(open('$ANALYSIS')); print(d.get('station_type','history_taking'))" 2>/dev/null || echo "history_taking")
    TRANSCRIPT_TEXT=$(cat "$TRANSCRIPT")
    ANALYSIS_JSON=$(cat "$ANALYSIS")

    echo "[$(date -Iseconds)]   Station type: $STATION_TYPE | Words: $WORD_COUNT" | tee -a "$LOG"

    # Build prompt
    PROMPT=$(build_prompt "$STATION_TYPE" "$TRANSCRIPT_TEXT" "$ANALYSIS_JSON" "$SLUG")

    # Call claude CLI to generate clinical notes
    # Pipe prompt via stdin to handle large transcripts; use --system-prompt for persona
    echo "[$(date -Iseconds)]   Calling claude CLI for clinical notes..." | tee -a "$LOG"

    SYSTEM_PROMPT="You are an expert AMC Clinical Examination educator producing book-quality clinical reference notes for Australian medical graduates preparing for the AMC Clinical Examination. Write with clinical authority, precision, and educational depth. Never reference source media, videos, or recordings. Write as authoritative published clinical notes."

    if echo "$PROMPT" | claude -p \
              --model claude-sonnet-4-5-20250929 \
              --system-prompt "$SYSTEM_PROMPT" \
              > "$NOTES_FILE" 2>>"$LOG"; then

        NOTES_SIZE=$(wc -c < "$NOTES_FILE")
        if [[ $NOTES_SIZE -lt 1000 ]]; then
            echo "[$(date -Iseconds)]   ERROR: claude output too small (${NOTES_SIZE} bytes) for $SLUG" | tee -a "$LOG"
            rm -f "$NOTES_FILE"
            FAILED=$((FAILED + 1))
            return 1
        fi

        echo "[$(date -Iseconds)]   clinical_notes.md: ${NOTES_SIZE} bytes" | tee -a "$LOG"

        # Extract key_facts.json from the notes
        echo "[$(date -Iseconds)]   Extracting key_facts.json..." | tee -a "$LOG"
        extract_key_facts "$SLUG" 2>>"$LOG" || true

        # Re-run diagrams and assemble
        run_diagrams_and_assemble "$SLUG"

        DONE=$((DONE + 1))
        echo "[$(date -Iseconds)]   COMPLETE: $SLUG" | tee -a "$LOG"

    else
        echo "[$(date -Iseconds)]   ERROR: claude CLI failed for $SLUG" | tee -a "$LOG"
        rm -f "$NOTES_FILE"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

run_diagrams_and_assemble() {
    local SLUG="$1"
    local BASE="$OUTPUT_DIR/$SLUG"

    # Clear old diagrams so we start fresh with new 4-diagram templates
    rm -f "$BASE/diagrams/"*.png 2>/dev/null || true
    rm -f "$BASE/diagrams_manifest.json" 2>/dev/null || true

    echo "[$(date -Iseconds)]   Running 07_diagrams.py..." | tee -a "$LOG"
    if "$MSDEV_PYTHON" "$SCRIPTS_DIR/07_diagrams.py" "$SLUG" 2>>"$LOG"; then
        echo "[$(date -Iseconds)]   Running 08_assemble.py..." | tee -a "$LOG"
        "$MSDEV_PYTHON" "$SCRIPTS_DIR/08_assemble.py" "$SLUG" 2>>"$LOG" || true
    else
        echo "[$(date -Iseconds)]   WARNING: diagrams failed for $SLUG, assembling without" | tee -a "$LOG"
        "$MSDEV_PYTHON" "$SCRIPTS_DIR/08_assemble.py" "$SLUG" 2>>"$LOG" || true
    fi
}

# ============================================================
# Main execution
# ============================================================
if [[ -n "$SINGLE_SLUG" ]]; then
    # Single slug mode
    echo "[$(date -Iseconds)] Single slug mode: $SINGLE_SLUG" | tee -a "$LOG"
    process_slug "$SINGLE_SLUG" || true
else
    # Full batch — all slug directories
    TOTAL_SLUGS=$(find "$OUTPUT_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)
    echo "[$(date -Iseconds)] Total slug directories: $TOTAL_SLUGS" | tee -a "$LOG"

    for SLUG_DIR in "$OUTPUT_DIR"/*/; do
        SLUG=$(basename "$SLUG_DIR")
        process_slug "$SLUG" || true
    done
fi

# ============================================================
# Regenerate master index
# ============================================================
echo "" | tee -a "$LOG"
echo "[$(date -Iseconds)] Regenerating master index..." | tee -a "$LOG"
"$MSDEV_PYTHON" "$SCRIPTS_DIR/09_index.py" 2>>"$LOG" || true

# ============================================================
# Final summary
# ============================================================
echo "" | tee -a "$LOG"
echo "[$(date -Iseconds)] ============================================" | tee -a "$LOG"
echo "[$(date -Iseconds)] ENHANCEMENT COMPLETE: $DONE enhanced, $SKIPPED skipped, $FAILED failed" | tee -a "$LOG"
echo "RALPH_STATUS: ENHANCEMENT_COMPLETE | Enhanced: $DONE | Skipped: $SKIPPED | Failed: $FAILED"
