# HEAL Playwright Downloader - Quick Start
**Fully Automated Image Download for AMC Exam Prep**

**Created:** 2026-02-03
**Status:** Ready to use

---

## What This Does

**Fully automated** download of HEAL medical images using Playwright browser automation:

1. ✅ Searches HEAL collection by topic
2. ✅ Extracts all file IDs automatically
3. ✅ Downloads images with metadata
4. ✅ Saves in organized folders
5. ✅ No manual clicking required!

---

## Installation (5 minutes)

```bash
# Run setup script
chmod +x scripts/setup_playwright.sh
./scripts/setup_playwright.sh

# This installs:
# - playwright
# - beautifulsoup4
# - tqdm
# - Chromium browser
```

**Manual installation:**
```bash
pip3 install playwright beautifulsoup4 tqdm
playwright install chromium
```

---

## Quick Test (2 minutes)

Download 5 dermatology images to test:

```bash
python3 scripts/download_heal_playwright.py \
    --query "melanoma" \
    --collection dermatology \
    --max-images 5 \
    --show-browser
```

**Expected output:**
```
Searching HEAL Collection...
✓ Found 12 unique file IDs
Extracting metadata...
✓ Downloaded 5 images
```

---

## Usage Examples

### 1. Single Topic Download

```bash
# Dermatology - Melanoma (30 images)
python3 scripts/download_heal_playwright.py \
    --query "melanoma" \
    --collection dermatology \
    --max-images 30

# Cardiology - ECG (20 images)
python3 scripts/download_heal_playwright.py \
    --query "electrocardiogram arrhythmia" \
    --collection cardiology \
    --max-images 20

# Pulmonology - Pneumonia (15 images)
python3 scripts/download_heal_playwright.py \
    --query "pneumonia chest xray" \
    --collection pulmonology \
    --max-images 15
```

### 2. Multiple Topics with Boolean Search

```bash
# Dermatology - Multiple conditions
python3 scripts/download_heal_playwright.py \
    --query "melanoma OR psoriasis OR eczema OR dermatitis" \
    --collection dermatology \
    --max-images 50

# Cardiology - Heart conditions
python3 scripts/download_heal_playwright.py \
    --query "myocardial infarction OR heart failure OR angina" \
    --collection cardiology \
    --max-images 30
```

### 3. Batch Download (All AMC Topics)

**Recommended for Phase 1:**

```bash
# Download 10 images per topic across all specialties
python3 scripts/download_heal_batch.py \
    --max-per-topic 10

# This downloads from:
# - Dermatology (15 topics)
# - Cardiology (10 topics)
# - Pulmonology (10 topics)
# - Neurology (10 topics)
# - Pathology (10 topics)
# - Hematology (10 topics)
# - Gastroenterology (10 topics)
# - Orthopedics (10 topics)
# - Emergency (10 topics)
# - Pediatrics (10 topics)
#
# Total: ~1000 images!
```

**Select specific specialties:**

```bash
# Download only dermatology and cardiology
python3 scripts/download_heal_batch.py \
    --specialties dermatology cardiology \
    --max-per-topic 20

# Download only high-priority specialties for AMC
python3 scripts/download_heal_batch.py \
    --specialties dermatology cardiology pulmonology \
    --max-per-topic 15
```

---

## Script Options

### download_heal_playwright.py

| Option | Description | Default |
|--------|-------------|---------|
| `--query` | Search query (required) | - |
| `--collection` | Collection name (required) | - |
| `--max-images` | Maximum images to download | 50 |
| `--output` | Output directory | `data/medical_images/heal` |
| `--show-browser` | Show browser window (debugging) | False (headless) |

### download_heal_batch.py

| Option | Description | Default |
|--------|-------------|---------|
| `--specialties` | Specialties to download | all |
| `--max-per-topic` | Max images per topic | 10 |
| `--output` | Output directory | `data/medical_images/heal` |
| `--show-browser` | Show browser window (debugging) | False (headless) |

---

## Output Structure

```
data/medical_images/heal/
├── dermatology/
│   ├── heal_889750.jpg
│   ├── heal_889751.jpg
│   ├── ...
│   ├── dermatology_metadata.json
│   └── dermatology_metadata.csv
│
├── cardiology/
│   ├── heal_890123.jpg
│   ├── ...
│   ├── cardiology_metadata.json
│   └── cardiology_metadata.csv
│
└── all_downloads_metadata.json  (combined)
```

**Metadata format:**
```json
{
  "file_id": "889750",
  "url": "https://collections.lib.utah.edu/file?id=889750",
  "title": "Melanoma - Clinical Presentation",
  "description": "Irregular pigmented lesion...",
  "subject": "Dermatology; Skin Cancer; Melanoma",
  "collection": "Knowledge Weavers Dermatology",
  "rights": "CC-BY-NC",
  "image_url": "https://collections.lib.utah.edu/file?id=889750",
  "filepath": "data/medical_images/heal/dermatology/heal_889750.jpg",
  "filename": "heal_889750.jpg",
  "file_size_kb": 245,
  "downloaded_at": "2026-02-03T14:30:00"
}
```

---

## Complete Workflow

### Phase 1: Download Images (1-2 hours)

```bash
# Option A: Single specialty (fast, controlled)
python3 scripts/download_heal_playwright.py \
    --query "melanoma OR psoriasis OR eczema" \
    --collection dermatology \
    --max-images 50

# Option B: All specialties (comprehensive)
python3 scripts/download_heal_batch.py \
    --max-per-topic 10
```

### Phase 2: Process Metadata (5 minutes)

```bash
# Extract metadata from all downloaded images
python3 scripts/process_image_metadata.py \
    --source data/medical_images/heal \
    --output data/heal_metadata.json
```

### Phase 3: Enrich HEAL Metadata (2 minutes)

```bash
# Add HEAL-specific fields (citation, license, tags)
python3 scripts/enrich_heal_metadata.py \
    --metadata data/heal_metadata.json
```

### Phase 4: Upload to CDN (10 minutes)

```bash
# Setup R2 credentials
export R2_ENDPOINT_URL="https://<account-id>.r2.cloudflarestorage.com"
export R2_ACCESS_KEY_ID="<your-key>"
export R2_SECRET_ACCESS_KEY="<your-secret>"

# Upload images
python3 scripts/upload_to_cdn.py \
    --source data/medical_images/heal \
    --bucket irstudy-medical-images \
    --metadata data/heal_metadata.json
```

### Phase 5: Index in Database (2 minutes)

```bash
# Index in PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost/irstudy"

python3 scripts/index_images.py \
    --metadata data/heal_metadata.json
```

---

## Time & Resource Estimates

### Download Time

| Images | Headless Mode | With Browser |
|--------|---------------|--------------|
| 50 images | 5-10 minutes | 10-15 minutes |
| 200 images | 20-30 minutes | 40-50 minutes |
| 1000 images | 1.5-2 hours | 3-4 hours |

**Factors:**
- Network speed
- HEAL server response time
- Rate limiting (2 seconds between requests)

### Storage Requirements

| Images | Original | With Thumbnails | CDN |
|--------|----------|-----------------|-----|
| 50 | ~10 MB | ~12 MB | ~15 MB |
| 200 | ~40 MB | ~50 MB | ~60 MB |
| 1000 | ~200 MB | ~250 MB | ~300 MB |

---

## Troubleshooting

### "playwright: command not found"

```bash
# Install playwright CLI
pip3 install playwright

# Install browser
playwright install chromium
```

### "Browser launch failed"

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

### "No results found"

```bash
# Try broader search query
python3 scripts/download_heal_playwright.py \
    --query "dermatology" \
    --collection dermatology \
    --max-images 20

# Or check HEAL manually:
open https://collections.lib.utah.edu/search?facet_setname_s=ehsl_heal
```

### "Download failed"

```bash
# Show browser to debug
python3 scripts/download_heal_playwright.py \
    --query "melanoma" \
    --collection dermatology \
    --max-images 5 \
    --show-browser

# Check image URL format in metadata JSON
cat data/medical_images/heal/dermatology/dermatology_metadata.json | jq '.[0].image_url'
```

### Rate Limiting

If you get rate limited (very rare):
- Reduce concurrent downloads
- Increase sleep time in script (default: 2 seconds)
- Download during off-peak hours

---

## Recommended Download Strategy

### Phase 1 Pilot (50-100 images, 30 minutes)

**High-priority specialties for AMC:**

```bash
# Dermatology (30 images)
python3 scripts/download_heal_playwright.py \
    --query "melanoma OR basal cell carcinoma OR psoriasis OR eczema" \
    --collection dermatology \
    --max-images 30

# Cardiology ECG (20 images)
python3 scripts/download_heal_playwright.py \
    --query "electrocardiogram OR ECG" \
    --collection cardiology \
    --max-images 20

# Total: 50 images in ~30 minutes
```

### Phase 2 Expansion (200-500 images, 1-2 hours)

```bash
# All high-priority specialties
python3 scripts/download_heal_batch.py \
    --specialties dermatology cardiology pulmonology neurology \
    --max-per-topic 15
```

### Phase 3 Comprehensive (1000+ images, 2-3 hours)

```bash
# All AMC exam specialties
python3 scripts/download_heal_batch.py \
    --max-per-topic 10
```

---

## Advantages Over Manual Download

| Feature | Manual | Playwright | Improvement |
|---------|--------|------------|-------------|
| **Time for 50 images** | 2-3 hours | 10 minutes | 12-18x faster |
| **Metadata capture** | Copy-paste | Automatic | 100% accurate |
| **File naming** | Manual | Systematic | Consistent |
| **Citation extraction** | Manual | Automatic | No errors |
| **Bulk download** | Impossible | Easy | Scalable |

---

## Integration with Existing System

Once downloaded, HEAL images integrate seamlessly with your existing pipeline:

```bash
# Same workflow as MedPix, NIH, etc.
python3 scripts/process_image_metadata.py --source data/medical_images/heal
python3 scripts/enrich_heal_metadata.py --metadata data/heal_metadata.json
python3 scripts/upload_to_cdn.py --source data/medical_images/heal ...
python3 scripts/index_images.py --metadata data/heal_metadata.json
```

**Query via multimodal RAG:**

```python
from src.services.multimodal_rag_service import MultimodalRAGService

rag = MultimodalRAGService()
result = rag.query_with_images(
    query="melanoma Australian guidelines",
    specialty="dermatology",
    include_images=True
)

# HEAL images will be included automatically
```

---

## Next Steps

1. **Test installation:**
   ```bash
   ./scripts/setup_playwright.sh
   ```

2. **Run pilot download:**
   ```bash
   python3 scripts/download_heal_playwright.py \
       --query "melanoma" \
       --collection dermatology \
       --max-images 5 \
       --show-browser
   ```

3. **Scale to Phase 1:**
   ```bash
   python3 scripts/download_heal_batch.py \
       --specialties dermatology cardiology \
       --max-per-topic 20
   ```

4. **Process and integrate:**
   - Follow complete workflow above
   - Upload to CDN
   - Index in database
   - Generate MCQs with images!

---

## Support

**Script issues?**
- Check error messages in console
- Use `--show-browser` to debug
- Verify HEAL website is accessible

**Questions?**
- See full guide: `HEAL_INTEGRATION_GUIDE.md`
- Check main assessment: `MEDICAL_IMAGE_REPOSITORIES_ASSESSMENT.md`

---

**Estimated total time: 2-3 hours for complete HEAL integration (1000+ images)**

**Result: Fully automated, scalable medical image download for AMC exam prep!**
