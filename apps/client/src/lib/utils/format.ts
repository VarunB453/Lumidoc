/**
 * Display-formatting helpers shared across the UI.
 */
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Combine class names with Tailwind-aware merging so later classes win.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Render a byte count as a human-friendly string (e.g. "1.2 MB"). */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

/** Render seconds as `m:ss` for use in audio/video timestamp pills. */
export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
