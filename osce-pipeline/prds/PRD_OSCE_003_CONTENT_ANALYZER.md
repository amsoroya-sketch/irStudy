# PRD_OSCE_003_CONTENT_ANALYZER

## R — Request

Parse the Whisper transcript for each video to:
1. Detect the OSCE station type (History Taking / Physical Examination / Communication)
2. Extract clinical entities (symptoms, diagnoses, investigations, medications)
3. Identify the presenting complaint and main topic
4. Capture screenshots at key teaching moments

**Context**: Output of this PRD feeds the knowledge enhancer (PRD_004) with structured data.
Station type detection drives the diagram set selection in PRD_005.

---

## A — Architecture

### Components
1. **Station Type Classifier** — keyword/pattern matching on transcript
2. **Clinical Entity Extractor** — regex + keyword lists for symptoms, DDx, investigations
3. **Screenshot Capturer** — ffmpeg: extract frames every N seconds
4. **Analysis Writer** — saves `analysis.json` with all structured data

### Station Type Detection Rules
```
History Taking:   keywords = ["history", "presenting complaint", "SOCRATES", "HPC",
                               "how long", "what brought you", "pain score", "systems review"]
Physical Exam:    keywords = ["examine", "inspection", "palpation", "percussion",
                               "auscultation", "findings", "signs", "tenderness", "reflexes"]
Communication:    keywords = ["counsel", "explain", "breaking bad news", "consent",
                               "discharge", "patient education", "ICE", "concerns"]
```
Decision: whichever category has highest keyword match count.

### Screenshot Intervals by Duration
- Video < 5 min: every 30 seconds
- Video 5-15 min: every 60 seconds
- Video > 15 min: every 90 seconds

---

## L — Loop / Phases

### Phase 1: Transcript Analysis (Python script)
```python
import json, re
from pathlib import Path

SLUG = "$SLUG"
transcript = Path(f"output/{SLUG}/transcript.txt").read_text()

# Station type detection
station_scores = {
    "history_taking": 0,
    "physical_examination": 0,
    "communication": 0
}
history_kw = ["history", "presenting complaint", "socrates", "hpc",
              "how long", "pain score", "systems review", "ddx"]
exam_kw = ["examine", "inspection", "palpation", "percussion",
           "auscultation", "findings", "tenderness", "reflexes", "signs"]
comm_kw = ["counsel", "explain", "consent", "breaking bad", "discharge",
           "patient education", "ice", "concerns", "expectations"]

for kw in history_kw:
    station_scores["history_taking"] += transcript.lower().count(kw)
for kw in exam_kw:
    station_scores["physical_examination"] += transcript.lower().count(kw)
for kw in comm_kw:
    station_scores["communication"] += transcript.lower().count(kw)

station_type = max(station_scores, key=station_scores.get)

# Extract presenting complaint (first 200 words)
first_section = " ".join(transcript.split()[:200])

# Extract DDx candidates
ddx_pattern = r'\b(cancer|carcinoma|gastritis|PUD|peptic|GORD|pancreatitis|' \
              r'cholecystitis|aortic|ectopic|appendicitis|IBS|IBD|Crohn|colitis)\b'
ddx_found = list(set(re.findall(ddx_pattern, transcript, re.IGNORECASE)))

# Extract investigations mentioned
inv_pattern = r'\b(FBC|UEC|LFT|CRP|ESR|AXR|CXR|CT|MRI|ultrasound|endoscopy|' \
              r'colonoscopy|ECG|troponin|lipase|amylase|H\.pylori|CLO test)\b'
inv_found = list(set(re.findall(inv_pattern, transcript, re.IGNORECASE)))

analysis = {
    "slug": SLUG,
    "station_type": station_type,
    "station_scores": station_scores,
    "presenting_complaint": first_section,
    "ddx_mentioned": ddx_found,
    "investigations_mentioned": inv_found,
    "transcript_word_count": len(transcript.split()),
    "screenshot_interval_sec": 60
}

with open(f"output/{SLUG}/analysis.json", "w") as f:
    json.dump(analysis, f, indent=2)
```

### Phase 2: Screenshot Extraction
```bash
# Read interval from analysis.json
INTERVAL=$(jq '.screenshot_interval_sec' "output/$SLUG/analysis.json")
mkdir -p "output/$SLUG/screenshots"
ffmpeg -i "output/$SLUG/video.mp4" \
       -vf "fps=1/$INTERVAL" \
       "output/$SLUG/screenshots/screenshot_%04d.png" -y
```

### Phase 3: Update Status
```bash
jq '.step = "analyzed"' "output/$SLUG/status.json" > tmp.json && mv tmp.json "output/$SLUG/status.json"
```

---

## P — Plan / Tasks

| Task | Script | Acceptance Criterion |
|------|--------|---------------------|
| Classify station type | `scripts/05_analyze.sh` | `analysis.json` has valid `station_type` field |
| Extract clinical entities | included above | `ddx_mentioned` array populated |
| Capture screenshots | `scripts/05_analyze.sh` | `screenshots/` dir has > 3 PNG files |
| Update status | included | `status.json` shows step=analyzed |

---

## H — Handoff / Acceptance

### Done When:
- [ ] Each slug dir contains `analysis.json` with valid `station_type` (one of 3 values)
- [ ] `screenshots/` directory exists with PNG files
- [ ] `ddx_mentioned` and `investigations_mentioned` arrays populated (may be empty for comms stations)
- [ ] `status.json` shows `"step": "analyzed"`

### Hands Off To: PRD_OSCE_004_KNOWLEDGE_ENHANCER
