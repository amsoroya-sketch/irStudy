#!/bin/bash
################################################################################
# Medical Resources Download Orchestrator
# Purpose: Parallel download of all medical resources to external disk
# Estimated Total Size: 50-100 GB
# Estimated Time: 4-8 hours (parallel execution across 3 terminals)
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
EXTERNAL_DISK="${1:-}"
DOWNLOAD_DIR="${EXTERNAL_DISK}/medical_resources"
LOG_DIR="${DOWNLOAD_DIR}/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MAIN_LOG="${LOG_DIR}/download_orchestrator_${TIMESTAMP}.log"

# Required disk space (in GB)
REQUIRED_SPACE_GB=100
MIN_FREE_SPACE_GB=120  # Recommend 20% extra

################################################################################
# Helper Functions
################################################################################

log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${MAIN_LOG}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@" | tee -a "${MAIN_LOG}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@" | tee -a "${MAIN_LOG}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@" | tee -a "${MAIN_LOG}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $@" | tee -a "${MAIN_LOG}"
}

print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$@${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

check_disk_space() {
    local path="$1"
    local available_kb=$(df -k "${path}" | tail -1 | awk '{print $4}')
    local available_gb=$((available_kb / 1024 / 1024))
    echo "${available_gb}"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Required command not found: $1"
        log_info "Please install: $1"
        return 1
    fi
    return 0
}

create_progress_file() {
    local task_name="$1"
    local progress_file="${LOG_DIR}/progress_${task_name}.txt"
    echo "STATUS=pending" > "${progress_file}"
    echo "START_TIME=$(date +%s)" >> "${progress_file}"
    echo "${progress_file}"
}

update_progress() {
    local progress_file="$1"
    local status="$2"
    local message="${3:-}"

    sed -i "s/^STATUS=.*/STATUS=${status}/" "${progress_file}"
    echo "LAST_UPDATE=$(date +%s)" >> "${progress_file}"
    if [ -n "${message}" ]; then
        echo "MESSAGE=${message}" >> "${progress_file}"
    fi
}

################################################################################
# Validation
################################################################################

# Create directories first (before any logging)
mkdir -p "${DOWNLOAD_DIR}"/{statpearls,cochrane,racgp,ranzcog,ranzcp,stroke_foundation,nsw_health,immunisation,mesh,pubmed,therapeutic_guidelines,other}
mkdir -p "${LOG_DIR}"

print_header "Medical Resources Download Orchestrator"

# Check if external disk path provided
if [ -z "${EXTERNAL_DISK}" ]; then
    log_error "No external disk path provided!"
    echo ""
    echo "Usage: $0 <external_disk_mount_point>"
    echo ""
    echo "Examples:"
    echo "  $0 /media/\$USER/MyDrive"
    echo "  $0 /mnt/external"
    echo "  $0 ~/external_drive"
    echo ""
    echo "Current mounted drives:"
    df -h | grep -E '(/mnt|/media|/run/media)' || echo "  No external drives detected"
    echo ""
    exit 1
fi

# Check if external disk exists and is writable
if [ ! -d "${EXTERNAL_DISK}" ]; then
    log_error "External disk path does not exist: ${EXTERNAL_DISK}"
    exit 1
fi

if [ ! -w "${EXTERNAL_DISK}" ]; then
    log_error "External disk is not writable: ${EXTERNAL_DISK}"
    log_info "Try: sudo chmod -R u+w ${EXTERNAL_DISK}"
    exit 1
fi

log_success "External disk found: ${EXTERNAL_DISK}"

# Check available disk space
AVAILABLE_GB=$(check_disk_space "${EXTERNAL_DISK}")
log_info "Available space on external disk: ${AVAILABLE_GB} GB"
log_info "Required space: ${REQUIRED_SPACE_GB} GB"
log_info "Recommended space: ${MIN_FREE_SPACE_GB} GB"

if [ "${AVAILABLE_GB}" -lt "${REQUIRED_SPACE_GB}" ]; then
    log_error "Insufficient disk space!"
    log_error "Available: ${AVAILABLE_GB} GB"
    log_error "Required: ${REQUIRED_SPACE_GB} GB"
    exit 1
elif [ "${AVAILABLE_GB}" -lt "${MIN_FREE_SPACE_GB}" ]; then
    log_warning "Disk space is tight!"
    log_warning "Available: ${AVAILABLE_GB} GB"
    log_warning "Recommended: ${MIN_FREE_SPACE_GB} GB"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    log_success "Sufficient disk space available: ${AVAILABLE_GB} GB"
fi

# Directories already created at start
log_success "Directories created at: ${DOWNLOAD_DIR}"

# Check required commands
log_info "Checking required commands..."
MISSING_COMMANDS=()

check_command "python3" || MISSING_COMMANDS+=("python3")
check_command "curl" || MISSING_COMMANDS+=("curl")
check_command "wget" || MISSING_COMMANDS+=("wget")
check_command "git" || MISSING_COMMANDS+=("git")

if [ ${#MISSING_COMMANDS[@]} -gt 0 ]; then
    log_error "Missing required commands: ${MISSING_COMMANDS[*]}"
    log_info "Install with: sudo apt install ${MISSING_COMMANDS[*]}"
    exit 1
fi

log_success "All required commands available"

################################################################################
# Download Plan
################################################################################

print_header "Download Plan - 3 Parallel Terminals"

cat << EOF | tee -a "${MAIN_LOG}"
This script will guide you through downloading medical resources in parallel.

SETUP:
1. Open 3 terminal windows/tabs
2. Run different download tasks in each terminal
3. All downloads save to: ${DOWNLOAD_DIR}

ESTIMATED DOWNLOAD SIZES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Terminal 1 (Automated - 30 min):
  • RACGP Red Book           ~50 MB
  • MeSH Database           ~500 MB
  • Australian Immunisation  ~100 MB
  • Stroke Foundation       ~200 MB
  Total: ~850 MB

Terminal 2 (Python Script - 4-6 hours):
  • StatPearls Database    15-20 GB
  Total: 15-20 GB

Terminal 3 (Manual Downloads - 2-4 hours):
  • Cochrane Reviews        5-10 GB
  • RANZCOG Guidelines      ~500 MB
  • RANZCP Guidelines       ~200 MB
  • NSW Health Protocols    ~300 MB
  • Therapeutic Guidelines  ~1 GB (if accessible)
  Total: 7-12 GB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL SIZE: 25-35 GB (Essential resources)
TOTAL TIME: 4-6 hours (parallel execution)

EOF

echo ""
read -p "Ready to proceed with download setup? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Download cancelled by user"
    exit 0
fi

################################################################################
# Generate Terminal Scripts
################################################################################

print_header "Generating Terminal Scripts"

# Terminal 1: Automated downloads
TERMINAL1_SCRIPT="${LOG_DIR}/terminal1_automated.sh"
cat > "${TERMINAL1_SCRIPT}" << 'SCRIPT1'
#!/bin/bash
# Terminal 1: Automated Downloads (Small Files)
# Estimated time: 30 minutes

DOWNLOAD_DIR="DOWNLOAD_DIR_PLACEHOLDER"
LOG_FILE="${DOWNLOAD_DIR}/logs/terminal1_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

echo "============================================================"
echo "Terminal 1: Automated Downloads"
echo "============================================================"
echo ""

# RACGP Red Book
log "Downloading RACGP Red Book 10th Edition..."
mkdir -p "${DOWNLOAD_DIR}/racgp"
wget -O "${DOWNLOAD_DIR}/racgp/red_book_10th_edition.pdf" \
    "https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-racgp-guidelines/red-book" \
    2>&1 | tee -a "${LOG_FILE}" || log "RACGP Red Book: Manual download needed"

# MeSH Database
log "Downloading MeSH Database..."
mkdir -p "${DOWNLOAD_DIR}/mesh"
wget -O "${DOWNLOAD_DIR}/mesh/mesh_2024.xml" \
    "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/desc2024.xml" \
    2>&1 | tee -a "${LOG_FILE}"

# Australian Immunisation Handbook
log "Downloading Australian Immunisation Handbook..."
mkdir -p "${DOWNLOAD_DIR}/immunisation"
wget -O "${DOWNLOAD_DIR}/immunisation/immunisation_handbook.pdf" \
    "https://immunisationhandbook.health.gov.au/resources/handbook-pdf" \
    2>&1 | tee -a "${LOG_FILE}" || log "Immunisation Handbook: Check URL or download manually"

# Stroke Foundation Guidelines
log "Downloading Stroke Foundation Guidelines..."
mkdir -p "${DOWNLOAD_DIR}/stroke_foundation"
wget -O "${DOWNLOAD_DIR}/stroke_foundation/clinical_guidelines.pdf" \
    "https://strokefoundation.org.au/what-we-do/for-health-professionals/clinical-guidelines" \
    2>&1 | tee -a "${LOG_FILE}" || log "Stroke Guidelines: Manual download needed"

log "Terminal 1 downloads complete!"
log "Check log: ${LOG_FILE}"
SCRIPT1

# Replace placeholder
sed -i "s|DOWNLOAD_DIR_PLACEHOLDER|${DOWNLOAD_DIR}|g" "${TERMINAL1_SCRIPT}"
chmod +x "${TERMINAL1_SCRIPT}"

# Terminal 2: StatPearls
TERMINAL2_SCRIPT="${LOG_DIR}/terminal2_statpearls.sh"
cat > "${TERMINAL2_SCRIPT}" << 'SCRIPT2'
#!/bin/bash
# Terminal 2: StatPearls Database Download
# Estimated time: 4-6 hours
# Requires: NCBI API key

DOWNLOAD_DIR="DOWNLOAD_DIR_PLACEHOLDER"
PROJECT_DIR="PROJECT_DIR_PLACEHOLDER"
LOG_FILE="${DOWNLOAD_DIR}/logs/terminal2_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

echo "============================================================"
echo "Terminal 2: StatPearls Database Download"
echo "============================================================"
echo ""

# Check for NCBI API key
if [ -z "${NCBI_API_KEY}" ]; then
    log "ERROR: NCBI_API_KEY not set!"
    echo ""
    echo "To get an API key:"
    echo "1. Visit: https://www.ncbi.nlm.nih.gov/account/settings/"
    echo "2. Register/login (free)"
    echo "3. Request API key"
    echo "4. Export it: export NCBI_API_KEY='your_key_here'"
    echo ""
    echo "Then run this script again."
    exit 1
fi

log "NCBI API key found: ${NCBI_API_KEY:0:10}..."
log "Starting StatPearls download..."
log "This will take 4-6 hours - do not close this terminal!"
echo ""

# Run StatPearls downloader
python3 "${PROJECT_DIR}/scripts/download_statpearls.py" \
    --output "${DOWNLOAD_DIR}/statpearls" \
    --api-key "${NCBI_API_KEY}" \
    2>&1 | tee -a "${LOG_FILE}"

log "StatPearls download complete!"
log "Check log: ${LOG_FILE}"
SCRIPT2

# Replace placeholders
sed -i "s|DOWNLOAD_DIR_PLACEHOLDER|${DOWNLOAD_DIR}|g" "${TERMINAL2_SCRIPT}"
sed -i "s|PROJECT_DIR_PLACEHOLDER|$(pwd)|g" "${TERMINAL2_SCRIPT}"
chmod +x "${TERMINAL2_SCRIPT}"

# Terminal 3: Manual downloads
TERMINAL3_INSTRUCTIONS="${LOG_DIR}/terminal3_manual_instructions.md"
cat > "${TERMINAL3_INSTRUCTIONS}" << 'INSTRUCTIONS'
# Terminal 3: Manual Downloads Instructions

**Estimated time:** 2-4 hours
**Download to:** DOWNLOAD_DIR_PLACEHOLDER

---

## 1. Cochrane Systematic Reviews (5-10 GB)

**Steps:**
1. Visit: https://www.cochranelibrary.com/
2. Create free account (if needed)
3. Search by specialty and download PDFs:

### Cardiology
- Search: "cardiovascular" OR "cardiology" OR "acute coronary syndrome"
- Filter: Cochrane Reviews only
- Download ~50-100 reviews
- Save to: `DOWNLOAD_DIR_PLACEHOLDER/cochrane/cardiology/`

### Respiratory
- Search: "asthma" OR "COPD" OR "pneumonia" OR "respiratory"
- Download ~50-100 reviews
- Save to: `DOWNLOAD_DIR_PLACEHOLDER/cochrane/respiratory/`

### Other Specialties
Repeat for: gastroenterology, endocrinology, neurology, emergency, obgyn, paediatrics, psychiatry, general_practice

---

## 2. RANZCOG Guidelines (500 MB)

**Steps:**
1. Visit: https://ranzcog.edu.au/statements-guidelines
2. Download all clinical statements and guidelines
3. Save to: `DOWNLOAD_DIR_PLACEHOLDER/ranzcog/`

**Key guidelines:**
- Antenatal screening
- Pre-eclampsia management
- Gestational diabetes
- Post-partum haemorrhage
- Contraception
- Menopause

---

## 3. RANZCP Clinical Guidelines (200 MB)

**Steps:**
1. Visit: https://www.ranzcp.org/clinical-guidelines-publications/clinical-guidelines-publications-library
2. Download all clinical practice guidelines
3. Save to: `DOWNLOAD_DIR_PLACEHOLDER/ranzcp/`

**Key guidelines:**
- Depression
- Anxiety disorders
- Schizophrenia
- Bipolar disorder
- Suicide risk assessment

---

## 4. NSW Health Protocols (300 MB)

**Steps:**
1. Visit: https://www.health.nsw.gov.au/policies/
2. Search for clinical protocols and guidelines
3. Save to: `DOWNLOAD_DIR_PLACEHOLDER/nsw_health/`

**Key protocols:**
- Emergency department protocols
- Resuscitation guidelines
- Sepsis management
- Mental health protocols

---

## 5. Therapeutic Guidelines (1 GB) - OPTIONAL

**If you have eTG subscription:**
1. Login to: https://www.tg.org.au/
2. Download PDF versions of:
   - Cardiovascular
   - Respiratory
   - Antibiotic
   - Endocrinology
   - Neurology
   - Gastrointestinal
   - Mental Health
3. Save to: `DOWNLOAD_DIR_PLACEHOLDER/therapeutic_guidelines/`

**Note:** Already have 9,672 eTG chunks in vector database, so this is optional.

---

## Progress Checklist

- [ ] Cochrane Reviews (all specialties)
- [ ] RANZCOG Guidelines
- [ ] RANZCP Guidelines
- [ ] NSW Health Protocols
- [ ] Therapeutic Guidelines (optional)

**When complete, create a file:** `DOWNLOAD_DIR_PLACEHOLDER/logs/terminal3_complete.txt`

---

**Estimated total:** 7-12 GB
**Estimated time:** 2-4 hours
INSTRUCTIONS

# Replace placeholder
sed -i "s|DOWNLOAD_DIR_PLACEHOLDER|${DOWNLOAD_DIR}|g" "${TERMINAL3_INSTRUCTIONS}"

log_success "Terminal scripts generated:"
log_info "  Terminal 1: ${TERMINAL1_SCRIPT}"
log_info "  Terminal 2: ${TERMINAL2_SCRIPT}"
log_info "  Terminal 3: ${TERMINAL3_INSTRUCTIONS}"

################################################################################
# Instructions
################################################################################

print_header "Download Instructions"

cat << EOF

${GREEN}✓ Setup complete!${NC} Now execute downloads in 3 parallel terminals:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
${BLUE}TERMINAL 1${NC} - Automated Downloads (30 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run this command:

    bash ${TERMINAL1_SCRIPT}

Downloads:
  • RACGP Red Book (~50 MB)
  • MeSH Database (~500 MB)
  • Immunisation Handbook (~100 MB)
  • Stroke Guidelines (~200 MB)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
${BLUE}TERMINAL 2${NC} - StatPearls Database (4-6 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
First, get NCBI API key:
  1. Visit: https://www.ncbi.nlm.nih.gov/account/settings/
  2. Register/login (free)
  3. Request API key
  4. Export: export NCBI_API_KEY='your_key'

Then run:

    export NCBI_API_KEY='your_key_here'
    bash ${TERMINAL2_SCRIPT}

Downloads:
  • StatPearls Database (15-20 GB, 10,000+ articles)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
${BLUE}TERMINAL 3${NC} - Manual Downloads (2-4 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Read instructions:

    cat ${TERMINAL3_INSTRUCTIONS}

Or open in editor:

    nano ${TERMINAL3_INSTRUCTIONS}

Downloads:
  • Cochrane Reviews (5-10 GB)
  • RANZCOG Guidelines (~500 MB)
  • RANZCP Guidelines (~200 MB)
  • NSW Health Protocols (~300 MB)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${YELLOW}MONITORING:${NC}

Watch progress:
    watch -n 10 du -sh ${DOWNLOAD_DIR}/*

Check logs:
    tail -f ${DOWNLOAD_DIR}/logs/*.log

Check disk space:
    df -h ${EXTERNAL_DISK}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${GREEN}All downloads save to:${NC} ${DOWNLOAD_DIR}

${GREEN}Estimated completion:${NC} 4-6 hours (all terminals running in parallel)

EOF

# Create a README in the download directory
cat > "${DOWNLOAD_DIR}/README.md" << EOF
# Medical Resources Download

**Started:** $(date)
**Location:** ${DOWNLOAD_DIR}
**Orchestrator Log:** ${MAIN_LOG}

## Download Progress

Check individual terminal logs:
- Terminal 1 (Automated): ${LOG_DIR}/terminal1_*.log
- Terminal 2 (StatPearls): ${LOG_DIR}/terminal2_*.log
- Terminal 3 (Manual): ${TERMINAL3_INSTRUCTIONS}

## Directory Structure

\`\`\`
${DOWNLOAD_DIR}/
├── statpearls/          # StatPearls Database (15-20 GB)
├── cochrane/            # Cochrane Reviews (5-10 GB)
├── racgp/               # RACGP Red Book (~50 MB)
├── ranzcog/             # RANZCOG Guidelines (~500 MB)
├── ranzcp/              # RANZCP Guidelines (~200 MB)
├── stroke_foundation/   # Stroke Guidelines (~200 MB)
├── nsw_health/          # NSW Health Protocols (~300 MB)
├── immunisation/        # Immunisation Handbook (~100 MB)
├── mesh/                # MeSH Database (~500 MB)
├── therapeutic_guidelines/ # eTG (optional, ~1 GB)
├── other/               # Other resources
└── logs/                # Download logs
\`\`\`

## Monitoring

\`\`\`bash
# Watch disk usage
watch -n 10 du -sh ${DOWNLOAD_DIR}/*

# Check total size
du -sh ${DOWNLOAD_DIR}

# Monitor logs
tail -f ${DOWNLOAD_DIR}/logs/*.log
\`\`\`

## Completion Checklist

- [ ] Terminal 1 complete (automated downloads)
- [ ] Terminal 2 complete (StatPearls)
- [ ] Terminal 3 complete (manual downloads)
- [ ] All resources validated
- [ ] Total size: ~25-35 GB

**Estimated completion time:** 4-6 hours (parallel execution)
EOF

log_success "Setup complete!"
log_info "Download directory: ${DOWNLOAD_DIR}"
log_info "Main log: ${MAIN_LOG}"
log_info "Follow instructions above to start downloads in 3 terminals"

echo ""
echo "${GREEN}✓ Ready to download!${NC}"
echo ""
