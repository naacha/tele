FROM --platform=linux/arm64 python:3.11-slim-bookworm

ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --break-system-packages -r requirements.txt

# Create directories
RUN mkdir -p /app/data /app/credentials /app/downloads /app/logs /app/torrents

# Copy application
COPY app/ /app/

# Set permissions
RUN chmod +x /app/bot.py

CMD ["python", "bot.py"]
