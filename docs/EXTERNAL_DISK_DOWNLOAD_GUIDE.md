# External Disk Download Guide - Medical Resources

**Date:** January 17, 2026
**Version:** 1.0.0
**Estimated Total Size:** 25-35 GB
**Estimated Time:** 4-6 hours (parallel execution)

---

## 🎯 Quick Start

### 1. Attach External Disk

```bash
# Check mounted disks
df -h | grep -E '(/mnt|/media)'

# Your external disk should appear as:
# /media/$USER/MyDrive
# /mnt/external
# etc.
```

### 2. Run Download Orchestrator

```bash
# Navigate to project
cd /home/dev/Development/irStudy

# Run orchestrator with your external disk path
bash scripts/download_orchestrator.sh /media/$USER/MyDrive
```

### 3. Follow Instructions

The orchestrator will:
- ✅ Check disk space (needs 100+ GB free)
- ✅ Create directory structure
- ✅ Generate scripts for 3 parallel terminals
- ✅ Provide step-by-step instructions

---

## 📋 Prerequisites

### Required

- **External disk:** 120+ GB free space (100 GB data + 20% buffer)
- **Internet connection:** Stable connection for 4-6 hours
- **Python 3:** For StatPearls downloader
- **Basic tools:** curl, wget, git (auto-checked by orchestrator)

### Optional

- **NCBI API key:** For StatPearls download (free, highly recommended)
- **Therapeutic Guidelines subscription:** For eTG PDFs (optional)

---

## 🗂️ What You'll Download

### Essential Resources (25-35 GB)

| Resource | Size | Priority | Method |
|----------|------|----------|--------|
| **StatPearls Database** | 15-20 GB | HIGH | Automated (Python) |
| **Cochrane Reviews** | 5-10 GB | HIGH | Manual |
| **RACGP Red Book** | 50 MB | HIGH | Automated |
| **RANZCOG Guidelines** | 500 MB | HIGH | Manual |
| **RANZCP Guidelines** | 200 MB | HIGH | Manual |
| **MeSH Database** | 500 MB | MEDIUM | Automated |
| **Immunisation Handbook** | 100 MB | MEDIUM | Automated |
| **Stroke Foundation** | 200 MB | MEDIUM | Automated |
| **NSW Health Protocols** | 300 MB | MEDIUM | Manual |
| **Therapeutic Guidelines** | 1 GB | LOW | Manual (subscription) |

### Optional Resources (50+ GB)

| Resource | Size | Notes |
|----------|------|-------|
| MIMIC-III Database | 50 GB | Requires PhysioNet approval (1-2 weeks) |
| PubMed Central Bulk | 500+ GB | NOT recommended (use API instead) |

---

## 🚀 Step-by-Step Guide

### Step 1: Mount External Disk

**Option A: USB Drive (auto-mounts)**
```bash
# Plug in USB drive
# Check where it mounted
df -h | grep media

# Example output:
# /dev/sdb1  500G  50G  450G  10% /media/dev/MyUSB
```

**Option B: Manual Mount**
```bash
# Create mount point
sudo mkdir -p /mnt/external

# Mount disk (replace /dev/sdb1 with your disk)
sudo mount /dev/sdb1 /mnt/external

# Make writable
sudo chmod -R u+w /mnt/external
```

**Option C: Network Drive**
```bash
# Mount network share
sudo mount -t cifs //server/share /mnt/network \
  -o username=youruser,password=yourpass
```

### Step 2: Run Orchestrator

```bash
cd /home/dev/Development/irStudy

# Replace with your actual mount point
bash scripts/download_orchestrator.sh /media/$USER/MyUSB
```

**What the orchestrator does:**
1. Validates external disk exists and is writable
2. Checks available space (needs 100+ GB)
3. Creates directory structure
4. Generates scripts for 3 parallel terminals
5. Provides detailed instructions

**Example output:**
```
[SUCCESS] External disk found: /media/dev/MyUSB
[INFO] Available space on external disk: 450 GB
[INFO] Required space: 100 GB
[INFO] Recommended space: 120 GB
[SUCCESS] Sufficient disk space available: 450 GB

[SUCCESS] Directories created at: /media/dev/MyUSB/medical_resources

[SUCCESS] Terminal scripts generated:
  Terminal 1: /media/dev/MyUSB/medical_resources/logs/terminal1_automated.sh
  Terminal 2: /media/dev/MyUSB/medical_resources/logs/terminal2_statpearls.sh
  Terminal 3: /media/dev/MyUSB/medical_resources/logs/terminal3_manual_instructions.md
```

### Step 3: Open 3 Terminals

**Terminal 1:** Automated small downloads (30 min)
**Terminal 2:** StatPearls database (4-6 hours)
**Terminal 3:** Manual downloads (2-4 hours)

Run them **in parallel** for maximum efficiency!

---

## 📺 Terminal 1: Automated Downloads

**Time:** 30 minutes
**Size:** ~850 MB

### Run Command

```bash
# Generated script path will be shown by orchestrator
bash /media/$USER/MyUSB/medical_resources/logs/terminal1_automated.sh
```

### What It Downloads

- **RACGP Red Book** (~50 MB)
  - Australia's primary care guidelines
  - Source: https://www.racgp.org.au/

- **MeSH Database** (~500 MB)
  - Medical subject headings
  - Source: https://nlmpubs.nlm.nih.gov/

- **Australian Immunisation Handbook** (~100 MB)
  - Vaccination guidelines
  - Source: https://immunisationhandbook.health.gov.au/

- **Stroke Foundation Guidelines** (~200 MB)
  - Stroke management protocols
  - Source: https://strokefoundation.org.au/

### Monitoring

```bash
# Watch Terminal 1 log
tail -f /media/$USER/MyUSB/medical_resources/logs/terminal1_*.log
```

---

## 🐍 Terminal 2: StatPearls Database

**Time:** 4-6 hours
**Size:** 15-20 GB
**Articles:** 10,000+

### Prerequisites: Get NCBI API Key (FREE)

1. **Visit:** https://www.ncbi.nlm.nih.gov/account/settings/
2. **Register/Login** (free account)
3. **Request API Key** (instant approval)
4. **Copy your key** (looks like: 1234567890abcdef1234567890abcdef1234)

### Run Command

```bash
# Export your API key
export NCBI_API_KEY='your_key_here'

# Run StatPearls downloader
bash /media/$USER/MyUSB/medical_resources/logs/terminal2_statpearls.sh
```

### What It Downloads

- **10,000+ medical articles** from StatPearls
- **High-quality content** written by medical experts
- **Regularly updated** clinical information
- **Covers all specialties** (cardiology, respiratory, etc.)

### Monitoring

```bash
# Watch download progress
tail -f /media/$USER/MyUSB/medical_resources/logs/terminal2_*.log

# Check downloaded files
du -sh /media/$USER/MyUSB/medical_resources/statpearls/

# Count articles downloaded
find /media/$USER/MyUSB/medical_resources/statpearls/ -name "*.xml" | wc -l
```

### Troubleshooting

**Problem:** `ERROR: NCBI_API_KEY not set!`
```bash
# Solution: Export your API key
export NCBI_API_KEY='your_key_here'
```

**Problem:** Rate limit errors
```bash
# The script automatically handles rate limits
# Just wait - it will resume automatically
```

**Problem:** Download interrupted
```bash
# Just re-run the script - it auto-resumes from where it stopped
bash /media/$USER/MyUSB/medical_resources/logs/terminal2_statpearls.sh
```

---

## 📖 Terminal 3: Manual Downloads

**Time:** 2-4 hours
**Size:** 7-12 GB

### Instructions File

```bash
# Read instructions
cat /media/$USER/MyUSB/medical_resources/logs/terminal3_manual_instructions.md

# Or open in editor
nano /media/$USER/MyUSB/medical_resources/logs/terminal3_manual_instructions.md
```

### Downloads Checklist

#### 1. Cochrane Reviews (5-10 GB) ✅

**Website:** https://www.cochranelibrary.com/

**Steps:**
1. Create free account
2. Search by specialty:
   - **Cardiology:** "cardiovascular" OR "acute coronary syndrome"
   - **Respiratory:** "asthma" OR "COPD" OR "pneumonia"
   - **Gastro:** "inflammatory bowel disease" OR "GI bleeding"
   - **Endocrine:** "diabetes" OR "thyroid"
   - **Neurology:** "stroke" OR "seizure" OR "headache"
   - **Emergency:** "trauma" OR "sepsis" OR "resuscitation"
   - **ObGyn:** "pregnancy" OR "contraception"
   - **Paediatrics:** "pediatric" OR "child"
   - **Psychiatry:** "depression" OR "anxiety"
   - **General Practice:** "primary care"

3. Filter: "Cochrane Reviews" only
4. Download PDFs (50-100 per specialty)
5. Save to: `/media/$USER/MyUSB/medical_resources/cochrane/[specialty]/`

**Tip:** Sort by "Most Recent" to get latest evidence

#### 2. RANZCOG Guidelines (500 MB) ✅

**Website:** https://ranzcog.edu.au/statements-guidelines

**Steps:**
1. Browse clinical statements and guidelines
2. Download key guidelines:
   - Antenatal screening
   - Pre-eclampsia management
   - Gestational diabetes
   - Post-partum haemorrhage
   - Contraception options
   - Menopause management
3. Save to: `/media/$USER/MyUSB/medical_resources/ranzcog/`

#### 3. RANZCP Guidelines (200 MB) ✅

**Website:** https://www.ranzcp.org/clinical-guidelines-publications

**Steps:**
1. Download clinical practice guidelines:
   - Depression treatment
   - Anxiety disorders
   - Schizophrenia management
   - Bipolar disorder
   - Suicide risk assessment
   - Mental Health Act procedures
2. Save to: `/media/$USER/MyUSB/medical_resources/ranzcp/`

#### 4. NSW Health Protocols (300 MB) ✅

**Website:** https://www.health.nsw.gov.au/policies/

**Steps:**
1. Search for clinical protocols
2. Download:
   - Emergency department protocols
   - Resuscitation guidelines
   - Sepsis management
   - Mental health crisis
   - Paediatric emergencies
3. Save to: `/media/$USER/MyUSB/medical_resources/nsw_health/`

#### 5. Therapeutic Guidelines (1 GB) - OPTIONAL ✅

**Website:** https://www.tg.org.au/ (requires subscription)

**If you have access:**
1. Login to eTG Complete
2. Download PDFs:
   - Cardiovascular
   - Respiratory
   - Antibiotic
   - Endocrinology
   - Gastrointestinal
   - Neurology
   - Mental Health
3. Save to: `/media/$USER/MyUSB/medical_resources/therapeutic_guidelines/`

**Note:** We already have 9,672 eTG chunks in the vector database, so this is optional.

---

## 📊 Monitoring Downloads

### Watch Disk Usage

```bash
# Real-time disk usage (updates every 10 seconds)
watch -n 10 du -sh /media/$USER/MyUSB/medical_resources/*

# Check total size
du -sh /media/$USER/MyUSB/medical_resources/

# Check available space
df -h /media/$USER/MyUSB
```

### Monitor Logs

```bash
# Watch all logs
tail -f /media/$USER/MyUSB/medical_resources/logs/*.log

# Check specific terminal
tail -f /media/$USER/MyUSB/medical_resources/logs/terminal1_*.log
tail -f /media/$USER/MyUSB/medical_resources/logs/terminal2_*.log
```

### Check Progress

```bash
# Count files by directory
find /media/$USER/MyUSB/medical_resources/ -type f | wc -l

# Size by directory
du -h --max-depth=1 /media/$USER/MyUSB/medical_resources/ | sort -h
```

---

## ✅ Validation

### After Downloads Complete

```bash
# Check total size (should be 25-35 GB)
du -sh /media/$USER/MyUSB/medical_resources/

# Validate directory structure
ls -lh /media/$USER/MyUSB/medical_resources/

# Expected directories:
# drwxr-xr-x statpearls/          (15-20 GB)
# drwxr-xr-x cochrane/             (5-10 GB)
# drwxr-xr-x racgp/                (50 MB)
# drwxr-xr-x ranzcog/              (500 MB)
# drwxr-xr-x ranzcp/               (200 MB)
# drwxr-xr-x mesh/                 (500 MB)
# drwxr-xr-x immunisation/         (100 MB)
# drwxr-xr-x stroke_foundation/    (200 MB)
# drwxr-xr-x nsw_health/           (300 MB)
# drwxr-xr-x logs/                 (logs)
```

### Completion Checklist

- [ ] Terminal 1 complete (automated downloads)
- [ ] Terminal 2 complete (StatPearls database)
- [ ] Terminal 3 complete (manual downloads)
- [ ] Total size: 25-35 GB
- [ ] All directories present
- [ ] No error messages in logs

### Create Completion Marker

```bash
# Mark downloads as complete
echo "Downloads completed: $(date)" > /media/$USER/MyUSB/medical_resources/DOWNLOAD_COMPLETE.txt
echo "Total size: $(du -sh /media/$USER/MyUSB/medical_resources/ | cut -f1)" >> /media/$USER/MyUSB/medical_resources/DOWNLOAD_COMPLETE.txt
```

---

## 🔧 Troubleshooting

### External Disk Not Detected

```bash
# List all disks
lsblk

# Check mount points
df -h

# Try manual mount
sudo mount /dev/sdb1 /mnt/external
```

### Permission Denied

```bash
# Make writable
sudo chmod -R u+w /media/$USER/MyUSB/medical_resources/

# Or change ownership
sudo chown -R $USER:$USER /media/$USER/MyUSB/medical_resources/
```

### Disk Space Full

```bash
# Check available space
df -h /media/$USER/MyUSB

# Free up space
# Delete unnecessary files from external disk

# Or use a larger disk (120+ GB recommended)
```

### Download Interrupted

```bash
# Terminal 1 (automated) - re-run script
bash /media/$USER/MyUSB/medical_resources/logs/terminal1_automated.sh

# Terminal 2 (StatPearls) - auto-resumes
bash /media/$USER/MyUSB/medical_resources/logs/terminal2_statpearls.sh

# Terminal 3 (manual) - continue from checklist
cat /media/$USER/MyUSB/medical_resources/logs/terminal3_manual_instructions.md
```

### Slow Download Speed

```bash
# Check internet speed
speedtest-cli

# Try at different time (off-peak hours)
# Night downloads (11 PM - 6 AM) often faster

# Consider wired connection instead of WiFi
```

---

## 📈 Expected Timeline

### Hour-by-Hour Progress

| Hour | Terminal 1 | Terminal 2 | Terminal 3 | Total Downloaded |
|------|-----------|-----------|-----------|------------------|
| 0 | Starting | Starting | Starting | 0 GB |
| 0.5 | ✅ Complete (~850 MB) | ~5% (~1 GB) | ~10% (~1 GB) | ~3 GB |
| 1 | Done | ~10% (~2 GB) | ~20% (~2 GB) | ~5 GB |
| 2 | Done | ~20% (~4 GB) | ~40% (~4 GB) | ~9 GB |
| 3 | Done | ~30% (~6 GB) | ~60% (~6 GB) | ~13 GB |
| 4 | Done | ~50% (~10 GB) | ~80% (~8 GB) | ~19 GB |
| 5 | Done | ~70% (~14 GB) | ✅ Complete (~10 GB) | ~25 GB |
| 6 | Done | ✅ Complete (~18 GB) | Done | ~30 GB |

**Total Time:** 4-6 hours (all terminals in parallel)
**Total Size:** 25-35 GB

---

## 💾 Backup & Safety

### Backup Downloaded Resources

```bash
# Compress for backup
tar -czf medical_resources_backup_$(date +%Y%m%d).tar.gz \
  /media/$USER/MyUSB/medical_resources/

# Or sync to another location
rsync -av --progress \
  /media/$USER/MyUSB/medical_resources/ \
  ~/backup/medical_resources/
```

### Safely Unmount

```bash
# Sync all writes to disk
sync

# Unmount (replace with your actual mount point)
sudo umount /media/$USER/MyUSB

# Or use file manager to "Safely Remove"
```

---

## 🎯 Next Steps After Download

### 1. Verify Downloads

```bash
# Check completion status
cat /media/$USER/MyUSB/medical_resources/DOWNLOAD_COMPLETE.txt

# Validate total size
du -sh /media/$USER/MyUSB/medical_resources/
```

### 2. Integrate with RAG System

```bash
# Copy or symlink to project
ln -s /media/$USER/MyUSB/medical_resources ~/medical_resources

# Process documents for vector database
# (Future step - document processing scripts)
```

### 3. Update Medical Agents

Medical expert agents (MED-001 to MED-010) will use these resources for:
- Citation verification
- Evidence-based recommendations
- Up-to-date medical knowledge
- Australian guideline compliance

---

## 📚 Resource Quality

### StatPearls Database
- **Quality:** ⭐⭐⭐⭐⭐ (5/5)
- **Currency:** Updated regularly
- **Coverage:** All major specialties
- **Authority:** Written by medical experts
- **Usage:** Primary source for medical facts

### Cochrane Reviews
- **Quality:** ⭐⭐⭐⭐⭐ (5/5)
- **Currency:** Latest evidence-based medicine
- **Coverage:** Systematic reviews
- **Authority:** Gold standard for clinical evidence
- **Usage:** Treatment efficacy validation

### Australian Guidelines (RACGP, RANZCOG, RANZCP)
- **Quality:** ⭐⭐⭐⭐⭐ (5/5)
- **Currency:** Australia-specific, current
- **Coverage:** Clinical practice guidelines
- **Authority:** Official Australian medical colleges
- **Usage:** Ensure Australian compliance

---

## ✅ Summary

**What You'll Have:**
- ✅ 25-35 GB of high-quality medical resources
- ✅ 10,000+ StatPearls articles
- ✅ 500+ Cochrane systematic reviews
- ✅ Australian clinical guidelines (RACGP, RANZCOG, RANZCP)
- ✅ MeSH database for medical terminology
- ✅ Organized directory structure
- ✅ Complete logs for troubleshooting

**Time Investment:**
- Setup: 10 minutes
- Download: 4-6 hours (parallel)
- Total: ~6 hours

**Storage Required:**
- External disk: 120+ GB (100 GB data + buffer)
- After compression: ~15-20 GB (for backup)

**Cost:**
- All resources: **FREE**
- NCBI API key: **FREE**
- External disk: ~$50 for 500 GB USB drive (if needed)

---

**Last Updated:** January 17, 2026
**Status:** ✅ Ready to Use
**Next:** Attach external disk and run orchestrator!
