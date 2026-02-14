#!/bin/bash
set -e

cd /home/dev/Development/irStudy

echo "========================================="
echo "MCQ File Structure Converter"
echo "========================================="
echo ""

# Run the fix script
python3 fix_all_mcq_files.py

echo ""
echo "========================================="
echo "Conversion complete!"
echo "========================================="
echo ""
echo "To verify, run:"
echo "  python3 -c 'from data.mcqs.WEEK3_RESP_114_125_THROMBOPHILIA_ILD import GENERATED_MCQS; print(len(GENERATED_MCQS))'"
echo ""
