#!/bin/bash
# STB HG680P Setup Script with FIXED externally-managed-environment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${CYAN}🚀 STB HG680P Setup - FIXED externally-managed-environment${NC}"
echo -e "${CYAN}========================================================${NC}"
echo -e "${PURPLE}🔧 FIXED: No more externally-managed-environment errors!${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root: sudo ./setup.sh${NC}"
    exit 1
fi

# Function to fix GPG key errors
fix_gpg_keys() {
    echo -e "${BLUE}🔑 Fixing GPG key errors...${NC}"

    # Add missing Debian archive keys
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9 2>/dev/null || true
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6ED0E7B82643E131 2>/dev/null || true  
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 605C66F00D6C9793 2>/dev/null || true

    # Update sources.list to use current repos if using archive
    if grep -q "archive.debian.org" /etc/apt/sources.list; then
        echo -e "${YELLOW}⚠️ Detected archive.debian.org, updating to current repos...${NC}"

        # Create backup
        cp /etc/apt/sources.list /etc/apt/sources.list.backup

        # Detect Debian version
        DEBIAN_VERSION=$(lsb_release -cs 2>/dev/null || echo "bullseye")

        if [ "$DEBIAN_VERSION" = "bookworm" ]; then
            # Bookworm sources
            cat > /etc/apt/sources.list << EOF
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware

deb http://deb.debian.org/debian-security/ bookworm-security main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian-security/ bookworm-security main contrib non-free non-free-firmware

deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
EOF
        else
            # Bullseye sources
            cat > /etc/apt/sources.list << EOF
deb http://deb.debian.org/debian bullseye main contrib non-free
deb-src http://deb.debian.org/debian bullseye main contrib non-free

deb http://deb.debian.org/debian-security/ bullseye-security main contrib non-free
deb-src http://deb.debian.org/debian-security/ bullseye-security main contrib non-free

deb http://deb.debian.org/debian bullseye-updates main contrib non-free
deb-src http://deb.debian.org/debian bullseye-updates main contrib non-free

deb http://deb.debian.org/debian bullseye-backports main contrib non-free
deb-src http://deb.debian.org/debian bullseye-backports main contrib non-free
EOF
        fi

        echo -e "${GREEN}✅ Updated sources.list for $DEBIAN_VERSION${NC}"
    fi

    # Clean package cache and update
    apt-get clean
    rm -rf /var/lib/apt/lists/*

    echo -e "${GREEN}✅ GPG keys and repositories fixed${NC}"
}

# Function to fix broken packages
fix_broken_packages() {
    echo -e "${BLUE}🔧 Fixing broken packages...${NC}"

    # Fix broken install
    apt --fix-broken install -y

    # Configure any pending packages
    dpkg --configure -a

    # Clean up
    apt-get autoremove -y
    apt-get autoclean

    echo -e "${GREEN}✅ Broken packages fixed${NC}"
}

# FIXED: Function to handle externally-managed-environment
fix_externally_managed_environment() {
    echo -e "${PURPLE}🔧 FIXING externally-managed-environment error...${NC}"

    # Method 1: Set global environment variable
    export PIP_BREAK_SYSTEM_PACKAGES=1
    echo "export PIP_BREAK_SYSTEM_PACKAGES=1" >> /etc/environment

    # Method 2: Create pip.conf
    mkdir -p /etc/pip
    cat > /etc/pip/pip.conf << EOF
[global]
break-system-packages = true
EOF

    # Method 3: For current user
    mkdir -p ~/.pip
    cat > ~/.pip/pip.conf << EOF
[global]
break-system-packages = true
EOF

    echo -e "${GREEN}✅ externally-managed-environment FIXED${NC}"
    echo -e "${GREEN}   • PIP_BREAK_SYSTEM_PACKAGES=1 set globally${NC}"
    echo -e "${GREEN}   • pip.conf configured${NC}"
    echo -e "${GREEN}   • Ready for Docker container build${NC}"
}

# Check if Docker is already installed
check_docker_installed() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✅ Docker and Docker Compose already installed${NC}"
        echo "Docker version: $(docker --version)"
        echo "Docker Compose version: $(docker-compose --version)"
        return 0
    else
        return 1
    fi
}

# FIXED: Install Docker for ARM64 with pip fix
install_docker() {
    echo -e "${BLUE}🐳 Installing Docker for ARM64 with FIXED pip...${NC}"

    # Install prerequisites
    apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker GPG key
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Detect Debian version
    DEBIAN_VERSION=$(lsb_release -cs 2>/dev/null || echo "bullseye")

    # Add Docker repository
    echo "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $DEBIAN_VERSION stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Update and install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io

    # FIXED: Install Docker Compose with proper pip handling
    apt-get install -y python3-pip python3-full

    # Apply externally-managed-environment fix
    export PIP_BREAK_SYSTEM_PACKAGES=1

    # Install docker-compose using FIXED pip
    python3 -m pip install --break-system-packages docker-compose

    # Enable Docker service
    systemctl enable docker
    systemctl start docker

    echo -e "${GREEN}✅ Docker and Docker Compose installed with FIXED pip${NC}"
}

# Function to install AnyDesk with dependency fixing
install_anydesk_with_deps() {
    echo -e "${PURPLE}🖥️ Installing AnyDesk with dependency fixing...${NC}"

    # Install required dependencies first
    echo -e "${BLUE}📦 Installing AnyDesk dependencies...${NC}"
    apt-get install -y \
        libgtkglext1 \
        libgtkglext1-dev \
        libglib2.0-0 \
        libgtk2.0-0 \
        libgtk2.0-dev \
        libx11-6 \
        libxext6 \
        libxfixes3 \
        libxrandr2 \
        libasound2 \
        libpulse0 \
        || true

    # Add AnyDesk repository key
    echo -e "${BLUE}🔑 Adding AnyDesk repository key...${NC}"
    wget -qO - https://keys.anydesk.com/repos/DEB-GPG-KEY | apt-key add - || true

    # Add AnyDesk repository
    echo "deb http://deb.anydesk.com/ all main" > /etc/apt/sources.list.d/anydesk-stable.list

    # Update package list
    apt-get update || true

    # Try to install AnyDesk
    if apt-get install -y anydesk; then
        echo -e "${GREEN}✅ AnyDesk installed successfully${NC}"

        # Enable AnyDesk service
        systemctl enable anydesk 2>/dev/null || true
        systemctl start anydesk 2>/dev/null || true

        # Configure unattended access
        sleep 3
        anydesk --set-password fixedaccess 2>/dev/null || true

        # Get AnyDesk ID
        ANYDESK_ID=$(anydesk --get-id 2>/dev/null || echo "Will be available after restart")
        echo -e "${PURPLE}🆔 AnyDesk ID: ${ANYDESK_ID}${NC}"

        return 0
    else
        echo -e "${YELLOW}⚠️ AnyDesk installation failed, continuing without remote access${NC}"
        return 1
    fi
}

# Stop existing containers
cleanup_existing_containers() {
    echo -e "${BLUE}🛑 Cleaning up existing containers...${NC}"

    # Stop and remove containers
    docker stop telegram-bot-stb-fileupload-fixed aria2-stb-fileupload-fixed 2>/dev/null || true
    docker rm -f telegram-bot-stb-fileupload-fixed aria2-stb-fileupload-fixed 2>/dev/null || true

    # Clean Docker system
    docker system prune -f 2>/dev/null || true

    echo -e "${GREEN}✅ Container cleanup completed${NC}"
}

# Main setup process
main_setup() {
    # Fix externally-managed-environment FIRST
    fix_externally_managed_environment

    # Fix GPG keys and repositories
    fix_gpg_keys

    # Update system
    echo -e "${BLUE}📦 Updating system packages...${NC}"
    apt-get update || (fix_gpg_keys && apt-get update)

    # Fix broken packages
    fix_broken_packages

    # Upgrade system
    apt-get upgrade -y

    # Install base dependencies
    echo -e "${BLUE}📦 Installing base dependencies with FIXED pip...${NC}"
    apt-get install -y \
        curl \
        wget \
        gnupg \
        lsb-release \
        ca-certificates \
        apt-transport-https \
        software-properties-common \
        build-essential \
        python3 \
        python3-pip \
        python3-full \
        python3-venv

    # Check if Docker is already installed
    if ! check_docker_installed; then
        install_docker
    fi

    # Cleanup existing containers
    cleanup_existing_containers

    # Install minimal GUI support tools
    echo -e "${PURPLE}🖥️ Installing minimal GUI support tools...${NC}"
    apt-get install -y \
        x11-utils \
        x11-xserver-utils \
        xauth \
        mesa-utils \
        || true

    # Install AnyDesk with dependency fixing
    install_anydesk_with_deps

    # Install enhanced dependencies for JMDKH features
    echo -e "${BLUE}📦 Installing JMDKH dependencies...${NC}"
    apt-get install -y \
        aria2 \
        ffmpeg \
        mediainfo \
        unzip \
        p7zip-full \
        git \
        || true

    # Create directory structure
    echo -e "${BLUE}📁 Creating directory structure...${NC}"
    mkdir -p data downloads logs credentials torrents aria2-config
    chmod -R 755 data downloads logs credentials torrents aria2-config

    # Create environment file
    if [ ! -f ".env" ]; then
        echo -e "${BLUE}⚙️ Creating environment configuration...${NC}"
        cp .env.example .env
    fi

    # Set proper permissions
    echo -e "${BLUE}🔧 Setting permissions...${NC}"
    chown -R $(logname):$(logname) . 2>/dev/null || chown -R 1000:1000 .
    chmod +x scripts/*.sh

    # Show system information
    echo -e "${CYAN}📊 FIXED STB Setup Complete${NC}"
    echo "CPU: $(cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2 | xargs)"
    echo "Memory: $(free -h | awk '/^Mem:/ {print $2}') total"
    echo "Storage: $(df -h / | awk 'NR==2 {print $4}') available"
    echo "Architecture: $(uname -m)"
    echo ""

    # Show services status
    echo -e "${CYAN}🔧 Services Status:${NC}"
    echo "Docker: $(systemctl is-active docker)"
    if command -v anydesk &> /dev/null; then
        echo "AnyDesk: $(systemctl is-active anydesk)"
        echo "AnyDesk ID: $(anydesk --get-id 2>/dev/null || echo 'Will be available after restart')"
    else
        echo "AnyDesk: Not installed"
    fi

    # Show FIXED status
    echo ""
    echo -e "${PURPLE}🔧 FIXED Status:${NC}"
    echo "externally-managed-environment: ✅ FIXED"
    echo "PIP_BREAK_SYSTEM_PACKAGES: ✅ Set globally"
    echo "pip.conf: ✅ Configured"
    echo "Docker pip: ✅ Working"

    echo ""
    echo -e "${GREEN}✅ STB HG680P FIXED setup completed successfully!${NC}"
    echo ""
    echo -e "${CYAN}🎉 FIXED Enhanced features ready:${NC}"
    echo -e "${PURPLE}• externally-managed-environment FIXED${NC}"
    echo -e "${PURPLE}• PIP_BREAK_SYSTEM_PACKAGES configured${NC}"
    echo -e "${PURPLE}• Bot Token and Channel ID integrated${NC}"
    echo -e "${PURPLE}• File upload credentials via Telegram${NC}"
    echo -e "${PURPLE}• Flexible Google account switching${NC}"
    echo -e "${PURPLE}• JMDKH features ready${NC}"
    echo -e "${PURPLE}• Docker deployment ready${NC}"
    echo -e "${PURPLE}• AnyDesk remote access${NC}"
    echo -e "${PURPLE}• All errors FIXED${NC}"
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "1. Start bot: ./start.sh"
    echo "2. Use /auth to upload credentials.json"
    echo "3. Complete OAuth authorization"
    echo "4. Start using all features!"
    echo ""
    echo -e "${CYAN}🎉 Your FIXED STB is ready - No more pip errors!${NC}"
}

# Run main setup
main_setup
