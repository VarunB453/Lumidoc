/**
 * App-wide constants. Keep this file dependency-free so it can be imported
 * from anywhere (including bootstrapping code).
 */

export const APP_NAME = 'Lumidoc'

/** localStorage keys. */
export const STORAGE_KEYS = {
  accessToken: 'lumidoc.access_token',
  refreshToken: 'lumidoc.refresh_token',
  store: 'lumidoc-store',
} as const

/** Limits that mirror server-side validation. */
export const LIMITS = {
  avatarMaxBytes: 5 * 1024 * 1024,
  passwordMinLength: 8,
} as const

/** Polling cadence for background-task statuses (summaries, timestamps). */
export const POLL_INTERVAL_MS = 2500
