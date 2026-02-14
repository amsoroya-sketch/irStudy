# Medical Resources Download Instructions

## Overview

This guide will help you download **15+ free medical resources** (~25-35 GB) to enhance the Medical Expert Agents (MED-001 to MED-010).

**Total Time**: 8-12 hours hands-on, 1-2 weeks calendar time (due to approval delays)
**Total Storage**: ~25-35 GB essential, ~75-85 GB with MIMIC-III

---

## Quick Start (3 Steps)

### Step 1: Mount External Drive
```bash
# Find your external drive
lsblk

# Mount it (replace sdX1 with your device)
sudo mount /dev/sdX1 /mnt/external

# Or create a directory on your main drive
mkdir -p ~/medical_resources
```

### Step 2: Run Automated Downloads
```bash
cd /home/dev/Development/irStudy/scripts

# Run the main download script
bash download_external_resources.sh /mnt/external/medical_resources

# This will automatically download:
# - RACGP Red Book (~50 MB)
# - MeSH Database (~500 MB)
# - Check for Australian Immunisation Handbook in project
```

### Step 3: Execute Manual Downloads
Follow the checklist created at: `/mnt/external/medical_resources/DOWNLOAD_CHECKLIST.md`

---

## Parallel Download Strategy

You can run these downloads **in parallel** while continuing other work:

### Terminal 1: Automated Downloads (30 minutes)
```bash
bash scripts/download_external_resources.sh ~/medical_resources
```

### Terminal 2: StatPearls Download (4-6 hours, requires API key)
```bash
# First, get your NCBI API key (takes 2 minutes):
# 1. Visit: https://www.ncbi.nlm.nih.gov/account/settings/
# 2. Sign in with Google/GitHub or create account
# 3. Go to "API Key Management"
# 4. Click "Create an API Key"
# 5. Copy the key

# Set the API key
export NCBI_API_KEY='your_key_here'

# Download StatPearls
python3 scripts/download_statpearls.py --output ~/medical_resources/statpearls
```

### Terminal 3: Manual Browser Downloads (2-3 hours)
Open these URLs in your browser and download:

1. **Cochrane Reviews** (largest manual task - 4-6 hours)
   - URL: https://www.cochranelibrary.com/
   - Create free account
   - Download specialty reviews (see detailed instructions below)

2. **RANZCOG Guidelines** (30 minutes)
   - URL: https://ranzcog.edu.au/womens-health/statements-guidelines/
   - Create healthcare professional account
   - Download all PDFs

3. **RANZCP Guidelines** (30 minutes)
   - URL: https://www.ranzcp.org/clinical-guidelines-publications/
   - Download all clinical practice guidelines

4. **Australian Stroke Guidelines** (15 minutes)
   - URL: https://informme.org.au/
   - Navigate to Clinical Guidelines
   - Download stroke management guidelines

5. **NSW Health Protocols** (1 hour)
   - URL: https://www1.health.nsw.gov.au/pds/Pages/doc.aspx
   - Search and download emergency, obstetric, mental health protocols

---

## Detailed Download Instructions

### StatPearls (15-20 GB, 4-6 hours)

**Prerequisites:**
- NCBI API key (free, instant): https://www.ncbi.nlm.nih.gov/account/settings/

**Download:**
```bash
# Install required Python packages (if not already installed)
pip install requests tqdm

# Set API key
export NCBI_API_KEY='your_key_here'

# Download
python3 scripts/download_statpearls.py --output ~/medical_resources/statpearls

# The script will:
# - Search for all StatPearls books (~10,000 articles)
# - Download each as XML and TXT
# - Track progress with metadata.json
# - Resume if interrupted
```

**Resume after interruption:**
```bash
# The script automatically resumes - just run it again
python3 scripts/download_statpearls.py --output ~/medical_resources/statpearls
```

---

### Cochrane Reviews (5-10 GB, 4-6 hours)

**Prerequisites:**
- Free Cochrane Library account: https://www.cochranelibrary.com/

**Download by Specialty:**

1. **Cardiology** (~500 MB, 50-100 reviews)
   ```
   Search: "cardiovascular" OR "cardiology" OR "heart"
   Filter: Cochrane Reviews (not protocols)
   Sort by: Newest first
   Download: PDFs of reviews published 12+ months ago (free)
   Save to: ~/medical_resources/cochrane/cardiology/
   ```

2. **Respiratory** (~500 MB, 50-100 reviews)
   ```
   Search: "respiratory" OR "asthma" OR "COPD" OR "pneumonia"
   Download to: ~/medical_resources/cochrane/respiratory/
   ```

3. **Gastroenterology** (~400 MB, 40-80 reviews)
   ```
   Search: "gastrointestinal" OR "GI" OR "IBD" OR "hepatitis"
   Download to: ~/medical_resources/cochrane/gastroenterology/
   ```

4. **Endocrinology** (~300 MB, 30-60 reviews)
   ```
   Search: "diabetes" OR "thyroid" OR "endocrine" OR "metabolic"
   Download to: ~/medical_resources/cochrane/endocrinology/
   ```

5. **Neurology** (~400 MB, 40-80 reviews)
   ```
   Search: "neurology" OR "stroke" OR "seizure" OR "headache"
   Download to: ~/medical_resources/cochrane/neurology/
   ```

6. **Emergency Medicine** (~300 MB, 30-60 reviews)
   ```
   Search: "emergency" OR "trauma" OR "resuscitation" OR "acute"
   Download to: ~/medical_resources/cochrane/emergency/
   ```

7. **Obstetrics & Gynaecology** (~500 MB, 50-100 reviews)
   ```
   Search: "obstetric" OR "gynecology" OR "pregnancy" OR "contraception"
   Download to: ~/medical_resources/cochrane/obgyn/
   ```

8. **Paediatrics** (~600 MB, 60-120 reviews)
   ```
   Search: "pediatric" OR "child" OR "infant" OR "neonatal"
   Download to: ~/medical_resources/cochrane/paediatrics/
   ```

9. **Psychiatry** (~400 MB, 40-80 reviews)
   ```
   Search: "psychiatry" OR "depression" OR "mental health" OR "anxiety"
   Download to: ~/medical_resources/cochrane/psychiatry/
   ```

10. **General Practice** (~400 MB, 40-80 reviews)
    ```
    Search: "primary care" OR "general practice" OR "preventive"
    Download to: ~/medical_resources/cochrane/general_practice/
    ```

**Tips:**
- Download in batches (20-30 reviews at a time)
- Use browser's download manager
- Verify downloads are complete
- Total time: 4-6 hours of active downloading

---

### RANZCOG Guidelines (~500 MB, 30 minutes)

**Prerequisites:**
- Healthcare professional account (free): https://ranzcog.edu.au/

**Download:**
1. Create account (select "Healthcare Professional")
2. Navigate to: Women's Health > Statements & Guidelines
3. Download categories:
   - Obstetrics (all statements)
   - Gynaecology (all statements)
   - Women's Health (all statements)
   - Early Pregnancy (all statements)
   - Maternal-Fetal Medicine (all statements)
4. Save to: `~/medical_resources/ranzcog/`

**Key Documents for AMC:**
- Antenatal screening
- Intrapartum care
- Contraception
- Cervical cancer screening
- Gestational diabetes
- Pre-eclampsia/eclampsia

---

### RANZCP Guidelines (~200 MB, 30 minutes)

**Download:**
1. Visit: https://www.ranzcp.org/clinical-guidelines-publications/
2. Download all clinical practice guidelines (no account needed)
3. Key guidelines:
   - Depression and related disorders
   - Bipolar disorder
   - Schizophrenia and related psychoses
   - Anxiety disorders
   - Mood disorders
4. Save to: `~/medical_resources/ranzcp/`

---

### Australian Stroke Guidelines (~100 MB, 15 minutes)

**Download:**
1. Visit: https://informme.org.au/
2. Navigate to: Clinical Guidelines
3. Download: "Living Clinical Guidelines for Stroke Management"
4. Save to: `~/medical_resources/stroke_foundation/`

---

### NSW Health Protocols (~1 GB, 1 hour)

**Download:**
1. Visit: https://www1.health.nsw.gov.au/pds/Pages/doc.aspx
2. Search for:
   - Emergency medicine protocols
   - Obstetric and maternity guidelines
   - Mental Health Act protocols
   - Paediatric guidelines
   - Infection control protocols
3. Download all relevant PDFs
4. Save to: `~/medical_resources/nsw_health/`

---

## Registration Required (1-2 Weeks Approval)

### UMLS License for SNOMED CT (1-3 days approval)

**Purpose:** Clinical terminology validation

**Steps:**
1. Visit: https://uts.nlm.nih.gov/uts/signup-login
2. Create UMLS account
3. Request UMLS Metathesaurus License
4. Select "Affiliate License" (free for non-commercial use)
5. Wait for approval (usually 1-3 business days)
6. After approval, download SNOMED CT Australian Edition
7. Save to: `~/medical_resources/snomed_ct/`

---

### MIMIC-III Database (1-2 weeks approval, OPTIONAL)

**Purpose:** Clinical decision support patterns (optional, for advanced features)

**Steps:**
1. Visit: https://physionet.org/
2. Create account
3. Complete CITI training (required): https://physionet.org/about/citi-course/
4. Apply for MIMIC-III access: https://physionet.org/content/mimiciii/1.4/
5. Wait for approval (1-2 weeks)
6. After approval, download dataset (~50 GB)
7. Save to: `~/medical_resources/mimic3/`

**Note:** MIMIC-III is optional and very large. Only download if needed for advanced clinical decision support features.

---

## Progress Tracking

Use the checklist file created by the download script:
```bash
cat ~/medical_resources/DOWNLOAD_CHECKLIST.md
```

Monitor progress:
```bash
# Check download sizes
du -sh ~/medical_resources/*

# Count downloaded files
find ~/medical_resources -name "*.pdf" | wc -l
find ~/medical_resources -name "*.xml" | wc -l
find ~/medical_resources -name "*.txt" | wc -l
```

---

## After Downloads Complete

### Step 1: Verify Downloads
```bash
cd /home/dev/Development/irStudy/scripts
python3 verify_downloads.py --input ~/medical_resources
```

### Step 2: Process PDFs
```bash
# Process all PDFs (chunking, embedding, indexing)
python3 process_medical_resources.py --input ~/medical_resources --output data/processed
```

### Step 3: Index in Qdrant
```bash
# Index in vector database
python3 index_rag_resources.py --input data/processed --collection medical_knowledge_v2
```

### Step 4: Test Integration
```bash
# Test RAG retrieval
python3 test_rag_retrieval.py --query "acute coronary syndrome management"
```

---

## Troubleshooting

### StatPearls Download Fails
```bash
# Check API key is set
echo $NCBI_API_KEY

# Test API access
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=books&term=statpearls&api_key=$NCBI_API_KEY"

# Resume download (script auto-resumes)
python3 scripts/download_statpearls.py --output ~/medical_resources/statpearls
```

### Insufficient Disk Space
```bash
# Check available space
df -h

# Clean up temporary files
rm -rf /tmp/*

# Move to external drive
mv ~/medical_resources /mnt/external/
ln -s /mnt/external/medical_resources ~/medical_resources
```

### Slow Download Speed
```bash
# Use multiple parallel downloads (Cochrane, RANZCOG, etc.)
# Open multiple terminal windows
# Download different specialties simultaneously
```

### Rate Limited by NCBI
```bash
# If rate limited, wait 1 hour and resume
# Script automatically handles rate limiting with API key
# Without API key: 3 requests/second
# With API key: 10 requests/second
```

---

## Summary

**Automated Downloads** (Terminal 1):
- ✅ RACGP Red Book (~50 MB) - 2 minutes
- ✅ MeSH Database (~500 MB) - 5 minutes
- ✅ Australian Immunisation Handbook - Check project

**Automated with API Key** (Terminal 2):
- ⏳ StatPearls (~15-20 GB) - 4-6 hours

**Manual Downloads** (Terminal 3):
- ⏳ Cochrane Reviews (~5-10 GB) - 4-6 hours
- ⏳ RANZCOG (~500 MB) - 30 minutes
- ⏳ RANZCP (~200 MB) - 30 minutes
- ⏳ Stroke Guidelines (~100 MB) - 15 minutes
- ⏳ NSW Health (~1 GB) - 1 hour

**Registration Required** (1-2 weeks):
- ⏳ UMLS/SNOMED CT (~2 GB) - 1-3 days approval
- ⏳ MIMIC-III (~50 GB, optional) - 1-2 weeks approval

---

**Total Essential Downloads**: ~25-35 GB, 8-12 hours hands-on time

**Next Steps**: After downloads complete, return to main development and run processing scripts to integrate into RAG system.

---

**Questions?** Check the main download script log file:
```bash
tail -f ~/medical_resources/download_log_*.txt
```
