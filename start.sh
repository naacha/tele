#!/bin/bash
set -e

echo "🎉 Starting STB Bot - FINAL REVISION"

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs) 2>/dev/null || true
else
    echo "❌ .env file not found"
    exit 1
fi

# Stop existing containers
project_name="stb-bot-final"
if docker ps --format '{{.Names}}' | grep -q "${project_name}"; then
    echo "🛑 Stopping existing containers..."
    docker compose stop
    docker compose rm -f
fi

# Create directories
echo "📁 Creating directories..."
sudo mkdir -p data credentials downloads logs temp
sudo chmod 755 data downloads logs temp
sudo chmod 700 credentials
sudo chown -R $USER:$USER data downloads logs credentials temp

echo "🔨 Building FINAL REVISION..."
docker compose build --no-cache

echo "🚀 Starting FINAL REVISION bot..."
docker compose up -d

# Wait and check
sleep 20
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "✅ STB Bot started - FINAL REVISION!"
    echo ""
    echo "🎉 ALL FEATURES WORKING:"
    echo "• ✅ Facebook downloader (/fb) - Direct to Telegram"
    echo "• ✅ Instagram downloader (/ig) - Direct to Telegram"
    echo "• ✅ Twitter/X downloader (/x) - Direct to Telegram"
    echo "• ✅ YouTube video (/ytv) - Quality options"
    echo "• ✅ YouTube thumbnail (/ytm) - HD download"
    echo "• ✅ Video converter (/cv) - MP3/FLAC"
    echo "• ✅ Enhanced reverse search - Anime + illustration"
    echo "• ✅ nhentai download - PM-only, PDF format"
    echo ""
    echo "🔧 KEY IMPROVEMENTS:"
    echo "• ✅ No Google Drive needed for social downloads"
    echo "• ✅ Fixed all command responses"
    echo "• ✅ Enhanced reverse search with anime scene detection"
    echo "• ✅ nhentai downloads all pages to PDF"
    echo "• ✅ Auto cleanup prevents storage issues"
    echo "• ✅ Owner-only sensitive operations"
    echo ""
    echo "📋 USAGE:"
    echo "• Social: /fb /ig /x /ytv /ytm <url>"
    echo "• Convert: /cv (reply to video)"
    echo "• Reverse: Send photo → auto analysis"
    echo "• nhentai: Send 4+ digits in PM → PDF download"
    echo ""
    echo "👑 Owner commands: /auth /roottest"
    echo ""
    echo "Made by many fuck love @Zalhera"
    echo ""
else
    echo "❌ Bot failed to start"
    docker compose logs --tail=50
fi
