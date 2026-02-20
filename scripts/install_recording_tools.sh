#!/bin/bash

# Installation script for screen recording dependencies
# Run this if recording scripts report missing dependencies

set -e

echo "╔════════════════════════════════════════════════╗"
echo "║   Screen Recording Tools Installation          ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check what's already installed
echo -e "${BLUE}Checking current installation...${NC}"
echo ""

check_installed() {
    if command -v "$1" &> /dev/null; then
        echo -e "  ✓ $1 ${GREEN}(installed)${NC}"
        return 0
    else
        echo -e "  ✗ $1 ${YELLOW}(not installed)${NC}"
        return 1
    fi
}

NEEDS_INSTALL=false

check_installed "ffmpeg" || NEEDS_INSTALL=true
check_installed "xdotool" || NEEDS_INSTALL=true
check_installed "xwininfo" || NEEDS_INSTALL=true
check_installed "pactl" || NEEDS_INSTALL=true

echo ""

if [ "$NEEDS_INSTALL" = false ]; then
    echo -e "${GREEN}All required tools are already installed!${NC}"
    exit 0
fi

# Ask for confirmation
echo -e "${YELLOW}Some tools need to be installed.${NC}"
echo ""
echo "The following packages will be installed:"
echo "  - ffmpeg (video recording and processing)"
echo "  - xdotool (window management)"
echo "  - x11-utils (window information)"
echo "  - pulseaudio-utils (audio capture)"
echo ""
read -p "Continue with installation? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 1
fi

# Install packages
echo ""
echo -e "${BLUE}Installing packages...${NC}"
echo ""

sudo apt update
sudo apt install -y ffmpeg xdotool x11-utils pulseaudio-utils

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        Installation Complete!                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo "You can now use the recording scripts:"
echo ""
echo "  Simple recording:"
echo "    ./scripts/record_screen.sh"
echo ""
echo "  Advanced YouTube recording:"
echo "    ./scripts/record_youtube.sh window"
echo ""
