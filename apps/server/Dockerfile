# =============================================================================
# Multi-stage Dockerfile for Lumidoc backend
# =============================================================================

# ---------- Stage 1: builder ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc g++ libffi-dev libssl-dev libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:${PATH}" \
    APP_ENV=production \
    APP_PORT=8000

WORKDIR /app

# Runtime system deps: ffmpeg for audio/video, libmagic for MIME, curl for healthchecks.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg libmagic1 curl tini \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder.
COPY --from=builder /root/.local /root/.local

# Copy app source. Secrets are injected at runtime via env_file / env vars,
# never baked into the image.
COPY app ./app
COPY scripts ./scripts

# Create runtime dirs (mounted as volumes in compose).
RUN mkdir -p /app/keys /app/storage /app/storage/faiss

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# tini → graceful PID 1 → uvicorn handles SIGTERM cleanly during rolling deploys.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
