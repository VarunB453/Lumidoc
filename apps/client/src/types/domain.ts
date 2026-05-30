/**
 * Domain types — client-side derived/UI shapes that extend the wire types in
 * `./api`. These do not exist on the backend.
 */
import type {
  FileType,
  MessageRole,
  SourceChunk,
  TimestampRef,
} from './api'

export interface Message {
  id: string
  conversation_id: string
  user_id: string
  role: MessageRole
  content: string
  source_chunks: SourceChunk[]
  timestamp_refs: TimestampRef[]
  created_at: string
  // Local-only flag to render attachments / voice notes that the user added
  // before the AI replied.
  attachments?: ChatAttachment[]
  voice_url?: string
  voice_duration?: number
  // Local marker so we can render a streaming spinner.
  pending?: boolean
}

export interface ChatAttachment {
  id: string
  name: string
  type: FileType | 'image'
  url?: string
  thumbnail?: string
  size: number
}

export type UploadStatus = 'uploading' | 'processing' | 'ready' | 'error'

export interface UploadedFile {
  id: string
  name: string
  type: FileType
  size: number
  status: UploadStatus
  progress: number
  file?: File
  backendFileId?: string
  error?: string
}

export interface UserPreferences {
  theme: 'light' | 'dark'
  language: string
  notifications: {
    email: boolean
    push: boolean
    sound: boolean
  }
}
