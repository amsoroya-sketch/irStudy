#!/bin/bash
# Master script to download all Phase 1 medical images

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data/medical_images"

echo "==================================="
echo "Medical Image Dataset Downloader"
echo "Phase 1: Pilot (150 images)"
echo "==================================="
echo ""

# Create directory structure
mkdir -p "$DATA_DIR"/{nih_chest_xray,malaria,medpix,heal}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."
for cmd in wget curl unzip python3; do
    if ! command_exists $cmd; then
        echo "Error: $cmd not found. Please install it."
        exit 1
    fi
done
echo "✓ All prerequisites installed"
echo ""

# 1. Download NIH Chest X-Ray sample
echo "=== Step 1: NIH Chest X-Ray Dataset ==="
if [ ! -d "$DATA_DIR/nih_chest_xray_sample" ]; then
    echo "Note: Full dataset is 42GB. For pilot, we'll use Kaggle sample."
    echo "To download:"
    echo "  1. Install kaggle: pip3 install kaggle"
    echo "  2. Setup credentials: ~/.kaggle/kaggle.json"
    echo "  3. Run: kaggle datasets download -d nih-chest-xrays/sample"
    echo ""
    echo "Skipping automated download (requires Kaggle setup)"
else
    echo "✓ NIH Chest X-Ray sample already downloaded"
fi
echo ""

# 2. Download Malaria dataset
echo "=== Step 2: Malaria Screener Dataset ==="
if [ ! -f "$DATA_DIR/malaria/NLM-MalariaDataset.zip" ]; then
    echo "Downloading from NLM..."
    cd "$DATA_DIR/malaria"

    # Try direct download
    wget -O NLM-MalariaDataset.zip \
        "https://lhncbc.nlm.nih.gov/LHC-downloads/dataset/NLM-MalariaDataset.zip" \
        || echo "Warning: Direct download failed. Try manual download."

    if [ -f "NLM-MalariaDataset.zip" ]; then
        echo "Unzipping..."
        unzip -q NLM-MalariaDataset.zip
        echo "✓ Malaria dataset downloaded"
    fi
else
    echo "✓ Malaria dataset already downloaded"
fi
cd "$PROJECT_DIR"
echo ""

# 3. MedPix (requires credentials)
echo "=== Step 3: MedPix Cases ==="
echo "MedPix requires account credentials."
echo "Options:"
echo "  A) Manual download (recommended for pilot)"
echo "     - Visit: https://medpix.nlm.nih.gov/"
echo "     - Search and download 100 cases"
echo "  B) Automated download"
echo "     - Run: python3 scripts/download_medpix_api.py"
echo ""
read -p "Run automated MedPix download? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "$SCRIPT_DIR/download_medpix_api.py" ]; then
        python3 "$SCRIPT_DIR/download_medpix_api.py"
    else
        echo "Error: download_medpix_api.py not found"
    fi
else
    echo "Skipping automated MedPix download"
fi
echo ""

# 4. HEAL (manual only)
echo "=== Step 4: HEAL Images ==="
echo "HEAL requires manual download."
echo "  1. Visit: https://library.med.utah.edu/heal/"
echo "  2. Browse Dermatology collection"
echo "  3. Download 50 images"
echo "  4. Save to: $DATA_DIR/heal/"
echo ""

# Summary
echo "==================================="
echo "Download Summary"
echo "==================================="
echo "Downloaded to: $DATA_DIR"
echo ""
echo "Next steps:"
echo "  1. Complete manual downloads (MedPix, HEAL)"
echo "  2. Process metadata: python3 scripts/process_image_metadata.py"
echo "  3. Upload to CDN: python3 scripts/upload_to_cdn.py"
echo "  4. Index in database: python3 scripts/index_images.py"
echo ""
echo "See DATASET_DOWNLOAD_GUIDE.md for detailed instructions."
