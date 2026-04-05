#!/bin/bash
cd /home/dev/Development/irStudy
echo "Checking scripts directory..."
ls -la scripts/ | head -20
echo ""
echo "Checking if regenerate script exists..."
if [ -f scripts/regenerate_cardiology_osces.py ]; then
    echo "✅ File exists, showing first 30 lines:"
    head -30 scripts/regenerate_cardiology_osces.py
else
    echo "❌ File does NOT exist - will create it"
fi
