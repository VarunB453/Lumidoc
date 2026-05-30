import { motion } from 'framer-motion'
import { User, Play, FileText, Music, Video, Copy, ThumbsUp, ThumbsDown } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { cn, formatFileSize } from '@/lib/utils'
import type { Message, TimestampRef } from '@/types'
import { format } from 'date-fns'

/* ─── Animated AI Orb Icon (3D morphing blue shapes) ─── */
function AnimatedAIOrb() {
  return (
    <div className="w-9 h-9 relative flex items-center justify-center">
      <svg
        viewBox="0 0 40 40"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <radialGradient id="orb-grad-1" cx="35%" cy="35%" r="65%">
            <stop offset="0%" stopColor="#7CB9FF" />
            <stop offset="50%" stopColor="#4B7BF5" />
            <stop offset="100%" stopColor="#1E3A8A" />
          </radialGradient>
          <radialGradient id="orb-grad-2" cx="60%" cy="30%" r="60%">
            <stop offset="0%" stopColor="#93C5FD" />
            <stop offset="60%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#1D4ED8" />
          </radialGradient>
          <radialGradient id="orb-grad-3" cx="40%" cy="60%" r="55%">
            <stop offset="0%" stopColor="#60A5FA" />
            <stop offset="70%" stopColor="#2563EB" />
            <stop offset="100%" stopColor="#1E40AF" />
          </radialGradient>
          <filter id="orb-glow">
            <feGaussianBlur stdDeviation="1" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Main orb body */}
        <ellipse cx="20" cy="20" rx="9" ry="9" fill="url(#orb-grad-1)" filter="url(#orb-glow)">
          <animate
            attributeName="rx"
            values="9;10;8;9"
            dur="4s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="ry"
            values="9;8;10;9"
            dur="4s"
            repeatCount="indefinite"
          />
        </ellipse>

        {/* Orbiting petal 1 */}
        <ellipse cx="20" cy="20" rx="12" ry="5" fill="url(#orb-grad-2)" opacity="0.7">
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="0 20 20"
            to="360 20 20"
            dur="6s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="ry"
            values="5;3;5"
            dur="3s"
            repeatCount="indefinite"
          />
        </ellipse>

        {/* Orbiting petal 2 */}
        <ellipse cx="20" cy="20" rx="11" ry="4" fill="url(#orb-grad-3)" opacity="0.5">
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="120 20 20"
            to="480 20 20"
            dur="8s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="rx"
            values="11;8;11"
            dur="4s"
            repeatCount="indefinite"
          />
        </ellipse>

        {/* Small satellite orb */}
        <circle cx="30" cy="14" r="3" fill="url(#orb-grad-2)" opacity="0.8">
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="0 20 20"
            to="360 20 20"
            dur="5s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="r"
            values="3;2;3"
            dur="2.5s"
            repeatCount="indefinite"
          />
        </circle>

        {/* Highlight reflection */}
        <ellipse cx="17" cy="16" rx="3" ry="2" fill="white" opacity="0.25">
          <animate
            attributeName="opacity"
            values="0.25;0.4;0.25"
            dur="3s"
            repeatCount="indefinite"
          />
        </ellipse>
      </svg>
    </div>
  )
}

interface ChatMessageProps {
  message: Message
  index: number
  onTimestampClick?: (ref: TimestampRef) => void
}

export default function ChatMessage({ message, index, onTimestampClick }: ChatMessageProps) {
  const isUser = message.role === 'user'

  const renderContent = (content: string) => {
    return (
      <ReactMarkdown
        components={{
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          strong: ({ children }) => (
            <strong className="font-semibold text-text-primary">{children}</strong>
          ),
          em: ({ children }) => <em className="italic text-text-muted">{children}</em>,
          ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="text-text-muted">{children}</li>,
          code: ({ children, className }) => {
            const isBlock = className?.includes('language-')
            if (isBlock) {
              return (
                <pre className="msg-code p-3 my-2 overflow-x-auto">
                  <code className="text-xs font-mono text-text-primary">{children}</code>
                </pre>
              )
            }
            return (
              <code className="px-1.5 py-0.5 rounded text-xs font-mono" style={{ background: 'rgba(255,255,255,0.05)', color: '#F0845A' }}>
                {children}
              </code>
            )
          },
          h1: ({ children }) => (
            <h1 className="text-lg font-bold mb-2 text-text-primary font-serif">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-base font-bold mb-2 text-text-primary font-serif">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-sm font-bold mb-1 text-text-primary font-serif">{children}</h3>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-primary/40 pl-3 my-2 text-text-muted italic">
              {children}
            </blockquote>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline decoration-primary/30 hover:decoration-primary transition-colors"
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    )
  }

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return FileText
      case 'audio':
        return Music
      case 'video':
        return Video
      default:
        return FileText
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.04, ease: [0.25, 0.46, 0.45, 0.94] }}
      className="group relative"
    >
      <div className={cn('flex gap-3 mb-5', isUser ? 'flex-row-reverse' : 'flex-row')}>
        {/* Avatar */}
        {isUser ? (
          <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0"
            style={{
              background: 'linear-gradient(135deg, rgba(232, 98, 42, 0.15), rgba(232, 98, 42, 0.05))',
              border: '1px solid rgba(232, 98, 42, 0.2)',
            }}
          >
            <User className="w-4 h-4" style={{ color: '#E8622A' }} />
          </div>
        ) : (
          <div className="flex-shrink-0">
            <AnimatedAIOrb />
          </div>
        )}

        {/* Message Content */}
        <div className={cn('max-w-[80%]', isUser ? 'items-end' : 'items-start')}>
          <div
            className={cn(
              'rounded-2xl px-4 py-3',
              isUser
                ? 'msg-user text-text-primary'
                : 'msg-ai text-text-primary',
            )}
          >
            {message.pending ? (
              <div className="flex items-center gap-2 py-1">
                <motion.span
                  className="w-2 h-2 rounded-full"
                  style={{ background: '#4B7BF5' }}
                  animate={{ scale: [0.6, 1, 0.6], opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 1.4, repeat: Infinity, delay: 0 }}
                />
                <motion.span
                  className="w-2 h-2 rounded-full"
                  style={{ background: '#4B7BF5' }}
                  animate={{ scale: [0.6, 1, 0.6], opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 1.4, repeat: Infinity, delay: 0.2 }}
                />
                <motion.span
                  className="w-2 h-2 rounded-full"
                  style={{ background: '#4B7BF5' }}
                  animate={{ scale: [0.6, 1, 0.6], opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 1.4, repeat: Infinity, delay: 0.4 }}
                />
              </div>
            ) : (
              <div className="text-sm leading-relaxed font-body" style={{ color: '#FFFFFF' }}>{renderContent(message.content)}</div>
            )}

            {/* Attachments */}
            {message.attachments && message.attachments.length > 0 && (
              <div className="mt-3 space-y-2">
                {message.attachments.map((att) => {
                  const Icon = getFileIcon(att.type)
                  return (
                    <div
                      key={att.id}
                      className="flex items-center gap-3 p-3 rounded-xl border transition-colors hover:border-primary/20"
                      style={{
                        background: 'rgba(26, 35, 24, 0.6)',
                        borderColor: 'rgba(255, 255, 255, 0.06)',
                      }}
                    >
                      <div
                        className="w-10 h-10 rounded-lg flex items-center justify-center"
                        style={{ background: 'rgba(232, 98, 42, 0.1)' }}
                      >
                        <Icon className="w-5 h-5 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-text-primary truncate font-body">
                          {att.name}
                        </p>
                        <p className="text-xs text-text-muted font-mono">{formatFileSize(att.size)}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {/* Source chunks (citations) */}
            {!isUser && message.source_chunks && message.source_chunks.length > 0 && (
              <details className="mt-3 text-xs">
                <summary className="cursor-pointer text-text-muted hover:text-primary transition-colors font-body">
                  {message.source_chunks.length} source(s)
                </summary>
                <div className="mt-2 space-y-2">
                  {message.source_chunks.slice(0, 5).map((chunk, i) => (
                    <div
                      key={chunk.chunk_id || i}
                      className="p-2 rounded-lg border"
                      style={{
                        background: 'rgba(26, 35, 24, 0.4)',
                        borderColor: 'rgba(255, 255, 255, 0.05)',
                      }}
                    >
                      <p className="text-text-muted line-clamp-3 font-body">{chunk.text}</p>
                      {chunk.page != null && (
                        <span className="text-primary font-mono">Page {chunk.page}</span>
                      )}
                      {chunk.start_time != null && chunk.end_time != null && (
                        <span className="text-primary ml-2 font-mono">
                          {Math.floor(chunk.start_time / 60)}:
                          {String(Math.floor(chunk.start_time % 60)).padStart(2, '0')} –{' '}
                          {Math.floor(chunk.end_time / 60)}:
                          {String(Math.floor(chunk.end_time % 60)).padStart(2, '0')}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </details>
            )}

            {/* Timestamp refs */}
            {!isUser && message.timestamp_refs && message.timestamp_refs.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {message.timestamp_refs.map((ts, i) => (
                  <button
                    key={i}
                    onClick={() => onTimestampClick?.(ts)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all hover:scale-105 focus-ring font-mono"
                    style={{
                      background: 'rgba(232, 98, 42, 0.1)',
                      color: '#F0845A',
                      border: '1px solid rgba(232, 98, 42, 0.2)',
                    }}
                  >
                    <Play className="w-3 h-3" />
                    {Math.floor(ts.start_time / 60)}:
                    {String(Math.floor(ts.start_time % 60)).padStart(2, '0')}
                  </button>
                ))}
              </div>
            )}
          </div>

          <p className="text-xs mt-1.5 px-1 font-mono" style={{ color: '#5A5A4E' }}>
            {format(new Date(message.created_at), 'h:mm a')}
          </p>
        </div>
      </div>

      {/* Action buttons on hover (AI messages only) */}
      {!isUser && (
        <div className="absolute right-0 top-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center gap-1">
          <button
            className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors hover:bg-white/5"
            aria-label="Copy message"
            style={{ color: '#8A8A7A' }}
          >
            <Copy className="w-3.5 h-3.5" />
          </button>
          <button
            className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors hover:bg-white/5"
            aria-label="Thumbs up"
            style={{ color: '#8A8A7A' }}
          >
            <ThumbsUp className="w-3.5 h-3.5" />
          </button>
          <button
            className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors hover:bg-white/5"
            aria-label="Thumbs down"
            style={{ color: '#8A8A7A' }}
          >
            <ThumbsDown className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </motion.div>
  )
}
