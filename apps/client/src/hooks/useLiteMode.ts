import { useSyncExternalStore } from 'react'

/**
 * Detects slow network connections and low-end devices.
 * Returns true when the user should get a lighter experience:
 * - Slow effective connection (2g, slow-2g)
 * - Save-Data header enabled
 * - Low device memory (<= 4GB)
 * - prefers-reduced-motion enabled
 */

type NetworkInfo = {
  effectiveType?: string
  saveData?: boolean
}

function getSnapshot(): boolean {
  if (typeof window === 'undefined') return false

  // Check Network Information API
  const conn = (navigator as any).connection as NetworkInfo | undefined
  if (conn) {
    if (conn.saveData) return true
    if (conn.effectiveType === '2g' || conn.effectiveType === 'slow-2g') return true
  }

  // Check device memory (Chrome/Edge)
  const memory = (navigator as any).deviceMemory as number | undefined
  if (memory && memory <= 4) return true

  // Check prefers-reduced-motion
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return true

  return false
}

function subscribe(callback: () => void): () => void {
  const conn = (navigator as any).connection
  if (conn) {
    conn.addEventListener('change', callback)
  }
  const mql = window.matchMedia?.('(prefers-reduced-motion: reduce)')
  mql?.addEventListener('change', callback)

  return () => {
    conn?.removeEventListener('change', callback)
    mql?.removeEventListener('change', callback)
  }
}

/**
 * Returns true when the app should run in "lite mode" for slow connections.
 * Components can use this to skip heavy animations, WebGL effects, etc.
 */
export function useLiteMode(): boolean {
  return useSyncExternalStore(subscribe, getSnapshot, () => false)
}
