/**
 * Typed endpoint groups for the Lumidoc backend.
 */
import { api, API_ORIGIN, tokenStore, API_BASE_URL } from './client'
import { buildAssetUrl } from './interceptors'
import type {
  AuthResponse,
  Conversation,
  FileMetadata,
  FileUploadResponse,
  Message,
  SourceChunk,
  SummaryResponse,
  TimestampEntry,
  TimestampRef,
  User,
} from '@/types'

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------
export const authApi = {
  async register(name: string, email: string, password: string): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/register', { name, email, password })
    return data
  },
  async login(email: string, password: string): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/login', { email, password })
    return data
  },
  async logout(refresh_token: string): Promise<void> {
    await api.post('/auth/logout', { refresh_token })
  },
  googleLoginUrl(): string {
    // Google OAuth must start on the backend origin so Authlib's state/session
    // cookie is available when Google redirects to the backend callback.
    const origin = API_ORIGIN || window.location.origin
    return `${origin}/api/v1/auth/google`
  },
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------
export const userApi = {
  async me(): Promise<User> {
    const { data } = await api.get<User>('/users/me')
    return data
  },
  async updateProfile(payload: { name?: string; email?: string }): Promise<User> {
    const { data } = await api.patch<User>('/users/me', payload)
    return data
  },
  async changePassword(current_password: string, new_password: string): Promise<void> {
    await api.post('/users/me/password', { current_password, new_password })
  },
  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await api.post<{ avatar_url: string }>('/users/me/avatar', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
}

// ---------------------------------------------------------------------------
// Files
// ---------------------------------------------------------------------------
export const filesApi = {
  async list(): Promise<FileMetadata[]> {
    const { data } = await api.get<{ items: FileMetadata[] }>('/files', {
      params: { page: 1, page_size: 100 },
    })
    return data.items || []
  },
  async get(id: string): Promise<FileMetadata> {
    const { data } = await api.get<FileMetadata>(`/files/${id}`)
    return data
  },
  async upload(
    file: File,
    onProgress?: (percent: number) => void,
    abortSignal?: AbortSignal,
  ): Promise<FileUploadResponse> {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await api.post<FileUploadResponse>('/files/upload', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      // Disable axios timeout for uploads (large files can take minutes).
      timeout: 0,
      signal: abortSignal,
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          onProgress(Math.round((event.loaded / event.total) * 100))
        }
      },
    })
    return data
  },
  async remove(id: string): Promise<void> {
    await api.delete(`/files/${id}`)
  },
  async downloadUrl(id: string): Promise<string> {
    const { data } = await api.get<{ url: string }>(`/files/${id}/download`)
    return buildAssetUrl(data.url)
  },
}

// ---------------------------------------------------------------------------
// Chat — including SSE streaming
// ---------------------------------------------------------------------------
export interface StreamHandlers {
  onUserMessage?: (userMessageId: string) => void
  onSources?: (chunks: SourceChunk[]) => void
  onToken?: (text: string) => void
  onDone?: (payload: {
    message_id: string
    timestamp_refs: TimestampRef[]
    content: string
  }) => void
  onError?: (message: string) => void
  /** Called when the EventSource closes for any reason (success or failure). */
  onClose?: () => void
}

export interface StreamHandle {
  /** Closes the underlying EventSource immediately. */
  close: () => void
}

export const chatApi = {
  async listConversations(favorites = false): Promise<Conversation[]> {
    const { data } = await api.get<Conversation[]>('/chat/conversations', {
      params: { favorites },
    })
    return data
  },
  async getConversation(id: string): Promise<Conversation> {
    const { data } = await api.get<Conversation>(`/chat/conversations/${id}`)
    return data
  },
  async createConversation(payload: { title?: string; file_ids?: string[] }): Promise<Conversation> {
    const { data } = await api.post<Conversation>('/chat/conversations', {
      title: payload.title,
      file_ids: payload.file_ids || [],
    })
    return data
  },
  async updateConversation(
    id: string,
    payload: { title?: string; is_favorite?: boolean; file_ids?: string[] },
  ): Promise<Conversation> {
    const { data } = await api.patch<Conversation>(`/chat/conversations/${id}`, payload)
    return data
  },
  async deleteConversation(id: string): Promise<void> {
    await api.delete(`/chat/conversations/${id}`)
  },
  async listMessages(convId: string): Promise<Message[]> {
    const { data } = await api.get<Message[]>(`/chat/conversations/${convId}/messages`)
    return data
  },
  /** Non-streaming send. Used as a fallback when SSE is unavailable. */
  async sendMessage(convId: string, content: string): Promise<Message> {
    const { data } = await api.post<Message>(`/chat/conversations/${convId}/messages`, {
      content,
      stream: false,
    })
    return data
  },
  /**
   * Open an SSE stream for an AI response. Returns a handle that lets the
   * caller close the stream early. Tokens are passed via query string because
   * the EventSource API does not allow custom headers.
   *
   * The backend emits four events:
   *   - `user_message` { user_message_id }
   *   - `sources`      { chunks: SourceChunk[] }
   *   - `token`        { text: string } (many)
   *   - `done`         { message_id, timestamp_refs, content }
   *   - `error`        { message }
   *
   * Before opening the EventSource we proactively refresh the access token
   * when it looks stale (i.e. the JWT exp is within 60 s of now). This avoids
   * the 401 that would otherwise occur because EventSource cannot send an
   * Authorization header and the backend validates the token from the query
   * string.
   */
  streamMessage(convId: string, q: string, handlers: StreamHandlers): StreamHandle {
    let closed = false
    let es: EventSource | null = null

    const close = () => {
      if (closed) return
      closed = true
      es?.close()
      handlers.onClose?.()
    }

    const safeParse = (raw: string): any => {
      try {
        return JSON.parse(raw)
      } catch {
        return {}
      }
    }

    const openStream = (token: string) => {
      if (closed) return
      const params = new URLSearchParams({ q, token })
      const url = `${API_BASE_URL}/chat/conversations/${convId}/messages/stream?${params.toString()}`
      es = new EventSource(url)

      es.addEventListener('user_message', (e: MessageEvent) => {
        const data = safeParse(e.data)
        handlers.onUserMessage?.(data.user_message_id)
      })
      es.addEventListener('sources', (e: MessageEvent) => {
        const data = safeParse(e.data)
        handlers.onSources?.(data.chunks || [])
      })
      es.addEventListener('token', (e: MessageEvent) => {
        const data = safeParse(e.data)
        if (typeof data.text === 'string') handlers.onToken?.(data.text)
      })
      es.addEventListener('done', (e: MessageEvent) => {
        const data = safeParse(e.data)
        handlers.onDone?.({
          message_id: data.message_id,
          timestamp_refs: data.timestamp_refs || [],
          content: data.content || '',
        })
        close()
      })
      es.addEventListener('error', (e: MessageEvent) => {
        // Two flavors: a typed `error` server event, or a transport error.
        // For server-emitted error events the `data` is populated.
        const data = e?.data ? safeParse(e.data) : null
        if (data?.message) {
          handlers.onError?.(data.message)
        } else if (es!.readyState === EventSource.CLOSED) {
          handlers.onError?.('Stream closed unexpectedly.')
        } else {
          handlers.onError?.('Connection lost.')
        }
        close()
      })
    }

    // Proactively refresh the access token if it is expired or about to expire
    // (within 60 s). EventSource cannot send Authorization headers so the token
    // travels as a query param — a stale token causes an immediate 401.
    const getValidToken = async (): Promise<string> => {
      const raw = tokenStore.getAccess()
      if (raw) {
        try {
          // JWT payload is the second base64url segment.
          const payload = JSON.parse(
            atob(raw.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))
          )
          const expiresAt = (payload.exp as number) * 1000
          if (expiresAt - Date.now() > 60_000) return raw
        } catch {
          // Malformed token — fall through to refresh.
        }
      }
      // Token is missing, expired, or expiring soon — refresh using the shared
      // axios instance (interceptors already handle token storage).
      const refreshToken = tokenStore.getRefresh()
      if (!refreshToken) return raw || ''
      try {
        const { data } = await api.post<{
          access_token: string
          refresh_token: string
          token_type: string
          expires_in: number
        }>('/auth/refresh', { refresh_token: refreshToken })
        tokenStore.set(data)
        return data.access_token
      } catch {
        // Refresh failed — tokens are cleared by the response interceptor,
        // which will also redirect to /login.
        return ''
      }
    }

    getValidToken().then(openStream)

    return { close }
  },
}

// ---------------------------------------------------------------------------
// Summaries / timestamps
// ---------------------------------------------------------------------------
export const summariesApi = {
  async trigger(fileId: string) {
    const { data } = await api.post<{ status: string; task_id?: string | null }>(
      `/summaries/${fileId}`,
    )
    return data
  },
  async get(fileId: string): Promise<SummaryResponse> {
    const { data } = await api.get<SummaryResponse>(`/summaries/${fileId}`)
    return data
  },
}

export const timestampsApi = {
  async list(fileId: string): Promise<TimestampEntry[]> {
    const { data } = await api.get<{ entries: TimestampEntry[] }>(`/timestamps/${fileId}`)
    return data.entries || []
  },
  async trigger(fileId: string) {
    const { data } = await api.post<{ status: string; task_id?: string | null }>(
      `/timestamps/${fileId}`,
    )
    return data
  },
  async search(fileId: string, topic: string): Promise<TimestampEntry[]> {
    const { data } = await api.get<{ entries: TimestampEntry[] }>(
      `/timestamps/${fileId}/${encodeURIComponent(topic)}`,
    )
    return data.entries || []
  },
}

// ---------------------------------------------------------------------------
// Misc (translate, voice transcription)
// ---------------------------------------------------------------------------
export const miscApi = {
  async translate(text: string, target_language: string, source_language?: string) {
    const { data } = await api.post<{ translated_text: string; target_language: string }>(
      '/translate',
      { text, target_language, source_language },
    )
    return data
  },
  async transcribeVoice(blob: Blob, filename = 'voice.webm', language?: string) {
    const fd = new FormData()
    fd.append('file', blob, filename)
    if (language) fd.append('language', language)
    const { data } = await api.post<{ text: string; duration_seconds?: number }>(
      '/voice/transcribe',
      fd,
      { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 0 },
    )
    return data
  },
}
