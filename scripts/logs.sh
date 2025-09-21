#!/bin/bash
# Multi-Version STB Logs Script

echo "📋 Multi-Version STB HG680P Bot Logs"
echo "🖥️ Support: Armbian 20.11 Bullseye & 25.11 Bookworm"
echo "Press Ctrl+C to exit"
echo ""

docker-compose logs -f --tail=100
