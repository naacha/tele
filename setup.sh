#!/bin/bash
set -e

echo "🎉 STB Bot Setup - FINAL REVISION"
echo "=================================="

# Must be run as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo ./setup.sh"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release python3 python3-pip python3-full git build-essential sudo ffmpeg aria2

# Install Docker
if ! command -v docker >/dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose plugin
apt-get install -y docker-compose-plugin

# Install yt-dlp system-wide
echo "📱 Installing yt-dlp for social media downloads..."
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
chmod a+rx /usr/local/bin/yt-dlp

# Test yt-dlp
echo "🧪 Testing yt-dlp..."
if yt-dlp --version >/dev/null 2>&1; then
    echo "✅ yt-dlp installed successfully"
else
    echo "⚠️ yt-dlp installation issue"
fi

# Test ffmpeg
echo "🧪 Testing ffmpeg..."
if ffmpeg -version >/dev/null 2>&1; then
    echo "✅ ffmpeg available"
else
    echo "⚠️ ffmpeg installation issue"
fi

# Fix pip environment
export PIP_BREAK_SYSTEM_PACKAGES=1
echo "export PIP_BREAK_SYSTEM_PACKAGES=1" >> /etc/profile

echo ""
echo "✅ FINAL REVISION SETUP COMPLETED!"
echo "📱 Social Media: Facebook, Instagram, Twitter/X, YouTube"
echo "🔍 Reverse Search: Enhanced anime + illustration detection"
echo "📖 nhentai: PM-only, PDF downloads"
echo "🎵 Video Converter: MP3, FLAC"
echo "🧹 Auto Cleanup: Files deleted after upload"
echo "☁️ Google Drive: Optional (owner features)"
echo "📋 Next: ./start.sh"
