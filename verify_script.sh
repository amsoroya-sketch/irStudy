#!/bin/bash
# Verify the regeneration script exists and check its structure
cd /home/dev/Development/irStudy

if [ -f "scripts/regenerate_cardiology_osces.py" ]; then
    echo "✅ Regeneration script found"
    echo ""
    echo "=== Script preview (first 50 lines) ==="
    head -50 scripts/regenerate_cardiology_osces.py
    echo ""
    echo "=== Checking for Claude API usage ==="
    grep -n "anthropic\|claude" scripts/regenerate_cardiology_osces.py || echo "No Claude API calls found"
else
    echo "❌ Regeneration script NOT found at scripts/regenerate_cardiology_osces.py"
    echo ""
    echo "Creating regeneration script..."
fi

# Also check if placeholder detection script exists
if [ -f "scripts/detect_placeholder_content.py" ]; then
    echo "✅ Placeholder detection script found"
else
    echo "❌ Placeholder detection script NOT found"
fi
