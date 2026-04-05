#!/bin/bash
# Check if required files exist
echo "=== Checking required files ==="
ls -lh /home/dev/Development/irStudy/data/osces/cardiology_50_osces.json
ls -lh /home/dev/Development/irStudy/data/osces/psychiatry_week1_osces.json
ls -lh /home/dev/Development/irStudy/scripts/regenerate_cardiology_osces.py
ls -lh /home/dev/Development/irStudy/scripts/detect_placeholder_content.py
echo ""
echo "=== First few lines of cardiology OSCEs ==="
head -100 /home/dev/Development/irStudy/data/osces/cardiology_50_osces.json
