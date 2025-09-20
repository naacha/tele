#!/bin/bash
# STB Build Script for Built-in GUI Bullseye

cd "$(dirname "$0")"

CYAN='\033[0;36m'
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${CYAN}🔨 Building STB HG680P Bot - Armbian 20.05 Bullseye${NC}"
echo -e "${PURPLE}🖥️ With Built-in GUI Support (No XFCE4)${NC}"
echo ""

# Force cleanup
echo -e "${BLUE}🛑 Force cleanup...${NC}"
docker stop telegram-bot-stb-bullseye aria2-stb-bullseye 2>/dev/null || true
docker rm -f telegram-bot-stb-bullseye aria2-stb-bullseye 2>/dev/null || true
docker system prune -f 2>/dev/null || true

echo -e "${GREEN}✅ Cleanup completed${NC}"

# Show Bullseye info
if [ -f "/etc/armbian-release" ]; then
    source /etc/armbian-release
    echo -e "${BLUE}📱 Target: $BOARD Armbian $VERSION${NC}"
fi

# Check built-in GUI
if pgrep -x "Xorg" > /dev/null; then
    echo -e "${GREEN}🖥️ Built-in GUI: Detected and active${NC}"
else
    echo -e "${YELLOW}🖥️ Built-in GUI: Available but not running${NC}"
fi

# Build enhanced image
echo -e "${BLUE}🔨 Building Built-in GUI optimized images...${NC}"
if docker-compose build --no-cache --force-rm; then
    echo -e "${GREEN}✅ Built-in GUI Bullseye build completed!${NC}"
    echo ""
    echo -e "${PURPLE}🌟 Features Integrated:${NC}"
    echo "• Armbian 20.05 Bullseye support"
    echo "• Built-in GUI support (no XFCE4 installation)"
    echo "• AnyDesk remote access"
    echo "• JMDKH torrent/mirror/clone features"
    echo "• Enhanced error handling"
    echo "• Lightweight and optimized"
    echo ""
    echo -e "${GREEN}🚀 Ready to start: ./start.sh${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi
