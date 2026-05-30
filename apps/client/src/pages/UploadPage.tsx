import { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Upload, Trash2, CheckCircle2 } from 'lucide-react'
import { useStore } from '@/store'
import MainLayout from '@/components/layout/MainLayout'
import FileDropzone from '@/components/upload/FileDropzone'
import UploadQueue from '@/components/upload/UploadQueue'
import Button from '@/components/ui/Button'
import { filesApi, extractError } from '@/lib/api'
import type { FileType, UploadedFile } from '@/types'
import toast from 'react-hot-toast'

function inferFileType(file: File): FileType {
  if (file.type.includes('audio')) return 'audio'
  if (file.type.includes('video')) return 'video'
  return 'pdf'
}

export default function UploadPage() {
  const navigate = useNavigate()
  const { upsertFile, loadFiles, createConversation } = useStore()
  const [uploadQueue, setUploadQueue] = useState<UploadedFile[]>([])
  const abortControllers = useRef<Map<string, AbortController>>(new Map())
  const updateQueuedFile = useCallback((id: string, patch: Partial<UploadedFile>) => {
    setUploadQueue((prev) => prev.map((file) => (file.id === id ? { ...file, ...patch } : file)))
  }, [])

  const uploadOne = useCallback(
    async (queued: UploadedFile) => {
      if (!queued.file) return
      const controller = new AbortController()
      abortControllers.current.set(queued.id, controller)
      try {
        const response = await filesApi.upload(
          queued.file,
          (progress) => {
            updateQueuedFile(queued.id, { progress, status: 'uploading' })
          },
          controller.signal,
        )
        updateQueuedFile(queued.id, {
          backendFileId: response.file_id,
          progress: 100,
          status: response.status === 'ready' ? 'ready' : 'processing',
        })
        const metadata = await filesApi.get(response.file_id)
        upsertFile(metadata)
        toast.success(`${queued.name} uploaded`)
      } catch (err) {
        if (controller.signal.aborted) {
          updateQueuedFile(queued.id, { status: 'error', error: 'Upload cancelled' })
        } else {
          updateQueuedFile(queued.id, {
            status: 'error',
            error: extractError(err),
          })
          toast.error(extractError(err))
        }
      } finally {
        abortControllers.current.delete(queued.id)
      }
    },
    [updateQueuedFile, upsertFile],
  )

  const handleFilesDrop = useCallback(
    (droppedFiles: File[]) => {
      const newFiles: UploadedFile[] = droppedFiles.map((file) => ({
        id: `upload-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        name: file.name,
        type: inferFileType(file),
        size: file.size,
        status: 'uploading',
        progress: 0,
        file,
      }))

      setUploadQueue((prev) => [...prev, ...newFiles])
      newFiles.forEach(uploadOne)
    },
    [uploadOne],
  )

  const handleRemove = useCallback((fileId: string) => {
    setUploadQueue((prev) => prev.filter((f) => f.id !== fileId))
  }, [])

  const handleRetry = useCallback(
    (fileId: string) => {
      const file = uploadQueue.find((f) => f.id === fileId)
      if (!file) return
      updateQueuedFile(fileId, { status: 'uploading', progress: 0, error: undefined })
      uploadOne(file)
    },
    [uploadQueue, updateQueuedFile, uploadOne],
  )

  const handleCancel = useCallback((fileId: string) => {
    const controller = abortControllers.current.get(fileId)
    if (controller) {
      controller.abort()
    }
    updateQueuedFile(fileId, { status: 'error', error: 'Upload cancelled' })
  }, [updateQueuedFile])

  const handleClearAll = () => {
    setUploadQueue([])
  }

  const handleStartChat = async () => {
    const fileIds = uploadQueue
      .filter((f) => f.backendFileId && f.status !== 'error')
      .map((f) => f.backendFileId as string)
    try {
      await loadFiles()
      const conv = await createConversation({ title: 'New file chat', file_ids: fileIds })
      navigate(`/chat/${conv.id}`)
    } catch (err) {
      toast.error(extractError(err))
    }
  }

  const readyFiles = uploadQueue.filter((f) => f.backendFileId && f.status !== 'error')
  const hasReadyFiles = readyFiles.length > 0

  return (
    <MainLayout>
      <div className="p-6 lg:p-8 max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-display font-bold" style={{ color: '#F2F0E8' }}>
                Upload Files
              </h1>
              <p className="mt-1" style={{ color: '#8A8A7A' }}>
                Upload PDFs, audio, and video files for AI analysis
              </p>
            </div>
            {uploadQueue.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearAll}
                className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Clear All
              </Button>
            )}
          </div>
        </motion.div>

        <div className="mb-8">
          <FileDropzone onFilesDrop={handleFilesDrop} />
        </div>

        {uploadQueue.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-display font-semibold" style={{ color: '#F2F0E8' }}>
                Upload Queue ({uploadQueue.length})
              </h2>
              {hasReadyFiles && (
                <div className="flex items-center gap-2 text-sm" style={{ color: '#0EC8A0' }}>
                  <CheckCircle2 className="w-4 h-4" />
                  {readyFiles.length} uploaded
                </div>
              )}
            </div>
            <UploadQueue
              files={uploadQueue}
              onRemove={handleRemove}
              onRetry={handleRetry}
              onCancel={handleCancel}
            />
          </motion.div>
        )}

        {hasReadyFiles && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 flex items-center gap-3 p-4 rounded-2xl"
            style={{ backgroundColor: 'rgba(232, 98, 42, 0.08)', border: '1px solid rgba(232, 98, 42, 0.2)' }}
          >
            <div className="flex-1">
              <p className="text-sm font-medium" style={{ color: '#E8622A' }}>
                {readyFiles.length} file(s) ready for analysis
              </p>
              <p className="text-xs mt-0.5" style={{ color: '#8A8A7A' }}>
                Start chatting with your uploaded content
              </p>
            </div>
            <Button onClick={handleStartChat} className="bg-accent hover:bg-accent-600">
              <Upload className="w-4 h-4 mr-2" />
              Start Chat
            </Button>
          </motion.div>
        )}

        {uploadQueue.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4" style={{ backgroundColor: 'rgba(232, 98, 42, 0.1)' }}>
              <Upload className="w-10 h-10" style={{ color: '#E8622A' }} />
            </div>
            <h3 className="text-lg font-semibold mb-2" style={{ color: '#F2F0E8' }}>
              No files in queue
            </h3>
            <p className="text-sm max-w-sm mx-auto" style={{ color: '#8A8A7A' }}>
              Drag and drop files above or click to browse your device
            </p>
          </motion.div>
        )}
      </div>
    </MainLayout>
  )
}
