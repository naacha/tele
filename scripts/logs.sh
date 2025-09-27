#!/bin/bash
# File Upload STB Logs Script

echo "📋 File Upload STB HG680P Bot Logs"
echo "🖥️ Enhanced with Telegram File Upload for credentials.json"
echo "Press Ctrl+C to exit"
echo ""

docker-compose logs -f --tail=100
