
FROM --platform=linux/arm64 python:3.11-slim-bookworm
ENV PIP_BREAK_SYSTEM_PACKAGES=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN python -m pip install --no-cache-dir --break-system-packages -r requirements.txt
COPY app/ /app/
CMD ["python","/app/bot.py"]
