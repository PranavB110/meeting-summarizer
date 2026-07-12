FROM python:3.11-slim

# ffmpeg is required by faster-whisper/av for audio decoding
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Mirror the same backend/frontend folder layout as the local repo,
# so path resolution in app/core/config.py and app/main.py (which
# walks up from __file__ to find the project root) works identically
# whether running locally or inside this container.
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/app backend/app
COPY frontend frontend

RUN mkdir -p storage/audio storage/transcripts

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]