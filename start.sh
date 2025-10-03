#!/bin/bash
set -e

echo "🛡️ Starting STB Bot - SECURE VERSION WITH AUTO CLEANUP"

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs) 2>/dev/null || true
else
    echo "❌ .env file not found"
    exit 1
fi

# Test secure access first
echo "🧪 Testing secure system access..."
if echo "hakumen12312" | sudo -S whoami >/dev/null 2>&1; then
    echo "✅ Secure access confirmed"
else
    echo "⚠️ Secure access issue - run setup.sh first"
fi

# Stop existing containers
project_name="stb-bot-secure"
if docker ps --format '{{.Names}}' | grep -q "${project_name}"; then
    echo "🛑 Stopping existing secure containers..."
    docker compose stop
    docker compose rm -f
fi

# Create directories with secure permissions
echo "📁 Creating directories with secure permissions..."
sudo mkdir -p data credentials downloads logs torrents temp
sudo chmod 755 data downloads logs torrents temp
sudo chmod 700 credentials
sudo chown -R $USER:$USER data downloads logs torrents credentials temp

echo "🔨 Building with secure configuration + auto cleanup..."
docker compose build --no-cache

echo "🚀 Starting secure bot with auto cleanup..."
docker compose up -d

# Wait and check
sleep 20
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "✅ STB Bot started - SECURE VERSION WITH AUTO CLEANUP!"
    echo ""
    echo "🛡️ SECURITY FEATURES:"
    echo "• ✅ Owner-only sensitive commands"
    echo "• ✅ System operations restricted to owner"
    echo "• ✅ Credentials upload: Owner only"
    echo "• ✅ OAuth setup: Owner only"
    echo "• ✅ System testing: Owner only"
    echo ""
    echo "📖 NHENTAI SECURITY:"
    echo "• ✅ PM only: Groups ignored"
    echo "• ✅ Minimum 4 digits (was 3)"
    echo "• ✅ Enhanced validation"
    echo ""
    echo "🧹 AUTO CLEANUP FEATURES:"
    echo "• ✅ Files deleted after upload"
    echo "• ✅ Temp directories cleaned"
    echo "• ✅ Download cleanup scheduled"
    echo "• ✅ System space management"
    echo ""
    echo "🎉 ALL FEATURES WITH SECURITY:"
    echo "• ✅ Facebook downloader (/fb) + cleanup"
    echo "• ✅ Instagram downloader (/ig) + cleanup"
    echo "• ✅ Twitter downloader (/x) + cleanup"
    echo "• ✅ YouTube downloader (/ytv) + cleanup"
    echo "• ✅ YouTube thumbnail (/ytm) + cleanup"
    echo "• ✅ Video converter (/cv) + cleanup"
    echo "• ✅ Reverse image search (auto on photo) + cleanup"
    echo "• ✅ nhentai search (PM only, 4+ digits) + cleanup"
    echo "• ✅ Google Drive mirror (/d) + cleanup"
    echo "• ✅ Torrent leech (/t) + cleanup"
    echo ""
    echo "📋 SECURE SETUP INSTRUCTIONS:"
    echo "1. Owner: /auth (owner only - secure upload)"
    echo "2. Owner: Upload credentials.json (secure handling)"
    echo "3. Owner: /code <auth-code> (owner only - secure)"
    echo "4. Owner: /roottest (owner only - system test)"
    echo "5. Users: Try all features with auto cleanup!"
    echo ""
    echo "🔍 AUTO FEATURES:"
    echo "• Send photo → Auto reverse search + cleanup"
    echo "• Send 4+ digits in PM → Auto nhentai + cleanup"
    echo ""
    echo "🔑 Secure Password: hakumen12312"
    echo "Made by many fuck love @Zalhera"
    echo ""
else
    echo "❌ Bot failed to start"
    docker compose logs --tail=50
fi
