#!/bin/bash
################################################################################
# Fixed Medical Resources Download Script
# Purpose: Download medical resources with correct URLs
# Output: /mnt/data/medical_resources/
################################################################################

set -e

DOWNLOAD_DIR="/mnt/data/medical_resources"
LOG_FILE="${DOWNLOAD_DIR}/logs/fixed_downloads_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

mkdir -p "${DOWNLOAD_DIR}"/{racgp,mesh,stroke_foundation,immunisation}

echo "============================================================"
echo "Fixed Medical Resources Download"
echo "============================================================"
echo ""

#------------------------------------------------------------------------------
# 1. RACGP Red Book 10th Edition (Correct PDF URL)
#------------------------------------------------------------------------------
log "Downloading RACGP Red Book 10th Edition (Correct URL)..."
wget -O "${DOWNLOAD_DIR}/racgp/red_book_10th_edition.pdf" \
    "https://www.racgp.org.au/FSDEDEV/media/documents/Clinical%20Resources/Guidelines/Red%20Book/Guidelines-for-preventive-activities-in-general-practice.pdf" \
    2>&1 | tee -a "${LOG_FILE}"

if [ -f "${DOWNLOAD_DIR}/racgp/red_book_10th_edition.pdf" ]; then
    SIZE=$(du -h "${DOWNLOAD_DIR}/racgp/red_book_10th_edition.pdf" | cut -f1)
    log "✓ RACGP Red Book downloaded: ${SIZE}"
else
    log "✗ RACGP Red Book download failed"
fi

#------------------------------------------------------------------------------
# 2. MeSH Database 2025 (Descriptors XML)
#------------------------------------------------------------------------------
log "Downloading MeSH 2025 Descriptors XML..."
wget -O "${DOWNLOAD_DIR}/mesh/desc2025.xml" \
    "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/desc2025.xml" \
    2>&1 | tee -a "${LOG_FILE}"

if [ -f "${DOWNLOAD_DIR}/mesh/desc2025.xml" ]; then
    SIZE=$(du -h "${DOWNLOAD_DIR}/mesh/desc2025.xml" | cut -f1)
    log "✓ MeSH 2025 Descriptors downloaded: ${SIZE}"
else
    log "✗ MeSH download failed - trying alternate URL..."
    # Try the qualifiers file as backup
    wget -O "${DOWNLOAD_DIR}/mesh/qual2025.xml" \
        "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/qual2025.xml" \
        2>&1 | tee -a "${LOG_FILE}" || log "MeSH alternate download also failed"
fi

#------------------------------------------------------------------------------
# 3. Stroke Foundation Guidelines (GP Summary + Full Guidelines)
#------------------------------------------------------------------------------
log "Downloading Stroke Foundation Clinical Guidelines..."

# GP Summary (June 2025)
wget -O "${DOWNLOAD_DIR}/stroke_foundation/gp_clinical_guidelines_summary_jun25.pdf" \
    "https://informme.org.au/media/grmfajgt/general-practitioners-clinical-guidelines-summary_jun25.pdf" \
    2>&1 | tee -a "${LOG_FILE}"

# Full Guidelines PDF (Chapter 1 - Pre-hospital care)
wget -O "${DOWNLOAD_DIR}/stroke_foundation/full_guidelines_chapter1.pdf" \
    "https://files.magicapp.org/guideline/4ae82c3c-1f47-4f2a-8cc2-a0f2e1e5d6fa/published_guideline_6172-8_1.pdf" \
    2>&1 | tee -a "${LOG_FILE}"

# Full Guidelines PDF (Chapter 8 - Community participation)
wget -O "${DOWNLOAD_DIR}/stroke_foundation/full_guidelines_chapter8.pdf" \
    "https://files.magicapp.org/guideline/89b1578e-bfeb-463e-a9c3-3c890911bc85/published_guideline_7394-8_0.pdf" \
    2>&1 | tee -a "${LOG_FILE}"

if [ -f "${DOWNLOAD_DIR}/stroke_foundation/gp_clinical_guidelines_summary_jun25.pdf" ]; then
    SIZE=$(du -sh "${DOWNLOAD_DIR}/stroke_foundation/" | cut -f1)
    log "✓ Stroke Guidelines downloaded: ${SIZE}"
else
    log "✗ Stroke Guidelines download failed"
fi

#------------------------------------------------------------------------------
# 4. Australian Immunisation Handbook (NOTE: No PDF available)
#------------------------------------------------------------------------------
log "NOTE: Australian Immunisation Handbook is online-only (no PDF)"
log "  - Online: https://immunisationhandbook.health.gov.au/"
log "  - Mobile app: iOS/Android (Immunisation Handbook)"
echo "Australian Immunisation Handbook is a living online document" > "${DOWNLOAD_DIR}/immunisation/README.txt"
echo "Access at: https://immunisationhandbook.health.gov.au/" >> "${DOWNLOAD_DIR}/immunisation/README.txt"
echo "Mobile app available on iOS/Android app stores" >> "${DOWNLOAD_DIR}/immunisation/README.txt"

#------------------------------------------------------------------------------
# Summary
#------------------------------------------------------------------------------
echo ""
echo "============================================================"
log "Download Complete!"
echo "============================================================"
echo ""
log "Downloaded resources:"
du -sh "${DOWNLOAD_DIR}/racgp" 2>/dev/null && log "  ✓ RACGP Red Book"
du -sh "${DOWNLOAD_DIR}/mesh" 2>/dev/null && log "  ✓ MeSH Database 2025"
du -sh "${DOWNLOAD_DIR}/stroke_foundation" 2>/dev/null && log "  ✓ Stroke Foundation Guidelines"
echo ""
log "Total size:"
du -sh "${DOWNLOAD_DIR}"
echo ""
log "Log saved to: ${LOG_FILE}"
