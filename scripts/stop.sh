#!/bin/bash
# FIXED File Upload STB Stop Script

cd "$(dirname "$0")"

echo "🛑 Stopping FIXED File Upload STB Telegram Bot..."
echo "🖥️ Stopping FIXED file upload services..."

docker-compose down
docker stop telegram-bot-stb-fileupload-fixed aria2-stb-fileupload-fixed 2>/dev/null || true

echo "✅ FIXED File Upload STB Bot stopped"
echo "💾 Data preserved"
echo "📄 credentials.json preserved"
echo "🔧 externally-managed-environment: FIXED"
echo "🔄 Use ./start.sh to restart"
