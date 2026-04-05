#!/bin/bash
#
# Batch Update Script for Psychiatry MCQs
# Applies SAFE-T fixes to all psychiatry MCQ files
#
# Based on IMPLEMENTATION_CHECKLIST.md Phase 5
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
PROJECT_ROOT="/home/dev/Development/irStudy"
DATA_DIR="$PROJECT_ROOT/data/mcqs"
BACKUP_DIR="$DATA_DIR/backups/$(date +%Y%m%d_%H%M%S)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# Create backup directory
echo -e "${YELLOW}Creating backup directory: $BACKUP_DIR${NC}"
mkdir -p "$BACKUP_DIR"

# Statistics
TOTAL_FILES=0
SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_MCQS_FIXED=0

# Find all psychiatry MCQ files
PSYCHIATRY_FILES=(
    "$DATA_DIR/psychiatry_depression_day1.json"
    "$DATA_DIR/psychiatry_anxiety_bipolar_day2.json"
    "$DATA_DIR/psychiatry_psychosis_day3.json"
    "$DATA_DIR/psychiatry_suicide_mha_day4.json"
    "$DATA_DIR/psychiatry_final_day5.json"
    "$DATA_DIR/week2_day6_psychiatry_80_mcqs.json"
    "$DATA_DIR/week3_psychiatry_additional_100_mcqs.json"
    "$DATA_DIR/week3_psychiatry_additional_100_mcqs_with_images.json"
    "$DATA_DIR/missing_psychiatry_150_mcqs.json"
)

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}Batch Update: Psychiatry MCQs${NC}"
echo -e "${YELLOW}========================================${NC}\n"

for file in "${PSYCHIATRY_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}⚠️  Skipping (not found): $(basename $file)${NC}"
        continue
    fi

    TOTAL_FILES=$((TOTAL_FILES + 1))
    filename=$(basename "$file")

    echo -e "\n${YELLOW}========================================${NC}"
    echo -e "${YELLOW}Processing: $filename${NC}"
    echo -e "${YELLOW}========================================${NC}"

    # Backup original file
    echo -e "📦 Backing up to: $BACKUP_DIR/$filename"
    cp "$file" "$BACKUP_DIR/$filename"

    # Apply auto-fixes
    echo -e "\n🔧 Applying auto-fixes..."
    temp_fixed="${file%.json}_temp_fixed.json"

    if python3 "$SCRIPTS_DIR/auto_fix_psychiatry_mcqs.py" "$file" "$temp_fixed"; then
        echo -e "${GREEN}✅ Auto-fix completed${NC}"

        # Validate fixed file
        echo -e "\n🔍 Validating fixed MCQs..."
        if python3 "$SCRIPTS_DIR/validate_psychiatry_mcq_generation.py" "$temp_fixed"; then
            echo -e "${GREEN}✅ Validation passed - replacing original${NC}"
            mv "$temp_fixed" "$file"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

            # Count MCQs fixed
            mcq_count=$(python3 -c "import json; data=json.load(open('$file')); print(len(data.get('mcqs', data if isinstance(data, list) else [data])))")
            TOTAL_MCQS_FIXED=$((TOTAL_MCQS_FIXED + mcq_count))
        else
            echo -e "${RED}❌ Validation failed - keeping original${NC}"
            rm "$temp_fixed"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    else
        echo -e "${RED}❌ Auto-fix failed - keeping original${NC}"
        if [ -f "$temp_fixed" ]; then
            rm "$temp_fixed"
        fi
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done

# Print summary
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}Batch Update Summary${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "Total files processed: $TOTAL_FILES"
echo -e "${GREEN}✅ Successfully fixed: $SUCCESS_COUNT${NC}"
echo -e "${RED}❌ Failed: $FAIL_COUNT${NC}"
echo -e "Total MCQs fixed: $TOTAL_MCQS_FIXED"
echo -e "Backup location: $BACKUP_DIR"
echo -e "${YELLOW}========================================${NC}\n"

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 Batch update completed successfully!${NC}\n"
    exit 0
else
    echo -e "${YELLOW}⚠️  Batch update completed with errors${NC}\n"
    exit 1
fi
