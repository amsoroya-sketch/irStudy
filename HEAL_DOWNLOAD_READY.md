# HEAL Playwright Downloader - Ready to Use

**Status:** ✅ Fully Functional
**Date:** 2026-02-03
**Test Results:** Successfully downloaded 3 melanoma images from HEAL

---

## What Was Fixed

### Issue 1: Virtual Environment Setup ✅
- **Problem:** `externally-managed-environment` error when installing pip packages
- **Solution:** Updated `scripts/setup_playwright.sh` to create and use Python virtual environment
- **Status:** Fixed and tested

### Issue 2: No File IDs Found ✅
- **Problem:** Script returned "✓ Found 0 unique file IDs" when searching HEAL
- **Root Cause:** Script was looking for `/file?id=` pattern, but HEAL uses `/details?id=`
- **Solution:** Updated ID extraction to use three methods:
  1. Regex search for `/details?id=(\d+)` pattern (primary)
  2. Regex search for `/file?id=(\d+)` pattern (fallback)
  3. Extract IDs from thumbnail parent links
- **Status:** Fixed and tested - successfully extracted IDs: 872205, 872258, 870235

### Issue 3: Download Failed (net::ERR_ABORTED) ✅
- **Problem:** Images failed to download with "net::ERR_ABORTED" error
- **Root Cause:** Script tried to download from `/file?id=` URLs which are blocked
- **Solution:** Updated download logic to extract actual image URLs from detail pages:
  1. Look for `/dl_files/` image paths in `<img>` tags (primary)
  2. Extract from JavaScript `imagezoom` initialization (fallback)
  3. Use download links as last resort
- **Status:** Fixed and tested - successfully downloaded 3 images (67KB, 21KB, 23KB)

---

## Test Results

```bash
$ python3 scripts/download_heal_playwright.py \
    --query "melanoma" \
    --collection dermatology_test \
    --max-images 3

✓ Found 3 unique file IDs
✓ Downloaded: 3 images
✓ Metadata JSON: dermatology_test_metadata.json
✓ Metadata CSV: dermatology_test_metadata.csv
```

**Downloaded Files:**
- `heal_870235.jpg` (67KB) - Melanoma in scalp
- `heal_872205.jpg` (21KB) - Melanoma metastasis to brain
- `heal_872258.jpg` (23KB) - Melanoma metastasis to temporal lobe

**Metadata Captured:**
- File ID
- Details URL
- Title
- Description
- Image URL (`/dl_files/` path)
- File path
- File size
- Download timestamp

---

## Usage

### 1. Setup (One-Time)

Already complete! Virtual environment exists with:
- ✅ Python venv at `venv/`
- ✅ Playwright 1.41.0
- ✅ BeautifulSoup4 4.12.3
- ✅ tqdm 4.67.1
- ✅ Chromium browser installed

### 2. Single Topic Download

```bash
# Activate virtual environment
source venv/bin/activate

# Download dermatology images (melanoma, psoriasis, etc.)
python3 scripts/download_heal_playwright.py \
    --query "melanoma OR psoriasis OR eczema" \
    --collection dermatology \
    --max-images 30

# Or use helper script (automatically activates venv)
./download_heal.sh \
    --query "electrocardiogram OR ECG" \
    --collection cardiology \
    --max-images 20
```

### 3. Batch Download (Recommended)

Download 10 images per topic across all AMC specialties (1000+ images):

```bash
# Using helper script
./download_heal_batch.sh --max-per-topic 10

# Or manually
source venv/bin/activate
python3 scripts/download_heal_batch.py --max-per-topic 10
```

**Specialties covered:**
- Dermatology (15 topics: melanoma, psoriasis, eczema, etc.)
- Cardiology (10 topics: ECG, MI, arrhythmia, etc.)
- Pulmonology (10 topics: pneumonia, TB, COPD, etc.)
- Neurology (10 topics: stroke, MS, epilepsy, etc.)
- Pathology (10 topics: histology, biopsy, cancer, etc.)
- Hematology (10 topics: anemia, leukemia, etc.)
- Gastroenterology (10 topics: ulcer, IBD, hepatitis, etc.)
- Orthopedics (10 topics: fracture, arthritis, etc.)
- Emergency (10 topics: trauma, acute abdomen, etc.)
- Pediatrics (10 topics: pediatric conditions)

**Total:** 95 topics × 10 images = 950+ images

### 4. Select Specific Specialties

```bash
# Download only dermatology and cardiology
./download_heal_batch.sh \
    --specialties dermatology cardiology \
    --max-per-topic 20

# Or 3 high-priority specialties
./download_heal_batch.sh \
    --specialties dermatology cardiology pulmonology \
    --max-per-topic 15
```

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
└── all_downloads_metadata.json  (combined from batch download)
```

**Metadata Format (JSON):**
```json
{
  "file_id": "872205",
  "details_url": "https://collections.lib.utah.edu/details?id=872205",
  "title": "Melanoma, malignant to brain",
  "description": "Melanoma, malignant to brain. Case A36-83...",
  "image_url": "https://collections.lib.utah.edu/dl_files/ef/25/ef2570...",
  "filepath": "data/medical_images/heal/dermatology/heal_872205.jpg",
  "filename": "heal_872205.jpg",
  "file_size_kb": 20,
  "downloaded_at": "2026-02-03T12:40:50.742137"
}
```

---

## Next Steps

### Option 1: Quick Test (5 minutes)

Download a small batch to verify everything works:

```bash
./download_heal.sh \
    --query "melanoma" \
    --collection test \
    --max-images 5 \
    --show-browser
```

This will:
- Show the browser so you can see what's happening
- Download only 5 images
- Save to `data/medical_images/heal/test/`

### Option 2: Phase 1 Pilot (30 minutes)

Download high-priority AMC specialties:

```bash
./download_heal_batch.sh \
    --specialties dermatology cardiology pulmonology \
    --max-per-topic 15
```

This will download:
- Dermatology: 15 topics × 15 images = 225 images
- Cardiology: 10 topics × 15 images = 150 images
- Pulmonology: 10 topics × 15 images = 150 images
- **Total: 525 images in ~30 minutes**

### Option 3: Complete Download (2-3 hours)

Download all AMC specialties:

```bash
./download_heal_batch.sh --max-per-topic 10
```

This will download:
- 95 topics across 10 specialties
- **Total: ~950 images in 2-3 hours**

---

## Integration with Existing System

Once images are downloaded, integrate with your existing RAG system:

### 1. Process Metadata
```bash
python3 scripts/process_image_metadata.py \
    --source data/medical_images/heal \
    --output data/heal_metadata.json
```

### 2. Enrich with HEAL Citations
```bash
python3 scripts/enrich_heal_metadata.py \
    --metadata data/heal_metadata.json
```

### 3. Upload to CDN (Cloudflare R2)
```bash
# Set credentials
export R2_ENDPOINT_URL="https://<account-id>.r2.cloudflarestorage.com"
export R2_ACCESS_KEY_ID="<your-key>"
export R2_SECRET_ACCESS_KEY="<your-secret>"

# Upload
python3 scripts/upload_to_cdn.py \
    --source data/medical_images/heal \
    --bucket irstudy-medical-images \
    --metadata data/heal_metadata.json
```

### 4. Index in Database
```bash
export DATABASE_URL="postgresql://user:pass@localhost/irstudy"

python3 scripts/index_images.py \
    --metadata data/heal_metadata.json
```

### 5. Query via Multimodal RAG

```python
from src.services.multimodal_rag_service import MultimodalRAGService

rag = MultimodalRAGService()
result = rag.query_with_images(
    query="melanoma Australian guidelines",
    specialty="dermatology",
    include_images=True
)

# Result will include HEAL images with citations:
# Image: (HEAL #872205, University of Utah, CC-BY-NC)
# Text: (Therapeutic Guidelines: Dermatology, Section 5.2.1, 2024)
```

---

## Time Estimates

| Task | Images | Time |
|------|--------|------|
| Quick test | 5 | 2 minutes |
| Single specialty | 50 | 10 minutes |
| Phase 1 pilot | 525 | 30 minutes |
| Complete download | 950+ | 2-3 hours |

**Factors affecting time:**
- Network speed
- HEAL server response time
- Rate limiting (2 seconds between requests)
- Headless vs. browser mode

---

## Troubleshooting

### Browser launch failed
```bash
# Install system dependencies
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2
```

### No results found
```bash
# Try broader search query
./download_heal.sh --query "dermatology" --collection test --max-images 10

# Or check HEAL manually
firefox "https://collections.lib.utah.edu/search?facet_setname_s=ehsl_heal"
```

### Download errors
```bash
# Show browser to debug
./download_heal.sh \
    --query "melanoma" \
    --collection test \
    --max-images 5 \
    --show-browser
```

---

## Scripts Summary

| Script | Purpose | Location |
|--------|---------|----------|
| `setup_playwright.sh` | Install dependencies | `scripts/` |
| `download_heal_playwright.py` | Single topic download | `scripts/` |
| `download_heal_batch.py` | Multi-topic batch download | `scripts/` |
| `download_heal.sh` | Helper wrapper (venv) | Root |
| `download_heal_batch.sh` | Helper wrapper (venv) | Root |

---

## Success Metrics

✅ **Setup:** Virtual environment with all dependencies
✅ **ID Extraction:** Finds file IDs from search results (872205, 872258, 870235)
✅ **Download:** Successfully downloads images from `/dl_files/` URLs
✅ **Metadata:** Captures title, description, file size, timestamps
✅ **Batch Processing:** Supports 95 AMC topics across 10 specialties
✅ **Rate Limiting:** Built-in delays to respect HEAL server
✅ **Error Handling:** Graceful fallback and debugging output

---

## Documentation

- **Quick Start:** `HEAL_PLAYWRIGHT_QUICKSTART.md`
- **Complete Guide:** `HEAL_INTEGRATION_GUIDE.md`
- **Repository Assessment:** `MEDICAL_IMAGE_REPOSITORIES_ASSESSMENT.md`
- **Dataset Download:** `DATASET_DOWNLOAD_GUIDE.md`

---

**Ready to use!** Start with Option 1 (Quick Test) above to verify your setup, then proceed to Phase 1 or complete download.
