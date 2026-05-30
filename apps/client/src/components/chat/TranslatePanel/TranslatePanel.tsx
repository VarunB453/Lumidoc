import { useState } from 'react'
import { motion } from 'framer-motion'
import { Languages, Loader2, Copy } from 'lucide-react'
import { miscApi, extractError } from '@/lib/api'
import toast from 'react-hot-toast'

const LANGUAGES = [
  'English',
  'Spanish',
  'French',
  'German',
  'Italian',
  'Portuguese',
  'Hindi',
  'Mandarin Chinese',
  'Japanese',
  'Korean',
  'Arabic',
]

interface Props {
  onClose: () => void
  onUseInChat: (text: string) => void
}

export default function TranslatePanel({ onClose, onUseInChat }: Props) {
  const [text, setText] = useState('')
  const [target, setTarget] = useState('Spanish')
  const [translated, setTranslated] = useState('')
  const [loading, setLoading] = useState(false)

  const handleTranslate = async () => {
    if (!text.trim()) {
      toast.error('Type something to translate')
      return
    }
    setLoading(true)
    try {
      const res = await miscApi.translate(text.trim(), target)
      setTranslated(res.translated_text)
    } catch (err) {
      toast.error(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      className="surface rounded-2xl shadow-soft-lg border border-primary-50 dark:border-primary-900 p-4 mb-3"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Languages className="w-4 h-4 text-primary" />
          <h4 className="font-semibold text-sm text-text-primary">Translate</h4>
        </div>
        <button
          onClick={onClose}
          className="text-xs text-text-muted hover:text-text-primary"
        >
          Close
        </button>
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={3}
        placeholder="Type or paste text to translate…"
        className="w-full px-3 py-2 rounded-xl bg-white/80 dark:bg-white/5 border border-primary-100 dark:border-primary-900 text-sm focus-ring focus:border-primary resize-none"
      />

      <div className="flex items-center gap-2 mt-3">
        <select
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          className="px-3 py-2 rounded-xl surface border border-primary-100 dark:border-primary-900 text-sm focus-ring focus:border-primary"
        >
          {LANGUAGES.map((l) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>
        <button
          onClick={handleTranslate}
          disabled={loading}
          className="ml-auto inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-white text-sm font-medium hover:bg-primary-600 disabled:opacity-60 transition-colors focus-ring"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Languages className="w-4 h-4" />}
          Translate
        </button>
      </div>

      {translated && (
        <div className="mt-3 p-3 rounded-xl bg-primary-50 dark:bg-primary-900/30 text-sm text-text-primary">
          <p className="whitespace-pre-wrap">{translated}</p>
          <div className="flex items-center justify-end gap-2 mt-2">
            <button
              onClick={() => {
                navigator.clipboard.writeText(translated)
                toast.success('Copied')
              }}
              className="inline-flex items-center gap-1 text-xs text-text-muted hover:text-primary"
            >
              <Copy className="w-3.5 h-3.5" /> Copy
            </button>
            <button
              onClick={() => {
                onUseInChat(translated)
                onClose()
              }}
              className="text-xs text-primary font-medium hover:underline"
            >
              Use in chat
            </button>
          </div>
        </div>
      )}
    </motion.div>
  )
}
