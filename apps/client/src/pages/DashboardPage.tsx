import { useEffect, useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Paperclip,
  Smile,
  Settings2,
  Zap,
} from 'lucide-react'
import { useStore } from '@/store'
import MainLayout from '@/components/layout/MainLayout'
import { extractError } from '@/lib/api'
import toast from 'react-hot-toast'

export default function DashboardPage() {
  const navigate = useNavigate()
  const {
    loadConversations,
    createConversation,
  } = useStore()
  const [message, setMessage] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    loadConversations().catch(() => {})
  }, [loadConversations])

  const handleSend = useCallback(async () => {
    if (!message.trim()) return
    try {
      const conv = await createConversation({ title: message.trim().slice(0, 60) })
      navigate(`/chat/${conv.id}`, { state: { initialMessage: message.trim() } })
    } catch (err) {
      toast.error(extractError(err))
    }
  }, [message, createConversation, navigate])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`
  }

  return (
    <MainLayout className="flex flex-col h-screen">
      <div className="flex flex-1 overflow-hidden relative z-10">
        {/* Main content area */}
        <div className="flex-1 flex flex-col justify-end p-8">
          {/* Large prompt area */}
          <div className="flex-1" />

          {/* Ask your data anything input */}
          <div className="mb-8 animate-fade-in-up">
            <div className="relative">
              <textarea
                ref={inputRef}
                value={message}
                onChange={handleInput}
                onKeyDown={handleKeyDown}
                placeholder="Ask your data anything_"
                rows={1}
                className="w-full bg-transparent border-0 resize-none py-2 focus:outline-none focus:ring-0 min-h-[60px] max-h-[120px]"
                style={{
                  color: '#F2F0E8',
                  fontFamily: "'Instrument Serif', serif",
                  fontSize: 'clamp(28px, 4vw, 42px)',
                  lineHeight: '1.2',
                  caretColor: '#E8622A',
                }}
              />
            </div>

            {/* Input action bar */}
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center gap-3">
                <button
                  className="w-9 h-9 rounded-full flex items-center justify-center transition-colors hover:bg-white/5"
                  style={{ border: '1px solid rgba(255,255,255,0.1)', color: '#8A8A7A' }}
                  aria-label="Attach file"
                  onClick={() => navigate('/upload')}
                >
                  <Paperclip className="w-4 h-4" />
                </button>
                <button
                  className="w-9 h-9 rounded-full flex items-center justify-center transition-colors hover:bg-white/5"
                  style={{ border: '1px solid rgba(255,255,255,0.1)', color: '#8A8A7A' }}
                  aria-label="Emoji"
                >
                  <Smile className="w-4 h-4" />
                </button>
                <button
                  className="w-9 h-9 rounded-full flex items-center justify-center transition-colors hover:bg-white/5"
                  style={{ border: '1px solid rgba(255,255,255,0.1)', color: '#8A8A7A' }}
                  aria-label="Settings"
                >
                  <Settings2 className="w-4 h-4" />
                </button>
                <button
                  className="w-9 h-9 rounded-full flex items-center justify-center transition-colors hover:bg-white/5"
                  style={{ border: '1px solid rgba(255,255,255,0.1)', color: '#8A8A7A' }}
                  aria-label="Model"
                >
                  <span className="text-xs font-bold">M</span>
                </button>
              </div>
              <button
                onClick={handleSend}
                className="w-11 h-11 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-105"
                style={{
                  backgroundColor: '#E8622A',
                  boxShadow: '0 0 20px rgba(232, 98, 42, 0.3)',
                }}
                aria-label="Send message"
              >
                <Zap className="w-5 h-5 text-white" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
