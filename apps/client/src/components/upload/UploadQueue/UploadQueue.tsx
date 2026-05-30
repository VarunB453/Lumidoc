import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText,
  Music,
  Video,
  X,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from 'lucide-react'
import { cn, formatFileSize } from '@/lib/utils'
import type { UploadedFile } from '@/types'
import Badge from '@/components/ui/Badge'

interface UploadQueueProps {
  files: UploadedFile[]
  onRemove: (fileId: string) => void
  onRetry: (fileId: string) => void
  onCancel: (fileId: string) => void
}

export default function UploadQueue({ files, onRemove, onRetry, onCancel }: UploadQueueProps) {
  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf': return FileText
      case 'audio': return Music
      case 'video': return Video
      default: return FileText
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'uploading': return <Badge variant="info">Uploading</Badge>
      case 'processing': return <Badge variant="warning">Processing</Badge>
      case 'ready': return <Badge variant="success">Ready</Badge>
      case 'error': return <Badge variant="error">Error</Badge>
      default: return null
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploading': return <Loader2 className="w-4 h-4 animate-spin text-primary" />
      case 'processing': return <Loader2 className="w-4 h-4 animate-spin text-yellow-500" />
      case 'ready': return <CheckCircle2 className="w-4 h-4 text-accent" />
      case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />
      default: return null
    }
  }

  return (
    <div className="space-y-3">
      <AnimatePresence>
        {files.map((file) => {
          const Icon = getFileIcon(file.type)
          return (
            <motion.div
              key={file.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="bg-white rounded-2xl p-4 shadow-soft"
            >
              <div className="flex items-center gap-4">
                {/* File Icon */}
                <div
                  className={cn(
                    'w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0',
                    file.type === 'pdf' && 'bg-red-50',
                    file.type === 'audio' && 'bg-blue-50',
                    file.type === 'video' && 'bg-green-50'
                  )}
                >
                  <Icon
                    className={cn(
                      'w-6 h-6',
                      file.type === 'pdf' && 'text-red-500',
                      file.type === 'audio' && 'text-blue-500',
                      file.type === 'video' && 'text-green-500'
                    )}
                  />
                </div>

                {/* File Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="text-sm font-medium text-text-primary truncate">
                      {file.name}
                    </p>
                    {getStatusBadge(file.status)}
                  </div>
                  <p className="text-xs text-text-muted">
                    {formatFileSize(file.size)}
                  </p>

                  {/* Progress Bar */}
                  {(file.status === 'uploading' || file.status === 'processing') && (
                    <div className="mt-2">
                      <div className="h-2 bg-primary-50 rounded-full overflow-hidden">
                        <motion.div
                          className={cn(
                            'h-full rounded-full',
                            file.status === 'uploading' ? 'bg-primary' : 'bg-yellow-400'
                          )}
                          initial={{ width: 0 }}
                          animate={{ width: `${file.progress}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                      <p className="text-xs text-text-muted mt-1">{file.progress}%</p>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1">
                  {getStatusIcon(file.status)}

                  {file.status === 'error' && (
                    <button
                      onClick={() => onRetry(file.id)}
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-text-muted hover:bg-primary-50 hover:text-primary transition-colors focus-ring"
                      aria-label="Retry upload"
                    >
                      <RotateCcw className="w-4 h-4" />
                    </button>
                  )}

                  {(file.status === 'uploading' || file.status === 'processing') && (
                    <button
                      onClick={() => onCancel(file.id)}
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-text-muted hover:bg-red-50 hover:text-red-500 transition-colors focus-ring"
                      aria-label="Cancel upload"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}

                  {file.status === 'ready' && (
                    <button
                      onClick={() => onRemove(file.id)}
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-text-muted hover:bg-red-50 hover:text-red-500 transition-colors focus-ring"
                      aria-label="Remove file"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
