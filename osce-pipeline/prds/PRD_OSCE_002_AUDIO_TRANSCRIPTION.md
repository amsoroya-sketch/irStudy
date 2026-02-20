# PRD_OSCE_002_AUDIO_TRANSCRIPTION

## R — Request

Extract audio from each downloaded video and generate a full transcript using OpenAI Whisper
running locally. Output must include plain transcript, timestamped transcript, and JSON data.

**Context**: Whisper is already installed in `~/.venvs/whisper` from earlier work.
Uses `base` model (139MB). No internet required after first model download.

---

## A — Architecture

### Components
1. **Audio Extractor** — ffmpeg: video.mp4 → audio.wav (16kHz mono, required by Whisper)
2. **Whisper Transcriber** — Python script using `~/.venvs/whisper` venv
3. **Output Writer** — saves 3 formats per video

### Venv Path
```
~/.venvs/whisper/bin/python
```

### Input/Output Per Video
```
output/{slug}/
├── video.mp4           ← input
├── audio.wav           ← extracted (16kHz mono)
├── transcript.txt      ← plain text, no timestamps
├── timestamped.txt     ← [HH:MM:SS] sentence format
└── transcript.json     ← full Whisper JSON with segments
```

---

## L — Loop / Phases

### Phase 1: Audio Extraction
```bash
ffmpeg -i "output/$SLUG/video.mp4" \
       -ar 16000 -ac 1 -c:a pcm_s16le \
       "output/$SLUG/audio.wav" -y
```

### Phase 2: Whisper Transcription
```python
#!/usr/bin/env python3
# Run with: ~/.venvs/whisper/bin/python

import whisper, json
from datetime import timedelta

SLUG = "$SLUG"
AUDIO = f"output/{SLUG}/audio.wav"

model = whisper.load_model("base")
result = model.transcribe(AUDIO, verbose=False)

# Plain transcript
with open(f"output/{SLUG}/transcript.txt", "w") as f:
    f.write(result["text"].strip())

# Timestamped transcript
with open(f"output/{SLUG}/timestamped.txt", "w") as f:
    for seg in result["segments"]:
        ts = str(timedelta(seconds=int(seg["start"])))
        f.write(f"[{ts}] {seg['text'].strip()}\n")

# Full JSON
with open(f"output/{SLUG}/transcript.json", "w") as f:
    json.dump(result, f, indent=2)
```

### Phase 3: Validation
- transcript.txt must be > 100 chars (non-empty transcription)
- timestamped.txt must have > 5 lines
- Update `status.json` → `{"step": "transcribed", ...}`

---

## P — Plan / Tasks

| Task | Script | Acceptance Criterion |
|------|--------|---------------------|
| Extract audio | `scripts/03_extract_audio.sh` | `audio.wav` exists, 16kHz mono |
| Run Whisper | `scripts/04_transcribe.sh` | `transcript.txt` > 100 chars |
| Validate output | included in script | All 3 files exist per slug |
| Update status | included in script | `status.json` shows step=transcribed |

---

## H — Handoff / Acceptance

### Done When:
- [ ] Each slug dir contains `audio.wav`, `transcript.txt`, `timestamped.txt`, `transcript.json`
- [ ] `wc -c transcript.txt` > 100 for each
- [ ] `status.json` shows `"step": "transcribed"`
- [ ] No Whisper errors in log

### Hands Off To: PRD_OSCE_003_CONTENT_ANALYZER
