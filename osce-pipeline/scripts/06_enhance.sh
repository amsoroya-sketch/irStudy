#!/bin/bash
# PRD_OSCE_004: Knowledge Enhancement via expert agent
# Usage: ./06_enhance.sh <SLUG>
# NOTE: This script prepares the prompt file for Ralph to dispatch to an expert agent.
#       Ralph reads enhance_prompt.md and dispatches the correct expert subagent.
set -uo pipefail

SLUG="$1"
PIPELINE_DIR="/home/dev/Development/irStudy/osce-pipeline"
OUTPUT_DIR="$PIPELINE_DIR/output/$SLUG"

TRANSCRIPT=$(cat "$OUTPUT_DIR/transcript.txt" 2>/dev/null || echo "")
ANALYSIS=$(cat "$OUTPUT_DIR/analysis.json" 2>/dev/null || echo "{}")
STATION_TYPE=$(python3 -c "import json; print(json.loads('$(echo $ANALYSIS | python3 -c "import sys; print(sys.stdin.read().replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))")' 2>/dev/null || echo '{}')').get('station_type', 'history_taking'))" 2>/dev/null || echo "history_taking")

# Map station type to expert agent
case "$STATION_TYPE" in
    physical_examination) AGENT="physical-examination-expert" ;;
    communication)        AGENT="clinical-documentation-expert" ;;
    *)                    AGENT="history-taking-expert" ;;
esac

echo "Station type: $STATION_TYPE"
echo "Expert agent: $AGENT"

# Generate enhancement prompt for Ralph
TRANSCRIPT_EXCERPT=$(head -c 3000 "$OUTPUT_DIR/transcript.txt" 2>/dev/null || echo "")
DDX=$(python3 -c "import json; d=json.load(open('$OUTPUT_DIR/analysis.json')); print(', '.join(d.get('ddx_mentioned', [])))" 2>/dev/null || echo "")
INV=$(python3 -c "import json; d=json.load(open('$OUTPUT_DIR/analysis.json')); print(', '.join(d.get('investigations_mentioned', [])))" 2>/dev/null || echo "")

cat > "$OUTPUT_DIR/enhance_prompt.md" << PROMPT_EOF
# Expert Enhancement Request

## Agent: $AGENT
## Station Type: $STATION_TYPE
## Slug: $SLUG

## Clinical Context
- Differentials detected: $DDX
- Investigations mentioned: $INV

## Transcript Excerpt
$TRANSCRIPT_EXCERPT

## Task

You are an expert clinical educator aligned with AMC Clinical Examination standards.

Generate comprehensive AMC-standard clinical notes for this OSCE station.

### REQUIRED SECTIONS:

1. **Station Overview**
   - Station type, presenting complaint, time allocation (8 minutes typical)

2. **SOCRATES Assessment** (for history stations)
   - Each component with clinical examples and what to ask

3. **Systematic History Framework**
   - HPC, PMHx, Medications (include H. pylori therapy where relevant), Allergies, FHx, SHx, Systems Review

4. **Differential Diagnoses** (top 3–5)
   - Each with distinguishing clinical features and likelihood

5. **Red Flags**
   - Full list with clinical significance and immediate actions

6. **Relevant Investigations**
   - Ordered by priority (bedside → bloods → imaging → endoscopy)

7. **Management Principles**
   - Initial, definitive, and safety-net

8. **AMC Marking Criteria Alignment**
   - What examiners specifically assess

9. **Key Facts for AMC Exam** (10 bullet points)
   - High-yield, exam-relevant facts

### CRITICAL CONSTRAINTS:
- Australian AMC standards ONLY
- NEVER mention "video", "recording", "the video says", "missing"
- Present all content as authoritative clinical reference
- Use Australian drug names and guidelines
- Include specific examples and clinical pearls

### OUTPUT FORMAT:
Structured Markdown saved to: $OUTPUT_DIR/clinical_notes.md
Also save structured JSON to: $OUTPUT_DIR/key_facts.json

### key_facts.json must contain:
\`\`\`json
{
  "station_type": "$STATION_TYPE",
  "main_diagnosis": "",
  "differential_diagnoses": [],
  "red_flags": [],
  "investigations": [],
  "management_steps": [],
  "amc_criteria": [],
  "domain_scores": {
    "history_structure": 8,
    "clinical_reasoning": 8,
    "communication": 7,
    "differential_diagnosis": 8,
    "red_flags": 7,
    "investigations": 8,
    "management": 7,
    "patient_education": 7
  }
}
\`\`\`
PROMPT_EOF

echo "Enhancement prompt written to: $OUTPUT_DIR/enhance_prompt.md"
echo "Ralph should dispatch: $AGENT subagent with this prompt"

# If running under Ralph, the agent will pick up enhance_prompt.md automatically.
# For standalone testing, output the instruction:
echo ""
echo "RALPH_INSTRUCTION: Dispatch $AGENT subagent with prompt from $OUTPUT_DIR/enhance_prompt.md"
echo "RALPH_INSTRUCTION: Write output to $OUTPUT_DIR/clinical_notes.md and $OUTPUT_DIR/key_facts.json"

# Write status (Ralph updates this to 'enhanced' after agent completes)
cat > "$OUTPUT_DIR/status.json" << EOF
{
  "step": "enhancing",
  "slug": "$SLUG",
  "agent": "$AGENT",
  "updated_at": "$(date -Iseconds)"
}
EOF
