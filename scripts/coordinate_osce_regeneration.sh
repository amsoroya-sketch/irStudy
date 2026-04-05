#!/bin/bash
#
# Master coordination script for OSCE regeneration
# Coordinates regeneration of Psychiatry, Cardiology, and Respiratory OSCEs
# Uses Agent OS expert agents with quality validation
#
# Usage:
#   ./scripts/coordinate_osce_regeneration.sh [specialty]
#
# Options:
#   psychiatry   - Regenerate 40 psychiatry OSCEs
#   cardiology   - Regenerate 50 cardiology OSCEs
#   respiratory  - Regenerate 50 respiratory OSCEs
#   all          - Regenerate all 140 OSCEs (sequential)
#

set -e  # Exit on error

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPTS_DIR")"
DATA_DIR="$PROJECT_DIR/data/osces"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to validate placeholder rate
validate_output() {
    local output_file=$1
    local specialty=$2

    print_status "Validating $specialty OSCEs..."

    if [ ! -f "$output_file" ]; then
        print_error "Output file not found: $output_file"
        return 1
    fi

    # Run placeholder detection
    python3 "$SCRIPTS_DIR/detect_placeholder_content.py" "$output_file" > /tmp/placeholder_check.txt 2>&1

    # Check if any placeholders detected
    if grep -q "NEEDS_REGENERATION\|NEEDS_REVIEW" /tmp/placeholder_check.txt; then
        print_error "$specialty validation FAILED - placeholders detected"
        cat /tmp/placeholder_check.txt
        return 1
    else
        print_success "$specialty validation PASSED - 0% placeholder rate"
        return 0
    fi
}

# Function to regenerate psychiatry OSCEs
regenerate_psychiatry() {
    print_status "Starting Psychiatry OSCE Regeneration (40 OSCEs)"
    print_status "Agent: mental-health-crisis-expert"
    print_status "Estimated time: 90-120 minutes"
    echo ""

    cd "$PROJECT_DIR"

    python3 "$SCRIPTS_DIR/regenerate_psychiatry_osces.py" \
        "$DATA_DIR/psychiatry_40_osces.json" \
        "$DATA_DIR/psychiatry_40_osces_regenerated.json"

    if [ $? -eq 0 ]; then
        validate_output "$DATA_DIR/psychiatry_40_osces_regenerated.json" "Psychiatry"
        if [ $? -eq 0 ]; then
            print_success "Psychiatry OSCEs regeneration complete!"
            return 0
        else
            return 1
        fi
    else
        print_error "Psychiatry regeneration script failed"
        return 1
    fi
}

# Function to regenerate cardiology OSCEs
regenerate_cardiology() {
    print_status "Starting Cardiology OSCE Regeneration (50 OSCEs)"
    print_status "Agent: medication-management-expert"
    print_status "Estimated time: 100-150 minutes"
    echo ""

    cd "$PROJECT_DIR"

    python3 "$SCRIPTS_DIR/regenerate_cardiology_osces.py" \
        "$DATA_DIR/cardiology_50_osces.json" \
        "$DATA_DIR/cardiology_50_osces_regenerated.json"

    if [ $? -eq 0 ]; then
        validate_output "$DATA_DIR/cardiology_50_osces_regenerated.json" "Cardiology"
        if [ $? -eq 0 ]; then
            print_success "Cardiology OSCEs regeneration complete!"
            return 0
        else
            return 1
        fi
    else
        print_error "Cardiology regeneration script failed"
        return 1
    fi
}

# Function to regenerate respiratory OSCEs
regenerate_respiratory() {
    print_status "Starting Respiratory OSCE Regeneration (50 OSCEs)"
    print_status "Agent: physical-examination-expert"
    print_status "Estimated time: 100-150 minutes"
    echo ""

    cd "$PROJECT_DIR"

    python3 "$SCRIPTS_DIR/regenerate_respiratory_osces.py" \
        "$DATA_DIR/respiratory_50_osces.json" \
        "$DATA_DIR/respiratory_50_osces_regenerated.json"

    if [ $? -eq 0 ]; then
        validate_output "$DATA_DIR/respiratory_50_osces_regenerated.json" "Respiratory"
        if [ $? -eq 0 ]; then
            print_success "Respiratory OSCEs regeneration complete!"
            return 0
        else
            return 1
        fi
    else
        print_error "Respiratory regeneration script failed"
        return 1
    fi
}

# Main execution
main() {
    local specialty=${1:-"all"}

    echo ""
    echo "=========================================="
    echo "OSCE Regeneration Coordinator"
    echo "=========================================="
    echo ""

    case $specialty in
        psychiatry)
            regenerate_psychiatry
            ;;
        cardiology)
            regenerate_cardiology
            ;;
        respiratory)
            regenerate_respiratory
            ;;
        all)
            print_status "Running all regenerations sequentially"
            echo ""

            # Phase 1: Psychiatry
            regenerate_psychiatry
            if [ $? -ne 0 ]; then
                print_error "Psychiatry regeneration failed. Stopping."
                exit 1
            fi

            echo ""
            print_success "Phase 1/3 complete. Proceeding to Cardiology..."
            echo ""

            # Phase 2: Cardiology
            regenerate_cardiology
            if [ $? -ne 0 ]; then
                print_error "Cardiology regeneration failed. Stopping."
                exit 1
            fi

            echo ""
            print_success "Phase 2/3 complete. Proceeding to Respiratory..."
            echo ""

            # Phase 3: Respiratory
            regenerate_respiratory
            if [ $? -ne 0 ]; then
                print_error "Respiratory regeneration failed. Stopping."
                exit 1
            fi

            echo ""
            echo "=========================================="
            print_success "ALL REGENERATIONS COMPLETE!"
            echo "=========================================="
            echo ""
            print_status "Summary:"
            echo "  ✅ Psychiatry: 40 OSCEs regenerated (0% placeholders)"
            echo "  ✅ Cardiology: 50 OSCEs regenerated (0% placeholders)"
            echo "  ✅ Respiratory: 50 OSCEs regenerated (0% placeholders)"
            echo "  ✅ TOTAL: 140 OSCEs regenerated"
            echo ""
            print_status "Next steps:"
            echo "  1. Replace original files with regenerated versions"
            echo "  2. Run full evaluation to confirm >8.0/10 scores"
            echo "  3. Create Constraint 16: OSCE Requirements"
            echo ""
            ;;
        *)
            print_error "Unknown specialty: $specialty"
            echo ""
            echo "Usage: $0 [psychiatry|cardiology|respiratory|all]"
            echo ""
            exit 1
            ;;
    esac
}

main "$@"
