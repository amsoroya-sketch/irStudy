#!/bin/bash
# Setup Playwright for HEAL image downloading (with virtual environment)

set -e

echo "=================================="
echo "Playwright Setup for HEAL Download"
echo "=================================="
echo ""

# Check Python version
python3 --version || {
    echo "Error: Python 3 not found"
    exit 1
}

# Check if we're already in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Step 1: Creating virtual environment..."

    # Check if venv already exists
    if [ ! -d "venv" ]; then
        python3 -m venv venv || {
            echo "Error: Failed to create virtual environment"
            echo "Install python3-venv: sudo apt-get install python3-venv"
            exit 1
        }
        echo "✓ Virtual environment created"
    else
        echo "✓ Virtual environment already exists"
    fi

    # Activate virtual environment
    echo ""
    echo "Step 2: Activating virtual environment..."
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "✓ Already in virtual environment: $VIRTUAL_ENV"
fi

# Upgrade pip
echo ""
echo "Step 3: Upgrading pip..."
pip install --upgrade pip -q

# Install Python dependencies
echo ""
echo "Step 4: Installing Python packages..."
pip install playwright beautifulsoup4 tqdm || {
    echo "Error: Failed to install Python packages"
    exit 1
}
echo "✓ Python packages installed"

# Install Playwright browsers
echo ""
echo "Step 5: Installing Playwright browser (Chromium)..."
playwright install chromium || {
    echo "Error: Failed to install Playwright browser"
    exit 1
}
echo "✓ Playwright browser installed"

echo ""
echo "=================================="
echo "✓ Setup Complete!"
echo "=================================="
echo ""
echo "IMPORTANT: Activate the virtual environment before running scripts:"
echo "  source venv/bin/activate"
echo ""
echo "Then test the installation with:"
echo "  python3 scripts/download_heal_playwright.py \\"
echo "      --query 'melanoma' \\"
echo "      --collection dermatology \\"
echo "      --max-images 5 \\"
echo "      --show-browser"
echo ""
echo "To deactivate virtual environment later:"
echo "  deactivate"
