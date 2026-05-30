import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileText, Music, Video, Check, Upload } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '@/store'
import { cn, formatFileSize } from '@/lib/utils'
import type { FileType } from '@/types'

const ICONS: Record<FileType, typeof FileText> = {
  pdf: FileText,
  audio: Music,
  video: Video,
}

const COLORS: Record<FileType, { icon: string; bg: string }> = {
  pdf: { icon: 'text-red-500', bg: 'bg-red-50 dark:bg-red-900/30' },
  audio: { icon: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-900/30' },
  video: { icon: 'text-green-500', bg: 'bg-green-50 dark:bg-green-900/30' },
}

interface Props {
  selectedIds: string[]
  onToggle: (id: string) => void
  onClose: () => void
}

export default function FilePickerPanel({ selectedIds, onToggle, onClose }: Props) {
  const navigate = useNavigate()
  const { files, loadFiles } = useStore()

  useEffect(() => {
    loadFiles().catch(() => {})
  }, [loadFiles])

  const ready = files.filter((f) => f.status === 'ready')

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      className="surface rounded-2xl shadow-soft-lg border border-primary-50 dark:border-primary-900 p-4 mb-3 max-h-72 overflow-y-auto scrollbar-thin"
    >
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-sm text-text-primary">Attach files from your library</h4>
        <button
          onClick={onClose}
          className="text-xs text-text-muted hover:text-text-primary"
        >
          Done
        </button>
      </div>
      {ready.length === 0 ? (
        <div className="text-center py-6">
          <Upload className="w-6 h-6 text-text-muted mx-auto mb-2" />
          <p className="text-sm text-text-muted mb-3">
            You haven't uploaded any files yet.
          </p>
          <button
            onClick={() => navigate('/upload')}
            className="text-sm text-primary font-medium hover:underline"
          >
            Upload a file
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          {ready.map((file) => {
            const Icon = ICONS[file.file_type]
            const c = COLORS[file.file_type]
            const selected = selectedIds.includes(file.id)
            return (
              <button
                key={file.id}
                onClick={() => onToggle(file.id)}
                className={cn(
                  'w-full flex items-center gap-3 p-2 rounded-xl transition-colors text-left focus-ring',
                  selected
                    ? 'bg-primary-50 dark:bg-primary-900/30 ring-1 ring-primary'
                    : 'hover:bg-primary-50/60 dark:hover:bg-primary-900/20',
                )}
              >
                <div
                  className={cn(
                    'w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0',
                    c.bg,
                  )}
                >
                  <Icon className={cn('w-4 h-4', c.icon)} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">
                    {file.original_name}
                  </p>
                  <p className="text-xs text-text-muted">
                    {formatFileSize(file.size_bytes)}
                  </p>
                </div>
                {selected && <Check className="w-4 h-4 text-primary" />}
              </button>
            )
          })}
        </div>
      )}
    </motion.div>
  )
}
