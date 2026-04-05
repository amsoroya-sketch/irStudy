#!/bin/bash
# Check if regeneration script exists and show its key components

cd /home/dev/Development/irStudy

echo "Checking for regeneration script..."
if [ -f "scripts/regenerate_respiratory_osces.py" ]; then
    echo "✅ Script exists: scripts/regenerate_respiratory_osces.py"
    echo ""
    echo "Script preview (first 50 lines):"
    head -50 scripts/regenerate_respiratory_osces.py
else
    echo "❌ Script NOT found: scripts/regenerate_respiratory_osces.py"
    echo ""
    echo "Available scripts in scripts/ directory:"
    ls -la scripts/*.py 2>/dev/null || echo "No Python scripts found"
fi

echo ""
echo "Checking for source data file..."
if [ -f "data/osces/respiratory_50_osces.json" ]; then
    echo "✅ Source file exists: data/osces/respiratory_50_osces.json"
    echo ""
    echo "File info:"
    wc -l data/osces/respiratory_50_osces.json
    echo ""
    echo "First OSCE structure (first 80 lines):"
    head -80 data/osces/respiratory_50_osces.json
else
    echo "❌ Source file NOT found"
fi

echo ""
echo "Checking for gold standard template..."
if [ -f "data/osces/psychiatry_week1_osces.json" ]; then
    echo "✅ Template exists: data/osces/psychiatry_week1_osces.json"
    echo ""
    echo "First OSCE structure (first 120 lines):"
    head -120 data/osces/psychiatry_week1_osces.json
else
    echo "❌ Template NOT found"
fi
