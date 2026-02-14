#!/bin/bash
# Quick Start Script - Production Server
# Launches production build on port 8000

echo "=========================================="
echo "Respiratory MCQ App - Production Server"
echo "=========================================="
echo ""

# Check if build exists
if [ ! -f "build/index.html" ]; then
    echo "⚠️  Production build not found!"
    echo "Building now..."
    node build.js
    echo ""
fi

echo "Starting production server on port 8000..."
echo "Access the app at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

cd "$(dirname "$0")/build"
python3 -m http.server 8000
