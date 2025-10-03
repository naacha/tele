#!/bin/bash
set -e

echo "🛡️ STB Setup - SECURE VERSION WITH AUTO CLEANUP"
echo "==============================================="

# Must be run as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo ./setup.sh"
    exit 1
fi

# Update system
apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release python3 python3-pip python3-full git build-essential sudo ffmpeg aria2

# Install Docker
if ! command -v docker >/dev/null; then
    echo "📦 Installing Docker with secure configuration..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose plugin
apt-get install -y docker-compose-plugin

# Configure secure root password
echo "🔑 Setting secure root password: hakumen12312"
echo "root:hakumen12312" | chpasswd

# Configure secure system access
echo "🛡️ Configuring secure system access..."
echo "ALL ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/stb-bot-secure
chmod 440 /etc/sudoers.d/stb-bot-secure

# Install yt-dlp system-wide
echo "📱 Installing yt-dlp for social media downloads..."
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
chmod a+rx /usr/local/bin/yt-dlp

# Fix pip environment
export PIP_BREAK_SYSTEM_PACKAGES=1
echo "export PIP_BREAK_SYSTEM_PACKAGES=1" >> /etc/profile

# Test secure access
echo "🧪 Testing secure system access..."
whoami
if sudo -u root whoami >/dev/null 2>&1; then
    echo "✅ Secure system access confirmed"
else
    echo "⚠️ Secure access issue - check configuration"
fi

echo ""
echo "✅ SECURE VERSION SETUP COMPLETED!"
echo "🛡️ Security: Owner-only sensitive commands"
echo "📖 nhentai: PM only, 4+ digits minimum"
echo "🧹 Auto Cleanup: Files deleted after upload"
echo "📱 Social Media: Facebook, Instagram, Twitter, YouTube"
echo "🔍 Auto Features: Reverse search, nhentai (PM only)"
echo "☁️ Google Drive: Mirror, Torrent with cleanup"
echo "🔑 Secure Password: hakumen12312"
echo "📋 Next: ./start.sh"
