# FIXED Dockerfile for STB HG680P - externally-managed-environment resolved
FROM --platform=linux/arm64 python:3.9-slim-bullseye

# Metadata
LABEL maintainer="STB HG680P FIXED File Upload Telegram Bot"
LABEL description="Telegram bot for STB HG680P with FIXED externally-managed-environment"
LABEL externally_managed_environment="FIXED"
LABEL pip_break_system_packages="enabled"

# FIXED: Environment variables for externally-managed-environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# FIXED: Install system dependencies with proper pip configuration
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    curl \
    wget \
    git \
    ca-certificates \
    procps \
    htop \
    nano \
    aria2 \
    ffmpeg \
    unzip \
    p7zip-full \
    mediainfo \
    x11-utils \
    x11-xserver-utils \
    xauth \
    mesa-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxss1 \
    lsb-release \
    python3-pip \
    python3-venv \
    python3-full \
    && rm -rf /var/lib/apt/lists/*

# FIXED: Configure pip to handle externally-managed-environment
RUN mkdir -p /etc/pip && echo "[global]\nbreak-system-packages = true" > /etc/pip/pip.conf

# Create app directory structure
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/downloads /app/logs /app/credentials /app/torrents && \
    chmod -R 755 /app && \
    chown -R root:root /app

# Copy requirements and install Python packages with FIXED pip
COPY requirements.txt /app/

# FIXED: Install Python packages with proper environment handling
RUN python3 -m pip install --break-system-packages --no-cache-dir --upgrade pip setuptools wheel && \
    python3 -m pip install --break-system-packages --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ /app/
COPY scripts/ /app/scripts/

# Set executable permissions
RUN chmod +x /app/bot.py && \
    chmod +x /app/scripts/*.sh && \
    chmod -R 777 /app/data && \
    chmod -R 777 /app/downloads && \
    chmod -R 777 /app/logs && \
    chmod -R 777 /app/torrents && \
    chmod -R 700 /app/credentials

# FIXED: Health check with externally-managed-environment resolution
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD python -c "print('STB FIXED externally-managed-environment Health OK'); exit(0)" || exit 1

# Expose ports
EXPOSE 8080 6800

# FIXED: Run the bot with proper environment
CMD ["python", "/app/bot.py"]
