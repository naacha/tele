#!/bin/bash
# Multi-Version STB Status Script

cd "$(dirname "$0")"

CYAN='\033[0;36m'
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${CYAN}📊 Multi-Version STB HG680P Status${NC}"
echo -e "${PURPLE}🖥️ Armbian 20.11 Bullseye & 25.11 Bookworm${NC}"
echo "================================="
echo ""

echo -e "${GREEN}🔑 Integrated Credentials:${NC}"
echo "✅ Bot Token: 8436081597:AAE-8bfWrbvhl26-l9y65p48DfWjQOYPR2A"
echo "✅ Channel ID: -1001802424804 (@ZalheraThink)"
echo ""

# Detect OS version
DETECTED_VERSION="Unknown"
DETECTED_BASE="bullseye"
if [ -f "/etc/armbian-release" ]; then
    source /etc/armbian-release
    DETECTED_VERSION="$VERSION"
    if [[ "$VERSION" == *"20.11"* ]] || [[ "$VERSION" == *"bullseye"* ]]; then
        DETECTED_BASE="bullseye"
    elif [[ "$VERSION" == *"25.11"* ]] || [[ "$VERSION" == *"bookworm"* ]]; then
        DETECTED_BASE="bookworm"
    fi
fi

echo -e "${PURPLE}🐧 Multi-Version Information:${NC}"
echo "Armbian Version: $DETECTED_VERSION"
echo "Base OS: $DETECTED_BASE"
echo "Architecture: $(uname -m)"

if [ "$DETECTED_BASE" = "bookworm" ]; then
    echo "Auth Method: Environment Tokens"
else
    echo "Auth Method: Credentials File"
fi
echo ""

# Check GUI status
GUI_TYPE="Not detected"
if [ -n "$DISPLAY" ] || pgrep -x "Xorg" > /dev/null; then
    if pgrep -x "lxsession" > /dev/null; then
        GUI_TYPE="LXDE (Built-in)"
    elif pgrep -x "openbox" > /dev/null; then
        GUI_TYPE="Openbox (Built-in)"
    else
        GUI_TYPE="Minimal GUI (Built-in)"
    fi
    GUI_STATUS="✅ Available"
else
    GUI_STATUS="🔄 Available but not running"
fi

echo -e "${PURPLE}🖥️ GUI Status:${NC}"
echo "GUI: $GUI_STATUS"
echo "Type: $GUI_TYPE"
echo "Display: ${DISPLAY:-'Not set'}"
echo ""

# Check AnyDesk status
if command -v anydesk &> /dev/null; then
    ANYDESK_STATUS=$(systemctl is-active anydesk 2>/dev/null || echo "inactive")
    ANYDESK_ID=$(anydesk --get-id 2>/dev/null || echo "Not available")
    echo -e "${PURPLE}🔗 AnyDesk Status:${NC}"
    echo "Service: $ANYDESK_STATUS"
    echo "ID: $ANYDESK_ID"
    if [ "$ANYDESK_STATUS" = "active" ]; then
        echo "Password: stbaccess"
        echo "GUI Access: $GUI_TYPE"
    fi
else
    echo -e "${PURPLE}🔗 AnyDesk: Not installed${NC}"
fi

echo ""
echo "🐳 Docker Services:"
docker-compose ps
echo ""

echo "💻 STB Resources:"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3}') used / $(free -h | awk '/^Mem:/ {print $2}') total"
echo "Storage: $(df -h / | awk 'NR==2 {print $3}') used / $(df -h / | awk 'NR==2 {print $2}') total"
echo "Temperature: $(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null | awk '{print $1/1000"°C"}' || echo 'N/A')"
echo ""

echo "📢 Channel: @ZalheraThink subscription required"
