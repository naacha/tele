#!/bin/bash
set -e

echo "🎉 Starting STB Bot - ALL FEATURES + FULL ACCESS"

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs) 2>/dev/null || true
else
    echo "❌ .env file not found"
    exit 1
fi

# Test full access first
echo "🧪 Testing full system access..."
if echo "hakumen12312" | sudo -S whoami >/dev/null 2>&1; then
    echo "✅ Full access confirmed"
else
    echo "⚠️ Full access issue - run setup.sh first"
fi

# Stop existing containers
project_name="stb-bot-complete"
if docker ps --format '{{.Names}}' | grep -q "${project_name}"; then
    echo "🛑 Stopping existing containers..."
    docker compose stop
    docker compose rm -f
fi

# Create directories with full access
echo "📁 Creating directories with full privileges..."
sudo mkdir -p data credentials downloads logs torrents temp
sudo chmod 755 data downloads logs torrents temp
sudo chmod 700 credentials
sudo chown -R $USER:$USER data downloads logs torrents credentials temp

echo "🔨 Building with all features + full access..."
docker compose build --no-cache

echo "🚀 Starting complete bot with full privileges..."
docker compose up -d

# Wait and check
sleep 20
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "✅ STB Bot started - ALL FEATURES + FULL ACCESS!"
    echo ""
    echo "🎉 COMPLETE FEATURE LIST:"
    echo "• ✅ Facebook downloader (/fb)"
    echo "• ✅ Instagram downloader (/ig)"
    echo "• ✅ Twitter downloader (/x)"
    echo "• ✅ YouTube downloader (/ytv)"  
    echo "• ✅ YouTube thumbnail (/ytm)"
    echo "• ✅ Video converter (/cv)"
    echo "• ✅ Reverse image search (auto on photo)"
    echo "• ✅ nhentai search (auto on numbers)"
    echo "• ✅ Google Drive mirror (/d)"
    echo "• ✅ Torrent leech (/t)"
    echo "• ✅ Google Drive clone (/dc)"
    echo ""
    echo "🛡️ FULL ACCESS FEATURES:"
    echo "• ✅ System privileges: hakumen12312"
    echo "• ✅ No permission issues"
    echo "• ✅ File system access"
    echo "• ✅ Directory management"
    echo ""
    echo "⚡ DOWNLOAD MANAGEMENT:"
    echo "• Speed: 5MB/s per user (shared)"
    echo "• Max: 2 concurrent downloads"
    echo "• Status: /etadl"
    echo "• Cancel: /stop1 /stop2"
    echo ""
    echo "📋 SETUP INSTRUCTIONS:"
    echo "1. Owner: /auth (upload credentials with full access)"
    echo "2. Owner: Upload credentials.json (no permission issues)"
    echo "3. Owner: /code <auth-code> (full access)"
    echo "4. Owner: /roottest (test all features)"
    echo "5. Users: Try all features!"
    echo ""
    echo "🔍 AUTO FEATURES:"
    echo "• Send photo → Auto reverse search"
    echo "• Send numbers → Auto nhentai search"
    echo ""
    echo "🔑 Full Access Password: hakumen12312"
    echo "Made by many fuck love @Zalhera"
    echo ""
else
    echo "❌ Bot failed to start"
    docker compose logs --tail=50
fi
