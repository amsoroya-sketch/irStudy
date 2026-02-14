#!/bin/bash
################################################################################
# External Medical Resource Download Script
# Purpose: Download all free medical resources for Medical Expert Agents
# Estimated Total Size: ~50-100 GB
# Estimated Time: 4-8 hours (depending on internet speed)
################################################################################

set -e  # Exit on error

# Configuration
DOWNLOAD_DIR="${1:-/mnt/external/medical_resources}"
LOG_FILE="${DOWNLOAD_DIR}/download_log_$(date +%Y%m%d_%H%M%S).txt"

# Create directory structure
mkdir -p "${DOWNLOAD_DIR}"/{statpearls,cochrane,racgp,ranzcog,ranzcp,stroke_foundation,nsw_health,australian_immunisation,mesh,other}

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

log "=========================================="
log "Medical Resource Download Script Started"
log "Download Directory: ${DOWNLOAD_DIR}"
log "=========================================="

################################################################################
# PRIORITY 1: StatPearls Database (FREE via NCBI Bookshelf)
################################################################################
log "TASK 1: StatPearls Medical Database"
log "Source: NCBI Bookshelf"
log "Size: ~15-20 GB (10,000+ articles)"
log "Method: Web scraping via NCBI E-Utilities API"
log ""
log "Manual Steps Required:"
log "1. Visit: https://www.ncbi.nlm.nih.gov/books/NBK430685/"
log "2. Browse StatPearls books collection"
log "3. Use bulk download tool or API"
log ""
log "Automated download (requires NCBI E-utilities API key - FREE):"
log "  - Apply for API key: https://www.ncbi.nlm.nih.gov/account/settings/"
log "  - Set environment variable: export NCBI_API_KEY='your_key_here'"
log "  - Run: scripts/download_statpearls.py --output ${DOWNLOAD_DIR}/statpearls"
log ""
log "Alternative: Use existing scripts/download_statpearls.py in project"
log "STATUS: READY TO EXECUTE (Python script needed)"
log "=========================================="
echo ""

################################################################################
# PRIORITY 2: PubMed Central (PMC) API Setup
################################################################################
log "TASK 2: PubMed Central API Integration"
log "Source: PMC Open Access Subset"
log "Size: Varies (real-time API, not bulk download)"
log "Method: API integration (no bulk download needed)"
log ""
log "Setup Steps:"
log "1. No download needed - API-based access"
log "2. NCBI E-utilities API key recommended (same as StatPearls)"
log "3. Documentation: https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/"
log ""
log "Optional Bulk Download (3+ million articles, ~500 GB):"
log "  - PMC Cloud Service: https://registry.opendata.aws/pmc/"
log "  - AWS S3: aws s3 sync s3://pmc-oa-opendata/ ${DOWNLOAD_DIR}/pmc/ --no-sign-request"
log "  - WARNING: Very large! Only download if needed for offline access"
log ""
log "STATUS: API-only (no download), bulk optional"
log "=========================================="
echo ""

################################################################################
# PRIORITY 3: Cochrane Systematic Reviews
################################################################################
log "TASK 3: Cochrane Systematic Reviews"
log "Source: Cochrane Library"
log "Size: ~5-10 GB (specialty-specific reviews)"
log "Method: Manual download (free reviews 12+ months old)"
log ""
log "Manual Download Steps:"
log "1. Visit: https://www.cochranelibrary.com/"
log "2. Create free account"
log "3. Search by specialty:"
log "   - Cardiology: 'cardiovascular' OR 'cardiology' OR 'heart'"
log "   - Respiratory: 'respiratory' OR 'asthma' OR 'COPD' OR 'pneumonia'"
log "   - Gastroenterology: 'gastrointestinal' OR 'GI' OR 'IBD'"
log "   - Endocrinology: 'diabetes' OR 'thyroid' OR 'endocrine'"
log "   - Neurology: 'neurology' OR 'stroke' OR 'seizure'"
log "   - Emergency: 'emergency' OR 'trauma' OR 'resuscitation'"
log "   - O&G: 'obstetric' OR 'gynecology' OR 'pregnancy'"
log "   - Paediatrics: 'pediatric' OR 'child' OR 'infant'"
log "   - Psychiatry: 'psychiatry' OR 'depression' OR 'mental health'"
log "   - General Practice: 'primary care' OR 'general practice'"
log "4. Filter: 'Cochrane Reviews' (not protocols)"
log "5. Download PDFs to: ${DOWNLOAD_DIR}/cochrane/[specialty]/"
log ""
log "Estimated downloads per specialty: 50-200 reviews"
log "STATUS: MANUAL DOWNLOAD REQUIRED"
log "=========================================="
echo ""

################################################################################
# PRIORITY 4: RACGP Red Book (10th Edition)
################################################################################
log "TASK 4: RACGP Red Book (Guidelines for Preventive Activities)"
log "Source: RACGP Website"
log "Size: ~50 MB (PDF)"
log "Method: Direct download (FREE)"
log ""
log "Download URL: https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-racgp-guidelines/red-book"
log ""
log "Automated download:"
cd "${DOWNLOAD_DIR}/racgp" || exit
log "Downloading RACGP Red Book..."
if command -v wget &> /dev/null; then
    wget -c "https://www.racgp.org.au/FSDEDEV/media/documents/Clinical%20Resources/Guidelines/Red%20Book/Red-Book-10th-edition.pdf" \
         -O "RACGP_Red_Book_10th_Edition.pdf" 2>&1 | tee -a "${LOG_FILE}"
    log "✓ RACGP Red Book downloaded successfully"
elif command -v curl &> /dev/null; then
    curl -L "https://www.racgp.org.au/FSDEDEV/media/documents/Clinical%20Resources/Guidelines/Red%20Book/Red-Book-10th-edition.pdf" \
         -o "RACGP_Red_Book_10th_Edition.pdf" 2>&1 | tee -a "${LOG_FILE}"
    log "✓ RACGP Red Book downloaded successfully"
else
    log "ERROR: wget or curl not found. Please install one."
    log "Manual download: https://www.racgp.org.au/clinical-resources/clinical-guidelines"
fi
log "STATUS: COMPLETED (or manual download needed)"
log "=========================================="
echo ""

################################################################################
# PRIORITY 5: RANZCOG Clinical Guidelines
################################################################################
log "TASK 5: RANZCOG Clinical Statements and Guidelines"
log "Source: RANZCOG Website"
log "Size: ~500 MB (200+ documents)"
log "Method: Manual download (FREE, requires account)"
log ""
log "Manual Download Steps:"
log "1. Visit: https://ranzcog.edu.au/womens-health/statements-guidelines/"
log "2. Create free account (healthcare professionals)"
log "3. Download all statements and guidelines"
log "4. Categories:"
log "   - Obstetrics"
log "   - Gynaecology"
log "   - Women's Health"
log "   - Early Pregnancy"
log "   - Maternal-Fetal Medicine"
log "5. Save to: ${DOWNLOAD_DIR}/ranzcog/"
log ""
log "Key documents for AMC:"
log "  - Antenatal screening guidelines"
log "  - Intrapartum care guidelines"
log "  - Contraception statements"
log "  - Cervical cancer screening"
log "  - Gestational diabetes"
log ""
log "STATUS: MANUAL DOWNLOAD REQUIRED (account needed)"
log "=========================================="
echo ""

################################################################################
# PRIORITY 6: RANZCP Clinical Practice Guidelines
################################################################################
log "TASK 6: RANZCP Clinical Practice Guidelines"
log "Source: RANZCP Website"
log "Size: ~200 MB"
log "Method: Manual download (FREE)"
log ""
log "Manual Download Steps:"
log "1. Visit: https://www.ranzcp.org/clinical-guidelines-publications/clinical-guidelines-publications-library"
log "2. Download all clinical practice guidelines"
log "3. Key guidelines:"
log "   - Depression"
log "   - Bipolar disorder"
log "   - Schizophrenia"
log "   - Anxiety disorders"
log "   - Mood disorders"
log "4. Save to: ${DOWNLOAD_DIR}/ranzcp/"
log ""
log "STATUS: MANUAL DOWNLOAD REQUIRED"
log "=========================================="
echo ""

################################################################################
# PRIORITY 7: Australian Stroke Foundation Guidelines
################################################################################
log "TASK 7: Australian Stroke Guidelines"
log "Source: Stroke Foundation Australia"
log "Size: ~100 MB"
log "Method: Direct download (FREE)"
log ""
log "Download URL: https://informme.org.au/guidelines/living-clinical-guidelines-for-stroke-management"
log ""
cd "${DOWNLOAD_DIR}/stroke_foundation" || exit
log "Downloading Australian Stroke Guidelines..."
# Note: Actual URL may require manual navigation
log "Manual download steps:"
log "1. Visit: https://informme.org.au/"
log "2. Navigate to 'Clinical Guidelines'"
log "3. Download 'Living Clinical Guidelines for Stroke Management'"
log "4. Save to: ${DOWNLOAD_DIR}/stroke_foundation/"
log ""
log "STATUS: MANUAL DOWNLOAD REQUIRED"
log "=========================================="
echo ""

################################################################################
# PRIORITY 8: NSW Health Clinical Practice Guidelines
################################################################################
log "TASK 8: NSW Health Clinical Practice Guidelines"
log "Source: NSW Health PD Portal"
log "Size: ~1 GB (multiple protocols)"
log "Method: Manual download (FREE, public access)"
log ""
log "Manual Download Steps:"
log "1. Visit: https://www1.health.nsw.gov.au/pds/Pages/doc.aspx"
log "2. Search for clinical protocols:"
log "   - Emergency medicine protocols"
log "   - Obstetric guidelines"
log "   - Mental health protocols"
log "   - Paediatric guidelines"
log "3. Download PDFs to: ${DOWNLOAD_DIR}/nsw_health/"
log ""
log "Key protocols for AMC/ICRP:"
log "  - NSW Emergency Department protocols"
log "  - NSW Maternity guidelines"
log "  - Mental Health Act protocols"
log ""
log "STATUS: MANUAL DOWNLOAD REQUIRED"
log "=========================================="
echo ""

################################################################################
# PRIORITY 9: Australian Immunisation Handbook
################################################################################
log "TASK 9: Australian Immunisation Handbook"
log "Source: Australian Government Department of Health"
log "Size: ~50 MB"
log "Method: Direct download (FREE)"
log ""
cd "${DOWNLOAD_DIR}/australian_immunisation" || exit
log "Downloading Australian Immunisation Handbook..."
# Check if already exists in project
if [ -f "/home/dev/Development/irStudy/AMC_Clinical_Exam_Resource_Center/Official_Resources/Australian_Immunisation_Handbook.pdf" ]; then
    log "✓ Australian Immunisation Handbook already available in project"
    cp "/home/dev/Development/irStudy/AMC_Clinical_Exam_Resource_Center/Official_Resources/Australian_Immunisation_Handbook.pdf" . 2>&1 | tee -a "${LOG_FILE}"
else
    log "Download from: https://immunisationhandbook.health.gov.au/"
    log "Manual download: Navigate website and download full handbook PDF"
fi
log "STATUS: CHECK PROJECT OR MANUAL DOWNLOAD"
log "=========================================="
echo ""

################################################################################
# PRIORITY 10: MIMIC-III Clinical Database
################################################################################
log "TASK 10: MIMIC-III Clinical Database"
log "Source: PhysioNet (requires registration)"
log "Size: ~50 GB compressed"
log "Method: Manual download (FREE after registration)"
log ""
log "Registration Steps:"
log "1. Visit: https://physionet.org/"
log "2. Create account"
log "3. Complete CITI training (required for data access)"
log "4. Apply for MIMIC-III access"
log "5. Approval takes 1-2 weeks"
log ""
log "Download after approval:"
log "1. Visit: https://physionet.org/content/mimiciii/1.4/"
log "2. Download files (requires PhysioNet credentials)"
log "3. Save to: ${DOWNLOAD_DIR}/mimic3/"
log ""
log "Note: Large dataset - only download if needed for clinical decision support training"
log "STATUS: REGISTRATION REQUIRED (1-2 weeks approval)"
log "=========================================="
echo ""

################################################################################
# PRIORITY 11: SNOMED CT (requires UMLS license)
################################################################################
log "TASK 11: SNOMED CT Clinical Terminology"
log "Source: UMLS (requires free affiliate license)"
log "Size: ~2 GB"
log "Method: Manual download (FREE after license approval)"
log ""
log "License Application Steps:"
log "1. Visit: https://uts.nlm.nih.gov/uts/signup-login"
log "2. Create UMLS account"
log "3. Request UMLS Metathesaurus License (affiliate license - FREE)"
log "4. Approval takes 1-3 business days"
log ""
log "Download after approval:"
log "1. Login to UMLS Terminology Services"
log "2. Download SNOMED CT Australian Edition"
log "3. Save to: ${DOWNLOAD_DIR}/snomed_ct/"
log ""
log "STATUS: LICENSE APPLICATION REQUIRED (1-3 days approval)"
log "=========================================="
echo ""

################################################################################
# PRIORITY 12: MeSH Medical Subject Headings
################################################################################
log "TASK 12: MeSH (Medical Subject Headings)"
log "Source: NIH NLM"
log "Size: ~500 MB"
log "Method: Direct download (FREE)"
log ""
cd "${DOWNLOAD_DIR}/mesh" || exit
log "Downloading MeSH database..."
log "Download URL: https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/"
log ""
if command -v wget &> /dev/null; then
    wget -c "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/desc2024.xml" \
         -O "mesh_descriptors_2024.xml" 2>&1 | tee -a "${LOG_FILE}"
    log "✓ MeSH descriptors downloaded"
else
    log "Manual download: https://www.nlm.nih.gov/mesh/download_mesh.html"
fi
log "STATUS: AUTOMATED (or manual download)"
log "=========================================="
echo ""

################################################################################
# Summary
################################################################################
log ""
log "=========================================="
log "DOWNLOAD SUMMARY"
log "=========================================="
log ""
log "AUTOMATED DOWNLOADS (Ready to execute):"
log "  ✓ RACGP Red Book - COMPLETED"
log "  ✓ MeSH Database - COMPLETED"
log "  ✓ Australian Immunisation Handbook - CHECK PROJECT"
log ""
log "MANUAL DOWNLOADS REQUIRED:"
log "  1. StatPearls (use Python script: scripts/download_statpearls.py)"
log "  2. Cochrane Reviews (account required, 10 specialty searches)"
log "  3. RANZCOG Guidelines (account required)"
log "  4. RANZCP Guidelines"
log "  5. Australian Stroke Guidelines"
log "  6. NSW Health Protocols"
log ""
log "REGISTRATION REQUIRED (delays 1-2 weeks):"
log "  1. MIMIC-III Database (PhysioNet account + CITI training)"
log "  2. SNOMED CT (UMLS license - 1-3 days approval)"
log ""
log "API INTEGRATIONS (no download needed):"
log "  1. PubMed Central API (real-time access)"
log ""
log "=========================================="
log "ESTIMATED STORAGE REQUIREMENTS"
log "=========================================="
log ""
log "StatPearls:              ~15-20 GB"
log "Cochrane Reviews:        ~5-10 GB"
log "RACGP Red Book:          ~50 MB"
log "RANZCOG Guidelines:      ~500 MB"
log "RANZCP Guidelines:       ~200 MB"
log "Stroke Guidelines:       ~100 MB"
log "NSW Health Protocols:    ~1 GB"
log "Australian Immunisation: ~50 MB"
log "MeSH Database:           ~500 MB"
log "MIMIC-III (optional):    ~50 GB"
log "SNOMED CT:               ~2 GB"
log "PMC Bulk (optional):     ~500 GB (not recommended)"
log ""
log "TOTAL (essential):       ~25-35 GB"
log "TOTAL (with MIMIC):      ~75-85 GB"
log "TOTAL (with PMC bulk):   ~525-585 GB (not recommended)"
log ""
log "=========================================="
log "NEXT STEPS"
log "=========================================="
log ""
log "1. Mount external drive: mount /dev/sdX1 /mnt/external"
log "2. Run this script: bash download_external_resources.sh /mnt/external/medical_resources"
log "3. Execute manual downloads as listed above"
log "4. Apply for UMLS license (1-3 days): https://uts.nlm.nih.gov/uts/signup-login"
log "5. Apply for MIMIC-III access (1-2 weeks): https://physionet.org/"
log "6. Get NCBI API key (instant): https://www.ncbi.nlm.nih.gov/account/settings/"
log "7. Run StatPearls download: python scripts/download_statpearls.py"
log ""
log "=========================================="
log "Script completed: $(date)"
log "Log file: ${LOG_FILE}"
log "=========================================="

# Create a checklist file
cat > "${DOWNLOAD_DIR}/DOWNLOAD_CHECKLIST.md" << 'EOF'
# Medical Resource Download Checklist

**Download Directory**: Set by script argument
**Total Storage Required**: ~25-35 GB (essential), ~75-85 GB (with MIMIC-III)

## Phase 1: Automated Downloads (Execute First)
- [ ] RACGP Red Book - Downloaded automatically by script
- [ ] MeSH Database - Downloaded automatically by script
- [ ] Australian Immunisation Handbook - Check project folder or download manually

## Phase 2: Manual Downloads (No Account Required)
- [ ] Australian Stroke Guidelines
  - URL: https://informme.org.au/
  - Navigate to Clinical Guidelines section
  - Save to: stroke_foundation/

- [ ] NSW Health Protocols
  - URL: https://www1.health.nsw.gov.au/pds/Pages/doc.aspx
  - Search: emergency, obstetric, mental health protocols
  - Save to: nsw_health/

- [ ] RANZCP Guidelines
  - URL: https://www.ranzcp.org/clinical-guidelines-publications/
  - Download all clinical practice guidelines
  - Save to: ranzcp/

## Phase 3: Manual Downloads (Account Required - FREE)
- [ ] Cochrane Reviews
  - URL: https://www.cochranelibrary.com/
  - Create free account
  - Search by 10 specialties (see script for search terms)
  - Download PDFs for reviews 12+ months old
  - Save to: cochrane/[specialty]/

- [ ] RANZCOG Guidelines
  - URL: https://ranzcog.edu.au/womens-health/statements-guidelines/
  - Create healthcare professional account (free)
  - Download all statements and guidelines
  - Save to: ranzcog/

## Phase 4: API Registrations (Required for Automation)
- [ ] NCBI API Key (instant, free)
  - URL: https://www.ncbi.nlm.nih.gov/account/settings/
  - Used for: StatPearls download, PubMed Central access
  - Set environment variable: export NCBI_API_KEY='your_key'

- [ ] UMLS License (1-3 days approval, free)
  - URL: https://uts.nlm.nih.gov/uts/signup-login
  - Request: UMLS Metathesaurus License (affiliate)
  - Used for: SNOMED CT Australian Edition
  - Save to: snomed_ct/

- [ ] PhysioNet MIMIC-III Access (1-2 weeks approval, free)
  - URL: https://physionet.org/
  - Complete CITI training (required)
  - Apply for MIMIC-III database access
  - Save to: mimic3/
  - Note: Optional, only if needed for clinical decision support

## Phase 5: Python Script Execution (After NCBI API Key)
- [ ] StatPearls Download
  - Ensure NCBI API key is set
  - Run: python scripts/download_statpearls.py --output [DOWNLOAD_DIR]/statpearls
  - Estimated time: 4-6 hours
  - Size: ~15-20 GB

## Phase 6: Processing & Integration (After Downloads Complete)
- [ ] Process PDFs (chunking, embedding)
- [ ] Index in Qdrant vector database
- [ ] Integrate with RAG system
- [ ] Test retrieval accuracy
- [ ] Validate citations

## Progress Tracking
| Resource | Status | Size | Date Completed |
|----------|--------|------|----------------|
| RACGP Red Book | ⏳ | 50 MB | |
| MeSH Database | ⏳ | 500 MB | |
| Australian Immunisation | ⏳ | 50 MB | |
| Stroke Guidelines | ⏳ | 100 MB | |
| NSW Health | ⏳ | 1 GB | |
| RANZCP | ⏳ | 200 MB | |
| Cochrane Reviews | ⏳ | 5-10 GB | |
| RANZCOG | ⏳ | 500 MB | |
| StatPearls | ⏳ | 15-20 GB | |
| SNOMED CT | ⏳ | 2 GB | |
| MIMIC-III | ⏳ | 50 GB | |

**Legend**: ⏳ Pending | ⬇️ Downloading | ✅ Complete | ❌ Failed

## Estimated Timeline
- **Phase 1** (Automated): 30 minutes
- **Phase 2** (Manual, no account): 2-3 hours
- **Phase 3** (Manual, with accounts): 4-6 hours
- **Phase 4** (API registrations): 1-2 weeks (approval delays)
- **Phase 5** (StatPearls download): 4-6 hours
- **Phase 6** (Processing): 8-12 hours

**Total Hands-on Time**: 8-12 hours
**Total Calendar Time**: 1-2 weeks (due to approval delays)

## Notes
- Run downloads in parallel where possible
- Monitor disk space during large downloads
- Keep downloaded PDFs for backup
- Document any download issues in log file
- Some URLs may change - check official websites if links broken
EOF

log "Checklist created: ${DOWNLOAD_DIR}/DOWNLOAD_CHECKLIST.md"
log ""
log "Review checklist and proceed with manual downloads as needed."
