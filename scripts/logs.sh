#!/bin/bash
# STB Logs Script for Built-in GUI Bullseye

echo "📋 STB HG680P Built-in GUI Bot Logs"
echo "🖥️ Built-in GUI + AnyDesk Support"
echo "Press Ctrl+C to exit"
echo ""

docker-compose logs -f --tail=100
