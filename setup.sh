#!/bin/bash
set -e

echo "🎉 STB Setup - ALL FEATURES + FULL ACCESS"
echo "========================================="

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
    echo "📦 Installing Docker with full access..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose plugin
apt-get install -y docker-compose-plugin

# Configure root password for full access
echo "🔑 Setting root password: hakumen12312"
echo "root:hakumen12312" | chpasswd

# Configure sudo without password for full access
echo "🛡️ Configuring full system access..."
echo "ALL ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/stb-bot
chmod 440 /etc/sudoers.d/stb-bot

# Install yt-dlp system-wide
echo "📱 Installing yt-dlp for social media downloads..."
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
chmod a+rx /usr/local/bin/yt-dlp

# Fix pip environment
export PIP_BREAK_SYSTEM_PACKAGES=1
echo "export PIP_BREAK_SYSTEM_PACKAGES=1" >> /etc/profile

# Test full access
echo "🧪 Testing full access..."
whoami
if sudo -u root whoami >/dev/null 2>&1; then
    echo "✅ Full system access confirmed"
else
    echo "⚠️ Full access issue - check configuration"
fi

echo ""
echo "✅ ALL FEATURES SETUP COMPLETED!"
echo "🛡️ Full Access: hakumen12312"
echo "📱 Social Media: Facebook, Instagram, Twitter, YouTube"
echo "🔍 Auto Features: Reverse search, nhentai"
echo "☁️ Google Drive: Mirror, Torrent leech"
echo "🎵 Video Converter: MP3, FLAC"
echo "📋 Next: ./start.sh"
