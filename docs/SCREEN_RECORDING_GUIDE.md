# Screen Recording Guide for YouTube Videos

Complete guide for recording YouTube videos (or any screen content) when you don't have direct access to download the video.

## Quick Start

### Option 1: Simple Screen Recording
```bash
# Record entire screen
./scripts/record_screen.sh my_recording.mp4
```

### Option 2: Advanced YouTube Recording
```bash
# Auto-detect browser window
./scripts/record_youtube.sh window youtube_lecture.mp4

# Record full screen
./scripts/record_youtube.sh fullscreen my_video.mp4

# Select specific region
./scripts/record_youtube.sh region custom_area.mp4
```

## Installation

First-time setup (installs required tools):

```bash
./scripts/install_recording_tools.sh
```

This installs:
- **ffmpeg** - Video recording engine
- **xdotool** - Window detection
- **x11-utils** - Screen information
- **pulseaudio-utils** - Audio capture

## Recording Modes

### 1. Window Mode (Recommended for YouTube)
Records only the browser window containing YouTube.

```bash
./scripts/record_youtube.sh window lecture.mp4
```

**Advantages:**
- Smaller file size
- No desktop clutter
- Focuses on video content only
- Auto-detects browser

**How it works:**
1. Script searches for browser windows (Chrome, Firefox)
2. You confirm the window (5 second delay)
3. Recording captures only that window
4. Press Ctrl+C to stop

### 2. Full Screen Mode
Records your entire screen.

```bash
./scripts/record_youtube.sh fullscreen presentation.mp4
```

**Use when:**
- Switching between multiple windows
- Recording entire workflow
- Capturing desktop demonstrations

### 3. Region Mode
Select a specific area to record.

```bash
./scripts/record_youtube.sh region custom.mp4
```

**How it works:**
1. Script prompts you to select region
2. Click and drag to select area
3. Recording captures only that region

**Use when:**
- Recording just the video player (not browser UI)
- Capturing specific sections
- Multiple monitors (select one)

## Complete Workflow

### Recording YouTube Educational Content

**Step 1: Prepare**
```bash
# Create dedicated recording directory (optional)
mkdir -p ~/Videos/medical_lectures

# Open YouTube video in browser
google-chrome https://youtube.com/watch?v=VIDEO_ID
# or
firefox https://youtube.com/watch?v=VIDEO_ID
```

**Step 2: Start Recording**
```bash
cd /home/dev/Development/irStudy

# Use window mode for clean recording
./scripts/record_youtube.sh window ~/Videos/medical_lectures/cardiovascular_exam.mp4
```

**Step 3: During Recording**
1. Script starts (wait for "REC" indicator)
2. Switch to browser with YouTube
3. Play the video at desired quality (1080p recommended)
4. Let video play completely
5. Return to terminal and press **Ctrl+C** to stop

**Step 4: Process Recording**
```bash
# Extract audio, generate transcripts, capture screenshots
./scripts/process_presentation_video.sh ~/Videos/medical_lectures/cardiovascular_exam.mp4 60
```

This creates:
- Audio file (WAV)
- Transcripts (text, timestamped, JSON)
- Screenshots every 60 seconds
- Summary report

## Audio Capture

The scripts automatically capture **system audio** (what you hear from YouTube).

### Audio Source Detection

1. **Automatic** - Script finds monitor source (system output)
2. **Manual** - If auto-detection fails:

```bash
# List available audio sources
pactl list sources short

# Use specific source
./scripts/record_screen.sh my_video.mp4 alsa_output.pci-0000_00_1f.3.analog-stereo.monitor
```

### Testing Audio

```bash
# Test system audio before recording
pactl list sources short | grep monitor

# If no monitor found, enable loopback:
pactl load-module module-loopback
```

### Troubleshooting Audio

**Issue: No audio in recording**

**Solution 1** - Check PulseAudio:
```bash
# Restart PulseAudio
pulseaudio --kill
pulseaudio --start
```

**Solution 2** - Use pavucontrol:
```bash
# Install PulseAudio Volume Control
sudo apt install pavucontrol

# Run it
pavucontrol

# Go to "Recording" tab while recording
# Select "Monitor of [your output device]"
```

**Solution 3** - Record with specific source:
```bash
# Find your monitor
pactl list sources | grep -A 5 "Monitor"

# Use the source name
./scripts/record_screen.sh video.mp4 alsa_output.your_device.monitor
```

## Recording Quality Settings

### Current Settings (in scripts)

- **Video Codec:** H.264 (libx264)
- **Preset:** ultrafast (low CPU usage during recording)
- **Quality (CRF):** 23 (good balance, lower = better quality)
- **Frame Rate:** 30 fps
- **Audio Codec:** AAC
- **Audio Bitrate:** 192 kbps

### Modify for Higher Quality

Edit the script and change:

```bash
# Higher quality (larger files)
-crf 18  # Default is 23

# Better compression (slower recording)
-preset fast  # Default is ultrafast

# Higher frame rate
-framerate 60  # Default is 30
```

### Modify for Smaller Files

```bash
# Lower quality (smaller files)
-crf 28

# Lower resolution
-video_size 1280x720  # Record at 720p instead of native
```

## Tips for Best Results

### 1. YouTube Video Quality
Set YouTube to highest quality:
- Click gear icon → Quality → 1080p or higher
- Disable autoplay (prevents interruptions)

### 2. Browser Setup
- Use full-screen mode (F key on YouTube)
- Disable browser extensions that overlay UI
- Close unnecessary tabs (reduces lag)

### 3. System Performance
- Close heavy applications
- Ensure sufficient disk space (1GB per 10 minutes of recording)
- Use SSD if available (faster writes)

### 4. Recording Environment
- Use wired internet (prevents buffering)
- Pause other downloads
- Disable notifications:
  ```bash
  # Enable "Do Not Disturb" in system settings
  ```

### 5. File Management
Recordings are saved to: `~/Videos/recordings/`

```bash
# Check disk space before recording
df -h ~/Videos

# Move recordings to project folder
mv ~/Videos/recordings/lecture.mp4 /home/dev/Development/irStudy/videos/
```

## Common Use Cases

### Use Case 1: Medical Lecture Series
```bash
#!/bin/bash
# Record entire lecture series

LECTURES=(
    "cardiovascular_examination"
    "respiratory_examination"
    "neurological_examination"
)

for lecture in "${LECTURES[@]}"; do
    echo "Ready to record: $lecture"
    read -p "Press Enter when YouTube video is ready..."

    ./scripts/record_youtube.sh window "$lecture.mp4"

    echo "Processing $lecture..."
    ./scripts/process_presentation_video.sh ~/Videos/recordings/"$lecture.mp4" 120

    echo "Completed: $lecture"
    echo "---"
done
```

### Use Case 2: Quick Clips
```bash
# Record short segment
./scripts/record_youtube.sh window quick_demo.mp4

# After 2 minutes, press Ctrl+C

# Extract just the audio and transcript
./scripts/process_presentation_video.sh ~/Videos/recordings/quick_demo.mp4
```

### Use Case 3: Multi-Monitor Setup
```bash
# Select specific monitor/region
./scripts/record_youtube.sh region monitor2_video.mp4

# Click on the monitor you want to record
```

## Integration with irStudy Platform

### For OSCE Training Content
1. Record clinical examination demonstrations
2. Process to extract teaching points (transcripts)
3. Use screenshots for step-by-step guides
4. Link to OSCE station content

### For EMR Training Videos
1. Record EHR workflow demonstrations
2. Extract transcripts for documentation
3. Create visual guides from screenshots
4. Build training modules

### Citation and Compliance
When using recorded YouTube content:

**Legal Requirements:**
- Only record for personal educational use
- Respect copyright and YouTube Terms of Service
- Do not redistribute recorded content
- Cite original video source

**For irStudy Platform:**
```markdown
**Source:** [Video Title] by [Creator]
**Original URL:** https://youtube.com/watch?v=VIDEO_ID
**Recorded:** [Date]
**Processing:** AI-generated transcript (reviewed by [Name])
**Use:** Educational purposes only
```

## File Organization

Recommended structure:

```
~/Videos/
├── recordings/              # Raw recordings
│   ├── lecture_001.mp4
│   └── lecture_002.mp4
├── processed/               # After processing
│   ├── processed_lecture_001_20260216/
│   │   ├── audio.wav
│   │   ├── transcript.txt
│   │   ├── screenshots/
│   │   └── SUMMARY.md
│   └── ...
└── archive/                # Completed/archived
```

## Performance Optimization

### Reduce CPU Usage During Recording
```bash
# Use faster preset (lower quality during recording)
# Re-encode after if needed
ffmpeg -i raw_recording.mp4 -c:v libx264 -preset slow -crf 20 final.mp4
```

### Background Recording
```bash
# Start recording in background
nohup ./scripts/record_youtube.sh window lecture.mp4 &

# Check status
jobs

# Stop when done
fg  # Bring to foreground
# Then Ctrl+C
```

## Troubleshooting

### Issue: "xdotool: command not found"
```bash
./scripts/install_recording_tools.sh
```

### Issue: Recording is laggy
- Close other applications
- Use lower frame rate: Edit script, change `-framerate 30` to `-framerate 20`
- Use lower quality: Change `-crf 23` to `-crf 28`

### Issue: Window detection fails
```bash
# List all windows
xdotool search --name "." | while read id; do
    echo "$id: $(xdotool getwindowname $id)"
done

# Use window ID manually
./scripts/record_youtube.sh window
# When prompted, enter the window ID
```

### Issue: File size is too large
```bash
# Re-encode with better compression
ffmpeg -i large_file.mp4 -c:v libx264 -preset slow -crf 23 compressed.mp4

# Or record at lower resolution
# Edit script: change screen size to 1280x720
```

## Advanced: Automated Workflow

Complete automation script:

```bash
#!/bin/bash
# auto_record_and_process.sh

VIDEO_NAME="$1"

# Record
./scripts/record_youtube.sh window "$VIDEO_NAME.mp4"

# Process
./scripts/process_presentation_video.sh ~/Videos/recordings/"$VIDEO_NAME.mp4" 60

# Cleanup
mkdir -p ~/Videos/archive
mv ~/Videos/recordings/"$VIDEO_NAME.mp4" ~/Videos/archive/

echo "Complete! Check ~/Videos/processed_${VIDEO_NAME}_*/"
```

Usage:
```bash
./auto_record_and_process.sh cardiology_lecture_01
```

---

**Created:** 2026-02-16
**Last Updated:** 2026-02-16
**Scripts Location:** `/home/dev/Development/irStudy/scripts/`
