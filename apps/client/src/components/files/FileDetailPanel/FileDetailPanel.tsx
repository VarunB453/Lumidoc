import { useEffect, useMemo, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import {
  X,
  Sparkles,
  Clock,
  Loader2,
  RefreshCcw,
  Play,
  MessageSquare,
} from 'lucide-react'
import {
  buildAssetUrl,
  extractError,
  filesApi,
  summariesApi,
  timestampsApi,
} from '@/lib/api'
import type { FileMetadata, SummaryResponse, TimestampEntry } from '@/types'
import { cn, formatDuration, formatFileSize } from '@/lib/utils'
import Button from '@/components/ui/Button'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import { useStore } from '@/store'

interface Props {
  file: FileMetadata
  onClose: () => void
}

const POLL_INTERVAL_MS = 2500

/**
 * Right-rail detail panel: lazy-loads the summary + timestamp segments for a
 * file. Polls until the backend returns ready data, then stops.
 */
export default function FileDetailPanel({ file, onClose }: Props) {
  const navigate = useNavigate()
  const { createConversation } = useStore()
  const [summary, setSummary] = useState<SummaryResponse | null>(null)
  const [summaryLoading, setSummaryLoading] = useState(true)
  const [summaryError, setSummaryError] = useState<string | null>(null)

  const [timestamps, setTimestamps] = useState<TimestampEntry[]>([])
  const [tsLoading, setTsLoading] = useState(true)
  const [tsError, setTsError] = useState<string | null>(null)

  const [mediaUrl, setMediaUrl] = useState('')
  const playerRef = useRef<HTMLAudioElement | HTMLVideoElement | null>(null)

  const supportsTimestamps = useMemo(
    () => file.file_type === 'audio' || file.file_type === 'video',
    [file.file_type],
  )

  // ---------- summary ----------
  useEffect(() => {
    let cancelled = false
    let stopPolling = false
    let timer: ReturnType<typeof setTimeout> | null = null

    const tick = async () => {
      try {
        const res = await summariesApi.get(file.id)
        if (cancelled) return
        setSummary(res)
        setSummaryError(null)
        if (res.status === 'ready' || res.status === 'failed') {
          stopPolling = true
          setSummaryLoading(false)
          return
        }
      } catch (err: any) {
        // 404 means summary doesn't exist yet — trigger generation once.
        if (err?.response?.status === 404 && !stopPolling) {
          try {
            await summariesApi.trigger(file.id)
          } catch (triggerErr) {
            if (!cancelled) {
              setSummaryError(extractError(triggerErr))
              setSummaryLoading(false)
              stopPolling = true
              return
            }
          }
        } else if (!cancelled) {
          setSummaryError(extractError(err))
          setSummaryLoading(false)
          return
        }
      }
      if (!cancelled && !stopPolling) {
        timer = setTimeout(tick, POLL_INTERVAL_MS)
      }
    }

    setSummaryLoading(true)
    setSummary(null)
    setSummaryError(null)
    tick()

    return () => {
      cancelled = true
      stopPolling = true
      if (timer) clearTimeout(timer)
    }
  }, [file.id])

  // ---------- timestamps ----------
  useEffect(() => {
    if (!supportsTimestamps) {
      setTsLoading(false)
      setTimestamps([])
      return
    }
    let cancelled = false
    let stopPolling = false
    let timer: ReturnType<typeof setTimeout> | null = null
    let triggered = false

    const tick = async () => {
      try {
        const list = await timestampsApi.list(file.id)
        if (cancelled) return
        if (list.length > 0) {
          setTimestamps(list)
          setTsLoading(false)
          stopPolling = true
          return
        }
        // Empty list — kick off generation once, then keep polling.
        if (!triggered) {
          triggered = true
          await timestampsApi.trigger(file.id).catch((err) => {
            if (!cancelled) {
              setTsError(extractError(err))
              setTsLoading(false)
              stopPolling = true
            }
          })
        }
      } catch (err) {
        if (!cancelled) {
          setTsError(extractError(err))
          setTsLoading(false)
          stopPolling = true
          return
        }
      }
      if (!cancelled && !stopPolling) {
        timer = setTimeout(tick, POLL_INTERVAL_MS)
      }
    }

    setTsLoading(true)
    setTimestamps([])
    setTsError(null)
    tick()

    return () => {
      cancelled = true
      stopPolling = true
      if (timer) clearTimeout(timer)
    }
  }, [file.id, supportsTimestamps])

  // ---------- media url ----------
  useEffect(() => {
    if (!supportsTimestamps) {
      setMediaUrl('')
      return
    }
    let cancelled = false
    filesApi
      .downloadUrl(file.id)
      .then((url) => {
        if (!cancelled) setMediaUrl(buildAssetUrl(url))
      })
      .catch(() => {
        if (!cancelled) setMediaUrl('')
      })
    return () => {
      cancelled = true
    }
  }, [file.id, supportsTimestamps])

  // ---------- handlers ----------
  const seekTo = (seconds: number) => {
    if (playerRef.current) {
      playerRef.current.currentTime = seconds
      playerRef.current.play().catch(() => {})
    }
  }

  const handleStartChat = async () => {
    try {
      const conv = await createConversation({
        title: file.original_name,
        file_ids: [file.id],
      })
      navigate(`/chat/${conv.id}`)
    } catch (err) {
      toast.error(extractError(err))
    }
  }

  const handleRegenerateSummary = async () => {
    setSummaryLoading(true)
    setSummary(null)
    try {
      await summariesApi.trigger(file.id)
      toast.success('Summary regeneration started')
    } catch (err) {
      toast.error(extractError(err))
      setSummaryLoading(false)
    }
  }

  return (
    <motion.aside
      initial={{ x: 360, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 360, opacity: 0 }}
      transition={{ type: 'spring', stiffness: 220, damping: 26 }}
      className={cn(
        'fixed top-0 right-0 z-30 h-full w-full sm:w-[420px]',
        'surface shadow-soft-lg border-l border-primary-100 dark:border-primary-900',
        'flex flex-col',
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-primary-50 dark:border-primary-900">
        <div className="min-w-0">
          <h3 className="font-semibold text-text-primary truncate">
            {file.original_name}
          </h3>
          <p className="text-xs text-text-muted">
            {formatFileSize(file.size_bytes)} • {file.file_type.toUpperCase()}
          </p>
        </div>
        <button
          onClick={onClose}
          className="w-9 h-9 rounded-lg flex items-center justify-center text-text-muted hover:bg-red-50 hover:text-red-500 transition-colors focus-ring"
          aria-label="Close panel"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {/* Media preview */}
        {supportsTimestamps && mediaUrl && (
          <div className="p-4">
            {file.file_type === 'video' ? (
              <video
                ref={playerRef as React.RefObject<HTMLVideoElement>}
                src={mediaUrl}
                controls
                className="w-full rounded-xl bg-black"
              />
            ) : (
              <audio
                ref={playerRef as React.RefObject<HTMLAudioElement>}
                src={mediaUrl}
                controls
                className="w-full"
              />
            )}
          </div>
        )}

        {/* Summary */}
        <section className="p-4 border-t border-primary-50 dark:border-primary-900">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-text-primary flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" /> Summary
            </h4>
            <button
              onClick={handleRegenerateSummary}
              disabled={summaryLoading}
              className="inline-flex items-center gap-1 text-xs text-text-muted hover:text-primary disabled:opacity-50 focus-ring rounded px-2 py-1"
            >
              <RefreshCcw className="w-3.5 h-3.5" /> Regenerate
            </button>
          </div>
          {summaryLoading && !summary && (
            <div className="flex items-center gap-2 text-sm text-text-muted">
              <Loader2 className="w-4 h-4 animate-spin" /> Generating summary…
            </div>
          )}
          {summaryError && (
            <p className="text-sm text-red-500">{summaryError}</p>
          )}
          {summary && (
            <p className="text-sm leading-relaxed whitespace-pre-wrap text-text-primary">
              {summary.content}
            </p>
          )}
        </section>

        {/* Timestamps */}
        {supportsTimestamps && (
          <section className="p-4 border-t border-primary-50 dark:border-primary-900">
            <h4 className="font-medium text-text-primary flex items-center gap-2 mb-3">
              <Clock className="w-4 h-4 text-primary" /> Topic Timestamps
            </h4>
            {tsLoading && timestamps.length === 0 && (
              <div className="flex items-center gap-2 text-sm text-text-muted">
                <Loader2 className="w-4 h-4 animate-spin" /> Extracting topics…
              </div>
            )}
            {tsError && <p className="text-sm text-red-500">{tsError}</p>}
            {timestamps.length > 0 && (
              <ul className="space-y-2">
                {timestamps.map((t, i) => (
                  <li
                    key={t.id || i}
                    className="p-3 rounded-xl bg-primary-50/60 dark:bg-primary-900/30"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="font-medium text-sm text-text-primary truncate">
                          {t.topic}
                        </p>
                        {t.summary && (
                          <p className="text-xs text-text-muted mt-1 line-clamp-2">
                            {t.summary}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => seekTo(t.start_time)}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-primary text-white text-xs font-medium hover:bg-primary-600 transition-colors focus-ring"
                      >
                        <Play className="w-3 h-3" /> {formatDuration(t.start_time)}
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-primary-50 dark:border-primary-900 surface-soft">
        <Button onClick={handleStartChat} className="w-full">
          <MessageSquare className="w-4 h-4 mr-2" />
          Chat with this file
        </Button>
      </div>
    </motion.aside>
  )
}
