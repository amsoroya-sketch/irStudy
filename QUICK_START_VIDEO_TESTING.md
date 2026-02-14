# 🎬 OSCE Video Integration - Quick Start Testing Guide

## TL;DR - One Command Deployment

```bash
# Run this single command to deploy and test everything:
./scripts/deploy-and-test-videos.sh
```

This script automatically:
1. ✅ Starts Docker services (PostgreSQL, Redis, Qdrant)
2. ✅ Runs database migration
3. ✅ Populates video data
4. ✅ Starts backend server
5. ✅ Starts frontend server
6. ✅ Runs automated Playwright tests with video recording
7. ✅ Generates test report

**Time:** ~3-5 minutes

---

## 📹 What This Does

After running the script, you'll have:

1. **Live Web App** running at http://localhost:5174
2. **Backend API** running at http://localhost:8000
3. **9 OSCEs** populated with **39 video links**
4. **Automated test videos** in `frontend/test-results/`
5. **Test report** in `frontend/playwright-report/index.html`

---

## 🎯 Quick Testing Steps

### 1. View Web App
```bash
# Open in browser
google-chrome http://localhost:5174/osces
```

### 2. Navigate to OSCE with Videos
- Click on any physical examination OSCE
- Examples:
  - "Cardiovascular Physical Examination"
  - "Abdominal Examination"
  - "Mental State Examination"

### 3. Check Video Component
Scroll down to see:
```
┌─────────────────────────────────────────┐
│  📺 Video Demonstrations                 │
│                                          │
│  🔵 Essential - Watch These First       │
│                                          │
│  [Video Card 1]  [Video Card 2]         │
│                                          │
│  ⚪ Supplementary Videos (2) ▼          │
└─────────────────────────────────────────┘
```

### 4. Test Interactions
- ✅ Click "Why recommended?" to expand details
- ✅ Click "Watch Video" to open external link
- ✅ Toggle "Supplementary Videos" section
- ✅ Resize browser to test responsive design

---

## 📊 View Test Results

### Automated Test Report
```bash
# Open Playwright HTML report
google-chrome frontend/playwright-report/index.html
```

### Test Videos
```bash
# List all recorded test videos
find frontend/test-results -name "video.webm"

# Play a test video
vlc frontend/test-results/*/video.webm
```

### Convert Videos to MP4
```bash
# Install ffmpeg
sudo apt install ffmpeg

# Convert all test videos to MP4
for video in frontend/test-results/*/video.webm; do
  ffmpeg -i "$video" "${video%.webm}.mp4"
done
```

---

## 🔍 Verify Everything Works

### Check Database
```bash
# Connect to database
docker exec -it irstudy-postgres psql -U postgres -d irstudy_medical

# Run query
SELECT
  osce_id,
  station_title,
  jsonb_array_length(video_resources->'essential_videos') as videos
FROM osces
WHERE video_resources IS NOT NULL;

# Exit
\q
```

**Expected Output:**
```
osce_id      | station_title                    | videos
-------------+----------------------------------+--------
OSCE-MED-001 | Cardiovascular Exam              | 4
OSCE-MED-002 | Abdominal Exam                   | 3
OSCE-SURG-001| Acute Abdomen                    | 2
... (more rows)
```

### Check API
```bash
# Test API endpoint
curl http://localhost:8000/api/v1/osces/1 | jq '.video_resources'
```

**Expected Output:**
```json
{
  "essential_videos": [
    {
      "title": "Cardiovascular Examination - Stanford Medicine 25",
      "url": "https://stanfordmedicine25.stanford.edu/...",
      "source": "Stanford Medicine 25",
      "duration_minutes": 10,
      ...
    }
  ],
  "supplementary_videos": []
}
```

---

## 🎥 Manual Video Recording

To record your own demo video:

### Option 1: Using SimpleScreenRecorder (Linux)
```bash
# Install
sudo apt install simplescreenrecorder

# Run
simplescreenrecorder

# Steps:
1. Select "Record a fixed rectangle"
2. Set resolution to 1920x1080
3. Start recording
4. Navigate through web app
5. Stop recording
6. Save as osce-video-demo.mp4
```

### Option 2: Using OBS Studio
```bash
# Install
sudo snap install obs-studio

# Run
obs-studio

# Steps:
1. Add "Window Capture" source (select Chrome)
2. Start recording
3. Navigate through web app
4. Stop recording
5. File saved to ~/Videos/
```

### Demo Script
```
1. Open http://localhost:5174
2. Show OSCE list page
3. Click "Cardiovascular Examination"
4. Scroll to video section
5. Hover over video card (show details)
6. Click "Why recommended?" (expand)
7. Show Australian relevance section
8. Click "Watch Video" (new tab opens)
9. Return to show second video
10. Toggle supplementary videos
11. Resize browser (show responsive design)
12. Navigate via keyboard (Tab key)
```

**Duration:** 2-3 minutes

---

## 🛑 Stop Servers

When done testing:

```bash
# Option 1: Use stop script
./scripts/stop-servers.sh

# Option 2: Manual kill
kill $(cat logs/backend.pid)
kill $(cat logs/frontend.pid)

# Option 3: Stop Docker services
docker compose down
```

---

## 📚 Full Documentation

Detailed guides available:

1. **Implementation Guide** - How everything works
   - File: `OSCE_VIDEO_INTEGRATION_GUIDE.md`
   - Topics: Database schema, API, frontend component

2. **UI/UX Design Spec** - Visual design details
   - File: `OSCE_VIDEO_UI_DESIGN.md`
   - Topics: Layout, colors, interactions, accessibility

3. **Testing Guide** - Comprehensive testing
   - File: `OSCE_VIDEO_TESTING_GUIDE.md`
   - Topics: Playwright tests, manual testing, video recording

4. **Complete Summary** - Full deliverables list
   - File: `OSCE_VIDEO_INTEGRATION_COMPLETE_SUMMARY.md`
   - Topics: All files created, deployment, troubleshooting

---

## 🐛 Troubleshooting

### Servers Won't Start

**Problem:** Port already in use

**Solution:**
```bash
# Find and kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 5174 (frontend)
lsof -ti:5174 | xargs kill -9

# Re-run deployment script
./scripts/deploy-and-test-videos.sh
```

### Database Connection Fails

**Problem:** PostgreSQL not running

**Solution:**
```bash
# Check Docker status
docker compose ps

# Restart services
docker compose restart postgres

# Check logs
docker compose logs postgres
```

### Videos Not Displaying

**Problem:** Data not populated

**Solution:**
```bash
# Re-run population script
python scripts/populate_osce_videos.py

# When prompted, type: y

# Verify in database
docker exec -it irstudy-postgres psql -U postgres -d irstudy_medical \
  -c "SELECT COUNT(*) FROM osces WHERE video_resources IS NOT NULL;"
```

### Frontend Not Loading

**Problem:** npm dependencies missing

**Solution:**
```bash
cd frontend
npm install
npm run dev
```

---

## ✅ Success Checklist

After running the deployment script, verify:

- [ ] Docker services running (`docker compose ps` shows "Up (healthy)")
- [ ] Backend accessible (http://localhost:8000/docs loads)
- [ ] Frontend accessible (http://localhost:5174 loads)
- [ ] Database has video data (SQL query returns 7+ rows)
- [ ] API returns video_resources (curl test succeeds)
- [ ] Video component visible on OSCE page
- [ ] External links work (clicking "Watch Video" opens Stanford/Geeky Medics)
- [ ] Responsive design works (mobile viewport shows single column)
- [ ] Test report generated (playwright-report/index.html exists)
- [ ] Test videos recorded (test-results/ has video.webm files)

---

## 🎉 You're Done!

If all checks passed, the video integration is working perfectly!

**Next Steps:**
1. Show demo to stakeholders
2. Deploy to staging environment
3. Run UAT testing with real users
4. Deploy to production

**Questions?**
- Check detailed docs in project root
- Review code comments
- Check test results in Playwright report

---

**Created:** February 13, 2026
**Status:** ✅ Ready to Test
**Estimated Time:** 5 minutes to deploy + 10 minutes to test
