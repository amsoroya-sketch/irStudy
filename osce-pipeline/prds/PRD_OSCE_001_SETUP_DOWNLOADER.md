# PRD_OSCE_001_SETUP_DOWNLOADER

## R — Request

Set up the OSCE pipeline environment and download all 34 YouTube videos for offline processing.
This PRD handles one-time setup (dependencies) and per-video download tasks.

**Context**: 34 MG4MGS OSCE teaching videos covering history taking, physical examination, and
communication stations. Videos are public YouTube content. Processing is local-only.

---

## A — Architecture

### Components
1. **Dependency Installer** — yt-dlp, ffmpeg (should already exist), jq
2. **Video Downloader** — yt-dlp wrapper with retry logic
3. **Directory Scaffolding** — creates per-video output folders
4. **Metadata Extractor** — pulls title, duration, upload date from yt-dlp JSON

### Directory Layout
```
osce-pipeline/
├── urls.txt                    ← 34 YouTube URLs (one per line)
├── config.yaml                 ← pipeline settings
├── output/
│   └── {topic_slug}/           ← created per video
│       ├── video.mp4
│       ├── metadata.json
│       └── status.json
├── prds/                       ← this directory
├── scripts/                    ← processing scripts
└── templates/                  ← HTML/Markdown templates
```

### Naming Convention
Topic slug = yt-dlp title → lowercase → spaces to underscores → truncate to 60 chars
Example: `upper_abdominal_pain_osce_history_taking_mg4mgs`

---

## L — Loop / Phases

### Phase 1: Environment Setup (run once)
```bash
# Install yt-dlp (system-wide via pipx or user-level)
pipx install yt-dlp || pip3 install --user yt-dlp

# Verify ffmpeg available
ffmpeg -version | head -1

# Verify jq available (for JSON parsing)
jq --version
```

### Phase 2: Per-Video Download
```bash
# For each URL in urls.txt:
SLUG=$(yt-dlp --print "%(title)s" "$URL" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | cut -c1-60)
mkdir -p "osce-pipeline/output/$SLUG"
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]" \
       --write-info-json \
       --output "osce-pipeline/output/$SLUG/video.%(ext)s" \
       "$URL"
# Extract metadata
cp "osce-pipeline/output/$SLUG/video.info.json" "osce-pipeline/output/$SLUG/metadata.json"
```

### Phase 3: Validate Downloads
- Confirm each output dir has `video.mp4` > 1MB
- Write `status.json` with `{"step": "downloaded", "slug": "...", "url": "..."}`

---

## P — Plan / Tasks

| Task | Script | Acceptance Criterion |
|------|--------|---------------------|
| Install yt-dlp | `scripts/01_setup.sh` | `yt-dlp --version` exits 0 |
| Create output dirs | auto in download script | 34 dirs exist |
| Download all videos | `scripts/02_download.sh` | 34 `video.mp4` files exist, each > 1MB |
| Extract metadata | included in download | 34 `metadata.json` files exist |
| Write status files | included in download | 34 `status.json` with step=downloaded |

---

## H — Handoff / Acceptance

### Done When:
- [ ] `yt-dlp --version` outputs version string
- [ ] `ls osce-pipeline/output/ | wc -l` == 34
- [ ] Each dir contains `video.mp4`, `metadata.json`, `status.json`
- [ ] No download errors in log
- [ ] `status.json` in each dir shows `"step": "downloaded"`

### Hands Off To: PRD_OSCE_002_AUDIO_TRANSCRIPTION
