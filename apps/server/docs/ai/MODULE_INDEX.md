# Lumidoc Server — AI Module Index

Single-page map for AI assistants. Read this **first** before pulling source files.
For each module, the line count is the post-refactor target.

## API layer (`app/api/v1`)

| Module | Lines | Purpose |
|---|---|---|
| `router.py` | 25 | Aggregates all endpoint routers under `/api/v1`. |
| `dependencies.py` | 65 | `Depends(...)` helpers: current user, admin gate, pagination. |
| `endpoints/auth.py` | 65 | `register / login / refresh / logout / google[+callback]`. |
| `endpoints/users.py` | 95 | `/me` profile, password change, avatar upload. Schemas live in `schemas/user.py`. |
| `endpoints/files.py` | 75 | Upload (dispatches Celery), list (paginated), get, delete, presigned download. |
| `endpoints/chat.py` | 105 | Conversations CRUD + messages + SSE streaming. |
| `endpoints/summaries.py` | 50 | Trigger (202) + retrieve (200) per file_id. |
| `endpoints/timestamps.py` | 65 | Trigger + list + topic search per file_id. |
| `endpoints/misc.py` | 100 | `/translate` (Gemini), `/voice/transcribe` (Whisper). |
| `endpoints/local_files.py` | 45 | Auth-gated dev download for local-storage URLs. |
| `endpoints/avatars.py` | 30 | Public read-only route for avatars. |
| `endpoints/health.py` | 50 | `/health`, `/ready`, `/live`. |

## Services (`app/services`)

| Module | Lines | Purpose |
|---|---|---|
| `auth_service.py` | 165 | Register / login / OAuth-or-create / refresh-rotate / logout. |
| `chat/` (package) | 5×~80 | RAG chat split: `prompts`, `llm`, `retrieval`, `conversation`, `service`. |
| `chat_service.py` | 10 | Re-export shim — keep for back-compat. Prefer `services.chat`. |
| `embedding_service.py` | 65 | Gemini text-embedding-004 with batching + retry. |
| `file_service.py` | 105 | Upload validation, classification, list/get/delete/presign. |
| `oauth_service.py` | 65 | Authlib Google OAuth wrapper. |
| `pdf_service.py` | 75 | PyMuPDF text extraction + page-aware chunking. |
| `storage_service.py` | 105 | S3 + local-FS storage abstraction. |
| `summary_service.py` | 120 | LlamaIndex TreeSummarize + Gemini fallback + Redis cache. |
| `timestamp_service.py` | 145 | LLM topic-segmentation + sanitize + Redis cache + search. |
| `transcription_service.py` | 200 | Whisper + ffmpeg extract/split + segment chunker. (planned split) |
| `vector_store.py` | 230 | FAISS namespaces + Pinecone fallback. (planned split) |

## Tasks (`app/tasks`)

| Module | Lines | Purpose |
|---|---|---|
| `_runner.py` | 35 | Async-in-Celery helper + DB/Redis bootstrap. |
| `_processor.py` | 60 | Generic `@celery_processor` decorator. **Use this for any new file-processor task.** |
| `process_pdf.py` | 50 | PDF → text → chunks → embed → upsert. |
| `process_audio.py` | 60 | Audio → Whisper → chunks → embed → upsert. |
| `process_video.py` | 65 | Video → ffmpeg → audio → reuse audio pipeline. |
| `generate_summary.py` | 35 | Async wrapper around `summary_service.generate`. |
| `generate_timestamps.py` | 35 | Async wrapper around `timestamp_service.generate`. |
| `schedules.py` | small | Celery beat schedule definitions. |

## Schemas (`app/schemas`)

| Module | Purpose |
|---|---|
| `common.py` | `ORMModel`, `MessageResponse`, `HealthResponse`, `Page[T]`, `PaginationMeta`, `ErrorResponse`. |
| `user.py` | Register/Login/Public, `TokenPair`, `Refresh/Logout`, `ProfileUpdate`, `PasswordChange`, `AvatarResponse`. |
| `chat.py` | `ConversationCreate/Public/Update`, `MessageCreate/Public`, `SourceChunk`, `TimestampRef`. |
| `file.py` | `FileMetadata`, `FileUploadResponse`, `FileDownloadURL`. |
| `summary.py` | `SummaryResponse`, `SummaryStatusResponse`. |
| `timestamp.py` | `TimestampEntry`, `TimestampListResponse`, `TimestampStatusResponse`. |

## Models (`app/models`)

Lightweight Mongo-doc helpers (`doc()`, `insert()`, `find_by_id()`, `to_public()`).
There is also a parallel `app/repositories/` layer that is **not yet wired in**.
**Decide:** finish the migration, or delete the unused layer.

## Middleware (`app/middleware`)

Order (outer → inner): `CORS → TrustedHost? → Session → RequestID → Logging → RateLimit → Auth`.

## Integrations (`app/integrations`)

| Module | Purpose |
|---|---|
| `gemini_client.py` | Idempotent `configure_once()` + `get_model()` factory. **Use this everywhere instead of inline `genai.configure()`.** |
| `openai_client.py` | Lazy `AsyncOpenAI` factory. |
| `s3_client.py` | Lazy `boto3` client factory. |
| `oauth_providers/` | Provider-specific OAuth glue. |

## Conventions

- **Errors:** raise `app.core.exceptions.AppException` subclasses (`NotFoundError`, `ValidationError`, `ConflictError`, `UnauthorizedError`, `ForbiddenError`, `RateLimitError`, `ServiceUnavailableError`, `ExternalServiceError`). The global handler returns `{"error": {"code", "message", "details"}}`.
- **Async-only** at request layer; Celery tasks bridge via `tasks/_processor.py`.
- **Auth dependency:** `Depends(get_current_user_id)` from `middleware/auth.py`.
- **Response envelopes:** use Pydantic models from `schemas/`. Don't reinvent in routers.
- **Logging:** always `get_logger("scope_name")` and emit structured kwargs.
