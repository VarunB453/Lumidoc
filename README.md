# Lumidoc

Lumidoc is a full-stack document and media intelligence platform. It lets users upload PDFs, audio, and video, processes them in background workers, and exposes a conversational RAG interface with summaries, timestamps, and source-grounded answers.

The current repository is a monorepo with a React/Vite frontend, a FastAPI backend, Celery workers, MongoDB, Redis, Docker Compose, Terraform scaffolding, operational docs, and shared TypeScript API types.

## Table of Contents

- [What It Does](#what-it-does)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Development Workflow](#development-workflow)
- [API Surface](#api-surface)
- [Testing and Quality](#testing-and-quality)
- [Deployment Workflow](#deployment-workflow)
- [Operations and Security](#operations-and-security)
- [Project Docs](#project-docs)
- [License](#license)

## What It Does

- Upload and manage PDFs, audio files, and video files.
- Process files asynchronously through Celery queues.
- Extract PDF text and metadata.
- Transcribe audio/video content with Whisper-backed services.
- Create summaries and topic timestamps for processed files.
- Store source chunks in a pluggable vector backend: FAISS locally or Pinecone in managed environments.
- Chat with uploaded content through retrieval-augmented generation.
- Stream chat responses over Server-Sent Events.
- Authenticate users with email/password JWT flows and optional Google OAuth.
- Serve a responsive React SPA with dashboard, upload, file library, chat, and settings pages.

## Architecture

```text
Browser
  |
  | HTTP, SSE
  v
React SPA / Nginx edge
  |
  | /api/v1, /local-files, /health
  v
FastAPI application
  |
  |-- MongoDB: users, files, conversations, messages, summaries, timestamps
  |-- Redis: cache, rate limiting, Celery broker/result backend
  |-- Vector store: FAISS local indexes or Pinecone
  |-- Local/S3 storage: uploaded source files and derived artifacts
  |
  v
Celery workers and beat
  |
  |-- PDF extraction
  |-- Audio/video transcription
  |-- Embeddings
  |-- Summary generation
  |-- Timestamp generation
  v
AI providers
  |
  |-- OpenRouter-compatible chat and embedding models
  |-- OpenAI Whisper transcription
  |-- Optional Google Gemini integration
```

Backend layering follows the current `apps/server/app` layout:

```text
api/v1/endpoints -> services -> repositories -> db/models
       |              |              |
       |              |              +-- MongoDB document access
       |              +-- business logic, RAG, storage, transcription
       +-- request/response schemas, auth dependencies, HTTP routes
```

## Repository Structure

```text
.
|-- .github/
|   `-- instructions/              # Repository instructions for automation tools
|-- Images/                         # Project screenshots/assets
|-- apps/
|   |-- client/                     # React 18 + Vite + TypeScript SPA
|   |   |-- src/
|   |   |   |-- animations/         # Page, chat, and sidebar animations
|   |   |   |-- assets/             # Global styles, icons, theme placeholders
|   |   |   |-- components/         # Chat, files, layout, upload, UI primitives
|   |   |   |-- config/             # Typed Vite env and constants
|   |   |   |-- features/           # Feature module placeholders
|   |   |   |-- hooks/              # Reusable app hooks
|   |   |   |-- lib/                # API client, utilities, analytics, logging
|   |   |   |-- pages/              # Dashboard, login, chat, upload, files, settings
|   |   |   |-- routes/             # Private/public route guards
|   |   |   |-- store/              # Zustand store
|   |   |   `-- types/              # Frontend domain/API types
|   |   |-- tests/                 # Vitest, integration, mocks, Playwright smoke test
|   |   |-- Dockerfile
|   |   |-- nginx.conf
|   |   |-- package.json
|   |   `-- vite.config.ts
|   `-- server/                     # FastAPI backend and worker code
|       |-- app/
|       |   |-- api/v1/endpoints/   # auth, users, files, chat, summaries, timestamps
|       |   |-- core/               # config, security, logging, telemetry, exceptions
|       |   |-- db/                 # MongoDB, Redis, indexes, migrations placeholder
|       |   |-- integrations/       # OpenAI, OpenRouter, Gemini, S3, OAuth providers
|       |   |-- middleware/         # auth, CORS, rate limit, request id, logging
|       |   |-- models/             # Mongo document helpers
|       |   |-- repositories/       # Data-access abstractions
|       |   |-- schemas/            # Pydantic request/response models
|       |   |-- services/           # Auth, chat, file, PDF, storage, summary, timestamps
|       |   |-- tasks/              # Celery jobs per processing workflow
|       |   |-- utils/              # Validation, file, text, datetime helpers
|       |   |-- workers/            # Celery worker/beat entry points
|       |   |-- celery_app.py
|       |   `-- main.py
|       |-- docs/ai/               # AI/module summaries
|       |-- scripts/               # Server maintenance scripts
|       |-- tests/                 # Unit, integration, and e2e tests
|       |-- Dockerfile
|       |-- Dockerfile.celery
|       |-- requirements.txt
|       `-- requirements-dev.txt
|-- docs/
|   |-- architecture/               # Architecture notes and ADRs
|   |-- runbooks/                   # Deployment, rollback, incident response
|   |-- CHANGELOG.md
|   |-- CODE_OF_CONDUCT.md
|   |-- CONTRIBUTING.md
|   |-- ENVIRONMENT.md
|   `-- SECURITY.md
|-- infrastructure/
|   |-- docker/                     # Alternative compose files and Dockerfiles
|   |-- k8s/                        # Kustomize scaffold placeholders
|   |-- nginx/                      # Nginx configs and snippets
|   |-- observability/              # Prometheus/Grafana/Loki scaffold placeholders
|   `-- terraform/                  # Cloud Run module and dev environment
|-- packages/
|   `-- shared-types/               # Shared/generated TypeScript API types
|-- scripts/                        # Root bootstrap, keys, backup, restore, healthcheck
|-- docker-compose.yml              # Root full-stack Compose workflow
|-- Makefile                        # Local shortcut targets
|-- README.md
`-- LICENSE
```

Some infrastructure folders are intentionally scaffolded with `.gitkeep` files. Treat them as ownership boundaries for future manifests or dashboards, not as complete production deployments.

## Tech Stack

| Area | Current stack |
| --- | --- |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, React Router, Zustand, TanStack Query, Axios |
| UI and motion | Framer Motion, GSAP, Three.js, Lucide React, React Hot Toast |
| Backend API | Python 3.11, FastAPI, Uvicorn, Pydantic v2, Pydantic Settings |
| Data | MongoDB 7 through Motor/PyMongo, Redis 7 |
| Workers | Celery with Redis broker/result backend |
| AI/RAG | OpenRouter-compatible chat and embeddings, OpenAI Whisper, Google Gemini integration, LangChain, LlamaIndex |
| Vector search | FAISS local backend, optional Pinecone backend |
| Storage | Local filesystem for development, S3-compatible storage for deployed environments |
| Auth | RS256 JWT, refresh tokens, bcrypt/passlib, Authlib Google OAuth |
| Edge/runtime | Nginx, Docker, Docker Compose |
| Infrastructure | Terraform Cloud Run module, K8s/observability scaffolds |
| Testing | Pytest, pytest-asyncio, pytest-cov, Vitest, Testing Library, Playwright |
| Quality | Ruff, mypy, ESLint, Prettier, pre-commit |

## Prerequisites

Install these for full local development:

| Tool | Version | Used for |
| --- | --- | --- |
| Node.js | 20+ | Frontend development and builds |
| npm | 10+ | Frontend dependency installation |
| Python | 3.11+ | FastAPI backend and Celery workers |
| Docker Engine | 24+ | Full stack dependencies and container workflow |
| Docker Compose | v2 | Root `docker compose` workflow |
| OpenSSL | 1.1+ | Local RS256 key generation |
| Git | Any current version | Source control |
| make | Optional | Shortcut commands in `Makefile` |

Optional native tools:

- `ffmpeg` for local audio/video processing outside Docker.
- `libmagic` for MIME detection outside Docker.
- `pre-commit` for local hook execution.
- MongoDB and Redis only if you do not use Docker for local dependencies.

Windows notes:

- Bash scripts under `scripts/` are intended for WSL2 or Git Bash.
- JWT key generation has a PowerShell equivalent: `scripts/generate_keys.ps1`.

## Environment Setup

Create local environment files from the committed examples:

```bash
cp apps/server/.env.example apps/server/.env
cp apps/client/.env.example apps/client/.env.development
```

PowerShell:

```powershell
Copy-Item apps\server\.env.example apps\server\.env
Copy-Item apps\client\.env.example apps\client\.env.development
```

Edit `apps/server/.env` before running real AI flows:

- `SECRET_KEY`: strong random string for sessions/OAuth.
- `OPENROUTER_API_KEY`: required for chat and embeddings.
- `OPENAI_API_KEY`: required for Whisper transcription.
- `VECTOR_BACKEND`: `faiss` for local development, `pinecone` for managed vector search.
- `USE_LOCAL_STORAGE`: `true` for local disk storage, `false` for S3-compatible storage.
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: only needed for Google OAuth.

Generate RS256 keys for local backend runs:

```bash
bash scripts/generate_keys.sh
```

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\generate_keys.ps1
```

The backend defaults to `apps/server/keys/private.pem` and `apps/server/keys/public.pem` when run from `apps/server`.

Frontend env values are read through `apps/client/src/config/env.ts`:

| Variable | Local default | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `/api/v1` | API base path used by Axios |
| `VITE_API_ORIGIN` | `http://localhost:8000` | Absolute API origin for OAuth/EventSource cases |
| `VITE_API_TIMEOUT_MS` | `60000` | Non-streaming request timeout |
| `VITE_DEV_PROXY_TARGET` | `http://localhost:8000` | Vite proxy target |

For the full environment reference, see [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md).

## Development Workflow

### 1. Bootstrap dependencies

The scripted bootstrap installs frontend and backend dependencies, copies env examples, generates keys, and installs pre-commit hooks when available:

```bash
make bootstrap
```

Equivalent manual setup:

```bash
cd apps/client
npm ci
cd ../server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cd ../..
bash scripts/generate_keys.sh
```

PowerShell activation:

```powershell
cd apps\server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
cd ..\..
```

### 2. Run the full stack with Docker

From the repository root:

```bash
docker compose up -d --build
```

This starts:

- Frontend/Nginx at `http://localhost`
- FastAPI API inside the Compose network
- Celery worker and Celery beat
- MongoDB
- Redis

Health check:

```bash
curl -fsS http://localhost/health
```

Stop the stack:

```bash
docker compose down
```

The root Compose stack serves the API through the frontend Nginx container at `/api/v1`. For direct API docs at `http://localhost:8000/docs`, use the local hot-reload workflow below or temporarily expose the API service port.

### 3. Run locally with hot reload

Start MongoDB and Redis with Docker:

```bash
docker run -d --name lumidoc-mongo -p 27017:27017 mongo:7
docker run -d --name lumidoc-redis -p 6379:6379 redis:7-alpine
```

Start the backend:

```bash
cd apps/server
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Start the worker when testing processing flows:

```bash
cd apps/server
source .venv/bin/activate
celery -A app.celery_app worker --loglevel=info -Q pdf,audio,video,summary,timestamps,default
```

Start the frontend:

```bash
cd apps/client
npm run dev
```

Local URLs:

| Service | URL |
| --- | --- |
| Frontend | `http://localhost:5173` |
| API root | `http://localhost:8000/` |
| API docs | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |
| Health | `http://localhost:8000/health` |

### 4. Makefile shortcuts

Useful targets:

```bash
make dev-client
make dev-server
make build-client
make build-server
make test-client
make test-server
make lint-client
make lint-server
make generate-keys
```

Check the target implementation before using Docker targets from `Makefile`; the root `docker-compose.yml` is the canonical full-stack Compose workflow for this checkout.

### 5. Shared types

Shared TypeScript types live in `packages/shared-types`:

```bash
cd packages/shared-types
npm install
npm run build
```

The package includes a `generate` script for OpenAPI-generated types. It expects an OpenAPI source file at `../docs/api/openapi.yaml`; create or export that file before running generation.

## API Surface

The FastAPI app serves metadata and docs at:

| Path | Purpose |
| --- | --- |
| `/` | API metadata |
| `/health` | Liveness/health response |
| `/docs` | Swagger UI |
| `/redoc` | ReDoc |
| `/openapi.json` | OpenAPI schema |

Versioned routes are mounted under `/api/v1`:

| Group | Prefix | Key capabilities |
| --- | --- | --- |
| Auth | `/api/v1/auth` | register, login, refresh, logout, Google OAuth |
| Users | `/api/v1/users` | profile/user operations |
| Files | `/api/v1/files` | upload, list, detail, delete, download URL |
| Chat | `/api/v1/chat` | conversations, messages, streaming answers |
| Summaries | `/api/v1/summaries` | trigger and read generated summaries |
| Timestamps | `/api/v1/timestamps` | trigger and read topic timestamps |
| Avatars | `/api/v1/avatars` | avatar upload/serve endpoints |
| Local files | `/local-files` and related routes | local storage file serving |

Protected API routes require:

```text
Authorization: Bearer <access_token>
```

Streaming chat endpoint shape:

```text
GET /api/v1/chat/conversations/{conversation_id}/messages/stream?q=<message>
```

The frontend uses `EventSource` for this route and can pass an auth token in the query string when browser APIs cannot set custom headers.

## Testing and Quality

Backend:

```bash
cd apps/server
pytest -v
pytest --cov=app --cov-report=term-missing
ruff check .
ruff format --check .
mypy app
```

Frontend:

```bash
cd apps/client
npm run typecheck
npm run lint
npm run test
npm run test:e2e
npm run build
```

Root shortcuts:

```bash
make test-server
make test-client
make lint-server
make lint-client
```

Recommended local workflow before opening a pull request:

1. Create a feature branch from `main`.
2. Update code and tests together.
3. Run the smallest relevant test suite while developing.
4. Run backend and frontend lint/type/test gates before final review.
5. Update docs or env examples when behavior/configuration changes.
6. Include screenshots or logs for UI and operational changes.

Pre-commit hooks are configured in [.pre-commit-config.yaml](.pre-commit-config.yaml). Install them with:

```bash
pip install pre-commit
pre-commit install
```

This checkout currently contains `.github/instructions/` but does not include committed `.github/workflows/` CI files. Until CI workflows are added, treat the local commands above as the required quality gate.

## Deployment Workflow

### Container deployment

The current production-like path is Docker:

```bash
docker compose up -d --build
```

For deployed environments:

- Provide a real `apps/server/.env` through secrets management or an env-file.
- Set `APP_ENV=production`.
- Set `FRONTEND_ORIGIN` and `ALLOWED_HOSTS` to the deployed domain.
- Use persistent storage for MongoDB, Redis, uploaded files, FAISS indexes, and JWT keys.
- Use `USE_LOCAL_STORAGE=false` with S3-compatible settings when local volumes are not appropriate.
- Keep `VITE_API_BASE_URL=/api/v1` when the frontend and API share the same origin.

### Terraform

Terraform files live under [infrastructure/terraform](infrastructure/terraform). The implemented module targets Cloud Run-style deployment boundaries:

```bash
cd infrastructure/terraform/environments/dev
terraform init
terraform plan
terraform apply
```

Review [infrastructure/terraform/README.md](infrastructure/terraform/README.md) before applying infrastructure.

### Kubernetes and observability

Kubernetes and observability folders exist as scaffolds:

- `infrastructure/k8s/base`
- `infrastructure/k8s/overlays/dev`
- `infrastructure/k8s/overlays/staging`
- `infrastructure/k8s/overlays/prod`
- `infrastructure/observability/prometheus`
- `infrastructure/observability/grafana`
- `infrastructure/observability/loki`

Add real manifests, dashboards, alerts, and environment overlays before using those paths for deployment.

## Operations and Security

Operational references:

- [docs/runbooks/deployment.md](docs/runbooks/deployment.md)
- [docs/runbooks/rollback.md](docs/runbooks/rollback.md)
- [docs/runbooks/incident-response.md](docs/runbooks/incident-response.md)

Security baseline:

- RS256 JWT signing through private/public PEM keys.
- Refresh-token rotation and Redis-backed token state.
- Password hashing through bcrypt/passlib.
- CORS allowlist through `FRONTEND_ORIGIN`.
- Trusted host enforcement in production through `ALLOWED_HOSTS`.
- Redis-backed rate limiting middleware.
- Structured logging through `structlog`.
- Upload validation by extension, MIME sniffing, and max size.
- Local or S3-compatible object storage.
- Secrets kept in env files or secret stores, not committed to source control.

Responsible disclosure and handling expectations are documented in [docs/SECURITY.md](docs/SECURITY.md).

## Project Docs

- [apps/client/README.md](apps/client/README.md): frontend-specific notes.
- [apps/server/README.md](apps/server/README.md): backend-specific notes.
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md): contribution standards.
- [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md): environment variable reference.
- [docs/architecture/README.md](docs/architecture/README.md): architecture overview.
- [docs/architecture/decisions](docs/architecture/decisions): ADRs.
- [docs/CHANGELOG.md](docs/CHANGELOG.md): project changelog.

## License

Released under the [MIT License](LICENSE).
