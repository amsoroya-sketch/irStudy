#!/bin/bash
# Helper script to run comprehensive HEAL downloader with virtual environment

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found"
    echo "Run: ./scripts/setup_playwright.sh first"
    exit 1
fi

# Run the comprehensive downloader with all arguments passed through
python3 scripts/download_heal_comprehensive.py "$@"

# Deactivate when done
deactivate
