/**
 * Request/response interceptors for the shared axios client.
 *
 * - Request: attaches the bearer access token if available.
 * - Response: on 401 (excluding /auth/* requests), tries to refresh once.
 *   On refresh failure, clears tokens and bounces to /login.
 */
import axios, { AxiosError } from 'axios'
import {
  API_BASE_URL,
  REQUEST_TIMEOUT_MS,
  api,
  tokenStore,
} from './client'
import type { TokenPair } from '@/types'

let refreshing: Promise<TokenPair | null> | null = null

/**
 * Refresh the access/refresh token pair using the stored refresh token.
 * Concurrent callers share the same in-flight promise so we never issue two
 * refresh requests at once. Exported for proactive use (e.g. on app boot)
 * before issuing requests that would otherwise produce a noisy 401.
 */
export async function refreshTokens(): Promise<TokenPair | null> {
  if (refreshing) return refreshing
  refreshing = (async () => {
    const refresh_token = tokenStore.getRefresh()
    if (!refresh_token) return null
    try {
      const { data } = await axios.post<TokenPair>(
        `${API_BASE_URL}/auth/refresh`,
        { refresh_token },
        { timeout: REQUEST_TIMEOUT_MS },
      )
      tokenStore.set(data)
      return data
    } catch {
      tokenStore.clear()
      return null
    }
  })().finally(() => {
    refreshing = null
  })
  return refreshing
}

api.interceptors.request.use((config) => {
  const token = tokenStore.getAccess()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original: any = error.config
    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !original.url?.includes('/auth/')
    ) {
      original._retry = true
      const tokens = await refreshTokens()
      if (tokens) {
        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${tokens.access_token}`
        return api(original)
      }
      tokenStore.clear()
      if (
        typeof window !== 'undefined' &&
        !window.location.pathname.startsWith('/login')
      ) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Build a fully-qualified URL safe to use in `<img>` / `<audio>` / `<video>` /
 * `EventSource`. Backed by the configured API origin in dev (with the Vite
 * proxy) and by relative paths in prod (single-origin nginx).
 */
export function buildAssetUrl(relativeOrAbsolute: string): string {
  if (!relativeOrAbsolute) return ''
  if (/^https?:\/\//.test(relativeOrAbsolute)) return relativeOrAbsolute
  if (relativeOrAbsolute.startsWith('/api/')) return relativeOrAbsolute
  if (relativeOrAbsolute.startsWith('/local-files/')) {
    const token = tokenStore.getAccess()
    return token
      ? `${relativeOrAbsolute}?token=${encodeURIComponent(token)}`
      : relativeOrAbsolute
  }
  return relativeOrAbsolute
}

export function extractError(error: unknown): string {
  const e = error as AxiosError<{ error?: { message?: string } }>
  if (e?.code === 'ECONNABORTED') {
    return 'Request timed out. Please try again.'
  }
  if (e?.message === 'Network Error') {
    return 'Cannot reach the server. Check your connection and try again.'
  }
  return (
    e?.response?.data?.error?.message ||
    e?.message ||
    'Something went wrong. Please try again.'
  )
}
