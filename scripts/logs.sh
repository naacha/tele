#!/bin/bash
# FIXED File Upload STB Logs Script

echo "📋 FIXED File Upload STB HG680P Bot Logs"
echo "🖥️ FIXED: externally-managed-environment error resolved"
echo "Press Ctrl+C to exit"
echo ""

docker-compose logs -f --tail=100
