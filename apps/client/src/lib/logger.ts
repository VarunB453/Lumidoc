/**
 * Tiny structured logger. Wraps `console` so we can later forward errors to a
 * remote sink (Sentry, Datadog) without changing call sites.
 */
type Level = 'debug' | 'info' | 'warn' | 'error'

const isDev = import.meta.env.DEV

function emit(level: Level, msg: string, meta?: Record<string, unknown>) {
  if (level === 'debug' && !isDev) return
  const fn =
    level === 'error'
      ? console.error
      : level === 'warn'
        ? console.warn
        : level === 'info'
          ? console.info
          : console.debug
  if (meta) fn(`[${level}]`, msg, meta)
  else fn(`[${level}]`, msg)
}

export const logger = {
  debug: (msg: string, meta?: Record<string, unknown>) => emit('debug', msg, meta),
  info: (msg: string, meta?: Record<string, unknown>) => emit('info', msg, meta),
  warn: (msg: string, meta?: Record<string, unknown>) => emit('warn', msg, meta),
  error: (msg: string, meta?: Record<string, unknown>) => emit('error', msg, meta),
}
