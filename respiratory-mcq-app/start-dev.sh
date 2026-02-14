#!/bin/bash
# Quick Start Script - Development Server
# Launches development server on port 8000

echo "========================================="
echo "Respiratory MCQ App - Development Server"
echo "========================================="
echo ""
echo "Starting development server on port 8000..."
echo "Access the app at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

cd "$(dirname "$0")/src"
python3 -m http.server 8000
