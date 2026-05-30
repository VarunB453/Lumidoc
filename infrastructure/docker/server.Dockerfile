# Base stage
FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY apps/server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base AS development

COPY apps/server/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY apps/server/ ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

COPY apps/server/ ./

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
