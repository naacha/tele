#!/bin/bash
set -e

echo "Starting STB Telegram Bot"

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs) 2>/dev/null || true
else
    echo ".env file not found"
    echo "Create .env with BOT_TOKEN and other settings"
    exit 1
fi

# Stop existing containers of this project only
project_name="stb-bot-cli"
if docker ps --format '{{.Names}}' | grep -q "${project_name}"; then
    echo "Stopping existing bot containers..."
    docker compose stop
    docker compose rm -f
fi

# Find available port
port=8080
while ss -tuln | awk '{print $4}' | grep -q ":$port$"; do
    port=$((port + 1))
done

export OAUTH_PORT=$port
echo "Using OAuth port: $port"

# Create directories
mkdir -p data credentials downloads logs torrents
chmod 755 data downloads logs torrents
chmod 700 credentials

# Build and start
echo "Building Docker image..."
docker compose build

echo "Starting bot container..."
docker compose up -d

# Check status
sleep 10
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "STB Telegram Bot started successfully!"
    echo ""
    echo "Container Status:"
    docker compose ps
    echo ""
    echo "Setup Instructions:"
    echo "1. Owner: Send /auth to bot"
    echo "2. Owner: Upload credentials.json file"  
    echo "3. Owner: Complete OAuth with /code"
    echo "4. Users: Subscribe to ${REQUIRED_CHANNEL}"
    echo "5. Users: Use /d /t /dc commands"
    echo ""
else
    echo "Bot failed to start"
    docker compose logs --tail=30
fi
