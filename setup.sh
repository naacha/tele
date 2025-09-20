#!/bin/bash
# STB HG680P Setup Script for Armbian 20.05 Bullseye - Uses Built-in GUI

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${CYAN}🚀 STB HG680P Setup for Armbian 20.05 Bullseye${NC}"
echo -e "${CYAN}================================================${NC}"
echo -e "${PURPLE}🖥️ Using Built-in GUI + AnyDesk Integration${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root: sudo ./setup.sh${NC}"
    exit 1
fi

# Detect Armbian version
if [ -f "/etc/armbian-release" ]; then
    source /etc/armbian-release
    echo -e "${BLUE}📱 Detected Armbian: $VERSION ($BRANCH)${NC}"
    echo -e "${BLUE}📱 Board: $BOARD${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️ Warning: Could not detect Armbian version${NC}"
fi

# Check architecture
if [[ $(uname -m) != "aarch64" ]]; then
    echo -e "${YELLOW}⚠️ Warning: Optimized for ARM64/aarch64 architecture${NC}"
fi

echo -e "${BLUE}📱 System Information:${NC}"
echo "Architecture: $(uname -m)"
echo "OS: $(uname -s)"
echo "Kernel: $(uname -r)"
echo "Distribution: $(lsb_release -d 2>/dev/null | cut -f2 || echo 'Unknown')"
echo ""

# Check for built-in GUI
if [ -n "$DISPLAY" ] || pgrep -x "Xorg" > /dev/null || pgrep -x "lightdm" > /dev/null; then
    echo -e "${GREEN}✅ Built-in GUI detected and active${NC}"
    GUI_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️ Built-in GUI not currently running${NC}"
    GUI_AVAILABLE=false
fi

# Detect desktop environment  
DE_DETECTED="None"
if pgrep -x "lxsession" > /dev/null; then
    DE_DETECTED="LXDE (Built-in)"
elif pgrep -x "openbox" > /dev/null; then
    DE_DETECTED="Openbox (Built-in)"  
elif pgrep -x "xfce4-session" > /dev/null; then
    DE_DETECTED="XFCE4"
elif pgrep -x "Xorg" > /dev/null; then
    DE_DETECTED="Minimal GUI (Built-in)"
fi

echo -e "${PURPLE}🖥️ GUI Information:${NC}"
echo "Built-in GUI: ${GUI_AVAILABLE}"
echo "Desktop Environment: ${DE_DETECTED}"
echo "Display: ${DISPLAY:-'Not set'}"
echo ""

# Stop existing Docker containers
echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
docker stop telegram-bot-stb-bullseye aria2-stb-bullseye 2>/dev/null || true
docker rm -f telegram-bot-stb-bullseye aria2-stb-bullseye 2>/dev/null || true

# Clean Docker system
echo -e "${BLUE}🧹 Cleaning Docker system...${NC}"
docker system prune -f 2>/dev/null || true

echo -e "${GREEN}✅ Docker cleanup completed${NC}"

# Update system packages for Bullseye
echo -e "${BLUE}📦 Updating Armbian Bullseye system packages...${NC}"
apt-get update -y
apt-get upgrade -y

# Install base dependencies for Bullseye
echo -e "${BLUE}📦 Installing base dependencies for Bullseye...${NC}"
apt-get install -y \
    curl \
    wget \
    gnupg \
    lsb-release \
    ca-certificates \
    apt-transport-https \
    software-properties-common

# Install Docker for ARM64 if not present
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}🐳 Installing Docker for ARM64 Bullseye...${NC}"

    # Add Docker GPG key
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Add Docker repository for ARM64 Bullseye
    echo "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bullseye stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io

    # Enable Docker service
    systemctl enable docker
    systemctl start docker

    echo -e "${GREEN}✅ Docker installed successfully${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# Install Docker Compose for ARM64
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}📦 Installing Docker Compose for ARM64...${NC}"

    # Install pip3 if not available
    apt-get install -y python3-pip

    # Install docker-compose via pip
    pip3 install docker-compose

    echo -e "${GREEN}✅ Docker Compose installed successfully${NC}"
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# Install GUI support tools (minimal - work with built-in GUI)
echo -e "${PURPLE}🖥️ Installing minimal GUI support tools...${NC}"

# Install only essential GUI tools that work with built-in GUI
apt-get install -y \
    x11-utils \
    x11-xserver-utils \
    xauth \
    mesa-utils

# NO DESKTOP ENVIRONMENT INSTALLATION - Use built-in GUI
echo -e "${GREEN}✅ Using Armbian 20.05 built-in GUI (no additional desktop installation)${NC}"
echo -e "${PURPLE}🖥️ Built-in GUI detected: ${DE_DETECTED}${NC}"

# Install AnyDesk for remote access
echo -e "${PURPLE}🖥️ Installing AnyDesk for remote access...${NC}"

# Add AnyDesk repository key
wget -qO - https://keys.anydesk.com/repos/DEB-GPG-KEY | apt-key add -

# Add AnyDesk repository for ARM64
echo "deb http://deb.anydesk.com/ all main" > /etc/apt/sources.list.d/anydesk-stable.list

# Update package list
apt-get update

# Install AnyDesk
if apt-get install -y anydesk; then
    echo -e "${GREEN}✅ AnyDesk installed successfully${NC}"

    # Enable AnyDesk service
    systemctl enable anydesk
    systemctl start anydesk

    # Get AnyDesk ID
    sleep 3  # Wait for service to start
    ANYDESK_ID=$(anydesk --get-id 2>/dev/null || echo "ID will be available after first start")
    echo -e "${PURPLE}🆔 AnyDesk ID: ${ANYDESK_ID}${NC}"

else
    echo -e "${YELLOW}⚠️ AnyDesk installation failed, continuing without remote access${NC}"
fi

# Install enhanced dependencies for JMDKH features
echo -e "${BLUE}📦 Installing enhanced dependencies for JMDKH features...${NC}"
apt-get install -y \
    aria2 \
    ffmpeg \
    mediainfo \
    unzip \
    p7zip-full \
    curl \
    wget \
    git

# Create enhanced directory structure
echo -e "${BLUE}📁 Creating enhanced directory structure...${NC}"
mkdir -p data downloads logs credentials torrents aria2-config
chmod -R 755 data downloads logs credentials torrents aria2-config

# Create environment file with Bullseye defaults
if [ ! -f ".env" ]; then
    echo -e "${BLUE}⚙️ Creating Bullseye environment configuration...${NC}"
    cp .env.example .env

    echo -e "${GREEN}📝 Bullseye Credentials Integrated:${NC}"
    echo ""
    echo -e "${PURPLE}✅ Bot Token: 8436081597:AAE-8bfWrbvhl26-l9y65p48DfWjQOYPR2A${NC}"
    echo -e "${PURPLE}✅ Channel ID: -1001802424804 (@ZalheraThink)${NC}"
    echo -e "${PURPLE}✅ Armbian: 20.05 Bullseye${NC}"
    echo -e "${PURPLE}✅ GUI Support: Built-in (${DE_DETECTED})${NC}"
    echo -e "${PURPLE}✅ AnyDesk: ${ANYDESK_ID}${NC}"
    echo ""
    echo -e "${YELLOW}🌟 JMDKH Features Ready:${NC}"
    echo "• Torrent & Magnet downloads"
    echo "• Google Drive cloning" 
    echo "• Multi-server mirroring"
    echo "• Built-in GUI remote access"
    echo "• No unnecessary desktop installation"
    echo ""
    echo -e "${YELLOW}📝 Optional Configuration:${NC}"
    echo "1. BOT_USERNAME - For inline commands"
    echo "2. GOOGLE_CLIENT_ID - For Google Drive"
    echo "3. GOOGLE_CLIENT_SECRET - For Google Drive"
    echo ""
    echo -e "${BLUE}Edit command: nano .env${NC}"
    echo ""
fi

# Set proper permissions for Bullseye
echo -e "${BLUE}🔧 Setting Bullseye permissions...${NC}"
chown -R $(logname):$(logname) . 2>/dev/null || chown -R root:root .
chmod +x scripts/*.sh

# Configure AnyDesk (if installed)
if command -v anydesk &> /dev/null; then
    echo -e "${PURPLE}🔧 Configuring AnyDesk for built-in GUI...${NC}"

    # Set unattended access
    anydesk --set-password bullseyeaccess 2>/dev/null || true

    # Enable service
    systemctl enable anydesk 2>/dev/null || true
    systemctl start anydesk 2>/dev/null || true

    echo -e "${GREEN}✅ AnyDesk configured for built-in GUI remote access${NC}"
fi

# Show comprehensive system information
echo -e "${CYAN}📊 Bullseye STB HG680P System Information:${NC}"
echo "CPU: $(cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2 | xargs)"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2}') total"
echo "Storage: $(df -h / | awk 'NR==2 {print $4}') available"
echo "Architecture: $(uname -m)"

if [ -f "/etc/armbian-release" ]; then
    source /etc/armbian-release
    echo "Armbian Version: $VERSION"
    echo "Armbian Branch: $BRANCH"
    echo "Board: $BOARD"
fi

# Display services status
echo ""
echo -e "${CYAN}🔧 Services Status:${NC}"
echo "Docker: $(systemctl is-active docker)"
if command -v anydesk &> /dev/null; then
    echo "AnyDesk: $(systemctl is-active anydesk)"
    echo "AnyDesk ID: $(anydesk --get-id 2>/dev/null || echo 'Will be available after restart')"
fi

# Check GUI availability
echo ""
echo -e "${PURPLE}🖥️ Built-in GUI Status:${NC}"
if [ "$GUI_AVAILABLE" = true ]; then
    echo "GUI: ✅ Built-in GUI active (${DE_DETECTED})"
    echo "Display: ${DISPLAY:-'Not set but GUI running'}"
else
    echo "GUI: 🔄 Built-in GUI available but not running"
    echo "Note: GUI can be started or accessed via AnyDesk"
fi

echo ""
echo -e "${GREEN}✅ STB HG680P Bullseye setup completed successfully!${NC}"
echo ""
echo -e "${CYAN}🎉 Enhanced features ready:${NC}"
echo -e "${PURPLE}• Bot Token and Channel ID integrated${NC}"
echo -e "${PURPLE}• JMDKH features ready for deployment${NC}"
echo -e "${PURPLE}• Built-in GUI support (no extra desktop)${NC}"
echo -e "${PURPLE}• AnyDesk remote access to built-in GUI${NC}"
echo -e "${PURPLE}• Lightweight and optimized${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Edit .env: nano .env (add Google credentials)"
echo "2. Start enhanced bot: ./start.sh"
echo "3. Check logs: ./logs.sh"
echo "4. Remote access: Use AnyDesk ID above"
echo "5. Test built-in GUI: /anydesk command"
echo ""
echo -e "${CYAN}🎉 Your optimized Bullseye STB is ready!${NC}"
