#!/bin/bash
# Multi-Version STB Stop Script

cd "$(dirname "$0")"

echo "🛑 Stopping Multi-Version STB Telegram Bot..."
echo "🖥️ Stopping multi-OS services..."

docker-compose down
docker stop telegram-bot-stb-multi aria2-stb-multi 2>/dev/null || true

echo "✅ Multi-Version STB Bot stopped"
echo "💾 Data preserved"
echo "🔄 Use ./start.sh to restart"
