/**
 * Base axios client + token store for the Lumidoc backend.
 *
 * All paths are relative to `VITE_API_BASE_URL`. The default value is `/api/v1`
 * which the Vite dev server proxies to the FastAPI app on port 8000. In Docker
 * the frontend container's nginx proxies `/api` → `api:8000`.
 */
import axios, { type AxiosInstance } from 'axios'
import type { TokenPair } from '@/types'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
export const API_ORIGIN =
  import.meta.env.VITE_API_ORIGIN ||
  (API_BASE_URL.startsWith('http') ? new URL(API_BASE_URL).origin : '')

export const REQUEST_TIMEOUT_MS = Number(
  import.meta.env.VITE_API_TIMEOUT_MS || 60_000,
)

const ACCESS_TOKEN_KEY = 'lumidoc.access_token'
const REFRESH_TOKEN_KEY = 'lumidoc.refresh_token'

// ---------------------------------------------------------------------------
// Token store (localStorage). Subscribers are notified when tokens change so
// that auth-dependent UI can re-render after the OAuth fragment-redirect flow.
// ---------------------------------------------------------------------------
type TokenSubscriber = (tokens: TokenPair | null) => void
const tokenSubscribers = new Set<TokenSubscriber>()

/**
 * Decode the `exp` claim of a JWT without verifying the signature. Returns
 * null if the token is missing or malformed. Used by client-side helpers to
 * decide whether to proactively refresh before issuing a request that would
 * otherwise produce a noisy 401.
 */
export function getJwtExpMs(token: string | null): number | null {
  if (!token) return null
  try {
    const payload = JSON.parse(
      atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')),
    )
    return typeof payload.exp === 'number' ? payload.exp * 1000 : null
  } catch {
    return null
  }
}

export const tokenStore = {
  getAccess(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY)
  },
  getRefresh(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },
  /** True when the access token is missing, malformed, or within `skewMs` of expiring. */
  isAccessExpired(skewMs = 60_000): boolean {
    const exp = getJwtExpMs(localStorage.getItem(ACCESS_TOKEN_KEY))
    if (exp == null) return true
    return exp - Date.now() <= skewMs
  },
  set(tokens: TokenPair) {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token)
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token)
    tokenSubscribers.forEach((cb) => cb(tokens))
  },
  clear() {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    tokenSubscribers.forEach((cb) => cb(null))
  },
  subscribe(cb: TokenSubscriber): () => void {
    tokenSubscribers.add(cb)
    return () => tokenSubscribers.delete(cb)
  },
}

// ---------------------------------------------------------------------------
// Axios instance. Interceptors are registered in `./interceptors`.
// ---------------------------------------------------------------------------
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT_MS,
  headers: { 'Content-Type': 'application/json' },
})

export default api
