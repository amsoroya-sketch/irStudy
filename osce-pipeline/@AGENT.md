# @AGENT.md — OSCE Pipeline Ralph Autonomous Execution Rules

## Identity
You are the OSCE Pipeline Agent. Your job is to process OSCE teaching videos into
comprehensive AMC Clinical Examination study reports.

## Working Directory
```
/home/dev/Development/irStudy/osce-pipeline/
```

## Primary Input
```
urls.txt          — 34 YouTube URLs to process (one per line)
config.yaml       — pipeline settings (venv paths, model, intervals)
```

## PRD Sequence (execute in order per video)
```
PRD_OSCE_001 → PRD_OSCE_002 → PRD_OSCE_003 → PRD_OSCE_004
    → PRD_OSCE_005 → PRD_OSCE_006 → [loop to next video]
PRD_OSCE_007 → orchestrates the loop
PRD_OSCE_008 → run after all videos complete
```

## Execution Rules

### 1. Resume Logic (CRITICAL)
Before processing any video, check `output/{slug}/status.json`:
- `step: "complete"` → SKIP (already done)
- `step: "diagrams"` → resume from PRD_006
- `step: "enhanced"` → resume from PRD_005
- `step: "analyzed"` → resume from PRD_004
- `step: "transcribed"` → resume from PRD_003
- `step: "downloaded"` → resume from PRD_002
- missing file → start from PRD_001

### 2. Content Rules (MANDATORY)
- NEVER mention "video", "recording", "the presenter says", "missing from the video"
- ALL content is presented as authoritative clinical reference material
- Use AMC Clinical Examination standards (Australian context)
- Reference AMC Part 1 and Clinical Examination (NOT ICRP, NOT UK/US references)
- Include H. pylori in all upper GI history-taking stations

### 3. Expert Agent Delegation
For PRD_004, dispatch the correct expert agent:
```
history_taking       → Task(subagent_type="history-taking-expert")
physical_examination → Task(subagent_type="physical-examination-expert")
communication        → Task(subagent_type="clinical-documentation-expert")
```

### 4. Diagram Generation
For PRD_005, use MSDev venv:
```
VENV=/home/dev/Development/MSDev/Archive/docs/ai-agents/diagrams/venv
$VENV/bin/python scripts/07_diagrams.py {slug}
```
Diagrams count is dynamic (not fixed to 6). Generate all applicable diagrams from registry.

### 5. Error Handling
- Any step failure → log to `pipeline_log.txt` with timestamp
- Mark `status.json` with `"step": "error", "error": "description"`
- Continue to next video (do not halt entire pipeline)
- Log failed URLs for manual review

### 6. Status Updates
After each successful step, update `output/{slug}/status.json`:
```json
{
  "step": "downloaded|transcribed|analyzed|enhanced|diagrams|complete",
  "slug": "{slug}",
  "url": "{original_url}",
  "updated_at": "{ISO timestamp}"
}
```

## Success Criteria
```
@fix_plan.md — mark each URL as [x] complete when report.html + report.md exist
pipeline_progress.json — shows "done": 34
index.html — master index with all 34 reports accessible
```

## RALPH_STATUS Protocol
After completing each video, output:
```
RALPH_STATUS: COMPLETE | Video: {slug} | Step: complete | Progress: {N}/34
```

After all 34 complete:
```
RALPH_STATUS: PIPELINE_COMPLETE | Total: 34 | Failed: 0 | Index: osce-pipeline/index.html
```

## Key Paths Reference
```
Whisper venv:     ~/.venvs/whisper/bin/python
MSDev venv:       /home/dev/Development/MSDev/Archive/docs/ai-agents/diagrams/venv/bin/python
Process script:   /home/dev/Development/irStudy/scripts/process_presentation_video.sh
Output base:      /home/dev/Development/irStudy/osce-pipeline/output/
PRDs directory:   /home/dev/Development/irStudy/osce-pipeline/prds/
```
