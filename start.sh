
#!/bin/bash
set -e
export $(grep -v '^#' .env | xargs) 2>/dev/null || true
project_name=stb-bot-cli
if docker ps --format '{{.Names}}' | grep -q "${project_name}"; then
  docker compose stop
  docker compose rm -f
fi
port=8080; while ss -ltn | awk '{print $4}' | grep -q ":$port$"; do port=$((port+1)); done
export OAUTH_PORT=$port
echo "Using OAuth port $port"
docker compose build
docker compose up -d
