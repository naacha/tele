#!/bin/bash
# Multi-Version STB Build Script

cd "$(dirname "$0")"

CYAN='\033[0;36m'
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${CYAN}🔨 Building Multi-Version STB HG680P Bot${NC}"
echo -e "${PURPLE}🖥️ Support: Armbian 20.11 Bullseye & 25.11 Bookworm${NC}"
echo ""

# Detect OS
DETECTED_BASE="bullseye"
if [ -f "/etc/armbian-release" ]; then
    source /etc/armbian-release
    if [[ "$VERSION" == *"25.11"* ]] || [[ "$VERSION" == *"bookworm"* ]]; then
        DETECTED_BASE="bookworm"
    fi
fi

if command -v lsb_release &> /dev/null; then
    LSB_CODENAME=$(lsb_release -cs 2>/dev/null || echo "")
    if [ "$LSB_CODENAME" = "bookworm" ]; then
        DETECTED_BASE="bookworm"
    fi
fi

# Force cleanup
echo -e "${BLUE}🛑 Force cleanup...${NC}"
docker stop telegram-bot-stb-multi aria2-stb-multi 2>/dev/null || true
docker rm -f telegram-bot-stb-multi aria2-stb-multi 2>/dev/null || true
docker system prune -f 2>/dev/null || true

echo -e "${GREEN}✅ Cleanup completed${NC}"

echo -e "${BLUE}📱 Target OS: $DETECTED_BASE${NC}"

# Build with OS-specific base
echo -e "${BLUE}🔨 Building multi-version optimized images...${NC}"
if BASE_OS=$DETECTED_BASE docker-compose build --no-cache --force-rm --build-arg BASE_OS=$DETECTED_BASE; then
    echo -e "${GREEN}✅ Multi-version build completed!${NC}"
    echo ""
    echo -e "${PURPLE}🌟 Features Integrated:${NC}"
    echo "• Multi-version OS support ($DETECTED_BASE)"
    echo "• Error fixing and dependency resolution"
    echo "• AnyDesk with dependency fixing"
    echo "• JMDKH features (torrent, mirror, clone)"
    echo "• Multi-auth method support"
    echo ""
    echo -e "${GREEN}🚀 Ready to start: ./start.sh${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi
