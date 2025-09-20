#!/bin/bash
# STB Stop Script for Built-in GUI Bullseye

cd "$(dirname "$0")"

echo "🛑 Stopping STB Built-in GUI Telegram Bot..."
echo "🖥️ Stopping built-in GUI optimized services..."

docker-compose down
docker stop telegram-bot-stb-bullseye aria2-stb-bullseye 2>/dev/null || true

echo "✅ Built-in GUI STB Bot stopped"
echo "💾 Data preserved"
echo "🔄 Use ./start.sh to restart"
