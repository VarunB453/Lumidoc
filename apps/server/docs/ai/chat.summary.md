# Chat — AI Context Card

## Public surface
`POST   /api/v1/chat/conversations`                    — create
`GET    /api/v1/chat/conversations?favorites=bool`     — list
`GET    /api/v1/chat/conversations/{id}`               — get
`PATCH  /api/v1/chat/conversations/{id}`               — title / favorite / file_ids
`DELETE /api/v1/chat/conversations/{id}`               — soft-delete
`GET    /api/v1/chat/conversations/{id}/messages`      — list messages
`POST   /api/v1/chat/conversations/{id}/messages`      — send + get answer (sync)
`GET    /api/v1/chat/conversations/{id}/messages/stream?q=` — SSE stream

## Service layout (`app/services/chat/`)
- `prompts.py` — system prompt + `PROMPT_TEMPLATE`.
- `llm.py` — `GeminiChatFactory` (sync + streaming clients, lazy).
- `retrieval.py` — `retrieve()`, `format_context()`, `format_history()`, `extract_timestamp_refs()`, meta builders.
- `conversation.py` — CRUD + ownership checks (depends on `ConversationModel`, `FileModel`, `MessageModel`).
- `service.py` — `ChatService` glue: `answer()` and `stream_answer()`.

## Data flow (one user question)
1. `ChatService._gather_inputs` validates conv, retrieves top-K chunks, loads recent history.
2. Persist user message.
3. Build LCEL chain: `RunnablePassthrough.assign(context, history) | PROMPT | llm | StrOutputParser`.
4. Sync: `await chain.ainvoke()`. Streaming: `async for token in chain.astream()`.
5. After completion: extract timestamp refs, persist assistant message, bump conv (`message_count += 2`).

## Streaming events (SSE)
`user_message → sources → token (×N) → done | error`

## Gotchas
- Streaming endpoint accepts `?token=` query param (EventSource cannot send headers).
- `retrieve()` does serial per-file FAISS loads — see "Next Steps" for parallelization.
- File ownership is re-checked on every conversation create/update via `_validate_file_ownership`.
