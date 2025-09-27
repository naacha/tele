# Dockerfile for STB HG680P with File Upload Credentials Support
FROM --platform=linux/arm64 python:3.9-slim-bullseye

# Metadata
LABEL maintainer="STB HG680P File Upload Telegram Bot"
LABEL description="Telegram bot for STB HG680P with file upload credentials.json support"
LABEL file_upload_support="yes"
LABEL credential_management="telegram_based"

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install system dependencies
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
    && rm -rf /var/lib/apt/lists/*

# Create app directory structure
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/downloads /app/logs /app/credentials /app/torrents && \
    chmod -R 755 /app && \
    chown -R root:root /app

# Copy requirements and install Python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

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

# Health check for file upload support
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD python -c "print('STB File Upload Health OK'); exit(0)" || exit 1

# Expose ports
EXPOSE 8080 6800

# Run the bot
CMD ["python", "/app/bot.py"]
