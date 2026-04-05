#!/bin/bash

echo "=========================================="
echo "RESPIRATORY OSCE REGENERATION"
echo "PREREQUISITE VALIDATION"
echo "=========================================="
echo ""

cd /home/dev/Development/irStudy

ERRORS=0

echo "[1/8] Checking input file..."
if [ -f "data/osces/respiratory_50_osces.json" ]; then
    SIZE=$(wc -l data/osces/respiratory_50_osces.json | awk '{print $1}')
    echo "  ✓ Input file exists ($SIZE lines)"
else
    echo "  ✗ Input file NOT found: data/osces/respiratory_50_osces.json"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "[2/8] Checking regeneration script..."
if [ -f "scripts/regenerate_respiratory_osces.py" ]; then
    echo "  ✓ Script exists: scripts/regenerate_respiratory_osces.py"
else
    echo "  ✗ Script NOT found: scripts/regenerate_respiratory_osces.py"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "[3/8] Checking placeholder detection script..."
if [ -f "scripts/detect_placeholder_content.py" ]; then
    echo "  ✓ Script exists: scripts/detect_placeholder_content.py"
else
    echo "  ✗ Script NOT found: scripts/detect_placeholder_content.py"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "[4/8] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $PYTHON_VERSION"
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "  ✓ Python 3.8+ detected"
else
    echo "  ✗ Python 3.8+ required"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "[5/8] Checking Python packages..."
PACKAGES=("anthropic" "json")
for pkg in "${PACKAGES[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo "  ✓ Package installed: $pkg"
    else
        echo "  ✗ Package NOT installed: $pkg"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

echo "[6/8] Checking Claude API configuration..."
if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    KEY_LEN=${#ANTHROPIC_API_KEY}
    echo "  ✓ ANTHROPIC_API_KEY is set (length: $KEY_LEN)"
else
    echo "  ⚠ ANTHROPIC_API_KEY not set in environment"
    echo "    Checking for config file..."
    if [ -f ".env" ] && grep -q "ANTHROPIC_API_KEY" .env; then
        echo "  ✓ Found in .env file"
    elif [ -f "config.json" ] && grep -q "anthropic" config.json; then
        echo "  ✓ Found in config.json"
    else
        echo "  ✗ No API key configuration found"
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

echo "[7/8] Checking output directory..."
if [ -d "data/osces" ]; then
    echo "  ✓ Output directory exists: data/osces"
    if [ -w "data/osces" ]; then
        echo "  ✓ Directory is writable"
    else
        echo "  ✗ Directory NOT writable"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ✗ Output directory NOT found: data/osces"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "[8/8] Checking baseline placeholder rate..."
if [ -f "scripts/detect_placeholder_content.py" ] && [ -f "data/osces/respiratory_50_osces.json" ]; then
    echo "  Running placeholder detection..."
    python3 scripts/detect_placeholder_content.py data/osces/respiratory_50_osces.json 2>&1 | grep -E "Placeholder Rate|placeholder" | head -5
    echo ""
else
    echo "  ⚠ Cannot check placeholder rate (missing files)"
fi

echo "=========================================="
echo "VALIDATION SUMMARY"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✓ ALL PREREQUISITES MET"
    echo ""
    echo "Ready to execute regeneration:"
    echo "  ./run_respiratory_regeneration.sh"
    echo ""
    echo "Or manually:"
    echo "  python3 scripts/regenerate_respiratory_osces.py \\"
    echo "    data/osces/respiratory_50_osces.json \\"
    echo "    data/osces/respiratory_50_osces_regenerated.json"
    echo ""
    echo "Expected duration: 100-150 minutes"
    exit 0
else
    echo "✗ VALIDATION FAILED: $ERRORS error(s) found"
    echo ""
    echo "Fix the errors above before proceeding."
    exit 1
fi
