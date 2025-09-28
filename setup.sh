#!/bin/bash
set -e

echo "STB HG680P Setup - Bookworm CLI"
echo "================================"

# Update system
apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release python3 python3-pip python3-full git build-essential

# Install Docker
if ! command -v docker >/dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose plugin
apt-get install -y docker-compose-plugin

# Fix externally-managed-environment
export PIP_BREAK_SYSTEM_PACKAGES=1
echo "export PIP_BREAK_SYSTEM_PACKAGES=1" >> /etc/profile

echo "Setup completed successfully!"
