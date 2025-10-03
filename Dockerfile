FROM --platform=linux/arm64 python:3.11-slim-bookworm

ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV PYTHONUNBUFFERED=1
ENV AUTO_CLEANUP_ENABLED=true

# Run as root for system access
USER root

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    curl \
    wget \
    ffmpeg \
    aria2 \
    sudo \
    git \
    python3-magic \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp (latest version)
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp

# Install Python requirements
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --break-system-packages -r requirements.txt

# Create directories
RUN mkdir -p /app/data /app/credentials /app/downloads /app/logs /app/temp && \
    chmod 755 /app/data /app/downloads /app/logs /app/temp && \
    chmod 700 /app/credentials

# Copy application
COPY app/ /app/

# Set permissions
RUN chmod +x /app/bot.py

CMD ["python", "bot.py"]
