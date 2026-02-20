# PRD_OSCE_004_KNOWLEDGE_ENHANCER

## R — Request

Use Ralph subagents (expert agents) to generate authoritative, enhanced clinical notes for each
OSCE station. Content must be presented as definitive clinical reference material aligned with
AMC Clinical Examination standards — NOT as a critique of any video.

**Context**: This is the intelligence layer. Expert agents expand on the raw transcript to
produce comprehensive, exam-ready clinical notes that exceed what the original video covers.

**Key Constraint**: NEVER reference the source video. NEVER say "the video mentions" or
"missing from the video". Present all content as canonical clinical knowledge.

---

## A — Architecture

### Expert Agent Selection by Station Type
```
history_taking      → history-taking-expert subagent
physical_examination → physical-examination-expert subagent
communication       → clinical-documentation-expert subagent
```

### Ralph Execution Pattern
Each expert agent runs as a Ralph subagent task with:
- Full transcript as context
- analysis.json data as structured input
- Explicit output format requirement
- AMC Clinical Examination framing

### Output Files Per Video
```
output/{slug}/
├── clinical_notes.md       ← comprehensive enhanced notes (authoritative)
├── key_facts.json          ← structured data for diagram generation
└── enhancement_log.txt     ← agent citations and sources
```

---

## L — Loop / Phases

### Phase 1: Prepare Agent Prompt
```python
# Load transcript + analysis
transcript = open(f"output/{SLUG}/transcript.txt").read()
analysis = json.load(open(f"output/{SLUG}/analysis.json"))
station_type = analysis["station_type"]
ddx = analysis["ddx_mentioned"]
investigations = analysis["investigations_mentioned"]

# Build prompt based on station type
if station_type == "history_taking":
    agent_prompt = f"""
    You are a history-taking-expert aligned with AMC Clinical Examination standards.

    TOPIC CONTEXT:
    - Transcript excerpt: {transcript[:3000]}
    - Differential diagnoses detected: {ddx}
    - Investigations mentioned: {investigations}

    TASK: Generate comprehensive AMC-standard clinical notes for this history-taking station.

    REQUIRED SECTIONS:
    1. Station Overview (presenting complaint, station type, time allocation)
    2. SOCRATES Assessment (full framework with clinical examples)
    3. Systematic History (HPC, PMHx, Medications, Allergies, FHx, SHx, ROS)
    4. Differential Diagnoses (top 3 with distinguishing features)
    5. Red Flags (list all with clinical significance)
    6. Relevant Investigations
    7. AMC Marking Criteria alignment
    8. Key Facts for AMC exam (bullet points)

    CONSTRAINTS:
    - Australian AMC standards only (no UK/US-specific references)
    - Do NOT mention any video or recording
    - Present as authoritative clinical reference
    - Include H. pylori testing where relevant to GI presentations
    - Include specific drug names (not brand names where possible)

    OUTPUT FORMAT: Structured Markdown with clear headings.
    """
```

### Phase 2: Ralph Subagent Execution
Ralph dispatches the expert agent task, receives clinical_notes.md, validates structure.

### Phase 3: Key Facts Extraction
```python
# Parse clinical_notes.md to extract structured data for diagrams
key_facts = {
    "station_type": station_type,
    "main_diagnosis": "",          # extracted from notes
    "differential_diagnoses": [],  # top 3 DDx with scores
    "red_flags": [],               # all red flags listed
    "investigations": [],          # ordered investigation list
    "socrates": {},                # SOCRATES components if history station
    "management_steps": [],        # management flow steps
    "amc_criteria": [],            # marking criteria points
    "domain_scores": {             # for radar chart
        "history_structure": 0,
        "clinical_reasoning": 0,
        "communication": 0,
        "differential_diagnosis": 0,
        "red_flags": 0,
        "investigations": 0,
        "management": 0,
        "patient_education": 0
    }
}
# Save to output/{slug}/key_facts.json
```

---

## P — Plan / Tasks

| Task | Agent | Acceptance Criterion |
|------|-------|---------------------|
| Dispatch expert agent | Ralph subagent | Returns structured Markdown |
| Validate notes format | Ralph PM | All required sections present |
| Extract key facts | Python parser | `key_facts.json` has all fields |
| Update status | bash | `status.json` shows step=enhanced |

---

## H — Handoff / Acceptance

### Done When:
- [ ] `clinical_notes.md` exists and has > 500 words
- [ ] All required sections present (SOCRATES, Red Flags, DDx, etc.)
- [ ] No video references in content ("video", "recording", "missing")
- [ ] `key_facts.json` valid JSON with all required fields
- [ ] `domain_scores` all populated (0–10 scale)
- [ ] `status.json` shows `"step": "enhanced"`

### Hands Off To: PRD_OSCE_005_DIAGRAM_GENERATOR
