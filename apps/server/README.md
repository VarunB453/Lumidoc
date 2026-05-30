# Lumidoc — AI-Powered Document & Media Chat Backend

A production-grade, async FastAPI backend for chatting with your PDFs, audio, and video files.
Built with LangChain + LlamaIndex (hybrid RAG), OpenRouter chat/embeddings + OpenAI Whisper, FAISS (Pinecone optional),
MongoDB, Redis, and Celery — all containerized and CI/CD ready.

---

## ✨ Features

- **Multi-modal ingest** — Upload PDF (PyMuPDF + pdfplumber fallback), audio (MP3/WAV/M4A), or
  video (MP4/MOV). Audio/video is transcribed with Whisper at word-level timestamps.
- **Hybrid RAG** — LlamaIndex `TreeSummarize` for hierarchical summaries; LangChain LCEL chain
  for chat with retrieval, conversational memory, and citation extraction.
- **Per-user namespace isolation** in FAISS (`{user_id}__{file_id}`), persisted to disk and
  swappable for Pinecone via env flag.
- **Streaming** — SSE endpoint that streams GPT-4o tokens + source-chunk citations + final
  timestamp metadata in one event stream.
- **Async everywhere** — Motor (Mongo), `redis.asyncio`, `aioboto3`, `httpx` AsyncClient,
  full FastAPI `async def` route handlers.
- **Auth** — JWT RS256 (asymmetric), bcrypt-12 passwords, refresh-token rotation with Redis
  blacklist, Google OAuth2 via Authlib.
- **Production middleware stack** — CORS → TrustedHost → RequestID → Logging → Redis
  sliding-window rate limit (per-IP + per-user) → JWT auth → global exception handler.
- **Background processing** — Celery + Redis broker with dedicated queues per modality
  (`pdf` / `audio` / `video` / `summary` / `timestamps`), retry with exponential backoff.
- **Observability** — `structlog` JSON logs, `X-Request-ID` tracing header, response-time
  header.
- **Tests** — pytest + pytest-asyncio + httpx AsyncClient + mongomock + fakeredis,
  targeting **≥ 95 % coverage**.

---

## 🏗 Architecture

```
                            ┌─────────────┐
                            │  Frontend   │
                            └──────┬──────┘
                                   │ HTTPS
                            ┌──────▼──────┐
                            │   Nginx     │  (TLS / SSE-friendly proxy)
                            └──────┬──────┘
                                   │
              ┌────────────────────▼─────────────────────┐
              │              FastAPI (Hono of Python)    │
              │  ┌────────────────────────────────────┐  │
              │  │ Middleware: CORS → TrustedHost →   │  │
              │  │  RequestID → Logging → RateLimit → │  │
              │  │  Auth → ExceptionHandler           │  │
              │  └────────────────────────────────────┘  │
              │  Routers: /auth /files /chat /summaries  │
              │           /timestamps                    │
              └──┬───────────────────────┬───────────────┘
                 │                       │
        ┌────────▼────┐        ┌─────────▼─────────┐
        │   MongoDB   │        │       Redis       │
        │ (users,     │        │ cache + queue +   │
        │  files,     │        │ blacklist + RL    │
        │  conv,...)  │        └─────────┬─────────┘
        └─────────────┘                  │
                                ┌────────▼────────┐
                                │ Celery Workers  │
                                │  pdf / audio /  │
                                │  video / summ.  │
                                └────────┬────────┘
                                         │
   ┌─────────────┐  ┌─────────────┐  ┌───▼──────────┐  ┌─────────────┐
   │   OpenAI    │  │   Whisper   │  │   FAISS /    │  │  S3 / Local │
   │  GPT-4o +   │  │  segments + │  │  Pinecone    │  │   storage   │
   │ embeddings  │  │ timestamps  │  │ (per-user NS)│  │             │
   └─────────────┘  └─────────────┘  └──────────────┘  └─────────────┘
```

---

## 🚀 Quick start (Docker)

```bash
cp .env.example .env                           # edit OPENROUTER_API_KEY at minimum
bash scripts/generate_keys.sh                  # generates ./keys/{private,public}.pem
docker compose up --build                      # API @ http://localhost:8000
```

Endpoints:
- API root: `http://localhost:8000/`
- Health:   `http://localhost:8000/health`
- Swagger:  `http://localhost:8000/docs`
- ReDoc:    `http://localhost:8000/redoc`

---

## 💻 Local dev (no Docker)

**Linux / macOS**
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# Start MongoDB and Redis locally (e.g. via Docker)
docker run -d -p 27017:27017 --name mongo mongo:7
docker run -d -p 6379:6379  --name redis redis:7-alpine

bash scripts/generate_keys.sh
cp .env.example .env

# API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another shell — Celery worker
celery -A app.celery_app worker --loglevel=info -Q pdf,audio,video,summary,timestamps,default
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# Start MongoDB and Redis locally (e.g. via Docker)
docker run -d -p 27017:27017 --name mongo mongo:7
docker run -d -p 6379:6379  --name redis redis:7-alpine

# Generate RSA keys (PowerShell equivalent)
New-Item -ItemType Directory -Force -Path keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem

Copy-Item .env.example .env   # then edit OPENROUTER_API_KEY

# API (runs on http://localhost:8000)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal — Celery worker
celery -A app.celery_app worker --loglevel=info -Q pdf,audio,video,summary,timestamps,default
```

> **Tip:** Uvicorn stdout/stderr are tailed in `uvicorn.out.log` / `uvicorn.err.log` when
> launched via the background process helper. Use `USE_LOCAL_STORAGE=true` and
> `VECTOR_BACKEND=faiss` (both default in `.env`) to avoid needing S3 or Pinecone in dev.

---

## 🧪 Testing

```bash
pytest --cov=app --cov-report=term-missing
```

The suite uses `mongomock-motor` for an in-memory MongoDB, `fakeredis` for Redis, and
monkey-patches all OpenAI calls — so no API keys or network are required.

CI enforces **`--cov-fail-under=95`**.

---

## 📚 API Reference (summary)

### Auth — `/api/v1/auth`
| Method | Path | Body | Description |
|---|---|---|---|
| POST | `/register` | `{email,password,name}` | Create account, returns user + tokens |
| POST | `/login` | `{email,password}` | Login, returns user + tokens |
| POST | `/refresh` | `{refresh_token}` | Rotate refresh, return new pair |
| POST | `/logout` | `{refresh_token}` | Blacklist refresh token |
| GET | `/google` | — | Redirect to Google consent |
| GET | `/google/callback` | — | Handle OAuth callback |

### Files — `/api/v1/files`
| Method | Path | Description |
|---|---|---|
| POST | `/upload` | Multipart upload, dispatches Celery task |
| GET | `/` | Paginated listing |
| GET | `/{file_id}` | Metadata + processing status |
| DELETE | `/{file_id}` | Soft-delete + drop vector namespace |
| GET | `/{file_id}/download` | 15-min presigned URL |

### Chat — `/api/v1/chat`
| Method | Path | Description |
|---|---|---|
| POST | `/conversations` | Create, optionally attach `file_ids` |
| GET | `/conversations` | List user's conversations |
| GET | `/conversations/{id}` | Get conversation |
| GET | `/conversations/{id}/messages` | Full history |
| POST | `/conversations/{id}/messages` | Send + return AI response |
| GET | `/conversations/{id}/messages/stream?q=...` | SSE token stream |

### Summaries — `/api/v1/summaries`
| Method | Path | Description |
|---|---|---|
| POST | `/{file_id}` | Trigger summarization (async, 202) |
| GET | `/{file_id}` | Get cached/freshly generated summary |

### Timestamps — `/api/v1/timestamps`
| Method | Path | Description |
|---|---|---|
| POST | `/{file_id}` | Trigger extraction (async, 202) |
| GET | `/{file_id}` | List all topic timestamps |
| GET | `/{file_id}/{topic}` | Topic search |

All protected routes require `Authorization: Bearer <access_token>`. The SSE stream
additionally accepts `?token=` for `EventSource` compatibility.

---

## 🔐 Security

- **Passwords**: bcrypt rounds=12.
- **JWT**: RS256, access 15 min, refresh 7 d, rotation on every refresh, Redis blacklist.
- **Input validation**: Pydantic v2 strict-mode schemas with custom validators.
- **File validation**: extension whitelist + MIME sniff (`python-magic`) + 500 MB cap.
- **Rate limits**: sliding-window Redis (100/min per IP, 30/min per user).
- **CORS**: explicit origin allowlist (no wildcard in production).
- **Secrets**: `.env` only; never logged, never committed.

---

## ⚙️ Configuration

All settings live in `app/core/config.py` (Pydantic Settings) and `.env`. See
[`.env.example`](.env.example) for the full reference — toggle:

- `USE_LOCAL_STORAGE` to skip S3 in dev
- `VECTOR_BACKEND=pinecone` + `USE_PINECONE=true` for cloud vectors
- `APP_ENV=production` to enable `TrustedHostMiddleware`

---

## 📂 Project layout

```
apps/server/
├── app/
│   ├── api/v1/endpoints/      # auth, files, chat, summaries, timestamps
│   ├── core/                  # config, logging, security, exceptions
│   ├── db/                    # mongodb, redis_client
│   ├── middleware/            # request_id, logging, rate_limit, auth
│   ├── models/                # Mongo doc helpers
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # storage, vector_store, embeddings,
│   │                          # pdf, transcription, chat, summary,
│   │                          # timestamp, auth, oauth
│   ├── tasks/                 # Celery tasks per modality
│   ├── utils/
│   ├── celery_app.py
│   └── main.py
├── tests/
│   ├── unit/   integration/   e2e/
│   └── conftest.py            # in-memory Mongo + fakeredis + OpenAI mocks
├── alembic/                   # DB migration scripts
├── keys/                      # RS256 private.pem + public.pem (git-ignored)
├── nginx/nginx.conf
├── scripts/generate_keys.sh
├── storage/                   # Local file + FAISS index storage (dev only)
├── .github/workflows/         # ci.yml + cd.yml
├── Dockerfile (multi-stage)
├── Dockerfile.celery
├── docker-compose.yml
├── docker-compose.dev.yml
├── pyproject.toml / requirements.txt / requirements-dev.txt
├── ruff.toml / mypy.ini / pytest.ini
├── uvicorn.out.log            # stdout when run as background process
├── uvicorn.err.log            # stderr when run as background process
└── .env.example
```

---

## 📜 License

MIT — use at will.
