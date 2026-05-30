/**
 * Hook that tracks browser online/offline status and provides retry helpers.
 */
import { useState, useEffect, useCallback, useRef } from 'react'

export interface OnlineStatus {
  /** Whether the browser reports being online. */
  isOnline: boolean
  /** Timestamp of the last detected offline event (null if never offline). */
  offlineSince: number | null
  /** Manually trigger a connectivity check (pings the API health endpoint). */
  checkNow: () => Promise<boolean>
}

export function useOnlineStatus(): OnlineStatus {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [offlineSince, setOfflineSince] = useState<number | null>(
    navigator.onLine ? null : Date.now(),
  )
  const checkingRef = useRef(false)

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      setOfflineSince(null)
    }
    const handleOffline = () => {
      setIsOnline(false)
      setOfflineSince(Date.now())
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const checkNow = useCallback(async (): Promise<boolean> => {
    if (checkingRef.current) return isOnline
    checkingRef.current = true
    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 5000)
      const resp = await fetch('/api/v1/health', {
        method: 'HEAD',
        signal: controller.signal,
        cache: 'no-store',
      })
      clearTimeout(timeout)
      const online = resp.ok
      setIsOnline(online)
      if (online) setOfflineSince(null)
      return online
    } catch {
      setIsOnline(false)
      if (!offlineSince) setOfflineSince(Date.now())
      return false
    } finally {
      checkingRef.current = false
    }
  }, [isOnline, offlineSince])

  return { isOnline, offlineSince, checkNow }
}
