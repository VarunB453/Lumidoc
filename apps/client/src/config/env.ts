/**
 * Validated, typed access to Vite environment variables.
 *
 * Centralising this keeps the rest of the app from having to deal with
 * `import.meta.env` directly and lets us coerce/default values in one place.
 */

function readEnv(key: string, fallback?: string): string | undefined {
  const value = (import.meta.env as Record<string, string | undefined>)[key]
  if (value === undefined || value === '') return fallback
  return value
}

function readNumber(key: string, fallback: number): number {
  const raw = readEnv(key)
  if (!raw) return fallback
  const parsed = Number(raw)
  return Number.isFinite(parsed) ? parsed : fallback
}

export const env = {
  /** Base URL the axios client uses; relative paths go through the Vite proxy. */
  apiBaseUrl: readEnv('VITE_API_BASE_URL', '/api/v1') as string,
  /** Origin used to build absolute URLs (Google OAuth, EventSource). */
  apiOrigin: readEnv('VITE_API_ORIGIN', '') as string,
  /** Default request timeout for non-streaming, non-upload calls. */
  apiTimeoutMs: readNumber('VITE_API_TIMEOUT_MS', 60_000),
  /** Vite-provided mode helpers. */
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
  mode: import.meta.env.MODE,
} as const

export type Env = typeof env
