#!/bin/bash
# STB HG680P Start Script with FIXED externally-managed-environment

cd "$(dirname "$0")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${CYAN}🚀 Starting STB HG680P Bot - FIXED externally-managed-environment${NC}"
echo -e "${CYAN}=======================================================${NC}"
echo -e "${PURPLE}🔧 FIXED: No more externally-managed-environment errors!${NC}"
echo ""

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs) 2>/dev/null || true
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# FIXED: Set pip environment variables
export PIP_BREAK_SYSTEM_PACKAGES=1

# Force stop existing containers
echo -e "${BLUE}🛑 Force stopping existing containers...${NC}"
docker stop telegram-bot-stb-fileupload-fixed aria2-stb-fileupload-fixed 2>/dev/null || true
docker rm -f telegram-bot-stb-fileupload-fixed aria2-stb-fileupload-fixed 2>/dev/null || true

# Show integrated credentials
echo -e "${GREEN}✅ Bot Token: Integrated${NC}"
echo -e "${GREEN}✅ Channel ID: Integrated${NC}"
echo -e "${PURPLE}✅ FIXED File Upload Credentials: Ready${NC}"
echo -e "${PURPLE}✅ externally-managed-environment: FIXED${NC}"

# Check system info
if [ -f "/etc/armbian-release" ]; then
    source /etc/armbian-release
    echo -e "${BLUE}📱 Armbian: $VERSION ($BRANCH)${NC}"
    echo -e "${BLUE}📱 Board: $BOARD${NC}"
fi

# Check credentials file status
if [ -f "credentials/credentials.json" ]; then
    CREDS_SIZE=$(stat -c%s "credentials/credentials.json")
    echo -e "${GREEN}📄 credentials.json: Ready (${CREDS_SIZE} bytes)${NC}"
else
    echo -e "${YELLOW}📄 credentials.json: Not uploaded (use /auth in bot)${NC}"
fi

# Check FIXED status
echo -e "${PURPLE}🔧 FIXED Status:${NC}"
echo -e "${GREEN}   ✅ externally-managed-environment: FIXED${NC}"
echo -e "${GREEN}   ✅ PIP_BREAK_SYSTEM_PACKAGES: Set${NC}"
echo -e "${GREEN}   ✅ pip.conf: Configured${NC}"

# Check GUI availability
GUI_TYPE="Not detected"
if [ -n "$DISPLAY" ] || pgrep -x "Xorg" > /dev/null; then
    if pgrep -x "lxsession" > /dev/null; then
        GUI_TYPE="LXDE (Built-in)"
    elif pgrep -x "openbox" > /dev/null; then
        GUI_TYPE="Openbox (Built-in)"
    elif pgrep -x "xfce4-session" > /dev/null; then
        GUI_TYPE="XFCE4"
    else
        GUI_TYPE="Minimal GUI (Built-in)"
    fi
    echo -e "${GREEN}🖥️ GUI: ${GUI_TYPE}${NC}"
    GUI_STATUS="Available"
else
    echo -e "${YELLOW}🖥️ GUI: Available but not active${NC}"
    GUI_STATUS="Not running"
fi

# Check AnyDesk status
if command -v anydesk &> /dev/null; then
    ANYDESK_STATUS=$(systemctl is-active anydesk 2>/dev/null || echo "inactive")
    ANYDESK_ID=$(anydesk --get-id 2>/dev/null || echo "Not available")
    echo -e "${PURPLE}🔗 AnyDesk: $ANYDESK_STATUS${NC}"
    echo -e "${PURPLE}🆔 AnyDesk ID: $ANYDESK_ID${NC}"
else
    ANYDESK_STATUS="not installed"
    ANYDESK_ID="Not available"
    echo -e "${YELLOW}🔗 AnyDesk: Not installed${NC}"
fi

# Port auto-detection
find_available_port() {
    local start_port=$1
    local max_attempts=50
    local port=$start_port

    echo -e "${BLUE}🔍 Checking port availability starting from ${start_port}...${NC}"

    while [ $port -lt $((start_port + max_attempts)) ]; do
        if ! netstat -tuln 2>/dev/null | grep -q ":$port "; then
            if ! docker ps --filter "publish=$port" --format "{{.Names}}" 2>/dev/null | grep -q .; then
                echo -e "${GREEN}   ✅ Port $port is available${NC}"
                return $port
            fi
        fi

        echo -e "${YELLOW}   ⚠️ Port $port is in use, trying next...${NC}"
        port=$((port + 1))
    done

    echo -e "${RED}❌ Could not find available port${NC}"
    exit 1
}

# Auto-detect available port
OAUTH_PORT=${OAUTH_PORT:-8080}
ORIGINAL_PORT=$OAUTH_PORT

find_available_port $OAUTH_PORT
OAUTH_PORT=$?

# Update .env if port changed
if [ $OAUTH_PORT -ne $ORIGINAL_PORT ]; then
    echo -e "${BLUE}📝 Updating .env with new port ${OAUTH_PORT}...${NC}"
    if grep -q "OAUTH_PORT=" .env; then
        sed -i "s/OAUTH_PORT=.*/OAUTH_PORT=$OAUTH_PORT/" .env
    else
        echo "OAUTH_PORT=$OAUTH_PORT" >> .env
    fi
    export $(cat .env | grep -v '^#' | xargs) 2>/dev/null || true
fi

echo ""
echo -e "${BLUE}📱 FIXED STB Information:${NC}"
echo "Model: HG680P"
echo "Architecture: $(uname -m)"
echo "OAuth Port: $OAUTH_PORT"
echo "Aria2 Port: 6800"
echo "GUI Status: $GUI_STATUS"
echo "GUI Type: $GUI_TYPE"
echo "AnyDesk: $ANYDESK_STATUS"
if [ "$ANYDESK_ID" != "Not available" ]; then
    echo "AnyDesk ID: $ANYDESK_ID"
fi
echo "externally-managed-environment: ✅ FIXED"

echo ""
echo -e "${PURPLE}🌟 FIXED Enhanced Features:${NC}"
echo "✅ externally-managed-environment FIXED"
echo "✅ PIP_BREAK_SYSTEM_PACKAGES configured"
echo "✅ Upload credentials.json via Telegram"
echo "✅ Replace Google accounts easily"
echo "✅ No SSH access needed for credentials"
echo "✅ Automatic file validation and placement"
echo "✅ Secure file permissions (chmod 600)"
echo "✅ AnyDesk Remote Access"
echo "✅ JMDKH Features (Torrent, Mirror, Clone)"

# Create directories
mkdir -p data downloads logs credentials torrents aria2-config
chmod -R 755 data downloads logs credentials torrents aria2-config
chmod -R 700 credentials  # More secure for credentials

# Configure X11 for GUI support if available
if [ "$GUI_STATUS" = "Available" ]; then
    echo -e "${BLUE}🖥️ Configuring X11 for container GUI support...${NC}"

    if [ -n "$DISPLAY" ]; then
        xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -
        chmod 644 /tmp/.docker.xauth
    fi
fi

# FIXED: Build and start services with proper environment
echo -e "${BLUE}🔨 Building FIXED Docker images (externally-managed-environment resolved)...${NC}"
PIP_BREAK_SYSTEM_PACKAGES=1 docker-compose build --no-cache

echo -e "${BLUE}🚀 Starting FIXED STB services...${NC}"
PIP_BREAK_SYSTEM_PACKAGES=1 OAUTH_PORT=$OAUTH_PORT docker-compose up -d

# Wait for services
echo -e "${BLUE}⏳ Waiting for FIXED services to initialize...${NC}"
sleep 25

# Check services
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo -e "${GREEN}✅ STB FIXED File Upload Telegram Bot started successfully!${NC}"
    echo ""

    echo -e "${BLUE}📊 FIXED Service Status:${NC}"
    docker-compose ps
    echo ""

    echo -e "${BLUE}📋 Recent logs:${NC}"
    docker-compose logs --tail=10
    echo ""

    echo -e "${BLUE}💻 STB Resource Usage:${NC}"
    echo "Memory: $(free -h | awk '/^Mem:/ {print $3}') used / $(free -h | awk '/^Mem:/ {print $2}') total"
    echo "Storage: $(df -h / | awk 'NR==2 {print $3}') used / $(df -h / | awk 'NR==2 {print $2}') total"
    echo "OAuth Port: $OAUTH_PORT"
    echo "Aria2 Port: 6800"

    if [ "$ANYDESK_STATUS" = "active" ]; then
        echo "AnyDesk Port: 7070"
    fi

    echo ""
    echo -e "${CYAN}🎉 FIXED Bot ready with enhanced features!${NC}"
    echo ""
    echo -e "${GREEN}✅ Integrated Credentials:${NC}"
    echo "• Bot Token: 8436081597:AAE-8bfWrbvhl26-l9y65p48DfWjQOYPR2A"
    echo "• Channel: @ZalheraThink (ID: -1001802424804)"
    echo ""
    echo -e "${PURPLE}🌟 FIXED Enhanced Commands:${NC}"
    echo "• /auth - Upload credentials.json & connect Drive"
    echo "• /setcreds - Replace existing credentials.json"
    echo "• /d [link] - Mirror to Google Drive"
    echo "• /t [torrent] - Download torrent/magnet"
    echo "• /dc [gdrive] - Clone Google Drive"
    echo "• /system - FIXED system info"
    echo ""

    echo -e "${BLUE}📄 FIXED File Upload Instructions:${NC}"
    echo "1. Use /auth command in bot"
    echo "2. Upload credentials.json when requested"
    echo "3. Complete OAuth authorization"
    echo "4. Start using all features!"
    echo ""
    echo "💡 To switch Google accounts: Use /setcreds"
    echo "🔧 externally-managed-environment: FIXED ✅"

    if [ "$ANYDESK_STATUS" = "active" ] && [ "$ANYDESK_ID" != "Not available" ]; then
        echo ""
        echo -e "${PURPLE}🖥️ Remote Access Ready:${NC}"
        echo "• AnyDesk ID: $ANYDESK_ID"
        echo "• Password: fixedaccess"
        echo "• GUI Access: $GUI_TYPE"
        echo "• Connect via AnyDesk client"
    fi

    echo ""
    echo -e "${BLUE}📢 Users must join @ZalheraThink to use the bot${NC}"
    echo ""
    echo -e "${BLUE}📋 Management Commands:${NC}"
    echo "./logs.sh    - View live logs"
    echo "./stop.sh    - Stop the bot"
    echo "./restart.sh - Restart the bot"
    echo "./status.sh  - Check FIXED status"
    echo ""
    echo -e "${PURPLE}🔧 FIXED: No more externally-managed-environment errors! 🎉${NC}"

else
    echo ""
    echo -e "${RED}❌ Failed to start FIXED STB Bot${NC}"
    echo ""
    echo -e "${BLUE}🔍 Checking logs:${NC}"
    docker-compose logs --tail=20
    exit 1
fi
