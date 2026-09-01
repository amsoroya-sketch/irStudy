# Video Transcript & Generated OSCE Notes - Location Guide

**Date:** 2026-05-27
**Status:** ✅ Located - Video transcripts processed but not yet converted to formal OSCE notes

---

## 📍 Quick Answer

Your video transcripts from Dr. Amir teaching videos are located in:

```
/home/dev/Development/irStudy/archive/old-data/processed_window_20260217_124331/
/home/dev/Development/irStudy/archive/old-data/processed_window_20260217_121553/
```

---

## 📹 What Was Done

### Video Processing System Created
You have a complete video processing pipeline that:

1. **Extracts Audio** from videos (using FFmpeg)
2. **Generates Transcripts** using OpenAI Whisper AI
3. **Captures Screenshots** at regular intervals
4. **Creates Metadata** with timestamps

### Processing Script
**Location:** `/home/dev/Development/irStudy/scripts/process_presentation_video.sh`

**Documentation:**
- `/home/dev/Development/irStudy/docs/VIDEO_PROCESSING_GUIDE.md`
- `/home/dev/Development/irStudy/docs/SCREEN_RECORDING_GUIDE.md`

---

## 📂 Processed Video Transcript Found

### Case: Acute Abdomen - Peptic Ulcer Disease

**Location:** `archive/old-data/processed_window_20260217_124331/`

**Files:**
```
├── window_audio.wav (39MB) - Extracted audio
├── window_transcript.txt (20KB) - Plain text transcript
├── window_transcript_timestamped.txt (30KB) - With timestamps
├── window_transcript.json (252KB) - Full metadata
├── screenshots/ - Visual captures from video
└── SUMMARY.md - Processing summary
```

**Content:** Dr. Amir teaching session on:
- Upper abdominal pain assessment
- History taking structure (6 minutes)
- Peptic ulcer disease vs gastroesophageal reflux
- Red flag questioning
- Differential diagnosis approach
- Australian clinical context (Quickies, Mylanta, Panadol, Nurofen)

**Duration:** 20 minutes
**Processing Date:** February 17, 2026

---

## ❌ Status: Not Yet Converted to OSCE Notes

### Current State
- ✅ Video processed and transcribed
- ✅ Transcript available in multiple formats
- ✅ Screenshots captured
- ❌ **Not yet converted to formal OSCE note structure**
- ❌ **Not yet integrated with other OSCE notes**
- ❌ **Not yet imported to database**

### What's Missing
The transcript contains valuable teaching content but needs to be:

1. **Structured** using the 5 Ps framework
2. **Formatted** like other OSCE notes
3. **Enhanced** with:
   - Marking criteria
   - Learning objectives
   - Australian guideline references
   - PBS medication codes
   - Differential diagnosis tables

4. **Integrated** into:
   - `ICRP_OSCE_Preparation/Medicine/` directory
   - Database as a new OSCE scenario
   - Master OSCE index

---

## 📋 Transcript Content Analysis

### Topics Covered in the Transcript

1. **Case Presentation**
   - 32-year-old truck driver
   - Left upper quadrant pain
   - 6-minute history taking station

2. **Systematic Approach**
   - Hemodynamic stability check
   - SOCRATES pain assessment
   - Food relationship (worse after eating)
   - Timing significance (immediate vs delayed)

3. **Differential Diagnosis Groups**
   - Peptic ulcer disease (gastric vs duodenal)
   - Gastroesophageal reflux disease
   - Pancreatitis
   - Gallbladder disease (biliary colic, cholecystitis, cholangitis)
   - Hepatitis/hepatocellular carcinoma
   - Gastric cancer (red flags emphasized)
   - Acute coronary syndrome
   - Lower lobe pneumonia
   - Lactose intolerance, splenic issues

4. **Key Clinical Pearls**
   - **Peptic ulcer:** Pain immediately after eating
   - **Duodenal ulcer:** Pain delayed after eating
   - **Risk factors:** NSAIDs, steroids, bisphosphonates
   - **Australian medications:** Quickies (antacid), Mylanta, Gaviscon, Panadol, Nurofen

5. **Red Flag Questions**
   - Weight loss, appetite loss
   - Hematemesis (vomiting blood)
   - Dark stools (melena)
   - Dysphagia (difficulty swallowing)
   - Family history of cancer
   - Night pain (peptic ulcer sign)

6. **Specific GERD Questions**
   - Heartburn
   - Bitter/metallic taste
   - Waterbrush (sudden increase in saliva)

---

## 🔄 How to Convert to Formal OSCE Notes

### Recommended Process

**Option 1: Manual Structuring**
1. Read the transcript
2. Extract key points
3. Structure using 5 Ps framework
4. Add marking criteria
5. Add Australian guidelines
6. Save to `ICRP_OSCE_Preparation/Medicine/`

**Option 2: AI-Assisted Conversion**
Use Claude/LLM to:
```
"Convert this Dr. Amir video transcript into a formal OSCE note
following the structure in ICRP_OSCE_Preparation/Medicine/ files.
Include: 5 Ps framework, marking criteria, learning objectives,
Australian guidelines, PBS codes, and high-yield indicators."
```

**Option 3: Database Import Script**
Create script to:
1. Parse transcript content
2. Extract clinical information
3. Generate OSCE scenario JSON
4. Import to database

---

## 📊 Integration Opportunities

### 1. Add to ICRP_OSCE_Preparation
**New file:** `Medicine/14_GI_Acute_Abdomen_Peptic_Ulcer.md`

**Structure:**
```markdown
# Acute Abdomen - Peptic Ulcer Disease OSCE Station
## AMC Clinical / ICRP NSW Preparation

[⭐⭐⭐ HIGH-YIELD] - Upper GI pain is common in AMC exams

## THE 5 Ps FRAMEWORK

### 1. PREPARATION
[Standard introduction and consent]

### 2. POSITION
[Patient seated/lying comfortably]

### 3. PERMISSION
[Consent for history taking]

### 4. PERFORM - SYSTEMATIC HISTORY
[Based on transcript content - structured approach]
- SOCRATES pain assessment
- Food relationship questions
- Red flag screening
- Differential-specific questions (GERD, pancreatitis, etc.)

### 5. PRESENT
[Diagnosis and differentials from transcript]

## MARKING CRITERIA
[Develop based on transcript content]

## LEARNING OBJECTIVES
[Extract from teaching points]
```

### 2. Import to Database
**File:** Create `data/osces/gi_acute_abdomen_peptic_ulcer.json`

```json
{
  "osce_id": "GI-ACUTE-001",
  "title": "Acute Abdomen - Peptic Ulcer Disease",
  "specialty": "general_practice",
  "difficulty": "medium",
  "duration_minutes": 6,
  "patient_scenario": {
    "demographics": {
      "age": "32",
      "gender": "Male",
      "occupation": "Truck driver"
    },
    "chief_complaint": "Left upper quadrant abdominal pain",
    "history_presenting_illness": "[Extract from transcript]"
  },
  "marking_criteria": {
    "history_taking_structure": 40,
    "differential_diagnosis": 30,
    "red_flag_identification": 20,
    "communication": 10
  },
  "learning_objectives": [
    "Differentiate peptic ulcer from GERD based on timing",
    "Identify red flags for gastric cancer",
    "Recognize Australian medication names",
    "Apply systematic GI pain assessment"
  ],
  "references": [
    {
      "title": "Source: Dr. Amir video transcript",
      "date": "2026-02-17"
    }
  ]
}
```

---

## 🎯 Clinical Content from Transcript

### High-Value Teaching Points

1. **Food Relationship Questions**
   - "Is there a specific food that makes it worse?"
   - "How soon after eating does the pain start?"
   - **Peptic ulcer:** Immediately after eating
   - **Duodenal ulcer:** Delayed (1-2 hours after)

2. **Australian Medications (Critical for AMC)**
   - **Quickies** - Antacid (OTC)
   - **Mylanta** - Antacid (common brand)
   - **Gaviscon** - Antacid (seen in ads)
   - **Panadol** - Paracetamol
   - **Nurofen** - Ibuprofen
   - **Mykards** - Telithromycin

3. **Red Flag Emphasis**
   - "I'm emphasizing a lot on gastric cancers"
   - Must rule out malignancy in all upper GI cases
   - Night pain = specific for peptic ulcer
   - Dark stools + hematemesis = upper GI bleed

4. **Differential Diagnosis Structure**
   - **3 main groups for upper abdomen:**
     1. Pancreatitis
     2. GERD + Peptic ulcer
     3. Liver/Gallbladder (cholecystitis, cholangitis, biliary colic)
   - **Plus:** ACS, pneumonia (always consider)

5. **Risk Factors to Cover**
   - Medications (NSAIDs, steroids, bisphosphonates)
   - Alcohol
   - Smoking
   - Coffee/tea
   - Spicy foods
   - Previous ulcers
   - Hyperlipidemia (for pancreatitis)

---

## 🔧 Technical Details

### Transcript Processing Stats
- **Audio quality:** 16kHz mono WAV
- **Transcription model:** OpenAI Whisper (base model)
- **Accuracy:** High (medical terminology captured)
- **Timestamp precision:** Segment-level
- **Screenshots:** 20 images (every 60 seconds)

### File Sizes
- Audio: 39.3 MB
- Text transcript: 20 KB
- Timestamped: 30 KB
- JSON metadata: 252 KB
- Screenshots: Variable

---

## 📝 Next Steps

### To Utilize This Content

1. **Immediate Use**
   - Read transcript for learning
   - Use as study supplement
   - Reference teaching points

2. **Integration (Recommended)**
   - Convert to formal OSCE note
   - Add to Medicine folder
   - Update master index
   - Create database entry

3. **Future Processing**
   - Process additional Dr. Amir videos
   - Build complete video-based OSCE library
   - Cross-reference with existing notes

---

## 🎬 Video Processing Capability

### You Have the Tools To:

1. **Process More Videos**
   ```bash
   ./scripts/process_presentation_video.sh [video_file.mp4] [screenshot_interval]
   ```

2. **Batch Process**
   - Process entire video library
   - Extract all teaching content
   - Build comprehensive transcript database

3. **Auto-Generate OSCE Notes**
   - Use LLM to structure transcripts
   - Generate formal OSCE scenarios
   - Populate database automatically

---

## 📚 Related Documentation

### OSCE Notes (Already Created)
- `/home/dev/Development/irStudy/ICRP_OSCE_Preparation/`
- 106 files covering all major specialties
- Based on Dr. Amir's 5 Ps methodology

### Video Integration (Completed)
- `OSCE_VIDEO_INTEGRATION_COMPLETE_SUMMARY.md`
- `OSCE_VIDEO_INTEGRATION_GUIDE.md`
- `OSCE_VIDEO_UI_DESIGN.md`
- `OSCE_VIDEO_TESTING_GUIDE.md`

### Database OSCEs (In Use)
- 225 OSCE scenarios imported
- Available at http://localhost:5173
- Accessible via API

---

## ⚠️ Important Notes

### Why Not Fully Integrated

The video transcripts were **processed but not converted** to formal OSCE notes because:

1. **Manual Review Needed:** Transcripts contain teaching commentary, not just clinical content
2. **Structure Required:** Need to extract and organize into 5 Ps framework
3. **Enhancement Needed:** Must add marking criteria, guidelines, PBS codes
4. **Quality Control:** Requires medical accuracy verification

### Value Proposition

**If converted, this would add:**
- Real teaching scenarios from Dr. Amir
- Authentic clinical reasoning flow
- Australian medication context
- Practical exam tips and strategies

---

## 🔄 Conversion Project (Optional)

If you want to convert these transcripts to formal OSCE notes, I can help you:

1. **Extract** clinical content from transcripts
2. **Structure** using 5 Ps framework
3. **Format** like existing OSCE notes
4. **Generate** database JSON
5. **Import** to application
6. **Update** master indexes

This would give you **Dr. Amir video-based OSCE notes** integrated with your existing 225 scenarios.

---

**Summary:** Your video transcripts are in `archive/old-data/processed_window_20260217_124331/`. They contain valuable Dr. Amir teaching content on peptic ulcer disease but are **not yet converted to formal OSCE notes** or integrated with your existing OSCE preparation materials. The transcript processing system is fully functional and ready to process more videos.

Would you like me to convert this transcript into a formal OSCE note and integrate it with your existing materials?
