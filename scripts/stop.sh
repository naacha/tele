#!/bin/bash
# File Upload STB Stop Script

cd "$(dirname "$0")"

echo "🛑 Stopping File Upload STB Telegram Bot..."
echo "🖥️ Stopping file upload services..."

docker-compose down
docker stop telegram-bot-stb-fileupload aria2-stb-fileupload 2>/dev/null || true

echo "✅ File Upload STB Bot stopped"
echo "💾 Data preserved"
echo "📄 credentials.json preserved"
echo "🔄 Use ./start.sh to restart"
