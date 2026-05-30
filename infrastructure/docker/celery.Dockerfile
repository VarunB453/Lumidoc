FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY apps/server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/server/ ./

RUN adduser --disabled-password --gecos '' celeryuser && chown -R celeryuser /app
USER celeryuser

CMD ["celery", "-A", "app.celery_app:celery", "worker", "--loglevel=info", "--concurrency=4"]
