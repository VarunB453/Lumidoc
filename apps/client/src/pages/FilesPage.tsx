import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Grid3X3,
  List,
  FileText,
  Music,
  Video,
  MessageSquare,
  Sparkles,
  Trash2,
  Eye,
} from 'lucide-react'
import { useStore } from '@/store'
import MainLayout from '@/components/layout/MainLayout'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import { cn, formatFileSize } from '@/lib/utils'
import { extractError } from '@/lib/api'
import type { FileMetadata, FileType } from '@/types'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import FileDetailPanel from '@/components/files/FileDetailPanel'

type ViewMode = 'grid' | 'list'
type FilterType = 'all' | FileType

const fileIcons: Record<FileType, typeof FileText> = {
  pdf: FileText,
  audio: Music,
  video: Video,
}

function getFileColor(type: FileType) {
  switch (type) {
    case 'pdf': return { icon: 'text-red-400', bg: 'bg-red-500/10' }
    case 'audio': return { icon: 'text-blue-400', bg: 'bg-blue-500/10' }
    case 'video': return { icon: 'text-green-400', bg: 'bg-green-500/10' }
  }
}

export default function FilesPage() {
  const navigate = useNavigate()
  const { files, loadFiles, removeFile, createConversation } = useStore()
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [filter, setFilter] = useState<FilterType>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [hoveredFile, setHoveredFile] = useState<string | null>(null)
  const [previewFile, setPreviewFile] = useState<FileMetadata | null>(null)

  useEffect(() => {
    loadFiles().catch((err) => toast.error(extractError(err)))
  }, [loadFiles])

  const filteredFiles = files.filter((file) => {
    const matchesFilter = filter === 'all' || file.file_type === filter
    const matchesSearch = file.original_name.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const handleChat = async (fileId: string) => {
    try {
      const conv = await createConversation({ title: 'File chat', file_ids: [fileId] })
      navigate(`/chat/${conv.id}`)
    } catch (err) {
      toast.error(extractError(err))
    }
  }

  const handleDelete = async (fileId: string) => {
    try {
      await removeFile(fileId)
      toast.success('File deleted')
    } catch (err) {
      toast.error(extractError(err))
    }
  }

  const filters: { value: FilterType; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'pdf', label: 'PDFs' },
    { value: 'audio', label: 'Audio' },
    { value: 'video', label: 'Video' },
  ]

  const renderFileCard = (file: FileMetadata, index: number) => {
    const Icon = fileIcons[file.file_type]
    const colors = getFileColor(file.file_type)
    return (
      <motion.div
        key={file.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.05 }}
        onMouseEnter={() => setHoveredFile(file.id)}
        onMouseLeave={() => setHoveredFile(null)}
      >
        <Card
          hover
          className={cn('p-5 relative overflow-hidden', hoveredFile === file.id && 'ring-2 ring-primary/20')}
        >
          <div className="flex items-start justify-between mb-4">
            <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center', colors.bg)}>
              <Icon className={cn('w-6 h-6', colors.icon)} />
            </div>
            <Badge variant={file.status === 'ready' ? 'success' : 'warning'}>
              {file.status}
            </Badge>
          </div>
          <h3 className="font-medium truncate mb-1" style={{ color: '#F2F0E8' }}>{file.original_name}</h3>
          <p className="text-xs mb-3" style={{ color: '#8A8A7A' }}>
            {formatFileSize(file.size_bytes)} • {format(new Date(file.created_at), 'MMM d, yyyy')}
          </p>
          <AnimatePresence>
            {hoveredFile === file.id && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="flex items-center gap-2 mt-3 pt-3"
                style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}
              >
                <button
                  onClick={() => handleChat(file.id)}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors focus-ring"
                  style={{ backgroundColor: 'rgba(232, 98, 42, 0.1)', color: '#E8622A' }}
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  Chat
                </button>
                <button
                  onClick={() => setPreviewFile(file)}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors focus-ring"
                  style={{ backgroundColor: 'rgba(75, 123, 245, 0.1)', color: '#4B7BF5' }}
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  Insights
                </button>
                <button
                  onClick={() => handleDelete(file.id)}
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors focus-ring"
                  aria-label="Delete file"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </Card>
      </motion.div>
    )
  }

  return (
    <MainLayout hideGhostCursor>
      <div className="p-6 lg:p-8" style={{ backgroundColor: '#000000', minHeight: '100vh' }}>
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl font-display font-bold" style={{ color: '#F2F0E8' }}>
                Files Library
              </h1>
              <p className="mt-1" style={{ color: '#8A8A7A' }}>
                Manage and organize your uploaded files
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={cn('w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 focus-ring', viewMode === 'grid' ? 'shadow-glow' : 'hover:bg-white/5')}
                style={{
                  backgroundColor: viewMode === 'grid' ? '#E8622A' : 'transparent',
                  color: viewMode === 'grid' ? '#fff' : '#8A8A7A',
                }}
                aria-label="Grid view"
              >
                <Grid3X3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={cn('w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 focus-ring', viewMode === 'list' ? 'shadow-glow' : 'hover:bg-white/5')}
                style={{
                  backgroundColor: viewMode === 'list' ? '#E8622A' : 'transparent',
                  color: viewMode === 'list' ? '#fff' : '#8A8A7A',
                }}
                aria-label="List view"
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>
        </motion.div>

        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            {filters.map((f) => (
              <button
                key={f.value}
                onClick={() => setFilter(f.value)}
                className={cn('px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 focus-ring whitespace-nowrap')}
                style={{
                  backgroundColor: filter === f.value ? '#E8622A' : 'transparent',
                  color: filter === f.value ? '#fff' : '#8A8A7A',
                  border: filter === f.value ? 'none' : '1px solid rgba(255,255,255,0.08)',
                }}
              >
                {f.label}
              </button>
            ))}
          </div>
          <div className="relative flex-1 sm:max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: '#5A5A4E' }} />
            <input
              type="text"
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-1 focus:ring-[#E8622A]/40"
              style={{
                backgroundColor: '#0A0A0A',
                border: '1px solid rgba(255,255,255,0.08)',
                color: '#F2F0E8',
              }}
            />
          </div>
        </div>

        {filteredFiles.length > 0 ? (
          <AnimatePresence mode="wait">
            {viewMode === 'grid' ? (
              <motion.div
                key="grid"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
              >
                {filteredFiles.map(renderFileCard)}
              </motion.div>
            ) : (
              <motion.div
                key="list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-2"
              >
                {filteredFiles.map((file, index) => {
                  const Icon = fileIcons[file.file_type]
                  const colors = getFileColor(file.file_type)
                  return (
                    <motion.div
                      key={file.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Card hover className="p-4">
                        <div className="flex items-center gap-4">
                          <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center', colors.bg)}>
                            <Icon className={cn('w-5 h-5', colors.icon)} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-medium truncate" style={{ color: '#F2F0E8' }}>{file.original_name}</h3>
                            <p className="text-xs" style={{ color: '#8A8A7A' }}>
                              {formatFileSize(file.size_bytes)} • {format(new Date(file.created_at), 'MMM d, yyyy')}
                            </p>
                          </div>
                          <Badge variant={file.status === 'ready' ? 'success' : 'warning'}>
                            {file.status}
                          </Badge>
                          <div className="flex items-center gap-1">
                            <button onClick={() => handleChat(file.id)} className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-white/5 focus-ring" style={{ color: '#8A8A7A' }} aria-label="Chat with file">
                              <MessageSquare className="w-4 h-4" />
                            </button>
                            <button onClick={() => setPreviewFile(file)} className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-white/5 focus-ring" style={{ color: '#8A8A7A' }} aria-label="Open insights">
                              <Eye className="w-4 h-4" />
                            </button>
                            <button onClick={() => handleDelete(file.id)} className="w-8 h-8 rounded-lg flex items-center justify-center text-red-400 hover:bg-red-500/10 transition-colors focus-ring" aria-label="Delete file">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </Card>
                    </motion.div>
                  )
                })}
              </motion.div>
            )}
          </AnimatePresence>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-16">
            <div className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4" style={{ backgroundColor: 'rgba(232, 98, 42, 0.1)' }}>
              <Search className="w-10 h-10" style={{ color: '#E8622A' }} />
            </div>
            <h3 className="text-lg font-semibold mb-2" style={{ color: '#F2F0E8' }}>No files found</h3>
            <p className="text-sm max-w-sm mx-auto" style={{ color: '#8A8A7A' }}>
              {searchQuery ? `No files matching "${searchQuery}"` : 'Upload your first file to get started'}
            </p>
          </motion.div>
        )}
      </div>
      <AnimatePresence>
        {previewFile && (
          <FileDetailPanel
            file={previewFile}
            onClose={() => setPreviewFile(null)}
          />
        )}
      </AnimatePresence>
    </MainLayout>
  )
}
