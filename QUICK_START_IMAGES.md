# Quick Start: Medical Image Integration
**Get medical images into your AMC exam prep platform in 3 steps**

---

## Prerequisites (5 minutes)

```bash
# 1. Install Python dependencies
pip3 install requests beautifulsoup4 tqdm Pillow boto3 psycopg2-binary

# 2. Create data directory
mkdir -p data/medical_images/{medpix,heal,nih_chest_xray,malaria}

# 3. Verify scripts are executable
chmod +x scripts/download_medical_images.sh
chmod +x scripts/*.py
```

---

## Step 1: Download Images (1-2 hours)

### Option A: Automated Download (Recommended)

```bash
# Run master download script
./scripts/download_medical_images.sh

# This will guide you through:
# - Malaria dataset (automated)
# - NIH Chest X-Ray (via Kaggle - requires setup)
# - MedPix (semi-automated - requires account)
# - HEAL (manual instructions provided)
```

### Option B: Manual Download (Most Control)

**MedPix (50 cases - Priority #1):**
```bash
# 1. Register account: https://medpix.nlm.nih.gov/register
# 2. Login and search:
#    - "pneumonia" → Download 10 cases
#    - "melanoma" → Download 10 cases
#    - "myocardial infarction" → Download 10 cases
#    - "stroke" → Download 10 cases
#    - "fracture" → Download 10 cases
# 3. Save to: data/medical_images/medpix/<specialty>/
```

**HEAL (50 images):**
```bash
# 1. Visit: https://library.med.utah.edu/heal/
# 2. Browse Dermatology collection
# 3. Download 50 images
# 4. Save to: data/medical_images/heal/dermatology/
```

**NIH Chest X-Ray (100 images):**
```bash
# Via Kaggle (easiest)
pip3 install kaggle

# Setup Kaggle API
# 1. Get API token: https://www.kaggle.com/settings → Create New API Token
# 2. Save to: ~/.kaggle/kaggle.json

# Download dataset
kaggle datasets download -d nih-chest-xrays/sample
unzip sample.zip -d data/medical_images/nih_chest_xray/
```

---

## Step 2: Process & Upload (30 minutes)

```bash
# 1. Extract metadata from downloaded images
python3 scripts/process_image_metadata.py \
    --source data/medical_images \
    --output data/image_metadata.json

# Output: data/image_metadata.json (metadata for all images)

# 2. (Optional) Manually enrich metadata
# Edit data/image_metadata.json to add:
# - amc_relevance (1-5 rating)
# - tags (e.g., ["pneumonia", "chest-xray", "consolidation"])

# 3. Setup Cloudflare R2 CDN
# - Create Cloudflare account: https://cloudflare.com
# - Create R2 bucket: "irstudy-medical-images"
# - Get API credentials from R2 dashboard

export R2_ENDPOINT_URL="https://<account-id>.r2.cloudflarestorage.com"
export R2_ACCESS_KEY_ID="<your-key>"
export R2_SECRET_ACCESS_KEY="<your-secret>"

# 4. Upload to CDN (with automatic thumbnail generation)
python3 scripts/upload_to_cdn.py \
    --source data/medical_images \
    --bucket irstudy-medical-images \
    --metadata data/image_metadata.json \
    --cdn-url https://cdn.irstudy.com

# Output: CDN URLs added to data/image_metadata.json
```

---

## Step 3: Index in Database (5 minutes)

```bash
# Setup database connection
export DATABASE_URL="postgresql://irstudy:password@localhost/irstudy"

# Index images in PostgreSQL
python3 scripts/index_images.py \
    --metadata data/image_metadata.json

# This creates:
# - medical_images table
# - Full-text search indexes
# - Fast query indexes (specialty, modality, tags)
```

---

## Verify Setup

```bash
# Check database
psql $DATABASE_URL -c "SELECT source, COUNT(*) FROM medical_images GROUP BY source;"

# Expected output:
#     source      | count
# ----------------+-------
#  medpix         |    50
#  heal           |    50
#  nih_chest_xray |   100
#  malaria        |   150

# Test image search
psql $DATABASE_URL -c "
  SELECT external_id, diagnosis, modality, cdn_url
  FROM medical_images
  WHERE diagnosis ILIKE '%pneumonia%'
  LIMIT 5;
"
```

---

## Usage in Your App

### Backend: Multimodal RAG Query

```python
# src/services/multimodal_rag_service.py
from src.services.multimodal_rag_service import MultimodalRAGService

rag = MultimodalRAGService()

# Query for MCQ with images
result = rag.query_with_images(
    query="community-acquired pneumonia treatment",
    specialty="pulmonology",
    include_images=True,
    max_images=2
)

# Returns:
# {
#   'text_citations': [...],  # From existing RAG
#   'images': [
#     {
#       'external_id': 'medpix_12345',
#       'diagnosis': 'Community-acquired pneumonia',
#       'cdn_url': 'https://cdn.irstudy.com/images/medpix/...',
#       'citation': '(MedPix Case #12345, Public Domain)'
#     }
#   ],
#   'combined_context': '...'  # For LLM generation
# }
```

### Frontend: Display Images

```typescript
// frontend/src/components/MCQWithImage.tsx
import { MedicalImageViewer } from './MedicalImageViewer';

const MCQComponent = ({ mcq }) => {
  return (
    <div>
      <h3>{mcq.scenario}</h3>

      {/* Display clinical images */}
      {mcq.images && (
        <MedicalImageViewer
          images={mcq.images}
          caption="Chest X-ray showing right lower lobe consolidation"
        />
      )}

      <div className="options">
        {/* MCQ options */}
      </div>

      <div className="citation">
        {mcq.images.map(img => img.citation).join('; ')}
      </div>
    </div>
  );
};
```

---

## Cost Summary

**Phase 1 Pilot (150 images):**
- Storage: 5 GB (~$1/month)
- Bandwidth: 50 GB/month (~$4/month)
- **Total: ~$5/month**

**Scaling to 5,000 images:**
- Storage: 100 GB (~$3/month)
- Bandwidth: 500 GB/month (~$15/month)
- **Total: ~$18/month**

---

## Troubleshooting

### "MedPix login failed"
```bash
# Check credentials
# Visit: https://medpix.nlm.nih.gov/profile
# Verify account is active
```

### "No images with CDN URL to index"
```bash
# You forgot to upload to CDN first
python3 scripts/upload_to_cdn.py --source data/medical_images ...
```

### "Database connection error"
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

### "Kaggle API not found"
```bash
# Install kaggle CLI
pip3 install kaggle

# Setup credentials
# 1. Get token from https://www.kaggle.com/settings
# 2. Save to ~/.kaggle/kaggle.json
# 3. Set permissions: chmod 600 ~/.kaggle/kaggle.json
```

---

## Next Steps

Once images are indexed:

1. **Generate Image-Enhanced MCQs**
   ```bash
   python3 scripts/generate_mcqs_with_images.py \
       --specialty cardiology \
       --count 10
   ```

2. **Create OSCE Stations with Images**
   ```bash
   python3 scripts/generate_osces_with_images.py \
       --topic "chest pain assessment" \
       --include-images true
   ```

3. **Add 3D Anatomy**
   ```typescript
   // Add Z-Anatomy to OSCE stations
   <AnatomyViewer3D
     structure="rotator_cuff"
     system="muscular"
   />
   ```

---

## Full Documentation

- **Comprehensive Guide:** [MEDICAL_IMAGE_REPOSITORIES_ASSESSMENT.md](MEDICAL_IMAGE_REPOSITORIES_ASSESSMENT.md)
- **Download Details:** [DATASET_DOWNLOAD_GUIDE.md](DATASET_DOWNLOAD_GUIDE.md)
- **Architecture:** See "Technical Integration Architecture" section in assessment

---

## Support

Questions? Check:
- LHC Downloads: https://lhncbc.nlm.nih.gov/LHC-downloads/downloads.html
- MedPix Help: https://medpix.nlm.nih.gov/help
- Cloudflare R2 Docs: https://developers.cloudflare.com/r2/

---

**Estimated Time: 2-3 hours to complete full setup**

**Result: 150+ medical images ready for AMC exam MCQs and OSCEs**
