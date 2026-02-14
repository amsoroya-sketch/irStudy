#!/bin/bash
#
# MCQ File Structure Fix - Execution Script
# Converts 7 Week 3 Respiratory MCQ files from list to dictionary format
#

set -e  # Exit on error

cd /home/dev/Development/irStudy

echo ""
echo "=========================================================================="
echo " MCQ File Structure Converter"
echo " Converting 7 Respiratory MCQ files to dictionary format"
echo "=========================================================================="
echo ""

# Run the converter
python3 FINAL_MCQ_CONVERTER.py

# Store exit code
EXIT_CODE=$?

echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "=========================================================================="
    echo " ✓ CONVERSION SUCCESSFUL"
    echo "=========================================================================="
    echo ""
    echo "Next steps:"
    echo "  1. Verify one file:"
    echo "     python3 -c \"from data.mcqs.WEEK3_RESP_114_125_THROMBOPHILIA_ILD import GENERATED_MCQS; print(f'{len(GENERATED_MCQS)} MCQs')\" "
    echo ""
    echo "  2. Run consolidation:"
    echo "     python3 scripts/consolidate_week3_respiratory_mcqs.py"
    echo ""
    echo "  3. Delete backups (after verification):"
    echo "     rm data/mcqs/WEEK3_RESP_*.BACKUP"
    echo ""
else
    echo "=========================================================================="
    echo " ✗ CONVERSION FAILED"
    echo "=========================================================================="
    echo ""
    echo "Check the error messages above."
    echo "Original files have been restored from backup."
    echo ""
fi

exit $EXIT_CODE
