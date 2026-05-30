/**
 * A dismissible banner that appears when the user goes offline.
 * Includes a "Retry" button that pings the health endpoint.
 */
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { WifiOff, RefreshCw, X } from 'lucide-react'
import { useOnlineStatus } from '@/hooks/useOnlineStatus'

export default function OfflineBanner() {
  const { isOnline, checkNow } = useOnlineStatus()
  const [dismissed, setDismissed] = useState(false)
  const [checking, setChecking] = useState(false)

  const handleRetry = async () => {
    setChecking(true)
    const online = await checkNow()
    setChecking(false)
    if (online) setDismissed(false) // will hide naturally since isOnline = true
  }

  const visible = !isOnline && !dismissed

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ y: -60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -60, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="fixed top-0 inset-x-0 z-50 flex items-center justify-center gap-3 px-4 py-3 bg-amber-500 text-white text-sm font-medium shadow-lg"
          role="alert"
          aria-live="assertive"
        >
          <WifiOff className="w-4 h-4 flex-shrink-0" />
          <span>You appear to be offline. Some features may be unavailable.</span>
          <button
            onClick={handleRetry}
            disabled={checking}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/20 hover:bg-white/30 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${checking ? 'animate-spin' : ''}`} />
            {checking ? 'Checking...' : 'Retry'}
          </button>
          <button
            onClick={() => setDismissed(true)}
            className="ml-2 p-1 rounded hover:bg-white/20 transition-colors"
            aria-label="Dismiss offline notification"
          >
            <X className="w-4 h-4" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
