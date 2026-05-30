import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import {
  X,
  Sparkles,
  MoreVertical,
  Loader2,
} from 'lucide-react'
import { useStore } from '@/store'
import MainLayout from '@/components/layout/MainLayout'
import ChatMessage from '@/components/chat/ChatMessage'
import ChatInput, { type ChatPanel } from '@/components/chat/ChatInput'
import TypingIndicator from '@/components/chat/TypingIndicator'
import FilePickerPanel from '@/components/chat/FilePickerPanel'
import TranslatePanel from '@/components/chat/TranslatePanel'
import {
  buildAssetUrl,
  chatApi,
  extractError,
  filesApi,
  type StreamHandle,
} from '@/lib/api'
import type { Message, TimestampRef, FileMetadata } from '@/types'
import toast from 'react-hot-toast'

const TEMP_USER_PREFIX = 'temp-user-'
const TEMP_AI_PREFIX = 'temp-ai-'

export default function ChatPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const {
    conversations,
    setActiveConversation,
    loadConversations,
    upsertConversation,
    updateConversation,
    files,
    loadFiles,
  } = useStore()
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isStreaming, setIsStreaming] = useState(false)
  const [openPanel, setOpenPanel] = useState<ChatPanel>(null)
  const [draftFromTranslate, setDraftFromTranslate] = useState<string>('')
  const [selectedFileIds, setSelectedFileIds] = useState<string[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const streamHandleRef = useRef<StreamHandle | null>(null)
  const conversation = conversations.find((c) => c.id === id)

  // ---------- Bootstrapping ----------
  useEffect(() => {
    if (!id) return
    setActiveConversation(id)
    setIsLoading(true)
    Promise.all([
      chatApi.getConversation(id),
      chatApi.listMessages(id),
      loadFiles(),
    ])
      .then(([conv, list]) => {
        upsertConversation(conv)
        setMessages(list)
        setSelectedFileIds(conv.file_ids || [])
      })
      .catch((err) => {
        toast.error(extractError(err))
      })
      .finally(() => setIsLoading(false))
    return () => {
      streamHandleRef.current?.close()
      streamHandleRef.current = null
    }
  }, [id, setActiveConversation, upsertConversation, loadFiles])

  useEffect(() => {
    if (conversations.length === 0) loadConversations().catch(() => {})
  }, [conversations.length, loadConversations])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isStreaming])

  // ---------- Streaming send ----------
  const handleSend = useCallback(
    async (content: string, attachmentIds?: string[]) => {
      if (!id || isStreaming) return

      // Sync attachments with the conversation if they changed.
      const activeFileIds = attachmentIds ?? selectedFileIds
      if (activeFileIds.length > 0 && conversation) {
        const same =
          activeFileIds.length === (conversation.file_ids?.length || 0) &&
          activeFileIds.every((f) => conversation.file_ids.includes(f))
        if (!same) {
          try {
            await updateConversation(id, { file_ids: activeFileIds })
          } catch (err) {
            toast.error(extractError(err))
          }
        }
      }

      const now = new Date().toISOString()
      const tempUserId = `${TEMP_USER_PREFIX}${Date.now()}`
      const tempAiId = `${TEMP_AI_PREFIX}${Date.now()}`

      // Optimistic user + pending AI placeholder.
      setMessages((prev) => [
        ...prev,
        {
          id: tempUserId,
          conversation_id: id,
          user_id: 'me',
          role: 'user',
          content,
          source_chunks: [],
          timestamp_refs: [],
          created_at: now,
        },
        {
          id: tempAiId,
          conversation_id: id,
          user_id: 'ai',
          role: 'assistant',
          content: '',
          source_chunks: [],
          timestamp_refs: [],
          created_at: now,
          pending: true,
        },
      ])
      setIsStreaming(true)

      const handle = chatApi.streamMessage(id, content, {
        onUserMessage: (uid) => {
          setMessages((prev) =>
            prev.map((m) => (m.id === tempUserId ? { ...m, id: uid } : m)),
          )
        },
        onSources: (chunks) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === tempAiId ? { ...m, source_chunks: chunks } : m,
            ),
          )
        },
        onToken: (text) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === tempAiId
                ? { ...m, content: m.content + text, pending: false }
                : m,
            ),
          )
        },
        onDone: ({ message_id, timestamp_refs, content: full }) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === tempAiId
                ? {
                    ...m,
                    id: message_id,
                    content: full || m.content,
                    timestamp_refs,
                    pending: false,
                  }
                : m,
            ),
          )
          // Refresh conversation summary (message_count / updated_at).
          chatApi.getConversation(id).then(upsertConversation).catch(() => {})
        },
        onError: (msg) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === tempAiId
                ? { ...m, content: m.content || `(${msg})`, pending: false }
                : m,
            ),
          )
          toast.error(msg || 'Streaming failed')
        },
        onClose: () => {
          setIsStreaming(false)
          streamHandleRef.current = null
        },
      })
      streamHandleRef.current = handle
    },
    [id, isStreaming, conversation, updateConversation, upsertConversation, selectedFileIds],
  )

  // ---------- Misc handlers ----------
  const toggleFile = (fid: string) =>
    setSelectedFileIds((prev) =>
      prev.includes(fid) ? prev.filter((x) => x !== fid) : [...prev, fid],
    )

  // ---------- Media player surface ----------
  // For audio/video files attached to the conversation, render a deep-linkable
  // player so timestamp pills can seek inside it.
  const playableFile = useMemo<FileMetadata | null>(() => {
    const ids = conversation?.file_ids || []
    return (
      files.find((f) => ids.includes(f.id) && (f.file_type === 'audio' || f.file_type === 'video')) ||
      null
    )
  }, [conversation?.file_ids, files])

  const playerRef = useRef<HTMLAudioElement | HTMLVideoElement>(null)
  const [mediaUrl, setMediaUrl] = useState<string>('')
  useEffect(() => {
    let cancelled = false
    if (!playableFile) {
      setMediaUrl('')
      return
    }
    filesApi
      .downloadUrl(playableFile.id)
      .then((url) => {
        if (!cancelled) setMediaUrl(buildAssetUrl(url))
      })
      .catch(() => setMediaUrl(''))
    return () => {
      cancelled = true
    }
  }, [playableFile])

  const handleTimestampClick = (ref: TimestampRef) => {
    if (playerRef.current) {
      playerRef.current.currentTime = ref.start_time
      playerRef.current.play().catch(() => {})
    }
  }

  if (!id || (!conversation && !isLoading)) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-text-primary mb-2">Chat not found</h2>
            <button
              onClick={() => navigate('/dashboard')}
              className="text-primary hover:underline"
            >
              Go back to dashboard
            </button>
          </div>
        </div>
      </MainLayout>
    )
  }

  return (
    <MainLayout className="flex flex-col h-screen">
      <div className="flex items-center justify-between px-6 py-4 backdrop-blur-sm" style={{ backgroundColor: 'rgba(10, 10, 10, 0.9)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: 'rgba(232, 98, 42, 0.15)' }}>
            <Sparkles className="w-5 h-5" style={{ color: '#E8622A' }} />
          </div>
          <div>
            <h2 className="font-semibold" style={{ color: '#F2F0E8' }}>
              {conversation?.title || 'Conversation'}
            </h2>
            <p className="text-xs" style={{ color: '#8A8A7A' }}>
              {(conversation?.message_count ?? messages.length)} messages
              {isStreaming && (
                <span className="ml-2 inline-flex items-center gap-1" style={{ color: '#E8622A' }}>
                  <Loader2 className="w-3 h-3 animate-spin" /> streaming
                </span>
              )}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate('/files')}
            className="w-9 h-9 rounded-lg flex items-center justify-center transition-colors hover:bg-white/5"
            style={{ color: '#8A8A7A' }}
            aria-label="More options"
          >
            <MoreVertical className="w-5 h-5" />
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="w-9 h-9 rounded-lg flex items-center justify-center transition-colors hover:bg-white/5"
            style={{ color: '#8A8A7A' }}
            aria-label="Close chat"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Media player surface (when audio/video attached) */}
      {playableFile && mediaUrl && (
        <div className="px-6 py-3" style={{ backgroundColor: 'rgba(10, 10, 10, 0.8)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          {playableFile.file_type === 'video' ? (
            <video
              ref={playerRef as React.RefObject<HTMLVideoElement>}
              src={mediaUrl}
              controls
              className="w-full max-h-72 rounded-xl bg-black"
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

      <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <TypingIndicator />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style={{ backgroundColor: 'rgba(232, 98, 42, 0.1)' }}>
                <Sparkles className="w-8 h-8" style={{ color: '#E8622A' }} />
              </div>
              <h3 className="text-lg font-semibold mb-2" style={{ color: '#F2F0E8' }}>
                Start a conversation
              </h3>
              <p className="text-sm max-w-sm" style={{ color: '#8A8A7A' }}>
                Ask questions about your uploaded files or start a new topic.
              </p>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto">
            {messages.map((message, index) => (
              <ChatMessage
                key={message.id}
                message={message}
                index={index}
                onTimestampClick={handleTimestampClick}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="px-6 py-4 backdrop-blur-sm" style={{ backgroundColor: 'rgba(10, 10, 10, 0.9)', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        <div className="max-w-3xl mx-auto">
          <AnimatePresence>
            {openPanel === 'files' && (
              <FilePickerPanel
                key="files"
                selectedIds={selectedFileIds}
                onToggle={toggleFile}
                onClose={() => setOpenPanel(null)}
              />
            )}
            {openPanel === 'translate' && (
              <TranslatePanel
                key="translate"
                onClose={() => setOpenPanel(null)}
                onUseInChat={(text) => {
                  setDraftFromTranslate(text)
                  setOpenPanel(null)
                }}
              />
            )}
          </AnimatePresence>
          <ChatInput
            onSend={handleSend}
            isLoading={isStreaming}
            onOpenPanel={(p) => setOpenPanel(openPanel === p ? null : p)}
            selectedFileIds={selectedFileIds}
            onClearAttachments={() => setSelectedFileIds([])}
            draft={draftFromTranslate}
          />
        </div>
      </div>
    </MainLayout>
  )
}
