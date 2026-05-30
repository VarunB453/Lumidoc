# Environment Variables Reference

Complete reference for all environment variables used by Lumidoc.

---

## Backend (`apps/server/.env`)

### Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_ENV` | No | `development` | Environment mode: `development`, `staging`, `production`, `test` |
| `APP_NAME` | No | `Lumidoc` | Application name (used in logs and metadata) |
| `APP_VERSION` | No | `1.0.0` | Semantic version string |
| `APP_HOST` | No | `0.0.0.0` | Host to bind uvicorn to |
| `APP_PORT` | No | `8000` | Port to bind uvicorn to |
| `DEBUG` | No | `true` | Enable debug mode (verbose errors, auto-reload) |
| `SECRET_KEY` | **Yes** | — | Random string for session signing and CSRF. Generate with `openssl rand -hex 32` |
| `FRONTEND_ORIGIN` | **Yes** | `http://localhost:5173` | Comma-separated list of allowed CORS origins |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated allowed hostnames |

### JWT Authentication (RS256)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_ALGORITHM` | No | `RS256` | JWT signing algorithm |
| `JWT_PRIVATE_KEY_PATH` | **Yes** | `./keys/private.pem` | Path to RSA private key (PEM) |
| `JWT_PUBLIC_KEY_PATH` | **Yes** | `./keys/public.pem` | Path to RSA public key (PEM) |
| `ACCESS_TOKEN_TTL_MINUTES` | No | `15` | Access token lifetime in minutes |
| `REFRESH_TOKEN_TTL_DAYS` | No | `7` | Refresh token lifetime in days |
| `JWT_ISSUER` | No | `lumidoc` | JWT `iss` claim |
| `JWT_AUDIENCE` | No | `lumidoc-api` | JWT `aud` claim |

> Generate keys with `scripts/generate_keys.sh` (Linux/macOS) or `scripts/generate_keys.ps1` (Windows).

### MongoDB

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGODB_URL` | **Yes** | `mongodb://localhost:27017` | MongoDB connection string (supports Atlas SRV) |
| `MONGODB_DB_NAME` | No | `lumidoc` | Database name |

### Redis

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | **Yes** | `redis://localhost:6379/0` | Redis connection URL (scheme://host:port/db) |
| `REDIS_CACHE_DB` | No | `1` | Redis DB index for application cache |
| `REDIS_RATELIMIT_DB` | No | `2` | Redis DB index for rate limiting counters |

### Storage

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USE_LOCAL_STORAGE` | No | `true` | Use local filesystem instead of S3 |
| `LOCAL_STORAGE_PATH` | No | `./storage` | Directory for local file storage |
| `AWS_ACCESS_KEY_ID` | Prod | — | AWS access key (required when `USE_LOCAL_STORAGE=false`) |
| `AWS_SECRET_ACCESS_KEY` | Prod | — | AWS secret key |
| `AWS_REGION` | No | `us-east-1` | AWS region for S3 |
| `S3_BUCKET_NAME` | Prod | `lumidoc-files` | S3 bucket name |
| `S3_PRESIGNED_URL_TTL` | No | `900` | Presigned URL expiry in seconds (15 min) |
| `MAX_UPLOAD_SIZE_MB` | No | `500` | Maximum upload file size in MB |

### OpenAI

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | **Yes** | — | OpenAI API key (starts with `sk-`) |
| `OPENAI_MODEL` | No | `gpt-4o` | Chat completion model |
| `OPENAI_EMBEDDING_MODEL` | No | `text-embedding-3-small` | Embedding model |
| `OPENAI_WHISPER_MODEL` | No | `whisper-1` | Audio transcription model |
| `OPENAI_TEMPERATURE` | No | `0.2` | LLM temperature (0–2) |
| `OPENAI_MAX_TOKENS` | No | `2048` | Max tokens per completion |

### Vector Store

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VECTOR_BACKEND` | No | `faiss` | Vector backend: `faiss` or `pinecone` |
| `FAISS_INDEX_DIR` | No | `./storage/faiss` | Directory for FAISS index files |
| `USE_PINECONE` | No | `false` | Enable Pinecone backend |
| `PINECONE_API_KEY` | Pinecone | — | Pinecone API key |
| `PINECONE_ENVIRONMENT` | Pinecone | `us-east-1-aws` | Pinecone environment |
| `PINECONE_INDEX_NAME` | Pinecone | `lumidoc` | Pinecone index name |
| `EMBEDDING_DIM` | No | `1536` | Embedding vector dimension |

### Google OAuth2

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | OAuth | — | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth | — | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | OAuth | `http://localhost:8000/api/v1/auth/google/callback` | OAuth callback URL |
| `GOOGLE_FRONTEND_REDIRECT` | OAuth | `http://localhost:5173/auth/callback` | Frontend redirect after OAuth |

### Rate Limiting

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RATE_LIMIT_PER_IP` | No | `100` | Max requests per IP per window |
| `RATE_LIMIT_PER_USER` | No | `30` | Max requests per authenticated user per window |
| `RATE_LIMIT_WINDOW_SECONDS` | No | `60` | Rate limit window duration in seconds |

### Celery (Background Tasks)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CELERY_BROKER_URL` | No | `redis://localhost:6379/3` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | No | `redis://localhost:6379/4` | Celery result backend URL |
| `CELERY_CONCURRENCY` | No | `4` | Number of Celery worker processes |

### Logging

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOG_LEVEL` | No | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_JSON` | No | `true` | Output structured JSON logs |

---

## Frontend (`apps/client/.env`)

All frontend variables must be prefixed with `VITE_` to be exposed to the client bundle.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | No | `/api/v1` | API base path (relative for same-origin, absolute for cross-origin) |
| `VITE_API_ORIGIN` | No | `http://localhost:8000` | API origin for absolute URLs (EventSource, OAuth). Leave empty in production when same-origin. |
| `VITE_API_TIMEOUT_MS` | No | `60000` | Default request timeout in milliseconds (non-streaming, non-upload) |
| `VITE_DEV_PROXY_TARGET` | No | `http://localhost:8000` | Dev proxy target (Vite dev server only) |

---

## Docker Compose Overrides

When running via `docker-compose.yml`, these variables are overridden automatically to point at container service names:

| Variable | Docker Value | Purpose |
|----------|-------------|---------|
| `MONGODB_URL` | `mongodb://mongodb:27017` | Internal Docker network |
| `REDIS_URL` | `redis://redis:6379/0` | Internal Docker network |
| `CELERY_BROKER_URL` | `redis://redis:6379/3` | Internal Docker network |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/4` | Internal Docker network |
| `FRONTEND_ORIGIN` | `http://localhost` | Same-origin in Docker |

---

## Security Notes

1. **Never commit `.env` files** — they are in `.gitignore`.
2. **Rotate exposed keys immediately** — if secrets are accidentally committed, rotate them in the provider dashboard.
3. **Use a vault in production** — mount secrets from AWS Secrets Manager, HashiCorp Vault, or similar.
4. **JWT keys** — in production, mount pre-generated keys as Docker secrets or volume mounts. Do not use the auto-generation feature.
