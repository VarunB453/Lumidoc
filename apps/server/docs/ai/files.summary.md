# Files — AI Context Card

## Public surface
`POST   /api/v1/files/upload`             — multipart, dispatches Celery
`GET    /api/v1/files?page=&page_size=&status=`  — paginated
`GET    /api/v1/files/{id}`               — metadata
`DELETE /api/v1/files/{id}`               — soft-delete + remove vector NS
`GET    /api/v1/files/{id}/download`      — presigned URL

## Pipeline
upload → `FileService.upload` validates (size/ext/mime) → S3/local-FS via `storage_service.upload_bytes` → `FileModel.insert(status="pending")` → `_dispatch_processing` puts a job on the right Celery queue (`process_pdf` / `process_audio` / `process_video`).

Worker → download → extract or transcribe → chunk → embed (Gemini) → upsert into `vector_store` (FAISS namespace per `user__file`) → `FileModel.update_status("ready", extra={...})`.

## Schemas (`app/schemas/file.py`)
`FileType = "pdf"|"audio"|"video"`, `FileStatus = "pending"|"processing"|"ready"|"failed"`.
`FileMetadata`, `FileUploadResponse`, `FileDownloadURL`.

## Storage abstraction (`storage_service.py`)
- `USE_LOCAL_STORAGE=true` → writes under `LOCAL_STORAGE_PATH/` and `presigned_url()` returns `/local-files/{key}` (auth-gated).
- Otherwise: boto3 S3 with real presigned URLs.

## Gotchas
- Audio/video tasks store `transcript_text[:2_000_000]` and `transcript_segments[:10_000]` directly on the file doc — large docs. Migration path: `transcripts` collection or GridFS.
- `delete()` is best-effort on the vector namespace (logs warning on failure).
- Dispatch silently returns `task_id=None` if the broker is missing (dev mode); routers don't surface this.
