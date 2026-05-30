import { useState, useRef, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Send,
  Mic,
  Paperclip,
  Plus,
  FileText,
  Image as ImageIcon,
  Languages,
  Headphones,
  Square,
  Loader2,
  X,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useVoiceRecorder } from '@/hooks/useVoiceRecorder'
import { miscApi, extractError } from '@/lib/api'
import toast from 'react-hot-toast'

export type ChatPanel = 'files' | 'translate' | 'images' | 'audio' | null

const quickActions: Array<{
  icon: typeof FileText
  label: string
  color: string
  bg: string
  action: ChatPanel
}> = [
  { icon: FileText, label: 'Chat Files', color: 'text-red-400', bg: 'bg-red-900/30', action: 'files' },
  { icon: ImageIcon, label: 'Images', color: 'text-blue-400', bg: 'bg-blue-900/30', action: 'images' },
  { icon: Languages, label: 'Translate', color: 'text-green-400', bg: 'bg-green-900/30', action: 'translate' },
  { icon: Headphones, label: 'Audio Chat', color: 'text-orange-400', bg: 'bg-orange-900/30', action: 'audio' },
]

interface ChatInputProps {
  onSend: (message: string, attachmentIds?: string[]) => void
  isLoading?: boolean
  onOpenPanel?: (panel: ChatPanel) => void
  selectedFileIds?: string[]
  onClearAttachments?: () => void
  draft?: string
}

export default function ChatInput({
  onSend,
  isLoading,
  onOpenPanel,
  selectedFileIds = [],
  onClearAttachments,
  draft,
}: ChatInputProps) {
  const [message, setMessage] = useState(draft ?? '')
  const [showActions, setShowActions] = useState(false)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (draft) {
      setMessage(draft)
      setTimeout(() => {
        const el = inputRef.current
        if (!el) return
        el.style.height = 'auto'
        el.style.height = `${Math.min(el.scrollHeight, 200)}px`
        el.focus()
      }, 0)
    }
  }, [draft])

  const { isRecording, start: startRecording, stop: stopRecording } = useVoiceRecorder()
  const [transcribing, setTranscribing] = useState(false)

  const handleSubmit = useCallback(() => {
    if (!message.trim() || isLoading) return
    onSend(message.trim(), selectedFileIds.length ? selectedFileIds : undefined)
    setMessage('')
    setShowActions(false)
    if (inputRef.current) inputRef.current.style.height = 'auto'
  }, [message, isLoading, onSend, selectedFileIds])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`
  }

  const handleVoice = async () => {
    if (isRecording) {
      try {
        const { blob } = await stopRecording()
        setTranscribing(true)
        const res = await miscApi.transcribeVoice(blob)
        if (res.text) {
          setMessage((prev) => (prev ? `${prev} ${res.text}` : res.text))
        }
      } catch (err) {
        toast.error(extractError(err))
      } finally {
        setTranscribing(false)
      }
    } else {
      try {
        await startRecording()
      } catch {
        toast.error('Microphone access denied')
      }
    }
  }

  const handleAttachClick = () => {
    if (onOpenPanel) onOpenPanel('files')
    else toast('Use the Upload page to add files, then attach them here.', { icon: '📁' })
  }

  return (
    <div className="w-full">
      <AnimatePresence>
        {showActions && onOpenPanel && (
          <motion.div
            className="flex gap-2 mb-3 overflow-x-auto pb-1"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {quickActions.map((action) => (
              <motion.button
                key={action.label}
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                onClick={() => onOpenPanel(action.action)}
                className={cn(
                  'flex items-center gap-2 px-4 py-2.5 rounded-xl min-w-fit',
                  'transition-shadow duration-200 focus-ring',
                )}
                style={{
                  backgroundColor: '#0A0A0A',
                  border: '1px solid rgba(255,255,255,0.06)',
                }}
              >
                <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center', action.bg)}>
                  <action.icon className={cn('w-4 h-4', action.color)} />
                </div>
                <span className="text-sm font-medium whitespace-nowrap" style={{ color: '#F2F0E8' }}>
                  {action.label}
                </span>
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {selectedFileIds.length > 0 && (
        <div className="mb-2 flex items-center gap-2 text-xs">
          <span className="font-medium" style={{ color: '#E8622A' }}>
            {selectedFileIds.length} file{selectedFileIds.length === 1 ? '' : 's'} attached
          </span>
          {onClearAttachments && (
            <button
              onClick={onClearAttachments}
              className="inline-flex items-center gap-1 transition-colors"
              style={{ color: '#5A5A4E' }}
              aria-label="Clear attachments"
            >
              <X className="w-3 h-3" /> clear
            </button>
          )}
        </div>
      )}

      <div className="chat-input-wrapper p-2">
        <div className="flex items-end gap-2">
          {onOpenPanel && (
            <button
              onClick={() => setShowActions(!showActions)}
              className={cn(
                'w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 focus-ring',
                showActions
                  ? 'text-white'
                  : 'text-[#5A5A4E] hover:text-[#9A9A8A] hover:bg-white/[0.04]',
              )}
              style={{
                backgroundColor: showActions ? 'rgba(232, 98, 42, 0.25)' : 'transparent',
              }}
              aria-label="Toggle quick actions"
            >
              <Plus className="w-5 h-5" />
            </button>
          )}

          <textarea
            ref={inputRef}
            value={message}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything..."
            rows={1}
            className={cn(
              'flex-1 bg-transparent border-0 resize-none py-3 px-2',
              'text-sm focus:outline-none focus:ring-0',
              'max-h-[200px] min-h-[40px]',
            )}
            style={{ color: '#F2F0E8' }}
          />

          <div className="flex items-center gap-1">
            <button
              onClick={handleVoice}
              disabled={transcribing}
              className={cn(
                'w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 focus-ring',
                isRecording
                  ? 'bg-red-500 text-white recording-pulse'
                  : 'text-[#5A5A4E] hover:text-[#9A9A8A] hover:bg-white/[0.04]',
              )}
              aria-label={isRecording ? 'Stop recording' : 'Voice input'}
            >
              {transcribing ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : isRecording ? (
                <Square className="w-4 h-4" />
              ) : (
                <Mic className="w-5 h-5" />
              )}
            </button>

            <button
              onClick={handleAttachClick}
              className="w-10 h-10 rounded-xl flex items-center justify-center text-[#5A5A4E] hover:text-[#9A9A8A] hover:bg-white/[0.04] transition-all duration-200 focus-ring"
              aria-label="Attach file"
            >
              <Paperclip className="w-5 h-5" />
            </button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95, rotate: -15 }}
              onClick={handleSubmit}
              disabled={!message.trim() || isLoading}
              className={cn(
                'w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 focus-ring',
                message.trim() && !isLoading
                  ? 'text-white'
                  : 'cursor-not-allowed opacity-40',
              )}
              style={{
                background: message.trim() && !isLoading
                  ? '#E8622A'
                  : 'rgba(232, 98, 42, 0.12)',
                boxShadow: message.trim() && !isLoading
                  ? '0 0 20px rgba(232, 98, 42, 0.25)'
                  : 'none',
              }}
              aria-label="Send message"
            >
              <Send className="w-5 h-5" />
            </motion.button>
          </div>
        </div>
      </div>
    </div>
  )
}
