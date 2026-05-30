/**
 * Wire-level types — the shapes the FastAPI backend returns.
 *
 * In a follow-up these can be regenerated from the OpenAPI schema. For now
 * they are hand-maintained to match the Pydantic schemas in `server/app`.
 */

export interface User {
  id: string
  email: string
  name: string
  avatar_url?: string | null
  role?: string
  is_active?: boolean
  created_at?: string
  updated_at?: string | null
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface AuthResponse {
  user: User
  tokens: TokenPair
}

// ---------- Files ----------
export type FileType = 'pdf' | 'audio' | 'video'
export type FileStatus = 'pending' | 'processing' | 'ready' | 'failed'

export interface FileMetadata {
  id: string
  user_id: string
  filename: string
  original_name: string
  file_type: FileType
  s3_key: string
  size_bytes: number
  status: FileStatus
  error_message?: string | null
  mime_type?: string | null
  duration_seconds?: number | null
  page_count?: number | null
  created_at: string
  processed_at?: string | null
  is_deleted?: boolean
}

export interface FileUploadResponse
  extends Pick<FileMetadata, 'file_type' | 'filename' | 'original_name' | 'size_bytes' | 'status'> {
  file_id: string
  task_id?: string | null
}

// ---------- Chat ----------
export type MessageRole = 'user' | 'assistant' | 'system'

export interface SourceChunk {
  file_id: string
  chunk_id: string
  text: string
  score: number
  start_time?: number | null
  end_time?: number | null
  page?: number | null
}

export interface TimestampRef {
  file_id: string
  start_time: number
  end_time: number
  topic?: string | null
}

export interface Conversation {
  id: string
  user_id: string
  title: string
  file_ids: string[]
  message_count: number
  is_favorite: boolean
  created_at: string
  updated_at: string
}

// ---------- Summaries / timestamps ----------
export interface SummaryResponse {
  id: string
  file_id: string
  user_id: string
  content: string
  status: 'pending' | 'processing' | 'ready' | 'failed'
  model_used: string
  generated_at: string
}

export interface TimestampEntry {
  id?: string
  file_id: string
  user_id?: string
  topic: string
  start_time: number
  end_time: number
  summary: string
  created_at?: string
}
