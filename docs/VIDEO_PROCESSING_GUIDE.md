# Video Processing Guide

Complete guide for extracting audio, generating transcripts, and capturing screenshots from presentation videos.

## Quick Start

```bash
# Basic usage (screenshots every 30 seconds)
./scripts/process_presentation_video.sh your_video.mp4

# Custom screenshot interval (every 60 seconds)
./scripts/process_presentation_video.sh your_video.mp4 60

# Process a specific file
./scripts/process_presentation_video.sh ~/Videos/lecture.mp4 45
```

## What It Does

The script automatically:

1. **Extracts Audio** - Converts video audio to high-quality WAV format (16kHz mono)
2. **Generates Transcripts** - Uses OpenAI Whisper AI to create:
   - Plain text transcript
   - Timestamped transcript (with start/end times for each segment)
   - JSON file with full metadata
3. **Captures Screenshots** - Takes screenshots at regular intervals
4. **Creates Summary** - Generates a markdown report with all details

## Output Structure

```
processed_[filename]_[timestamp]/
├── [filename]_audio.wav                    # Extracted audio
├── [filename]_transcript.txt               # Plain text transcript
├── [filename]_transcript_timestamped.txt   # With timestamps
├── [filename]_transcript.json              # Full JSON data
├── screenshots/                            # Screenshot folder
│   ├── screenshot_0001.png
│   ├── screenshot_0002.png
│   └── ...
└── SUMMARY.md                              # Processing summary
```

## Installation Requirements

### 1. FFmpeg (Already Installed)
```bash
# Verify installation
ffmpeg -version
```

### 2. OpenAI Whisper
The script will auto-install Whisper on first run, or install manually:

```bash
pip3 install openai-whisper
```

**Note:** First run will download the Whisper model (~140MB for base model).

### 3. Optional: Upgrade to Better Models

Whisper models (trade-off: speed vs accuracy):
- `tiny` - Fastest, least accurate (~39MB)
- `base` - Good balance (default, ~74MB)
- `small` - Better accuracy (~244MB)
- `medium` - High accuracy (~769MB)
- `large` - Best accuracy, slowest (~1550MB)

To use a different model, edit line 67 in the script:
```python
model = whisper.load_model("small")  # Change "base" to "small", "medium", etc.
```

## Use Cases

### Medical Education Videos
```bash
# Capture key slides every 2 minutes (120 seconds)
./scripts/process_presentation_video.sh lecture_cardiovascular_exam.mp4 120
```

### Clinical Demonstrations
```bash
# Frequent screenshots (every 15 seconds) for detailed procedures
./scripts/process_presentation_video.sh physical_exam_demo.mp4 15
```

### Long Presentations
```bash
# Less frequent screenshots (every 5 minutes = 300 seconds)
./scripts/process_presentation_video.sh full_conference_talk.mp4 300
```

## Tips

### 1. Screenshot Interval Selection
- **Detailed tutorials:** 10-20 seconds
- **Standard lectures:** 30-60 seconds
- **Long seminars:** 120-300 seconds

### 2. Transcript Quality
- Clear audio = better transcription
- Medical/technical terms may need manual review
- Check timestamped transcript for context

### 3. Performance
- **Processing time:** ~1-2x video duration for base model
- **Disk space:** Plan for ~500MB per hour of video (audio + screenshots + transcripts)

### 4. Batch Processing
Process multiple videos:

```bash
for video in ~/Videos/*.mp4; do
    ./scripts/process_presentation_video.sh "$video" 60
done
```

## Advanced Features

### Extract Specific Time Range
```bash
# Extract only 5:00 to 15:00 (5 to 15 minutes)
ffmpeg -i input.mp4 -ss 00:05:00 -to 00:15:00 -c copy segment.mp4
./scripts/process_presentation_video.sh segment.mp4 30
```

### Convert Transcript to SRT (Subtitles)
Use the JSON output with tools like:
- `whisper --task transcribe --output_format srt video.mp4`

### Search Transcript
```bash
# Find all mentions of "examination"
grep -i "examination" processed_*/transcript.txt
```

## Troubleshooting

### Issue: "Whisper not installed"
**Solution:** Script auto-installs, but if it fails:
```bash
pip3 install --upgrade openai-whisper
```

### Issue: "ffmpeg: command not found"
**Solution:** Install ffmpeg:
```bash
sudo apt update
sudo apt install ffmpeg
```

### Issue: Screenshots are blurry
**Solution:** Video resolution is low. Use higher quality source video.

### Issue: Transcript has errors
**Solution:**
1. Upgrade to `small` or `medium` model for better accuracy
2. Manually review and edit the `.txt` file
3. For medical terms, create a custom vocabulary list

### Issue: Processing is slow
**Solution:**
1. Use `tiny` or `base` model for faster processing
2. Process shorter video segments
3. Run on a machine with GPU support for 5-10x speedup

## Integration with irStudy

### For OSCE Video Content
1. Process instructional videos
2. Use screenshots for slide decks
3. Use transcripts for searchable content database
4. Link timestamps to specific learning objectives

### For EMR Training Videos
1. Capture key workflow screenshots
2. Generate documentation from transcripts
3. Create step-by-step guides with screenshots + text

### Citation Requirements
When using transcripts in educational content:
- Always cite original video source
- Include processing date
- Note AI-generated nature of transcript
- Manual review recommended for clinical accuracy

## Security Notes

- Videos may contain PHI (Protected Health Information)
- Process only de-identified educational content
- Store processed files securely
- Delete intermediate files (audio) if not needed
- Review transcripts before sharing publicly

---

**Script Location:** `/home/dev/Development/irStudy/scripts/process_presentation_video.sh`
**Last Updated:** 2026-02-16
