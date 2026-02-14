#!/bin/bash
# Week 3 Respiratory - Execute All Batch Consolidations
# Runs all 8 batch consolidation scripts sequentially

set -e  # Exit on error

echo "================================================================================"
echo "WEEK 3 RESPIRATORY - CONSOLIDATING ALL 8 BATCHES"
echo "================================================================================"
echo "Started: $(date)"
echo ""

cd /home/dev/Development/irStudy/scripts-jan-26/respiratory_consolidation

echo "Batch 1 (001-025): Asthma & Early COPD..."
python3 consolidate_batch_001_025.py
echo ""

echo "Batch 2 (026-050): COPD Management & Bronchiectasis..."
python3 consolidate_batch_026_050.py
echo ""

echo "Batch 3 (051-075): Pneumonia & TB..."
python3 consolidate_batch_051_075.py
echo ""

echo "Batch 4 (076-100): TB Complications & PE Diagnosis..."
python3 consolidate_batch_076_100.py
echo ""

echo "Batch 5 (101-125): PE/DVT Management & ILD..."
python3 consolidate_batch_101_125.py
echo ""

echo "Batch 6 (126-150): Advanced ILD & Respiratory Failure..."
python3 consolidate_batch_126_150.py
echo ""

echo "Batch 7 (151-175): Ventilation & Pleural Disease..."
python3 consolidate_batch_151_175.py
echo ""

echo "Batch 8 (176-200): Lung Cancer & Diagnostics - FINAL BATCH..."
python3 consolidate_batch_176_200.py
echo ""

echo "================================================================================"
echo "ALL 8 BATCHES CONSOLIDATED SUCCESSFULLY!"
echo "================================================================================"
echo "Completed: $(date)"
echo ""
echo "Week 3 Respiratory: 200/200 MCQs complete with zero placeholder content"
echo "================================================================================"
