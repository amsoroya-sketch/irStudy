#!/bin/bash
# PRD_OSCE_003: Content analysis + screenshot extraction
# Usage: ./05_analyze.sh <SLUG>
set -uo pipefail

SLUG="$1"
PIPELINE_DIR="/home/dev/Development/irStudy/osce-pipeline"
OUTPUT_DIR="$PIPELINE_DIR/output/$SLUG"

# Run Python analysis
OSCE_BASE="$OUTPUT_DIR" OSCE_SLUG="$SLUG" python3 - << 'PYEOF'
import json, re, subprocess, os
from pathlib import Path

SLUG = os.environ["OSCE_SLUG"]
BASE = Path(os.environ["OSCE_BASE"])
transcript_file = BASE / "transcript.txt"

if not transcript_file.exists():
    print("ERROR: transcript.txt not found")
    exit(1)

transcript = transcript_file.read_text(encoding="utf-8")
lower = transcript.lower()

# Station type detection
scores = {"history_taking": 0, "physical_examination": 0, "communication": 0}

history_kw = ["history", "presenting complaint", "socrates", "hpc", "how long",
              "pain score", "systems review", "ddx", "differential", "symptoms",
              "onset", "duration", "character", "radiation", "timing"]
exam_kw = ["examine", "inspection", "palpation", "percussion", "auscultation",
           "findings", "tenderness", "reflexes", "signs", "mass", "lymph",
           "organomegaly", "bowel sounds", "hepatomegaly", "splenomegaly"]
comm_kw = ["counsel", "explain", "consent", "breaking bad", "discharge",
           "patient education", "ice", "concerns", "expectations", "address",
           "empathy", "understanding", "worried", "feelings"]

for kw in history_kw: scores["history_taking"] += lower.count(kw)
for kw in exam_kw: scores["physical_examination"] += lower.count(kw)
for kw in comm_kw: scores["communication"] += lower.count(kw)

station_type = max(scores, key=scores.get)

# Extract clinical entities
ddx_pattern = r'\b(cancer|carcinoma|gastritis|PUD|peptic ulcer|GORD|reflux|pancreatitis|' \
              r'cholecystitis|cholelithiasis|aortic|ectopic|appendicitis|IBS|IBD|Crohn|' \
              r'colitis|hepatitis|cirrhosis|pneumonia|pleurisy|MI|angina|PE|DVT|' \
              r'meningitis|SAH|stroke|epilepsy|asthma|COPD|heart failure)\b'
ddx_found = list(set(re.findall(ddx_pattern, transcript, re.IGNORECASE)))[:10]

inv_pattern = r'\b(FBC|UEC|LFT|CRP|ESR|AXR|CXR|CT|MRI|ultrasound|OGD|endoscopy|' \
              r'colonoscopy|ECG|troponin|lipase|amylase|H\.pylori|CLO test|' \
              r'urea breath|stool antigen|biopsy|ERCP|MRCP|PET|bone scan)\b'
inv_found = list(set(re.findall(inv_pattern, transcript, re.IGNORECASE)))[:10]

# Get video duration for screenshot interval
video_file = next(BASE.glob("video.*"), None)
duration_sec = 600  # default 10 min
if video_file:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_file)],
        capture_output=True, text=True
    )
    try:
        duration_sec = int(float(result.stdout.strip()))
    except:
        pass

if duration_sec < 300:
    interval = 30
elif duration_sec < 900:
    interval = 60
else:
    interval = 90

# First 200 words as presenting complaint context
first_section = " ".join(transcript.split()[:200])

analysis = {
    "slug": SLUG,
    "station_type": station_type,
    "station_scores": scores,
    "presenting_complaint": first_section,
    "ddx_mentioned": ddx_found,
    "investigations_mentioned": inv_found,
    "transcript_word_count": len(transcript.split()),
    "video_duration_sec": duration_sec,
    "screenshot_interval_sec": interval
}

with open(BASE / "analysis.json", "w") as f:
    json.dump(analysis, f, indent=2)

print(f"Station type: {station_type} (scores: {scores})")
print(f"DDx found: {ddx_found}")
print(f"Screenshot interval: {interval}s")
PYEOF

# Extract screenshots
VIDEO_FILE=$(ls "$OUTPUT_DIR"/video.* 2>/dev/null | grep -v "\.json$" | head -1)
INTERVAL=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/analysis.json'))['screenshot_interval_sec'])")

mkdir -p "$OUTPUT_DIR/screenshots"
echo "Extracting screenshots every ${INTERVAL}s..."
ffmpeg -i "$VIDEO_FILE" \
       -vf "fps=1/$INTERVAL" \
       "$OUTPUT_DIR/screenshots/screenshot_%04d.png" \
       -y -loglevel error

SCREENSHOT_COUNT=$(ls "$OUTPUT_DIR/screenshots/"*.png 2>/dev/null | wc -l)
echo "Screenshots extracted: $SCREENSHOT_COUNT"

# Write status
cat > "$OUTPUT_DIR/status.json" << EOF
{
  "step": "analyzed",
  "slug": "$SLUG",
  "updated_at": "$(date -Iseconds)"
}
EOF

echo "Analysis complete: $SLUG"
